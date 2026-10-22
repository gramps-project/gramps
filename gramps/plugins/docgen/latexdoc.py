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
#               2019-2020  Harald Rosemann
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""LaTeX document generator"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from __future__ import annotations
from bisect import bisect
import re
import os.path
import hashlib
import logging

try:
    from PIL import Image

    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

# ----------------------------------------------------------------------- -
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug.docgen import (
    BaseDoc,
    TextDoc,
    PAPER_LANDSCAPE,
    FONT_SANS_SERIF,
    URL_PATTERN,
)
from gramps.gen.plug.docbackend import DocBackend
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.image import crop_percentage_to_pixel

_ = glocale.translation.gettext

_LOG = logging.getLogger(".latexdoc")

_CLICKABLE = "\\url{\\1}"

# ------------------------------------------------------------------------
#
# Special settings for LaTeX output
#
# ------------------------------------------------------------------------
#   For an interim mark e.g. for an intended linebreak I use a special pattern.
#   It shouldn't interfere with normal text. In LaTeX character '&' is used
#   for column separation in tables and may occur there in series. The pattern
#   is used here before column separation is set. On the other hand incoming
#   text can't show this pattern for it would have been replaced by '\&\&'.
#   So the choosen pattern will do the job without confusion:

SEPARATION_PAT = "&&"
# \\grmkpicture{file}{width}{height}{label} and text following it
PICT_PAT = re.compile(
    r"(\\grmkpicture\{[^}]*\}\{([^}]*)\}\{[^}]*\}\{)([^}]*)\}(.*)", re.S
)
# image formats pdflatex includes without conversion
LATEX_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".pdf")

# ------------------------------------------------------------------------
#
# LaTeX Article Template
#
# ------------------------------------------------------------------------

