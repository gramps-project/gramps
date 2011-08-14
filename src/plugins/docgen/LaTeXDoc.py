#
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
# Copyright (C) 2008       Raphael Ackermann
#               2002-2003  Donald A. Peterson
#               2003       Alex Roitman
#               2009       Benny Malengier
#               2010       Peter Landgren
#               2011       Harald Rosemann
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
from gen.ggettext import gettext as _
from bisect import bisect

#----------------------------------------------------------------------- -
#
# gramps modules
#
#------------------------------------------------------------------------
from gen.plug.docgen import BaseDoc, TextDoc, PAPER_LANDSCAPE, FONT_SANS_SERIF
from gen.plug.docbackend import DocBackend
import ImgManip
import Errors
import Utils
import re

#------------------------------------------------------------------------
#
# Special settings for LaTeX output
#
#------------------------------------------------------------------------
#   If there is one overwide column consuming too much space of paperwidth its
#   line(s) must be broken and wrapped in a 'minipage' with appropriate width.
#   The table construction beneath does this job but for now must know which
#   column. (Later it shall be determined in another way)
#   As to gramps in most cases it is the last column, hence:

MINIPAGE_COL = -1   #   Python indexing: last one

#   In trunk there is a 'LastChangeReport' where the last but one
#   is such a column. If you like, you can instead choose this setting:

# MINIPAGE_COL = -2   #   Python indexing: last but one

#   ----------------------------------
#   For an interim mark of an intended linebreak I use a special pattern. It
#   shouldn't interfere with normal text. The charackter '&' is used in LaTeX
#   for column separation in tables and may occur there in series. The pattern
#   is used here before column separation is set. On the other hand incoming
#   text can't show this pattern for it would have been replaced by '\&\&'.
#   So the choosen pattern will do the job without confusion:

PAT_FOR_LINE_BREAK = '&&'

#------------------------------------------------------------------------
#
# Latex Article Template
#
#------------------------------------------------------------------------

_LATEX_TEMPLATE_1 = '\\documentclass[%s]{article}\n'
_LATEX_TEMPLATE = '''%
%
% Vertical spacing between paragraphs:
% take one of three possibilities or modify to your taste:
%\\setlength{\\parskip}{1.0ex plus0.2ex minus0.2ex}
\\setlength{\\parskip}{1.5ex plus0.3ex minus0.3ex}
%\\setlength{\\parskip}{2.0ex plus0.4ex minus0.4ex}
%
% Vertical spacing between lines:
% take one of three possibilities or modify to your taste:
\\renewcommand{\\baselinestretch}{1.0}
%\\renewcommand{\\baselinestretch}{1.1}
%\\renewcommand{\\baselinestretch}{1.2}
%
% Indentation; substitute for '1cm' of gramps
% take one of three possibilities or modify to your taste:
\\newlength{\\grbaseindent}%
\\setlength{\\grbaseindent}{3.0em}
%\\setlength{\\grbaseindent}{2.5em}
%\\setlength{\\grbaseindent}{2.0em}
%
%
\\usepackage[T1]{fontenc}
%
% We use latin1 encoding at a minimum by default.
% GRAMPS uses unicode UTF-8 encoding for its
% international support. LaTeX can deal gracefully
% with unicode encoding by using the ucs style invoked
% when utf8 is specified as an option to the inputenc
% package. This package is included by default in some
% installations, but not in others, so we do not make it
% the default.  Uncomment the second line if you wish to use it
% (If you do not have ucs.sty, you may obtain it from
%  http://www.tug.org/tex-archive/macros/latex/contrib/supported/unicode/)
%
\\usepackage[latin1]{inputenc}
%\\usepackage[latin1,utf8]{inputenc}
\\usepackage{graphicx}  % Extended graphics support
\\usepackage{longtable} % For multi-page tables
\\usepackage{calc} % For some calculations
\\usepackage{ifthen} % For table width calculations
%
% Depending on your LaTeX installation, the margins may be too
% narrow.  This can be corrected by uncommenting the following
% two lines and adjusting the width appropriately. The example
% removes 0.5in from each margin. (Adds 1 inch to the text)
%\\addtolength{\\oddsidemargin}{-0.5in}
%\\addtolength{\\textwidth}{1.0in}
%
%
% New lengths and commands
% for calculating widths and struts in tables
%
\\newlength{\\grtempint}%
\\newlength{\\grminpgwidth}%
\\setlength{\\grminpgwidth}{0.8\\textwidth}
%
\\newcommand{\\inittabvars}[2]{%
  \\ifthenelse{\\isundefined{#1}}%
    {\\newlength{#1}}{}%
  \\setlength{#1}{#2}%
}%
%
\\newcommand{\\grcalctextwidth}[2]{%
  \\settowidth{\\grtempint}{#1}%                #1: text
  \\ifthenelse{\\lengthtest{\\grtempint > #2}}% #2: grcolwidth_
    {\\setlength{#2}{\\grtempint}}{}%
}%
%
\\newcommand{\\grminvaltofirst}[2]{%
  \\setlength{\\grtempint}{#2}%
  \\ifthenelse{\\lengthtest{#1 > \\grtempint}}%
    {\\setlength{#1}{\\grtempint}}{}%
}%
%
\\newcommand{\\grmaxvaltofirst}[2]{%
  \\setlength{\\grtempint}{#2}%
  \\ifthenelse{\\lengthtest{#1 < \\grtempint}}%
    {\\setlength{#1}{\\grtempint}}{}%
}%
%
%        lift   width   heigh
\\newcommand{\\tabheadstrutceil}{%
 \\rule[0.0ex]{0.00em}{3.5ex}}%
\\newcommand{\\tabheadstrutfloor}{%
 \\rule[-2.0ex]{0.00em}{2.5ex}}%
\\newcommand{\\tabrowstrutceil}{%
 \\rule[0.0ex]{0.00em}{3.0ex}}%
\\newcommand{\\tabrowstrutfloor}{%
 \\rule[-1.0ex]{0.00em}{3.0ex}}%
%
%
\\begin{document}
'''


