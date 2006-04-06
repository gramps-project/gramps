#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# $Id$

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import BaseDoc
from PluginUtils import register_text_doc, register_draw_doc, register_book_doc
import Errors
import ImgManip
import Mime

_H   = 'Helvetica'
_HB  = 'Helvetica-Bold'
_HO  = 'Helvetica-Oblique'
_HBO = 'Helvetica-BoldOblique'
_T   = 'Times-Roman'
_TB  = 'Times-Bold'
_TI  = 'Times-Italic'
_TBI = 'Times-BoldItalic'

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".PdfDoc")

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
    import reportlab.graphics.shapes
    import reportlab.lib.styles
    from reportlab.pdfbase.pdfmetrics import *

    for faceName in reportlab.pdfbase.pdfmetrics.standardFonts:
        reportlab.pdfbase.pdfmetrics.registerTypeFace(
            reportlab.pdfbase.pdfmetrics.TypeFace(faceName))
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

def enc(s):
    try:
        new_s = s
        return new_s.encode('iso-8859-1')
    except:
        return str(s)
    
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
            pdf_style.leading = font.get_size()*1.2
            
            if font.get_type_face() == BaseDoc.FONT_SERIF:
                if font.get_bold():
                    if font.get_italic():
                        pdf_style.fontName = _TBI
                    else:
                        pdf_style.fontName = _TB
                else:
                    if font.get_italic():
                        pdf_style.fontName = _TI
                    else:
                        pdf_style.fontName = _T
            else:
                if font.get_bold():
                    if font.get_italic():
                        pdf_style.fontName = _HBO
                    else:
                        pdf_style.fontName = _HB
                else:
                    if font.get_italic():
                        pdf_style.fontName = _HO
                    else:
                        pdf_style.fontName = _H
            pdf_style.bulletFontName = pdf_style.fontName

            pdf_style.rightIndent = style.get_right_margin()*cm
            pdf_style.leftIndent = style.get_left_margin()*cm
            pdf_style.firstLineIndent = style.get_first_indent()*cm
            pdf_style.bulletIndent = pdf_style.firstLineIndent + \
                                     pdf_style.leftIndent
            
            align = style.get_alignment()
            if align == BaseDoc.PARA_ALIGN_RIGHT:
                pdf_style.alignment = TA_RIGHT
            elif align == BaseDoc.PARA_ALIGN_LEFT:
                pdf_style.alignment = TA_LEFT
            elif align == BaseDoc.PARA_ALIGN_CENTER:
                pdf_style.alignment = TA_CENTER
            else:
                pdf_style.alignment = TA_JUSTIFY
            pdf_style.spaceBefore = style.get_top_margin()*cm
            pdf_style.spaceAfter = style.get_bottom_margin()*cm
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

        if self.print_req:
            apptype = 'application/pdf'
            app = Mime.get_application(apptype)
            os.environ["FILE"] = self.filename
            os.system ('%s "$FILE" &' % app[0])

    def page_break(self):
        self.story.append(PageBreak())

    def start_paragraph(self,style_name,leader=None):
        self.current_para = self.pdfstyles[style_name]
        self.my_para = self.style_list[style_name]
        self.super = "<font size=%d><super>" \
                     % (self.my_para.get_font().get_size()-2)
        if leader==None:
            self.text = ''
        else:
            self.current_para.firstLineIndent = 0
            self.text = '<bullet>%s</bullet>' % leader

    def end_paragraph(self):
        if self.in_table:
            self.cur_cell.append(Paragraph(enc(self.text),self.current_para))
        else:
            self.story.append(Paragraph(enc(self.text),self.current_para))

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
        self.text = ""

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
        self.cur_table_cols = []
        width = float(self.cur_table.get_width()/100.0) * self.get_usable_width()
        for val in range(self.cur_table.get_columns()):
            percent = float(self.cur_table.get_column_width(val))/100.0
            self.cur_table_cols.append(int(width * percent * cm))

    def end_row(self):
        self.table_data.append(self.cur_row)

    def start_cell(self,style_name,span=1):
        self.span = span
        self.my_table_style = self.cell_styles[style_name]
        self.cur_cell = []

    def end_cell(self):
        if self.cur_cell:
            self.cur_row.append(self.cur_cell)
        else:
            self.cur_row.append("")
        
        the_width = self.cur_table_cols[self.col]
        for val in range(1,self.span):
            self.cur_row.append("")
            the_width += self.cur_table_cols[self.col+val]
            self.cur_table_cols[self.col+val] = 0
        self.cur_table_cols[self.col] = the_width

        p = self.my_para
        f = p.get_font()
        if f.get_type_face() == BaseDoc.FONT_SANS_SERIF:
            if f.get_bold():
                fn = _HB
            else:
                fn = _H
        else:
            if f.get_bold():
                fn = _TB
            else:
                fn = _T

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
        self.text = ""

    def add_media_object(self,name,pos,x_cm,y_cm):
        try:
            img = ImgManip.ImgManip(name)
        except:
            return
        
        x,y = img.size()

        ratio = float(x_cm)*float(y)/(float(y_cm)*float(x))

        if ratio < 1:
            act_width = x_cm
            act_height = y_cm*ratio
        else:
            act_height = y_cm
            act_width = x_cm/ratio

        im = Image(enc(name),act_width*cm,act_height*cm)
        if pos in ['left','right','center']:
            im.hAlign = pos.upper()
        else:
            im.hAlign = 'LEFT'

        if self.in_table:
            self.cur_cell.append(Spacer(1,0.5*cm))
            self.cur_cell.append(im)
            self.cur_cell.append(Spacer(1,0.5*cm))
        else:
            self.story.append(Spacer(1,0.5*cm))
            self.story.append(im)
            self.story.append(Spacer(1,0.5*cm))

    def write_note(self,text,format,style_name):
        text = enc(text)
        current_para = self.pdfstyles[style_name]
        self.my_para = self.style_list[style_name]
        self.super = "<font size=%d><super>" \
                     % (self.my_para.get_font().get_size()-2)

        text = text.replace('&','&amp;')       # Must be first
        text = text.replace('<','&lt;')
        text = text.replace('>','&gt;')
        text = text.replace('&lt;super&gt;',self.super)
        text = text.replace('&lt;/super&gt;','</super></font>')

        if format == 1:
            text = '<para firstLineIndent="0" fontname="Courier">%s</para>' \
                   % text.replace('\t',' '*8)
            if self.in_table:
                self.cur_cell.append(XPreformatted(text,current_para))
            else:
                self.story.append(XPreformatted(text,current_para))
        elif format == 0:
            for line in text.split('\n\n'):
                if self.in_table:
                    self.cur_cell.append(Paragraph(line,current_para))
                else:
                    self.story.append(Paragraph(line,current_para))

    def write_text(self,text):
        text = text.replace('&','&amp;')       # Must be first
        text = text.replace('<','&lt;')
        text = text.replace('>','&gt;')
        text = text.replace('&lt;super&gt;',self.super)
        text = text.replace('&lt;/super&gt;','</super></font>')
        self.text =  self.text + text.replace('\n','<br>')

    def start_page(self):
        x = self.get_usable_width()*cm
        y = self.get_usable_height()*cm
        self.drawing = reportlab.graphics.shapes.Drawing(x,y)

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
            
        l = reportlab.graphics.shapes.Line(x1*cm,y1*cm,
                                           x2*cm,y2*cm,
                                           strokeWidth=stype.get_line_width(),
                                           strokeDashArray=line_array)
        self.drawing.add(l)

    def write_at(self, style, text, x, y):
        para_style = self.style_list[style]
        font_style = para_style.get_font()
        size = font_style.get_size()
        y = self.get_usable_height() - y

        if text != "":
            lines = text.split('\n')
            self.left_print(lines,font_style,x*cm,y*cm - size)

    def draw_bar(self, style, x1, y1, x2, y2):
        style = self.draw_styles[style]
        fill_color = make_color(style.get_fill_color())
        color = make_color(style.get_color())
        line_width = style.get_line_width()
        w = (x2-x1)*cm
        h = (y2-y1)*cm

        y1 = self.get_usable_height() - y1

        r = reportlab.graphics.shapes.Rect((x1)*cm,(y1*cm)-h,w,h,
                                           strokeWidth=line_width,
                                           fillColor=fill_color,
                                           strokeColor=color)
        self.drawing.add(r)

    def draw_path(self,style,path):
        stype = self.draw_styles[style]
        color = make_color(stype.get_fill_color())
        y = self.get_usable_height()*cm
        
        if stype.get_line_style() == BaseDoc.SOLID:
            line_array = None
        else:
            line_array = [2,4]

        scol = make_color(stype.get_color())
        p = reportlab.graphics.shapes.Path(strokeWidth=stype.get_line_width(),
                                           strokeDashArray=line_array,
                                           fillColor=color,
                                           strokeColor=scol)
         
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

        sspace = box_style.get_shadow_space()
        if box_style.get_shadow():
            col = make_color((0xc0,0xc0,0xc0))
            r = reportlab.graphics.shapes.Rect((x+sspace)*cm,
                                               (y-sspace)*cm-h,
                                               w,h,
                                               fillColor=col,
                                               strokeColor=col)
            self.drawing.add(r)

        sw = box_style.get_line_width()
        fc = box_style.get_fill_color()
        sc = box_style.get_color()
        r = reportlab.graphics.shapes.Rect((x)*cm,(y*cm)-h,w,h,
                                           strokeWidth=sw,
                                           fillColor=fc,
                                           strokeColor=sc)
        self.drawing.add(r)

        size = p.get_font().get_size()

        x = x + sspace
        if text != "":
            lines = text.split('\n')
            self.left_print(lines,p.get_font(),x*cm,y*cm - size)
            
    def draw_text(self,style,text,x,y):
        stype = self.draw_styles[style]
        pname = stype.get_paragraph_style()
        p = self.style_list[pname]
        font = p.get_font()
        size = font.get_size()
        y = (self.get_usable_height()*cm)-(y*cm)
        sc = make_color(font.get_color())
        fc = make_color(font.get_color())
        fnt = self.pdf_set_font(font)
        if p.get_alignment() == BaseDoc.PARA_ALIGN_CENTER:
            twidth = ((self.string_width(font,enc(text)))/2.0)*cm
            xcm = (stype.get_width() - x) - twidth
        else:
            xcm = x * cm
        s = reportlab.graphics.shapes.String(xcm,
                                             y-size,
                                             enc(text),
                                             strokeColor=sc,
                                             fillColor=fc,
                                             fontName=fnt,
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
        g = reportlab.graphics.shapes.Group()
        fnt = self.pdf_set_font(font)
        sc = make_color(font.get_color())
        fc = make_color(font.get_color())
        for line in text:
            s = reportlab.graphics.shapes.String(0,yval,enc(line),
                                                 fontName=fnt,
                                                 fontSize=size,
                                                 strokeColor=sc,
                                                 fillColor=fc,
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

        fnt = self.pdf_set_font(font)
        sc = make_color(font.get_color())
        fc = make_color(font.get_color())
        s = reportlab.graphics.shapes.String(x*cm,
                                             yt,
                                             enc(text),
                                             fontName=fnt,
                                             fontSize=font.get_size(),
                                             strokeColor=sc,
                                             fillColor=fc,
                                             textAnchor='middle')
        self.drawing.add(s)

    def center_print(self,lines,font,x,y,w,h):
        l = len(lines)
        size = font.get_size()
        start_y = (y + h/2.0 + l/2.0 + l) - ((l*size) + ((l-1)*0.2))/2.0
        start_x = (x + w/2.0)

        fnt = self.pdf_set_font(font)
        size = font.get_size()
        sc = make_color(font.get_color())
        fc = make_color(font.get_color())
        for text in lines:
            s = reportlab.graphics.shapes.String(start_x*cm,
                                                 start_y*cm,
                                                 enc(text),
                                                 fontName=fnt,
                                                 fontSize=size,
                                                 strokeColor=sc,
                                                 fillColor=fc)
            self.drawing.add(s)
            start_y = start_y - size*1.2

    def left_print(self,lines,font,x,y):
        size = font.get_size()
        start_y = y
        start_x = x 

        fnt = self.pdf_set_font(font)
        sc = make_color(font.get_color())
        fc = make_color(font.get_color())
        for text in lines:
            s = reportlab.graphics.shapes.String(start_x,
                                                 start_y,
                                                 enc(text),
                                                 fontSize=size,
                                                 strokeColor=sc,
                                                 fillColor=fc,
                                                 fontName=fnt)
            self.drawing.add(s)
            start_y = start_y - size*1.2

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
print_label = None
try:
    import Utils

    mprog = Mime.get_application("application/pdf")
    mtype = Mime.get_description("application/pdf")
    
    if Utils.search_for(mprog[0]):
        print_label=_("Open in %s") % mprog[1]
    else:
        print_label=None
    register_text_doc(mtype, PdfDoc, 1, 1, 1, ".pdf", print_label)
    register_draw_doc(mtype, PdfDoc, 1, 1,    ".pdf", print_label)
    register_book_doc(mtype,classref=PdfDoc,
                      table=1,paper=1,style=1,ext=".pdf")
except:
    register_text_doc(_('PDF document'), PdfDoc,1, 1, 1,".pdf", None)
    register_draw_doc(_('PDF document'), PdfDoc,1, 1,   ".pdf", None)
    register_book_doc(name=_("PDF document"),classref=PdfDoc,
                      table=1,paper=1,style=1,ext=".pdf")
