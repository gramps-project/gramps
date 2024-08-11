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


# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".paperstyle")

# -------------------------------------------------------------------------
#
# Page orientation
#
# -------------------------------------------------------------------------
PAPER_PORTRAIT = 0
PAPER_LANDSCAPE = 1


# ------------------------------------------------------------------------
#
# PaperSize
#
# ------------------------------------------------------------------------
class PaperSize:
    """
    Defines the dimensions of a sheet of paper. All dimensions are in
    centimeters.
    """

    def __init__(self, name, height, width):
        """
        Create a new paper style with.

        :param name: name of the new style
        :param height: page height in centimeters
        :param width: page width in centimeters
        """
        self.name = name
        self.height = height
        self.width = width
        if self.name == "Letter":
            self.trans_pname = _("Letter", "paper size")
        elif self.name == "Legal":
            self.trans_pname = _("Legal", "paper size")
        elif self.name == "Custom Size":
            self.trans_pname = _("Custom Size")
        else:
            self.trans_pname = None

    def get_name(self):
        "Return the name of the paper style"
        return self.name

    def get_height(self):
        "Return the page height in cm"
        return self.height

    def set_height(self, height):
        "Set the page height in cm"
        self.height = height

    def get_width(self):
        "Return the page width in cm"
        return self.width

    def set_width(self, width):
        "Set the page width in cm"
        self.width = width

    def get_height_inches(self):
        "Return the page height in inches"
        return self.height / 2.54

    def get_width_inches(self):
        "Return the page width in inches"
        return self.width / 2.54


# ------------------------------------------------------------------------
#
# PaperStyle
#
# ------------------------------------------------------------------------
class PaperStyle:
    """
    Define the various options for a sheet of paper.
    """

    def __init__(
        self, size, orientation, lmargin=2.54, rmargin=2.54, tmargin=2.54, bmargin=2.54
    ):
        """
        Create a new paper style.

        :param size: size of the new style
        :type size: :class:`.PaperSize`
        :param orientation: page orientation
        :type orientation: PAPER_PORTRAIT or PAPER_LANDSCAPE

        """
        self.__orientation = orientation

        if orientation == PAPER_PORTRAIT:
            self.__size = PaperSize(
                size.get_name(), size.get_height(), size.get_width()
            )
        else:
            self.__size = PaperSize(
                size.get_name(), size.get_width(), size.get_height()
            )
        self.__lmargin = lmargin
        self.__rmargin = rmargin
        self.__tmargin = tmargin
        self.__bmargin = bmargin

    def get_size(self):
        """
        Return the size of the paper.

        :returns: object indicating the paper size
        :rtype: :class:`.PaperSize`

        """
        return self.__size

    def get_orientation(self):
        """
        Return the orientation of the page.

        :returns: PAPER_PORTRIAT or PAPER_LANDSCAPE
        :rtype: int

        """
        return self.__orientation

    def get_usable_width(self):
        """
        Return the width of the page area in centimeters.

        The value is the page width less the margins.

        """
        return self.__size.get_width() - (self.__rmargin + self.__lmargin)

    def get_usable_height(self):
        """
        Return the height of the page area in centimeters.

        The value is the page height less the margins.

        """
        return self.__size.get_height() - (self.__tmargin + self.__bmargin)

    def get_right_margin(self):
        """
        Return the right margin.

        :returns: Right margin in centimeters
        :rtype: float

        """
        return self.__rmargin

    def get_left_margin(self):
        """
        Return the left margin.

        :returns: Left margin in centimeters
        :rtype: float

        """
        return self.__lmargin

    def get_top_margin(self):
        """
        Return the top margin.

        :returns: Top margin in centimeters
        :rtype: float

        """
        return self.__tmargin

    def get_bottom_margin(self):
        """
        Return the bottom margin.

        :returns: Bottom margin in centimeters
        :rtype: float

        """
        return self.__bmargin
