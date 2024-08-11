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

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".fontstyle")


# -------------------------------------------------------------------------
#
# constants
#
# -------------------------------------------------------------------------
FONT_SANS_SERIF = 0
FONT_SERIF = 1
FONT_MONOSPACE = 2


# ------------------------------------------------------------------------
#
# FontStyle
#
# ------------------------------------------------------------------------
class FontStyle:
    """
    Defines a font style. Controls the font face, size, color, and
    attributes. In order to remain generic, the only font faces available
    are FONT_SERIF and FONT_SANS_SERIF. Document formatters should convert
    these to the appropriate fonts for the target format.

    The FontStyle represents the desired characteristics. There are no
    guarentees that the document format generator will be able implement
    all or any of the characteristics.
    """

    def __init__(self, style=None):
        """
        Create a new FontStyle object, accepting the default values.

        :param style: if specified, initializes the FontStyle from the passed
                      FontStyle instead of using the defaults.
        """
        if style:
            self.face = style.face
            self.size = style.size
            self.italic = style.italic
            self.bold = style.bold
            self.color = style.color
            self.under = style.under
        else:
            self.face = FONT_SERIF
            self.size = 12
            self.italic = 0
            self.bold = 0
            self.color = (0, 0, 0)
            self.under = 0

    def set(
        self, face=None, size=None, italic=None, bold=None, underline=None, color=None
    ):
        """
        Set font characteristics.

        :param face: font type face, either FONT_SERIF or FONT_SANS_SERIF
        :param size: type face size in points
        :param italic: True enables italics, False disables italics
        :param bold: True enables bold face, False disables bold face
        :param underline: True enables underline, False disables underline
        :param color: an RGB color representation in the form of three integers
                      in the range of 0-255 represeting the red, green, and blue
                      components of a color.
        """
        if face is not None:
            self.set_type_face(face)
        if size is not None:
            self.set_size(size)
        if italic is not None:
            self.set_italic(italic)
        if bold is not None:
            self.set_bold(bold)
        if underline is not None:
            self.set_underline(underline)
        if color is not None:
            self.set_color(color)

    def set_italic(self, val):
        "0 disables italics, 1 enables italics"
        self.italic = val

    def get_italic(self):
        "1 indicates use italics"
        return self.italic

    def set_bold(self, val):
        "0 disables bold face, 1 enables bold face"
        self.bold = val

    def get_bold(self):
        "1 indicates use bold face"
        return self.bold

    def set_color(self, val):
        "sets the color using an RGB color tuple"
        self.color = val

    def get_color(self):
        "Return an RGB color tuple"
        return self.color

    def set_size(self, val):
        "sets font size in points"
        self.size = val

    def get_size(self):
        "returns font size in points"
        return self.size

    def set_type_face(self, val):
        "sets the font face type"
        self.face = val

    def get_type_face(self):
        "returns the font face type"
        return self.face

    def set_underline(self, val):
        "1 enables underlining"
        self.under = val

    def get_underline(self):
        "1 indicates underlining"
        return self.under
