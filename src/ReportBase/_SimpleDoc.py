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
Provides a simplified database access interface to the GRAMPS database.
"""
from types import NoneType
import BaseDoc

class SimpleDoc:
    """
    """

    def __init__(self, doc):
        """
        """
        self.doc = doc

    def __define_styles(self):
        pass

    def __write(self, format, text):
        self.doc.start_paragraph(format)
        self.doc.write_text(text)
        self.doc.end_paragraph()

    def title(self, text):
        """
        """
        self.__write('Title', text)

    def header1(self, text):
        """
        """
        self.__write('Header1', text)

    def header2(self, text):
        """
        """
        self.__write('Header2', text)

    def header3(self, text):
        """
        """
        self.__write('Header3', text)

    def paragraph(self, text):
        """
        """
        self.__write('Normal', text)

def make_basic_stylesheet():
    sheet = BaseDoc.StyleSheet()

    pstyle = BaseDoc.ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(BaseDoc.FONT_SANS_SERIF)
    fstyle.set_size(14)
    fstyle.set_bold(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    sheet.add_paragraph_style('Title', pstyle)

    pstyle = BaseDoc.ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(BaseDoc.FONT_SANS_SERIF)
    fstyle.set_size(12)
    fstyle.set_bold(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
    sheet.add_paragraph_style('Header1', pstyle)

    pstyle = BaseDoc.ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(BaseDoc.FONT_SANS_SERIF)
    fstyle.set_size(10)
    fstyle.set_bold(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
    sheet.add_paragraph_style('Header2', pstyle)

    pstyle = BaseDoc.ParagraphStyle()
    fstyle = pstyle.get_font()
    fstyle.set_type_face(BaseDoc.FONT_SANS_SERIF)
    fstyle.set_size(10)
    fstyle.set_bold(True)
    fstyle.set_italic(True)
    pstyle.set_font(fstyle)
    pstyle.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
    sheet.add_paragraph_style('Header3', pstyle)

    sheet.add_paragraph_style('Normal', BaseDoc.ParagraphStyle())
    return sheet
