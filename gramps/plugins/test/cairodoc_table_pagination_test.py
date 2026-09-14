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

"""Regression test for bug 6324 (cairo/PDF table cell dropped at a page break).

In the cairo (print/PDF) document backend a table row that lands near the foot
of a page with a cell whose short paragraph has to wrap to a second line was
rendered *torn*: the wrapping cell printed **blank** at the bottom of the page
while its text was pushed onto the next page beside blank copies of the row's
other cells (dsblank, Mantis 6324 -- "the cell prints no text at all").

The pagination invariant is that all cells of a table row begin together: a
cell whose text crosses a page boundary must appear in full across the pages --
either the whole row moves to the next page, or the row splits with every cell
rendering its first lines on the same page as its siblings -- and a cell must
never be left blank while a sibling cell in the same row keeps its text.

This test drives the **production** pagination path -- ``CairoDoc.paginate`` and
the ``GtkDocTable`` / ``GtkDocTableRow`` / ``GtkDocTableCell`` /
``GtkDocParagraph`` ``divide`` chain in
:mod:`gramps.plugins.lib.libcairodoc` -- against a realistic geometry, and
checks that the wrapping cell begins on the same page as its rowmate, that no
line is dropped, and that pagination always terminates.  It covers the four
page-boundary branches the fix touches:

* the wrapping cell is the *last* column (the whole row moves to the next page);
* an *earlier* column splits across the boundary and the later short column must
  split too instead of being left blank beside it;
* a degenerate geometry where the wrapping cell cannot fit even a full empty
  page -- the paginator must force the split and terminate, not spin forever;
* an *unsplittable image* cell in a torn row must move to the next page **intact**
  (never clipped/overflowed into the too-small slot) -- the ``force_split`` vs
  ``allow_overflow`` distinction.

It is headless: Pango lays text out against an in-memory cairo image surface; no
X display, GTK main loop, D-Bus or AT-SPI is used.  (``libcairodoc`` imports
``gramps.gui.utils``, which is explicitly written to import without a DISPLAY.)
"""

import unittest

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo

from gramps.gen.plug.docgen import (
    ParagraphStyle,
    TableStyle,
    TableCellStyle,
    FontStyle,
    FONT_SANS_SERIF,
    PARA_ALIGN_LEFT,
)
from gramps.plugins.lib.libcairodoc import (
    CairoDoc,
    GtkDocDocument,
    GtkDocTable,
    GtkDocTableRow,
    GtkDocTableCell,
    GtkDocParagraph,
    GtkDocPicture,
    fontstyle_to_fontdescription,
)

DPI = 72.0
PAGE_WIDTH = 500.0  # points
FONT_SIZE = 12

# Distinctive opening tokens so a cell's rendered text can be located per page
# regardless of where Pango happens to wrap it.
LABEL_TEXT = "Zlabel"
# A value that wraps to more than one but fewer than four lines in a
# half-page-wide, single-column cell -- the "short cell paragraph" that hits the
# keep-together branch of GtkDocParagraph.divide.
WRAP_TEXT = (
    "Wstart is a long cell value that will wrap onto a second line for sure "
    "yes indeed today"
)
# A value of four or more lines, so it is genuinely split (not kept together)
# when it lands at a page boundary.
TALL_TEXT = (
    "Talpha bravo charlie delta echo foxtrot golf hotel india juliet kilo "
    "lima mike november oscar papa quebec romeo sierra tango uniform victor "
    "whiskey xray yankee zulu one two three four five six seven eight nine ten"
)


