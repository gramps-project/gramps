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
Unit tests for the book style collation in
``gramps.gen.plug.report._book`` (Bug 0006128).

A Book Report renders several items into a single shared document that
carries one shared stylesheet (a hard requirement of backends such as ODF,
which emit the whole stylesheet once at ``open()``). Two items of the same
report type define styles under identical names (e.g. two Descendant
Reports both define "DR-Title"). ``append_styles`` used to collate every
item's styles into the flat shared stylesheet keyed by style name, so a
second item's style overwrote the first item's same-named style and BOTH
items then resolved that name to the last-written values -- e.g. an item-1
title configured 14pt and an item-2 title configured 48pt both rendered at
48pt.

These tests drive the real book collation path -- ``add_book_item_styles``
(which calls the production ``append_styles`` and installs the production
``BookItemStyleProxy``) -- against a document that resolves a style name
exactly as the real document backends do, and assert each item keeps its
own configured values. The invariant is checked over:

  * the reported start_paragraph (title) case,
  * write_styled_note (a style-name-bearing TextDoc method every
    REPORT_MODE_BKI textual report uses for notes),
  * draw_box (a DrawDoc style whose *embedded* paragraph reference must
    also stay per-item), and
  * a run-time ``set_style_sheet`` read-modify-write (the pattern
    AncestorTree/DescendTree/FanChart use to compute styles while
    rendering),

over an arbitrary shared style name and more than two items, so the fix is
not special-cased to the "Descendant Report"/"DR-Title" reproduction.
"""

import os
import tempfile
import unittest

from gramps.gen.plug.docgen import StyleSheet, StyleSheetList
from gramps.gen.plug.docgen import ParagraphStyle, FontStyle, GraphicsStyle

# Stable, pre- and post-fix import. ``append_styles`` exists on both trees
# (pre-fix with signature (selected_style, item); post-fix with an added
# prefix="" default), so this import succeeds on the C4-verify red leg too.
from gramps.gen.plug.report._book import append_styles


# -------------------------------------------------------------------------
#
# Test doubles: the minimal book-item interface append_styles consumes, and
# a document that resolves a style by name the way the real backends do.
#
# -------------------------------------------------------------------------
class _FakeHandler:
    """The handler interface ``append_styles`` reads an item's styles through."""

    def __init__(self, savefile, style_name):
        self._savefile = savefile
        self._style_name = style_name
        self.doc = None

    def set_default_stylesheet_name(self, name):
        self._style_name = name

    def get_default_stylesheet_name(self):
        return self._style_name

    def get_stylesheet_savefile(self):
        return self._savefile


class _FakeOptionClass:
    def __init__(self, savefile, style_name, default_para_names):
        self.handler = _FakeHandler(savefile, style_name)
        self._default_para_names = default_para_names

    def make_default_style(self, default_style):
        # A report supplies its own default styles before its saved sheet is
        # read; mirror that so StyleSheetList has a non-empty default sheet.
        for name in self._default_para_names:
            default_style.add_paragraph_style(name, ParagraphStyle())

    def set_document(self, val):
        self.handler.doc = val

    def get_document(self):
        return self.handler.doc


class _FakeBookItem:
    """A stand-in for a configured :class:`~._book.BookItem`."""

    def __init__(self, savefile, style_name, default_para_names):
        self.option_class = _FakeOptionClass(savefile, style_name, default_para_names)

    def get_style_name(self):
        return self.option_class.handler.get_default_stylesheet_name()


