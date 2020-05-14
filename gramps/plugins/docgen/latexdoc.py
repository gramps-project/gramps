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
# Copyright (C) 2011       Adam Stein <adam@csh.rit.edu>
#               2011-2012  Harald Rosemann
#               2019_2020  Harald Rosemann
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""LaTeX document generator"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from bisect import bisect
import re
import os.path
import logging
import csv

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

#----------------------------------------------------------------------- -
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug.docgen import (BaseDoc, TextDoc, PAPER_LANDSCAPE,
                                    FONT_SANS_SERIF, URL_PATTERN)
from gramps.gen.plug.docbackend import DocBackend
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

_LOG = logging.getLogger(".latexdoc")

_CLICKABLE = r'\url{\1}'

#------------------------------------------------------------------------
#
# Special settings for LaTeX output
#
#------------------------------------------------------------------------
#   For an interim mark e.g. for an intended linebreak I use a special pattern.
#   It shouldn't interfere with normal text. In LaTeX character '&' is used
#   for column separation in tables and may occur there in series. The pattern
#   is used here before column separation is set. On the other hand incoming
#   text can't show this pattern for it would have been replaced by '\&\&'.
#   So the choosen pattern will do the job without confusion:

SEPARATION_PAT = '&&'

#------------------------------------------------------------------------
#
# LaTeX Article Template
#
#------------------------------------------------------------------------

