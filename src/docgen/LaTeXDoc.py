#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007       Brian G. Matherly
#
# Modifications and feature additions:
#               2002-2003  Donald A. Peterson
# 
# Formatted notes addition:
#               2003  Alex Roitman
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

"""LaTeX document generator"""

#------------------------------------------------------------------------
#
# python modules 
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# gramps modules 
#
#------------------------------------------------------------------------
import BaseDoc
from PluginUtils import register_text_doc
import ImgManip
import Errors

#------------------------------------------------------------------------
#
# Convert from roman to arabic numbers
#
#------------------------------------------------------------------------
def roman2arabic(strval):
    """
    Roman to arabic converter for 0 < num < 4000.

    Always returns an integer.
    On an invalid input zero is returned.
    """
    # Return zero if the type is not str
    try:
        strval = str(strval).upper()
        if not strval:
            return 0
    except:
        return 0

    # Return None if there are chars outside of valid roman numerals
    if [char for char in strval if char not in 'MDCLXVI']:
        return 0

    vals2 = ['CM', 'CD', 'XC', 'XL', 'IX', 'IV']
    nums2 = ( 900,  400,   90,   40,    9,    4)

    vals1 = [ 'M', 'D', 'C', 'L', 'X', 'V', 'I']
    nums1 = (1000, 500, 100,  50,  10,   5,   1)

    ret = 0
    max_num = 1000
    # Start unrolling strval from left to right,
    # up to the penultimate char
    i = 0
    while i < len(strval):
        first_index = vals1.index(strval[i])

        if i+1 < len(strval) and strval[i:i+2] in vals2:
            this_num = nums2[vals2.index(strval[i:i+2])]
            if first_index+1 < len(nums1):
                new_max_num = nums1[first_index+1]
            else:
                new_max_num = 0
            i += 2
        else:
            this_num = nums1[first_index]
            new_max_num = this_num
            i += 1

        # prohibit larger numbers following smaller ones,
        # except for the above 2-char combinations
        if this_num >  max_num:
            return 0
        ret += this_num
        max_num = new_max_num

    return ret
            
