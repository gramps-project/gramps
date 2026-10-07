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
"""Exercise portable GEDCOM exports with disposable trees and media."""

# ------------------------
# Python modules
# ------------------------
import gzip
import hashlib
import io
import json
import shutil
import tarfile
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import Mock, patch

# ------------------------
# Gramps modules
# ------------------------
from gramps.cli.user import User
from gramps.gen.db import DbTxn
from gramps.gen.const import TEST_DIR
from gramps.gen.lib import (
    Attribute,
    DNAAttribute,
    DNAMatch,
    DNATest,
    Media,
    MediaRef,
    Note,
    Person,
    Tag,
)
from gramps.gen.proxy import PrivateProxyDb
from gramps.gen.types import MediaHandle
from gramps.plugins.db.dbapi.sqlite import SQLite
from gramps.plugins.importer.importgedcom import importData as import_gedcom
from gramps.plugins.importer.importgpkg import impData as import_package
from gramps.plugins.importer.importxml import importData as import_xml
from gramps.plugins.export.exportxml import XmlWriter

# ------------------------
# Gramps specific
# ------------------------
from .. import exportgedcom


# ------------------------------------------------------------
# PortableGedcomTest
# ------------------------------------------------------------
class PortableGedcomTest(unittest.TestCase):
    """Check export completeness, relocation, filtering and failure safety."""

    def setUp(self) -> None:
        """Create an in-memory tree and isolated source/export directories."""
        self.temporary = tempfile.TemporaryDirectory(prefix="gramps-gedcom-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "originals"
        self.source.mkdir()
        self.destination = self.root / "export"
        self.destination.mkdir()
        self.filename = self.destination / "tree.ged"
        self.database = SQLite()
        self.database.load(":memory:")
        self.addCleanup(self.database.close)
        self.database.set_mediapath(str(self.source))
        self.messages = io.StringIO()
        self.user = User(callback=lambda *args, **kwargs: None, quiet=True)
        self.user._fileout = self.messages

    def add_media(self, path: str, content: bytes = b"medal image") -> MediaHandle:
        """Add a media record and optional file without touching a live tree.

        :param path: Relative, absolute or remote media path.
        :param content: Content for a local fixture file.
        :returns: Handle of the new record.
        """
        if not path.startswith(("http://", "https://")):
            source = self.source / path
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(content)
        media = Media()
        media.set_path(path)
        media.set_mime_type("image/jpeg")
        media.set_description("Synthetic medal")
        with DbTxn("Test fixture", self.database) as transaction:
            return self.database.add_media(media, transaction)

    def export(self, options: Mock | None = None) -> Path:
        """Export through the registered plugin entry point.

        :param options: Optional GUI-style export filters.
        :returns: Companion directory of a successful export.
        """
        before = set(self.destination.iterdir())
        self.assertTrue(
            exportgedcom.export_data(
                self.database, str(self.filename), self.user, options
            ),
            self.messages.getvalue(),
        )
        created = set(self.destination.iterdir()) - before - {self.filename}
        self.assertEqual(len(created), 1)
        return created.pop()

    def package_xml(self, companion: Path) -> ET.Element:
        """Read native data from the recovery package.

        :param companion: Completed export companion directory.
        :returns: Parsed native XML root.
        """
        with tarfile.open(companion / "restore.gpkg") as archive:
            stream = archive.extractfile("data.gramps")
            assert stream is not None
            with stream:
                return ET.fromstring(gzip.decompress(stream.read()))

    def test_media_copies_and_links_survive_relocation(self) -> None:
        """Move the export and import GEDCOM after removing original files."""
        handle = self.add_media("medals/ribbon @ ü.jpg")
        before = self.database.get_media_from_handle(handle).serialize()
        companion = self.export()
        manifest = json.loads((companion / "manifest.json").read_text("utf-8"))
        copied = companion / manifest[0]["path"]
        self.assertEqual(copied.read_bytes(), b"medal image")
        self.assertEqual(
            manifest[0]["sha256"], hashlib.sha256(b"medal image").hexdigest()
        )
        self.assertEqual(
            self.database.get_media_from_handle(handle).serialize(), before
        )
        self.assertEqual(
            (self.source / "medals/ribbon @ ü.jpg").read_bytes(), b"medal image"
        )
        moved = self.root / "moved"
        shutil.move(str(self.destination), moved)
        shutil.rmtree(self.source)
        restored = SQLite()
        restored.load(":memory:")
        self.addCleanup(restored.close)
        import_gedcom(restored, str(moved / "tree.ged"), self.user)
        self.assertEqual(restored.get_number_of_media(), 1)
        imported = restored.get_media_from_handle(restored.get_media_handles()[0])
        self.assertEqual(Path(imported.get_path()).read_bytes(), b"medal image")

    def test_native_data_and_media_reference_are_preserved(self) -> None:
        """Restore Gramps tags, custom attributes, notes and crop rectangles."""
        handle = self.add_media("ribbon.jpg")
        media = self.database.get_media_from_handle(handle)
        attribute = Attribute()
        attribute.set_type("Medal provenance")
        attribute.set_value("Original award certificate")
        media.add_attribute(attribute)
        note = Note()
        note.set("Native research note")
        tag = Tag()
        tag.set_name("Verified award")
        person = Person()
        person.get_primary_name().set_first_name("Synthetic")
        reference = MediaRef()
        reference.set_reference_handle(handle)
        reference.set_rectangle((10, 20, 80, 90))
        person.add_media_reference(reference)
        with DbTxn("Native data fixture", self.database) as transaction:
            note_handle = self.database.add_note(note, transaction)
            tag_handle = self.database.add_tag(tag, transaction)
            media.add_note(note_handle)
            media.add_tag(tag_handle)
            self.database.commit_media(media, transaction)
            self.database.add_person(person, transaction)
        companion = self.export()
        xml = self.package_xml(companion)
        namespace = {"g": xml.tag.partition("}")[0][1:]}
        attribute_element = xml.find(".//g:attribute", namespace)
        assert attribute_element is not None
        self.assertEqual(attribute_element.attrib["value"], attribute.get_value())
        recovered = SQLite()
        recovered.load(":memory:")
        self.addCleanup(recovered.close)
        recovered.set_mediapath(str(self.root))
        recovered.set_feature("skip-import-additions", True)
        import_package(recovered, str(companion / "restore.gpkg"), self.user)
        recovered_media = recovered.get_media_from_handle(
            recovered.get_media_handles()[0]
        )
        self.assertEqual(
            recovered_media.get_attribute_list()[0].get_value(), attribute.get_value()
        )
        self.assertEqual(recovered.get_number_of_tags(), 1)
        self.assertEqual(recovered.get_number_of_notes(), 1)
        recovered_person = recovered.get_person_from_handle(
            recovered.get_person_handles()[0]
        )
        self.assertEqual(
            recovered_person.get_media_list()[0].get_rectangle(), (10, 20, 80, 90)
        )
        extracted = self.root / "restore.gpkg.media" / recovered_media.get_path()
        self.assertEqual(extracted.read_bytes(), b"medal image")

    def test_duplicate_basenames_do_not_collide(self) -> None:
        """Retain different files with identical names in separate directories."""
        self.add_media("one/medal.jpg", b"first")
        self.add_media("two/medal.jpg", b"second")
        companion = self.export()
        manifest = json.loads((companion / "manifest.json").read_text("utf-8"))
        self.assertEqual(
            {(companion / entry["path"]).read_bytes() for entry in manifest},
            {b"first", b"second"},
        )

    def test_filters_apply_to_media_and_recovery_data(self) -> None:
        """Excluded private data must not appear in either exported format."""
        self.add_media("public.jpg")
        hidden_handle = self.add_media("private.jpg")
        hidden = self.database.get_media_from_handle(hidden_handle)
        hidden.set_privacy(True)
        hidden.set_description("Private award details")
        private_person = Person()
        private_person.get_primary_name().set_first_name("Excluded private person")
        private_person.set_privacy(True)
        private_note = Note()
        private_note.set("Excluded private research")
        private_note.set_privacy(True)
        public = self.database.get_media_from_handle(
            self.database.get_media_handles()[0]
        )
        if public.get_handle() == hidden_handle:
            public = self.database.get_media_from_handle(
                self.database.get_media_handles()[1]
            )
        with DbTxn("Private fixture", self.database) as transaction:
            self.database.commit_media(hidden, transaction)
            self.database.add_person(private_person, transaction)
            private_note_handle = self.database.add_note(private_note, transaction)
            public.add_note(private_note_handle)
            self.database.commit_media(public, transaction)
        (self.source / "private.jpg").unlink()
        options = Mock()
        options.get_filtered_database.return_value = PrivateProxyDb(self.database)
        companion = self.export(options)
        options.parse_options.assert_called_once()
        self.assertNotIn("Private award details", self.filename.read_text("utf-8"))
        self.assertNotIn(
            b"Private award details", ET.tostring(self.package_xml(companion))
        )
        for secret in ("Excluded private person", "Excluded private research"):
            self.assertNotIn(secret, self.filename.read_text("utf-8"))
            self.assertNotIn(secret.encode(), ET.tostring(self.package_xml(companion)))
        self.assertEqual(
            len(json.loads((companion / "manifest.json").read_text("utf-8"))), 1
        )

    def test_failure_preserves_existing_export(self) -> None:
        """Missing media must fail without truncating an existing GEDCOM."""
        self.add_media("missing.jpg")
        (self.source / "missing.jpg").unlink()
        self.filename.write_text("previous successful export", encoding="utf-8")
        self.assertFalse(
            exportgedcom.export_data(self.database, str(self.filename), self.user)
        )
        self.assertEqual(self.filename.read_text("utf-8"), "previous successful export")
        self.assertEqual(list(self.destination.iterdir()), [self.filename])

    def test_remote_media_requires_local_storage(self) -> None:
        """Remote links must not masquerade as included media files."""
        self.add_media("https://example.invalid/medal.jpg")
        self.assertFalse(
            exportgedcom.export_data(self.database, str(self.filename), self.user)
        )
        self.assertEqual(list(self.destination.iterdir()), [])
        self.assertIn("local", self.messages.getvalue())

    def test_destination_cannot_overwrite_original_media(self) -> None:
        """Protect original bytes if a media file is selected as destination."""
        self.add_media(str(self.filename), b"original media")
        self.assertFalse(
            exportgedcom.export_data(self.database, str(self.filename), self.user)
        )
        self.assertEqual(self.filename.read_bytes(), b"original media")

    def test_copy_failure_does_not_publish_partial_export(self) -> None:
        """Disk/copy failures leave no successful-looking GEDCOM or companion."""
        self.add_media("medal.jpg")
        with patch.object(
            exportgedcom.shutil, "copyfile", side_effect=OSError("disk full")
        ):
            self.assertFalse(
                exportgedcom.export_data(self.database, str(self.filename), self.user)
            )
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_recovery_failure_preserves_previous_export(self) -> None:
        """Native serialization must finish before replacing the GEDCOM."""
        self.add_media("medal.jpg")
        self.filename.write_text("previous export", encoding="utf-8")
        with patch.object(
            exportgedcom.XmlWriter, "write_handle", side_effect=OSError("disk full")
        ):
            self.assertFalse(
                exportgedcom.export_data(self.database, str(self.filename), self.user)
            )
        self.assertEqual(self.filename.read_text("utf-8"), "previous export")
        self.assertEqual(list(self.destination.iterdir()), [self.filename])

    def test_empty_tree_still_has_native_recovery(self) -> None:
        """A tree without media still receives a complete native companion."""
        companion = self.export()
        self.assertTrue((companion / "restore.gpkg").is_file())
        self.assertTrue(self.filename.read_text("utf-8").endswith("0 TRLR\n"))
        self.assertEqual(
            json.loads((companion / "manifest.json").read_text("utf-8")), []
        )

    def test_master_dna_records_survive_native_recovery(self) -> None:
        """Native DNA records, attributes and bookmarks survive the wrapper."""
        test = DNATest()
        test.set_account_name("Synthetic DNA account")
        test.set_kit_id("SYNTHETIC-KIT")
        attribute = DNAAttribute()
        attribute.set_type("Synthetic provenance")
        attribute.set_value("Preserved DNA attribute")
        test.add_attribute(attribute)
        match = DNAMatch()
        match.set_shared_cm(123.5)
        with DbTxn("Synthetic DNA", self.database) as transaction:
            handle = self.database.add_dnatest(test, transaction)
            match.set_subject_test_handle(handle)
            match_handle = self.database.add_dnamatch(match, transaction)
        self.database.dnatest_bookmarks.append(handle)
        self.database.dnamatch_bookmarks.append(match_handle)
        companion = self.export()
        xml = self.package_xml(companion)
        namespace = {"g": xml.tag.partition("}")[0][1:]}
        self.assertEqual(len(xml.findall("g:dnatests/g:dnatest", namespace)), 1)
        self.assertEqual(len(xml.findall("g:dnamatches/g:dnamatch", namespace)), 1)
        self.assertIn(b"Preserved DNA attribute", ET.tostring(xml))
        restored = SQLite()
        restored.load(":memory:")
        self.addCleanup(restored.close)
        restored.set_mediapath(str(self.root))
        self.assertIsNotNone(
            import_package(restored, str(companion / "restore.gpkg"), self.user)
        )
        self.assertEqual(restored.get_number_of_dnatests(), 1)
        self.assertEqual(restored.get_number_of_dnamatches(), 1)
        self.assertEqual(
            restored.get_dnatest_from_handle(handle).get_kit_id(), "SYNTHETIC-KIT"
        )
        self.assertEqual(
            restored.get_dnatest_from_handle(handle)
            .get_attribute_list()[0]
            .get_value(),
            "Preserved DNA attribute",
        )
        self.assertEqual(
            restored.get_dnamatch_from_handle(match_handle).get_shared_cm(), 123.5
        )
        self.assertEqual(restored.dnatest_bookmarks.get(), [handle])
        self.assertEqual(restored.dnamatch_bookmarks.get(), [match_handle])

    def test_filtered_dna_fails_without_replacing_previous_export(self) -> None:
        """Unsupported master DNA filtering cannot leak data or replace output."""
        self.filename.write_bytes(b"previous export")
        options = Mock()
        options.get_filtered_database.return_value = PrivateProxyDb(self.database)
        for test_count, match_count in ((1, 0), (0, 1)):
            with (
                self.subTest(tests=test_count, matches=match_count),
                patch.object(
                    self.database, "get_number_of_dnatests", return_value=test_count
                ),
                patch.object(
                    self.database, "get_number_of_dnamatches", return_value=match_count
                ),
                patch.object(self.database, "get_dnatest_handles") as tests,
                patch.object(self.database, "get_dnamatch_handles") as matches,
            ):
                self.assertFalse(
                    exportgedcom.export_data(
                        self.database, str(self.filename), self.user, options
                    )
                )
                tests.assert_not_called()
                matches.assert_not_called()
                self.assertEqual(self.filename.read_bytes(), b"previous export")
                self.assertEqual(list(self.destination.iterdir()), [self.filename])
        self.assertIn("DNA", self.messages.getvalue())

    def test_filtered_non_dna_bookmarks_still_export(self) -> None:
        """Empty DNA tables do not break an otherwise filtered bookmarked tree."""
        person = Person()
        with DbTxn("Synthetic bookmark", self.database) as transaction:
            handle = self.database.add_person(person, transaction)
        self.database.bookmarks.append(handle)
        options = Mock()
        options.get_filtered_database.return_value = PrivateProxyDb(self.database)
        self.export(options)

    def test_repeated_exports_preserve_previous_media(self) -> None:
        """Re-exporting uses a new companion and keeps previous copies intact."""
        self.add_media("medal.jpg", b"old version")
        old = self.export()
        (self.source / "medal.jpg").write_bytes(b"updated version")
        new = self.export()
        self.assertNotEqual(old, new)
        self.assertEqual(next((old / "media").iterdir()).read_bytes(), b"old version")
        self.assertEqual(
            next((new / "media").iterdir()).read_bytes(), b"updated version"
        )

    def test_sample_preserves_all_native_record_types(self) -> None:
        """Compare the companion's native data to a full native sample export."""
        self.database.set_mediapath("")
        import_xml(self.database, str(Path(TEST_DIR) / "exp_sample.gramps"), self.user)
        companion = self.export()
        actual = self.package_xml(companion)
        with io.BytesIO() as output:
            XmlWriter(self.database, self.user, 0).write_handle(output)
            expected = ET.fromstring(gzip.decompress(output.getvalue()))
        namespace = {"g": actual.tag.partition("}")[0][1:]}
        header = expected.find("g:header", namespace)
        media_base = expected.find("g:header/g:mediapath", namespace)
        assert header is not None and media_base is not None
        header.remove(media_base)
        for element in (expected, actual):
            for child in element.iter():
                if child.tail and not child.tail.strip():
                    child.tail = None
        # Only media locations change; all other native content remains equal.
        for original, portable in zip(
            expected.findall("g:objects/g:object/g:file", namespace),
            actual.findall("g:objects/g:object/g:file", namespace),
        ):
            original.set("src", portable.attrib["src"])
        self.assertEqual(ET.tostring(actual), ET.tostring(expected))
        self.assertGreater(len(actual.findall("g:people/g:person", namespace)), 1)
        self.assertGreater(len(actual.findall("g:events/g:event", namespace)), 1)
        self.assertGreater(len(actual.findall("g:citations/g:citation", namespace)), 1)

    def test_corrupt_copy_is_rejected(self) -> None:
        """Detect a copy whose bytes do not match the original media."""
        self.add_media("medal.jpg")
        with patch.object(
            exportgedcom.shutil,
            "copyfile",
            side_effect=lambda source, target: Path(target).write_bytes(b"corrupt"),
        ):
            self.assertFalse(
                exportgedcom.export_data(self.database, str(self.filename), self.user)
            )
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_publication_failure_preserves_existing_export(self) -> None:
        """A locked destination must not lose its previous contents."""
        self.add_media("medal.jpg")
        self.filename.write_text("previous export", encoding="utf-8")
        with patch.object(
            exportgedcom.os, "replace", side_effect=PermissionError("locked")
        ):
            self.assertFalse(
                exportgedcom.export_data(self.database, str(self.filename), self.user)
            )
        self.assertEqual(self.filename.read_text("utf-8"), "previous export")
        self.assertEqual(list(self.destination.iterdir()), [self.filename])

    def test_media_change_during_copy_is_rejected(self) -> None:
        """Abort rather than exporting stale bytes when a source file changes."""
        self.add_media("medal.jpg")
        original_copy = exportgedcom.shutil.copyfile

        def cb_changing_copy(source: str, target: str) -> None:
            """Copy the fixture and simulate its replacement during export.

            :param source: Original fixture path.
            :param target: Staged media destination.
            """
            original_copy(source, target)
            Path(source).write_bytes(b"changed source")

        with patch.object(
            exportgedcom.shutil, "copyfile", side_effect=cb_changing_copy
        ):
            self.assertFalse(
                exportgedcom.export_data(self.database, str(self.filename), self.user)
            )
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_gui_summary_names_companion_directory(self) -> None:
        """The GUI completion message tells the user which folder to keep."""
        options = Mock(spec=exportgedcom.GedcomOptionBox)
        options.get_filtered_database.return_value = self.database
        companion = self.export(options)
        self.assertIn(str(companion), options.export_message)
        self.assertIn("restore.gpkg", options.export_message)


if __name__ == "__main__":
    unittest.main()
