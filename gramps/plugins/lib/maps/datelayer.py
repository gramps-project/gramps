# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011-2016       Serge Noiraud
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
# Python modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("maps.datelayer")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
import cairo

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.config import config

#-------------------------------------------------------------------------
#
# osmGpsMap
#
#-------------------------------------------------------------------------

try:
    import gi
    gi.require_version('OsmGpsMap', '1.0')
    from gi.repository import OsmGpsMap as osmgpsmap
except:
    raise

# pylint: disable=unused-argument

class DateLayer(GObject.GObject, osmgpsmap.MapLayer):
    """
    This is the layer used to display the two extreme dates
    on the top left of the view
    """
    def __init__(self):
        """
        Initialize the layer
        """
        GObject.GObject.__init__(self)
        self.first = "    "
        self.last = "    "
        self.color = "black"
        self.font = config.get('utf8.selected-font')
        self.size = 36

    def clear_dates(self):
        """
        reset the layer attributes.
        """
        self.first = "    "
        self.last = "    "
        self.color = "black"
        self.font = config.get('utf8.selected-font')
        self.size = 36

    def set_font_attributes(self, font, size, color):
        """
        Set the font color, size and name
        """
        self.color = color
        if font:
            self.font = font
        else:
            self.font = config.get('utf8.selected-font')
        self.size = size

    def add_date(self, date):
        """
        Add a date
        """
        if date == "    " or date == "0000" or date == "9999":
            return
        if date < self.first or self.first == "    ":
            self.first = date
        if date > self.last or self.last == "    ":
            self.last = date

    def do_draw(self, gpsmap, ctx):
        """
        Draw the two extreme dates
        """
        ctx.select_font_face(self.font,
                             cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(int(self.size))
        color = Gdk.color_parse(self.color)
        ctx.set_source_rgba(float(color.red / 65535.0),
                            float(color.green / 65535.0),
                            float(color.blue / 65535.0),
                            0.6) # transparency
        coord_x = 10
        coord_y = 15 + 2*int(self.size) # Display the oldest date
        ctx.move_to(coord_x, coord_y)
        ctx.show_text(self.first)
        coord_y = 15 + 3*int(self.size) # Display the newest date
        ctx.move_to(coord_x, coord_y)
        ctx.show_text(self.last)

    def do_render(self, gpsmap):
        """
        render the layer
        """
        pass

    def do_busy(self):
        """
        set the layer busy
        """
        return False

    def do_button_press(self, gpsmap, gdkeventbutton):
        """
        When we press a button.
        """
        return False

GObject.type_register(DateLayer)

