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

"""LaTeX document generator"""

#------------------------------------------------------------------------
#
# gramps modules 
#
#------------------------------------------------------------------------
from TextDoc import *
import Plugins
import intl
_ = intl.gettext

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
	    self.firstLineIndent = style.firstLineIndent
	else:
	    self.font_beg = ""
	    self.font_end = ""
	    self.leftIndent = ""
	    self.firstLineIndent = ""
    
#------------------------------------------------------------------------
#
# LaTeXDon
#
#------------------------------------------------------------------------
class LaTeXDoc(TextDoc):
    """LaTeX document interface class. Derived from TextDoc"""
    
    def open(self,filename):
        """Opens the specified file, making sure that it has the
        extension of .tex"""
        
        if filename[-4:] != ".tex":
            self.filename = filename + ".tex"
        else:
            self.filename = filename
        self.f = open(self.filename,"w")

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
        self.f.write('\\usepackage{longtable} % For multi-page tables\n')
        self.f.write('\\usepackage{calc} % For margin indents\n')
	self.f.write('%\n% Depending on your LaTeX installation, the')
	self.f.write(' margins may be too\n% narrow. ')
	self.f.write(' This can be corrected by uncommenting the following\n')
	self.f.write('% two lines and adjusting the width appropriately.')
	self.f.write(' The example\n% removes 0.5in from each margin.')
	self.f.write(' (Adds 1 inch to the text)\n')
	self.f.write('%\\addtolength{\\oddsidemargin}{-0.5in}\n')
	self.f.write('%\\addtolength{\\textwidth}{1.0in}\n%\n')
	self.f.write('% Create a margin-adjusting command that allows LaTeX\n')
	self.f.write('% to behave like the other gramps-supported output formats\n')
	self.f.write('\\newlength{\\leftedge}\n')
	self.f.write('\\setlength{\\leftedge}{\\parindent}\n')
	self.f.write('\\newlength{\\grampstext}\n')
	self.f.write('\\setlength{\\grampstext}{\\textwidth}\n')
	self.f.write('\\newcommand{\\grampsindent}[1]{%\n')
	self.f.write('   \\setlength{\\parindent}{\\leftedge + #1}%\n')
	self.f.write('   \\setlength{\\textwidth}{\\grampstext - #1}%\n')
	self.f.write('}\n\n')
        self.f.write('\\begin{document}\n\n')

        self.in_list = 0
	self.in_table = 0
	
	#Establish some local styles for the report
	self.latexstyle = {}
	self.latex_font = {}
	
        for style_name in self.style_list.keys():
            style = self.style_list[style_name]
            font = style.get_font()

	    self.latex_font[style_name] = TexFont()
	    thisstyle = self.latex_font[style_name]
	    
	    thisstyle.font_beg = ""
	    thisstyle.font_end = ""
	    if font.get_type_face() == FONT_SANS_SERIF:
		thisstyle.font_beg = thisstyle.font_beg + "\\sffamily"
		thisstyle.font_end = "\\rmfamily" + thisstyle.font_end 
	    if font.get_bold():
		thisstyle.font_beg = thisstyle.font_beg + "\\bfseries"
		thisstyle.font_end = "\\mdseries" + thisstyle.font_end
	    if font.get_italic() or font.get_underline():
		thisstyle.font_beg = thisstyle.font_beg + "\\itshape"
		thisstyle.font_end = "\\upshape" + thisstyle.font_end

	    thisstyle.font_beg = thisstyle.font_beg + " "
	    thisstyle.font_end = thisstyle.font_end + " "

	    left  = style.get_left_margin()
	    right = style.get_right_margin()
	    first = style.get_first_indent() + left
	    
	    thisstyle.leftIndent = left
	    thisstyle.firstLineIndent = first
	    
	    self.latexstyle[style_name] = thisstyle
	    
	    

    def close(self):
        """Clean up and close the document"""
        if self.in_list:
            self.f.write('\\end{enumerate}\n')
        self.f.write('\n\\end{document}\n')
        self.f.close()

    def start_page(self,orientation=None):
        """Nothing needs to be done to start a page"""
        pass

    def end_page(self):
        """Issue a new page command"""
        self.f.write('\\newpage')

    def start_paragraph(self,style_name,leader=None):
        """Paragraphs handling - A Gramps paragraph is any 
	single body of text, from a single word, to several sentences.
	We assume a linebreak at the end of each paragraph."""

        style = self.style_list[style_name]
	ltxstyle = self.latexstyle[style_name]
        self.level = style.get_header_level()

	self.fbeg = ltxstyle.font_beg 
	self.fend = ltxstyle.font_end
	self.indent = ltxstyle.leftIndent
	self.FLindent = ltxstyle.firstLineIndent
	
	if self.indent != None and not self.in_table:
	    myspace = _('%scm' % str(self.indent))
	    self.f.write('\\grampsindent{%s}\n' % myspace)
	    self.fix_indent = 1
	    
        if leader != None and not self.in_list:
            self.f.write('\\begin{enumerate}\n')
            self.in_list = 1
        if leader != None:
	    self.f.write('  \\setcounter{enumi}{%s} ' % leader[:-1])
	    self.f.write('  \\addtocounter{enumi}{-1}\n')
            self.f.write('  \\item ')

	if leader == None and not self.in_list and not self.in_table:
	    self.f.write('\n')
	
        self.f.write('%s ' % self.fbeg)
    
    def end_paragraph(self):
        """End the current paragraph"""
	newline = _('\ \\newline\n')

	if self.in_list:
	    self.in_list = 0
	    self.f.write('\n\\end{enumerate}\n')

	elif self.in_table:
	    newline = _('')

	self.f.write('%s%s' % (self.fend,newline))
	if self.fix_indent == 1:
	    self.fix_indent = 0
	    self.f.write('\\grampsindent{0cm}\n')

    def start_bold(self):
        """Bold face"""
        self.f.write('\\textbf{')

    def end_bold(self):
        """End bold face"""
        self.f.write('}')

    def start_table(self,name,style_name):
        """Begin new table"""
	self.in_table = 1
	self.currow = 0
	# We need to know a priori how many columns are in this table
	self.tblstyle = self.table_styles[style_name]
	self.numcols = self.tblstyle.get_columns()

	tblfmt = _('*{%d}{l}' % self.numcols)
	self.f.write('\n\n\\begin{longtable}{%s}\n' % tblfmt)

    def end_table(self):
        """Close the table environment"""
	self.in_table = 0
	# Using \hfill immediately after the tabular should left-justify
	# the entire table, then create a paragraph separation below it.
	self.f.write('\\end{longtable}\n\\hfill\\par\n')

    def start_row(self):
        """Begin a new row"""
	# doline is a flag for adding "\hline" at the end
	# (doesn't quite work yet)
