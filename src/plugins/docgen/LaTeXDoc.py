#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
# Copyright (C) 2008       Raphael Ackermann
#               2002-2003  Donald A. Peterson
#               2003       Alex Roitman
#               2009       Benny Malengier
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

# $Id:LaTeXDoc.py 9912 2008-01-22 09:17:46Z acraphae $

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

from gen.plug import PluginManager, DocGenPlugin
from gen.plug.docgen import BaseDoc, TextDoc
from gen.plug.docgen.basedoc import PAPER_LANDSCAPE, FONT_SANS_SERIF
from gen.plug.docbackend import LateXBackend, latexescape
import ImgManip
import Errors
import Utils

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
class TexFont(object):
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
# LaTeXDoc
#
#------------------------------------------------------------------------

class LaTeXDoc(BaseDoc, TextDoc):
    """LaTeX document interface class. Derived from BaseDoc"""

    def page_break(self):
        "Forces a page break, creating a new page"
        self._backend.write('\\newpage ')
    
    def open(self, filename):
        """Opens the specified file, making sure that it has the
        extension of .tex"""
        self._backend = LateXBackend(filename)
        self._backend.open()

        # Font size control seems to be limited. For now, ignore
        # any style constraints, and use 12pt has the default
        
        options = "12pt"

        if self.paper.get_orientation() == PAPER_LANDSCAPE:
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
        self._backend.write('\\documentclass[%s]{article}\n' % options)
        self._backend.write('\\usepackage[T1]{fontenc}\n')
        self._backend.write('%\n% We use latin1 encoding at a minimum by default.\n')
        self._backend.write('% GRAMPS uses unicode UTF-8 encoding for its\n')
        self._backend.write('% international support. LaTeX can deal gracefully\n')
        self._backend.write('% with unicode encoding by using the ucs style invoked\n')
        self._backend.write('% when utf8 is specified as an option to the inputenc\n')
        self._backend.write('% package. This package is included by default in some\n')
        self._backend.write('% installations, but not in others, so we do not make it\n')
        self._backend.write('% the default.  Uncomment the second line if you wish to use it\n')
        self._backend.write('% (If you do not have ucs.sty, you may obtain it from\n')
        self._backend.write('%  http://www.tug.org/tex-archive/macros/latex/contrib/supported/unicode/)\n')
        self._backend.write('%\n')
        self._backend.write('\\usepackage[latin1]{inputenc}\n')
        self._backend.write('%\\usepackage[latin1,utf8]{inputenc}\n')
        # add packages (should be standard on a default installation)
        # for finer output control.  Put comments in file for user to read
        self._backend.write('\\usepackage{graphicx}  % Extended graphics support\n')
        self._backend.write('\\usepackage{longtable} % For multi-page tables\n')
        self._backend.write('\\usepackage{calc} % For margin indents\n')
        self._backend.write('%\n% Depending on your LaTeX installation, the')
        self._backend.write(' margins may be too\n% narrow. ')
        self._backend.write(' This can be corrected by uncommenting the following\n')
        self._backend.write('% two lines and adjusting the width appropriately.')
        self._backend.write(' The example\n% removes 0.5in from each margin.')
        self._backend.write(' (Adds 1 inch to the text)\n')
        self._backend.write('%\\addtolength{\\oddsidemargin}{-0.5in}\n')
        self._backend.write('%\\addtolength{\\textwidth}{1.0in}\n%\n')
        self._backend.write('% Create a margin-adjusting command that allows LaTeX\n')
        self._backend.write('% to behave like the other gramps-supported output formats\n')
        self._backend.write('\\newlength{\\leftedge}\n')
        self._backend.write('\\setlength{\\leftedge}{\\parindent}\n')
        self._backend.write('\\newlength{\\grampstext}\n')
        self._backend.write('\\setlength{\\grampstext}{\\textwidth}\n')
        self._backend.write('\\newcommand{\\grampsindent}[1]{%\n')
        self._backend.write('   \\setlength{\\parindent}{\\leftedge + #1}%\n')
        self._backend.write('   \\setlength{\\textwidth}{\\grampstext - #1}%\n')
        self._backend.write('}\n\n')
        self._backend.write('\\begin{document}\n\n')
    
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
            if font.get_type_face() == FONT_SANS_SERIF:
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
            self._backend.write('\\end{enumerate}\n')
        self._backend.write('\n\\end{document}\n')
        self._backend.close()
        if self.open_req:
            Utils.open_file_with_default_application(self._backend.filename)

    def end_page(self):
        """Issue a new page command"""
        self._backend.write('\\newpage')

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
    
        if self.indent is not None and not self.in_table:
            myspace = '%scm' % str(self.indent)
            self._backend.write('\\grampsindent{%s}\n' % myspace)
            self.fix_indent = 1
    
            if leader is not None and not self.in_list:
                self._backend.write('\\begin{enumerate}\n')
                self.in_list = 1
            if leader is not None:
                # try obtaining integer
                leader_1 = leader[:-1]
                num = roman2arabic(leader_1)
                if num == 0:
                    # Not roman, try arabic or fallback to 1
                    try:
                        num = int(leader_1)
                    except ValueError:
                        num = 1
                    self._backend.write('  \\renewcommand\\theenumi{\\arabic{enumi}}')
                else:
                    # roman, set the case correctly
                    if leader_1.islower():
                        self._backend.write('  \\renewcommand\\theenumi{\\roman{enumi}}')
                    else:
                        self._backend.write('  \\renewcommand\\theenumi{\\Roman{enumi}}')
    
                self._backend.write('  \\setcounter{enumi}{%d} ' % num)
                self._backend.write('  \\addtocounter{enumi}{-1}\n')
                self._backend.write('  \\item ')

        if leader is None and not self.in_list and not self.in_table:
            self._backend.write('\n')
        
            self._backend.write('%s ' % self.fbeg)
    
    def end_paragraph(self):
        """End the current paragraph"""
        newline = '\ \\newline\n'
    
        if self.in_list:
            self.in_list = 0
            self._backend.write('\n\\end{enumerate}\n')
            newline = ''
    
        elif self.in_table:
            newline = ('')
    
        self._backend.write('%s%s' % (self.fend, newline))
        if self.fix_indent == 1:
            self.fix_indent = 0
            self._backend.write('\\grampsindent{0cm}\n')

    def start_bold(self):
        """Bold face"""
        self._backend.write('\\textbf{')

    def end_bold(self):
        """End bold face"""
        self._backend.write('}')
        
    def start_superscript(self):
        self._backend.write('\\textsuperscript{')

    def end_superscript(self):
        self._backend.write('}')

    def start_table(self, name,style_name):
        """Begin new table"""
        self.in_table = 1
        self.currow = 0

        # We need to know a priori how many columns are in this table
        styles = self.get_style_sheet()
        self.tblstyle = styles.get_table_style(style_name)
        self.numcols = self.tblstyle.get_columns()

        tblfmt = '*{%d}{l}' % self.numcols
        self._backend.write('\n\n\\begin{longtable}[l]{%s}\n' % tblfmt)

    def end_table(self):
        """Close the table environment"""
        self.in_table = 0
        # Create a paragraph separation below the table.
        self._backend.write('\\end{longtable}\n\\par\n')

    def start_row(self):
        """Begin a new row"""
        # doline/skipfirst are flags for adding hor. rules
        self.doline = 0
        self.skipfirst = 0
        self.curcol = 0
        self.currow = self.currow + 1
    
    def end_row(self):
        """End the row (new line)"""
        self._backend.write('\\\\ ')
        if self.doline == 1:
            if self.skipfirst == 1:
                self._backend.write('\\cline{2-%d}\n' % self.numcols)
            else:
                self._backend.write('\\hline \\\\ \n')
        else:
            self._backend.write('\n')
        
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
            self._backend.write('\\hline\n')
        self._backend.write ('\\multicolumn{%d}{%s}{' % (span,cellfmt))
    
    def end_cell(self):
        """Prepares for next cell"""
        self._backend.write('} ')
        if self.curcol < self.numcols:
            self._backend.write('& ')

    def add_media_object(self, name,pos,x,y):
        """Add photo to report"""
        return

        try:
            pic = ImgManip.ImgManip(name)
        except:
            return

        self.imagenum = self.imagenum + 1
        picf = self.filename[:-4] + '_img' + str(self.imagenum) + '.eps'
        pic.eps_convert(picf)
        
        # x and y will be maximum width OR height in units of cm
        mysize = 'width=%dcm, height=%dcm,keepaspectratio' % (x,y)
        if pos == "right":
            self._backend.write('\\hfill\\includegraphics[%s]{%s}\n' % (mysize,picf))
        elif pos == "left":
            self._backend.write('\\includegraphics[%s]{%s}\\hfill\n' % (mysize,picf))
        else:
            self._backend.write('\\centerline{\\includegraphics[%s]{%s}}\n' % (mysize,picf))

    def write_text(self,text,mark=None):
        """Write the text to the file"""
        if text == '\n':
            text = '\\newline\n'
        text = latexescape(text)
        #hard coded replace of the underline used for missing names/data
        text = text.replace('\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_',
                            '\\underline{\hspace{3cm}}')
        self._backend.write(text)

    def write_styled_note(self, styledtext, format, style_name):
        """
        Convenience function to write a styledtext to the latex doc. 
        styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        
        @note: text=normal text, p_text=text with pango markup, s_tags=styled
                text tags, p
        """
        text = str(styledtext)

        s_tags = styledtext.get_tags()
        if format == 1:
            #preformatted, use different escape function
            self._backend.setescape(True)
        
        markuptext = self._backend.add_markup_from_styled(text, s_tags)
        
        #there is a problem if we write out a note in a table. No newline is
        # possible, the note runs over the margin into infinity.
        # A good solution for this ???
        # A quick solution: create a minipage for the note and add that always
        #   hoping that the user will have left sufficient room for the page
        self._backend.write("\\begin{minipage}{{0.8\\linewidth}}\n")
        self.start_paragraph(style_name)
        self._backend.write(markuptext)
        self.end_paragraph()
        #end the minipage, add trick to have a white line at bottom of note,
        # we assume here a note should be distinct from its surrounding.
        self._backend.write("\n\\vspace*{0.5cm} \n\end{minipage}\n\n")
        if format == 1:
            #preformatted finished, go back to normal escape function
            self._backend.setescape(False)

    def write_note(self,text,format,style_name):
        """Write the note's text to the file, respecting the format"""
        self.start_paragraph(style_name)
        if format == 1:
            self._backend.write('\\begin{verbatim}')
        self.write_text(text)
        if format == 1:
            self._backend.write('\\end{verbatim}')
        self.end_paragraph()

#------------------------------------------------------------------------
#
# register_plugin
#
#------------------------------------------------------------------------
def register_plugin():
    """
    Register the document generator with the GRAMPS plugin system.
    """
    pmgr = PluginManager.get_instance()
    plugin = DocGenPlugin(name        = _('LaTeX'), 
                          description = _("Generates documents in LaTeX "
                                          "format."),
                          basedoc     = LaTeXDoc,
                          paper       = True,
                          style       = False, 
                          extension   = "tex" )
    pmgr.register_plugin(plugin)
    
register_plugin()