class CairoDocTablePaginationTest(unittest.TestCase):
    """A wrapping table cell at a page boundary must not tear its row."""

    def setUp(self):
        # Headless Pango context backed by an in-memory image surface.
        self._surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 4000, 4000)
        self._cr = cairo.Context(self._surface)
        self._context = PangoCairo.font_map_get_default().create_context()
        self._layout = Pango.Layout(self._context)
        PangoCairo.update_layout(self._cr, self._layout)

        self._font = FontStyle()
        self._font.set_type_face(FONT_SANS_SERIF)
        self._font.set_size(FONT_SIZE)

        self._para_style = ParagraphStyle()
        self._para_style.set_font(self._font)
        self._para_style.set_alignment(PARA_ALIGN_LEFT)

    # -- builders ---------------------------------------------------------

    def _cell(self, text):
        """A cell holding one paragraph, or -- if ``text`` is a (w, h) tuple --
        an unsplittable image of that size in cm."""
        cell = GtkDocTableCell(TableCellStyle())
        if isinstance(text, tuple):
            width_cm, height_cm = text
            cell.add_child(GtkDocPicture("left", "unused.png", width_cm, height_cm))
        else:
            paragraph = GtkDocParagraph(ParagraphStyle(self._para_style))
            paragraph.add_text(text)
            cell.add_child(paragraph)
        return cell

    def _row(self, texts):
        """A row with one cell per item in ``texts`` (equal column widths)."""
        widths = [100 // len(texts)] * len(texts)
        row = GtkDocTableRow(widths)
        for text in texts:
            row.add_child(self._cell(text))
        return row

    def _table(self, rows):
        columns = len(rows[0])
        table_style = TableStyle()
        table_style.set_width(100)
        table_style.set_columns(columns)
        for col in range(columns):
            table_style.set_column_width(col, 100 // columns)
        table = GtkDocTable(table_style)
        for texts in rows:
            table.add_child(self._row(texts))
        return table

    # -- production-path measurement -------------------------------------

    def _row_height(self, texts):
        """Full rendered height of a row, via the production ``divide``.

        Dividing with a very large available height fully places the row and
        returns its true height; this is the same code pagination uses, so the
        page geometry below is derived from production, not re-implemented.
        """
        (r1, r2), height = self._row(texts).divide(
            self._layout, PAGE_WIDTH, 100000.0, DPI, DPI
        )
        self.assertIsNotNone(r1)
        self.assertIsNone(r2)
        return height

    def _line_count(self, text, columns=2):
        """Number of wrapped lines of ``text`` at a cell's text width."""
        cell_width = PAGE_WIDTH / columns  # table width is 100%; equal columns
        layout = Pango.Layout(self._context)
        PangoCairo.update_layout(self._cr, layout)
        layout.set_width(int(cell_width * Pango.SCALE))
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        layout.set_font_description(fontstyle_to_fontdescription(self._font))
        layout.set_text(text, -1)
        return layout.get_line_count()

    # -- production paginator (bounded) ----------------------------------

    def _paginate(self, table, page_height, max_iterations=200):
        """Drive the production paginator step in a bounded loop.

        ``CairoDoc.paginate_document`` is ``while not paginate(): pass`` -- an
        unbounded driver.  We call the production ``CairoDoc.paginate`` step
        ourselves with a hard iteration cap so a pagination that fails to make
        progress is REPORTED (``completed`` stays False) instead of hanging the
        suite forever.
        """
        document = GtkDocDocument()
        document.add_child(table)

        doc = CairoDoc.__new__(CairoDoc)
        doc._doc = document
        doc._pages = []
        doc._elements_to_paginate = []

        completed = False
        for _ in range(max_iterations):
            if doc.paginate(self._layout, PAGE_WIDTH, page_height, DPI, DPI):
                completed = True
                break
        return completed, doc._pages

    # -- analysis of the paginated output --------------------------------

    def _page_texts(self, pages):
        """Concatenated rendered ``_plaintext`` per page.

        We read ``_plaintext`` (what ``divide`` actually places and truncates),
        NOT ``_text`` (the untouched source), so a dropped or truncated cell is
        genuinely detectable rather than tautologically present.
        """
        out = []
        for page in pages:
            words = []
            for table in page._children:
                if not isinstance(table, GtkDocTable):
                    continue
                for row in table._children:
                    for cell in row._children:
                        for child in cell._children:
                            if isinstance(child, GtkDocParagraph):
                                words.append(child._plaintext or "")
            out.append(" ".join(words))
        return out

    def _image_pages(self, pages):
        """Indices of pages that actually render an image cell."""
        found = []
        for index, page in enumerate(pages):
            for table in page._children:
                if not isinstance(table, GtkDocTable):
                    continue
                for row in table._children:
                    for cell in row._children:
                        if any(
                            isinstance(child, GtkDocPicture) for child in cell._children
                        ):
                            found.append(index)
        return found

    def _first_page(self, pages, marker):
        """Index of the first page whose rendered text contains ``marker``."""
        for index, text in enumerate(self._page_texts(pages)):
            if marker in text:
                return index
        return None

    def _pages_containing(self, pages, marker):
        return [
            index
            for index, text in enumerate(self._page_texts(pages))
            if marker in text
        ]

    def _assert_no_dropped_words(self, pages, text):
        rendered = " ".join(self._page_texts(pages))
        for word in text.split():
            self.assertIn(
                word,
                rendered,
                "wrapping cell text was dropped from the paginated output "
                "(bug 6324): the word %r is missing" % word,
            )

    # -- the tests --------------------------------------------------------

    def test_wrapping_last_cell_moves_row_whole(self):
        """Last-column wrapping cell at the page foot: the row moves whole.

        Filler rows fill most of the page; the final ``[LABEL, WRAP]`` row lands
        where the one-line LABEL cell fits but the wrapping cell does not.  The
        whole row must move to the next page -- pre-fix the LABEL rendered alone
        with a blank cell beside it while the WRAP text landed a page later
        (Mantis 6324, the torn row).
        """
        # Sanity: WRAP_TEXT must be the "short (2-3 line) cell paragraph" case
        # that takes the keep-together branch; a font substitution making it one
        # line, or four+ lines, would not exercise the bug -- fail loudly.
        self.assertGreaterEqual(self._line_count(WRAP_TEXT), 2)
        self.assertLess(self._line_count(WRAP_TEXT), 4)

        filler_h = self._row_height(["filler a", "filler b"])
        wrap_h = self._row_height([LABEL_TEXT, WRAP_TEXT])
        self.assertGreater(wrap_h, filler_h)  # the wrapping row is taller

        # Page holds three filler rows plus an amount strictly between one line
        # (the LABEL cell) and the full wrapping row: LABEL fits at the bottom,
        # the wrapping cell cannot -- forcing the boundary case.
        page_height = 3 * filler_h + (filler_h + wrap_h) / 2.0

        table = self._table([["filler a", "filler b"]] * 3 + [[LABEL_TEXT, WRAP_TEXT]])
        completed, pages = self._paginate(table, page_height)

        self.assertTrue(completed, "pagination did not terminate (bug 6324)")
        self.assertGreaterEqual(
            len(pages),
            2,
            "geometry did not straddle a page boundary -- the test is not "
            "exercising the wrapping-cell-at-page-bottom case",
        )

        # The row's two cells must begin on the same page: pre-fix the LABEL
        # rendered a page before its wrapping rowmate (the torn row).
        label_page = self._first_page(pages, LABEL_TEXT)
        wrap_page = self._first_page(pages, "Wstart")
        self.assertIsNotNone(label_page)
        self.assertIsNotNone(wrap_page)
        self.assertEqual(
            wrap_page,
            label_page,
            "table row torn at the page boundary (bug 6324): the wrapping cell "
            "begins on page %s but its rowmate LABEL is on page %s"
            % (wrap_page, label_page),
        )
        self._assert_no_dropped_words(pages, WRAP_TEXT)

    def test_wrapping_cell_splits_beside_split_sibling(self):
        """Earlier column splits: the later short column must split too.

        A ``[TALL, WRAP]`` row lands where the four+-line TALL cell splits across
        the boundary but the short WRAP cell (kept-together) cannot fit.  The
        WRAP cell must render its first lines beside TALL rather than blank --
        pre-fix TALL split alone with a blank cell beside it (the same bug in the
        multi-column / cell-split branch).
        """
        self.assertGreaterEqual(self._line_count(WRAP_TEXT), 2)
        self.assertLess(self._line_count(WRAP_TEXT), 4)
        self.assertGreaterEqual(self._line_count(TALL_TEXT), 4)  # genuinely split

        filler_h = self._row_height(["filler a", "filler b"])
        tall_h = self._row_height([TALL_TEXT, WRAP_TEXT])
        line_h = (tall_h - filler_h) / (self._line_count(TALL_TEXT) - 1)

        # One filler row plus about two text lines of room: TALL places two lines
        # and splits, but the three-line WRAP cell cannot fit and would (pre-fix)
        # be left blank beside it.
        page_height = filler_h + 2 * line_h

        table = self._table([["filler a", "filler b"], [TALL_TEXT, WRAP_TEXT]])
        completed, pages = self._paginate(table, page_height)

        self.assertTrue(completed, "pagination did not terminate (bug 6324)")
        self.assertGreaterEqual(len(pages), 2)

        # Precondition: the TALL cell must genuinely split (span >= 2 pages),
        # otherwise this is not the cell-split branch.
        self.assertGreaterEqual(len(self._pages_containing(pages, "Talpha")), 1)
        self.assertGreaterEqual(len(self._pages_containing(pages, "zulu")), 1)
        self.assertGreater(
            self._first_page(pages, "zulu"),
            self._first_page(pages, "Talpha"),
            "the TALL cell did not split across a page boundary -- the test is "
            "not exercising the cell-split branch",
        )

        # The wrapping cell must begin on the same page as the split TALL cell,
        # not a page later beside a blank placeholder (bug 6324).
        tall_page = self._first_page(pages, "Talpha")
        wrap_page = self._first_page(pages, "Wstart")
        self.assertIsNotNone(wrap_page)
        self.assertEqual(
            wrap_page,
            tall_page,
            "table row torn at the page boundary (bug 6324): the wrapping cell "
            "begins on page %s but its splitting rowmate begins on page %s"
            % (wrap_page, tall_page),
        )
        self._assert_no_dropped_words(pages, WRAP_TEXT)

    def test_wrapping_cell_taller_than_page_terminates(self):
        """No-progress guard: a cell that cannot fit even a full page must not

        hang.  With a page barely one line tall, the short (kept-together) WRAP
        cell cannot fit even on a fresh empty page.  Pre-guard the paginator's
        unbounded ``while not paginate()`` loop re-queued the row onto empty page
        after empty page forever; the fix must force the cell to split and always
        terminate, still rendering every word.
        """
        self.assertGreaterEqual(self._line_count(WRAP_TEXT, columns=1), 2)

        filler_h = self._row_height(["filler"])
        wrap_h = self._row_height([WRAP_TEXT])
        line_h = (wrap_h - filler_h) / (self._line_count(WRAP_TEXT, columns=1) - 1)

        # A page about one and a half text lines tall: the multi-line WRAP cell
        # cannot be kept together on any page, so keep-together makes no progress.
        page_height = filler_h + 0.5 * line_h

        table = self._table([[WRAP_TEXT]])
        completed, pages = self._paginate(table, page_height)

        self.assertTrue(
            completed,
            "pagination did not terminate for a cell taller than a page "
            "(bug 6324: no-progress guard missing -- the paginator loops)",
        )
        self._assert_no_dropped_words(pages, WRAP_TEXT)

    def test_image_cell_in_torn_row_moves_intact_not_overflowed(self):
        """Unsplittable image beside a splitting text cell must not be clipped.

        A ``[TALL, image]`` row lands where the four+-line TALL cell splits at
        the boundary but the image does not fit the room left.  An image cannot
        be split; the least-bad rendering is to move it **intact to the next
        page** (blank beside TALL's first lines, full beside TALL's
        continuation) -- NOT to force it into the too-small slot where it would
        overflow/clip past the page edge.

        This guards the ``force_split`` (split splittable content) vs
        ``allow_overflow`` (place an unsplittable element accepting overflow --
        only when a fresh page cannot hold it either) distinction: a merely-torn
        row forces the split but must NOT set allow_overflow, so the image moves
        rather than clips.  A naive single-flag fix that force-placed the image
        here regressed exactly this case.
        """
        self.assertGreaterEqual(self._line_count(TALL_TEXT), 4)  # genuinely split

        filler_h = self._row_height(["filler a", "filler b"])
        tall_h = self._row_height([TALL_TEXT, "filler b"])
        line_h = (tall_h - filler_h) / (self._line_count(TALL_TEXT) - 1)

        # A 2 cm-tall image: larger than the ~2 lines of room left when TALL
        # splits, but comfortably smaller than a full page.
        image_cm = 2.0
        image_pts = image_cm * DPI / 2.54

        # Three filler rows plus ~2 text lines of room: TALL places two lines and
        # splits, the image does not fit the ~2-line remainder, and a full page
        # (3 fillers + 2 lines) easily holds the 2 cm image.
        room = 2 * line_h
        page_height = 3 * filler_h + room
        self.assertGreater(
            page_height,
            image_pts + filler_h,
            "geometry error: a full page must comfortably hold the image "
            "(else this is the taller-than-page case, not the torn-row case)",
        )
        self.assertLess(
            room,
            image_pts,
            "geometry error: the image must NOT fit the room left beside the "
            "split TALL cell (else there is no tear to test)",
        )

        table = self._table(
            [["filler a", "filler b"]] * 3 + [[TALL_TEXT, (4.0, image_cm)]]
        )
        completed, pages = self._paginate(table, page_height)

        self.assertTrue(completed, "pagination did not terminate (bug 6324)")
        self.assertGreaterEqual(len(pages), 2)

        # The TALL cell splits: head on its first page, tail on the next.
        tall_head_page = self._first_page(pages, "Talpha")
        tall_tail_page = self._first_page(pages, "zulu")
        self.assertIsNotNone(tall_head_page)
        self.assertGreater(
            tall_tail_page,
            tall_head_page,
            "the TALL cell did not split -- not exercising the torn-row case",
        )

        # The image must render on exactly one page, and that page must be the
        # TALL *continuation* page (moved intact), never the cramped head page
        # (where placing it would overflow the tiny slot).
        image_pages = self._image_pages(pages)
        self.assertEqual(
            len(image_pages),
            1,
            "the image must render on exactly one page (intact), not be "
            "duplicated or dropped -- got pages %s" % image_pages,
        )
        self.assertNotEqual(
            image_pages[0],
            tall_head_page,
            "bug 6324 regression: the image was force-placed into the too-small "
            "slot on the TALL cell's head page (page %s) where it overflows, "
            "instead of moving intact to the continuation page" % tall_head_page,
        )
        self.assertEqual(
            image_pages[0],
            tall_tail_page,
            "the image should render intact on the TALL continuation page "
            "(page %s) beside its rowmate, but is on page %s"
            % (tall_tail_page, image_pages[0]),
        )


if __name__ == "__main__":
    unittest.main()
