#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2002       Gary Shao
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009       Gary Burton
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

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .fontstyle import FontStyle

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".paragraphstyle")

#-------------------------------------------------------------------------
#
# Paragraph alignment
#
#-------------------------------------------------------------------------
PARA_ALIGN_CENTER = 0
PARA_ALIGN_LEFT = 1
PARA_ALIGN_RIGHT = 2
PARA_ALIGN_JUSTIFY = 3

#------------------------------------------------------------------------
#
# ParagraphStyle
#
#------------------------------------------------------------------------
class ParagraphStyle:
    """
    Defines the characteristics of a paragraph. The characteristics are:
    font (a :class:`.FontStyle` instance), right margin, left margin,
    first indent, top margin, bottom margin, alignment, level, top border,
    bottom border, right border, left border, padding, and background color.

    """
    def __init__(self, source=None):
        """
        :param source: if not None, then the ParagraphStyle is created using the
                       values of the source instead of the default values.
        """
        if source:
            self.font = FontStyle(source.font)
            self.rmargin = source.rmargin
            self.lmargin = source.lmargin
            self.first_indent = source.first_indent
            self.tmargin = source.tmargin
            self.bmargin = source.bmargin
            self.align = source.align
            self.level = source.level
            self.top_border = source.top_border
            self.bottom_border = source.bottom_border
            self.right_border = source.right_border
            self.left_border = source.left_border
            self.pad = source.pad
            self.bgcolor = source.bgcolor
            self.description = source.description
            self.tabs = source.tabs
        else:
            self.font = FontStyle()
            self.rmargin = 0
            self.lmargin = 0
            self.tmargin = 0
            self.bmargin = 0
            self.first_indent = 0
            self.align = PARA_ALIGN_LEFT
            self.level = 0
            self.top_border = 0
            self.bottom_border = 0
            self.right_border = 0
            self.left_border = 0
            self.pad = 0
            self.bgcolor = (255, 255, 255)
            self.description = ""
            self.tabs = []

    def set_description(self, text):
        """
        Set the description of the paragraph
        """
        self.description = text

    def get_description(self):
        """
        Return the description of the paragraph
        """
        return self.description

    def set(self, rmargin=None, lmargin=None, first_indent=None,
            tmargin=None, bmargin=None, align=None,
            tborder=None, bborder=None, rborder=None, lborder=None,
            pad=None, bgcolor=None, font=None):
        """
        Allows the values of the object to be set.

        :param rmargin: right indent in centimeters
        :param lmargin: left indent in centimeters
        :param first_indent: first line indent in centimeters
        :param tmargin: space above paragraph in centimeters
        :param bmargin: space below paragraph in centimeters
        :param align: alignment type (PARA_ALIGN_LEFT, PARA_ALIGN_RIGHT, PARA_ALIGN_CENTER, or PARA_ALIGN_JUSTIFY)
        :param tborder: non zero indicates that a top border should be used
        :param bborder: non zero indicates that a bottom border should be used
        :param rborder: non zero indicates that a right border should be used
        :param lborder: non zero indicates that a left border should be used
        :param pad: padding in centimeters
        :param bgcolor: background color of the paragraph as an RGB tuple.
        :param font: FontStyle instance that defines the font
        """
        if font is not None:
            self.font = FontStyle(font)
        if pad is not None:
            self.set_padding(pad)
        if tborder is not None:
            self.set_top_border(tborder)
        if bborder is not None:
            self.set_bottom_border(bborder)
        if rborder is not None:
            self.set_right_border(rborder)
        if lborder is not None:
            self.set_left_border(lborder)
        if bgcolor is not None:
            self.set_background_color(bgcolor)
        if align is not None:
            self.set_alignment(align)
        if rmargin is not None:
            self.set_right_margin(rmargin)
        if lmargin is not None:
            self.set_left_margin(lmargin)
        if first_indent is not None:
            self.set_first_indent(first_indent)
        if tmargin is not None:
            self.set_top_margin(tmargin)
        if bmargin is not None:
            self.set_bottom_margin(bmargin)

    def set_header_level(self, level):
        """
        Set the header level for the paragraph. This is useful for
        numbered paragraphs. A value of 1 indicates a header level
        format of X, a value of two implies X.X, etc. A value of zero
        means no header level.
        """
        self.level = level

    def get_header_level(self):
        "Return the header level of the paragraph"
        return self.level

    def set_font(self, font):
        """
        Set the font style of the paragraph.

        :param font: :class:`.FontStyle` object containing the font definition
                     to use.
        """
        self.font = FontStyle(font)

    def get_font(self):
        "Return the :class:`.FontStyle` of the paragraph"
        return self.font

    def set_padding(self, val):
        """
        Set the paragraph padding in centimeters

        :param val: floating point value indicating the padding in centimeters
        """
        self.pad = val

    def get_padding(self):
        """Return a the padding of the paragraph"""
        return self.pad

    def set_top_border(self, val):
        """
        Set the presence or absence of top border.

        :param val: True indicates a border should be used, False indicates
                    no border.
        """
        self.top_border = val

    def get_top_border(self):
        "Return 1 if a top border is specified"
        return self.top_border

    def set_bottom_border(self, val):
        """
        Set the presence or absence of bottom border.

        :param val: True indicates a border should be used, False
                    indicates no border.
        """
        self.bottom_border = val

    def get_bottom_border(self):
        "Return 1 if a bottom border is specified"
        return self.bottom_border

    def set_left_border(self, val):
        """
        Set the presence or absence of left border.

        :param val: True indicates a border should be used, False
                    indicates no border.
        """
        self.left_border = val

    def get_left_border(self):
        "Return 1 if a left border is specified"
        return self.left_border

    def set_right_border(self, val):
        """
        Set the presence or absence of rigth border.

        :param val: True indicates a border should be used, False
                    indicates no border.
        """
        self.right_border = val

    def get_right_border(self):
        "Return 1 if a right border is specified"
        return self.right_border

    def get_background_color(self):
        """
        Return a tuple indicating the RGB components of the background
        color
        """
        return self.bgcolor

    def set_background_color(self, color):
        """
        Set the background color of the paragraph.

        :param color: tuple representing the RGB components of a color
                      (0,0,0) to (255,255,255)
        """
        self.bgcolor = color

    def set_alignment(self, align):
        """
        Set the paragraph alignment.

        :param align: PARA_ALIGN_LEFT, PARA_ALIGN_RIGHT, PARA_ALIGN_CENTER,
                      or PARA_ALIGN_JUSTIFY
        """
        self.align = align

    def get_alignment(self):
        "Return the alignment of the paragraph"
        return self.align

    def get_alignment_text(self):
        """
        Return a text string representing the alignment, either 'left',
        'right', 'center', or 'justify'
        """
        if self.align == PARA_ALIGN_LEFT:
            return "left"
        elif self.align == PARA_ALIGN_CENTER:
            return "center"
        elif self.align == PARA_ALIGN_RIGHT:
            return "right"
        elif self.align == PARA_ALIGN_JUSTIFY:
            return "justify"
        return "unknown"

    def set_left_margin(self, value):
        "sets the left indent in centimeters"
        self.lmargin = value

    def set_right_margin(self, value):
        "sets the right indent in centimeters"
        self.rmargin = value

    def set_first_indent(self, value):
        "sets the first line indent in centimeters"
        self.first_indent = value

    def set_top_margin(self, value):
        "sets the space above paragraph in centimeters"
        self.tmargin = value

    def set_bottom_margin(self, value):
        "sets the space below paragraph in centimeters"
        self.bmargin = value

    def get_left_margin(self):
        "returns the left indent in centimeters"
        return self.lmargin

    def get_right_margin(self):
        "returns the right indent in centimeters"
        return self.rmargin

    def get_first_indent(self):
        "returns the first line indent in centimeters"
        return self.first_indent

    def get_top_margin(self):
        "returns the space above paragraph in centimeters"
        return self.tmargin

    def get_bottom_margin(self):
        "returns the space below paragraph in centimeters"
        return self.bmargin

    def set_tabs(self, tab_stops):
        assert isinstance(tab_stops, list)
        self.tabs = tab_stops

    def get_tabs(self):
        return self.tabs