class _RecordingDoc:
    """
    A minimal stand-in for a real document backend.

    It resolves a style by name against its current stylesheet exactly as the
    real backends do (cf. ``AsciiDoc.start_paragraph`` and
    ``svgdrawdoc``/``libcairodoc`` draw methods, which read
    ``self.get_style_sheet().get_paragraph_style(name)`` / ``get_draw_style``)
    and records the resolved style, so a test can assert what each item
    actually rendered. Stylesheet storage copies on set/get, matching
    ``BaseDoc``.
    """

    def __init__(self):
        self._style_sheet = StyleSheet()
        self.rendered = []  # (kind, requested-name, resolved-paragraph-style)

    # -- BaseDoc stylesheet storage (copy semantics, like BaseDoc) -----------
    def set_style_sheet(self, style_sheet):
        self._style_sheet = StyleSheet(style_sheet)

    def get_style_sheet(self):
        return StyleSheet(self._style_sheet)

    # -- a couple of no-op methods reports/_reportbase poke at ---------------
    def set_creator(self, name):
        pass

    def set_rtl_doc(self, value):
        pass

    def open(self, filename):
        pass

    # -- TextDoc style-name methods we resolve & record ----------------------
    def start_paragraph(self, style_name, leader=None):
        style = self.get_style_sheet().get_paragraph_style(style_name)
        self.rendered.append(("paragraph", style_name, style))

    def write_styled_note(
        self, styledtext, format, style_name, contains_html=False, links=False
    ):
        style = self.get_style_sheet().get_paragraph_style(style_name)
        self.rendered.append(("note", style_name, style))

    # -- a DrawDoc style-name method: a draw style embeds a paragraph ref ----
    def draw_box(self, style_name, text, x, y, w, h, mark=None):
        ss = self.get_style_sheet()
        box_style = ss.get_draw_style(style_name)
        para = ss.get_paragraph_style(box_style.get_paragraph_style())
        self.rendered.append(("box", style_name, para))


def _para_size(style):
    """Font size of a resolved paragraph style (0 for the default/None case)."""
    return style.get_font().get_size()