#	self.doline = 0
        self.curcol = 1
	self.currow = self.currow + 1
	
    def end_row(self):
        """End the row (new line)"""
	if self.currow == 1:
	    self.f.write('\\\\ \\hline\n')
	else:
	    self.f.write('\\\\ \n')
	    
    def start_cell(self,style_name,span=1):
        """Add an entry to the table.
	   We always place our data inside braces 
	   for safety of formatting."""
	self.colspan = span
	cellfmt = ""
	if span != 1:
	    cellfmt = ('\\multicolumn{%d}{l}{' % span)
#	    self.doline = 1 
	    
	self.f.write('%s' % cellfmt)
	self.curcol = self.curcol + span
	
    def end_cell(self):
        """Prepares for next cell"""
	if self.colspan > 1:
	    self.f.write('}')
	if self.curcol < self.numcols:
	    self.f.write(' & ')
	self.f.write(' ')

    def add_photo(self,name,pos,x,y):
        """Currently no photo support"""
        pass
    
    def write_text(self,text):
        """Write the text to the file"""
        self.f.write(text)


#------------------------------------------------------------------------
#
# Register the document generator with the system
#
#------------------------------------------------------------------------
Plugins.register_text_doc(
    name=_("LaTeX"),
    classref=LaTeXDoc,
    table=1,
    paper=1,
    style=0
    )