#------------------------------------------------------------------------
#
# Font size table and function
#
#------------------------------------------------------------------------

# These tables correlate font sizes to Latex.  The first table contains
# typical font sizes in points.  The second table contains the standard
# Latex font size names. Since we use bisect to map the first table to the
# second, we are guaranteed that any font less than 6 points is 'tiny', fonts
# from 6-7 points are 'script', etc. and fonts greater than or equal to 22
# are considered 'Huge'.  Note that fonts from 12-13 points are not given a
# Latex font size name but are considered "normal."

_FONT_SIZES = [6, 8, 10, 12, 14, 16, 18, 20, 22]
_FONT_NAMES = ['tiny', 'scriptsize', 'footnotesize', 'small', '',
               'large', 'Large', 'LARGE', 'huge', 'Huge']

def map_font_size(fontsize):
    """ Map font size in points to Latex font size """
    return _FONT_NAMES[bisect(_FONT_SIZES, fontsize)]


#------------------------------------------------------------------------
#
# auxiliaries to facilitate table construction
#
#------------------------------------------------------------------------

# patterns for regular expressions, module re:
TBLFMT_PAT = re.compile(r'({\|?)l(\|?})')

# constants for routing in table construction:
(CELL_BEG, CELL_TEXT, CELL_END,
    ROW_BEG, ROW_END, TAB_BEG, TAB_END,
    NESTED_MINPG) = range(8)
FIRST_ROW, SUBSEQ_ROW = range(2)


def get_charform(col_num):
    """
    Transfer column number to column charakter,
    limited to letters within a-z;
    26, there is no need for more.
    early test of column count in start_table()
    """
    if col_num > ord('z') - ord('a'):
        raise ValueError, ''.join((
            '\n number of table columns is ', repr(col_num),
            '\n                     should be <= ', repr(ord('z') - ord('a'))))
    return chr(ord('a') + col_num)

def get_numform(col_char):
    return ord(col_char) - ord('a')


#------------------------------------------
#   'aa' is sufficient for up to 676 table-rows in each table;
#   do you need more?
#   uncomment one of the two lines
ROW_COUNT_BASE = 'aa'
# ROW_COUNT_BASE = 'aaa'
#------------------------------------------
def str_incr(str_counter):
    """ for counting table rows """
    lili = list(str_counter)
    while 1:
        yield ''.join(lili)
        if ''.join(lili) == len(lili)*'z':
            raise ValueError, ''.join((
                '\n can\'t increment string ', ''.join(lili),
                ' of length ', str(len(lili))))
        for i in range(len(lili)-1, -1, -1):
            if lili[i] < 'z':
                lili[i] = chr(ord(lili[i])+1)
                break
            else:
                lili[i] = 'a'

