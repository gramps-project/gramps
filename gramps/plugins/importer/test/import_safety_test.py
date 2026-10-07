#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
"""Check import confinement, bounded parsing and state recovery."""

# -------------------------------------------------------------------------
# Python modules
# -------------------------------------------------------------------------
import gzip
import io
import ntpath
import os
from pathlib import Path
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, mock_open, patch
from xml.parsers.expat import ExpatError

# -------------------------------------------------------------------------
# Gramps modules
# -------------------------------------------------------------------------
from gramps.plugins.importer import importgpkg, importxml
from gramps.plugins.export import exportpkg
from gramps.plugins.importer.importvcard import VCardParser
from gramps.plugins.lib import libprogen
from gramps.cli.user import User
from gramps.gen.db import DbTxn
from gramps.gen.lib import DNAMatch, DNATest, Media
from gramps.gen.proxy import PrivateProxyDb
from gramps.gen.utils.file import media_path_full
from gramps.plugins.db.dbapi.sqlite import SQLite


# -------------------------------------------------------------------------
# PackageSafetyTest
# -------------------------------------------------------------------------
class PackageSafetyTest(unittest.TestCase):
    """Use disposable media roots, without reading a real family tree."""

    def setUp(self) -> None:
        """Prepare an empty media root and a mocked XML importer."""
        self.temporary = tempfile.TemporaryDirectory(prefix="gramps-import-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.media = self.root / "media"
        self.media.mkdir()
        self.package = self.root / "family.gpkg"
        self.destination = self.media / "family.gpkg.media"
        self.database = Mock()
        self.database.get_mediapath.return_value = str(self.media)
        self.user = Mock()

    def write_package(self, members: list[tarfile.TarInfo]) -> None:
        """Create a synthetic package containing fixed, non-private content.

        :param members: Additional member metadata for the test.
        """
        with tarfile.open(self.package, "w:gz") as archive:
            xml = tarfile.TarInfo("data.gramps")
            xml.size = len(b"<database/>")
            archive.addfile(xml, io.BytesIO(b"<database/>"))
            for member in members:
                content = io.BytesIO(b"media") if member.isfile() else None
                if member.isfile():
                    member.size = 5
                archive.addfile(member, content)

    def import_package(self) -> Mock:
        """Run the production package entry point with XML parsing isolated.

        :returns: The XML import mock, for checking whether it was reached.
        """
        with patch.object(importgpkg, "importData", return_value=True) as importer:
            importgpkg.impData(self.database, str(self.package), self.user)
        return importer

    def test_nested_media_and_legacy_hardlinks(self) -> None:
        """Valid packages keep media and safely copy older hard-link entries."""
        media = tarfile.TarInfo("pictures/photo.jpg")
        duplicate = tarfile.TarInfo("pictures/copy.jpg")
        duplicate.type = tarfile.LNKTYPE
        duplicate.linkname = media.name
        self.write_package([media, duplicate])
        importer = self.import_package()
        importer.assert_called_once()
        self.user.notify_error.assert_not_called()
        self.assertEqual((self.destination / media.name).read_bytes(), b"media")
        self.assertEqual((self.destination / duplicate.name).read_bytes(), b"media")
        self.assertFalse((self.destination / "data.gramps").exists())

    def test_unsafe_paths_fail_before_import(self) -> None:
        """Traversal, absolute paths and Windows alternate streams are rejected."""
        marker = self.root / "sentinel.txt"
        marker.write_text("unchanged", encoding="utf-8")
        for name in (
            "../sentinel.txt",
            "../../sentinel.txt",
            "..\\sentinel.txt",
            str(marker),
            "/absolute.txt",
            "C:/outside.txt",
            "C:relative.txt",
            "//server/share/file",
            "photo.jpg:stream",
            "NUL.txt",
            "pictures/COM1",
            "pictures/LPT\u00b2.txt",
            "pictures/alias. ",
        ):
            with self.subTest(name=name):
                self.write_package([tarfile.TarInfo(name)])
                self.import_package().assert_not_called()
                self.assertFalse(self.destination.exists())
                self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")

    def test_symlinks_special_files_and_escaping_hardlinks(self) -> None:
        """Package metadata never creates OS links, devices or named pipes."""
        for kind in (
            tarfile.SYMTYPE,
            tarfile.FIFOTYPE,
            tarfile.CHRTYPE,
            tarfile.LNKTYPE,
        ):
            with self.subTest(kind=kind):
                member = tarfile.TarInfo("pictures/unsafe")
                member.type = kind
                member.linkname = "../../outside"
                self.write_package([member])
                self.import_package().assert_not_called()
                self.assertFalse(self.destination.exists())

    def test_existing_media_directory_is_preserved(self) -> None:
        """An existing destination is never removed or overwritten."""
        self.destination.mkdir()
        original = self.destination / "original.txt"
        original.write_bytes(b"original")
        self.write_package([])
        self.import_package().assert_not_called()
        self.assertEqual(original.read_bytes(), b"original")

    def test_truncated_archive_can_be_retried(self) -> None:
        """A failed extraction leaves no owned directory blocking a retry."""
        self.package.write_bytes(b"not a tar archive")
        self.import_package().assert_not_called()
        self.assertFalse(self.destination.exists())
        self.write_package([])
        self.import_package().assert_called_once()

    def test_native_export_stores_regular_media_contents(self) -> None:
        """Repeated source files are packaged as data, not filesystem links."""
        photo = self.media / "photo.jpg"
        photo.write_bytes(b"media")
        self.database.get_media_handles.return_value = ["M1", "M2"]
        self.database.get_media_from_handle.return_value.get_path.return_value = (
            "photo.jpg"
        )
        with patch.object(exportpkg, "XmlWriter") as writer:
            writer.return_value.write_handle.side_effect = lambda stream: stream.write(
                b"<database/>"
            )
            self.assertTrue(
                exportpkg.PackageWriter(
                    self.database, str(self.package), self.user
                ).export()
            )
        with tarfile.open(self.package) as archive:
            media = [member for member in archive if member.name.startswith("media/")]
            self.assertEqual(len(media), 2)
            self.assertTrue(all(member.isfile() for member in media))
        self.import_package().assert_called_once()
        self.assertEqual((self.destination / "media/000001.jpg").read_bytes(), b"media")

    def test_truncated_gzip_archive_is_cleaned_up(self) -> None:
        """A truncated compressed stream is reported and its directory removed."""
        self.package.write_bytes(gzip.compress(b"\0" * 10240)[:12])
        self.import_package().assert_not_called()
        self.assertFalse(self.destination.exists())

    def test_native_export_preserves_privacy_filter(self) -> None:
        """Path rewriting does not reintroduce excluded records or media bytes."""
        database = SQLite()
        database.load(":memory:")
        self.addCleanup(database.close)
        database.set_mediapath(str(self.media))
        with DbTxn("Filtered synthetic media", database) as transaction:
            for private in (False, True):
                name = "private.jpg" if private else "public.jpg"
                (self.media / name).write_bytes(name.encode("ascii"))
                media = Media()
                media.set_path(name)
                media.set_description(name)
                media.set_privacy(private)
                database.add_media(media, transaction)
        options = Mock()
        options.get_filtered_database.return_value = PrivateProxyDb(database)
        self.assertTrue(
            exportpkg.writeData(database, str(self.package), self.user, options)
        )
        options.parse_options.assert_called_once()
        with tarfile.open(self.package) as archive:
            members = [member for member in archive if member.name.startswith("media/")]
            self.assertEqual(len(members), 1)
            content = archive.extractfile(members[0])
            assert content is not None
            with content:
                self.assertEqual(content.read(), b"public.jpg")
            content = archive.extractfile("data.gramps")
            assert content is not None
            with content:
                xml = gzip.decompress(content.read())
                self.assertIn(b"public.jpg", xml)
                self.assertNotIn(b"private.jpg", xml)

    def test_native_package_preserves_master_dna_records(self) -> None:
        """Unfiltered native packaging retains master's additional record types."""
        database = SQLite()
        database.load(":memory:")
        self.addCleanup(database.close)
        test = DNATest()
        test.set_kit_id("SYNTHETIC-KIT")
        match = DNAMatch()
        match.set_shared_cm(123.5)
        with DbTxn("Synthetic DNA", database) as transaction:
            handle = database.add_dnatest(test, transaction)
            match.set_subject_test_handle(handle)
            match_handle = database.add_dnamatch(match, transaction)
        user = User(callback=lambda *args, **kwargs: None, quiet=True)
        user._fileout = io.StringIO()
        self.assertTrue(
            exportpkg.PackageWriter(database, str(self.package), user).export()
        )
        restored = SQLite()
        restored.load(":memory:")
        self.addCleanup(restored.close)
        restored.set_mediapath(str(self.media))
        self.assertIsNotNone(importgpkg.impData(restored, str(self.package), user))
        self.assertEqual(restored.get_number_of_dnatests(), 1)
        self.assertEqual(restored.get_number_of_dnamatches(), 1)
        self.assertEqual(
            restored.get_dnatest_from_handle(handle).get_kit_id(), "SYNTHETIC-KIT"
        )
        self.assertEqual(
            restored.get_dnamatch_from_handle(match_handle).get_shared_cm(), 123.5
        )

    def test_filtered_dna_preserves_existing_package(self) -> None:
        """Unsupported DNA filtering is rejected before opening the archive."""
        database = SQLite()
        database.load(":memory:")
        self.addCleanup(database.close)
        filtered = PrivateProxyDb(database)
        self.package.write_bytes(b"previous native package")
        for count in (1, None):
            with (
                self.subTest(count=count),
                patch.object(database, "get_number_of_dnatests", return_value=count),
                patch.object(database, "get_dnatest_handles") as handles,
            ):
                self.assertFalse(
                    exportpkg.PackageWriter(
                        filtered, str(self.package), self.user
                    ).export()
                )
                handles.assert_not_called()
                self.assertEqual(self.package.read_bytes(), b"previous native package")

    def test_native_package_roundtrip_with_media_outside_base(self) -> None:
        """Parent-relative media keeps its bytes and links after relocation."""
        database = SQLite()
        database.load(":memory:")
        self.addCleanup(database.close)
        database.set_mediapath(str(self.media))
        original = self.root / "outside.jpg"
        original.write_bytes(b"outside media")
        media = Media()
        media.set_path("../outside.jpg")
        media.set_mime_type("image/jpeg")
        with DbTxn("Synthetic media", database) as transaction:
            handle = database.add_media(media, transaction)
        original_path = database.get_media_from_handle(handle).get_path()
        user = User(callback=lambda *args, **kwargs: None, quiet=True)
        user._fileout = io.StringIO()
        self.assertTrue(
            exportpkg.PackageWriter(database, str(self.package), user).export()
        )
        self.assertEqual(
            database.get_media_from_handle(handle).get_path(), original_path
        )
        self.assertEqual(original.read_bytes(), b"outside media")
        # Remove only this test's original, proving that recovery uses the copy.
        original.unlink()
        for index, base in enumerate((str(self.media), None, "")):
            with self.subTest(base=base):
                package = self.root / ("restore-%d.gpkg" % index)
                package.write_bytes(self.package.read_bytes())
                restored = SQLite()
                restored.load(":memory:")
                self.addCleanup(restored.close)
                restored.set_mediapath(base)
                existing = Media()
                existing.set_path("existing.jpg")
                with DbTxn("Existing media", restored) as transaction:
                    existing_handle = restored.add_media(existing, transaction)
                with patch.object(
                    importgpkg, "media_path", return_value=str(self.media)
                ):
                    self.assertIsNotNone(
                        importgpkg.impData(restored, str(package), user)
                    )
                self.assertEqual(restored.get_mediapath(), base)
                self.assertEqual(
                    restored.get_media_from_handle(existing_handle).get_path(),
                    "existing.jpg",
                )
                recovered = restored.get_media_from_handle(handle)
                self.assertEqual(
                    Path(media_path_full(restored, recovered.get_path())).read_bytes(),
                    b"outside media",
                )


# -------------------------------------------------------------------------
# ParserSafetyTest
# -------------------------------------------------------------------------
class ParserSafetyTest(unittest.TestCase):
    """Check finite parsing and state restoration on malformed inputs."""

    def test_package_paths_resolve_only_extracted_media(self) -> None:
        """Legacy absolute paths and portable names find only packaged copies."""
        parser = object.__new__(importxml.GrampsParser)
        key = os.path.normcase(os.path.normpath("photos/medal.jpg"))
        extracted = str(
            Path(tempfile.gettempdir()) / "package" / "photos" / "medal.jpg"
        )
        parser.package_media_paths = {key: extracted}
        for source in ("photos/medal.jpg", "/photos/medal.jpg", r"C:\photos\medal.jpg"):
            with self.subTest(source=source):
                self.assertEqual(parser._resolve_media_path(source), extracted)
        for source in ("missing.jpg", "https://example.invalid/medal.jpg"):
            self.assertEqual(parser._resolve_media_path(source), source)
        parser.package_media_paths = None
        self.assertEqual(
            parser._resolve_media_path("photos/medal.jpg"), "photos/medal.jpg"
        )

    def test_progen_failure_restores_signals_and_progress(self) -> None:
        """A failed import transaction restores database and GUI state."""
        parser = object.__new__(libprogen.ProgenParser)
        parser.option = {"prim_person": True, "prim_family": False, "prim_child": False}
        parser.fname = "tree.def"
        parser.bname = "tree"
        parser.dbase = Mock()
        parser.uistate = True
        parser.progress = Mock()
        with (
            patch.object(
                libprogen, "_get_defname", return_value=("tree.def", "tree.def")
            ),
            patch.object(libprogen, "PG30Def") as definition,
            patch.object(libprogen, "_read_mem", return_value=[]),
            patch.object(libprogen, "_read_recs", return_value=[]),
            patch.object(libprogen, "DbTxn"),
            patch.object(parser, "_ProgenParser__display_message"),
            patch.object(
                parser, "create_tags", side_effect=ValueError("invalid record")
            ),
        ):
            definition.return_value.tables = {
                "Genealogical": SimpleNamespace(
                    parms={"field_father": "father", "field_mother": "mother"}
                )
            }
            with self.assertRaises(ValueError):
                parser.parse_progen_file()
        parser.dbase.disable_signals.assert_called_once()
        parser.dbase.enable_signals.assert_called_once()
        parser.dbase.request_rebuild.assert_called_once()
        parser.progress.close.assert_called_once()

    def test_vcard_unterminated_parameters(self) -> None:
        """Malformed quoted properties return without restarting the search."""
        for value in ('FN;TYPE="home:bad', 'FN;TYPE="home:bad"', ":bad", "FN"):
            with self.subTest(value=value):
                self.assertEqual(VCardParser.name_value_split(value), ())

    def test_vcard_valid_quoted_colons_and_groups(self) -> None:
        """Quoted parameter colons do not change the property delimiter."""
        self.assertEqual(
            VCardParser.name_value_split('item1.FN;TYPE="home:work":A:B'),
            ('FN;TYPE="home:work"', "A:B"),
        )

    def test_xml_counts_plain_and_compressed_input(self) -> None:
        """Ordinary progress and person counts are retained for both formats."""
        content = '<database>\n  <person id="I1"/>\n</database>'
        with tempfile.TemporaryDirectory(prefix="gramps-xml-") as temporary:
            filename = Path(temporary) / "tree.gramps"
            for compressed in (False, True):
                with self.subTest(compressed=compressed):
                    data = content.encode("utf-8")
                    filename.write_bytes(gzip.compress(data) if compressed else data)
                    counter = importxml.LineParser(str(filename))
                    self.assertEqual(counter.get_count(), 3)
                    self.assertEqual(counter.get_person_count(), 1)

    def test_xml_long_compressed_line_abandons_progress_estimate(self) -> None:
        """A compressed long line need not be fully allocated for progress."""
        with tempfile.TemporaryDirectory(prefix="gramps-xml-") as temporary:
            filename = Path(temporary) / "tree.gramps"
            filename.write_bytes(gzip.compress(b"x" * (1024 * 1024)))
            counter = importxml.LineParser(str(filename))
            self.assertEqual(counter.get_count(), 0)

    def test_xml_progress_scan_has_a_total_budget(self) -> None:
        """Many short compressed lines also stop the optional counting pass."""
        with tempfile.TemporaryDirectory(prefix="gramps-xml-") as temporary:
            filename = Path(temporary) / "tree.gramps"
            filename.write_bytes(gzip.compress(b"x\n" * 100))
            with patch.object(importxml.LineParser, "MAX_SCAN_LENGTH", 32):
                self.assertEqual(importxml.LineParser(str(filename)).get_count(), 0)

    def test_xml_unreadable_counter_does_not_mask_error(self) -> None:
        """An unopened file does not cause an UnboundLocalError during cleanup."""
        with (
            patch.object(importxml, "open", side_effect=OSError("unreadable")),
            patch.object(importxml, "GZIP_OK", False),
        ):
            self.assertEqual(importxml.LineParser("absent.gramps").get_count(), 0)

    def test_xml_truncated_gzip_is_reported(self) -> None:
        """A truncated gzip header or payload produces a handled import error."""
        with tempfile.TemporaryDirectory(prefix="gramps-xml-") as temporary:
            filename = Path(temporary) / "truncated.gramps"
            data = gzip.compress(b"<database>\n</database>\n")
            for damaged in (data[:12], data[:-6]):
                with self.subTest(size=len(damaged)):
                    filename.write_bytes(damaged)
                    self.assertEqual(importxml.LineParser(str(filename)).get_count(), 0)
                    database = SQLite()
                    database.load(":memory:")
                    self.addCleanup(database.close)
                    user = Mock()
                    self.assertIsNone(
                        importxml.importData(database, str(filename), user)
                    )
                    user.notify_error.assert_called_once()

    def test_xml_parse_failure_restores_readonly(self) -> None:
        """The import entry point restores the caller's read-only state."""
        database = Mock(readonly=True)
        with (
            patch.object(importxml, "ImportOpenFileContextManager") as context,
            patch.object(importxml, "GrampsParser") as parser,
        ):
            context.return_value.__enter__.return_value = io.BytesIO(b"invalid")
            parser.return_value.parse.side_effect = ExpatError("invalid XML")
            importxml.importData(database, "-", Mock())
        self.assertTrue(database.readonly)

    def test_xml_parse_failure_restores_signals(self) -> None:
        """Failed XML parsing cannot leave database notifications disabled."""
        parser = object.__new__(importxml.GrampsParser)
        parser.db = Mock()
        with patch.object(parser, "_parse", side_effect=ExpatError("invalid XML")):
            with self.assertRaises(ExpatError):
                parser.parse(io.BytesIO(b"invalid"))
        parser.db.enable_signals.assert_called_once()
        parser.db.request_rebuild.assert_called_once()

    def test_xml_date_without_parent_reports_parse_error(self) -> None:
        """Misplaced dates produce a handled parser error instead of a crash."""
        parser = object.__new__(importxml.GrampsParser)
        for owner in (
            "citation",
            "ord",
            "object",
            "address",
            "name",
            "event",
            "placeref",
            "place_name",
            "dnatest",
            "dnamatch",
        ):
            setattr(parser, owner, None)
        for callback, args in (
            (parser.start_compound_date, ({"start": "1900", "stop": "1901"}, 4)),
            (parser.start_dateval, ({"val": "1900"},)),
            (parser.start_datestr, ({"val": "unknown"},)),
        ):
            with (
                self.subTest(callback=callback.__name__),
                self.assertRaises(ExpatError),
            ):
                callback(*args)

    def test_progen_missing_definition_stops_at_windows_roots(self) -> None:
        """Drive and UNC roots terminate even when the referenced DEF is absent."""
        for filename in (r"C:\data\tree.def", r"\\server\share\data\tree.def"):
            with (
                self.subTest(filename=filename),
                patch.object(
                    libprogen, "open", mock_open(read_data="\\0\nmissing.def\n")
                ),
                patch.object(libprogen, "os", SimpleNamespace(path=ntpath, sep="\\")),
                patch.object(ntpath, "exists", return_value=False),
            ):
                self.assertEqual(
                    libprogen._get_defname(filename), (None, "missing.def")
                )

    def test_progen_empty_definition_is_rejected(self) -> None:
        """An empty pointer file is invalid instead of raising IndexError."""
        with patch.object(libprogen, "open", mock_open(read_data="")):
            self.assertEqual(libprogen._get_defname("empty.def"), (None, "empty.def"))

    def test_progen_valid_memo_chain(self) -> None:
        """Acyclic memo text retains its decoding and control-character cleanup."""
        table = object.__new__(libprogen.PG30DefTable)
        self.assertEqual(
            table.get_mem_text([[2, b"Hello\x1b\r"], [0, b"world\x00"]], 1),
            "Hello\nworld",
        )
        self.assertEqual(table.get_mem_text([], 0), "")

    def test_progen_cyclic_and_out_of_range_memos(self) -> None:
        """Memo pointers cannot loop or index outside the supplied records."""
        table = object.__new__(libprogen.PG30DefTable)
        for memos, first in (
            ([[1, b"x"]], 1),
            ([[2, b"x"], [1, b"y"]], 1),
            ([[4, b"x"]], 1),
            ([], 1),
        ):
            with self.subTest(memos=memos), self.assertRaises(libprogen.ProgenError):
                table.get_mem_text(memos, first)
