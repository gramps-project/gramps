#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  Gramps Development Team
# Copyright (C) 2026  Doug Blank
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
import shutil
import tempfile
import unittest
from unittest import mock

from gramps.gen.plug.docgen import ParagraphStyle, TableCellStyle
from gramps.gen.plug.docgen.paperstyle import PAPER_PORTRAIT, PaperSize, PaperStyle
from gramps.gen.plug.docgen.stylesheet import StyleSheet
from gramps.gen.plug.docgen.tablestyle import TableStyle
from gramps.plugins.docgen import latexdoc
from gramps.plugins.docgen.latexdoc import NO_PAGE_BREAK, LaTeXDoc


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


# ------------------------------------------------------------
#
# TestPicturesInTables
#
# ------------------------------------------------------------
class TestPicturesInTables(unittest.TestCase):
    """
    Tables of captioned pictures, as written by the Complete Individual
    Report's image gallery (indivcomplete.write_images).
    """

    cells = 3

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._open_doc()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _open_doc(self, subdir=""):
        """Open a new LaTeX document in (a subdir of) the temp dir."""
        styles = StyleSheet()
        for name in ("IDS-Normal", "IDS-SectionTitle", "IDS-ImageCaption"):
            styles.add_paragraph_style(name, ParagraphStyle())
        tblstyle = TableStyle()
        tblstyle.set_columns(self.cells)
        tblstyle.set_column_widths([33, 33, 34])
        styles.add_table_style("IDS-GalleryTable", tblstyle)
        styles.add_cell_style("IDS-TableHead", TableCellStyle())
        styles.add_cell_style("IDS-NormalCell", TableCellStyle())
        paper = PaperStyle(PaperSize("A4", 29.7, 21.0), PAPER_PORTRAIT)
        self.doc = LaTeXDoc(styles, paper)
        self.fname = os.path.join(self.tmpdir, subdir, "report.tex")
        os.makedirs(os.path.dirname(self.fname), exist_ok=True)
        self.doc.open(self.fname)

    def _image(self, name):
        """Return the path of an image file, if PIL can create one."""
        path = os.path.join(os.path.dirname(self.fname), name)
        if latexdoc.HAVE_PIL:
            latexdoc.Image.new("RGB", (40, 20), "blue").save(path)
        return path

    def _gallery(self, images, crop=None):
        """Write a gallery table the way write_images does."""
        self.doc.start_paragraph("IDS-Normal")
        self.doc.write_text("Person")
        self.doc.end_paragraph()
        self.doc.start_table("images", "IDS-GalleryTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", self.cells)
        self.doc.start_paragraph("IDS-SectionTitle")
        self.doc.write_text("Images")
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        for count, image in enumerate(images):
            if count % self.cells == 0:
                self.doc.start_row()
            self.doc.start_cell("IDS-NormalCell")
            self.doc.start_paragraph("IDS-ImageCaption")
            self.doc.write_text("Caption %d" % count)
            self.doc.end_paragraph()
            self.doc.add_media(image, "center", 5.0, 5.0, crop=crop)
            self.doc.end_cell()
            if count % self.cells == self.cells - 1:
                self.doc.end_row()
        if len(images) % self.cells != 0:
            self.doc.end_row()
        self.doc.end_table()

    def _finish_and_read(self):
        self.doc.close()
        with open(self.fname, encoding="utf-8") as fh:
            return fh.read()

    def _check_rows(self, num_images):
        """Each gallery row becomes a caption row and a picture row."""
        rows = self.doc.tabmem.rows
        num_gallery_rows = -(-num_images // self.cells)
        self.assertEqual(len(rows), 1 + 2 * num_gallery_rows)
        for row in rows:
            self.assertEqual(len(row.cells), self.cells)
        self.assertFalse(self.doc.in_multrow_cell)

    def test_short_last_row(self):
        """A last row with fewer pictures than columns is padded."""
        self.doc.close()
        for num_images in (1, 2, 4, 5):
            with self.subTest(num_images=num_images):
                self._open_doc("n%d" % num_images)
                images = [self._image("img%d.jpg" % i) for i in range(num_images)]
                self._gallery(images)
                self._check_rows(num_images)
                content = self._finish_and_read()
                for count in range(num_images):
                    self.assertIn("Caption %d" % count, content)

    def test_full_rows(self):
        """
        Full rows of pictures emit the picture width as text, limited to
        the share of a column.
        """
        images = [self._image("img%d.jpg" % i) for i in range(6)]
        self._gallery(images)
        self._check_rows(6)
        content = self._finish_and_read()
        self.assertIn(
            "\\setlength{\\grpictsize}"
            "{\\minof{5.0\\grbaseindent}{\\grprorated - 2\\tabcolsep}}",
            content,
        )

    def test_section_title_keeps_rows_together(self):
        """The rows after a section title are kept on the same page."""
        self._gallery([self._image("img0.jpg")])
        self.assertTrue(self.doc.tabmem.rows[0].tail.startswith(NO_PAGE_BREAK))
        self._finish_and_read()

    def test_no_file_name_label_in_table(self):
        """
        The report writes the caption, so the picture gets no label, and
        it is fitted into its cell.
        """
        image = self._image("img0.jpg")
        self._gallery([image, image])
        content = self._finish_and_read()
        self.assertIn("\\grcellpicture{%s}{5.0}{5.0}{}" % image, content)
        self.assertNotIn("img0}", content)

    def test_png_without_pil(self):
        """Without PIL, a picture LaTeX can read is used as it is."""
        image = self._image("img0.png")
        with mock.patch.object(latexdoc, "HAVE_PIL", False):
            self._gallery([image, image])
        content = self._finish_and_read()
        self.assertIn("\\grcellpicture{%s}" % image, content)
        self.assertNotIn("*** Error", content)

    def test_unsupported_format_without_pil(self):
        """
        Without PIL, a picture that needs conversion is left out, and the
        error comment is kept out of the table cells.
        """
        image = self._image("img0.gif")
        with (
            mock.patch.object(latexdoc, "HAVE_PIL", False),
            mock.patch("gramps.gen.config.config.get", return_value=True),
            self.assertLogs(".latexdoc", "WARNING"),
        ):
            self._gallery([image, image])
        for row in self.doc.tabmem.rows:
            for cell in row.cells:
                self.assertNotIn("%", cell.content)
        content = self._finish_and_read()
        self.assertNotIn("picture{%s" % self.tmpdir, content)
        self.assertLess(content.index("*** Error"), content.index("\\begin{longtable}"))
        self.assertIn("Caption 1", content)

    def test_missing_file(self):
        """A picture that cannot be read is left out."""
        image = os.path.join(self.tmpdir, "missing.jpg")
        with (
            mock.patch.object(latexdoc, "HAVE_PIL", True),
            mock.patch.object(latexdoc, "Image", create=True) as image_mod,
            self.assertLogs(".latexdoc", "WARNING"),
        ):
            image_mod.open.side_effect = IOError("no such file")
            self._gallery([image])
        content = self._finish_and_read()
        self.assertNotIn("picture{%s" % self.tmpdir, content)
        self.assertIn("*** Error: cannot include %s" % image, content)

    @unittest.skipUnless(latexdoc.HAVE_PIL, "PIL not installed")
    def test_conversion_with_pil(self):
        """A picture LaTeX cannot read is converted to jpg."""
        image = self._image("img0.gif")
        self._gallery([image])
        converted = os.path.join(self.tmpdir, "img0.jpg")
        self.assertTrue(os.path.exists(converted))
        self.assertIn("\\grcellpicture{%s}" % converted, self._finish_and_read())

    @unittest.skipUnless(latexdoc.HAVE_PIL, "PIL not installed")
    def test_crop_with_pil(self):
        """A cropped picture is saved next to the LaTeX file."""
        image = self._image("img0.jpg")
        self._gallery([image], crop=(0, 0, 50, 50))
        cropped = os.path.join(self.tmpdir, "temp_img0.png")
        self.assertTrue(os.path.exists(cropped))
        self.assertIn("\\grcellpicture{%s}" % cropped, self._finish_and_read())

    def test_picture_outside_table(self):
        """
        A picture outside a table keeps its file name label, and the
        indentation it causes ends with the paragraph.
        """
        self.doc.start_paragraph("IDS-Normal")
        self.doc.add_media(self._image("img0.jpg"), "right", 4.0, 4.0)
        self.assertEqual(self.doc.pict_width, 4.0)
        self.doc.write_text("Next to the picture")
        self.doc.end_paragraph()
        self.assertEqual(self.doc.pict_width, 0)
        content = self._finish_and_read()
        self.assertIn("{4.0}{4.0}{img0}", content)

    def test_only_defined_macros(self):
        """Paragraphs and tables only use macros the template defines."""
        self._gallery([self._image("img0.jpg")])
        content = self._finish_and_read()
        self.assertNotIn("\\grparagrtail", content)
        self.assertNotIn("\\grmaxlencolcont", content)
        self.assertIn("\\newcommand{\\grcellpicture}", content)

    def test_photo_beside_table(self):
        """
        A picture in the last column of the first row is set beside the
        table, with the text following it in the cell as its label.
        """
        self.doc.start_paragraph("IDS-Normal")
        self.doc.write_text("Person")
        self.doc.end_paragraph()
        self.doc.start_table("person", "IDS-GalleryTable")
        self.doc.start_row()
        for text in ("Name:", "Somebody"):
            self.doc.start_cell("IDS-NormalCell")
            self.doc.start_paragraph("IDS-Normal")
            self.doc.write_text(text)
            self.doc.end_paragraph()
            self.doc.end_cell()
        self.doc.start_cell("IDS-NormalCell")
        image = self._image("img0.jpg")
        self.doc.add_media(image, "right", 4.0, 4.0)
        self.doc.start_paragraph("IDS-Normal")
        self.doc.write_text("(Age: 50)")
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        self.doc.end_table()
        content = self._finish_and_read()
        self.assertIn("\\grmkpicture{%s}{4.0}{4.0}{(Age: 50)" % image, content)
        self.assertIn("Somebody", content)

    def test_paragraph_in_first_table(self):
        """A table paragraph may come before any other paragraph."""
        self.doc.start_table("images", "IDS-GalleryTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-NormalCell")
        self.doc.start_paragraph("IDS-ImageCaption")
        self.doc.write_text("First")
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        self.doc.end_table()
        self.assertIn("First", self._finish_and_read())


if __name__ == "__main__":
    unittest.main()
