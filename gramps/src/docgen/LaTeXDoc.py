#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
#
# Modifications and feature additions:
#               2002  Donald A. Peterson
#
# Modified August 2002 by Gary Shao
#
#   Removed Gramps dependencies
#
#   Added rightIndent, bottomBorder, and topBorder attributes to TexFont
#   class in support of allowing these properties to be expressed when
#   defining paragraphs.
#
#   Completely changed the way paragraph margins are handled. Now use
#   LaTeX \parbox command to create a paragraph region, and \hspace command
#   to position it on the page. Old method ignored the right margin,
#   and didn't seem to correctly handle left margins or first line
#   indents.
#
#   Replaced instances of \centerline command with use of \hspace*{\fill}
#   to achieve centered text. This was particularly a problem inside
#   tables, where LaTeX would occasionally reject the original output
#   constructs.
#
#   Enabled the use of underline font property.
#
#   Enable the drawing of top and bottom paragraph borders using the
#   LaTeX \rule command.
#
#   Reworked the way table declarations were written to allow table
#   width to be specified as a percentages of \textwidth and column
#   widths as percentages of table width, in the spirit of how TextDoc
#   intended. Table widths of 0 will result in tables that are sized
#   automatically by LaTeX.
#
#   Modified open() and close() methods to allow the filename parameter
#   passed to open() to be either a string containing a file name, or
#   a Python file object. This allows the document generator to be more
#   easily used with its output directed to stdout, as may be called for
#   in a CGI script.
#
# Modified August 2002 by Gary Shao
#
#   Added line_break() and page_break() methods to LaTeXDoc class.
#
#   Added two new methods (start_listing() and end_listing()) to
#   enable writing a text block with no filling or justifying
#   Implementation uses the fancyvrb package.
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

"""LaTeX document generator"""

#------------------------------------------------------------------------
#
# gramps modules 
#
#------------------------------------------------------------------------
from TextDoc import *
from re import sub
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
# Paragraph Handling
#
#------------------------------------------------------------------------
class TexFont(TextDoc):
    def __init__(self, style=None):
	if style:
	    self.font_beg = style.font_beg
	    self.font_end = style.font_end
	    self.leftIndent = style.left_indent
	    self.rightIndent = style.right_indent
	    self.firstLineIndent = style.firstLineIndent
	    self.topBorder = style.topBorder
	    self.bottomBorder = style.bottomBorder
	else:
	    self.font_beg = ""
	    self.font_end = ""
	    self.leftIndent = ""
	    self.rightIndent = ""
	    self.firstLineIndent = ""
	    self.topBorder = 0
	    self.bottomBorder = 0
    
