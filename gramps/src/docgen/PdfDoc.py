#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
#
# Modified August 2002 by Gary Shao
#
#   Removed Gramps dependencies.
#
#   Finagled the import name of the TableStyle class from reportlab so
#   that it doesn't conflict with TableStyle class name from TextDoc
#   module. Reportlab version is now referenced as ReportlabTableStyle.
#
#   Added two new derived classes (BoxedParagraphStyle, BoxedParagraph)
#   to replace standard reportlab classes to allow for drawing a border
#   around a Paragraph flowable.
#
#   Added new derived class SpanTable to replace standard reportlab class
#   Table. Allows for proper placement of text within a table cell which
#   spans several columns.
#
#   Modified open() and close() methods to allow the filename parameter
#   passed to open() to be either a string containing a file name, or
#   a Python file object. This allows the document generator to be more
#   easily used with its output directed to stdout, as may be called for
#   in a CGI script.
#
# Modified September 2002 by Gary Shao
#
#   Added new derived class BoxedPreformatted to replace standard
#   reportlab class Preformatted to allow for drawing a border around
#   the flowable.
#
#   Added new methods start_listing() and end_listing() for specifying
#   a block of text that should be rendered without any filling or
#   justification.
#
#   Added new methods start_italic() and end_italic() to enable
#   italicizing parts of text within a paragraph
#
#   Added method show_link() to display in text the value of a link.
#   This method really only has an active role in the HTML generator,
#   but is provided here for interface consistency.
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
from TextDoc import *
OldTableStyle = TableStyle  #Make an alias for original TableStyle
                            #because reportlab.platypus.tables also
			    #has a TableStyle class whose name will
			    #cover up the one from the TextDoc module
import ImgManip

try:
    import Plugins
    import intl
    _ = intl.gettext
except:
    withGramps = 0
else:
    withGramps = 1

#------------------------------------------------------------------------
#
# ReportLab python/PDF modules
#
#------------------------------------------------------------------------

try:
    import reportlab.platypus.tables
    from reportlab.platypus import *
    ReportlabTableStyle = reportlab.platypus.tables.TableStyle
    TableStyle = OldTableStyle  #Let TableStyle refer to the original class
    from reportlab.lib.units import cm
    from reportlab.lib.colors import Color,black,white
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
    import reportlab.lib.styles
except:
    if withGramps:
        raise Plugins.MissingLibraries, _("The ReportLab modules are not installed")
    else:
        print "The ReportLab modules are not installed"
	raise

#------------------------------------------------------------------------
#
# BoxedParagraphStyle
#
#   Class derived from ParagraphStyle which adds four attributes
#   (topBorder, bottomBorder, leftBorder, rightBorder). Allows
#   for drawing border sides around a standard paragraph when using
#   a BoxedParagraph flowable (see below).
#
#------------------------------------------------------------------------
class BoxedParagraphStyle(reportlab.lib.styles.ParagraphStyle):
    defaults = {
        'fontName':'Times-Roman',
        'fontSize':10,
        'leading':12,
        'leftIndent':0,
        'rightIndent':0,
        'firstLineIndent':0,
        'alignment':TA_LEFT,
        'spaceBefore':0,
        'spaceAfter':0,
        'bulletFontName':'Times-Roman',
        'bulletFontSize':10,
        'bulletIndent':0,
        'textColor': black,
        'backColor':None,
	'topBorder':0,
	'bottomBorder':0,
	'leftBorder':0,
	'rightBorder':0
        }

#------------------------------------------------------------------------
#
# BoxedParagraph
#
#   Class derived from Paragraph which overrides the original drawing
#   method with one which also allows for drawing the sides of a border
#   around a Paragraph flowable.
#
#------------------------------------------------------------------------
class BoxedParagraph(Paragraph):
    def draw(self):
        self.drawPara2(self.debug)

    def drawPara2(self, debug=0):
        #call the original drawing method
        self.drawPara(debug)

	#stash some key facts locally for speed
	canvas = self.canv
	style = self.style

        #if borders are called for, draw them
	extra = 0.5 * style.leading
        if style.bottomBorder:
	    canvas.line(style.leftIndent, 0.0-extra, self.width-style.rightIndent, 0.0-extra)
        if style.topBorder:
	    canvas.line(style.leftIndent, self.height, self.width-style.rightIndent, self.height)
        if style.leftBorder:
	    canvas.line(style.leftIndent, 0.0-extra, style.leftIndent, self.height)
        if style.rightBorder:
	    canvas.line(self.width-style.rightIndent, 0.0-extra, self.width-style.rightIndent, self.height)
	