_LATEX_TEMPLATE_1 = r'\documentclass[%s]{article}'
_LATEX_TEMPLATE = r'''%
%
%	new version: xelatex must be used instead of the previous recommended pdflatex:
%		xelatex <file-name>.tex
%	due to the usage of unicode utf8 consistently. In some cases several consecutive
%	calls are required; xelatex will prompt  'Rerun LaTeX'.
%
\usepackage{graphicx}% Extended graphics support
\usepackage{longtable}% For multi-page tables
\usepackage{calc}% For some calculations
\usepackage{ifthen}% For table width calculations
\usepackage{ragged2e}% For left aligning
\usepackage{needspace}% For smart pagebreaking
%
\usepackage{xeCJK}%
\usepackage{polyglossia}%
\usepackage{xltxtra}%
%
% posible choices tested with ubuntu 
%\setmainfont[Mapping=tex-text]{Linux Libertine O}%
%\setmainfont[Mapping=tex-text]{Ubuntu Condensed}%
%\setmainfont[Mapping=tex-text]{Latin Modern Roman}%
%
% not tested; perhaps Font names must be adapted
%\setmainfont[Mapping=tex-text]{Times New Roman}%
%\setmainfont[Mapping=tex-text]{Courier New}%
%\setmainfont[Mapping=tex-text]{Arial}%
\setmainlanguage{english}%
%
%
% adjustment of margins, you may choose a suitable one
\addtolength{\topmargin}{-1.0in}%
\addtolength{\textwidth}{1.0in}%
%\addtolength{\textwidth}{1.2in}%
%\addtolength{\textwidth}{1.5in}%
%\addtolength{\textheight}{0.5in}%
\addtolength{\textheight}{1.5in}%
\addtolength{\footskip}{0.2in}%
% \addtolength{\oddsidemargin}{-0.6in}%
\addtolength{\oddsidemargin}{-0.3in}%
% \addtolength{\evensidemargin}{-0.6in}%
\addtolength{\evensidemargin}{-0.3in}%
%
%
% Vertical spacing between LaTeX-paragraphs:
% take one of three possibilities or modify to your taste:
\setlength{\parskip}{1.0ex plus0.2ex minus0.2ex}%
%\setlength{\parskip}{1.5ex plus0.3ex minus0.3ex}%
%\setlength{\parskip}{2.0ex plus0.4ex minus0.4ex}%
%
% Factor for vertical spacing between lines:
% take one of four possibilities or modify to your taste:
%\renewcommand{\baselinestretch}{0.90}%
\renewcommand{\baselinestretch}{1.0}%
%\renewcommand{\baselinestretch}{1.2}%
%\renewcommand{\baselinestretch}{1.5}%
%
% Indentation; substitute for '1cm' of gramps,
% 2.85em is nearly exact for 12pt; I choosed 2.6
% !!! will be halved for descendants report !!!
% take one of the possibilities or modify to your taste:
\newlength{\grbaseindent}%
%\setlength{\grbaseindent}{3.0em}%
%\setlength{\grbaseindent}{2.85em}%
\setlength{\grbaseindent}{2.6em}%
%\setlength{\grbaseindent}{2.5em}%
%\setlength{\grbaseindent}{2.0em}%
%
%----------------------------------------------------
% standard adjustments in layout
%----------------------------------------------------
%
% raggedright for slim table columns, justification for broader ones:
\newlength{\grthresholdmarginalign}%
\setlength{\grthresholdmarginalign}{0.4\textwidth}%
%
% general page breaking settings
\raggedbottom%
\clubpenalty10000%
\widowpenalty10000%
\displaywidowpenalty10000%
%
% invisible struts for fine tuning of vertical distances
\newcommand{\grupstrut}[1]{%
  \rule[0em]{0em}{0.7\baselineskip+#1}}%
\newcommand{\grdownstrut}[1]{%
  \rule[-0.2\baselineskip-#1]{0em}{0.2\baselineskip-#1}}%
%
%
%
% ----------------------------------------------------
% New lengths, counters and commands for calculations 
% ----------------------------------------------------
%
\newlength{\grtabtextwd}%
\newlength{\grtempwd}%
\newlength{\grtabindent}%
\newlength{\grfreespace}%
\newlength{\grspanwidth}%
\newlength{\grleadlabelwidth}%
\newlength{\grparagrindent}%
\newlength{\grlistbacksp}%
\newlength{\grdeltwd}%
\newlength{\grbirthdaylineup}%
\setlength{\grbirthdaylineup}{\baselineskip+1\parskip}%
%
\newcounter{grnumbmajcolsnew}%
\newcounter{grnumbmajcolsold}%
%
%
\newcommand{\grinitlength}[2]{%
  \ifthenelse{\isundefined{#1}}%
    {\newlength{#1}}{}%
  \setlength{#1}{#2}%
}%
%
\newcommand{\grpresettab}[2]{%%
  \setlength{\grtabindent}{#2\grbaseindent}%
  \setlength{\grtabtextwd}{\textwidth-\grtabindent}%
  \setlength{\grfreespace}{\grtabtextwd}%
  \setcounter{grnumbmajcolsnew}{#1}%
  \setlength{\grtempwd}{0em}%
}%
%
\newcommand{\grinittab}[2]{%
  \settowidth{\grtempwd}{ }%
  \setlength{\LTleft}{\grtabindent-\grtempwd}%
  \setlength{\LTright}{\fill}%
  \vspace{#1}%
  \begin{longtable}{#2}%
}%
%
\newcommand{\grclosetab}[1]{%
  \end{longtable}%
  \vspace{#1}%
}%
%
\newcommand{\grwidthofpict}[2]{%%
  \setlength{\grtempwd}{#1+2\tabcolsep}%
  \grinitlength{#2}{\maxof{#2}{\grtempwd+2\tabcolsep}}%
}%
%
\newcommand{\grwidthoftext}[2]{%
  \settowidth{\grtempwd}{#1}%
  \grinitlength{#2}{\maxof{#2}{\grtempwd+2\tabcolsep}}%
}%
%
\newcommand{\grprepcolswidthfix}{%
  \ifthenelse{\value{grnumbmajcolsnew} > 0}%
    {  \setlength{\grdeltwd}{\grfreespace*\ratio{1pt}{\value{grnumbmajcolsnew}pt}}%
       \setcounter{grnumbmajcolsold}{\value{grnumbmajcolsnew}}%
       \setcounter{grnumbmajcolsnew}{0}%
       \setlength{\grfreespace}{0.0em}%
    }{}%
}%
%
\newcommand{\grcolswidthfix}[2]{%
   \ifthenelse{\value{grnumbmajcolsold} > 0 %
            \AND \lengthtest{#2 > #1}}%
     {  \addtolength{#1}{\grdeltwd}%
        \ifthenelse{\lengthtest{#1 > #2}}%
          {  \addtolength{\grfreespace}{#1-#2}%
             \setlength{#1}{#2}%
          }{ \stepcounter{grnumbmajcolsnew}%
          }%
     }{}%
}%
%
\newcommand{\grlisthead}[2]{%
  \needspace{#1\baselineskip}%
  \begin{list}{#2}%
    { \setlength{\labelsep}{0.5em}%
      \setlength{\labelwidth}{\grleadlabelwidth}%
      \setlength{\leftmargin}{\grlistbacksp}%
    }\item%
}%
%
\newcommand{\grlisttail}{%
  \end{list}%
}%
%
\newcommand{\grparagrhead}[4]{%
  \vspace{#1}%%
  \setlength{\grparagrindent}{#2\grbaseindent-\grlistbacksp}%
  \needspace{#3\baselineskip}%
  \begin{list}{}{%
    \topsep0ex%
    \partopsep0ex%
    \leftmargin\grparagrindent%
    \rightmargin0em%
    \listparindent0em%
    }#4\item%
}%
%
\newcommand{\grparagrtail}[1]{%
  \end{list}%
  \vspace{#1}%
}%
%
\newcommand{\grordinalshead}[1]{%
  \makebox[2em][r]{#1~~}%
  \parbox[t]{\textwidth-2em}{%
}%
%
\newcommand{\grordinalstail}{%
  }%
}%
%
\newcommand{\grempty}[1]{}%
%
\newcommand{\graddvdots}[1]{%
  \hspace*{\fill}\hspace*{\fill}\raisebox{#1}{\vdots}%
}%
%
\newcommand{\grtabpgbreak}[4]{%
  #1 { \parbox[t]{ #2 - 2\tabcolsep}{\hspace*{\fill}%
  \raisebox{#4}{\vdots} #3{#4} \hspace*{\fill}}}%
}%
%
\newcommand{\grcolpart}[5]{%
  #1{ \ifthenelse{\lengthtest{#2 < \grthresholdmarginalign}}%
        {\RaggedRight}{}%
      \parbox[#3]{#2 - 1.0\tabcolsep}%
        {\grupstrut{#4}#5}%
    }%
}%
%
\newcommand{\grprepleader}[1]{%
  \settowidth{\grtempwd}{#1}%
  \ifthenelse{\lengthtest{\grtempwd > \grleadlabelwidth}}%
    { \setlength{\grleadlabelwidth}{\grtempwd}}{}%
  \setlength{\grlistbacksp}{\grleadlabelwidth + 1.0em}%
}%
%
\newcommand{\grprepnoleader}{%
  \setlength{\grleadlabelwidth}{0em}%
  \setlength{\grlistbacksp}{0em}%
}%
%
\newcommand{\grindivipict}[2]{% #1: pict, #2: caption
  \grcolpart%
    {\multicolumn{1}{c}}%
    {\grcolwidthc}%%
    {t}{1.0ex}%
    {\vspace{-\baselineskip}%
      \centering #1#2%
    }%
}%
%
\newcommand{\grmkpicture}[4]{%
  \ifthenelse{\equal{#1}{Error\_!}}%
    { \vspace{-1.5\baselineskip}%
      \begin{center}%
        \fbox%
          { \rule{0.0em}{#2\grbaseindent}%
            \parbox[b]{#3\grbaseindent}%
              { #1~\\[5.0ex]%
                #4%
              }%
          }%
      \end{center}%
    }%
    { \begin{center}%
        \vspace*{-1.0\baselineskip}%
        \parbox[#4]{#2\grbaseindent}%
          { \fbox%
            {\includegraphics%%
                [ width= #2\grbaseindent,%
                  height= #3\grbaseindent,%
                  keepaspectratio%
                ]%
              {#1}%
            }%
          }\\%
      \end{center}%
    }%
}%
%
%
\begin{document}%
'''


#------------------------------------------------------------------------
#
# Font size table and function
#
#------------------------------------------------------------------------

# These tables correlate font sizes to LaTeX.  The first table contains
# typical font sizes in points.  The second table contains the standard
# LaTeX font size names. Since we use bisect to map the first table to the
# second, we are guaranteed that any font less than 6 points is 'tiny', fonts
# from 6-7 points are 'script', etc. and fonts greater than or equal to 22
# are considered 'Huge'.  Note that fonts from 12-13 points are not given a
# LaTeX font size name but are considered "normal."

_FONT_SIZES = [6, 8, 10, 12, 14, 16, 18, 20, 22]
_FONT_NAMES = ['tiny', 'scriptsize', 'footnotesize', 'small', '',
               'large', 'Large', 'LARGE', 'huge', 'Huge']

def map_font_size(fontsize):
    """ Map font size in points to LaTeX font size """
    return _FONT_NAMES[bisect(_FONT_SIZES, fontsize)]


#------------------------------------------------------------------------
#
# auxiliaries to facilitate table construction
#
#------------------------------------------------------------------------