_LATEX_TEMPLATE_1 = "\\documentclass[%s]{article}\n"
_LATEX_TEMPLATE = """%
%
\\usepackage[T1]{fontenc}%
%
% We use latin1 encoding at a minimum by default.
% Gramps uses unicode UTF-8 encoding for its
% international support. LaTeX can deal gracefully
% with unicode encoding by using the ucs style invoked
% when utf8 is specified as an option to the inputenc
% package. This package is included by default in some
% installations, but not in others, so we do not make it
% the default.  Uncomment the first line if you wish to use it
% (If you do not have ucs.sty, you may obtain it from
%  http://www.tug.org/tex-archive/macros/latex/contrib/supported/unicode/)
%
%\\usepackage[latin1]{inputenc}%
\\usepackage[latin1,utf8]{inputenc}%
\\usepackage{graphicx}% Extended graphics support
\\usepackage{longtable}% For multi-page tables
\\usepackage{calc}% For some calculations
\\usepackage{ifthen}% For table width calculations
\\usepackage{ragged2e}% For left aligning with hyphenation
\\usepackage{wrapfig}% wrap pictures in text
\\usepackage[normalem]{ulem}% For strikeout
%
% Depending on your LaTeX installation, the margins may be too
% narrow.  This can be corrected by uncommenting the following
% two lines and adjusting the width appropriately. The example
% removes 0.5in from each margin. (Adds 1 inch to the text)
%\\addtolength{\\oddsidemargin}{-0.5in}%
%\\addtolength{\\textwidth}{1.0in}%
%
% Vertical spacing between paragraphs:
% take one of three possibilities or modify to your taste:
%\\setlength{\\parskip}{1.0ex plus0.2ex minus0.2ex}%
\\setlength{\\parskip}{1.5ex plus0.3ex minus0.3ex}%
%\\setlength{\\parskip}{2.0ex plus0.4ex minus0.4ex}%
%
% Vertical spacing between lines:
% take one of three possibilities or modify to your taste:
\\renewcommand{\\baselinestretch}{1.0}%
%\\renewcommand{\\baselinestretch}{1.1}%
%\\renewcommand{\\baselinestretch}{1.2}%
%
% Indentation; substitute for '1cm' of gramps, 2.5em is right for 12pt
% take one of three possibilities or modify to your taste:
\\newlength{\\grbaseindent}%
%\\setlength{\\grbaseindent}{3.0em}%
\\setlength{\\grbaseindent}{2.5em}%
%\\setlength{\\grbaseindent}{2.0em}%
%
%
% -------------------------------------------------------------
% New lengths, counters and commands for calculations in tables
% -------------------------------------------------------------
%
\\newlength{\\grtabwidth}%
\\newlength{\\grtabprepos}%
\\newlength{\\grreqwidth}%
\\newlength{\\grtempwd}%
\\newlength{\\grmaxwidth}%
\\newlength{\\grprorated}%
\\newlength{\\grxwd}%
\\newlength{\\grcellpictwd}%
\\newlength{\\grwidthused}%
\\newlength{\\grreduce}%
\\newlength{\\grcurcolend}%
\\newlength{\\grspanwidth}%
\\newlength{\\grleadlabelwidth}%
\\newlength{\\grminpgindent}%
\\newlength{\\grlistbacksp}%
\\newlength{\\grpictsize}%
\\newlength{\\grmaxpictsize}%
\\newlength{\\grtextsize}%
\\newlength{\\grmaxtextsize}%
\\newcounter{grtofixcnt}%
\\newcounter{grxwdcolcnt}%
%
%
\\newcommand{\\grinitlength}[2]{%
  \\ifthenelse{\\isundefined{#1}}%
    {\\newlength{#1}}{}%
  \\setlength{#1}{#2}%
}%
%
\\newcommand{\\grinittab}[2]{%    #1: tabwidth, #2 = 1.0/anz-cols
  \\setlength{\\grtabwidth}{#1}%
  \\setlength{\\grprorated}{#2\\grtabwidth}%
  \\setlength{\\grwidthused}{0em}%
  \\setlength{\\grreqwidth}{0em}%
  \\setlength{\\grmaxwidth }{0em}%
  \\setlength{\\grxwd}{0em}%
  \\setlength{\\grtempwd}{0em}%
  \\setlength{\\grpictsize}{0em}%
  \\setlength{\\grmaxpictsize}{0em}%
  \\setlength{\\grtextsize}{0em}%
  \\setlength{\\grmaxtextsize}{0em}%
  \\setlength{\\grcurcolend}{0em}%
  \\setcounter{grxwdcolcnt}{0}%
  \\setcounter{grtofixcnt}{0}%  number of wide cols%
  \\grinitlength{\\grcolbega}{0em}% beg of first col
}%
%
\\newcommand{\\grmaxvaltofirst}[2]{%
  \\ifthenelse{\\lengthtest{#1 < #2}}%
    {\\setlength{#1}{#2}}{}%
}%
%
\\newcommand{\\grsetreqfull}{%
  \\grmaxvaltofirst{\\grmaxpictsize}{\\grpictsize}%
  \\grmaxvaltofirst{\\grmaxtextsize}{\\grtextsize}%
}%
%
\\newcommand{\\grsetreqpart}[1]{%
  \\addtolength{\\grtextsize}{#1 - \\grcurcolend}%
  \\addtolength{\\grpictsize}{#1 - \\grcurcolend}%
  \\grsetreqfull%
}%
%
\\newcommand{\\grdividelength}{%
 \\setlength{\\grtempwd}{\\grtabwidth - \\grwidthused}%
%    rough division of lengths:
%    if 0 < #1 <= 10: \\grxwd = ~\\grtempwd / grtofixcnt
%    otherwise: \\grxwd =  \\grprorated
 \\ifthenelse{\\value{grtofixcnt} > 0}%
  {\\ifthenelse{\\value{grtofixcnt}=1}%
                    {\\setlength{\\grxwd}{\\grtempwd}}{%
    \\ifthenelse{\\value{grtofixcnt}=2}
                    {\\setlength{\\grxwd}{0.5\\grtempwd}}{%
     \\ifthenelse{\\value{grtofixcnt}=3}
                    {\\setlength{\\grxwd}{0.333\\grtempwd}}{%
      \\ifthenelse{\\value{grtofixcnt}=4}
                    {\\setlength{\\grxwd}{0.25\\grtempwd}}{%
       \\ifthenelse{\\value{grtofixcnt}=5}
                    {\\setlength{\\grxwd}{0.2\\grtempwd}}{%
        \\ifthenelse{\\value{grtofixcnt}=6}
                    {\\setlength{\\grxwd}{0.166\\grtempwd}}{%
         \\ifthenelse{\\value{grtofixcnt}=7}
                    {\\setlength{\\grxwd}{0.143\\grtempwd}}{%
          \\ifthenelse{\\value{grtofixcnt}=8}
                    {\\setlength{\\grxwd}{0.125\\grtempwd}}{%
           \\ifthenelse{\\value{grtofixcnt}=9}
                    {\\setlength{\\grxwd}{0.111\\grtempwd}}{%
            \\ifthenelse{\\value{grtofixcnt}=10}
                    {\\setlength{\\grxwd}{0.1\\grtempwd}}{%
             \\setlength{\\grxwd}{\\grprorated}% give up, take \\grprorated%
    }}}}}}}}}}%
  \\setlength{\\grreduce}{0em}%
  }{\\setlength{\\grxwd}{0em}}%
}%
%
\\newcommand{\\grtextneedwidth}[1]{%
  \\settowidth{\\grtempwd}{#1}%
  \\grmaxvaltofirst{\\grtextsize}{\\grtempwd}%
}%
%
\\newcommand{\\grcolsfirstfix}[5]{%
  \\grinitlength{#1}{\\grcurcolend}%
  \\grinitlength{#3}{0em}%
  \\grinitlength{#4}{\\grmaxpictsize}%
  \\grinitlength{#5}{\\grmaxtextsize}%
  \\grinitlength{#2}{#5}%
  \\grmaxvaltofirst{#2}{#4}%
  \\addtolength{#2}{2\\tabcolsep}%
  \\grmaxvaltofirst{\\grmaxwidth}{#2}%
  \\ifthenelse{\\lengthtest{#2 < #4} \\or \\lengthtest{#2 < \\grprorated}}%
    { \\setlength{#3}{#2}%
      \\addtolength{\\grwidthused}{#2} }%
    { \\stepcounter{grtofixcnt} }%
  \\addtolength{\\grcurcolend}{#2}%
}%
%
\\newcommand{\\grcolssecondfix}[4]{%
  \\ifthenelse{\\lengthtest{\\grcurcolend < \\grtabwidth}}%
    { \\setlength{#3}{#2} }%
    { \\addtolength{#1}{-\\grreduce}%
      \\ifthenelse{\\lengthtest{#2 = \\grmaxwidth}}%
        { \\stepcounter{grxwdcolcnt}}%
        { \\ifthenelse{\\lengthtest{#3 = 0em} \\and %
                       \\lengthtest{#4 > 0em}}%
            { \\setlength{\\grtempwd}{#4}%
              \\grmaxvaltofirst{\\grtempwd}{\\grxwd}%
              \\addtolength{\\grreduce}{#2 - \\grtempwd}%
              \\setlength{#2}{\\grtempwd}%
              \\addtolength{\\grwidthused}{#2}%
              \\addtocounter{grtofixcnt}{-1}%
              \\setlength{#3}{#2}%
            }{}%
        }%
    }%
}%
%
\\newcommand{\\grcolsthirdfix}[3]{%
  \\ifthenelse{\\lengthtest{\\grcurcolend < \\grtabwidth}}%
    {}{ \\addtolength{#1}{-\\grreduce}%
        \\ifthenelse{\\lengthtest{#3 = 0em} \\and %
                     \\lengthtest{#2 < \\grmaxwidth}}%
          { \\ifthenelse{\\lengthtest{#2 < 0.5\\grmaxwidth}}%
              { \\setlength{\\grtempwd}{0.5\\grxwd}%
                \\grmaxvaltofirst{\\grtempwd}{0.7\\grprorated}}%
              { \\setlength{\\grtempwd}{\\grxwd}}%
            \\addtolength{\\grreduce}{#2 - \\grtempwd}%
            \\setlength{#2}{\\grtempwd}%
            \\addtolength{\\grwidthused}{#2}%
            \\addtocounter{grtofixcnt}{-1}%
            \\setlength{#3}{#2}%
          }{}%
      }%
}%
%
\\newcommand{\\grcolsfourthfix}[3]{%
  \\ifthenelse{\\lengthtest{\\grcurcolend < \\grtabwidth}}%
    {}{ \\addtolength{#1}{-\\grreduce}%
        \\ifthenelse{\\lengthtest{#3 = 0em}}%
          { \\addtolength{\\grreduce}{#2 - \\grxwd}%
            \\setlength{#2}{\\grxwd}%
            \\setlength{#3}{#2}%
          }{}%
      }%
}%
%
\\newcommand{\\grgetspanwidth}[4]{%
  \\grinitlength{#1}{#3 - #2 + #4}%
}%
%
\\newcommand{\\tabheadstrutceil}{%
  \\rule[0.0ex]{0.00em}{3.5ex}}%
\\newcommand{\\tabheadstrutfloor}{%
  \\rule[-2.0ex]{0.00em}{2.5ex}}%
\\newcommand{\\tabrowstrutceil}{%
  \\rule[0.0ex]{0.00em}{2.9ex}}%
\\newcommand{\\tabrowstrutfloor}{%
  \\rule[-0.1ex]{0.00em}{2.0ex}}%
%
\\newcommand{\\grempty}[1]{}%
%
\\newcommand{\\graddvdots}[1]{%
  \\hspace*{\\fill}\\hspace*{\\fill}\\raisebox{#1}{\\vdots}%
}%
%
\\newcommand{\\grtabpgbreak}[4]{%
  #1 { \\parbox[t]{ #2 - 2\\tabcolsep}{\\tabheadstrutceil\\hspace*{\\fill}%
  \\raisebox{#4}{\\vdots} #3{#4} \\hspace*{\\fill}\\tabheadstrutfloor}}%
}%
%
\\newcommand{\\grcolpart}[3]{%
  #1 { \\parbox[t]{ #2 - 2\\tabcolsep}%
  {\\tabrowstrutceil #3~\\\\[-1.6ex]\\tabrowstrutfloor}}%
}%
%
\\newcommand{\\grminpghead}[2]{%
  \\setlength{\\grminpgindent}{#1\\grbaseindent-\\grlistbacksp}%
  \\hspace*{\\grminpgindent}%
  \\ifthenelse{\\not \\lengthtest{#2em > 0em}}%
    {\\begin{minipage}[t]{\\textwidth -\\grminpgindent}}%
    {\\begin{minipage}[t]{\\textwidth -\\grminpgindent%
        -#2\\grbaseindent -4\\tabcolsep}}%
}%
%
\\newcommand{\\grminpgtail}{%
  \\end{minipage}\\parindent0em%
}%
%
\\newcommand{\\grlisthead}[1]{%
  \\begin{list}{#1}%
    { \\setlength{\\labelsep}{0.5em}%
      \\setlength{\\labelwidth}{\\grleadlabelwidth}%
      \\setlength{\\leftmargin}{\\grlistbacksp}%
    }\\item%
}%
%
\\newcommand{\\grlisttail}{%
  \\end{list}%
}%
%
\\newcommand{\\grprepleader}[1]{%
  \\settowidth{\\grtempwd}{#1}%
  \\ifthenelse{\\lengthtest{\\grtempwd > \\grleadlabelwidth}}%
    { \\setlength{\\grleadlabelwidth}{\\grtempwd}}{}%
  \\setlength{\\grlistbacksp}{\\grleadlabelwidth + 1.0em}%
}%
%
\\newcommand{\\grprepnoleader}{%
  \\setlength{\\grleadlabelwidth}{0em}%
  \\setlength{\\grlistbacksp}{0em}%
}%
%
\\newcommand{\\grmkpicture}[4]{%
    \\begin{wrapfigure}{r}{#2\\grbaseindent}%
      \\vspace{-6ex}%
      \\begin{center}%
      \\includegraphics[%
        width= #2\\grbaseindent,%
        height= #3\\grbaseindent,%
          keepaspectratio]%
        {#1}\\\\%
      {\\RaggedRight\\footnotesize#4}%
      \\end{center}%
    \\end{wrapfigure}%
    \\settowidth{\\grtempwd}{\\footnotesize#4}%
    \\setlength{\\grxwd}{#2\\grbaseindent}%
    \\ifthenelse{\\lengthtest{\\grtempwd < 0.7\\grxwd}}%
                    {\\setlength{\\grxwd}{1ex}}{%
      \\ifthenelse{\\lengthtest{\\grtempwd < 1.2\\grxwd}}%
                    {\\setlength{\\grxwd}{2ex}}{%
        \\ifthenelse{\\lengthtest{\\grtempwd < 1.8\\grxwd}}%
                    {\\setlength{\\grxwd}{6ex}}{%
          \\ifthenelse{\\lengthtest{\\grtempwd < 2.0\\grxwd}}%
                    {\\setlength{\\grxwd}{10ex}}{%
                     \\setlength{\\grxwd}{12ex}}%
                    }}}%
  \\setlength{\\grtempwd}{#3\\grbaseindent + \\grxwd}%
  \\rule[-\\grtempwd]{0pt}{\\grtempwd}%
  \\setlength{\\grtabprepos}{-\\grtempwd}%
}%
%
\\newcommand{\\grcellpicture}[4]{%  picture inside a table cell
  \\setlength{\\grcellpictwd}{\\minof{#2\\grbaseindent}{\\linewidth}}%
  {\\centering\\includegraphics[%
    width= \\grcellpictwd,%
    height= #3\\grbaseindent,%
    keepaspectratio]%
    {#1}\\par}%
}%
%
%
\\begin{document}%
"""


