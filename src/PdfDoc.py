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

from TextDoc import *

import reportlab.platypus.tables
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import cm
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

import reportlab.lib.styles

def page_def(canvas,doc):
    canvas.saveState()
    canvas.restoreState()

def make_color(color):
    return Color(float(color[0])/255.0, float(color[1])/255.0,
                 float(color[2])/255.0)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class PdfDoc(TextDoc):

    def open(self,filename):
        if filename[-4:] != ".pdf":
            self.filename = filename + ".pdf"
        else:
            self.filename = filename
        self.doc = SimpleDocTemplate(self.filename, 
	                             pagesize=(self.width*cm,self.height*cm))
        self.pdfstyles = {}

        for style_name in self.style_list.keys():
            style = self.style_list[style_name]
            font = style.get_font()

	    pdf_style = reportlab.lib.styles.ParagraphStyle(name=style_name)
            pdf_style.fontSize = font.get_size()
            if font.get_type_face() == FONT_SERIF:
                if font.get_bold():
	            pdf_style.fontName = "Times-Bold"
                else:
	            pdf_style.fontName = "Times-Roman"
            else:
                if font.get_bold():
	            pdf_style.fontName = "Helvetica-Bold"
                else:
	            pdf_style.fontName = "Helvetica"
            pdf_style.rightIndent = style.get_right_margin()*cm
            pdf_style.leftIndent = style.get_left_margin()*cm
            pdf_style.firstLineIndent = style.get_first_indent()*cm
	    align = style.get_alignment()
            if align == PARA_ALIGN_RIGHT:
		pdf_style.alignment = TA_RIGHT
            elif align == PARA_ALIGN_LEFT:
		pdf_style.alignment = TA_LEFT
            elif align == PARA_ALIGN_CENTER:
		pdf_style.alignment = TA_CENTER
            else:
		pdf_style.alignment = TA_JUSTIFY
            pdf_style.spaceBefore = style.get_padding()
            pdf_style.spaceAfter = style.get_padding()
            pdf_style.textColor = make_color(font.get_color())
	    self.pdfstyles[style_name] = pdf_style

	self.story = []
	self.in_table = 0

    def close(self):
        self.doc.build(self.story,onLaterPages=page_def)

    def start_page(self,orientation=None):
        pass

    def end_page(self):
        self.story.append(PageBreak())

    def start_paragraph(self,style_name):
        self.current_para = self.pdfstyles[style_name]
        self.my_para = self.style_list[style_name]
        self.text = ""

    def end_paragraph(self):
        if self.in_table == 0:
	    self.story.append(Paragraph(self.text,self.current_para))
	    self.story.append(Spacer(1,0.5*cm))

    def start_bold(self):
        self.text = self.text + '<b>'

    def end_bold(self):
        self.text = self.text + '</b>'

    def start_table(self,name,style_name):
        self.in_table = 1
        self.cur_table = self.table_styles[style_name]
        self.row = -1
        self.col = 0
        self.cur_row = []
        self.table_data = []

	self.tblstyle = []
        self.cur_table_cols = []
        width = (float(self.cur_table.get_width())/100.0) * self.get_usable_width() * cm
	for val in range(self.cur_table.get_columns()):
            percent = float(self.cur_table.get_column_width(val))/100.0
            self.cur_table_cols.append(width * percent)

    def end_table(self):
        ts = reportlab.platypus.tables.TableStyle(self.tblstyle)
	tbl = reportlab.platypus.tables.Table(data=self.table_data,
                                              colWidths=self.cur_table_cols,
                                              style=ts)
	self.story.append(tbl)
	self.story.append(Spacer(1,0.5*cm))
        self.in_table = 0

    def start_row(self):
	self.row = self.row + 1
        self.col = 0
        self.cur_row = []

    def end_row(self):
        self.table_data.append(self.cur_row)

    def start_cell(self,style_name,span=1):
        self.span = span
        self.my_table_style = self.cell_styles[style_name]
        pass

    def end_cell(self):
        self.cur_row.append(self.text)
        for val in range(1,self.span):
            self.cur_row.append("")

	p = self.my_para
        f = p.get_font()
        if f.get_type_face() == FONT_SANS_SERIF:
            if f.get_bold():
                fn = 'Helvetica-Bold'
            else:
                fn = 'Helvetica'
        else:
            if f.get_bold():
                fn = 'Times-Bold'
            else:
                fn = 'Times-Roman'

        black = Color(0,0,0)
        
        for inc in range(self.col,self.col+self.span):
            loc = (inc,self.row)
            self.tblstyle.append(('FONT', loc, loc, fn, f.get_size()))
            if self.span == 1 or inc == self.col + self.span - 1:
                if self.my_table_style.get_right_border():
                    self.tblstyle.append('LINEAFTER', loc, loc, 1, black)
            if self.span == 1 or inc == self.col:
                if self.my_table_style.get_left_border():
                    self.tblstyle.append('LINEBEFORE', loc, loc, 1, black)
            if self.my_table_style.get_top_border():
                self.tblstyle.append('LINEABOVE', loc, loc, 1, black)
            if self.my_table_style.get_bottom_border():
                self.tblstyle.append('LINEBELOW', loc, loc, 1, black)
            if p.get_alignment() == PARA_ALIGN_LEFT:
                self.tblstyle.append('ALIGN', loc, loc, 'LEFT')
            elif p.get_alignment() == PARA_ALIGN_RIGHT:
                self.tblstyle.append('ALIGN', loc, loc, 'RIGHT')
            else:
                self.tblstyle.append('ALIGN', loc, loc, 'CENTER')
            self.tblstyle.append('VALIGN', loc, loc, 'TOP')

        self.col = self.col + self.span

    def horizontal_line(self):
        pass

    def write_text(self,text):
        self.text = self.text + text

