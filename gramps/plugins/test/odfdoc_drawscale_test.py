#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps developers
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
Regression test for bug #5733: a graphical report's "scale tree to fit" option
scales the boxes of an ODT drawing but not the text inside them.

Graphical tree reports (Ancestor/Descendant chart) draw their boxes through the
document backend's ``draw_box`` / ``draw_text`` / ``center_text``.  When "scale
tree to fit" is chosen the report scales the style sheet's fonts *after*
``doc.init()`` has already run (``gramps/cli/plug/__init__.py`` runs ``init()``
then ``begin_report()``, which calls the report's ``scale_styles``).  The cairo
(PDF) backend reads the font at draw time so its text scales; the ODF backend,
however, wrote fixed named "F<name>" text styles from the unscaled sheet in
``init()`` and referenced them at draw time, so ODT box text stayed at the
original size and overflowed the shrunk boxes.

This test drives the production ODF draw path under an applied scale (exactly
the style-sheet mutation ``descendtree.scale_styles`` performs) and asserts the
font size emitted for the drawn text reflects the scale factor.  The cairo
backend reads the paragraph font at draw time, so its effective rendered size is
``BASE_SIZE * SCALE`` — the value asserted here is therefore also the parity
target, without importing the (GUI-heavy) cairo backend.

It is import-light: it touches only ``gramps.gen`` /
``gramps.plugins.docgen.odfdoc`` and never a GUI toolkit, so it runs headless.
"""

import re
import unittest

from gramps.gen.plug.docgen import (
    FontStyle,
    FONT_SANS_SERIF,
    GraphicsStyle,
    ParagraphStyle,
    PaperSize,
    PaperStyle,
    PAPER_PORTRAIT,
    StyleSheet,
)
from gramps.plugins.docgen.odfdoc import ODFDoc

PARA_NAME = "TestPara"
DRAW_NAME = "TestBox"
BASE_SIZE = 16.0
SCALE = 0.5


def _make_style_sheet(extra_para_names=()):
    """A minimal style sheet with one paragraph style and one draw box style,
    exactly the shape a graphical tree report uses (a draw style whose
    paragraph style carries the box font).  ``extra_para_names`` adds further
    (unused) paragraph styles — used to probe override-name collisions."""
    sheet = StyleSheet()

    font = FontStyle()
    font.set_size(BASE_SIZE)
    font.set_type_face(FONT_SANS_SERIF)
    para = ParagraphStyle()
    para.set_font(font)
    sheet.add_paragraph_style(PARA_NAME, para)

    for name in extra_para_names:
        sheet.add_paragraph_style(name, ParagraphStyle(para))

    box = GraphicsStyle()
    box.set_paragraph_style(PARA_NAME)
    sheet.add_draw_style(DRAW_NAME, box)

    return sheet


def _make_doc(sheet=None):
    paper = PaperStyle(PaperSize("Letter", 27.94, 21.59), PAPER_PORTRAIT)
    doc = ODFDoc(sheet or _make_style_sheet(), paper)
    # open() only records the filename + creates the content buffers; the file
    # is not written until close(), which we do not call.
    doc.open("odfdoc_drawscale_test_output")
    doc.init()
    return doc


def _apply_report_scale(doc, amount, para_name=PARA_NAME):
    """Scale a paragraph font in the document's style sheet, the way a
    graphical report's ``scale_styles`` does after begin_report: fetch the
    sheet, shrink the paragraph font, and set it back on the doc.  This is the
    report -> doc contract (``descendtree.scale_styles``), not a
    reimplementation of the ODF backend."""
    sheet = doc.get_style_sheet()
    para = sheet.get_paragraph_style(para_name)
    font = para.get_font()
    font.set_size(font.get_size() * amount)
    para.set_font(font)
    sheet.add_paragraph_style(para_name, para)
    doc.set_style_sheet(sheet)


def _span_style_for(content, text):
    """The text style-name the drawn <text:span> for ``text`` references."""
    match = re.search(
        r'<text:span text:style-name="([^"]+)">' + re.escape(text) + r"</text:span>",
        content,
    )
    assert match, "no drawn text span found for %r" % text
    return match.group(1)


def _font_size_of(content, style_name):
    """The fo:font-size (pt, float) declared for the named text style."""
    pattern = (
        r'style:name="'
        + re.escape(style_name)
        + r'"\s+style:family="text">\s*'
        + r'<style:text-properties\b[^>]*?fo:font-size="([0-9.]+)pt"'
    )
    match = re.search(pattern, content)
    assert match, "no font-size for text style %r" % style_name
    return float(match.group(1))


class OdfDrawScaleTest(unittest.TestCase):
    def test_scaled_box_text_font_is_scaled(self):
        """Box text drawn after a scale-to-fit is emitted at the scaled font
        size (bug #5733) — parity with the cairo/PDF backend, which renders
        BASE_SIZE * SCALE by reading the same scaled sheet at draw time."""
        doc = _make_doc()
        _apply_report_scale(doc, SCALE)

        doc.draw_box(DRAW_NAME, "Scaled", 0.0, 0.0, 5.0, 2.0)
        doc.finish_cntnt_creation()
        content = doc.cntntx.getvalue()

        span_style = _span_style_for(content, "Scaled")
        emitted = _font_size_of(content, span_style)
        expected = BASE_SIZE * SCALE  # what cairo/PDF renders at draw time

        # The bug: emitted stayed at BASE_SIZE (the unscaled named "F" style).
        self.assertAlmostEqual(
            emitted,
            expected,
            places=2,
            msg=(
                "ODF box text font size %.2fpt is not scaled to %.2fpt "
                "(cairo/PDF renders %.2fpt)" % (emitted, expected, expected)
            ),
        )

    def test_center_text_font_is_scaled(self):
        """The title path (center_text) scales too."""
        doc = _make_doc()
        _apply_report_scale(doc, SCALE)

        doc.center_text(DRAW_NAME, "Title", 3.0, 0.0)
        doc.finish_cntnt_creation()
        content = doc.cntntx.getvalue()

        span_style = _span_style_for(content, "Title")
        self.assertAlmostEqual(
            _font_size_of(content, span_style), BASE_SIZE * SCALE, places=2
        )

    def test_unscaled_output_unchanged(self):
        """Without a scale the drawn span keeps the pre-written named "F"
        style at the base size — no behaviour change for the common case."""
        doc = _make_doc()

        doc.draw_box(DRAW_NAME, "Plain", 0.0, 0.0, 5.0, 2.0)
        doc.finish_cntnt_creation()
        content = doc.cntntx.getvalue()

        span_style = _span_style_for(content, "Plain")
        self.assertEqual(span_style, "F" + PARA_NAME)
        self.assertAlmostEqual(_font_size_of(content, span_style), BASE_SIZE, places=2)

    def test_draw_box_without_paragraph_style_does_not_crash(self):
        """A draw style with no paragraph style set (para name defaults to "")
        must not crash draw_box.  Regression for the KeyError('') the first
        #5733 attempt introduced by resolving the paragraph style eagerly."""
        sheet = _make_style_sheet()
        box = GraphicsStyle()  # leaves the paragraph-style name unset ("")
        sheet.add_draw_style("NoParaBox", box)
        doc = _make_doc(sheet)

        # Must not raise; preserves the original pre-#5733 "F" reference.
        doc.draw_box("NoParaBox", "hello", 0.0, 0.0, 5.0, 2.0)
        doc.finish_cntnt_creation()
        content = doc.cntntx.getvalue()
        self.assertEqual(_span_style_for(content, "hello"), "F")

    def test_scaled_override_name_does_not_collide(self):
        """The generated override name must not collide with an "F<name>" style
        init() wrote for a user paragraph style literally named "Scaled1"
        (which yields "FScaled1") — that would emit a duplicate ODF style
        definition.  Regression for the second #5733-attempt defect."""
        sheet = _make_style_sheet(extra_para_names=("Scaled1",))
        doc = _make_doc(sheet)
        _apply_report_scale(doc, SCALE)

        doc.draw_box(DRAW_NAME, "Boxed", 0.0, 0.0, 5.0, 2.0)
        doc.finish_cntnt_creation()
        content = doc.cntntx.getvalue()

        override = _span_style_for(content, "Boxed")
        # The override must dodge the reserved "FScaled1" (== "F" + "Scaled1").
        self.assertNotEqual(override, "FScaled1")
        # And every emitted text style name must be defined exactly once.
        names = re.findall(r'<style:style style:name="([^"]+)" ', content)
        dupes = {n for n in names if names.count(n) > 1}
        self.assertEqual(dupes, set(), "duplicate ODF style definitions: %s" % dupes)
        # The override still carries the scaled size.
        self.assertAlmostEqual(
            _font_size_of(content, override), BASE_SIZE * SCALE, places=2
        )


if __name__ == "__main__":
    unittest.main()