#------------------------------------------------------------------------
#
# Structure of Table-Memory
#
#------------------------------------------------------------------------

class Tab_Cell():
    def __init__(self, colchar, span, head):
        self.colchar = colchar
        self.span = span
        self.head = head
        self.content = ''
        self.nested_minpg = False
class Tab_Row():
    def __init__(self):
        self.cells =[]
        self.tail = ''
        self.addit = '' # for: \\hline, \\cline{}
        self.spec_var_cell_width = ''
        self.total_width = ''
class Tab_Mem():
    def __init__(self, head):
        self.head = head
        self.tail =''
        self.rows =[]

#------------------------------------------------------------------------
#
# Functions for docbackend
#
#------------------------------------------------------------------------
def latexescape(text):
    """
    change text in text that latex shows correctly
    special characters: \&     \$     \%     \#     \_    \{     \}
    """
    text = text.replace('&','\\&')
    text = text.replace('$','\\$')
    text = text.replace('%','\\%')
    text = text.replace('#','\\#')
    text = text.replace('_','\\_')
    text = text.replace('{','\\{')
    text = text.replace('}','\\}')
    return text

def latexescapeverbatim(text):
    """
    change text in text that latex shows correctly respecting whitespace
    special characters: \&     \$     \%     \#     \_    \{     \}
    Now also make sure space and newline is respected
    """
    text = text.replace('&', '\\&')
    text = text.replace('$', '\\$')
    text = text.replace('%', '\\%')
    text = text.replace('#', '\\#')
    text = text.replace('_', '\\_')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    text = text.replace(' ', '\\ ')
    text = text.replace('\n', '~\\newline\n')
    #spaces at begin are normally ignored, make sure they are not.
    #due to above a space at begin is now \newline\n\
    text = text.replace('\\newline\n\\ ',
                        '\\newline\n\\hspace*{0.1\\grbaseindent}\\ ')
    return text

#------------------------------------------------------------------------
#
# Document Backend class for cairo docs
#
#------------------------------------------------------------------------

class LateXBackend(DocBackend):
    """
    Implementation of docbackend for latex docs.
    File and File format management for latex docs
    """
    # overwrite base class attributes, they become static var of LaTeXDoc
    SUPPORTED_MARKUP = [
            DocBackend.BOLD,
            DocBackend.ITALIC,
            DocBackend.UNDERLINE,
            DocBackend.FONTSIZE,
            DocBackend.FONTFACE,
            DocBackend.SUPERSCRIPT ]

    STYLETAG_MARKUP = {
        DocBackend.BOLD        : ("\\textbf{", "}"),
        DocBackend.ITALIC      : ("\\textit{", "}"),
        DocBackend.UNDERLINE   : ("\\underline{", "}"),
        DocBackend.SUPERSCRIPT : ("\\textsuperscript{", "}"),
    }

    ESCAPE_FUNC = lambda x: latexescape

    def setescape(self, preformatted=False):
        """
        Latex needs two different escape functions depending on the type.
        This function allows to switch the escape function
        """
        if not preformatted:
            LateXBackend.ESCAPE_FUNC = lambda x: latexescape
        else:
            LateXBackend.ESCAPE_FUNC = lambda x: latexescapeverbatim

    def _create_xmltag(self, type, value):
        """
        overwrites the method in DocBackend.
        creates the latex tags needed for non bool style types we support:
            FONTSIZE : use different \large denomination based
                                        on size
                                     : very basic, in mono in the font face
                                        then we use {\ttfamily }
        """
        if type not in self.SUPPORTED_MARKUP:
            return None
        elif type == DocBackend.FONTSIZE:
            #translate size in point to something LaTeX can work with
            fontsize = map_font_size(value)
            if fontsize:
                return ("{\\" + fontsize + ' ', "}")
            else:
                return ("", "")

        elif type == DocBackend.FONTFACE:
            if 'MONO' in value.upper():
                return ("{\\ttfamily ", "}")
            elif 'ROMAN' in value.upper():
                return ("{\\rmfamily ", "}")
        return None

    def _checkfilename(self):
        """
        Check to make sure filename satisfies the standards for this filetype
        """
        if not self._filename.endswith(".tex"):
            self._filename = self._filename + ".tex"


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