#------------------------------------------------------------------------
#
# BoxedPreformatted
#
#   Class derived from Preformatted which overrides the original drawing
#   method with one which also allows for drawing the sides of a border
#   around a Preformatted flowable.
#
#------------------------------------------------------------------------
class BoxedPreformatted(Preformatted):
    def draw(self):
	cur_x = self.style.leftIndent
	cur_y = self.height - self.style.fontSize
	self.canv.addLiteral('%PreformattedPara')
	if self.style.textColor:
	    self.canv.setFillColor(self.style.textColor)
	tx = self.canv.beginText(cur_x, cur_y)
	#set up the font etc.
	tx.setFont( self.style.fontName,
	    self.style.fontSize,
	    self.style.leading)

	for text in self.lines:
	    tx.textLine(text)
	self.canv.drawText(tx)
        #if borders are called for, draw them
	style = self.style
	canvas = self.canv
	extra = 0.5 * style.leading
        if style.bottomBorder:
	    canvas.line(style.leftIndent, 0.0-extra, self.width-style.rightIndent, 0.0-extra)
        if style.topBorder:
	    canvas.line(style.leftIndent, self.height, self.width-style.rightIndent, self.height)
        if style.leftBorder:
	    canvas.line(style.leftIndent, 0.0-extra, style.leftIndent, self.height)
        if style.rightBorder:
	    canvas.line(self.width-style.rightIndent, 0.0-extra, self.width-style.rightIndent, self.height)