# ------------------------------------------------------------------------
#
# Font size table and function
#
# ------------------------------------------------------------------------

# These tables correlate font sizes to LaTeX.  The first table contains
# typical font sizes in points.  The second table contains the standard
# LaTeX font size names. Since we use bisect to map the first table to the
# second, we are guaranteed that any font less than 6 points is 'tiny', fonts
# from 6-7 points are 'script', etc. and fonts greater than or equal to 22
# are considered 'Huge'.  Note that fonts from 12-13 points are not given a
# LaTeX font size name but are considered "normal."

_FONT_SIZES = [6, 8, 10, 12, 14, 16, 18, 20, 22]
_FONT_NAMES = [
    "tiny",
    "scriptsize",
    "footnotesize",
    "small",
    "",
    "large",
    "Large",
    "LARGE",
    "huge",
    "Huge",
]


def map_font_size(fontsize):
    """Map font size in points to LaTeX font size"""
    return _FONT_NAMES[bisect(_FONT_SIZES, fontsize)]


# ------------------------------------------------------------------------
#
# auxiliaries to facilitate table construction
#
# ------------------------------------------------------------------------

# patterns for regular expressions, module re:
TBLFMT_PAT = re.compile(r"({\|?)l(\|?})")

# constants for routing in table construction:
CELL_BEG, CELL_TEXT, CELL_END, ROW_BEG, ROW_END, TAB_BEG, TAB_END = list(range(7))
FIRST_ROW, SUBSEQ_ROW = list(range(2))

