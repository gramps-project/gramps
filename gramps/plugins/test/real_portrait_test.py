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

TREE = "Test_realportraittest"
PORTRAIT_DIR = os.path.join(os.path.dirname(__file__), "portrait_images")
MASK_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "images", "masks")
)
MEDIA_DIR = os.path.join("temp", "real_portrait_media")
OUT_DIR = "tree_report_output"
REPORT_MASKS = {
    "ancestor_chart": "rectangular_frame_antique_silver.png",
    "descend_chart": "oval_frame_empty.png",
}

# (report, format, output file, subject option, thumb_fit or None)
JOBS = [
    ("ancestor_chart", "svg", "thumbnail_ancestor_shrink.svg", "pid=I0005", None),
    ("ancestor_chart", "svg", "thumbnail_ancestor_crop.svg", "pid=I0005", 1),
    ("ancestor_chart", "svg", "thumbnail_ancestor_stretch.svg", "pid=I0005", 2),
    ("ancestor_chart", "odt", "thumbnail_ancestor.odt", "pid=I0005", None),
    ("ancestor_chart", "pdf", "thumbnail_ancestor.pdf", "pid=I0005", None),
    ("descend_chart", "svg", "thumbnail_descendant.svg", "pid=F0003", None),
    ("descend_chart", "odt", "thumbnail_descendant.odt", "pid=F0003", None),
    ("descend_chart", "pdf", "thumbnail_descendant.pdf", "pid=F0003", None),
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


def move_portrait_reference(db, media_id, source_id, target_id):
    """Move a media reference from one person to another."""
    source = db.get_person_from_gramps_id(source_id)
    target = db.get_person_from_gramps_id(target_id)
    media = db.get_media_from_gramps_id(media_id)
    if source is None or target is None or media is None:
        raise RuntimeError(
            "Could not find person/media records: %s, %s, %s"
            % (source_id, target_id, media_id)
        )

    source.remove_media_references([media.handle])
    media_ref = MediaRef()
    media_ref.set_reference_handle(media.handle)
    target.add_media_reference(media_ref)
    with DbTxn("Move portrait reference", db) as trans:
        db.commit_person(source, trans)
        db.commit_person(target, trans)


def attach_portrait_to_person(db, media_path, person_id, description):
    """Create a media record and attach it to a person."""
    person = db.get_person_from_gramps_id(person_id)
    if person is None:
        raise RuntimeError("Could not find person record: %s" % person_id)

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
            move_portrait_reference(db, "O0003", "I0037", "I0000")
            move_portrait_reference(db, "O0000", "I0001", "I0057")
            move_portrait_reference(db, "O0005", "I0005", "I0015")
            move_portrait_reference(db, "O0001", "I0024", "I0008")
            move_portrait_reference(db, "O0004", "I0040", "I0010")
            attach_portrait_to_person(
                db, "O6.jpg", "I0037", "Portrait of a ten-year-old boy"
            )
        finally:
            db.close()

    @classmethod
    def tearDownClass(cls):
        cls.gramps.run("-y", "--remove", TREE)

    def test_portrait_reports_generate(self):
        """Generate SVG, ODT, and available PDF reports with real portraits."""
        for report, out_format, name, subject, fit in JOBS:
            if out_format == "pdf" and not HAVE_CAIRO:
                continue
            with self.subTest(report=report, format=out_format, file=name):
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
                out, err = self.gramps.run(
                    "--force",
                    "-O",
                    TREE,
                    "--action",
                    "report",
                    "--options",
                    options,
                )
                self.assertNotIn("Failed to write report.", err, out + err)
                self.assertTrue(os.path.isfile(target), out + err)
                self.assertGreater(os.path.getsize(target), 0)
                if out_format == "svg":
                    xml.etree.ElementTree.parse(target)
                    with open(target, encoding="utf-8") as fp:
                        content = fp.read()
                    self.assertIn("data:image/", content)
                    self.assertIn("Smith, Edwin Michael", content)
                    self.assertTrue(
                        svg_embeds_portrait(
                            target, os.path.join(PORTRAIT_DIR, "P7.png")
                        ),
                        "P7.png is not embedded in %s" % name,
                    )
                    if subject == "pid=F0003":
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