#   ---------------------------------------------------------------------
#   some additional variables
#   -------------------------------------------------------------------------
    in_table = False
    spec_var_col = 0
    textmem = []
    in_title = True


#   ---------------------------------------------------------------------
#   begin of table special treatment
#   -------------------------------------------------------------------------
    def emit(self, text, tab_state=CELL_TEXT, span=1):
        """
        Hand over all text but tables to self._backend.write(), (line 1-2).
        In case of tables pass to specal treatment below.
        """
        if not self.in_table: # all stuff but table
            self._backend.write(text)
        else:
            self.handle_table(text, tab_state, span)


    def handle_table(self, text, tab_state, span):
        """
        Collect tables elements in an adequate cell/row/table structure and
        call for LaTeX width calculations and writing out
        """
        if tab_state == CELL_BEG:
            # here text is head
            self.textmem = []
            self.curcol_char = get_charform(self.curcol-1)
            if span > 1: # phantom columns prior to multicolumns
                for col in range(self.curcol - span, self.curcol - 1):
                    col_char = get_charform(col)
                    phantom = Tab_Cell(col_char, 0, '')
                    self.tabrow.cells.append(phantom)
            if not self.tabrow.cells and text.rfind('{|l') != -1:
                self.leftmost_vrule = True
            if (self.leftmost_vrule and
                    self.curcol == self.numcols and
                    text.endswith('l}')):
                text =  text.replace('l}', 'l|}')
            self.tabcell = Tab_Cell(self.curcol_char, span, text)
        elif tab_state == CELL_TEXT:
            self.textmem.append(text)

        elif tab_state == CELL_END: # text == ''
            self.tabcell.content = ''.join(self.textmem)
            if self.tabcell.content.find('\\centering') != -1:
                self.tabcell.content = self.tabcell.content.replace(
                        '\\centering', '')
                self.tabcell.head = re.sub(
                    TBLFMT_PAT, '\\1c\\2', self.tabcell.head)
                self.tabcell.content = self.tabcell.content.replace('\n\n}', '}')
            self.tabrow.cells.append(self.tabcell)
            self.textmem = []
        elif tab_state == ROW_BEG:
            self.tabrow = Tab_Row()
            self.leftmost_vrule  = False
        elif tab_state == ROW_END:
            self.tabrow.tail = ''.join(self.textmem)
            self.tabrow.addit = text # text: \\hline, \\cline{}
            self.tabmem.rows.append(self.tabrow)
        elif tab_state == TAB_BEG: # text: \\begin{longtable}[l]{<tblfmt>}
            self.tabmem = Tab_Mem(text)
        elif tab_state == NESTED_MINPG:
            self.tabcell.nested_minpg = True
            self.tabcell.content.append(text)
        elif tab_state == TAB_END: # text: \\end{longtable}
            self.tabmem.tail = text

            # table completed, calc widths and write out
            self.calc_latex_widths()
            self.write_table()


    def calc_latex_widths(self):
        """
        In tab-cells LaTeX needs fixed width for minipages.
        Evaluations are set up here and passed to LaTeX:
        Calculate needed/usable widths (lengths),
        adjust rows to equal widths (lengths), thus prepared to put something
        like hints as '→ ...' in the FamilySheet at rightmost position.
        ??? Can all this be done exclusively in TeX? Don't know how.
        """
        self._backend.write('\\inittabvars{\\grwidthused}{\\tabcolsep}%\n')
        width_used = ['\\tabcolsep']

        for col_num in range(self.numcols):
            col_char = get_charform(col_num)

            if MINIPAGE_COL < 0:
                self.spec_var_col = self.numcols + MINIPAGE_COL
            else:
                self.spec_var_col = MINIPAGE_COL

            # for all columns but spec_var_col: calculate needed col width
            if col_num == self.spec_var_col:
                continue
            self._backend.write(''.join(('\\inittabvars{\\grcolwidth',
                col_char, '}{0.0em}%\n')))
            for row in self.tabmem.rows:
                cell = row.cells[col_num]
                if cell.span:
                    for part in cell.content.split(PAT_FOR_LINE_BREAK):
                        self._backend.write(''.join(('\\grcalctextwidth{',
                            part, '}{\\grcolwidth', col_char, '}%\n')))
                    row.cells[col_num].content = cell.content.replace(
                            PAT_FOR_LINE_BREAK, '~\\newline %\n')
            self._backend.write(''.join(('\\addtolength{\\grwidthused}{',
                '\\grcolwidth', col_char, '+\\tabcolsep}%\n')))
            self._backend.write(''.join(('\\inittabvars{',
                '\\grwidthusedtill', col_char, '}{ \\grwidthused}%\n')))
            width_used.append('\\grwidthusedtill' + col_char)
        self._backend.write(''.join(('\\inittabvars{\\grwidthavailable}{',
            '\\textwidth-\\grwidthused}%\n')))

        # spec_var_col
        self._backend.write('\\inittabvars{\\grmaxrowwidth}{0.0em}%\n')
        row_alph_counter = str_incr(ROW_COUNT_BASE)
        for row in self.tabmem.rows:
            row_alph_id = row_alph_counter.next()
            row.spec_var_cell_width = ''.join(('\\grcellwidth', row_alph_id))

            cell = row.cells[self.spec_var_col]
            self._backend.write(''.join(('\\inittabvars{',
                row.spec_var_cell_width, '}{0.0em}%\n')))

            lines = cell.content.split(PAT_FOR_LINE_BREAK)
            for part in  lines:
                self._backend.write(''.join(('\\grcalctextwidth{', part, '}{',
                    row.spec_var_cell_width, '}%\n')))
            row.cells[self.spec_var_col].content = '~\\newline %\n'.join(lines)

            # shorten cells too long, calc row-length, search max row width
            self._backend.write('\\inittabvars{\\grspangain}{0.0em}')
            if cell.span > 1:
                self._backend.write(''.join(('\\inittabvars{\\grspangain}{',
                    width_used[self.spec_var_col], '-',
                    width_used[self.spec_var_col - cell.span + 1], '}%\n')))
            self._backend.write(''.join(('\\inittabvars{\\grspecavailable}{',
                '\\grwidthavailable+\\grspangain}%\n')))
            self._backend.write(''.join(('\\grminvaltofirst{',
                row.spec_var_cell_width, '}{\\grspecavailable}%\n')))
            row.total_width = ''.join(('\\grrowwidth', row_alph_id))
            self._backend.write(''.join(('\\inittabvars{', row.total_width,
                '}{\\grwidthused +', row.spec_var_cell_width,
                '-\\grspangain}%\n')))
            self._backend.write(''.join(('\\grmaxvaltofirst{\\grmaxrowwidth}{',
                row.total_width, '}%\n')))

        # widen spec_var cell:
        # (special feature; allows text to be placed at the right border.
        # for later use, doesn't matter here)
        for row in self.tabmem.rows:
            self._backend.write(''.join(('\\grmaxvaltofirst{',
                row.spec_var_cell_width, '}{', row.spec_var_cell_width,
                '+\\grmaxrowwidth-\\grspangain-', row.total_width, '}%\n')))


    def write_table(self):
        # open table with '\\begin{longtable}':
        self._backend.write(''.join(self.tabmem.head))

        # special treatment at begin of longtable for heading and
        # closing at top and bottom of table
        # and parts of it at pagebreak separating
        (separate,
        complete_row) = self.mk_first_row(self.tabmem.rows[FIRST_ROW])
        self._backend.write(separate)
        self._backend.write('\\endhead%\n')
        self._backend.write(separate.replace('raisebox{+1ex}',
            'raisebox{-2ex}'))
        self._backend.write('\\endfoot%\n')
        if self.head_line:
            self._backend.write('\\hline%\n')
            self.head_line= False
        else:
            self._backend.write('%\n')
        self._backend.write(complete_row)
        self._backend.write('\\endfirsthead%\n')
        self._backend.write('\\endlastfoot%\n')

        # now hand over subsequent rows
        for row in self.tabmem.rows[SUBSEQ_ROW:]:
            complete_row = self.mk_subseq_rows(row)
            self._backend.write(complete_row)

        # close table with '\\end{longtable}':
        self._backend.write(''.join(self.tabmem.tail))


    def mk_first_row(self, first_row):
        complete =[]
        separate =[]
        add_vdots = ''
        for cell in first_row.cells:
            if cell.span == 0: # phantom columns prior to multicolumns
                continue
            leading = '{'
            closing = '} & %\n'
            if get_numform(cell.colchar) == self.spec_var_col:
                leading = ''.join(('{\\tabheadstrutceil\\begin{minipage}[t]{',
                    first_row.spec_var_cell_width, '}{'))
                closing = '\\tabheadstrutfloor}\\end{minipage}} & %\n'
            if (not separate and
                get_numform(cell.colchar) == self.numcols - 1):
                add_vdots = ''.join(('\\hspace*{\\fill}\\hspace*{\\fill}',
                                     '\\raisebox{+1ex}{\\vdots}'))
            complete.append(''.join((cell.head, leading,
                cell.content, closing)))
            separate.append(''.join((cell.head, leading,
                '\\hspace*{\\fill}\\raisebox{+1ex}{\\vdots}',
                add_vdots, '\\hspace*{\\fill}', closing)))
        return (''.join((''.join(separate)[:-4], '%\n', first_row.tail)),
                ''.join((''.join(complete)[:-4], '%\n', first_row.tail,
                    first_row.addit)))


    def mk_subseq_rows(self, row):
        complete =[]
        for cell in row.cells:
            if cell.span == 0: # phantom columns prior to multicolumns
                continue
            leading = '{'
            closing = '} & %\n'
            if get_numform(cell.colchar) == self.spec_var_col: # last col
                if cell.nested_minpg:
                    cell.content.replace('\\begin{minipage}{\\grminpgwidth}',
                            ''.join(('\\begin{minipage}{0.8',
                                     row.spec_var_cell_width, '}')))
                leading = ''.join(('{\\tabrowstrutceil\\begin{minipage}[t]{',
                    row.spec_var_cell_width, '}{'))
                closing = '}\\end{minipage}} & %\n'
            complete.append(''.join((cell.head, leading,
                cell.content, closing)))
        return ''.join((''.join(complete)[:-4], '%\n', row.tail, row.addit))