# endings of table rows
NORMAL_END = r"\\"
NO_PAGE_BREAK = r"\\*"

# rows of a table cell written in these styles are kept on one page
KEEP_TOGETHER_STYLES = {
    "EOL-Generation",
    "EOL-Normal",
    "FGR-ChildText",
    "FGR-ParentName",
    "IDS-SectionTitle",
    "IDS-ImageCaption",
    "NoteLink-Normal-Bold",
    "PLC-ColumnTitle",
    "TR-Normal-Bold",
}
# headings, kept on one page with the row following them
HEADING_STYLES = {"IDS-SectionTitle", "FGR-ParentName", "PLC-ColumnTitle"}


def get_charform(col_num):
    """Transfer column number to column character,
    limited to letters within Station a-z  (26, there is no need for more).
    early test of column count in start_table()
    """
    if col_num > ord("z") - ord("a"):
        raise ValueError(
            "".join(
                (
                    "\n number of table columns is ",
                    repr(col_num),
                    "\n                     should be <= ",
                    repr(ord("z") - ord("a")),
                )
            )
        )
    return chr(ord("a") + col_num)


def get_numform(col_char):
    return ord(col_char) - ord("a")


# ------------------------------------------
#   row_alph_counter = str_incr(MULTCOL_COUNT_BASE)
#
#   'aaa' is sufficient for up to 17576 multicolumns in each table;
#   do you need more?
#   uncomment one of the two lines
MULTCOL_COUNT_BASE = "aaa"
# MULTCOL_COUNT_BASE = 'aaaa'
# ------------------------------------------


def str_incr(str_counter):
    """for counting table rows"""
    lili = list(str_counter)
    while 1:
        yield "".join(lili)
        if "".join(lili) == len(lili) * "z":
            raise ValueError(
                "".join(
                    (
                        "\n can't increment string ",
                        "".join(lili),
                        " of length ",
                        str(len(lili)),
                    )
                )
            )
        for i in reversed(range(len(lili))):
            if lili[i] < "z":
                lili[i] = chr(ord(lili[i]) + 1)
                break
            else:
                lili[i] = "a"


def pict_with_caption(pict: str, more_lines: list[str] | None = None) -> str:
    """
    Move the text following a \\grmkpicture command, and any further
    caption lines, into its label argument, so that they are set beneath
    the picture.
    """
    match = PICT_PAT.match(pict)
    if match is None:
        return pict
    lines = [match.group(4)] + (more_lines or [])
    # an unescaped "%" would comment out the end of the label
    lines = [
        re.sub(r"(?<!\\)%.*", "", line).replace("\\hfill", "").strip() for line in lines
    ]
    caption = "\\newline ".join(line for line in lines if line)
    if not caption:
        return "".join((match.group(1), match.group(3), "}"))
    label = " ".join(part for part in (match.group(3), caption) if part)
    return "".join((match.group(1), label, "}"))


def pict_width_of(pict: str) -> float:
    """
    Return the width argument of a \\grmkpicture command, or 0.
    """
    match = PICT_PAT.match(pict)
    if match is None:
        return 0
    try:
        return float(match.group(2))
    except ValueError:
        return 0


# ------------------------------------------------------------------------
#
# LaTeX Table-Memory and related methods
#
# ------------------------------------------------------------------------


class TabCell:
    """ " cell of a row of a table"""

    def __init__(self, colchar, span, head, content):
        self.colchar = colchar
        self.span = span
        self.head = head
        self.content = content


class TabRow:
    """ " row of a table"""

    def __init__(self):
        self.cells = []
        self.tail = ""
        self.addit = ""  # for: \\hline, \\cline{}


class TabMem:
    def __init__(self, head):
        self.head = head
        self.tail = ""
        self.rows = []


# ------------------------------------------------------------------------
#
# Functions for docbackend
#
# ------------------------------------------------------------------------
def latexescape(text):
    """
    Escape the following special characters: & $ % # _ { }
    """
    text = text.replace("&", "\\&")
    text = text.replace("$", "\\$")
    text = text.replace("%", "\\%")
    text = text.replace("#", "\\#")
    text = text.replace("_", "\\_")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    # replace character unknown to LaTeX
    text = text.replace("→", "$\\longrightarrow$")
    return text


def latexescapeverbatim(text):
    """Escape special characters and also make sure that LaTeX
    respects whitespace and newlines correctly.
    """
    text = latexescape(text)
    text = text.replace(" ", "\\ ")
    text = text.replace("\n", "~\\newline \n")
    # spaces at begin are normally ignored, make sure they are not.
    # due to above a space at begin is now \newline\n\
    text = text.replace("\\newline\n\\ ", "\\newline\n\\hspace*{0.1\\grbaseindent}\\ ")
    return text


# ------------------------------------------------------------------------
#
# Document Backend class for cairo docs
#
# ------------------------------------------------------------------------


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
        DocBackend.SUPERSCRIPT,
        DocBackend.SUBSCRIPT,
        DocBackend.STRIKETHROUGH,
    ]

    STYLETAG_MARKUP = {
        DocBackend.BOLD: ("\\textbf{", "}"),
        DocBackend.ITALIC: ("\\textit{", "}"),
        DocBackend.UNDERLINE: ("\\underline{", "}"),
        DocBackend.SUPERSCRIPT: ("\\textsuperscript{", "}"),
        DocBackend.SUBSCRIPT: ("\\textsubscript{", "}"),
        DocBackend.STRIKETHROUGH: ("\\sout{", "}"),
    }

    def ESCAPE_FUNC(x):
        return latexescape

    def setescape(self, preformatted=False):
        """
        LaTeX needs two different escape functions depending on the type.
        This function allows to switch the escape function
        """
        if not preformatted:
            LaTeXBackend.ESCAPE_FUNC = lambda x: latexescape

        else:
            LaTeXBackend.ESCAPE_FUNC = lambda x: latexescapeverbatim

    def _create_xmltag(self, tagtype, value):
        r"""
        overwrites the method in DocBackend.
        creates the latex tags needed for non bool style types we support:
            FONTSIZE : use different \large denomination based on size
                                     : very basic, in mono in the font face
                                        then we use {\ttfamily }
        """
        if tagtype not in self.SUPPORTED_MARKUP:
            return None
        elif tagtype == DocBackend.FONTSIZE:
            # translate size in point to something LaTeX can work with
            fontsize = map_font_size(value)
            if fontsize:
                return ("{\\" + fontsize + " ", "}")
            else:
                return ("", "")

        elif tagtype == DocBackend.FONTFACE:
            if "MONO" in value.upper():
                return ("{\\ttfamily ", "}")
            elif "ROMAN" in value.upper():
                return ("{\\rmfamily ", "}")
        return None

    def _checkfilename(self):
        """
        Check to make sure filename satisfies the standards for this filetype
        """

        if not self._filename.endswith(".tex"):
            self._filename = self._filename + ".tex"