#------------------------------------------------------------------------
#
# SpanTable
#
#   Class derived from Table which overrides the original __init__ method
#   to allow one additional parameter (an array of integer values giving
#   the span of each cell in a table), and overrides the draw method to
#   adjust cell output when the cell spans several columns.
#
#------------------------------------------------------------------------
class SpanTable(reportlab.platypus.tables.Table):
    def __init__(self, data, spandata, colWidths=None, rowHeights=None,
                 style=None, repeatRows=0, repeatCols=0, splitByRow=1,
		 emptyTableAction=None):
        reportlab.platypus.tables.Table.__init__(self, data, colWidths,
	    rowHeights, style, repeatRows, repeatCols, splitByRow,
	    emptyTableAction)
	self.span_data = spandata

    def draw(self):
        self._curweight = self._curcolor = self._curcellstyle = None
	self._drawBkgrnd()
	self._drawLines()
	in_span = 0
	span_cnt = 0
	for row, rowstyle, rowpos, rowheight, rowspan in map(None, self._cellvalues, self._cellStyles, self._rowpositions[1:], self._rowHeights, self.span_data):
	    for cellval, cellstyle, colpos, colwidth, cellspan in map(None, row, rowstyle, self._colpositions[:-1], self._colWidths, rowspan):
	        if in_span:
		    span_cnt = span_cnt - 1
		    span_width = span_width + colwidth
		    if span_cnt:
		        continue
	            else:
		        cellval, cellstyle, colpos, rowpos, rowheight = save_data
                        self._drawCell(cellval, cellstyle, (colpos, rowpos), (span_width, rowheight))
			in_span = 0
			continue
	        if cellspan > 1:
		    in_span = 1
		    span_cnt = cellspan - 1
		    span_width = colwidth
		    save_data = (cellval, cellstyle, colpos, rowpos, rowheight)
		    continue
                self._drawCell(cellval, cellstyle, (colpos, rowpos), (colwidth, rowheight))

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
class PdfDoc(TextDoc):

    def open(self,filename):
        if type(filename) == type(""):
            if filename[-4:] != ".pdf":
                self.filename = "%s.pdf" % filename
            else:
                self.filename = filename
	elif hasattr(filename, "write"):
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

	    #pdf_style = reportlab.lib.styles.ParagraphStyle(name=style_name)
	    pdf_style = BoxedParagraphStyle(name=style_name)
            pdf_style.fontSize = font.get_size()
            pdf_style.bulletFontSize = font.get_size()
            
            if font.get_type_face() == FONT_MONOSPACE:
                if font.get_bold():
                    if font.get_italic():
                        pdf_style.fontName = "Courier-BoldOblique"
                    else:
                        pdf_style.fontName = "Courier-Bold"
                else:
                    if font.get_italic():
                        pdf_style.fontName = "Courier-Oblique"
                    else:
                        pdf_style.fontName = "Courier"
            elif font.get_type_face() == FONT_SERIF:
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
            #first = left + style.get_first_indent()*cm
            first = style.get_first_indent()*cm

	    pdf_style.topBorder = style.get_top_border()
	    pdf_style.bottomBorder = style.get_bottom_border()
	    pdf_style.leftBorder = style.get_left_border()
	    pdf_style.rightBorder = style.get_right_border()

            pdf_style.rightIndent = right
            pdf_style.leftIndent = left
            pdf_style.firstLineIndent = first
            pdf_style.bulletIndent = first

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
	self.in_listing = 0

    def close(self):
        self.doc.build(self.story)

    def end_page(self):
        self.story.append(PageBreak())

    def start_listing(self,style_name):
        self.text = ''
        self.current_para = self.pdfstyles[style_name]
	self.in_listing = 1

    def end_listing(self):
        text = self.text
        index = string.find(text, '\n')
	if index > -1:
	    if index > 0 and text[index-1] == '\r':
	        eol = '\r\n'
	    else:
	        eol = '\n'
	else:
	    eol = ''
	text = ' ' + text
	if eol:
	    text = string.replace(text,eol,eol+' ');
	self.story.append(BoxedPreformatted(text,self.current_para))
	self.story.append(Spacer(1,0.5*cm))
	self.in_listing = 0

    def start_paragraph(self,style_name,leader=None):
        self.current_para = self.pdfstyles[style_name]
        self.my_para = self.style_list[style_name]
        if leader==None:
            self.text = ''
        else:
            self.text = '<bullet>%s</bullet>' % leader
        self.image = 0

    def end_paragraph(self):
        if self.in_table == 0 and self.image == 0:
	    self.story.append(BoxedParagraph(self.text,self.current_para))
	    self.story.append(Spacer(1,0.5*cm))
        else:
            self.image = 0

    def start_bold(self):
        self.text = self.text + '<b>'

    def end_bold(self):
        self.text = self.text + '</b>'

    def start_italic(self):
        self.text = self.text + '<i>'

    def end_italic(self):
        self.text = self.text + '</i>'

    def start_table(self,name,style_name):
        self.in_table = 1
        self.cur_table = self.table_styles[style_name]
        self.row = -1
        self.col = 0
        self.cur_row = []
        self.table_data = []
	self.span_data = []

	self.tblstyle = []
        self.cur_table_cols = []
        width = float(self.cur_table.get_width()/100.0) * self.get_usable_width()
	for val in range(self.cur_table.get_columns()):
            percent = float(self.cur_table.get_column_width(val))/100.0
            self.cur_table_cols.append(int(width * percent * cm))

    def end_table(self):
        ts = ReportlabTableStyle(self.tblstyle)
	#tbl = reportlab.platypus.tables.Table(data=self.table_data,
        #                                      colWidths=self.cur_table_cols,
        #                                      style=ts)
	tbl = SpanTable(data=self.table_data, spandata=self.span_data, 
	                colWidths=self.cur_table_cols, style=ts)
	self.story.append(tbl)
	self.story.append(Spacer(1,0.5*cm))
        self.in_table = 0

    def start_row(self):
	self.row = self.row + 1
        self.col = 0
        self.cur_row = []
	self.cur_span_row = []

    def end_row(self):
        self.table_data.append(self.cur_row)
	self.span_data.append(self.cur_span_row)

    def start_cell(self,style_name,span=1):
        self.span = span
	self.cur_span_row.append(span)
        self.my_table_style = self.cell_styles[style_name]
        pass

    def end_cell(self):
        if self.span == 1:
            self.cur_row.append(Paragraph(self.text,self.current_para))
        else:
            self.cur_row.append(Paragraph(self.text,self.current_para))
            #self.cur_row.append(self.text)
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
                    self.tblstyle.append(('LINEAFTER', loc, loc, 1, black))
            if self.span == 1 or inc == self.col:
                if self.my_table_style.get_left_border():
                    self.tblstyle.append(('LINEBEFORE', loc, loc, 1, black))
            if self.my_table_style.get_top_border():
                self.tblstyle.append(('LINEABOVE', loc, loc, 1, black))
            if self.my_table_style.get_bottom_border():
                self.tblstyle.append(('LINEBELOW', loc, loc, 1, black))
            if p.get_alignment() == PARA_ALIGN_LEFT:
                self.tblstyle.append(('ALIGN', loc, loc, 'LEFT'))
            elif p.get_alignment() == PARA_ALIGN_RIGHT:
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

        self.story.append(Image(name,act_width*cm,act_height*cm))
        self.story.append(Spacer(1,0.5*cm))
        self.image = 1

    def write_text(self,text):
        if not self.in_listing:
            text = string.replace(text,'&','&amp;');       # Must be first
            text = string.replace(text,'<','&lt;');
            text = string.replace(text,'>','&gt;');
	self.text = self.text + text

    def show_link(self, text, href):
        self.write_text("%s (" % text)
	self.start_italic()
	self.write_text(href)
	self.end_italic()
	self.write_text(") ")

#------------------------------------------------------------------------
#
# Convert an RGB color tuple to a Color instance
#
#------------------------------------------------------------------------
def make_color(color):
    return Color(float(color[0])/255.0, float(color[1])/255.0,
                 float(color[2])/255.0)

#------------------------------------------------------------------------
#
# Register the document generator with the GRAMPS plugin system
#
#------------------------------------------------------------------------

if withGramps:
    Plugins.register_text_doc(
        name=_("PDF"),
        classref=PdfDoc,
        table=1,
        paper=1,
        style=1
        )
