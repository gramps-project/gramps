#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

import os
import tempfile

from TextDoc import *
from latin_utf8 import latin_to_utf8
import const


class AbiWordDoc(TextDoc):

    def __init__(self,type,orientation):
        TextDoc.__init__(self,type,orientation)
        self.f = None
        self.level = 0

    def open(self,filename):

        if filename[-4:] != ".abw":
            self.filename = filename + ".abw"
        else:
            self.filename = filename
            
        self.f = open(filename,"w")
        self.f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
        self.f.write('<abiword version="0.7.13" fileformat="1.0">\n')
        self.f.write('<pagesize ')
        if self.orientation == PAPER_US_LETTER:
            self.f.write('pagetype="Letter" ')
        else:
            self.f.write('pagetype="A4" ')
        if self.orientation == PAPER_PORTRAIT:
            self.f.write('orientation="portrait" ')
        else:
            self.f.write('orientation="landscape" ')
        self.f.write('width="%.4f" ' % (self.width/2.54))
        self.f.write('height="%.4f" ' % (self.height/2.54))
        self.f.write('units="inch" page-scale="1.000000"/>\n')
        self.f.write('<section ')
        rmargin = float(self.rmargin)/2.54
        lmargin = float(self.lmargin)/2.54
        self.f.write('props="page-margin-right:%.4fin; ' % rmargin)
        self.f.write('page-margin-left:%.4fin"' % lmargin)
        self.f.write('>\n')

    def close(self):
        self.f.write('</section>\n')
        self.f.write('</abiword>\n')
        self.f.close()

    def start_paragraph(self,style_name):
        style = self.style_list[style_name]
        self.f.write('<p props="')
        if style.get_alignment() == PARA_ALIGN_RIGHT:
            self.f.write('text-align:right;')
        elif style.get_alignment() == PARA_ALIGN_LEFT:
            self.f.write('text-align:left;')
        elif style.get_alignment() == PARA_ALIGN_CENTER:
            self.f.write('text-align:center;')
        else:
            self.f.write('text-align:justify;')
        rmargin = float(style.get_right_margin())/2.54
        lmargin = float(style.get_left_margin())/2.54
        indent = float(style.get_first_indent())/2.54
        self.f.write(' margin-right:%.4fin;' % rmargin)
        self.f.write(' margin-left:%.4fin;' % lmargin)
        self.f.write(' text-indent:%.4fin' % indent)
        self.f.write('">')
        font = style.get_font()
        self.f.write('<c props="font-family:')
        if font.get_type_face() == FONT_SANS_SERIF:
            self.f.write('Arial;')
        else:
            self.f.write('Times New Roman;')
        self.f.write('font-size:' + str(font.get_size()) + 'pt')
        if font.get_bold():
            self.f.write('; font-weight:bold')
        if font.get_italic():
            self.f.write('; font-style:italic')
        color = font.get_color()
        if color != (0,0,0):
            self.f.write('; color:%2x%2x%2x' % color)
        if font.get_underline():
            self.f.write('; text-decoration:underline' % color)
        self.f.write('">')
                     
    def end_paragraph(self):
        self.f.write('</c></p>\n')

    def write_text(self,text):
	self.f.write(text)

 
if __name__ == "__main__":
    doc = AbiWordDoc(PAPER_US_LETTER,PAPER_PORTRAIT)
    foo = FontStyle()
    foo.set_type_face(FONT_SANS_SERIF)
    foo.set_color((255,0,0))
    foo.set_size(24)

    para = ParagraphStyle()
    para.set_font(foo)
    para.set_alignment(PARA_ALIGN_RIGHT)
    doc.add_style("MyTitle",para)

    para = ParagraphStyle()
    para.set_left_margin(1)
    para.set_right_margin(1)
    para.set_alignment(PARA_ALIGN_JUSTIFY)
    doc.add_style("Normal",para)

    doc.open("/home/dona/oo_test.abw")
    doc.start_paragraph("MyTitle")
    doc.write_text("This is my Title")
    doc.end_paragraph()
    
    doc.start_paragraph("Normal")
    doc.write_text("This is a test of the emergency broadcast system. ")    
    doc.write_text("This is a only a test.  Repeat.  This is only a test. ")    
    doc.write_text("Had this been an actual emergency, we would not be here ")
    doc.write_text("to give you this message.")
    doc.end_paragraph()
    doc.close()