# -------------------------------------------------------------------------
#
# Tests
#
# -------------------------------------------------------------------------
class BookStyleCollationTest(unittest.TestCase):
    """Book items with same-named styles must keep their own values (#6128)."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="gramps_book_styles_")

    def tearDown(self):
        for name in os.listdir(self._tmp):
            os.remove(os.path.join(self._tmp, name))
        os.rmdir(self._tmp)

    # -- item builders -------------------------------------------------------
    def _save_sheet(self, index, sheet, default_para_names):
        savefile = os.path.join(self._tmp, "styles_%d.xml" % index)
        style_list = StyleSheetList(savefile, StyleSheet())
        style_list.set_style_sheet("ItemSheet", sheet)
        style_list.save()
        return _FakeBookItem(savefile, "ItemSheet", default_para_names)

    def _make_para_item(self, index, style_name, title_size):
        """An item whose selected sheet defines paragraph ``style_name`` at
        font size ``title_size``."""
        sheet = StyleSheet()
        para = ParagraphStyle()
        font = FontStyle()
        font.set_size(title_size)
        para.set_font(font)
        sheet.add_paragraph_style(style_name, para)
        return self._save_sheet(index, sheet, [style_name])

    def _make_draw_item(self, index, draw_name, para_name, title_size):
        """An item with a draw style ``draw_name`` whose embedded paragraph
        reference (``para_name``) is at font size ``title_size``."""
        sheet = StyleSheet()
        para = ParagraphStyle()
        font = FontStyle()
        font.set_size(title_size)
        para.set_font(font)
        sheet.add_paragraph_style(para_name, para)
        gstyle = GraphicsStyle()
        gstyle.set_paragraph_style(para_name)
        sheet.add_draw_style(draw_name, gstyle)
        return self._save_sheet(index, sheet, [para_name])

    # -- the production collation path ---------------------------------------
    def _collate(self, items):
        """
        Drive the production book style-collation path for ``items`` and return
        ``(doc, item_docs)``: the shared document and, per item, the document
        the item's report writes through.

        With the fix this routes through ``add_book_item_styles`` (per-item
        namespacing + ``BookItemStyleProxy``); without it (C4-verify red leg)
        it reproduces the pre-fix production behaviour -- flat collation onto
        the shared document with the raw document as each item's doc -- so the
        assertions fail on the actual collision.
        """
        try:
            from gramps.gen.plug.report._book import add_book_item_styles
        except ImportError:
            add_book_item_styles = None

        doc = _RecordingDoc()
        selected_style = StyleSheet()
        for item_number, item in enumerate(items):
            if add_book_item_styles is None:
                # Pre-fix production behaviour (cf. cli.plug.cl_book before the
                # fix): flat collation, the raw shared document as the item's doc.
                item.option_class.set_document(doc)
                append_styles(selected_style, item)
            else:
                add_book_item_styles(selected_style, item, doc, item_number)

        doc.set_style_sheet(selected_style)
        item_docs = [item.option_class.get_document() for item in items]
        return doc, item_docs

    # -- tests ---------------------------------------------------------------
    def test_two_same_type_items_keep_distinct_title_sizes(self):
        """The reported case: two Descendant-Report-like items, 14pt vs 48pt."""
        items = [
            self._make_para_item(0, "DR-Title", 14),
            self._make_para_item(1, "DR-Title", 48),
        ]
        doc, item_docs = self._collate(items)
        sizes = []
        for item_doc in item_docs:
            item_doc.start_paragraph("DR-Title")
            sizes.append(_para_size(doc.rendered[-1][2]))
        self.assertEqual(
            sizes,
            [14, 48],
            "each book item must render with its own title style size; "
            "got %r (the second item's style overwrote the first's)" % (sizes,),
        )

    def test_write_styled_note_keeps_per_item_style(self):
        """write_styled_note (used by every BKI textual report for notes) must
        also resolve to each item's own style, not the last-written one."""
        items = [
            self._make_para_item(0, "DDR-Note", 9),
            self._make_para_item(1, "DDR-Note", 33),
        ]
        doc, item_docs = self._collate(items)
        sizes = []
        for item_doc in item_docs:
            item_doc.write_styled_note("hello", 0, "DDR-Note")
            sizes.append(_para_size(doc.rendered[-1][2]))
        self.assertEqual(sizes, [9, 33])

    def test_draw_box_embedded_paragraph_ref_stays_per_item(self):
        """A draw style's embedded paragraph reference must stay per-item, so a
        book of same-type draw reports (AncestorTree/DescendTree) keeps each
        box's text style distinct."""
        items = [
            self._make_draw_item(0, "AC2-box", "AC2-Normal", 11),
            self._make_draw_item(1, "AC2-box", "AC2-Normal", 22),
        ]
        doc, item_docs = self._collate(items)
        sizes = []
        for item_doc in item_docs:
            item_doc.draw_box("AC2-box", "x", 0, 0, 1, 1)
            sizes.append(_para_size(doc.rendered[-1][2]))
        self.assertEqual(sizes, [11, 22])

    def test_runtime_set_style_sheet_is_per_item(self):
        """A report that computes styles at run time (get_style_sheet ->
        modify -> set_style_sheet, the AncestorTree/DescendTree/FanChart
        pattern) must not clobber another item's styles in the shared
        document."""
        items = [
            self._make_para_item(0, "CG-Title", 10),
            self._make_para_item(1, "CG-Title", 10),
        ]
        doc, item_docs = self._collate(items)

        # Item 0's report bumps its own title to 60pt at render time.
        sheet0 = item_docs[0].get_style_sheet()
        para0 = sheet0.get_paragraph_style("CG-Title")
        font0 = para0.get_font()
        font0.set_size(60)
        para0.set_font(font0)
        sheet0.add_paragraph_style("CG-Title", para0)
        item_docs[0].set_style_sheet(sheet0)

        item_docs[0].start_paragraph("CG-Title")
        size0 = _para_size(doc.rendered[-1][2])
        item_docs[1].start_paragraph("CG-Title")
        size1 = _para_size(doc.rendered[-1][2])
        self.assertEqual(
            (size0, size1),
            (60, 10),
            "item 0's run-time style change must not leak into item 1",
        )

    def test_generalizes_beyond_two_items_and_dr_title(self):
        """Not special-cased to "DR-Title"/two items: an arbitrary shared
        style name across three items must still preserve every item's value."""
        items = [
            self._make_para_item(0, "AB-Heading", 10),
            self._make_para_item(1, "AB-Heading", 20),
            self._make_para_item(2, "AB-Heading", 30),
        ]
        doc, item_docs = self._collate(items)
        sizes = []
        for item_doc in item_docs:
            item_doc.start_paragraph("AB-Heading")
            sizes.append(_para_size(doc.rendered[-1][2]))
        self.assertEqual(sizes, [10, 20, 30])


if __name__ == "__main__":
    unittest.main()