# ------------------------------------------------------------------------
#
# Paragraph Handling
#
# ------------------------------------------------------------------------


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


# ------------------------------------------------------------------
#
# LaTeXDoc
#
# ------------------------------------------------------------------


class LaTeXDoc(BaseDoc, TextDoc):
    """LaTeX document interface class. Derived from BaseDoc"""

    #   ---------------------------------------------------------------
    #   some additional variables
    #   ---------------------------------------------------------------
    in_table = False
    in_multrow_cell = False  #   for tab-strukt: cols of rows
    pict = ""
    pict_in_table = False
    pict_width = 0
    pict_height = 0
    fix_indent = False
    textmem: list[str] = []
    in_title = True
    row_styles: set[str] = set()

    #   ---------------------------------------------------------------
    #   begin of table special treatment
    #   ---------------------------------------------------------------
    def emit(self, text, tab_state=CELL_TEXT, span=1):
        """
        Hand over all text but tables and birthday-record lines to self._backend.write()
        In case of tables pass to specal treatment below.
        _    gramps serves tables column by column
        _    whereas LaTeX builds them row by row.
        """
        if not self.in_table:  # all stuff but table
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
            self.curcol_char = get_charform(self.curcol - 1)
            if span > 1:  # phantom columns prior to multicolumns
                for col in range(self.curcol - span, self.curcol - 1):
                    col_char = get_charform(col)
                    phantom = TabCell(col_char, 0, "", "")
                    self.tabrow.cells.append(phantom)
            self.tabcell = TabCell(self.curcol_char, span, text, "")
        elif tab_state == CELL_TEXT:
            self.textmem.append(text)
        elif tab_state == CELL_END:  # text == ''
            self.tabcell.content = "".join(self.textmem).strip()

            if self.tabcell.content.find("\\centering") != -1:
                self.tabcell.content = self.tabcell.content.replace("\\centering", "")
                self.tabcell.head = re.sub(TBLFMT_PAT, "\\1c\\2", self.tabcell.head)
            self.tabrow.cells.append(self.tabcell)
            self.textmem = []
        elif tab_state == ROW_BEG:
            self.tabrow = TabRow()
            self.row_styles = set()
        elif tab_state == ROW_END:
            self.tabrow.addit = text  # text: \\hline, \\cline{}
            self.tabrow.tail = "".join(self.textmem)  # \\\\ row-termination
            if self.in_multrow_cell:  #   cols of rows: convert to rows of cols
                self.repack_row()
            else:
                self.tabmem.rows.append(self.tabrow)
        elif tab_state == TAB_BEG:  # text: \\begin{longtable}[l]{
            self._backend.write(
                "".join(("\\grinittab{\\textwidth}{", repr(1.0 / self.numcols), "}%\n"))
            )
            self.tabmem = TabMem(text)
        elif tab_state == TAB_END:  # text: \\end{longtable}
            self.tabmem.tail = text

            # table completed, calc widths and write out
            self.calc_latex_widths()
            self.write_table()

    def repack_row(self) -> None:
        """
        Transpose contents contained in a row of cols of cells
        to rows of cells with corresponding contents.
        Cols of the mult-row-cell are ended by SEPARATION_PAT
        """
        # if last col empty: delete
        if self.tabrow.cells[-1].content == "":
            del self.tabrow.cells[-1]
            self.numcols -= 1

        # a short row (e.g. the last row of a gallery) gets empty cells
        for col_num in range(len(self.tabrow.cells), self.numcols):
            self.tabrow.cells.append(
                TabCell(get_charform(col_num), 1, "\\multicolumn{1}{l}", "")
            )

        # extract cell.contents; joining the lines must not let a
        # "%" comment out the rest of the cell
        bare_contents = [
            (cell.content + "\n")
            .replace("%\n", "")
            .replace("\n", "")
            .strip(SEPARATION_PAT)
            .split(SEPARATION_PAT)
            for cell in self.tabrow.cells
        ]

        # mk equal length & transpose
        num_new_rows = max([len(mult_row_cont) for mult_row_cont in bare_contents])
        cols_equ_len = []
        for mrc in bare_contents:
            for i in range(num_new_rows - len(mrc)):
                mrc.append("")
            cols_equ_len.append(mrc)
        transp_cont = list(zip(*cols_equ_len))

        # picts? extract, together with all lines of their caption
        last_cell = self.numcols
        if self.pict_in_table:
            if transp_cont[0][-1].startswith("\\grmkpicture"):
                self.pict = pict_with_caption(
                    transp_cont[0][-1], [cont[-1] for cont in transp_cont[1:]]
                )
                last_cell -= 1
                self.numcols -= 1
                self._backend.write(
                    "".join(
                        (
                            "\\addtolength{\\grtabwidth}{-",
                            repr(pict_width_of(self.pict)),
                            "\\grbaseindent -2\\tabcolsep}%\n",
                        )
                    )
                )
                # drop the rows that only held the caption
                while num_new_rows > 1 and not any(
                    transp_cont[num_new_rows - 1][:last_cell]
                ):
                    num_new_rows -= 1
            self.pict_in_table = False

        # new row-col structure
        keep_together = bool(self.row_styles & KEEP_TOGETHER_STYLES)
        for row in range(num_new_rows):
            new_row = TabRow()
            for i in range(last_cell):
                new_cell = TabCell(
                    get_charform(i),
                    self.tabrow.cells[i].span,
                    self.tabrow.cells[i].head,
                    transp_cont[row][i],
                )
                new_row.cells.append(new_cell)
            if keep_together and row < num_new_rows - 1:
                new_row.tail = NO_PAGE_BREAK + " "
            else:
                new_row.tail = self.tabrow.tail
            self.tabmem.rows.append(new_row)

        # a heading is kept on one page with the row following it
        if self.row_styles & HEADING_STYLES:
            self.tabmem.rows[-1].tail = NO_PAGE_BREAK + " "
        self.tabmem.rows[-1].addit = self.tabrow.addit
        self.in_multrow_cell = False

    def calc_latex_widths(self):
        """
        Control width settings in latex table construction.
        Evaluations are set up here and passed to LaTeX to calculate
        required and to fix suitable widths.
        """
        tabcol_chars = []
        for col_num in range(self.numcols):
            col_char = get_charform(col_num)
            tabcol_chars.append(col_char)
            for row in self.tabmem.rows:
                if col_num >= len(row.cells):
                    continue
                cell = row.cells[col_num]
                if cell.span == 0:
                    continue
                if cell.content.startswith("\\grmkpicture"):
                    self._backend.write(
                        "".join(
                            (
                                "\\setlength{\\grpictsize}{\\minof{",
                                repr(pict_width_of(cell.content)),
                                "\\grbaseindent}{\\grprorated - 2\\tabcolsep}}%\n",
                            )
                        )
                    )
                else:
                    for part in cell.content.split(SEPARATION_PAT):
                        self._backend.write(
                            "".join(("\\grtextneedwidth{", part, "}%\n"))
                        )
                    row.cells[col_num].content = cell.content.replace(
                        SEPARATION_PAT, "~\\newline \n"
                    )
                if cell.span == 1:
                    self._backend.write("".join(("\\grsetreqfull%\n")))
                elif cell.span > 1:
                    self._backend.write(
                        "".join(
                            (
                                "\\grsetreqpart{\\grcolbeg",
                                get_charform(get_numform(cell.colchar) - cell.span + 1),
                                "}%\n",
                            )
                        )
                    )
            self._backend.write(
                "".join(
                    (
                        "\\grcolsfirstfix",
                        " {\\grcolbeg",
                        col_char,
                        "}{\\grtempwidth",
                        col_char,
                        "}{\\grfinalwidth",
                        col_char,
                        "}{\\grpictreq",
                        col_char,
                        "}{\\grtextreq",
                        col_char,
                        "}%\n",
                    )
                )
            )
        self._backend.write("".join(("\\grdividelength%\n")))
        for col_char in tabcol_chars:
            self._backend.write(
                "".join(
                    (
                        "\\grcolssecondfix",
                        " {\\grcolbeg",
                        col_char,
                        "}{\\grtempwidth",
                        col_char,
                        "}{\\grfinalwidth",
                        col_char,
                        "}{\\grpictreq",
                        col_char,
                        "}%\n",
                    )
                )
            )
        self._backend.write("".join(("\\grdividelength%\n")))
        for col_char in tabcol_chars:
            self._backend.write(
                "".join(
                    (
                        "\\grcolsthirdfix",
                        " {\\grcolbeg",
                        col_char,
                        "}{\\grtempwidth",
                        col_char,
                        "}{\\grfinalwidth",
                        col_char,
                        "}%\n",
                    )
                )
            )
        self._backend.write("".join(("\\grdividelength%\n")))
        for col_char in tabcol_chars:
            self._backend.write(
                "".join(
                    (
                        "\\grcolsfourthfix",
                        " {\\grcolbeg",
                        col_char,
                        "}{\\grtempwidth",
                        col_char,
                        "}{\\grfinalwidth",
                        col_char,
                        "}%\n",
                    )
                )
            )
        self.multcol_alph_counter = str_incr(MULTCOL_COUNT_BASE)
        for row in self.tabmem.rows:
            for cell in row.cells:
                if cell.span > 1:
                    multcol_alph_id = next(self.multcol_alph_counter)
                    self._backend.write(
                        "".join(
                            (
                                "\\grgetspanwidth{",
                                "\\grspanwidth",
                                multcol_alph_id,
                                "}{\\grcolbeg",
                                get_charform(get_numform(cell.colchar) - cell.span + 1),
                                "}{\\grcolbeg",
                                cell.colchar,
                                "}{\\grtempwidth",
                                cell.colchar,
                                "}%\n",
                            )
                        )
                    )

    def write_table(self):
        # Choosing RaggedRight (with hyphenation) in table and
        # provide manually adjusting of column widths
        self._backend.write(
            "".join(
                (
                    "%\n",
                    self.pict,
                    "%\n%\n",
                    "%  ==> Comment out one of the two lines ",
                    'by a leading "%" (first position)\n',
                    "{ \\RaggedRight%      left align with hyphenation in table \n",
                    "%{%                no left align in table \n%\n",
                    "%  ==>  You may add pos or neg values ",
                    "to the following ",
                    repr(self.numcols),
                    " column widths %\n",
                )
            )
        )
        for col_num in range(self.numcols):
            self._backend.write(
                "".join(
                    (
                        "\\addtolength{\\grtempwidth",
                        get_charform(col_num),
                        "}{+0.0cm}%\n",
                    )
                )
            )
        self._backend.write("%  === %\n")

        # adjust & open table':
        if self.pict:
            self._backend.write(
                "".join(
                    (
                        "%\n\\vspace{\\grtabprepos}%\n",
                        "\\setlength{\\grtabprepos}{0ex}%\n",
                    )
                )
            )
            self.pict = ""
        self._backend.write("".join(self.tabmem.head))

        # special treatment at begin of longtable for heading and
        # closing at top and bottom of the table
        # and parts of it at pagebreak separating
        self.multcol_alph_counter = str_incr(MULTCOL_COUNT_BASE)
        splitting_row = self.mk_splitting_row(self.tabmem.rows[FIRST_ROW])
        self.multcol_alph_counter = str_incr(MULTCOL_COUNT_BASE)
        complete_row = self.mk_complete_row(self.tabmem.rows[FIRST_ROW], None)

        self._backend.write(splitting_row)
        self._backend.write("\\endhead%\n")
        self._backend.write(splitting_row.replace("{+2ex}", "{-2ex}"))
        self._backend.write("\\endfoot%\n")
        if self.head_line:
            self._backend.write("\\hline%\n")
            self.head_line = False
        else:
            self._backend.write("%\n")
        self._backend.write(complete_row)
        self._backend.write("\\endfirsthead%\n")
        self._backend.write("\\endlastfoot%\n")

        # hand over subsequent rows
        for row in self.tabmem.rows[SUBSEQ_ROW:]:
            self._backend.write(self.mk_complete_row(row, None))

        # close table by '\\end{longtable}', end '{\\RaggedRight' or '{' by '}'
        self._backend.write("".join(("".join(self.tabmem.tail), "}%\n\n")))

    def mk_splitting_row(self, row):
        splitting = []
        add_vdots = "\\grempty"
        for cell in row.cells:
            if cell.span == 0:
                continue
            if not splitting and get_numform(cell.colchar) == self.numcols - 1:
                add_vdots = "\\graddvdots"
            if cell.span == 1:
                cell_width = "".join(("\\grtempwidth", cell.colchar))
            else:
                cell_width = "".join(("\\grspanwidth", next(self.multcol_alph_counter)))
            splitting.append(
                "".join(
                    (
                        "\\grtabpgbreak{",
                        cell.head,
                        "}{",
                        cell_width,
                        "}{",
                        add_vdots,
                        "}{+2ex}%\n",
                    )
                )
            )
        return "".join((" & ".join(splitting), "%\n", row.tail))

    def mk_complete_row(self, row, last=None):
        #    last:  '-1' for [:-1] or
        #           'None' for all i.e. [:]
        """collocate all data of a latex row and write out"""
        complete = []
        for cell in row.cells[:last]:
            if cell.span == 0:
                continue
            elif cell.span == 1:
                cell_width = "".join(("\\grtempwidth", cell.colchar))
            else:
                cell_width = "".join(("\\grspanwidth", next(self.multcol_alph_counter)))
            complete.append(
                "".join(
                    (
                        "\\grcolpart{%\n  ",
                        cell.head,
                        "}{%\n",
                        cell_width,
                        "}{%\n  ",
                        cell.content.replace("\\grmkpicture{", "\\grcellpicture{"),
                        "%\n}%\n",
                    )
                )
            )
        return "".join((" & ".join(complete), "%\n", row.tail, row.addit))

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
        "Forces a page break, creating a new page"
        self.emit("\\newpage%\n")

    def open(self, filename):
        """Opens the specified file, making sure that it has the
        extension of .tex"""
        self._backend = LaTeXBackend(filename)
        self._backend.open()

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
            options += "," + paper_name + "paper"

        # Old:
        # Paper selections are somewhat limited on a stock installation.
        # Use the article template, T1 font encodings, and specify
        # that we should use Latin1 and unicode character encodings.
        self.emit(_LATEX_TEMPLATE_1 % options)
        self.emit(_LATEX_TEMPLATE)
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
            if align == "center":
                thisstyle.font_beg += "{\\centering"
                thisstyle.font_end = "".join(("\n\n}", thisstyle.font_end))
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
            self.emit("\\end{list}\n")
        self.emit("\\end{document}\n")
        self._backend.close()

    def end_page(self):
        """Issue a new page command"""
        self.emit("\\newpage")

    def start_paragraph(self, style_name, leader=None):
        """Paragraphs handling - A Gramps paragraph is any
        single body of text from a single word to several sentences.
        We assume a linebreak at the end of each paragraph.
        """
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_paragraph_style(style_name)
        ltxstyle = self.latexstyle[style_name]
        self.level = style.get_header_level()

        self.fbeg = ltxstyle.font_beg
        self.fend = ltxstyle.font_end

        self.indent = ltxstyle.left_indent
        self.first_line_indent = ltxstyle.first_line_indent
        if self.indent == 0:
            self.indent = self.first_line_indent

        # For additional vertical space beneath title line(s)
        # i.e. when the first centering ended:
        if self.in_title and ltxstyle.font_beg.find("centering") == -1:
            self.in_title = False
            self._backend.write("\\vspace{5ex}%\n")
        if self.in_table:  #   paragraph in table indicates: cols of rows
            self.in_multrow_cell = True
            self.row_styles.add(style_name)
        else:
            if leader:
                self._backend.write("".join(("\\grprepleader{", leader, "}%\n")))
            else:
                self._backend.write("\\grprepnoleader%\n")

            #           -------------------------------------------------------------------
            #   Gramps presumes 'cm' as units; here '\\grbaseindent' is used
            #   as equivalent, set in '_LATEX_TEMPLATE' above to '2.85em';
            #   there another value might be choosen.
            #           -------------------------------------------------------------------
            if self.indent is not None:
                self._backend.write(
                    "".join(
                        (
                            "\\grminpghead{",
                            repr(self.indent),
                            "}{",
                            repr(self.pict_width),
                            "}%\n",
                        )
                    )
                )
                self.fix_indent = True
                if leader is not None and not self.in_list:
                    self.in_list = True
                    self._backend.write("".join(("\\grlisthead{", leader, "}%\n")))

        if leader is None:
            self.emit("\n")
            self.emit("%s " % self.fbeg)

    def end_paragraph(self):
        """End the current paragraph"""
        newline = "%\n\n"
        if self.in_list:
            self.in_list = False
            self.emit("\n\\grlisttail%\n")
            newline = ""
        elif self.in_table:
            newline = SEPARATION_PAT

        self.emit("%s%s" % (self.fend, newline))
        if self.fix_indent:
            self.emit("\\grminpgtail%\n\n")
            self.fix_indent = False

        if self.pict_width:
            self.pict_width = 0
            self.pict_height = 0

    def start_bold(self):
        """Bold face"""
        self.emit("\\textbf{")

    def end_bold(self):
        """End bold face"""
        self.emit("}")

    def start_superscript(self):
        self.emit("\\textsuperscript{")

    def end_superscript(self):
        self.emit("}")

    # ---------------------------------------------------------------------
    #
    # Methods for table construction; values are supplied.
    # For new LaTeX output some former settings are ignored.
    #
    # ---------------------------------------------------------------------

    def start_table(self, name, style_name):
        """Begin new table"""
        self.in_table = True
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

        tblfmt = "*{%d}{l}" % self.numcols
        self.emit("\\begin{longtable}[l]{%s}\n" % (tblfmt), TAB_BEG)

    def end_table(self):
        """Close the table environment"""
        self.emit("%\n\\end{longtable}%\n", TAB_END)
        self.in_table = False

    def start_row(self):
        """Begin a new row"""
        self.emit("", ROW_BEG)
        # doline/skipfirst are flags for adding hor. rules
        self.doline = False
        self.skipfirst = False
        self.curcol = 0
        self.currow += 1

    def end_row(self):
        """End the row (new line)"""
        self.emit("\\\\ ")
        if self.doline:
            if self.skipfirst:
                self.emit("".join((("\\cline{2-%d}" % self.numcols), "%\n")), ROW_END)
            else:
                self.emit("\\hline %\n", ROW_END)
        else:
            self.emit("%\n", ROW_END)
        self.emit("%\n")

    def start_cell(self, style_name, span=1):
        """Add an entry to the table.
        We always place our data inside braces
        for safety of formatting."""
        self.colspan = span
        self.curcol += self.colspan
        styles = self.get_style_sheet()
        self.cstyle = styles.get_cell_style(style_name)

        #       ------------------------------------------------------------------
        # begin special modification for boolean values
        # values imported here are used for test '==1' and '!=0'. To get
        # local boolean values the tests are now transfered to the import lines
        #       ------------------------------------------------------------------
        self.lborder = self.cstyle.get_left_border() == 1
        self.rborder = self.cstyle.get_right_border() == 1
        self.bborder = self.cstyle.get_bottom_border() == 1
        self.tborder = self.cstyle.get_top_border() != 0
        cellfmt = "l"

        # Account for vertical rules
        if self.lborder:
            cellfmt = "|" + cellfmt
        if self.rborder:
            cellfmt = cellfmt + "|"

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

        self.emit("\\multicolumn{%d}{%s}" % (span, cellfmt), CELL_BEG, span)

    def end_cell(self):
        """Prepares for next cell"""
        self.emit("", CELL_END)

    def media_error(self, infile: str, reason: str) -> None:
        """
        Note a picture that cannot be included, as a LaTeX comment.

        The comment is written straight to the backend, so that it never ends
        up inside a table cell, where it would comment out the rest of the
        cell when the cell content is joined into a single line.
        """
        _LOG.warning("LaTeX: cannot include %s: %s", infile, reason)
        self._backend.write(
            "".join(
                ("%\n% *** Error: cannot include ", infile, "\n% *** ", reason, "\n")
            )
        )

    def derived_image_name(
        self, infile: str, crop: tuple[int, int, int, int] | None, ext: str
    ) -> str:
        """
        Return the name of an image derived from infile (cropped or
        converted), placed beside the LaTeX file. The name depends on the
        source and the crop, so that different derived images never share
        a file, and the user's media files are never overwritten.
        """
        key = "".join((os.path.abspath(infile), repr(crop))).encode("utf-8")
        name = "".join(
            (
                "temp_",
                os.path.splitext(os.path.basename(infile))[0],
                "_",
                hashlib.md5(key).hexdigest()[:8],
                ext,
            )
        )
        outdir = os.path.dirname(os.path.abspath(self._backend.getf()))
        return os.path.join(outdir, name)

    def warn_no_pil(self) -> None:
        """
        Tell the user once that pictures cannot be cropped or converted.
        """
        from gramps.gen.config import config

        if not config.get("interface.ignore-pil"):
            from gramps.gen.constfunc import has_display

            if has_display() and self.uistate:
                from gramps.gui.dialog import MessageHideDialog

                title = _("PIL (Python Imaging Library) not loaded.")
                message = _(
                    "Production of jpg images from non-jpg images "
                    "in LaTeX documents will not be available. "
                    "Use your package manager to install "
                    "python-imaging or python-pillow or "
                    "python3-pillow"
                )
                MessageHideDialog(
                    title,
                    message,
                    "interface.ignore-pil",
                    parent=self.uistate.window,
                )

    def add_media(self, infile, pos, x, y, alt="", style_name=None, crop=None):
        """Add photo to report"""
        base, ext = os.path.splitext(infile)
        outfile = infile
        if HAVE_PIL:
            try:
                with Image.open(infile) as curr_img:
                    if crop:
                        curr_img = curr_img.crop(
                            tuple(crop_percentage_to_pixel(*curr_img.size, crop))
                        )
                        if curr_img.mode not in ("1", "L", "LA", "P", "RGB", "RGBA"):
                            curr_img = curr_img.convert("RGB")
                        outfile = self.derived_image_name(infile, crop, ".png")
                        curr_img.save(outfile)
                    elif ext.lower() not in LATEX_IMAGE_EXTS:
                        outfile = self.derived_image_name(infile, None, ".jpg")
                        curr_img.convert("RGB").save(outfile)
                    width, height = curr_img.size
                    if height > width:
                        y = y * height / width
            except (IOError, ValueError) as err:
                self.media_error(infile, str(err))
                return
        elif ext.lower() not in LATEX_IMAGE_EXTS:
            self.warn_no_pil()
            self.media_error(infile, "PIL not installed")
            return
        elif crop:
            # include the whole picture rather than none of it
            self.warn_no_pil()
            _LOG.warning("LaTeX: cannot crop %s: PIL not installed", infile)

        if self.in_table:
            self.pict_in_table = True
            # the report writes its own caption into the table cell
            pictname = ""
        else:
            pictname = latexescape(os.path.basename(base))

        self.emit(
            "".join(
                (
                    "\\grmkpicture{",
                    outfile,
                    "}{",
                    repr(x),
                    "}{",
                    repr(y),
                    "}{",
                    pictname,
                    "}%\n",
                )
            )
        )
        if not self.in_table:
            # the next paragraph is set beside the picture
            self.pict_width = x
            self.pict_height = y

    def write_text(self, text, mark=None, links=False):
        """Write the text to the file"""
        if text == "\n":
            text = ""
        text = latexescape(text)
        if links is True:
            text = re.sub(URL_PATTERN, _CLICKABLE, text)

        # hard coded replace of the underline used for missing names/data
        text = text.replace("\\_" * 13, "\\underline{\\hspace{3\\grbaseindent}}")
        self.emit(text + " ")

    def write_styled_note(
        self, styledtext, format, style_name, contains_html=False, links=False
    ):
        """
        Convenience function to write a styledtext to the latex doc.
        styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
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
        if format:
            # preformatted, use different escape function
            self._backend.setescape(True)

        markuptext = self._backend.add_markup_from_styled(text, s_tags)

        if links is True:
            markuptext = re.sub(URL_PATTERN, _CLICKABLE, markuptext)
        markuptext = self._backend.add_markup_from_styled(text, s_tags)

        # there is a problem if we write out a note in a table.
        # ..................
        # now solved by postprocessing in self.calc_latex_widths()
        # by explicitely setting suitable width for all columns.
        #
        if format:
            self.start_paragraph(style_name)
            self.emit(markuptext)
            self.end_paragraph()
            # preformatted finished, go back to normal escape function
            self._backend.setescape(False)
        else:
            for line in markuptext.split("%\n%\n "):
                self.start_paragraph(style_name)
                for realline in line.split("\n"):
                    self.emit(realline)
                    self.emit("~\\newline \n")
                self.end_paragraph()