#       ---------------------------------------------------------------------
#       end of special table treatment
#       ---------------------------------------------------------------------


    def page_break(self):
        "Forces a page break, creating a new page"
        self.emit('\\newpage%\n')

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
        paper_name = self.paper.get_size().get_name().lower()
        if paper_name in ["a4", "a5", "legal", "letter"]:
            options += ',' + paper_name + 'paper'

        # Use the article template, T1 font encodings, and specify
        # that we should use Latin1 and unicode character encodings.
        self.emit(_LATEX_TEMPLATE_1 % options)
        self.emit(_LATEX_TEMPLATE)

        self.in_list = False
        self.in_table = False
        self.head_line = False
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
                thisstyle.font_beg += "{\\centering"
                thisstyle.font_end = ''.join(("\n\n}", thisstyle.font_end))
            elif align == "right":
                thisstyle.font_beg += "\\hfill"

            # Establish font face and shape
            if font.get_type_face() == FONT_SANS_SERIF:
                thisstyle.font_beg += "\\sffamily"
                thisstyle.font_end = "\\rmfamily" + thisstyle.font_end
            if font.get_bold():
                thisstyle.font_beg += "\\bfseries"
                thisstyle.font_end = "\\mdseries" + thisstyle.font_end
            if font.get_italic() or font.get_underline():
                thisstyle.font_beg += "\\itshape"
                thisstyle.font_end = "\\upshape" + thisstyle.font_end

            # Now determine font size
            fontsize = map_font_size(size)
            if fontsize:
                thisstyle.font_beg += "\\" + fontsize
                thisstyle.font_end += "\\normalsize"

            thisstyle.font_beg += " "
            thisstyle.font_end += " "

            left  = style.get_left_margin()
            first = style.get_first_indent() + left
            thisstyle.leftIndent = left
            thisstyle.firstLineIndent = first
            self.latexstyle[style_name] = thisstyle

    def close(self):
        """Clean up and close the document"""
        if self.in_list:
            self.emit('\\end{list}\n')
        self.emit('\\end{document}\n')
        self._backend.close()

    def end_page(self):
        """Issue a new page command"""
        self.emit('\\newpage')

    def start_paragraph(self, style_name, leader=None):
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
        if self.indent == 0:
            self.indent = self.FLindent

        # For additional vertical space beneath title line(s)
        # i.e. when the first centering ended:
        if self.in_title and ltxstyle.font_beg.find('centering') == -1:
            self.in_title = False
            self._backend.write('\\vspace{5ex}%\n')

        self._backend.write('\\inittabvars{\\grleadinglabelwidth}{0.0em}%\n')
        if leader:
            self._backend.write(''.join((
                '\\grcalctextwidth{', leader, '}{\\grleadinglabelwidth}%\n')))
            self._backend.write(
                '\\inittabvars{\\grlistbacksp}{\\grleadinglabelwidth +1em}%\n')
        else:
            self._backend.write(
                '\\inittabvars{\\grlistbacksp}{0em}%\n')