# patterns for regular expressions
TBLFMT_PAT = re.compile(r'({\|?)l(\|?})')
DIGIT_PAT = re.compile(r'\d+')
FLOAT_PAT = re.compile(r'[-+]?\d+\.\d+')
ORDINAL_PAT = re.compile(r'\d+\. *')
STYLE_DETAIL = re.compile(r'\A[^-]+-([^\d]*)(\d*)([^\d]*)\Z')
STYLE_PARTS = re.compile(r'([^-]*)-(\D+)[\d]*')
HASH_STRIP = re.compile(r' *#.*\Z')

HI_STRUT, LO_STRUT, HI_SPACE, LO_SPACE = range(4)
FIRST_ROW, SUBSEQ_ROW = list(range(2))

# kind_of_picture:
UNKNOWN, INDIVID_PICT, IN_GALLERY = list(range(3))

# endings of table rows
NORMAL_END = r'\\'
NO_PAGE_BREAK = r'\\*'

# Dictionary for transliteration and/or supplying hyphenation patterns. Mapping to be
# loaded in method LaTeXDoc.open(), to be used in global function latexescape(text)
gramps_to_latex = {}


def get_charform(col_num):
    """ Transfer column number to column charakter,
        limited to letters within Station a-z  (26, there is no need for more).
        early test of column count in start_table()
    """
    if col_num > ord('z') - ord('a'):
        raise ValueError(''.join((
            '\n number of table columns is ', repr(col_num),
            '\n                     should be <= ', repr(ord('z') - ord('a')))))
    return chr(ord('a') + col_num)

def get_numform(col_char):
    """ Transfer column charakter to column number,
        reverse to get_charform() above
    """
    return ord(col_char) - ord('a')


#------------------------------------------
MULTCOL_COUNT_BASE = 'aaa'
#   'aaa' is sufficient for up to 17576 multicolumns in each table;
#   do you need more?  Then put another a in as shown in next line
# MULTCOL_COUNT_BASE = 'aaaa'
#------------------------------------------

def str_incr(str_counter):
    """ For counting table rows:
        row_alph_counter = str_incr(MULTCOL_COUNT_BASE)
    """
    lili = list(str_counter)
    while 1:
        yield ''.join(lili)
        if ''.join(lili) == len(lili)*'z':
            raise ValueError(''.join((
                '\n can\'t increment string ', ''.join(lili),
                ' of length10 ', str(len(lili)))))
        for i in range(len(lili)-1, -1, -1):
            if lili[i] < 'z':
                lili[i] = chr(ord(lili[i])+1)
                break
            else:
                lili[i] = 'a'

#------------------------------------------------------------------------
#
# LaTeX Table-Memory and related methods
#
#------------------------------------------------------------------------

class TabCell:
    """" cell of a row of a table """
    def __init__(self, colchar, span, head, content):
        self.colchar = colchar
        self.span = span
        self.head = head
        self.content = content

    def close(self, text):
        self.content = text
        if self.content.find('\\centering') != -1:
            self.content = self.content.replace(
                '\\centering', '')
            self.head = re.sub(
                TBLFMT_PAT, '\\1c\\2', self.head)

class TabRow:
    """" row of a table """
    def __init__(self):
        self.cells = []
        self.tail = NORMAL_END
        self.addit = '' # for: \\hline, \\cline{}, empty row

    def add_cell(self, cell):
        self.cells.append(cell)

    def put_addit(self, text):
        self.addit = ''.join((self.addit, text))

    def get_addit(self):
        return self.addit

    def put_tail(self, tail):
        self.tail = tail

    def get_tail(self):
        return self.tail

class TabMem:
    """" table to be built by consecutive rows of consecutive cells """
    def __init__(self, v_space, tblfmt):
        self.head = ''.join(('\\grinittab{', v_space, '}{', tblfmt, '}%\n'))
        self.tail = ''
        self.rows = []

    def add_row(self, row):
        self.rows.append(row)

    def close(self, kind_of_pict, numcols, v_space):
        """ Transfer of data to table completed;
            close and organize gallery """
        self.tail = ''.join(('%\n\\grclosetab{', v_space, '}%\n'))

        if kind_of_pict == IN_GALLERY:
            for row_id, rrow in enumerate(self.rows):
                if rrow.cells[0].content.startswith('\\grmkpicture'):
                    rrow.put_tail(NO_PAGE_BREAK + '[-3.0ex]')
                    self.rows[row_id-1].put_tail(NO_PAGE_BREAK)
                    if row_id - numcols > 0:
                        self.rows[row_id-2].put_tail(NORMAL_END)
                    for ccell in self.rows[row_id-1].cells:
                        ccell.content = ''.join(('\\centering{', ccell.content, '}%\n'))
                    self.rows.insert(row_id, self.rows.pop(row_id-1))

    def purge_last_row(self):
        del self.rows[-1]

#------------------------------------------------------------------------
#
# Functions for docbackend
#
#------------------------------------------------------------------------