#------------------------------------------------------------------------
#
# LaTeXDoc
#
#------------------------------------------------------------------------
class LaTeXDoc(TextDoc):
    """LaTeX document interface class. Derived from TextDoc"""
    
    def open(self,filename):
        """Opens the specified file, making sure that it has the
        extension of .tex"""
        if type(filename) == type(""):
            if filename[-4:] != ".tex":
                self.filename = filename + ".tex"
            else:
                self.filename = filename
            self.f = open(self.filename,"w")
	    self.alreadyOpen = 0
	elif hasattr(filename, "write"):
	    self.f = filename
	    self.alreadyOpen = 1

        # Font size control seems to be limited. For now, ignore
        # any style constraints, and use 12pt has the default
        
        options = "12pt"

        if self.orientation == PAPER_LANDSCAPE:
            options = options + ",landscape"

        # Paper selections are somewhat limited on a stock installation. 
        # If the user picks something not listed here, we'll just accept
        # the default of the user's LaTeX installation (usually letter).
        if self.paper.name == "A4":
            options = options + ",a4paper"
        elif self.paper.name == "A5":
            options = options + ",a5paper"
        elif self.paper.name == "B5":
            options = options + ",b4paper"
        elif self.paper.name == "Legal":
            options = options + ",legalpaper"
        elif self.paper.name == "Letter":
            options = options + ",letterpaper"

        # Use the article template, T1 font encodings, and specify
        # that we should use Latin1 character encodings.
        self.f.write('\\documentclass[%s]{article}\n' % options)
        self.f.write('\\usepackage[T1]{fontenc}\n')
        self.f.write('\\usepackage[latin1]{inputenc}\n')
	# add packages (should be standard on a default installation)
	# for finer output control.  Put comments in file for user to read
        self.f.write('\\usepackage{graphicx} % Extended graphics support\n')
        self.f.write('\\usepackage{longtable} % For multi-page tables\n')
        self.f.write('\\usepackage{calc} % For margin indents\n')
        self.f.write('\\usepackage{fancyvrb} % For listing blocks\n')
	self.f.write('%\n% Depending on your LaTeX installation, the')
	self.f.write(' margins may be too\n% narrow. ')
	self.f.write(' This can be corrected by uncommenting the following\n')
	self.f.write('% two lines and adjusting the width appropriately.')
	self.f.write(' The example\n% removes 0.5in from the left margin.')
	self.f.write(' (Adds 0.5 inch to the text)\n')
	self.f.write('\\addtolength{\\oddsidemargin}{-0.5in}\n')
	self.f.write('\\addtolength{\\textwidth}{0.5in}\n%\n')
	self.f.write('\\setlength{\\parskip}{1.3ex plus0.5ex minus0.5ex}\n')
	self.f.write('% Create a first indent-adjusting command that allows LaTeX\n')
	self.f.write('% to behave like the other gramps-supported output formats\n')
	self.f.write('\\setlength{\\parindent}{0cm}\n')
	self.f.write('\\newlength{\\newwidth}\n')
	self.f.write('\\newcommand{\\grampsfirst}[1]{%\n')
	self.f.write('   \\setlength{\\parindent}{#1}%\n')
	self.f.write('}\n\n')
        self.f.write('\\begin{document}\n\n')

        self.in_list = 0
	self.in_table = 0
	self.imagenum = 0
	self.in_cell = 0
	self.cell_header_written = 0
	self.last_indent = 0
	self.fix_first = 0
	self.in_listing = 0
	
	#Establish some local styles for the report
	self.latexstyle = {}
	self.latex_font = {}
	
        for style_name in self.style_list.keys():
            style = self.style_list[style_name]
            font = style.get_font()
	    size = font.get_size()
	    
	    self.latex_font[style_name] = TexFont()
	    thisstyle = self.latex_font[style_name]
	    
	    thisstyle.font_beg = ""
	    thisstyle.font_end = ""
	    # Is there special alignment?  (default is left)
	    align = style.get_alignment_text()
	    if  align == "center":
		thisstyle.font_beg = thisstyle.font_beg + "\\hspace*{\\fill}"
		#thisstyle.font_end = "}" + thisstyle.font_end 
		thisstyle.font_end = "\\hspace*{\\fill}" + thisstyle.font_end 
	    elif align == "right":
		thisstyle.font_beg = thisstyle.font_beg + "\\hspace*{\\fill}"

	    # Establish font face and shape
	    if font.get_type_face() == FONT_SANS_SERIF:
		thisstyle.font_beg = thisstyle.font_beg + "\\sffamily"
		thisstyle.font_end = "\\rmfamily" + thisstyle.font_end 
	    if font.get_bold():
		thisstyle.font_beg = thisstyle.font_beg + "\\bfseries"
		thisstyle.font_end = "\\mdseries" + thisstyle.font_end
	    if font.get_italic():
		thisstyle.font_beg = thisstyle.font_beg + "\\itshape"
		thisstyle.font_end = "\\upshape" + thisstyle.font_end

	    # Now determine font size 
	    sflag = 0
	    if size >= 22:
		thisstyle.font_beg = thisstyle.font_beg + "\\Huge"
		sflag = 1
	    elif size >= 20:
		thisstyle.font_beg = thisstyle.font_beg + "\\huge"
		sflag = 1
	    elif size >= 18:
		thisstyle.font_beg = thisstyle.font_beg + "\\LARGE"
		sflag = 1
	    elif size >= 16:
		thisstyle.font_beg = thisstyle.font_beg + "\\Large"
		sflag = 1
	    elif size >= 14:
		thisstyle.font_beg = thisstyle.font_beg + "\\large"
		sflag = 1
	    elif size < 8:
		thisstyle.font_beg = thisstyle.font_beg + "\\scriptsize"
		sflag = 1
	    elif size < 10:
		thisstyle.font_beg = thisstyle.font_beg + "\\footnotesize"
		sflag = 1
	    elif size < 12:
		thisstyle.font_beg = thisstyle.font_beg + "\\small"
		sflag = 1
	    
	    if sflag == 1:
		thisstyle.font_end = thisstyle.font_end + "\\normalsize"

            if font.get_underline():
	        thisstyle.font_beg = thisstyle.font_beg + "\\underline{"
		thisstyle.font_end = "}" + thisstyle.font_end

	    thisstyle.font_beg = thisstyle.font_beg + " "
	    thisstyle.font_end = thisstyle.font_end + " "

	    left  = style.get_left_margin()
	    right = style.get_right_margin()
	    first = style.get_first_indent()
	    topborder = style.get_top_border()
	    bottomborder = style.get_bottom_border()
	    
	    thisstyle.leftIndent = left
	    thisstyle.rightIndent = right
	    thisstyle.firstLineIndent = first
	    thisstyle.topBorder = topborder
	    thisstyle.bottomBorder = bottomborder
	    
	    self.latexstyle[style_name] = thisstyle
	    
	    

    def close(self):
        """Clean up and close the document"""
        if self.in_list:
            self.f.write('\\end{enumerate}\n')
        self.f.write('\n\\end{document}\n')
	if not self.alreadyOpen:
            self.f.close()

    def start_page(self,orientation=None):
        """Nothing needs to be done to start a page"""
        pass

    def end_page(self):
        """Issue a new page command"""
        self.f.write('\\newpage')

    def start_listing(self, style_name):
        """Set up parameters for Verbatim environment of fancyvrb package"""

        style = self.style_list[style_name]
        font = style.get_font()
	size = font.get_size()
	# Determine font family
	if font.get_type_face() == FONT_MONOSPACE:
	    family = "courier"
	elif font.get_type_face() == FONT_SANS_SERIF:
	    family = "helvetica"
	else:
	    family = "tt"
	# Now determine font size 
	if size >= 22:
	    size = "\\Huge"
	elif size >= 20:
	    size = "\\huge"
	elif size >= 18:
	    size = "\\LARGE"
	elif size >= 16:
	    size = "\\Large"
	elif size >= 14:
	    size = "\\large"
	elif size < 8:
	    size = "\\scriptsize"
	elif size < 10:
	    size = "\\footnotesize"
	elif size < 12:
	    size = "\\small"
	else:
	    size = "\\normalsize"
	if font.get_bold():
	    series = 'b'
	else:
	    series = 'm'
	if font.get_italic():
	    shape = 'it'
	else:
	    shape = 'n'
	leftMargin = style.get_left_margin()
	rightMargin = style.get_right_margin()
	if style.get_top_border() and style.get_bottom_border():
	    if style.get_left_border() and style.get_right_border():
	        frame = "single"
	    else:
	        frame = "lines"
	elif style.get_top_border():
	    frame = "topline"
	elif style.get_bottom_border():
	    frame = "bottomline"
	else:
	    frame = ""

	self.f.write("\\begin{Verbatim}%\n")
	self.f.write("  [fontfamily=%s,\n" % family)
	self.f.write("   fontsize=%s,\n" % size)
	self.f.write("   fontshape=%s,\n" % shape)
	self.f.write("   fontseries=%s,\n" % series)
	if frame:
	    self.f.write("   frame=%s,\n" % frame)
	self.f.write("   xleftmargin=%.2fcm,\n" % leftMargin)
	self.f.write("   xrightmargin=%.2fcm]\n" % rightMargin)
	self.last_char_written = '\n'
	self.in_listing = 1

    def end_listing(self):
        if self.last_char_written != '\n':
	    self.f.write('\n')
	self.f.write('\\end{Verbatim}\n')
	self.in_listing = 0

    def start_paragraph(self,style_name,leader=None):
        """Paragraphs handling - A Gramps paragraph is any 
	single body of text, from a single word, to several sentences.
	We assume a linebreak at the end of each paragraph."""

        style = self.style_list[style_name]
	# Patch to get alignment in table cells working properly
	alignment = style.get_alignment()
	if alignment == PARA_ALIGN_RIGHT:
	    self.cell_para_align = 'r'
	elif alignment == PARA_ALIGN_CENTER:
	    self.cell_para_align = 'c'
	else:
	    self.cell_para_align = 'l'
	if self.in_cell and not self.cell_header_written:
	    if self.llist == 1:
	        cellfmt = "p{\linewidth-3cm}"
	    elif self.tablewidth:
	        width = 0.0
	        for i in range(self.cell_span):
		    width = width + self.colwidths[self.cell_cnt + i]
	        cellfmt = "p{%.2f\\textwidth}" % (width * 0.95)
	    else:
	        cellfmt = self.cell_para_align
	    # Account for vertical rules
	    if self.lborder == 1:
	        cellfmt = '|' + cellfmt
	    if self.rborder == 1:
	        cellfmt = cellfmt + '|'
	    if self.tborder != 0 and self.cell_cnt == 0:
	        self.f.write('\\hline ')
	    self.f.write ('\\multicolumn{%d}{%s}{' % (self.cell_span,cellfmt))
	    self.cell_header_written = 1
	
	ltxstyle = self.latexstyle[style_name]
        self.level = style.get_header_level()

	self.fbeg = ltxstyle.font_beg 
	self.fend = ltxstyle.font_end
	self.indent = ltxstyle.leftIndent
	self.rightmargin = ltxstyle.rightIndent
	self.FLindent = ltxstyle.firstLineIndent
	self.TBorder = ltxstyle.topBorder
	self.BBorder = ltxstyle.bottomBorder
	
	# Adjust the first line indent if needed
	if self.FLindent != self.last_indent and not self.in_table:
	    self.last_indent = self.FLindent
	    myspace = '%scm' % str(self.FLindent)
	    self.f.write('\\grampsfirst{%s}\n' % myspace)
	    self.fix_first = 1
	    
        if leader != None and not self.in_list:
            self.f.write('\\begin{enumerate}\n')
            self.in_list = 1
        if leader != None:
	    self.f.write('  \\setcounter{enumi}{%s} ' % leader[:-1])
	    self.f.write('  \\addtocounter{enumi}{-1}\n')
            self.f.write('  \\item ')

	if leader == None and not self.in_list and not self.in_table:
	    self.f.write('\n')
	
	# Patch for special handling of cell contents
	font_begin = self.fbeg
	if self.in_cell:
	    if not self.tablewidth and string.find(font_begin, '\\hspace*{\\fill}') == 0:
	        font_begin = font_begin[15:]
	# Use parbox command to simulate left and right margins if needed
	# Use rule element to make top border if needed
	else:
	    boxcmd = ""
	    if self.indent or self.rightmargin:
	        boxcmd = "\\setlength{\\newwidth}{\\textwidth - %.2fcm}" % \
		         float(self.indent + self.rightmargin)
		boxcmd = boxcmd + "\\hspace*{%.2fcm}\n" % float(self.indent)
		boxcmd = boxcmd + "\\parbox{\\newwidth}{"
	        if self.TBorder:
	            boxcmd = boxcmd + "\\vspace{0.5ex}\\rule{\\newwidth}{0.5pt}\\newline\n"
	    elif self.TBorder:
	        boxcmd = boxcmd + "\\rule{\\textwidth}{0.5pt}\\newline\n"
	    font_begin = boxcmd + font_begin
        self.f.write('%s ' % font_begin)
    
    def end_paragraph(self):
        """End the current paragraph"""
	#newline = '\ \\newline\n'
	newline = '\n'

	if self.in_list:
	    self.in_list = 0
	    self.f.write('\n\\end{enumerate}\n')
	    newline = ''

	elif self.in_table:
	    newline = ('')

        # Draw bottom border and close parbox command if needed
	if not self.in_cell:
	    if self.BBorder:
	        if (self.indent or self.rightmargin):
	            newline = newline + "\\ \\newline\\rule[0.5\\baselineskip]{\\newwidth}{0.5pt}\n"
	            newline = newline + '}\n'
		else:
	            newline = newline + "\\ \\newline\\rule[0.5\\baselineskip]{\\textwidth}{0.5pt}\n"
	    elif self.indent or self.rightmargin:
	        newline = newline + '}\n'

	# Patch for special handling of cell contents
	font_end = self.fend
	if self.in_cell:
	    if not self.tablewidth and string.find(font_end, '\\hspace*{\\fill}') == 0:
	        font_end = font_end[15:]
        self.f.write('%s%s' % (font_end,newline))
	if self.fix_first == 1:
	    self.last_indent = 0
	    self.fix_first = 0
	    self.f.write('\\grampsfirst{0cm}\n')

    def start_bold(self):
        """Bold face"""
        self.f.write('\\textbf{')

    def end_bold(self):
        """End bold face"""
        self.f.write('}')

    def start_italic(self):
        """Italic face"""
        self.f.write('\\textit{')

    def end_italic(self):
        """End italic face"""
        self.f.write('}')

    def start_table(self,name,style_name):
        """Begin new table"""
	self.in_cell = 0
	self.cell_header_written = 0
	self.in_table = 1
	self.currow = 0

	# We need to know a priori how many columns are in this table
	self.tblstyle = self.table_styles[style_name]
	self.numcols = self.tblstyle.get_columns()
	self.tablewidth = self.tblstyle.get_width()
	if self.tablewidth:
	    self.colwidths = []
	    tblfmt = ""
	    for i in range(self.numcols):
	        width = self.tblstyle.get_column_width(i)
	        mult = float(width * self.tablewidth) / 10000.0
	        self.colwidths.append(mult)
		tblfmt = tblfmt + "p{%.2f\\textwidth}" % (mult * 0.95)
	else:
	    tblfmt = '*{%d}{l}' % self.numcols
	self.f.write('\n\n\\begin{longtable}[l]{%s}\n' % tblfmt)

    def end_table(self):
        """Close the table environment"""
	self.in_table = 0
	# Create a paragraph separation below the table.
	self.f.write('\\end{longtable}\n\\par\n')

    def start_row(self):
        """Begin a new row"""
	# doline/skipfirst are flags for adding hor. rules
	self.cell_cnt = -1
	self.doline = 0
	self.skipfirst = 0
        self.curcol = 0
	self.currow = self.currow + 1
	
    def end_row(self):
        """End the row (new line)"""
	self.f.write('\\\\ ')
	if self.doline == 1:
	    if self.skipfirst == 1:
		self.f.write('\\cline{2-%d}\n' % self.numcols)
	    else:
		self.f.write('\\hline\n')
	else:
	    self.f.write('\n')
	    
    def start_cell(self,style_name,span=1):
        """Add an entry to the table.
	   We always place our data inside braces 
	   for safety of formatting."""
	self.cell_cnt = self.cell_cnt + 1
	self.in_cell = 1
	self.cell_span = span
	self.cell_header_written = 0
	self.colspan = span
	self.curcol = self.curcol + self.colspan

	self.cstyle = self.cell_styles[style_name]
	self.lborder = self.cstyle.get_left_border()
	self.rborder = self.cstyle.get_right_border()
	self.bborder = self.cstyle.get_bottom_border()
	self.tborder = self.cstyle.get_top_border()
	self.llist = self.cstyle.get_longlist()
	
	# Patched out - functionality moved to start of paragraph
	# because we have to wait until then to find out the
	# alignment properties of the paragraph which is the
	# contents of the cell

	##if self.llist == 1:
	##    cellfmt = "p{\linewidth-3cm}"
	##else:
	##    cellfmt = self.cell_para_align
	##self.cellfmt = cellfmt
	    
	## Account for vertical rules
	##if self.lborder == 1:
	##    cellfmt = '|' + cellfmt
	##if self.rborder == 1:
	##    cellfmt = cellfmt + '|'

	# and Horizontal rules
	if self.bborder == 1:
	    self.doline = 1 
	elif self.curcol == 1: 
	    self.skipfirst = 1
	    
	##if self.tborder != 0:
	##    self.f.write('\\hline\n')
	##self.f.write ('\\multicolumn{%d}{%s}{' % (span,cellfmt))
	
    def end_cell(self):
        """Prepares for next cell"""
	self.in_cell = 0
	self.cell_header_written = 0
	self.f.write('} ')
	if self.curcol < self.numcols:
	    self.f.write('& ')

    def add_photo(self,name,pos,x,y):
        """Add photo to report"""
	self.imagenum = self.imagenum + 1
        pic = ImgManip.ImgManip(name)
	picf = self.filename[:-4] + '_img' + str(self.imagenum) + '.eps'
	pic.eps_convert(picf)
	
	# x and y will be maximum width OR height in units of cm
	mysize = 'width=%dcm,height=%dcm,keepaspectratio' % (x,y)
	if pos == "right":
	    self.f.write('\\hspace*{\\fill}\\includegraphics[%s]{%s}\n' % (mysize,picf))
	elif pos == "left":
	    self.f.write('\\includegraphics[%s]{%s}\\hspace*{\\fill}\n' % (mysize,picf))
	else:
	    self.f.write('\\hspace*{\\fill}\\includegraphics[%s]{%s}\hspace*{\\fill}\n' % (mysize,picf))

    def write_text(self,text):
        """Write the text to the file"""
	if not self.in_listing:
	    if text == '\n':
	        text = '\\newline\n'
            else:
                # Quote unsafe characters.
                text = sub('[\\$&%#{}_^~]',quote_fun,text)
        self.f.write(text)
	if text:
	    self.last_char_written = text[-1]

    def line_break(self):
        self.f.write('\\newline\n')

    def page_break(self):
        self.f.write('\\newpage\n')

    def show_link(self, text, href):
        self.write_text("%s (" % text)
	self.start_italic()
	self.write_text(href)
	self.end_italic()
	self.write_text(") ")

def quote_fun(matchobj):
    """Quote unsafe LaTeX characters"""
    c = matchobj.group()
    if c == '^':
        return '\\verb+^+'
    elif c == '~':
        return '\\verb+~+'
    else:
        return '\\' + c


#------------------------------------------------------------------------
#
# Register the document generator with the system if in Gramps
#
#------------------------------------------------------------------------
if withGramps:
    Plugins.register_text_doc(
        name=_("LaTeX"),
        classref=LaTeXDoc,
        table=1,
        paper=1,
        style=1
        )
