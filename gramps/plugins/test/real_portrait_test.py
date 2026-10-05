#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Kevin White
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Integration tests that generate tree reports with real portrait photos."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import base64
import io
import os
import re
import unittest
import uuid
import zipfile
import xml.etree.ElementTree

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import TEST_DIR
from gramps.gen.db.txn import DbTxn
from gramps.gen.lib import Media, MediaRef, Person
from gramps.gen.user import User
from gramps.test.test_util import Gramps

try:
    import cairo

    from gi.repository import Gdk, GdkPixbuf

    HAVE_CAIRO = bool(cairo and Gdk and GdkPixbuf)
except (ImportError, ValueError):
    HAVE_CAIRO = False

TREE = "Test_realportraittest_%s" % uuid.uuid4().hex
PORTRAIT_DIR = os.path.join(os.path.dirname(__file__), "portrait_images")
MASK_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "images", "masks")
)
MEDIA_DIR = os.path.join("temp", "real_portrait_media")
OUT_DIR = os.path.join("test", "data", "tree_report_thumbnails_output")
REPORT_MASKS = {
    "ancestor_chart": "rectangular_frame_antique_silver.png",
    "descend_chart": "oval_frame_empty.png",
}

# (report, format, output file, subject option, thumb_fit or None)
JOBS = [
    ("ancestor_chart", "svg", "thumbnail_ancestor_shrink.svg", "ancestor", None),
    ("ancestor_chart", "svg", "thumbnail_ancestor_crop.svg", "ancestor", 1),
    ("ancestor_chart", "svg", "thumbnail_ancestor_stretch.svg", "ancestor", 2),
    ("ancestor_chart", "odt", "thumbnail_ancestor.odt", "ancestor", None),
    ("ancestor_chart", "pdf", "thumbnail_ancestor.pdf", "ancestor", None),
    ("descend_chart", "svg", "thumbnail_descendant.svg", "descendant", None),
    ("descend_chart", "odt", "thumbnail_descendant.odt", "descendant", None),
    ("descend_chart", "pdf", "thumbnail_descendant.pdf", "descendant", None),
]

PORTRAIT_MEDIA = {
    "P1.png": "O0.jpg",
    "P6.png": "O1.jpg",
    "P3.png": "O2.jpg",
    "P4.png": "O3.jpg",
    "P5.png": "O4.jpg",
    "P2.png": "O5.jpg",
    "P7.png": "O6.jpg",
}


def make_portrait_media(directory):
    """Convert and assign the supplied portraits to fixture media names."""
    from PIL import Image

    os.makedirs(directory, exist_ok=True)
    for portrait, media_name in PORTRAIT_MEDIA.items():
        source = os.path.join(PORTRAIT_DIR, portrait)
        target = os.path.join(directory, media_name)
        with Image.open(source) as image:
            image.convert("RGB").save(target, "JPEG")


def find_person(db, first_name, surname, suffix="", birth_year=None):
    """Find a fixture person by name and optional birth year."""
    matches = []
    for person in db.iter_people():
        name = person.get_primary_name()
        primary_surname = name.get_primary_surname()
        if (
            name.first_name != first_name
            or primary_surname is None
            or primary_surname.surname != surname
            or name.suffix != suffix
        ):
            continue
        if birth_year is not None:
            birth_ref = person.get_birth_ref()
            event = db.get_event_from_handle(birth_ref.ref) if birth_ref else None
            if event is None or event.get_date_object().get_year() != birth_year:
                continue
        matches.append(person)
    if len(matches) != 1:
        raise RuntimeError(
            "Expected one fixture person for %s %s, got %d"
            % (first_name, surname, len(matches))
        )
    return matches[0]


def find_family(db, father, mother):
    """Find a family by its parent records."""
    for family in db.iter_families():
        if (
            family.get_father_handle() == father.handle
            and family.get_mother_handle() == mother.handle
        ):
            return family
    raise RuntimeError("Could not find fixture family for the selected parents")


def move_portrait_reference(db, media_filename, source, target):
    """Move a media reference from one person to another."""
    media = next(
        (
            item
            for item in db.iter_media()
            if os.path.basename(item.get_path()) == media_filename
        ),
        None,
    )
    if media is None:
        raise RuntimeError("Could not find fixture media: %s" % media_filename)

    source.remove_media_references([media.handle])
    media_ref = MediaRef()
    media_ref.set_reference_handle(media.handle)
    target.add_media_reference(media_ref)
    with DbTxn("Move portrait reference", db) as trans:
        db.commit_person(source, trans)
        db.commit_person(target, trans)


def attach_portrait_to_person(db, media_path, person, description):
    """Create a media record and attach it to a person."""
    with DbTxn("Attach portrait to person", db) as trans:
        media = Media()
        media.set_path(media_path)
        media.set_mime_type("image/jpeg")
        media.desc = description
        media_handle = db.add_media(media, trans)
        media_ref = MediaRef()
        media_ref.set_reference_handle(media_handle)
        person.add_media_reference(media_ref)
        db.commit_person(person, trans)


def svg_embeds_portrait(report_path, portrait_path):
    """Check whether an SVG embeds a pixel match for the supplied portrait."""
    from PIL import Image, ImageChops, ImageStat

    with Image.open(portrait_path) as image:
        expected = image.convert("RGB").resize((32, 32))
    with open(report_path, encoding="utf-8") as fp:
        content = fp.read()
    for blob in re.findall(r'xlink:href="data:image/[^;]+;base64,([^"]+)"', content):
        with Image.open(io.BytesIO(base64.b64decode(blob))) as image:
            actual = image.convert("RGB").resize((32, 32))
        difference = ImageStat.Stat(ImageChops.difference(expected, actual))
        if max(difference.mean) < 20:
            return True
    return False