def mapping_to_latex(filename, mapping):
    """ reads mapping from gramps terms to LaTeX terms,
        and/or hyphenation patterns
        or initializes the mapping file
    """
    parts = os.path.split(filename)
    mapping_file = os.path.join(parts[0], 'mapping.csv')
    if os.path.exists(mapping_file):
        with open(mapping_file, newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                if line == []:
                    return
                cleared = [HASH_STRIP.sub('', cont) for cont in line]
                if cleared[0] != '':
                    mapping[cleared[0]] = cleared[1]
        return
    with open(mapping_file, 'w') as csv_file:
        csv_write = csv.writer(csv_file)
        csv_write.writerow([r'# From # on',      r'up to the end of each field: purged'])
        csv_write.writerow([r'# First field',    r'empty: line is ignored'])
        csv_write.writerow([r'# professionally', r'pro\-fessionally # may hyph. at \-'])
        csv_write.writerow([r'# professionally', r'\hyphenation{pro-fessionally} # new way'])
        csv_write.writerow([r'# professionally', r'\-professionally # no hyphenation'])
        csv_write.writerow([r'# 東京駅',         r'Tokyo Station # transcription'])
    return

def latexescape(text):
    """ Escape the following special characters: & $ % # _ { } """
    text = text.replace('&', '\\&')
    text = text.replace('$', '\\$')
    text = text.replace('%', '\\%')
    text = text.replace('#', '\\#')
    text = text.replace('_', '\\_')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')

   # apply mapping and/or special hyphenation to LaTeX
    for gr_term, la_term in gramps_to_latex.items():
        text = text.replace(gr_term, la_term)
    return text

def latexescapeverbatim(text):
    """ Escape special characters and also make sure that LaTeX
        respects whitespace and newlines correctly.
    """
    text = latexescape(text)
    text = text.replace(' ', '~\\-')
    text = text.replace('\n', '~\\newline%\n')
    return text

#------------------------------------------------------------------------
#
# Document Backend class for cairo docs
#
#------------------------------------------------------------------------

class LaTeXBackend(DocBackend):
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
        DocBackend.SUPERSCRIPT]

    STYLETAG_MARKUP = {
        DocBackend.BOLD        : ("\\textbf{", "}"),
        DocBackend.ITALIC      : ("\\textit{", "}"),
        DocBackend.UNDERLINE   : ("\\underline{", "}"),
        DocBackend.SUPERSCRIPT : ("\\textsuperscript{", "}"),
    }

    ESCAPE_FUNC = lambda x: latexescape

    def setescape(self, preformatted=False):
        """
        LaTeX needs two different escape functions depending on the type.
        This function allows to switch the escape function
        """
        if not preformatted:
            LaTeXBackend.ESCAPE_FUNC = lambda x: latexescape

        else:
            LaTeXBackend.ESCAPE_FUNC = lambda x: latexescapeverbatim

    def _create_xmltag(self, doc_type, value):
        #   parameter name: 'type' is reserved, changed to doc_type
        r"""
        overwrites the method in DocBackend.
        creates the latex tags needed for non bool style types we support:
            FONTSIZE : use different \large denomination based on size
                                     : very basic, in mono in the font face
                                        then we use {\ttfamily }
        """
        if doc_type not in self.SUPPORTED_MARKUP:
            return None
        elif doc_type == DocBackend.FONTSIZE:
            # translate size in point to something LaTeX can work with
            fontsize = map_font_size(value)
            if fontsize:
                return ("{\\" + fontsize + ' ', "}")
            else:
                return ("", "")

        elif doc_type == DocBackend.FONTFACE:
            if 'MONO' in value.upper():
                return ("{\\ttfamily ", "}")
            elif 'ROMAN' in value.upper():
                return ("{\\rmfamily ", "}")
        return None

    def _checkfilename(self):
        """
        Check to make sure filename satisfies the standards for %this filetype
        """

        if not self._filename.endswith(".tex"):
            self._filename = self._filename + ".tex"

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
            self.left_indent = style.left_indent
            self.first_line_indent = style.first_line_indent
        else:
            self.font_beg = ""
            self.font_end = ""
            self.left_indent = ""
            self.first_line_indent = ""

#-------------------------------------------------------------------------
#
# Vertical fine tuning, data and methods bound together to be included by LaTeXDoc
#
#-------------------------------------------------------------------------

class VerticalFineTuning:
    """ Specific adjustments yielding an appealing appearence in pdf"""
    tail_vals = list(range(4))
    tail_vals[HI_STRUT] = {'First-Entry': '1.0', 'Generation': '2.5', 'Entry': '0.5',
                           'ChildList': '0.8', 'ChildTitle': '1.5',
                           'ChildText': '2.0', 'MoreHeader': '1.5',
                           'NoteHeader': '1.5', 'ParentName': '2.0', 'PlaceTitle': '2.5',
                           'Section': '0.5'}
    tail_vals[LO_STRUT] = {'ParentName': '0.5', 'PlaceTitle': '1.0', 'Pedigree': '2.0'}
    tail_vals[HI_SPACE] = {'Heading': '2.0', 'Level': '-0.8', 'Spouse': '-1.0',
                           'PlaceDetails': '-1.0', 'PlaceTitle': '1.5', 'Section': '0.5',
                           'Monthstyle': '3.0'}
    tail_vals[LO_SPACE] = {'First-Entry': '-1.0', 'ChildTitle': '-1.0', 'Title': '3.0',
                           'ReportTitle': '3.0', 'blank': '-1.2', 'Section': '1.0',
                           'Datastyle': '-\\parskip', 'Daystyle': '-\grbirthdaylineup',
                           'instead_of_pg_break': '2.9'}

    cmpl_vals = list(range(4))
    cmpl_vals[HI_STRUT] = {}
    cmpl_vals[LO_STRUT] = {}
    cmpl_vals[HI_SPACE] = {'EOL': '1.0',  # short for:   endofline_report,
                           'IDS': '1.0', 'Not': '1.0', # indiv_complete, notelinkreport
                           'PCL': '1.0', 'TR-': '1.0', # place_report, tag_report
                           'KIN-Normal': '-1.0', 'KIN-Subtitle': '1.5',
                           'first_page_top': '3.0', 'before_tab': '-2.5'}
    cmpl_vals[LO_SPACE] = {'behind_tab': '-2.5', 'REC-Normal': '-1.0',
                           'TR-Heading': '2\\parskip', 'KIN-Subtitle': '0.5',
                           'REC-Subtitle': '2.0', 'EOL-Subtitle': '2.0'}

    in_front = ['\\grupstrut{', '\\grdownstrut{']
    vacant = ['', '', '0ex', '0ex']

    def decorate(self, what, vert_val):
        """ Complete number to strut or measure """
        if re.fullmatch(FLOAT_PAT, vert_val):
            if what in [HI_STRUT, LO_STRUT]:
                return ''.join((self.in_front[what], vert_val, 'ex}'))
            return ''.join((vert_val, 'ex'))
        return vert_val

    def get_v_adjust(self, what, style_name):
        """ Deliver special adjustments as strut or measure """
        style_tail = re.sub(STYLE_DETAIL, r'\1\3', style_name)
        if style_tail in self.tail_vals[what].keys():
            return self.decorate(what, self.tail_vals[what][style_tail])
        if style_name in self.cmpl_vals[what].keys():
            return self.decorate(what, self.cmpl_vals[what][style_name])
        return self.vacant[what]

#------------------------------------------------------------------
#
# LaTeXDoc
#
#------------------------------------------------------------------

class LaTeXDoc(BaseDoc, TextDoc, VerticalFineTuning):
    """LaTeX document interface class. Derived from BaseDoc"""

#   ---------------------------------------------------------------
#   some additional variables
#   ---------------------------------------------------------------
    in_table = False
    curr_tab_style = ''
    row_start = False
    stick_next = 0
    keep_text_style = ''
    kind_of_pict = UNKNOWN
    textmem = []

    #   for fine tuning of vertical distances
    space_above_paragr = '0ex'
    space_below_paragr = '0ex'
    curr_style_name = '00-00'

