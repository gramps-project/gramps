#
# Copyright (C) 2002  Gary Shao
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

"""nroff/groff document generator"""

#------------------------------------------------------------------------
#
# gramps modules 
#
#------------------------------------------------------------------------
from TextDoc import *
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
# Paragraph Handling
#
#------------------------------------------------------------------------
class RoffParastyle:
    def __init__(self, style=None):
	if style:
	    self.fontSize = style.fontSize
	    self.fontFamily = style.fontFamily
	    self.leftIndent = style.left_indent
	    self.rightIndent = style.right_indent
	    self.firstLineIndent = style.firstLineIndent
	    self.topBorder = style.topBorder
	    self.bottomBorder = style.bottomBorder
	    self.leftBorder = style.leftBorder
	    self.rightBorder = style.rightBorder
	    self.align = style.align
	else:
	    self.fontSize = 12
	    self.fontFamily = "R"
	    self.leftIndent = 0.0
	    self.rightIndent = 0.0
	    self.firstLineIndent = 0.0
	    self.topBorder = 0
	    self.bottomBorder = 0
	    self.leftBorder = 0
	    self.rightBorder = 0
	    self.align = "left"
    
# Standard paper sizes, width x height (cm)
PaperSizes = {"Letter" : (21.6,27.9),
              "Legal" : (21.6,35.6),
              "Executive" : (19.0,25.4),
              "Ledger" : (27.9,43.2),
              "A" : (21.6,27.9),
              "B" : (27.9,43.2),
              "C" : (43.2,55.9),
              "D" : (55.9,86.4),
              "E" : (86.4,111.8),
	      "A1" : (59.4,84.1),
	      "A2" : (42.0,59.4),
	      "A3" : (29.7,42.0),
	      "A4" : (21.0,29.7),
	      "A5" : (14.8,21.0),
	      "A6" : (10.5,14.8),
	      "A7" : (7.4,10.5),
	      "A8" : (5.2,7.4),
	      "B4" : (25.0,35.3),
	      "B5" : (17.6,25.0),
	      "B6" : (12.5,17.6),
	     }