#       -------------------------------------------------------------------
        #   Gramps presumes 'cm' as units; here '\\grbaseindent' is used
        #   as equivalent, set in '_LATEX_TEMPLATE' above to '3em';
        #   there another value might be choosen.
#       -------------------------------------------------------------------
        if self.indent is not None and not self.in_table:
            self.emit(''.join(('\\inittabvars{'
                '\\grminpgindent}{%s\\grbaseindent-\\grlistbacksp}' %
                repr(self.indent), '%\n\\hspace*{\\grminpgindent}%\n',
                '\\begin{minipage}[t]{\\textwidth-\\grminpgindent}',
                '%\n')))
            self.fix_indent = True

            if leader is not None and not self.in_list:
                self.in_list = True
                self._backend.write(''.join(('\\begin{list}{%\n', leader,
                '}{%\n', '\\labelsep0.5em %\n',
                '\\setlength{\\labelwidth}{\\grleadinglabelwidth}%\n',
                '\\setlength{\\leftmargin}{\\grlistbacksp}}%\n',
                '\\item%\n')))


        if leader is None:
            self.emit('\n')
            self.emit('%s ' % self.fbeg)

    def end_paragraph(self):
        """End the current paragraph"""
        newline = '%\n\n'
        if self.in_list:
            self.in_list = False
            self.emit('\n\\end{list}\n')
            newline = ''
        elif self.in_table:
            newline = ''

        self.emit('%s%s' % (self.fend, newline))
        if self.fix_indent:
            self.emit('\\end{minipage}\\parindent0em%\n\n')
            self.fix_indent = False

    def start_bold(self):
        """Bold face"""
        self.emit('\\textbf{')

    def end_bold(self):
        """End bold face"""
        self.emit('}')

    def start_superscript(self):
        self.emit('\\textsuperscript{')

    def end_superscript(self):
        self.emit('}')

    def start_table(self, name,style_name):
        """Begin new table"""
        self.in_table = True
        self.currow = 0

        # We need to know a priori how many columns are in this table
        styles = self.get_style_sheet()
        self.tblstyle = styles.get_table_style(style_name)
        self.numcols = self.tblstyle.get_columns()

        # early test of column count:
        z = get_charform(self.numcols-1)

        tblfmt = '*{%d}{l}' % self.numcols
        self.emit(
            '\\begin{longtable}[l]{%s}\n' % (tblfmt), TAB_BEG)

    def end_table(self):
        """Close the table environment"""
        # Create a paragraph separation below the table.
        self.emit(
                '%\n\\end{longtable}%\n\\par%\n', TAB_END)
        self.in_table = False

    def start_row(self):
        """Begin a new row"""
        self.emit('', ROW_BEG)
        # doline/skipfirst are flags for adding hor. rules
        self.doline = False
        self.skipfirst = False
        self.curcol = 0
        self.currow = self.currow + 1

    def end_row(self):
        """End the row (new line)"""
        self.emit('\\\\ ')
        if self.doline:
            if self.skipfirst:
                self.emit(''.join((('\\cline{2-%d}' %
                    self.numcols), '%\n')), ROW_END)
            else:
                self.emit('\\hline %\n', ROW_END)
        else:
            self.emit('%\n', ROW_END)
        self.emit('%\n')

    def start_cell(self,style_name,span=1):
        """Add an entry to the table.
        We always place our data inside braces
        for safety of formatting."""
        self.colspan = span
        self.curcol = self.curcol + self.colspan

        styles = self.get_style_sheet()
        self.cstyle = styles.get_cell_style(style_name)