#   ---------------------------------------------------------------
#   begin of table special treatment
#   ---------------------------------------------------------------
    def emit(self, text):
        """
        Hand over all text but tables and birthday-record lines to self._backend.write()
        In case of tables pass to specal treatment below.
        _    gramps serves tables column by column
        _    whereas LaTeX builds them row by row.
        """
        if self.in_table: # all stuff but table
            if text.startswith('\\grmkpicture'):
                text = ''.join(('\\centering', text))
                if len(self.tabmem.rows) == 1:
                    #        individual picture in 1. chunk of individual report
                    self.kind_of_pict = INDIVID_PICT
                else:    #    picture in gallery of individual report
                    self.kind_of_pict = IN_GALLERY
            self.textmem.append(text)
            return
        if (self.curr_style_name == 'REC-Normal' and re.fullmatch(ORDINAL_PAT, text) or
                          self.curr_style_name.startswith('BIR-Day') and text.isdigit()):
            text = ''.join(('\\grordinalshead{', text, '}%\n'))
        self._backend.write(text)
        return

    def repack_rows(self):
        """ Transpose contents contained in a row of cols of cells
            to rows of cells with corresponding contents.
            Cols of the mult-row-cell are ended by SEPARATION_PAT
        """
        def set_tail(index, what):
            if len(self.tabmem.rows) >= index:
                self.tabmem.rows[-index].put_tail(''.join((what, '%-', repr(index),
                                                           '-\n')))
        self.tabmem.purge_last_row()
        bare_contents = [cell.content.strip(SEPARATION_PAT).split(SEPARATION_PAT)
                         for cell in self.tabrow.cells]

        # mk equal length & transposeorganize
        num_new_rows = max([len(mult_row_cont)
                            for mult_row_cont in bare_contents])
        cols_equ_len = []
        for mrc in bare_contents:
            for i in range(num_new_rows - len(mrc)):
                mrc.append('')
            cols_equ_len.append(mrc)
        transp_cont = list(zip(*cols_equ_len))

        # new row-col structure
        first_cell, last_cell = (0, self.numcols)
        for row in range(num_new_rows):
            new_row = TabRow()
            self.tabmem.add_row(new_row)
            for i in range(first_cell, last_cell):
                if i >= len(self.tabrow.cells):
                    continue
                new_cell = TabCell(get_charform(i + first_cell),
                                   self.tabrow.cells[i].span, self.tabrow.cells[i].head,
                                   transp_cont[row][i + first_cell])
                new_row.add_cell(new_cell)
            new_row.put_tail(self.tabrow.get_tail())
            if self.stick_next > 0:
                set_tail(1, NO_PAGE_BREAK)
                self.stick_next -= 1
            new_row.put_addit('')
        self.tabmem.rows[-1].put_addit(self.tabrow.get_addit())

        if self.curr_style_name in ['EOL-Generation', 'EOL-Normal',
                                    'FGR-ChildText', 'FGR-ParentName',
                                    'IDS-SectionTitle',
                                    'IDS-ImageCaption', 'NoteLink-Normal-Bold',
                                    'PLC-ColumnTitle', 'TR-Normal_Bold']:
            set_tail(3, NO_PAGE_BREAK)  # last but two
            set_tail(2, NORMAL_END)     # next to last
            set_tail(1, NO_PAGE_BREAK)  # last row
            if self.curr_style_name in ['IDS-SectionTitle', 'FGR-ParentName',
                                        'PCL-ColumnTitle']:
                self.stick_next = 2
                return
            self.stick_next = 1

    def discover_col_widths(self):
        """ Control width settings in latex table csonstruction
            Evaluations are set up here and passed to LaTeX
            to calculate required and to fix suitable widths.
        """
        total_pict_width = 4.0
        for col_num in range(self.numcols):
            col_char = get_charform(col_num)
            self._backend.write(''.join(('\\grinitlength{\\grmaxlencolcont',
                                         col_char, '}{0ex}%\n')))
            if self.kind_of_pict == IN_GALLERY:
                relevant_rows = self.tabmem.rows[1:2]
            else:
                relevant_rows = self.tabmem.rows
            for row in relevant_rows:
                if col_num >= len(row.cells):
                    break
                cell = row.cells[col_num]
                if cell.content.startswith('\\grmkpicture'):
                    pict_width = cell.content.split('}{')[1]
                    if self.kind_of_pict == IN_GALLERY:
                        self._backend.write(''.join(('\\grwidthofpict{',
                            str(float(pict_width)/total_pict_width), '\\grtabtextwd',
                            '}{\\grmaxlencolcont', col_char, '}%\n')))
                    else:
                        self._backend.write(''.join(('\\grwidthofpict{',
                            pict_width, '\\grbaseindent',
                            '}{\\grmaxlencolcont', col_char, '}%\n')))
                else:
                    for part in cell.content.split(SEPARATION_PAT):
                        self._backend.write(''.join(('\\grwidthoftext{', part,
                            '}{\\grmaxlencolcont', col_char, '}%\n')))
                    row.cells[col_num].content = cell.content.replace(
                        SEPARATION_PAT, '~\\newline \n')
            self._backend.write(
                ''.join(('\\grinitlength{\\grcolwidth', col_char, '}{0.0em}%\n')))

        #    adaptive fixing of column width
        for iter_cnt in range(self.numcols):
            self._backend.write('\\grprepcolswidthfix%\n')
            for col_num in range(self.numcols):
                col_char = get_charform(col_num)
                self._backend.write(
                    ''.join(('\\grcolswidthfix{\\grcolwidth', col_char,
                             '}{\\grmaxlencolcont', col_char, '}%\n')))


    def discover_multcol_widths(self):
        """ calc width of _latex_ multicolumns for each row """
        self.multcol_alph_counter = str_incr(MULTCOL_COUNT_BASE)
        for row in self.tabmem.rows:
            for cell_id, cell in enumerate(row.cells):
                if cell.span > 1:
                    multcol_alph_id = next(self.multcol_alph_counter)
                    self._backend.write(
                        ''.join(('\\grinitlength{', '\\grspanwidth',
                                 multcol_alph_id, '}{0em}%\n')))
                    col_char = get_charform(0 + cell_id)
                    for spw in range(cell.span):
                        self._backend.write(
                            ''.join(('\\addtolength{', '\\grspanwidth',
                                     multcol_alph_id, '}{\\grcolwidth',
                                     get_charform(get_numform(col_char) - spw), '}%\n')))

    def write_table(self):
        """ table data are completed, write out to the latex file"""
        self._backend.write('{%    start of table %\n')
        self._backend.write(''.join(self.tabmem.head))

        # special treatment at begin of longtable for heading and
        # closing at top and bottom of the table
        # and parts of it at pagebreak separating
        self.multcol_alph_counter = str_incr(MULTCOL_COUNT_BASE)
        splitted_row = self.mk_splitting_row(self.tabmem.rows[FIRST_ROW])
        self.multcol_alph_counter = str_incr(MULTCOL_COUNT_BASE)

        self._backend.write(splitted_row)
        self._backend.write('%\n\\endhead%\n')
        splitted_row = splitted_row.replace('{+2.0ex}', '{-2.0ex}')
        splitted_row = splitted_row.replace(NO_PAGE_BREAK, NORMAL_END)
        self._backend.write(splitted_row)
        self._backend.write('%\n\\endfoot%\n')

        if self.head_line:
            self.tabmem.rows[0].put_addit(
                ''.join(('\\hline%\n%\n', (self.numcols-1)*'&',
                         NO_PAGE_BREAK, '[-2ex]%\n')))
            self.head_line = False
        else:
            self._backend.write('%\n')
        if self.kind_of_pict != INDIVID_PICT:
            self._backend.write(self.mk_complete_row(self.tabmem.rows[FIRST_ROW], None))
        self._backend.write('\\endfirsthead%\n')
        self._backend.write('\\endlastfoot%\n')

        if self.kind_of_pict == INDIVID_PICT:
            #    special treatment for individual report, individual data with picture
            self._backend.write('\\multicolumn{2}{l}{%\n')
            self._backend.write('\\begin{tabular}[t]{*{2}l}%\n')
            # hand over _all_ rows
            for row in self.tabmem.rows:
                self._backend.write(self.mk_complete_row(row, -1))
            self._backend.write('\\end{tabular}%\n')
            self._backend.write('}&%\n')
            self._backend.write(
                ''.join(('\\grindivipict{%\n',
                         self.tabmem.rows[FIRST_ROW].cells[-1].content.replace(
                             '{b}', '{}'), '}%\n{',
                         self.tabmem.rows[SUBSEQ_ROW].cells[-1].content.replace(
                             '\\hfill', ''), '}%\n')))
            #    end of special treament for individual report
            self.tabmem.rows[0].put_addit('\\hline%\n%\n')

        else:
            # hand over _subsequent_ rows from number one on
            for row in self.tabmem.rows[SUBSEQ_ROW:]:
                self._backend.write(self.mk_complete_row(row, None))
        # close table by '\\end{longtable}'
        self._backend.write(''.join((''.join(self.tabmem.tail), '}%\n\n')))

    def mk_splitting_row(self, row):
        """ Prepare for page break within longtable """
        splitted = []
        add_vdots = '\\grempty'
        for cell in row.cells:
            if cell.span == 0:
                continue
            if (not splitted and
                    get_numform(cell.colchar) == self.numcols - 1):
                add_vdots = '\\graddvdots'
            if cell.span == 1:
                cell_width = ''.join(('\\grcolwidth', cell.colchar))
            else:
                cell_width = ''.join(('\\grspanwidth',
                                      next(self.multcol_alph_counter)))
            splitted.append(
                ''.join(('\\grtabpgbreak{', cell.head, '}{',
                         cell_width, '}{', add_vdots, '}{+2.0ex}%\n')))
        return ''.join((' & '.join(splitted), '%\n', row.get_tail()))

    def mk_complete_row(self, row, last):
        #    last:  '-1' for [:-1] or
        #           'None' for all i.e. [:]
        """ collocate all data of a latex row and write out """
        complete = []
        for cell in row.cells[:last]:
            if cell.span == 0:
                continue
            elif cell.span == 1:
                c_width = ''.join(('\\grcolwidth', cell.colchar))
            else:
                c_width = ''.join(('\\grspanwidth', next(self.multcol_alph_counter)))
            c_vpos = 't'
            c_content = cell.content.strip()
            if c_content.endswith(' %'):
                c_content = c_content[:-2].strip()
            self.space_below_paragr = self.get_v_adjust(LO_SPACE, self.curr_style_name)
            if c_content[-3:] == '{b}':
                c_vpos = 'b'
            complete.append(
                ''.join(('\\grcolpart{%\n', cell.head,
                         '}{%\n', c_width,
                         '}{%\n', c_vpos,
                         '}{%\n', self.get_v_adjust(HI_SPACE, self.curr_style_name[:3]),
                         '}{%\n', c_content,
                         '%\n}%\n')))
        return ''.join((' & '.join(complete), '%\n', row.get_tail(), row.get_addit()))
