# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011-2012       Serge Noiraud
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

# $Id$

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
import gobject
import operator
from math import *

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("maps.messagelayer")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Cairo

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import const

#-------------------------------------------------------------------------
#
# osmGpsMap
#
#-------------------------------------------------------------------------

try:
    import osmgpsmap
except:
    raise

class MessageLayer(gobject.GObject, osmgpsmap.GpsMapLayer):
    """
    This is the layer used to display messages over the map
    """
    def __init__(self):
        """
        Initialize the layer
        """
        gobject.GObject.__init__(self)
        self.message = []
        self.color = "black"
        self.font = "Arial"
        self.size = 18
        #families = font_map.list_families()

    def clear_messages(self):
        """
        reset the layer attributes.
        """
        self.message = []

    def clear_font_attributes(self):
        """
        reset the font attributes.
        """
        self.color = "black"
        self.font = "Arial"
        self.size = 18

    def set_font_attributes(self, font, size, color):
        """
        Set the font color, size and name
        """
        if color is not None:
            self.color = color
        if font is not None:
            self.font = font
        if size is not None:
            self.size = size

    def add_message(self, message):
        """
        Add a message
        """
        self.message.append(message)

    def do_draw(self, gpsmap, drawable):
        """
        Draw the two extreme dates
        """
        ctx = drawable.cairo_create()
        ctx.select_font_face(self.font,
                             cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(int(self.size))
        color = Gdk.color_parse(self.color)
        ctx.set_source_rgba(float(color.red / 65535.0),
                            float(color.green / 65535.0),
                            float(color.blue / 65535.0),
                            0.9) # transparency
        coord_x = 100
        coord_y = int(self.size) # Show the first line under the zoom button
        (d_width, d_height) = drawable.get_size()
        d_width -= 100
        for line in self.message:
            line_to_print = line
            (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents(line_to_print)
            while ( width > d_width):
                line_length = len(line_to_print)
                character_length = int(width/line_length) + 1
                max_length = int(d_width / character_length) - 5
                ctx.move_to(coord_x, coord_y)
                ctx.show_text(line_to_print[:max_length])
                line_to_print = line_to_print[max_length:]
                (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents(line_to_print)
                coord_y += int(self.size) # calculate the next line position
            ctx.move_to(coord_x, coord_y)
            ctx.show_text(line_to_print)
            coord_y += int(self.size) # calculate the next line position

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

gobject.type_register(MessageLayer)