class TestRealPortraitReports(unittest.TestCase):
    """Generate report formats using the committed portrait fixtures."""

    @classmethod
    def setUpClass(cls):
        os.makedirs("temp", exist_ok=True)
        os.makedirs(OUT_DIR, exist_ok=True)
        cls.gramps = Gramps(user=User())
        cls.gramps.run("-y", "--remove", TREE)
        out, err = cls.gramps.run(
            "-C",
            TREE,
            "--import",
            os.path.join(TEST_DIR, "data.gramps"),
            "--config=preferences.iprefix:I%04d",
            "--config=preferences.oprefix:O%04d",
            "--config=preferences.fprefix:F%04d",
            "--config=preferences.sprefix:S%04d",
            "--config=preferences.cprefix:C%04d",
            "--config=preferences.pprefix:P%04d",
            "--config=preferences.eprefix:E%04d",
            "--config=preferences.rprefix:R%04d",
            "--config=preferences.nprefix:N%04d",
        )
        if "Failed to import" in err:
            raise RuntimeError("Could not create portrait test tree: " + out + err)
        make_portrait_media(MEDIA_DIR)
        from gramps.cli.clidbman import CLIDbManager
        from gramps.gen.db.utils import make_database
        from gramps.gen.dbstate import DbState

        trees = dict(CLIDbManager(DbState()).family_tree_list())
        db = make_database("sqlite")
        try:
            db.load(trees[TREE])
            db.set_mediapath(os.path.abspath(MEDIA_DIR))
            cls.tree_path = trees[TREE]
            mason = find_person(db, "Mason Michael", "Smith")
            gustaf = find_person(db, "Gustaf", "Smith", "Sr.")
            edwin = find_person(db, "Edwin Michael", "Smith")
            anna = find_person(db, "Anna", "Hansdotter")
            keith = find_person(db, "Keith Lloyd", "Smith")
            anna_louise = find_person(db, "Anna Louise", "Smith")
            gus = find_person(db, "Gus", "Smith")
            hjalmar = find_person(db, "Hjalmar", "Smith", birth_year=1895)
            marjorie = find_person(db, "Marjorie Alice", "Smith")
            hans_peter = find_person(db, "Hans Peter", "Smith")
            family = find_family(db, gustaf, anna)

            move_portrait_reference(db, "O3.jpg", edwin, anna)
            move_portrait_reference(db, "O0.jpg", keith, anna_louise)
            move_portrait_reference(db, "O5.jpg", mason, gus)
            move_portrait_reference(db, "O1.jpg", gustaf, hjalmar)
            move_portrait_reference(db, "O4.jpg", marjorie, hans_peter)
            attach_portrait_to_person(
                db, "O6.jpg", edwin, "Portrait of a ten-year-old boy"
            )
            cls.ancestor_person_id = mason.gramps_id
            cls.descendant_family_id = family.gramps_id
        finally:
            db.close()

    @classmethod
    def tearDownClass(cls):
        cls.gramps.run("-y", "--remove", TREE)

    def test_portrait_reports_generate(self):
        """Generate SVG, ODT, and available PDF reports with real portraits."""
        from gramps.cli.plug import run_report
        from gramps.gen.db.utils import make_database

        db = make_database("sqlite")
        db.load(self.tree_path)
        db.db_name = TREE
        db.set_mediapath(os.path.abspath(MEDIA_DIR))
        self.addCleanup(db.close)
        for report, out_format, name, subject_type, fit in JOBS:
            if out_format == "pdf" and not HAVE_CAIRO:
                continue
            with self.subTest(report=report, format=out_format, file=name):
                subject = (
                    "pid=%s" % self.ancestor_person_id
                    if subject_type == "ancestor"
                    else "pid=%s" % self.descendant_family_id
                )
                target = os.path.abspath(os.path.join(OUT_DIR, name)).replace("\\", "/")
                if os.path.exists(target):
                    os.unlink(target)
                options = "name=%s,off=%s,of=%s,%s,maxgen=5,inc_thumb=True" % (
                    report,
                    out_format,
                    target,
                    subject,
                )
                mask_path = os.path.join(MASK_DIR, REPORT_MASKS[report]).replace(
                    "\\", "/"
                )
                options += ",mask_path=%s" % mask_path
                if fit is not None:
                    options += ",thumb_fit=%d" % fit
                options_dict = dict(item.split("=", 1) for item in options.split(","))
                options_dict.pop("name")
                report_result = run_report(db, report, **options_dict)
                self.assertIsNotNone(report_result)
                self.assertTrue(
                    os.path.isfile(target), "Report was not created: %s" % target
                )
                self.assertGreater(os.path.getsize(target), 0)
                if out_format == "svg":
                    xml.etree.ElementTree.parse(target)
                    with open(target, encoding="utf-8") as fp:
                        content = fp.read()
                    self.assertIn("data:image/", content)
                    self.assertIn("Smith, Edwin Michael", content)
                    expected_subject = (
                        "Smith, Mason Michael"
                        if subject_type == "ancestor"
                        else "Smith, Gustaf Sr."
                    )
                    self.assertIn(expected_subject, content)
                    self.assertTrue(
                        svg_embeds_portrait(
                            target, os.path.join(PORTRAIT_DIR, "P7.png")
                        ),
                        "P7.png is not embedded in %s" % name,
                    )
                    if subject_type == "descendant":
                        self.assertNotIn(">P7<", content)
                elif out_format == "odt":
                    with zipfile.ZipFile(target) as archive:
                        pictures = [
                            path
                            for path in archive.namelist()
                            if path.startswith("Pictures/")
                        ]
                    self.assertTrue(pictures)
                else:
                    with open(target, "rb") as fp:
                        self.assertTrue(fp.read().startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