#       ---------------------------------------------------------------------
#       end of special table treatment
#       ---------------------------------------------------------------------



# ===========================================================
#
#       Interface to the central gramps doc-generator,
#       most of the following methods are called from there
#
# ===========================================================

    def page_break(self):
        """Should force a page break, creating a new page
           ... seldom used, can cause blank pages especially in conjunction
           with empty paragraphs; now replaced by vertical space
        """
        # self.emit('\\newpage%\n') #   previous version
        self.emit(''.join((
            '\\vspace{', self.get_v_adjust(LO_SPACE, 'instead_of_pg_break'), '}%\n')))

    def open(self, filename):
        """ Opens the specified file, making sure that it has the
            extension of .tex"""
        self._backend = LaTeXBackend(filename)
        self._backend.open()
        mapping_to_latex(filename, gramps_to_latex)

        # Font size control seems to be limited. For now, ignore
        # any style constraints, and use 12pt as the default
        options = "12pt"
        if self.paper.get_orientation() == PAPER_LANDSCAPE:
            options = options + ",landscape"

        # Old:
        # Paper selections are somewhat limited on a stock installation.
        # If the user picks something not listed here, we'll just accept
        # the default of the user's LaTeX installation (usually letter).
        paper_name = self.paper.get_size().get_name().lower()
        if paper_name in ["a4", "a5", "legal", "letter"]:
            options += ',' + paper_name + 'paper'

        # Old:
        # Paper selections are somewhat limited on a stock installation.
        # Use the article template, T1 font encodings, and specify
        # that we should use Latin1 and unicode character encodings.
        self.emit(_LATEX_TEMPLATE_1 % options)
        self.emit(_LATEX_TEMPLATE)
        self.emit(''.join(('\\vspace*{',
                           self.get_v_adjust(HI_SPACE, 'first_page_top'), '}%\n')))
        self.in_list = False
        self.in_table = False
        self.head_line = False

        # Establish some local styles for the report
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

            left = style.get_left_margin()
            first = style.get_first_indent() + left
            thisstyle.left_indent = left
            thisstyle.first_line_indent = first
            self.latexstyle[style_name] = thisstyle

    def close(self):
        """Clean up and close the document"""
        if self.in_list:
            self.emit('\\end{list}\n')
        self.emit('\\end{document}\n')
        self._backend.close()

    def end_page(self):
        """Issue a clear page command"""
        self.emit('\\clearpage')


    def prep_latex_styles(self):
        ''' special arrangement for latex '''
        self.space_below_paragr = self.get_v_adjust(LO_SPACE, self.curr_style_name)
        self.space_above_paragr = self.get_v_adjust(HI_SPACE, self.curr_style_name)
        if STYLE_DETAIL.sub(r'\1\3', self.curr_style_name) in ['ChildTitle', 'NoteHeader']:
            self.keep_text_style = '\\'.join((self.fend.rsplit('\\', 1)[0],
                                              self.fbeg.rsplit('\\', 1)[1]))
            return
        if STYLE_DETAIL.sub(r'\1\3', self.curr_style_name) in ['ChildList', 'Entry']:
            self.keep_text_style = ''
            return

    def start_paragraph(self, style_name, leader=None):
        """ Paragraphs handling - A Gramps paragraph is any
            single body of text from a single word to several sentences.
            We assume a linebreak at the end of each paragraph.
        """
        if style_name == 'DR-Title':
            self.emit('\\setlength{\\grbaseindent}{0.5\\grbaseindent}%\n')
        self.space_above_paragr = self.get_v_adjust(HI_SPACE, self.curr_style_name)
        self.space_below_paragr = self.get_v_adjust(LO_SPACE, self.curr_style_name)
        self.curr_style_name = style_name

        style_sheet = self.get_style_sheet()
        style = style_sheet.get_paragraph_style(style_name)
        ltxstyle = self.latexstyle[style_name]
        self.level = style.get_header_level()

        self.curr_style_name = style_name
        self.fbeg = ltxstyle.font_beg
        self.fend = ltxstyle.font_end

        self.indent = ltxstyle.left_indent
        self.first_line_indent = ltxstyle.first_line_indent
        if self.indent == 0:
            self.indent = self.first_line_indent

        self.prep_latex_styles()
        if not self.in_table:
            if leader:
                self._backend.write(
                    ''.join(('\\grprepleader{', leader, '}%\n')))
            else:
                self._backend.write('\\grprepnoleader%\n')