#------------------------------------------------------------------------
#
# NroffDoc
#
#------------------------------------------------------------------------
class NroffDoc(TextDoc):
    """Nroff document interface class. Derived from TextDoc"""
    
    def open(self,filename):
        """Opens the specified file, making sure that it has the
        extension of .rof"""
        if type(filename) == type(""):
            if filename[-4:] != ".rof":
                self.filename = filename + ".rof"
            else:
                self.filename = filename
            self.f = open(self.filename,"w")
	    self.alreadyOpen = 0
	elif hasattr(filename, "write"):
	    self.f = filename
	    self.alreadyOpen = 1

        if self.orientation == PAPER_LANDSCAPE:
            options = options + ",landscape"

        # If the user picks something not listed above, we'll just accept
        # the default of American letter size.
	if self.paper.name == "Terminal":
	    self.paperWidth = 80
	    self.paperHeight = 24
	elif self.paper.name == "Text":
	    self.paperWidth, self.paperHeight = PaperSizes["Letter"]
	elif self.paper.name in PaperSizes.keys():
	    self.paperWidth, self.paperHeight = PaperSizes[self.paper.name]
	else:
	    self.paperWidth, self.paperHeight = PaperSizes["Letter"]

        # Write any generator-supplied macros
	#   Macros and traps to set 1in. top and bottom page margins
	self.f.write('.de hd\n')
	self.f.write('\'sp 0.5i\n')
	self.f.write('..\n')
	self.f.write('\'bp\n')
	self.f.write('..\n')
	self.f.write('.wh 0 hd\n')
	self.f.write('.wh -1i fo\n')
	#   Macros for drawing parts of paragraph border
        #     Top side
	self.f.write('.de tb\n')
	self.f.write('.nr b \\\\n(.lu-\\\\n(.iu\n')
	self.f.write('.sp -1\n')
	self.f.write('.nf\n')
	self.f.write('\\h\'-.5n\'\\v\'|\\\\nau-1\'\\l\'\\\\nbu+1n\\(em\'\\v\'-|\\\\nau+1\'\\h\'|0u-.5n\'\n')
	self.f.write('.fi\n')
	self.f.write('..\n')
        #     Bottom side
	self.f.write('.de bb\n')
	self.f.write('.nr b \\\\n(.lu-\\\\n(.iu\n')
	self.f.write('.nf\n')
	self.f.write('\\h\'-.5n\'\\l\'\\\\nbu+1n\\(em\'\\h\'|0u-.5n\'\n')
	self.f.write('.fi\n')
	self.f.write('..\n')
	#   Macro for beginning a new paragraph
	self.f.write('.de pg\n')
	self.f.write('.br\n')
	self.f.write('.ft \\\\$1\n')
	self.f.write('.ps \\\\$2\n')
	self.f.write('.vs \\\\$3\n')
	self.f.write('.in \\\\$4\n')
	self.f.write('.ti \\\\$5\n')
	self.f.write('.ll \\\\$6\n')
	self.f.write('.sp 0.9\n')
	self.f.write('.ne 1+\\n(.Vu\n')
	self.f.write('.ad \\\\$7\n')
	self.f.write('..\n')

        # Set up an initial choice of font
        self.f.write('.ft R\n')
        self.f.write('.ps 12\n')

	# Set the page parameters
	#   Page length
	if self.paper.name == "Terminal":
	    self.f.write('.pl %dv\n' % self.paperHeight)
	else:
	    self.f.write('.pl %.2fc\n' % self.paperHeight)
	#   Start with a 1in. left and right margin unless targeting a terminal
	self.origLineLength = self.paperWidth - 5.08
	if self.paper.name == "Terminal":
	    self.origLineLength = self.paperWidth
	    self.f.write('.po 0\n')
	    self.f.write('.ll %dm\n' % self.origLineLength)
	else:
	    self.page_offset = 2.54
	    self.right_offset = 2.54
	    self.origLineLength = self.paperWidth - self.page_offset - self.right_offset 
	    self.f.write('.po %.2fc\n' % self.page_offset)
	    self.f.write('.ll %.2fc\n' % (self.origLineLength))
	
        self.in_list = 0
	self.in_paragraph = 0
	self.in_table = 0
	self.in_cell = 0
	self.cell_header_written = 0
	self.last_indent = 0
	self.fix_first = 0
	self.tabchar = '~'  # separator for table cell data
	
	#Establish some local styles for the report
	self.roffstyle = {}
	
        for style_name in self.style_list.keys():
            style = self.style_list[style_name]
            font = style.get_font()
	    size = font.get_size()
	    
	    thisstyle = RoffParastyle()
	    
	    # Is there special alignment?  (default is left)
	    align = style.get_alignment_text()
	    if  align == "center":
	        thisstyle.align = "center"
	    elif align == "right":
	        thisstyle.align = "right"
	    else:
	        thisstyle.align = "left"

	    # Establish font face and shape
	    if self.paper.name == "Terminal" or self.paper.name == "Text":
	        if font.get_bold():
		    if font.get_italic():
		        thisstyle.fontFamily = 'BI'
		    else:
		        thisstyle.fontFamily = 'B'
		else:
		    if font.get_italic():
		        thisstyle.fontFamily = 'I'
	            else:
		        thisstyle.fontFamily = 'R'
	    elif font.get_type_face() == FONT_MONOSPACE:
	        if font.get_bold():
		    if font.get_italic():
		        thisstyle.fontFamily = 'CBI'
		    else:
		        thisstyle.fontFamily = 'CB'
		else:
		    if font.get_italic():
		        thisstyle.fontFamily = 'CI'
	            else:
		        thisstyle.fontFamily = 'CR'
	    elif font.get_type_face() == FONT_SANS_SERIF:
	        if font.get_bold():
		    if font.get_italic():
		        thisstyle.fontFamily = 'HBI'
		    else:
		        thisstyle.fontFamily = 'HB'
		else:
		    if font.get_italic():
		        thisstyle.fontFamily = 'HI'
	            else:
		        thisstyle.fontFamily = 'HR'
	    else:
	        if font.get_bold():
		    if font.get_italic():
		        thisstyle.fontFamily = 'TBI'
		    else:
		        thisstyle.fontFamily = 'TB'
		else:
		    if font.get_italic():
		        thisstyle.fontFamily = 'TI'
	            else:
		        thisstyle.fontFamily = 'TR'

	    # Now determine font size 
	    thisstyle.fontSize = size

            # And add the other paragraph attributes
	    thisstyle.leftIndent = style.get_left_margin()
	    thisstyle.rightIndent = style.get_right_margin()
	    thisstyle.firstLineIndent = style.get_first_indent()
	    thisstyle.topBorder = style.get_top_border()
	    thisstyle.bottomBorder = style.get_bottom_border()
	    thisstyle.leftBorder = style.get_left_border()
	    thisstyle.rightBorder = style.get_right_border()
	    
	    self.roffstyle[style_name] = thisstyle

    def close(self):
        """Close the document if needed"""
	if not self.alreadyOpen:
            self.f.close()

    def start_page(self,orientation=None):
        """Nothing needs to be done to start a page"""
        pass

    def end_page(self):
        """Issue a new page command"""
        self.f.write('.bp\n')

    def start_listing(self,style_name):
        """Listing handling"""

        alignment = 'l'
        self.current_style = style_name
        style = self.roffstyle[style_name]
	linelength = self.paperWidth - self.page_offset - self.right_offset
	linelength = linelength - style.rightIndent
	self.lineLength = linelength
	self.f.write('.pg %s %d %d %.2fc %.2fc %.2fc %s\n' % \
	            (style.fontFamily, style.fontSize, style.fontSize+2,
		     style.leftIndent, style.leftIndent,
		     linelength, alignment))
	if style.topBorder:
	    self.f.write('.sp 1\n')
	self.f.write('.nf\n')
	self.f.write('.na\n')
	self.f.write('.mk a\n')
	self.last_char_written = '\n'

    def end_listing(self):
        if self.last_char_written != '\n':
	    self.f.write('\n')
        style = self.roffstyle[self.current_style]
	if style.topBorder:
	    self.f.write('.tb\n')
	if style.bottomBorder:
	    self.f.write('.bb\n')

    def start_paragraph(self,style_name,leader=None):
        """Paragraph handling - A Gramps paragraph is any 
	single body of text, from a single word, to several sentences."""

        self.current_style = style_name
        style = self.roffstyle[style_name]
	# Calculate table cell alignment and spacing
	if style.align == "right":
	    alignment = 'r'
	elif style.align == "center":
	    alignment = 'c'
	else:
	    alignment = 'l'
	self.cell_para_align = alignment
	if self.in_cell and not self.cell_header_written:
	    if self.tablewidth:
		width = self.colwidths[self.cell_cnt]
		cellfmt = "%sw(%.2fc-1.5m)" % (self.cell_para_align, width)
	    else:
	        cellfmt = self.cell_para_align
	    cellfmt = cellfmt + "p%d" % style.fontSize
	    cellfmt = cellfmt + "f%s " % style.fontFamily
            if self.cell_span > 1:
	        for i in range(1, self.cell_span):
		    cellfmt = cellfmt + " s"
	    # Account for vertical rules
	    rowformat = self.row_formatstr
	    end = len(rowformat) - 1
	    if end > -1:
	        lastformatchar = rowformat[end]
	    else:
	        lastformatchar = ""
	    if self.lborder == 1 and lastformatchar != '|':
	        cellfmt = '| ' + cellfmt
	    if self.rborder == 1:
	        cellfmt = cellfmt + ' |'
	    self.row_formatstr = self.row_formatstr + ' ' + cellfmt
	    self.cell_header_written = 1
	
	if not self.in_cell:
	    linelength = self.paperWidth - self.page_offset - self.right_offset
	    linelength = linelength - style.rightIndent
	    self.lineLength = linelength
	    self.f.write('.pg %s %d %d %.2fc %.2fc %.2fc %s\n' % \
	                (style.fontFamily, style.fontSize, style.fontSize+2,
			 style.leftIndent, style.leftIndent+style.firstLineIndent,
			 linelength, alignment))
	    if style.topBorder:
	        self.f.write('.sp 1\n')
	    self.f.write('.fi\n')
	    self.f.write('.mk a\n')
	    self.last_char_written = '\n'

        self.current_fontfamily = style.fontFamily
	self.in_paragraph = 1
    
    def end_paragraph(self):
        if not self.in_cell and self.last_char_written != '\n':
	    self.f.write('\n')
	if not self.in_cell:
            style = self.roffstyle[self.current_style]
	    if style.topBorder:
	        self.f.write('.tb\n')
	    if style.bottomBorder:
	        self.f.write('.bb\n')
	self.in_paragraph = 0

    def start_italic(self):
        """Italic face inside a paragraph"""
	if self.in_paragraph:
	    font = self.current_fontfamily
	    if 'I' not in font:
	        if font=='R':
		    newfont = 'I'
		elif font =='B':
		    newfont = 'BI'
		elif font[1]=='R':
		    newfont = font[0] + 'I'
		else:
		    newfont = font[0] + 'BI'
		if self.last_char_written != '\n':
	            self.f.write('\n.ft %s\n' % newfont)
		else:
	            self.f.write('.ft %s\n' % newfont)
		self.current_fontfamily = newfont

    def end_italic(self):
        """End italic face inside a paragraph"""
	if self.in_paragraph:
	    font = self.current_fontfamily
	    if 'I' in font:
	        if font=='I':
		    newfont = 'R'
		elif font=='BI':
		    newfont = 'B'
		elif len(font)==2 and font[1]=='I':
		    newfont = font[0] + 'R'
		else:
		    newfont = font[0] + 'B'
	        if self.last_char_written != '\n':
	            self.f.write('\n.ft %s\n' % newfont)
	        else:
	            self.f.write('.ft %s\n' % newfont)
		self.current_fontfamily = newfont

    def start_bold(self):
        """Bold face inside a paragraph"""
	if self.in_paragraph:
	    font = self.current_fontfamily
	    if 'B' not in font:
	        if font=='R':
		    newfont = 'B'
		elif font =='I':
		    newfont = 'BI'
		elif font[1]=='R':
		    newfont = font[0] + 'B'
		else:
		    newfont = font[0] + 'BI'
		if self.last_char_written != '\n':
	            self.f.write('\n.ft %s\n' % newfont)
		else:
	            self.f.write('.ft %s\n' % newfont)
		self.current_fontfamily = newfont

    def end_bold(self):
        """End bold face inside a paragraph"""
	if self.in_paragraph:
	    font = self.current_fontfamily
	    if 'B' in font:
	        if font=='B':
		    newfont = 'R'
		elif font=='BI':
		    newfont = 'I'
		elif len(font)==2 and font[1]=='B':
		    newfont = font[0] + 'R'
		else:
		    newfont = font[0] + 'I'
	        if self.last_char_written != '\n':
	            self.f.write('\n.ft %s\n' % newfont)
	        else:
	            self.f.write('.ft %s\n' % newfont)
		self.current_fontfamily = newfont

    def start_table(self,name,style_name):
        """Begin new table"""
	self.in_cell = 0
	self.cell_header_written = 0
	self.in_table = 1
	self.first_row = 1
	self.last_row_had_bottomborder = 0

	# Reset the left indent and line length to original values
	self.f.write('.in 0c\n')
	self.f.write('.ll %.2fc\n' % self.origLineLength)

	# Make the column separator character be the tilde when specifying
	# data in each table cell
	optionstr = "tab(%s)" % self.tabchar

	# We need to know a priori how many columns are in this table
	self.tblstyle = self.table_styles[style_name]
	self.numcols = self.tblstyle.get_columns()
	self.tablewidth = self.tblstyle.get_width()
	if self.tablewidth:
	    self.colwidths = []
	    for i in range(self.numcols):
	        width = self.tblstyle.get_column_width(i)
	        mult = self.origLineLength * float(width * self.tablewidth) / 10000.0
	        self.colwidths.append(mult)
	    optionstr =  optionstr + ";"
	else:
	    optionstr = optionstr + ",center;"
	self.f.write('.TS\n')
	self.f.write('%s\n' % optionstr)

    def end_table(self):
        """Close the table specification"""
	self.in_table = 0
	self.f.write('.TE\n')

    def start_row(self):
        """Begin a new row"""
	self.cell_cnt = -1
	self.row_line_above = 1
	self.row_line_below = 1
	self.row_formatstr = ""
	self.row_datastrs = []
	
    def end_row(self):
        """End the row (new line)"""

        # Write out the format string for the row if it is the first row,
	# or make a continuation row specification if the format has changed
	# from the last one
	self.row_formatstr = self.row_formatstr + ".\n"
	if self.first_row:
	    self.f.write(self.row_formatstr)
	    self.last_row_formatstr = self.row_formatstr
	else:
	    if self.row_formatstr != self.last_row_formatstr:
	        self.f.write('.T&\n')
		self.f.write(self.row_formatstr)
        # Write a horizontal line if the row calls for a top border
	# and any previous row did not already print a bottom border line
	if self.row_line_above and not self.last_row_had_bottomborder:
	    self.f.write('_\n')

	# Write out the row data
        datastr = self.row_datastrs.pop(0)
	self.f.write(datastr)
	while len(self.row_datastrs) > 0:
	    self.f.write("%s%s" % (self.tabchar, self.row_datastrs.pop(0)))
	self.f.write('\n')

	# Write a horizontal line if the row calls for a bottom border
	if self.row_line_below:
	    self.f.write('_\n')
	    self.last_row_had_bottomborder = 1
	else:
	    self.last_row_had_bottomborder = 0

	if self.first_row:
	    self.first_row = 0
	    
    def start_cell(self,style_name,span=1):
        """Add an entry to the table."""

	self.cell_cnt = self.cell_cnt + 1
	self.in_cell = 1
	self.cell_span = span
	self.cell_header_written = 0
	self.cell_string = ""

	self.cstyle = self.cell_styles[style_name]
	self.lborder = self.cstyle.get_left_border()
	self.rborder = self.cstyle.get_right_border()
	self.bborder = self.cstyle.get_bottom_border()
	if not self.bborder:
	    self.row_line_below = 0
	self.tborder = self.cstyle.get_top_border()
	if not self.tborder:
	    self.row_line_above = 0
	
	# Wait until paragraph start to get paragraph attributes so
	# that we can apply them to the cell format
	
    def end_cell(self):
        """Adds the cell data string to the row data"""
	self.in_cell = 0
	self.cell_header_written = 0
	if self.tablewidth:
	    width = self.colwidths[self.cell_cnt]
	    for i in range(1, self.cell_span):
	        width = width + self.colwidths[self.cell_cnt + i]
	    if (0.254 * len(self.cell_string)) > width:
	        self.cell_string = 'T{\n' + self.cell_string + '\nT}'
        self.row_datastrs.append(self.cell_string)

    def add_photo(self,name,pos,x,y):
        pass
		
    def write_text(self,text):
        """Write the text to the file"""
	if self.in_cell:
	    self.cell_string = self.cell_string + text
	else:
            self.f.write(text)
	    if text:
	        self.last_char_written = text[-1]

    def line_break(self):
        if self.in_paragraph and self.last_char_written != '\n':
	    self.f.write('\n.br\n')
	else:
	    self.f.write('.br\n')
	self.last_char_written = '\n'

    def page_break(self):
        if self.in_paragraph and self.last_char_written != '\n':
	    self.f.write('\n.bp\n')
	else:
	    self.f.write('.bp\n')
	self.last_char_written = '\n'

    def show_link(self, text, href):
        self.write_text("%s (" % text)
	self.start_italic()
	self.write_text(href)
	self.end_italic()
	self.write_text(") ")

#------------------------------------------------------------------------
#
# Register the document generator with the system if in Gramps
#
#------------------------------------------------------------------------
if withGramps:
    Plugins.register_text_doc(
        name=_("nroff/groff"),
        classref=NroffDoc,
        table=1,
        paper=1,
        style=1
        )