#------------------------------------------------------------------------
#
# Paragraph Handling
#
#------------------------------------------------------------------------
class TexFont:
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
class LaTeXDoc(BaseDoc.BaseDoc,BaseDoc.TextDoc):
    """LaTeX document interface class. Derived from BaseDoc"""
    
    def open(self,filename):
        """Opens the specified file, making sure that it has the
        extension of .tex"""
        
        if filename[-4:] != ".tex":
            self.filename = filename + ".tex"
        else:
            self.filename = filename

        try:
            self.f = open(self.filename,"w")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise Errors.ReportError(errmsg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.filename)

        # Font size control seems to be limited. For now, ignore
        # any style constraints, and use 12pt has the default
        
        options = "12pt"

        if self.paper.get_orientation() == BaseDoc.PAPER_LANDSCAPE:
            options = options + ",landscape"

        # Paper selections are somewhat limited on a stock installation. 
        # If the user picks something not listed here, we'll just accept
        # the default of the user's LaTeX installation (usually letter).
        paper_name = self.paper.get_size().get_name()
        if paper_name == "A4":
            options = options + ",a4paper"
        elif paper_name == "A5":
            options = options + ",a5paper"
        elif paper_name == "B5":
            options = options + ",b4paper"
        elif paper_name == "Legal":
            options = options + ",legalpaper"
        elif paper_name == "Letter":
            options = options + ",letterpaper"

        # Use the article template, T1 font encodings, and specify
        # that we should use Latin1 and unicode character encodings.
        self.f.write('\\documentclass[%s]{article}\n' % options)
        self.f.write('\\usepackage[T1]{fontenc}\n')
        self.f.write('%\n% We use latin1 encoding at a minimum by default.\n')
        self.f.write('% GRAMPS uses unicode UTF-8 encoding for its\n')
        self.f.write('% international support. LaTeX can deal gracefully\n')
        self.f.write('% with unicode encoding by using the ucs style invoked\n')
        self.f.write('% when utf8 is specified as an option to the inputenc\n')
        self.f.write('% package. This package is included by default in some\n')
        self.f.write('% installations, but not in others, so we do not make it\n')
        self.f.write('% the default.  Uncomment the second line if you wish to use it\n')
        self.f.write('% (If you do not have ucs.sty, you may obtain it from\n')
        self.f.write('%  http://www.tug.org/tex-archive/macros/latex/contrib/supported/unicode/)\n')
        self.f.write('%\n')
        self.f.write('\\usepackage[latin1]{inputenc}\n')
        self.f.write('%\\usepackage[latin1,utf8]{inputenc}\n')
        # add packages (should be standard on a default installation)
        # for finer output control.  Put comments in file for user to read
        self.f.write('\\usepackage{graphicx}  % Extended graphics support\n')
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
        self.imagenum = 0
        
        #Establish some local styles for the report
        self.latexstyle = {}
        self.latex_font = {}
        
        style_sheet = self.get_style_sheet()
        for style_name in style_sheet.get_paragraph_style_names():
            style = style_sheet.get_paragraph_style(style_name)
            font = style.get_font()
            size = font.get_size()
            
            self.latex_font[style_name] = TexFont()
            thisstyle = self.latex_font[style_name]
            
            thisstyle.font_beg = ""
            thisstyle.font_end = ""
            # Is there special alignment?  (default is left)
            align = style.get_alignment_text()
            if  align == "center":
                thisstyle.font_beg = thisstyle.font_beg + "\\centerline{"
                thisstyle.font_end = "}" + thisstyle.font_end 
            elif align == "right":
                thisstyle.font_beg = thisstyle.font_beg + "\\hfill"
    
            # Establish font face and shape
            if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
                thisstyle.font_beg = thisstyle.font_beg + "\\sffamily"
                thisstyle.font_end = "\\rmfamily" + thisstyle.font_end 
            if font.get_bold():
                thisstyle.font_beg = thisstyle.font_beg + "\\bfseries"
                thisstyle.font_end = "\\mdseries" + thisstyle.font_end
            if font.get_italic() or font.get_underline():
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
    
            thisstyle.font_beg = thisstyle.font_beg + " "
            thisstyle.font_end = thisstyle.font_end + " "
    
            left  = style.get_left_margin()
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

    def end_page(self):
        """Issue a new page command"""
        self.f.write('\\newpage')

    def start_paragraph(self,style_name,leader=None):
        """Paragraphs handling - A Gramps paragraph is any 
        single body of text from a single word to several sentences.
        We assume a linebreak at the end of each paragraph."""
        style_sheet = self.get_style_sheet()
    
        style = style_sheet.get_paragraph_style(style_name)
        ltxstyle = self.latexstyle[style_name]
        self.level = style.get_header_level()
    
        self.fbeg = ltxstyle.font_beg 
        self.fend = ltxstyle.font_end
        self.indent = ltxstyle.leftIndent
        self.FLindent = ltxstyle.firstLineIndent
    
        if self.indent != None and not self.in_table:
            myspace = '%scm' % str(self.indent)
            self.f.write('\\grampsindent{%s}\n' % myspace)
            self.fix_indent = 1
    
            if leader != None and not self.in_list:
                self.f.write('\\begin{enumerate}\n')
                self.in_list = 1
            if leader != None:
                # try obtaining integer
                leader_1 = leader[:-1]
                num = roman2arabic(leader_1)
                if num == 0:
                    # Not roman, try arabic or fallback to 1
                    try:
                        num = int(leader_1)
                    except ValueError:
                        num = 1
                    self.f.write('  \\renewcommand\\theenumi{\\arabic{enumi}}')
                else:
                    # roman, set the case correctly
                    if leader_1.islower():
                        self.f.write('  \\renewcommand\\theenumi{\\roman{enumi}}')
                    else:
                        self.f.write('  \\renewcommand\\theenumi{\\Roman{enumi}}')
    
                self.f.write('  \\setcounter{enumi}{%d} ' % num)
                self.f.write('  \\addtocounter{enumi}{-1}\n')
                self.f.write('  \\item ')

        if leader == None and not self.in_list and not self.in_table:
            self.f.write('\n')
        
            self.f.write('%s ' % self.fbeg)
    
    def end_paragraph(self):
        """End the current paragraph"""
        newline = '\ \\newline\n'
    
        if self.in_list:
            self.in_list = 0
            self.f.write('\n\\end{enumerate}\n')
            newline = ''
    
        elif self.in_table:
            newline = ('')
    
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
        
    def start_superscript(self):
        self.f.write('\\textsuperscript{')

    def end_superscript(self):
        self.f.write('}')

    def start_table(self,name,style_name):
        """Begin new table"""
        self.in_table = 1
        self.currow = 0

        # We need to know a priori how many columns are in this table
        styles = self.get_style_sheet()
        self.tblstyle = styles.get_table_style(style_name)
        self.numcols = self.tblstyle.get_columns()

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
        self.colspan = span
        self.curcol = self.curcol + self.colspan

        styles = self.get_style_sheet()
        self.cstyle = styles.get_cell_style(style_name)
        self.lborder = self.cstyle.get_left_border()
        self.rborder = self.cstyle.get_right_border()
        self.bborder = self.cstyle.get_bottom_border()
        self.tborder = self.cstyle.get_top_border()
        self.llist = self.cstyle.get_longlist()

        if self.llist == 1:
            cellfmt = "p{\linewidth-3cm}"
        else:
            cellfmt = "l"
        
        # Account for vertical rules
        if self.lborder == 1:
            cellfmt = '|' + cellfmt
        if self.rborder == 1:
            cellfmt = cellfmt + '|'

        # and Horizontal rules
        if self.bborder == 1:
            self.doline = 1 
        elif self.curcol == 1: 
           self.skipfirst = 1

        if self.tborder != 0:
            self.f.write('\\hline\n')
        self.f.write ('\\multicolumn{%d}{%s}{' % (span,cellfmt))
    
    def end_cell(self):
        """Prepares for next cell"""
        self.f.write('} ')
        if self.curcol < self.numcols:
            self.f.write('& ')

    def add_media_object(self,name,pos,x,y):
        """Add photo to report"""

        try:
            pic = ImgManip.ImgManip(name)
        except:
            return

        self.imagenum = self.imagenum + 1
        picf = self.filename[:-4] + '_img' + str(self.imagenum) + '.eps'
        pic.eps_convert(picf)
        
        # x and y will be maximum width OR height in units of cm
        mysize = 'width=%dcm,height=%dcm,keepaspectratio' % (x,y)
        if pos == "right":
            self.f.write('\\hfill\\includegraphics[%s]{%s}\n' % (mysize,picf))
        elif pos == "left":
            self.f.write('\\includegraphics[%s]{%s}\\hfill\n' % (mysize,picf))
        else:
            self.f.write('\\centerline{\\includegraphics[%s]{%s}}\n' % (mysize,picf))
        
    def write_note(self,text,format,style_name):
        """Write the note's text to the file, respecting the format"""
        self.start_paragraph(style_name)
        if format == 1:
            self.f.write('\\begin{verbatim}')
        self.write_text(text)
        if format == 1:
            self.f.write('\\end{verbatim}')
        self.end_paragraph()

    def write_text(self,text,mark=None):
        """Write the text to the file"""
        if text == '\n':
            text = '\\newline\n'
            text = text.replace('#','\#')
            text = text.replace('&','\&')
            text = text.replace('<super>','\\textsuperscript{')
            text = text.replace('</super>','}')
            text = text.replace('_____________','\\underline{\hspace{3cm}}')
            self.f.write(text)


#------------------------------------------------------------------------
#
# Register the document generator with the system
#
#------------------------------------------------------------------------
register_text_doc(
    name=_("LaTeX"),
    classref=LaTeXDoc,
    table=1,
    paper=1,
    style=0,
    ext=".tex"
    )