#           -------------------------------------------------------------------
            #   Gramps presumes 'cm' as units; here '\\grbaseindent' is used
            #   as equivalent, set in '_LATEX_TEMPLATE' above to '2.85em';
            #   there another value might be choosen.
#           -------------------------------------------------------------------
            if self.indent is not None:
                require_lines = '3'
                if STYLE_PARTS.sub(r'\2', self.curr_style_name) in ['First-Entry',
                    'Daystyle', 'Level', 'MoreHeader', 'NoteHeader',
                    'Subtitle', 'Header']:
                                            #      PCL-Section, geht das ???
                    require_lines = '6'
                if STYLE_PARTS.sub(r'\2', self.curr_style_name) in ['ChildTitle',
                           'Generation', 'Heading', 'Monthstyle', 'PlaceTitle', 'Section']:
                    require_lines = '8'
                if self.curr_style_name in ['PLC-PlaceTitle', 'BIR-Daystyle']:
                    self.indent = 0
                self._backend.write(''.join(('\\grparagrhead{', self.space_above_paragr,
                                             '}{', repr(self.indent),
                                             '}{', require_lines,
                                             '}{', self.keep_text_style, '}%\n')))
                self.fix_indent = True
                if leader is not None and not self.in_list:
                    self.in_list = True
                    self._backend.write(''.join(('\\grlisthead{', require_lines, '}{',
                                                 leader, '}%\n')))
        if leader is None:
            if self.fbeg.strip() != '':
                self.emit('%s ' % self.fbeg)
        self.emit(self.get_v_adjust(HI_STRUT, self.curr_style_name))


    def end_paragraph(self):
        """End the current paragraph"""
        if self.curr_style_name in ['REC-Normal', 'BIR-Day']:
            self.textmem.append('\\grordinalstail%\n')
        ending = ['%\n']
        ending.append(self.get_v_adjust(LO_STRUT, self.curr_style_name))
        if self.in_list:
            self.in_list = False
            self.emit('%\n\\grlisttail%\n')
            ending = []
        elif self.in_table:
            ending.append(SEPARATION_PAT)
        final = ''.join(ending)
        if self.fend.strip() != '' or final.strip() != '':
            self.emit('%s%s' % (self.fend, final))
        if self.fix_indent:
            self.fix_indent = False
            self.emit(''.join(('\\grparagrtail{', self.space_below_paragr, '}%\n')))
        self.space_below_paragr = self.get_v_adjust(LO_SPACE, self.curr_style_name)
        if self.curr_style_name.startswith('DR'):
            self.emit('\\small%\n')

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


#---------------------------------------------------------------------
#
# Methods for table construction; values are supplied.
# For new LaTeX output some former settings are ignored.
#
#---------------------------------------------------------------------

    def start_table(self, name, style_name):
        """Begin new table"""
        self.in_table = True
        self.curr_tab_style = style_name
        self.currow = 0

        # We need to know a priori how many columns are in this table
        styles = self.get_style_sheet()
        self.tblstyle = styles.get_table_style(style_name)
        self.numcols = self.tblstyle.get_columns()
        self.column_order = []
        for cell in range(self.numcols):
            self.column_order.append(cell)
        if self.get_rtl_doc():
            self.column_order.reverse()
        tblfmt = '*{%d}{l}' % self.numcols
        self._backend.write('\\needspace{5\\baselineskip}%\n')
        self._backend.write(''.join(('\\grpresettab{', repr(self.numcols),
                                     '}{', repr(self.indent), '}%\n')))
        self.tabmem = TabMem(self.get_v_adjust(HI_SPACE, 'before_tab'), tblfmt)

    def end_table(self):
        """Close the table environment"""
        self.tabmem.close(self.kind_of_pict, self.numcols,
                          self.get_v_adjust(LO_SPACE, 'behind_tab'))
        # table completed, calc widths and write out
        self.discover_col_widths()
        self.discover_multcol_widths()
        self.write_table()
        self.kind_of_pict = UNKNOWN
        self.in_table = False
        for col_num in range(self.numcols):
            col_char = get_charform(col_num)
            self._backend.write(''.join(('\\setlength{\\grmaxlencolcont', col_char,
                                         '}{0em}%\n')))

    def start_row(self):
        """Begin a new row"""
        self.tabrow = TabRow()
        self.tabmem.add_row(self.tabrow)
        self.row_start = True

        # doline/skipfirst are flags for adding hor. rules
        self.doline = False
        self.skipfirst = False
        self.curcol = 0
        self.currow += 1

    def end_row(self):
        """End the row (new line)"""
        if self.doline:
            if self.skipfirst:
                self.tabrow.put_addit(''.join((('\\cline{2-%d}' % self.numcols), '%\n')))
            else:
                self.tabrow.put_addit('\\hline%\n%\n')
        elif self.curr_style_name in ['PLC-ColumnTitle', 'TR-Normal-Bold',
                                      'NoteLink-Normal-Bold']:
            self.head_line = True
        else:
            self.tabrow.put_addit('%\n')
        self.repack_rows()

    def start_cell(self, style_name, span=1):
        """Add an entry to the table.
        We always place our data inside braces
        for safety of formatting."""
        self.colspan = span
        self.curcol += self.colspan
        styles = self.get_style_sheet()
        self.cstyle = styles.get_cell_style(style_name)

