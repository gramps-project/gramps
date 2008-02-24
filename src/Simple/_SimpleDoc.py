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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Provide a simplified database access interface to the GRAMPS database.
"""
import BaseDoc

class SimpleDoc:
    """
    Provide a simplified database access interface to the GRAMPS database.
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

def make_basic_stylesheet():
    """
    Create the basic style sheet for the SimpleDoc class
    """
    sheet = BaseDoc.StyleSheet()

    pstyle = BaseDoc.ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(BaseDoc.FONT_SANS_SERIF)
    fstyle.set_size(14)
    fstyle.set_bold(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
    sheet.add_paragraph_style('Title', pstyle)

    pstyle = BaseDoc.ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(BaseDoc.FONT_SANS_SERIF)
    fstyle.set_size(12)
    fstyle.set_bold(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
    pstyle.set_tabs([4, 8, 12, 16])
    sheet.add_paragraph_style('Header1', pstyle)

    pstyle = BaseDoc.ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(BaseDoc.FONT_SANS_SERIF)
    fstyle.set_size(10)
    fstyle.set_bold(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
    pstyle.set_tabs([4, 8, 12, 16])
    sheet.add_paragraph_style('Header2', pstyle)

    pstyle = BaseDoc.ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(BaseDoc.FONT_SANS_SERIF)
    fstyle.set_size(10)
    fstyle.set_bold(True)
    fstyle.set_italic(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
    pstyle.set_tabs([4, 8, 12, 16])
    sheet.add_paragraph_style('Header3', pstyle)

    pstyle = BaseDoc.ParagraphStyle()
    pstyle.set_tabs([4, 8, 12, 16])
    sheet.add_paragraph_style('Normal', pstyle)

    # Styles for tables:
    tbl = BaseDoc.TableStyle()
    tbl.set_width(100)
    tbl.set_columns(2)
    tbl.set_column_width(0,20)
    tbl.set_column_width(1,80)
    sheet.add_table_style("Table",tbl)

    cell = BaseDoc.TableCellStyle()
    cell.set_top_border(1)
    cell.set_bottom_border(1)
    sheet.add_cell_style("TableHead",cell)

    cell = BaseDoc.TableCellStyle()
    sheet.add_cell_style("TableNormalCell",cell)

    cell = BaseDoc.TableCellStyle()
    cell.set_longlist(1)
    sheet.add_cell_style("TableListCell",cell)

    return sheet
