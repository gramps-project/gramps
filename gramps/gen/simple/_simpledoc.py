#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Donald N. Allingham
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
Provide a simplified database access interface to the Gramps database.
"""
from ..plug.docgen import StyleSheet, ParagraphStyle, TableStyle,\
                            TableCellStyle,  FONT_SANS_SERIF, PARA_ALIGN_LEFT

class SimpleDoc:
    """
    Provide a simplified database access interface to the Gramps database.
    """

    def __init__(self, doc):
        """
        Initialize the class with the real document
        """
        self.doc = doc

    def __write(self, format, text):
        """
        Writes a paragraph using the specified format to the BaseDoc
        """
        self.doc.start_paragraph(format)
        self.doc.write_text(text)
        self.doc.end_paragraph()

    def title(self, text):
        """
        Writes the Title using the Title paragraph
        """
        self.__write('Title', text)

    def header1(self, text):
        """
        Writes the first level header using the Header1 paragraph
        """
        self.__write('Header1', text)

    def header2(self, text):
        """
        Writes the second level header using the Header2 paragraph
        """
        self.__write('Header2', text)

    def header3(self, text):
        """
        Writes the third level header using the Header3 paragraph
        """
        self.__write('Header3', text)

    def paragraph(self, text):
        """
        Writes a paragraph using the Normal format
        """
        self.__write('Normal', text)

def make_basic_stylesheet(**kwargs):
    """
    Create the basic style sheet for the SimpleDoc class.

    kwargs - a dictionary of the form:
           item={method: value, ...}, ...

    Example:

    make_basic_stylesheet(Table={"set_width": 90})

    """
    sheet = StyleSheet()

    pstyle = ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(FONT_SANS_SERIF)
    fstyle.set_size(14)
    fstyle.set_bold(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(PARA_ALIGN_LEFT)
    # Handle args:
    if "Title" in kwargs:
        for method in kwargs["Title"]:
            value = kwargs["Title"][method]
            if value is not None:
                getattr(pstyle, method)(value)
    sheet.add_paragraph_style('Title', pstyle)

    pstyle = ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(FONT_SANS_SERIF)
    fstyle.set_size(12)
    fstyle.set_bold(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(PARA_ALIGN_LEFT)
    pstyle.set_tabs([4, 8, 12, 16])
    # Handle args:
    if "Header1" in kwargs:
        for method in kwargs["Header1"]:
            value = kwargs["Header1"][method]
            if value is not None:
                getattr(pstyle, method)(value)
    sheet.add_paragraph_style('Header1', pstyle)

    pstyle = ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(FONT_SANS_SERIF)
    fstyle.set_size(10)
    fstyle.set_bold(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(PARA_ALIGN_LEFT)
    pstyle.set_tabs([4, 8, 12, 16])
    # Handle args:
    if "Header2" in kwargs:
        for method in kwargs["Header2"]:
            value = kwargs["Header2"][method]
            if value is not None:
                getattr(pstyle, method)(value)
    sheet.add_paragraph_style('Header2', pstyle)

    pstyle = ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(FONT_SANS_SERIF)
    fstyle.set_size(10)
    fstyle.set_bold(True)
    fstyle.set_italic(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(PARA_ALIGN_LEFT)
    pstyle.set_tabs([4, 8, 12, 16])
    # Handle args:
    if "Header3" in kwargs:
        for method in kwargs["Header3"]:
            value = kwargs["Header3"][method]
            if value is not None:
                getattr(pstyle, method)(value)
    sheet.add_paragraph_style('Header3', pstyle)

    pstyle = ParagraphStyle()
    pstyle.set_tabs([4, 8, 12, 16])
    # Handle args:
    if "Normal" in kwargs:
        for method in kwargs["Normal"]:
            value = kwargs["Normal"][method]
            if value is not None:
                getattr(pstyle, method)(value)
    sheet.add_paragraph_style('Normal', pstyle)

    # Styles for tables:
    tbl = TableStyle()
    tbl.set_width(100)
    tbl.set_columns(2)
    tbl.set_column_width(0,20)
    tbl.set_column_width(1,80)
    # Handle args:
    if "Table" in kwargs:
        for method in kwargs["Table"]:
            value = kwargs["Table"][method]
            if value is not None:
                getattr(tbl, method)(value)
    sheet.add_table_style("Table",tbl)

    cell = TableCellStyle()
    cell.set_top_border(1)
    cell.set_bottom_border(1)
    # Handle args:
    if "TableHead" in kwargs:
        for method in kwargs["TableHead"]:
            value = kwargs["TableHead"][method]
            if value is not None:
                getattr(cell, method)(value)
    sheet.add_cell_style("TableHead",cell)

    cell = TableCellStyle()
    # Handle args:
    if "TableHeaderCell" in kwargs:
        for method in kwargs["TableHeaderCell"]:
            value = kwargs["TableHeaderCell"][method]
            if value is not None:
                getattr(cell, method)(value)
    sheet.add_cell_style("TableHeaderCell",cell)

    cell = TableCellStyle()
    cell.set_longlist(1)
    # Handle args:
    if "TableDataCell" in kwargs:
        for method in kwargs["TableDataCell"]:
            value = kwargs["TableDataCell"][method]
            if value is not None:
                getattr(cell, method)(value)
    sheet.add_cell_style("TableDataCell",cell)

    return sheet