#------------------------------------------------------------------
        # begin special modification for boolean values
        # values imported here are used for test '==1' and '!=0'. To get
        # local boolean values the tests are now transfered to the import lines
#------------------------------------------------------------------
        self.lborder = self.cstyle.get_left_border() == 1
        self.rborder = self.cstyle.get_right_border() == 1
        self.bborder = self.cstyle.get_bottom_border() == 1
        self.tborder = self.cstyle.get_top_border() != 0
        cellfmt = "l"
        # new settings:
        self.lborder = 0
        self.rborder = 0
        self.bborder = 0

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

        self.row_start = False
        self.textmem = []
        self.curcol_char = get_charform(self.curcol-1)
        if span > 1: # phantom columns prior to multicolumns
            for col in range(self.curcol - span, self.curcol - 1):
                col_char = get_charform(col)
                self.tabrow.add_cell(TabCell(col_char, 0, '', ''))
        self.tabcell = TabCell(self.curcol_char, span,
                               '\\multicolumn{%d}{%s}' % (span, cellfmt), '')
        self.tabrow.add_cell(self.tabcell)

    def end_cell(self):
        """Close current cell and repare for next one"""
        self.textmem.insert(
            0, self.get_v_adjust(HI_STRUT, self.curr_style_name))
        self.tabcell.close(''.join(self.textmem).strip())
        self.textmem = []

    def add_media(self, infile, pos, x, y, alt='', style_name=None, crop=None):
        """Add photo to report"""
        outfile = infile
        pictname = latexescape(os.path.basename(infile))
        if HAVE_PIL:
            try:
                curr_img = Image.open(infile)
                if crop:
                    cr_n = [round(x*y/100) for x, y in zip(2*curr_img.size, crop)]
                    curr_img = curr_img.crop(cr_n)
                    outfile = 'temp_' + os.path.basename(infile)
                    curr_img.save(outfile)
                width, height = curr_img.size
                if height > y:
                    x = round(y*width/height)
            except IOError:
                self.emit(''.join(('\\grmkpicture{Error\_!}{', repr(x), '}{',
                                   repr(y), '}{', 'cannot convert:\\\\[2ex]',
                                   pictname, '\\\\[4ex]} ', SEPARATION_PAT)))
                return
        elif not HAVE_PIL:
            from gramps.gen.config import config
            if not config.get('interface.ignore-pil'):
                from gramps.gen.constfunc import has_display
                if has_display() and self.uistate:
                    from gramps.gui.dialog import MessageHideDialog
                    title = _("PIL (Python Imaging Library) not loaded.")
                    message = _("Production of jpg images from non-jpg images "
                                "in LaTeX documents will not be available. "
                                "Use your package manager to install "
                                "python-imaging or python-pillow or "
                                "python3-pillow")
                    MessageHideDialog(title, message, 'interface.ignore-pil',
                                      parent=self.uistate.window)
            self.emit(''.join(('\\grmkpicture{Error\_!}{', repr(x), '}{', repr(y), '}{',
                               'PIL not installed\\\\[4ex]} ', SEPARATION_PAT)))
            return
        self.emit(''.join(('\\grmkpicture{', outfile, '}{', repr(x), '}{',
                           repr(y), '}{b} ', SEPARATION_PAT)))

    def write_text(self, text, mark=None, links=False):
        """Write the text to the file"""
        if text == '\n':
            text = ''
        text = latexescape(text)
        self.space_below_paragr = self.get_v_adjust(LO_SPACE, self.curr_style_name)
        if links is True:
            text = re.sub(URL_PATTERN, _CLICKABLE, text)

        #hard coded replace of the underline used for missing names/data
        text = text.replace('\\_' * 13,
                            '\\underline{\\hspace{3.0\\grbaseindent}}')
        self.emit(text)


    def write_styled_note(self, styledtext, given_format, style_name,
                          contains_html=False, links=False):
        """

        Convenience function to write a styledtext to the latex doc.
        styledtext : assumed a StyledText object to write
        given_format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        contains_html: bool, the backend should not check if html is present.
            If contains_html=True, then the textdoc is free to handle that in
            some way. Eg, a textdoc could remove all tags, or could make sure
            a link is clickable. self ignores notes that contain html
        links: bool, make URLs clickable if True
        """
        if contains_html:
            return
        text = str(styledtext)

        s_tags = styledtext.get_tags()
        if given_format:
            # preformatted, use different escape function
            self._backend.setescape(True)

        markuptext = self._backend.add_markup_from_styled(text, s_tags)

        if links is True:
            markuptext = re.sub(URL_PATTERN, _CLICKABLE, markuptext)
        markuptext = self._backend.add_markup_from_styled(text, s_tags)

        # there is a problem if we write out a note in a table.
        # ...
        # now solved by postprocessing in self.discover_col_widths()
        # by explicitely setting suitable width for all columns.
        #
        if given_format:
            self.start_paragraph(style_name)
            self.emit(markuptext)
            self.end_paragraph()
            # preformatted finished, go back to normal escape function
            self._backend.setescape(False)
        else:
            for line in markuptext.split('%\n%\n '):
                self.start_paragraph(style_name)
                for realline in line.split('\n'):
                    self.emit(realline)
                self.end_paragraph()
