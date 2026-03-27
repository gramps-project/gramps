#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  Gramps Development Team
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

"""Integration tests for LaTeXDoc: full open/write/close cycle via temp files."""

import os
import tempfile
import unittest

from gramps.gen.plug.docgen import TableCellStyle
from gramps.gen.plug.docgen.paperstyle import PAPER_PORTRAIT, PaperSize, PaperStyle
from gramps.gen.plug.docgen.stylesheet import StyleSheet
from gramps.gen.plug.docgen.tablestyle import TableStyle
from gramps.plugins.docgen.latexdoc import LaTeXDoc


def _make_doc(ncols=2):
    """Return a (LaTeXDoc, StyleSheet) pair with a basic table/cell style."""
    styles = StyleSheet()

    tblstyle = TableStyle()
    tblstyle.set_columns(ncols)
    tblstyle.set_column_widths([100 // ncols] * ncols)
    styles.add_table_style("tbl", tblstyle)

    cstyle = TableCellStyle()
    styles.add_cell_style("cell", cstyle)

    paper = PaperStyle(PaperSize("A4", 29.7, 21.0), PAPER_PORTRAIT)
    return LaTeXDoc(styles, paper), styles


class LaTeXDocIntegrationBase(unittest.TestCase):
    """Base class: creates a temp .tex file, opens the doc, and tears down."""

    ncols = 2

    def setUp(self):
        self.doc, self.styles = _make_doc(self.ncols)
        fd, self.fname = tempfile.mkstemp(suffix=".tex")
        os.close(fd)
        self.doc.open(self.fname)

    def tearDown(self):
        try:
            os.unlink(self.fname)
        except FileNotFoundError:
            pass
        mapping = os.path.join(os.path.dirname(self.fname), "mapping.csv")
        if os.path.exists(mapping):
            os.unlink(mapping)

    def _finish_and_read(self):
        self.doc.close()
        with open(self.fname) as f:
            return f.read()

    def _write_table(self, rows):
        """Helper: rows is list-of-lists of cell text strings."""
        self.doc.start_table("t", "tbl")
        for row_cells in rows:
            self.doc.start_row()
            for text in row_cells:
                self.doc.start_cell("cell")
                self.doc.emit(text)
                self.doc.end_cell()
            self.doc.end_row()
        self.doc.end_table()


class TestDocumentStructure(LaTeXDocIntegrationBase):
    def test_output_contains_documentclass(self):
        content = self._finish_and_read()
        self.assertIn("\\documentclass", content)

    def test_output_ends_with_end_document(self):
        content = self._finish_and_read()
        self.assertIn("\\end{document}", content)

    def test_output_contains_latex_template_packages(self):
        content = self._finish_and_read()
        # The template should include some standard LaTeX infrastructure
        self.assertIn("\\usepackage", content)

    def test_mapping_csv_created(self):
        self._finish_and_read()
        mapping = os.path.join(os.path.dirname(self.fname), "mapping.csv")
        self.assertTrue(os.path.exists(mapping))


class TestTableOutput(LaTeXDocIntegrationBase):
    def test_table_contains_cell_text(self):
        self._write_table([["Hello", "World"]])
        content = self._finish_and_read()
        self.assertIn("Hello", content)
        self.assertIn("World", content)

    def test_table_uses_longtable(self):
        self._write_table([["A", "B"]])
        content = self._finish_and_read()
        self.assertIn("longtable", content)

    def test_table_uses_grinittab(self):
        self._write_table([["A", "B"]])
        content = self._finish_and_read()
        self.assertIn("\\grinittab", content)

    def test_multiple_rows_all_text_present(self):
        self._write_table([["Row1Col1", "Row1Col2"], ["Row2Col1", "Row2Col2"]])
        content = self._finish_and_read()
        for text in ["Row1Col1", "Row1Col2", "Row2Col1", "Row2Col2"]:
            self.assertIn(text, content)

    def test_table_cells_separated_by_ampersand(self):
        self._write_table([["Left", "Right"]])
        content = self._finish_and_read()
        # LaTeX table cells are separated by &
        self.assertIn("&", content)

    def test_empty_cell_text(self):
        self._write_table([["", "something"]])
        content = self._finish_and_read()
        self.assertIn("something", content)

    def test_cell_text_passed_through_emit(self):
        # emit() is a low-level method that does not escape; text is stored as-is.
        # Higher-level callers (write_text) apply latexescape before calling emit.
        self._write_table([["plaintext", "other"]])
        content = self._finish_and_read()
        self.assertIn("plaintext", content)


class TestThreeColumnTable(LaTeXDocIntegrationBase):
    ncols = 3

    def test_three_column_table(self):
        self._write_table([["A", "B", "C"]])
        content = self._finish_and_read()
        for text in ["A", "B", "C"]:
            self.assertIn(text, content)

    def test_grinittab_uses_correct_fraction(self):
        self._write_table([["A", "B", "C"]])
        content = self._finish_and_read()
        # 1/3 columns → repr(1.0/3) appears in grinittab call
        self.assertIn(repr(1.0 / 3), content)


if __name__ == "__main__":
    unittest.main()
