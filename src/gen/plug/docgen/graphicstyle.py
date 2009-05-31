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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: basedoc.py 12591 2009-05-29 22:25:44Z bmcage $


#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------


#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------


#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".graphicstyle")

#-------------------------------------------------------------------------
#
# Line style
#
#-------------------------------------------------------------------------
SOLID  = 0
DASHED = 1

#------------------------------------------------------------------------
#
# GraphicsStyle
#
#------------------------------------------------------------------------
class GraphicsStyle(object):
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
        else:
            self.para_name = ""
            self.shadow = 0
            self.shadow_space = 0.2
            self.lwidth = 0.5
            self.color = (0, 0, 0)
            self.fill_color = (255, 255, 255)
            self.lstyle = SOLID

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
