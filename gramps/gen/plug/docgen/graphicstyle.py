#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2002       Gary Shao
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010       Jakim Friant
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

log = logging.getLogger(".graphicstyle")

# -------------------------------------------------------------------------
#
# Line style
#
# -------------------------------------------------------------------------
SOLID = 0
DASHED = 1
DOTTED = 2

# Notes about adding new line styles:
#   1) the first style is used when an invalid style is specified by the report
#   2) the style names are used by the ODF generator and should be unique
#   3) the line style constants above need to be imported in the
#      gen.plug.docgen.__init__ file so they can be used in a report add-on
line_style_names = ("solid", "dashed", "dotted")
_DASH_ARRAY = [[1, 0], [2, 4], [1, 2]]


def get_line_style_by_name(style_name):
    which = 0
    for idx, sn in enumerate(line_style_names):
        if sn == style_name:
            which = idx
            break
    return _DASH_ARRAY[which]


# ------------------------------------------------------------------------
#
# GraphicsStyle
#
# ------------------------------------------------------------------------
class GraphicsStyle:
    """
    Defines the properties of graphics objects, such as line width,
    color, fill, ect.
    """

    def __init__(self, obj=None):
        """
        Initialize the object with default values, unless a source
        object is specified. In that case, make a copy of the source
        object.
        """
        if obj:
            self.para_name = obj.para_name
            self.shadow = obj.shadow
            self.shadow_space = obj.shadow_space
            self.color = obj.color
            self.fill_color = obj.fill_color
            self.lwidth = obj.lwidth
            self.lstyle = obj.lstyle
            self.description = obj.description
        else:
            self.para_name = ""
            self.shadow = 0
            self.shadow_space = 0.2
            self.lwidth = 0.5
            self.color = (0, 0, 0)
            self.fill_color = (255, 255, 255)
            self.lstyle = SOLID
            self.description = ""

    def set_description(self, text):
        """
        Set the description of the graphics object
        """
        self.description = text

    def get_description(self):
        """
        Return the description of the graphics object
        """
        return self.description

    def set_line_width(self, val):
        """
        sets the line width
        """
        self.lwidth = val

    def get_line_width(self):
        """
        Return the name of the StyleSheet
        """
        return self.lwidth

    def get_line_style(self):
        return self.lstyle

    def set_line_style(self, val):
        self.lstyle = val

    def get_dash_style(self, val=None):
        if val is None:
            val = self.lstyle
        if val >= 0 and val < len(_DASH_ARRAY):
            return _DASH_ARRAY[val]
        else:
            return _DASH_ARRAY[0]

    def get_dash_style_name(self, val=None):
        if val is None:
            val = self.lstyle
        if val >= 0 and val < len(line_style_names):
            return line_style_names[val]
        else:
            return line_style_names[0]

    def set_paragraph_style(self, val):
        self.para_name = val

    def set_shadow(self, val, space=0.2):
        self.shadow = val
        self.shadow_space = space

    def get_shadow_space(self):
        return self.shadow_space

    def set_color(self, val):
        self.color = val

    def set_fill_color(self, val):
        self.fill_color = val

    def get_paragraph_style(self):
        return self.para_name

    def get_shadow(self):
        return self.shadow

    def get_color(self):
        return self.color

    def get_fill_color(self):
        return self.fill_color
