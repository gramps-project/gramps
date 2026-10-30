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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Regression test for bug 6824.

The HTML text-report backend used to write each embedded image's ``<img src>``
as the *absolute* filesystem path of the report's data directory
(``datadirfull()``), so the generated ``.html`` only rendered on the machine
that produced it: copy/share it and every image broke.

This test drives the production ``HtmlDoc.add_media`` path and asserts the
emitted ``src`` is report-relative (the data-subdirectory basename + filename),
carrying no absolute directory prefix, while the on-disk copy still lands in the
absolute ``datadirfull()`` location.
"""

import os
import re
import shutil
import tempfile
import unittest
from unittest import mock

from gramps.gen.plug.docgen import StyleSheet
from gramps.plugins.docgen import htmldoc

# Extract the src of the (first) <img> from a rendered fragment of HTML.
_IMG_SRC = re.compile(r"<img\b[^>]*\bsrc=\"([^\"]*)\"")


class HtmlDocRelativeMediaTest(unittest.TestCase):
    """Exercise HtmlDoc.add_media and inspect the emitted <img src>."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="gramps_htmldoc_")
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)

    def _emit_img_src(self, pos, alt):
        """Open an HtmlDoc, add one media item, and return (src, resize_dest).

        Only the image-resize step is stubbed (so no real image encoder is
        needed); everything else runs the real production code.
        """
        report = os.path.join(self.tmpdir, "myreport.html")
        doc = htmldoc.HtmlDoc(StyleSheet(), None)
        doc.open(report)  # creates the "myreport" data subdirectory on disk

        recorded = {}

        def fake_resize(source, destination, width, height, crop=None):
            recorded["dest"] = destination
            # simulate the encoder writing the resized image to disk
            with open(destination, "w", encoding="utf-8") as handle:
                handle.write("stub-jpeg")

        with mock.patch.object(htmldoc, "resize_to_jpeg", fake_resize):
            doc.add_media(
                os.path.join(self.tmpdir, "photo.jpg"), pos, 4.0, 3.0, alt=alt
            )

        rendered = str(doc.htmllist[-1])
        srcs = _IMG_SRC.findall(rendered)
        self.assertTrue(srcs, "add_media emitted no <img> tag: %r" % rendered)
        return srcs[0], recorded, doc

    def test_add_media_src_is_report_relative(self):
        """The <img src> is report-relative, not the absolute datadirfull()."""
        for pos, alt in (("single", ""), ("right", ""), ("left", ["a caption"])):
            with self.subTest(pos=pos, alt=alt):
                src, recorded, doc = self._emit_img_src(pos, alt)
                datadirfull = doc._backend.datadirfull()

                # The absolute host path must NOT leak into the reference, and
                # the reference must be relative to the document.
                self.assertNotIn(
                    datadirfull,
                    src,
                    "img src carries the absolute datadirfull() path: %r" % src,
                )
                self.assertFalse(
                    os.path.isabs(src),
                    "img src should be report-relative, got absolute: %r" % src,
                )
                # It is exactly the data-subdirectory basename + refname.
                self.assertEqual(src, "myreport/isphoto.jpg")

    def test_copy_destination_stays_absolute(self):
        """The on-disk copy still targets the absolute datadirfull() path."""
        _src, recorded, doc = self._emit_img_src("single", "")
        expected_dest = os.path.join(doc._backend.datadirfull(), "isphoto.jpg")
        self.assertEqual(recorded.get("dest"), expected_dest)
        self.assertTrue(
            os.path.exists(expected_dest),
            "resized image did not land in the datadir: %r" % expected_dest,
        )


if __name__ == "__main__":
    unittest.main()
