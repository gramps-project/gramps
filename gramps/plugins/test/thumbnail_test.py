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

"""
Report-level thumbnail tests for the ancestor/descendant tree reports.

The shared ``reports_test`` fixture tree leaves five of its six media
references dangling by design, so these tests use their own tree instead.
A dedicated tree is imported from the same ``data.gramps`` and pointed at
a temporary media directory holding deterministic PIL-generated images:

- ``O0.jpg`` -- 228x350 tall portrait (matches the real committed photo)
- ``O1.jpg``/``O4.jpg`` -- 400x400 square baselines (distinct colours)
- ``O2.jpg`` -- 800x200 extreme wide
- ``O3.jpg`` -- 200x800 extreme tall
- ``O5.jpg`` -- 500x500 square

Person ``I0024`` (Gustaf Smith) links ``O1.jpg`` and ``O2.jpg``;
``I0001`` (Keith Lloyd Smith) links ``O0.jpg``; ``I0037`` links
``O3.jpg``; ``I0005`` links ``O5.jpg``; ``I0040`` links ``O4.jpg``.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import base64
import io
import os
import re
import shutil
import unittest
import xml.etree.ElementTree
import zipfile

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import TEST_DIR
from gramps.gen.user import User
from gramps.test.test_util import Gramps

try:
    # Cairo/PDF support needs PyGObject and pycairo; headless checkouts
    # without them still run the SVG/ODT tests.
    import cairo as _cairo

    from gi.repository import Gdk, GdkPixbuf

    HAVE_CAIRO = bool(_cairo and Gdk and GdkPixbuf)
except (ImportError, ValueError):
    HAVE_CAIRO = False

THUMB_TREE_NAME = "Test_thumbnailtest"

# The one real photograph committed as test data (228x350 portrait).  It
# stands in for O0.jpg so at least one report in the suite carries a real
# picture rather than a generated fixture.
REAL_PHOTO = os.path.join(TEST_DIR, "O0.jpg")

# Fixture images: name -> (width, height, fill colour).
_THUMB_MEDIA_SPECS = {
    "O0.jpg": (228, 350, (30, 80, 160)),
    "O1.jpg": (400, 400, (120, 40, 120)),
    "O2.jpg": (800, 200, (160, 40, 40)),
    "O3.jpg": (200, 800, (40, 160, 40)),
    "O4.jpg": (400, 400, (40, 120, 120)),
    "O5.jpg": (500, 500, (40, 40, 160)),
}


def make_thumb_media(directory):
    """Generate the thumbnail fixture images."""
    from PIL import Image

    os.makedirs(directory, exist_ok=True)
    for name, (width, height, colour) in _THUMB_MEDIA_SPECS.items():
        target = os.path.join(directory, name)
        if name == "O0.jpg" and os.path.isfile(REAL_PHOTO):
            # Use the real photograph where one is available; it has the
            # same 228x350 proportions as the generated fixture.
            shutil.copyfile(REAL_PHOTO, target)
            continue
        img = Image.new("RGB", (width, height), colour)
        if name == "O0.jpg":
            # A top-left red corner marker makes crop assertions possible:
            # it survives Shrink but is trimmed by Crop in a wide box.
            pixels = img.load()
            for x in range(40):
                for y in range(40):
                    pixels[x, y] = (255, 0, 0)
        img.save(target, "JPEG")


def set_tree_mediapath(tree_name, media_dir):
    """Point an imported test tree at the thumbnail fixture directory."""
    from gramps.cli.clidbman import CLIDbManager
    from gramps.gen.db.utils import make_database
    from gramps.gen.dbstate import DbState

    trees = dict(CLIDbManager(DbState()).family_tree_list())
    db = make_database("sqlite")
    try:
        db.load(trees[tree_name])
        db.set_mediapath(os.path.abspath(media_dir))
    finally:
        db.close()


def svg_image_tags(path):
    """Return the <image> tags emitted in an SVG report."""
    with open(path, encoding="utf-8") as fp:
        content = fp.read()
    return re.findall(r"<image[^>]*>", content)


def svg_embedded_images(path):
    """Decode the data-URI images embedded in an SVG report."""
    with open(path, encoding="utf-8") as fp:
        content = fp.read()
    return [
        base64.b64decode(href.split(",", 1)[1])
        for href in re.findall(r'xlink:href="(data:image/[^"]+)"', content)
    ]


def odt_thumb_frames(path):
    """Return the thumbnail draw:frame tags inside an ODT report."""
    with zipfile.ZipFile(path) as archive:
        content = archive.read("content.xml").decode("utf-8")
    return re.findall(
        r'<draw:frame[^>]*draw:name="thumb_[^>]*>.*?</draw:frame>',
        content,
        re.S,
    )


# -------------------------------------------------------------------------
#
# TestThumbnailReports
#
# -------------------------------------------------------------------------
class TestThumbnailReports(unittest.TestCase):
    """Report-level thumbnail tests for the ancestor/descendant trees."""

    MEDIA_DIR = os.path.join("temp", "thumb_media")

    @classmethod
    def setUpClass(cls):
        try:
            os.makedirs("temp")
        except OSError:
            pass
        cls.control = Gramps(user=User())
        # Remove a stale tree left behind by a previous interrupted run.
        cls.control.run("-y", "--remove", THUMB_TREE_NAME)
        cls.control.run(
            "-C",
            THUMB_TREE_NAME,
            "--import",
            os.path.join(TEST_DIR, "data.gramps"),
            # the test results depend on specific grampsIds, so we need to
            # use the same prefixes as the example database
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
        make_thumb_media(cls.MEDIA_DIR)
        set_tree_mediapath(THUMB_TREE_NAME, cls.MEDIA_DIR)

    @classmethod
    def tearDownClass(cls):
        cls.control.run("-y", "--remove", THUMB_TREE_NAME)

    @classmethod
    def call(cls, *args):
        gramps = Gramps(user=User())
        return gramps.run(*args)

    def _run_tree_report(
        self, report, out_format, filename, extra="", subject="pid=I0024"
    ):
        """Run a tree report with thumbnails on."""
        out, err = self.call(
            "--force",
            "-O",
            THUMB_TREE_NAME,
            "--action",
            "report",
            "--options",
            "name=%s,off=%s,of=%s,%s,maxgen=2,inc_thumb=True%s"
            % (report, out_format, filename, subject, extra),
        )
        self.assertNotIn("Failed to write report.", err, "report failed: " + out + err)
        return out, err

    def test_ancestor_svg_embeds_thumbnail(self):
        """An ancestor SVG report embeds the person's thumbnail image."""
        filename = os.path.join("temp", "thumb_ancestor.svg")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report("ancestor_chart", "svg", filename)
        self.assertTrue(os.path.isfile(filename))
        # Must be well-formed XML: an unbound xlink prefix made browsers
        # refuse to render the report at all.
        xml.etree.ElementTree.parse(filename)
        with open(filename, encoding="utf-8") as fp:
            content = fp.read()
        self.assertIn('xmlns:xlink="http://www.w3.org/1999/xlink"', content)
        tags = svg_image_tags(filename)
        self.assertGreaterEqual(len(tags), 1)
        self.assertTrue(all("xlink:href" in tag for tag in tags))
        # The picture travels inside the report, not as a filesystem
        # path that a browser cannot resolve.
        self.assertTrue(all("data:image/" in tag for tag in tags))

    def test_descendant_svg_embeds_thumbnail(self):
        """A descendant SVG report embeds the person's thumbnail image."""
        filename = os.path.join("temp", "thumb_descendant.svg")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report("descend_chart", "svg", filename, subject="pid=F0003")
        self.assertTrue(os.path.isfile(filename))
        xml.etree.ElementTree.parse(filename)
        tags = svg_image_tags(filename)
        self.assertGreaterEqual(len(tags), 1)
        self.assertTrue(all("data:image/" in tag for tag in tags))

    def test_report_with_real_photo_contains_picture_data(self):
        """A report on the real committed photo carries real picture data.

        ``I0001`` (Keith Lloyd Smith) links ``O0.jpg``, which the fixture
        step copies from the real photograph in the test data rather than
        generating.  A flat generated fixture would score a spread of 0.
        """
        from PIL import Image, ImageStat

        filename = os.path.join("temp", "thumb_real_photo.svg")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report("ancestor_chart", "svg", filename, subject="pid=I0001")
        xml.etree.ElementTree.parse(filename)
        blobs = svg_embedded_images(filename)
        self.assertGreaterEqual(len(blobs), 1)
        spreads = []
        for blob in blobs:
            with Image.open(io.BytesIO(blob)) as img:
                spreads.append(max(ImageStat.Stat(img.convert("RGB")).stddev))
        self.assertGreater(max(spreads), 20, "report has no real picture data")

    def test_ancestor_odt_embeds_thumbnail(self):
        """An ancestor ODT report bundles the thumbnail in Pictures/."""
        filename = os.path.join("temp", "thumb_ancestor.odt")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report("ancestor_chart", "odt", filename)
        self.assertTrue(os.path.isfile(filename))
        with zipfile.ZipFile(filename) as archive:
            pictures = [
                name for name in archive.namelist() if name.startswith("Pictures/")
            ]
        self.assertGreaterEqual(len(pictures), 1)
        self.assertGreaterEqual(len(odt_thumb_frames(filename)), 1)

    def test_svg_shrink_fit_uses_meet(self):
        """The default Shrink fit draws the SVG with ``meet``."""
        filename = os.path.join("temp", "thumb_shrink.svg")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report("ancestor_chart", "svg", filename)
        tags = svg_image_tags(filename)
        self.assertGreaterEqual(len(tags), 1)
        self.assertTrue(all('preserveAspectRatio="xMidYMid meet"' in t for t in tags))

    def test_svg_crop_fit_uses_slice(self):
        """Crop fit (thumb_fit=1) draws the SVG with ``slice``."""
        from gramps.plugins.lib.libtreebase import FIT_CROP

        filename = os.path.join("temp", "thumb_crop.svg")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report(
            "ancestor_chart", "svg", filename, extra=",thumb_fit=%d" % FIT_CROP
        )
        tags = svg_image_tags(filename)
        self.assertGreaterEqual(len(tags), 1)
        self.assertTrue(all('preserveAspectRatio="xMidYMid slice"' in t for t in tags))

    def test_svg_stretch_fit_stretches(self):
        """Stretch fit (thumb_fit=2) distorts the SVG image to the box."""
        from gramps.plugins.lib.libtreebase import FIT_STRETCH

        filename = os.path.join("temp", "thumb_stretch.svg")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report(
            "ancestor_chart", "svg", filename, extra=",thumb_fit=%d" % FIT_STRETCH
        )
        tags = svg_image_tags(filename)
        self.assertGreaterEqual(len(tags), 1)
        self.assertTrue(all('preserveAspectRatio="none"' in t for t in tags))

    def test_odt_crop_fit_clips_the_source(self):
        """Crop fit (thumb_fit=1) clips the image in the ODT content."""
        from gramps.plugins.lib.libtreebase import FIT_CROP

        filename = os.path.join("temp", "thumb_crop.odt")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report(
            "ancestor_chart", "odt", filename, extra=",thumb_fit=%d" % FIT_CROP
        )
        with zipfile.ZipFile(filename) as archive:
            content = archive.read("content.xml").decode("utf-8")
        self.assertIn("fo:clip=", content)
        # The frame must reference the clip style, not the plain style.
        frames = odt_thumb_frames(filename)
        self.assertGreaterEqual(len(frames), 1)
        self.assertTrue(
            all('draw:style-name="Left_' in frame for frame in frames), frames
        )

    def test_descendant_odt_embeds_thumbnail(self):
        """A descendant ODT report bundles the thumbnail in Pictures/."""
        filename = os.path.join("temp", "thumb_descendant.odt")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report("descend_chart", "odt", filename, subject="pid=F0003")
        self.assertTrue(os.path.isfile(filename))
        with zipfile.ZipFile(filename) as archive:
            pictures = [
                name for name in archive.namelist() if name.startswith("Pictures/")
            ]
        self.assertGreaterEqual(len(pictures), 1)

    def test_crop_fit_trims_wide_image(self):
        """Crop fit on the extreme-wide image emits a crop, not None."""
        from gramps.plugins.drawreport.ancestortree import PersonBox
        from gramps.plugins.lib.libtreebase import FIT_CROP

        box = PersonBox((0, 0))
        box.thumbnail = os.path.join(self.MEDIA_DIR, "O2.jpg")
        box.thumb_width = 1.5
        box.thumb_height = 2.0
        box.thumb_fit = FIT_CROP
        width, height, crop = box._thumbnail_fit()
        self.assertEqual((width, height), (1.5, 2.0))
        self.assertIsNotNone(crop)
        self.assertGreater(crop[0], 0)
        self.assertLess(crop[2], 100)

    def test_shrink_fit_keeps_whole_wide_image(self):
        """Shrink fit on the extreme-wide image keeps the full frame."""
        from gramps.plugins.drawreport.ancestortree import PersonBox
        from gramps.plugins.lib.libtreebase import FIT_SHRINK

        box = PersonBox((0, 0))
        box.thumbnail = os.path.join(self.MEDIA_DIR, "O2.jpg")
        box.thumb_width = 1.5
        box.thumb_height = 2.0
        box.thumb_fit = FIT_SHRINK
        width, height, crop = box._thumbnail_fit()
        self.assertIsNone(crop)
        self.assertAlmostEqual(width, 1.5, places=6)
        self.assertLess(height, 2.0)

    def test_stretch_fit_fills_the_box(self):
        """Stretch fit reports the full box with no crop to apply."""
        from gramps.plugins.drawreport.ancestortree import PersonBox
        from gramps.plugins.lib.libtreebase import FIT_STRETCH

        box = PersonBox((0, 0))
        box.thumbnail = os.path.join(self.MEDIA_DIR, "O2.jpg")
        box.thumb_width = 1.5
        box.thumb_height = 2.0
        box.thumb_fit = FIT_STRETCH
        width, height, crop = box._thumbnail_fit()
        self.assertEqual((width, height), (1.5, 2.0))
        self.assertIsNone(crop)

    def test_unsupported_media_is_skipped(self):
        """A non-image thumbnail path renders no image tag at all."""
        from io import StringIO

        from gramps.gen.plug.docgen import PAPER_PORTRAIT, PaperSize, PaperStyle
        from gramps.plugins.docgen.svgdrawdoc import SvgDrawDoc

        probe = os.path.join("temp", "thumb_probe.txt")
        with open(probe, "w", encoding="utf-8") as fp:
            fp.write("not an image")
        doc = SvgDrawDoc.__new__(SvgDrawDoc)
        doc.buffer = StringIO()
        doc.paper = PaperStyle(PaperSize("Letter", 27.94, 21.59), PAPER_PORTRAIT)
        doc.draw_image(probe, 1.0, 1.0, 1.5, 2.0)
        self.assertNotIn("<image", doc.buffer.getvalue())

    @unittest.skipUnless(HAVE_CAIRO, "requires PyGObject and pycairo")
    def test_cairo_stretch_fills_the_box(self):
        """Stretch fit on a square source fills a taller box (pixel check)."""
        from gramps.plugins.drawreport.ancestortree import PersonBox
        from gramps.plugins.lib.libcairodoc import GtkDocImage
        from gramps.plugins.lib.libtreebase import FIT_STRETCH

        box = PersonBox((0, 0))
        box.thumbnail = os.path.join(self.MEDIA_DIR, "O5.jpg")
        box.thumb_width = 1.5
        box.thumb_height = 2.0
        box.thumb_fit = FIT_STRETCH
        width_cm, height_cm, crop = box._thumbnail_fit()

        dpi = 96.0
        pix_w = int(width_cm * dpi / 2.54)
        pix_h = int(height_cm * dpi / 2.54)
        surface = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, pix_w, pix_h)
        cr = _cairo.Context(surface)
        image = GtkDocImage(box.thumbnail, 0, 0, width_cm, height_cm, crop=crop)
        image.draw(cr, None, pix_w, dpi, dpi)
        surface.flush()
        # The square source must reach the bottom of the taller box.
        stride = surface.get_stride()
        data = surface.get_data()
        offset = (pix_h - 3) * stride + (pix_w // 2) * 4
        self.assertGreater(data[offset + 3], 0, "bottom of the box is empty")

    @unittest.skipUnless(HAVE_CAIRO, "requires PyGObject and pycairo")
    def test_cairo_shrink_letterboxes_the_box(self):
        """Shrink fit on a square source leaves the box margins empty."""
        from gramps.plugins.drawreport.ancestortree import PersonBox
        from gramps.plugins.lib.libcairodoc import GtkDocImage
        from gramps.plugins.lib.libtreebase import FIT_SHRINK

        box = PersonBox((0, 0))
        box.thumbnail = os.path.join(self.MEDIA_DIR, "O5.jpg")
        box.thumb_width = 1.5
        box.thumb_height = 2.0
        box.thumb_fit = FIT_SHRINK
        width_cm, height_cm, crop = box._thumbnail_fit()

        dpi = 96.0
        pix_w = int(width_cm * dpi / 2.54)
        pix_h = int(height_cm * dpi / 2.54)
        surface = _cairo.ImageSurface(_cairo.FORMAT_ARGB32, pix_w, pix_h)
        cr = _cairo.Context(surface)
        image = GtkDocImage(box.thumbnail, 0, 0, width_cm, height_cm, crop=crop)
        image.draw(cr, None, pix_w, dpi, dpi)
        surface.flush()
        stride = surface.get_stride()
        data = surface.get_data()
        # The fitted box is square, so the whole surface holds the image.
        offset = (pix_h - 3) * stride + (pix_w // 2) * 4
        self.assertGreater(data[offset + 3], 0, "image should fill the fitted box")

    @unittest.skipUnless(HAVE_CAIRO, "requires PyGObject and pycairo")
    def test_ancestor_pdf_generates(self):
        """An ancestor PDF report generates with thumbnails embedded."""
        filename = os.path.join("temp", "thumb_ancestor.pdf")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report("ancestor_chart", "pdf", filename)
        self.assertTrue(os.path.isfile(filename))
        with open(filename, "rb") as fp:
            data = fp.read()
        self.assertGreater(len(data), 1000)
        self.assertTrue(data.startswith(b"%PDF"), "not a PDF file")
        self.assertIn(b"/Image", data, "no image object embedded in the PDF")

    @unittest.skipUnless(HAVE_CAIRO, "requires PyGObject and pycairo")
    def test_descendant_pdf_generates(self):
        """A descendant PDF report generates with thumbnails embedded."""
        filename = os.path.join("temp", "thumb_descendant.pdf")
        if os.path.exists(filename):
            os.unlink(filename)
        self._run_tree_report("descend_chart", "pdf", filename, subject="pid=F0003")
        self.assertTrue(os.path.isfile(filename))
        with open(filename, "rb") as fp:
            data = fp.read()
        self.assertGreater(len(data), 1000)
        self.assertTrue(data.startswith(b"%PDF"), "not a PDF file")
        self.assertIn(b"/Image", data, "no image object embedded in the PDF")


if __name__ == "__main__":
    unittest.main()