#       ------------------------------------------------------------------
#         begin special modification for boolean values
        # values imported here are used for test '==1' and '!=0'. To get
        # local boolean values the tests are now transfered to the import lines
#       ------------------------------------------------------------------
        self.lborder = 1 == self.cstyle.get_left_border()
        self.rborder = 1 == self.cstyle.get_right_border()
        self.bborder = 1 == self.cstyle.get_bottom_border()
        self.tborder = 0 != self.cstyle.get_top_border()

        # self.llist not needed, LaTeX has to decide on its own
        # wether a line fits or not. See comment in calc_latex_widths() above.
        # self.llist = 1 == self.cstyle.get_longlist()

        cellfmt = "l"
        # Account for vertical rules
        if self.lborder:
            cellfmt = '|' + cellfmt
        if self.rborder:
            cellfmt = cellfmt + '|'

        # and Horizontal rules
        if self.bborder:
            self.doline = True
        elif self.curcol == 1:
            self.skipfirst = True
        if self.tborder:
            self.head_line = True
#       ------------------------------------------------------------------
#         end special modification for boolean values
#       ------------------------------------------------------------------

        self.emit(
            ''.join(('%\n', '\\multicolumn{%d}{%s}' % (span, cellfmt))),
            CELL_BEG, span)


    def end_cell(self):
        """Prepares for next cell"""
        self.emit('', CELL_END)


    def add_media_object(self, name, pos, x, y, alt=''):
        """Add photo to report"""
        return

        try:
            pic = ImgManip.ImgManip(name)
        except:
            return

        self.imagenum = self.imagenum + 1
        picf = self.filename[:-4] + '_img' + str(self.imagenum) + '.eps'
        pic.eps_convert(picf)

