#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import BaseDoc
import Plugins
import Errors
import ImgManip
from gettext import gettext as _

_H = 'Helvetica'
_HB = 'Helvetica-Bold'
_T = 'Times-Roman'
_TB = 'Times-Bold'

#------------------------------------------------------------------------
#
# ReportLab python/PDF modules
#
#------------------------------------------------------------------------

try:
    import reportlab.platypus.tables
    from reportlab.platypus import *
    from reportlab.lib.units import cm
    from reportlab.lib.colors import Color
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
    from reportlab.graphics.shapes import *
    import reportlab.lib.styles
except ImportError:
    raise Errors.PluginError( _("The ReportLab modules are not installed"))

#------------------------------------------------------------------------
#
# GrampsDocTemplate
#
#------------------------------------------------------------------------
class GrampsDocTemplate(BaseDocTemplate):
    """A document template for the ReportLab routines."""
    
    def build(self,flowables):
        """Override the default build routine, to recalculate
        for any changes in the document (margins, etc.)"""
        self._calc()	
        BaseDocTemplate.build(self,flowables)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class PdfDoc(BaseDoc.BaseDoc):

    def open(self,filename):
        if filename[-4:] != ".pdf":
            self.filename = "%s.pdf" % filename
        else:
            self.filename = filename
            
        self.pagesize = (self.width*cm,self.height*cm)

        self.doc = GrampsDocTemplate(self.filename, 
	                             pagesize=self.pagesize,
                                     allowSplitting=1,
                                     _pageBreakQuick=0,
                                     leftMargin=self.lmargin*cm,
                                     rightMargin=self.rmargin*cm,
                                     topMargin=self.tmargin*cm,
                                     bottomMargin=self.bmargin*cm)
        frameT = Frame(0,0,self.width*cm,self.height*cm,
                       self.lmargin*cm, self.bmargin*cm, 
                       self.rmargin*cm,self.tmargin*cm,
                       id='normal')
        ptemp = PageTemplate(frames=frameT,pagesize=self.pagesize)
        self.doc.addPageTemplates([ptemp])

        self.pdfstyles = {}

        for style_name in self.style_list.keys():
            style = self.style_list[style_name]
            font = style.get_font()

	    pdf_style = reportlab.lib.styles.ParagraphStyle(name=style_name)
            pdf_style.fontSize = font.get_size()
            pdf_style.bulletFontSize = font.get_size()
            
            if font.get_type_face() == BaseDoc.FONT_SERIF:
                if font.get_bold():
                    if font.get_italic():
                        pdf_style.fontName = "Times-BoldItalic"
                    else:
                        pdf_style.fontName = "Times-Bold"
                else:
                    if font.get_italic():
                        pdf_style.fontName = "Times-Italic"
                    else:
                        pdf_style.fontName = "Times-Roman"
            else:
                if font.get_bold():
                    if font.get_italic():
                        pdf_style.fontName = "Helvetica-BoldOblique"
                    else:
                        pdf_style.fontName = "Helvetica-Bold"
                else:
                    if font.get_italic():
                        pdf_style.fontName = "Helvetica-Oblique"
                    else:
                        pdf_style.fontName = "Helvetica"
            pdf_style.bulletFontName = pdf_style.fontName

            right = style.get_right_margin()*cm
            left = style.get_left_margin()*cm
            first = left + style.get_first_indent()*cm

            pdf_style.rightIndent = right
            pdf_style.leftIndent = left
            pdf_style.firstLineIndent = first
            pdf_style.bulletIndent = first

	    align = style.get_alignment()
            if align == BaseDoc.PARA_ALIGN_RIGHT:
		pdf_style.alignment = TA_RIGHT
            elif align == BaseDoc.PARA_ALIGN_LEFT:
		pdf_style.alignment = TA_LEFT
            elif align == BaseDoc.PARA_ALIGN_CENTER:
		pdf_style.alignment = TA_CENTER
            else:
		pdf_style.alignment = TA_JUSTIFY
            pdf_style.spaceBefore = style.get_padding()*cm
            pdf_style.spaceAfter = style.get_padding()*cm
            pdf_style.textColor = make_color(font.get_color())
	    self.pdfstyles[style_name] = pdf_style

	self.story = []
	self.in_table = 0

    def close(self):
        try:
            self.doc.build(self.story)
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise Errors.ReportError(errmsg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.filename)

    def page_break(self):
        self.story.append(PageBreak())

    def start_paragraph(self,style_name,leader=None):
        self.current_para = self.pdfstyles[style_name]
        self.my_para = self.style_list[style_name]
        self.super = "<font size=%d><super>" % (self.my_para.get_font().get_size()-2)
        if leader==None:
            self.text = ''
        else:
            self.text = '<bullet>%s</bullet>' % leader
        self.image = 0

    def end_paragraph(self):
        if self.in_table == 0 and self.image == 0:
	    self.story.append(Paragraph(self.text,self.current_para))
        else:
            self.image = 0

    def start_bold(self):
        self.text = self.text + '<b>'

    def end_bold(self):
        self.text = self.text + '</b>'

    def start_superscript(self):
        fsize = self.my_para.get_font().get_size()
        self.text = self.text + '<font size=%d><super>' % (fsize-2)

    def end_superscript(self):
        self.text = self.text + '</super></font>'

    def start_table(self,name,style_name):
        self.in_table = 1
        self.cur_table = self.table_styles[style_name]
        self.row = -1
        self.col = 0
        self.cur_row = []
        self.table_data = []

	self.tblstyle = []
        self.cur_table_cols = []
        width = float(self.cur_table.get_width()/100.0) * self.get_usable_width()
	for val in range(self.cur_table.get_columns()):
            percent = float(self.cur_table.get_column_width(val))/100.0
            self.cur_table_cols.append(int(width * percent * cm))

    def end_table(self):
        ts = reportlab.platypus.tables.TableStyle(self.tblstyle)
	tbl = reportlab.platypus.tables.Table(data=self.table_data,
                                              colWidths=self.cur_table_cols,
                                              style=ts)
	self.story.append(tbl)
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
        if self.span == 1:
            self.cur_row.append(Paragraph(self.text,self.current_para))
        else:
            self.cur_row.append(self.text)
        for val in range(1,self.span):
            self.cur_row.append("")

	p = self.my_para
        f = p.get_font()
        if f.get_type_face() == BaseDoc.FONT_SANS_SERIF:
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
                    self.tblstyle.append(('LINEAFTER', loc, loc, 1, black))
            if self.span == 1 or inc == self.col:
                if self.my_table_style.get_left_border():
                    self.tblstyle.append(('LINEBEFORE', loc, loc, 1, black))
            if self.my_table_style.get_top_border():
                self.tblstyle.append(('LINEABOVE', loc, loc, 1, black))
            if self.my_table_style.get_bottom_border():
                self.tblstyle.append(('LINEBELOW', loc, loc, 1, black))
            if p.get_alignment() == BaseDoc.PARA_ALIGN_LEFT:
                self.tblstyle.append(('ALIGN', loc, loc, 'LEFT'))
            elif p.get_alignment() == BaseDoc.PARA_ALIGN_RIGHT:
                self.tblstyle.append(('ALIGN', loc, loc, 'RIGHT'))
            else:
                self.tblstyle.append(('ALIGN', loc, loc, 'CENTER'))
            self.tblstyle.append(('VALIGN', loc, loc, 'TOP'))

        self.col = self.col + self.span

    def add_photo(self,name,pos,x_cm,y_cm):
        img = ImgManip.ImgManip(name)
        x,y = img.size()

        ratio = float(x_cm)*float(y)/(float(y_cm)*float(x))

        if ratio < 1:
            act_width = x_cm
            act_height = y_cm*ratio
        else:
            act_height = y_cm
            act_width = x_cm/ratio

        self.story.append(Spacer(1,0.5*cm))
        self.story.append(Image(name,act_width*cm,act_height*cm))
        self.story.append(Spacer(1,0.5*cm))
        self.image = 1

    def write_text(self,text):
        text = text.replace('&','&amp;')       # Must be first
        text = text.replace('<','&lt;')
        text = text.replace('>','&gt;')
        text = text.replace('&lt;super&gt;',self.super)
        text = text.replace('&lt;/super&gt;','</super></font>')
        self.text =  self.text + text.replace('\n','<br>')

    def print_report(self):
        return run_print_dialog (self.filename)

    def start_page(self,orientation=None):
        self.drawing = Drawing(self.get_usable_width()*cm, self.get_usable_height()*cm)

    def end_page(self):
       self.story.append(self.drawing)

    def draw_line(self,style,x1,y1,x2,y2):
        y1 = self.get_usable_height() - y1
        y2 = self.get_usable_height() - y2

        stype = self.draw_styles[style]
        if stype.get_line_style() == BaseDoc.SOLID:
            line_array = None
        else:
            line_array = [2,4]
            
        self.drawing.add(Line(x1*cm,y1*cm,x2*cm,y2*cm,
                              strokeWidth=stype.get_line_width(),
                              strokeDashArray=line_array))

    def draw_bar(self,style,x1,y1,x2,y2):
        pass

    def draw_path(self,style,path):
        stype = self.draw_styles[style]
        color = make_color(stype.get_fill_color())
        y = self.get_usable_height()*cm
        
        if stype.get_line_style() == BaseDoc.SOLID:
            line_array = None
        else:
            line_array = [2,4]

        p = Path(strokeWidth=stype.get_line_width(),
                 strokeDashArray=line_array,
                 fillColor=color,
                 strokeColor=make_color(stype.get_color()))
         
        point = path[0]
        p.moveTo(point[0]*cm,y-point[1]*cm)
        for point in path[1:]:
            p.lineTo(point[0]*cm,y-point[1]*cm)
        p.closePath()
        self.drawing.add(p)

    def draw_box(self,style,text,x,y):
        y = self.get_usable_height() - y

	box_style = self.draw_styles[style]
	para_name = box_style.get_paragraph_style()
	p = self.style_list[para_name]

	w = box_style.get_width()*cm
        h = box_style.get_height()*cm

 	if box_style.get_shadow():
            col = make_color((0xc0,0xc0,0xc0))
            r = Rect((x+0.2)*cm,(y-0.2)*cm-h,w,h,
                     fillColor=col,
                     strokeColor=col)
            self.drawing.add(r)
            
        self.drawing.add(Rect((x)*cm,(y*cm)-h,w,h,
                              strokeWidth=box_style.get_line_width(),
                              fillColor=box_style.get_fill_color(),
                              strokeColor=box_style.get_color()))

        size = p.get_font().get_size()

        x = x + 0.2
	if text != "":
            lines = text.split('\n')
            self.left_print(lines,p.get_font(),x*cm,y*cm - size)
            
    def draw_text(self,style,text,x,y):
        stype = self.draw_styles[style]
        pname = stype.get_paragraph_style()
        p = self.style_list[pname]
 	font = p.get_font()
        size = font.get_size()
        s = String(x*cm,
                   (self.get_usable_height()*cm)-(y*cm),
                   str(text),
                   strokeColor=make_color(font.get_color()),
                   fillColor=make_color(font.get_color()),
                   fontName=self.pdf_set_font(font),
                   fontSize=size)
        self.drawing.add(s)

    def pdf_set_font(self,font):
        if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
            if font.get_bold():
                return _HB
            else:
                return _H
        else:
            if font.get_bold():
                return _TB
            else:
                return _T

    def rotate_text(self,style,text,x,y,angle):
        stype = self.draw_styles[style]
        pname = stype.get_paragraph_style()
        p = self.style_list[pname]
 	font = p.get_font()
        size = font.get_size()
        yt = (self.get_usable_height()*cm) - (y*cm) 

        yval = 0
        g = Group()
        for line in text:
            s = String(0,yval,str(line),
                       fontName=self.pdf_set_font(font),
                       fontSize=size,
                       strokeColor=make_color(font.get_color()),
                       fillColor=make_color(font.get_color()),
                       textAnchor='middle')
            yval -= size
            g.add(s)
            
        g.translate(x*cm,yt)
        g.rotate(-angle)
        self.drawing.add(g)

    def center_text(self,style,text,x,y):
        stype = self.draw_styles[style]
        pname = stype.get_paragraph_style()
        p = self.style_list[pname]
 	font = p.get_font()
        yt = (self.get_usable_height()*cm) - (y*cm) 

        s = String(x*cm,
                   yt,
                   str(text),
                   fontName=self.pdf_set_font(font),
                   fontSize=font.get_size(),
                   strokeColor=make_color(font.get_color()),
                   fillColor=make_color(font.get_color()),
                   textAnchor='middle')
        self.drawing.add(s)

    def center_print(self,lines,font,x,y,w,h):

        l = len(lines)
        size = font.get_size()
        start_y = (y + h/2.0 + l/2.0 + l) - ((l*size) + ((l-1)*0.2))/2.0
        start_x = (x + w/2.0)

        for text in lines:
            s = String(startx, start_y,
                       str(line),
                       fontName=self.pdf_set_font(font),
                       fontSize=font.get_size(),
                       strokeColor=make_color(font.get_color()),
                       fillColor=make_color(font.get_color()),
                       )
            self.drawing.add(String(start_x,start_y,str(text)))
            start_y = start_y - size*1.2

    def left_print(self,lines,font,x,y):
        l = len(lines)
        size = font.get_size()
        start_y = self.get_usable_height() - (y*cm)
        start_x = x * cm

        for text in lines:
            s = String(start_x,
                       start_y,
                       str(text),
                       fontSize=size,
                       strokeColor=make_color(font.get_color()),
                       fillColor=make_color(font.get_color()),
                       fontName=self.pdf_set_font(font))
            self.drawing.add(s)
            start_y = start_y - size*1.2

def make_color(c):
    return Color(float(c[0])/255.0, float(c[1])/255.0, float(c[2])/255.0)

#------------------------------------------------------------------------
#
# Convert an RGB color tulple to a Color instance
#
#------------------------------------------------------------------------
def make_color(c):
    return Color(float(c[0])/255.0, float(c[1])/255.0, float(c[2])/255.0)

#------------------------------------------------------------------------
#
# Register the document generator with the GRAMPS plugin system
#
#------------------------------------------------------------------------

Plugins.register_draw_doc(
    _("PDF"),
    PdfDoc,
    1,
    1,
    ".pdf"
    )

Plugins.register_text_doc(
    name=_("PDF"),
    classref=PdfDoc,
    table=1,
    paper=1,
    style=1,
    ext=".pdf"
    )

Plugins.register_book_doc(
    name=_("PDF"),
    classref=PdfDoc,
    table=1,
    paper=1,
    style=1,
    ext=".pdf"
    )