#       -------------------------------------------------------------------
        # x and y will be maximum width OR height in units of cm
        #   here '\\grbaseindent' is used as equivalent, see above
#       -------------------------------------------------------------------
        mysize = ''.join(('width=%d\\grbaseindent, ', 
                         'height=%d\\grbaseindent,keepaspectratio' % (x,y)))
        if pos == "right":
            self.emit((
                '\\hfill\\includegraphics[%s]{%s}\n' % (mysize,picf)))
        elif pos == "left":
            self.emit((
                '\\includegraphics[%s]{%s}\\hfill\n' % (mysize,picf)))
        else:
            self.emit((
                '\\centering{\\includegraphics[%s]{%s}}\n' % (mysize,picf)))

    def write_text(self, text, mark=None):
        """Write the text to the file"""
        if text == '\n':
            text = ''
        text = latexescape(text)
        #hard coded replace of the underline used for missing names/data
        text = text.replace('\\_'*13, '\\underline{\hspace{3\\grbaseindent}}')
        self.emit(text + ' ')

    def write_styled_note(self, styledtext, format, style_name,
                          contains_html=False):
        """
        Convenience function to write a styledtext to the latex doc.
        styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        contains_html: bool, the backend should not check if html is present.
            If contains_html=True, then the textdoc is free to handle that in
            some way. Eg, a textdoc could remove all tags, or could make sure
            a link is clickable. self ignores notes that contain html
        """
        if contains_html:
            return
        text = str(styledtext)

        s_tags = styledtext.get_tags()
        if format:
            #preformatted, use different escape function
            self._backend.setescape(True)

        markuptext = self._backend.add_markup_from_styled(text, s_tags)

        #there is a problem if we write out a note in a table. No newline is
        # possible, the note runs over the margin into infinity.
        # A good solution for this ???
        # A quick solution: create a minipage for the note and add that always
        #   hoping that the user will have left sufficient room for the page
        #
        # now solved by postprocessing in emit()
        # by explicitely calculating column widths
        #
        if format:
            self.start_paragraph(style_name)
            self.emit(markuptext)
            self.end_paragraph()
            #preformatted finished, go back to normal escape function
            self._backend.setescape(False)
        else:
            for line in markuptext.split('%\n%\n'):
                self.start_paragraph(style_name)
                for realline in line.split('\n'):
                    self.emit(realline)
                    self.emit("~\\newline%\n")
                self.end_paragraph()

    def write_endnotes_ref(self, text, style_name):
        """
        Overwrite base method for lines of endnotes references
        """
        self.emit("\\begin{minipage}{\\grminpgwidth}\n",
                NESTED_MINPG)
        for line in text.split('\n'):
            self.start_paragraph(style_name)
            self.write_text(line)
            self.end_paragraph()
        self.emit(
                "%\n\\vspace*{0.5\\grbaseindent}%\n\\end{minipage}%\n\n")

