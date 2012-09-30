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
from math import pi
from gi.repository import GObject

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("maps.selectionlayer")

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# osmGpsMap
#
#-------------------------------------------------------------------------

try:
    from gi.repository import OsmGpsMap as osmgpsmap
except:
    raise

class SelectionLayer(GObject.GObject, osmgpsmap.MapLayer):
    def __init__(self):
        """
        Initialize thz selection layer
        """
        GObject.GObject.__init__(self)
        self.circles = []
        self.rectangles = []

    def add_circle(self, rds, lat, lon):
        """
        Add a circle
        """
        self.circles.append((rds, lat, lon))

    def add_rectangle(self, cp1, cp2):
        """
        Add a rectangle
        """
        self.rectangles.append((cp1, cp2))

    def do_draw(self, gpsmap, ctx):
        """
        draw the circles and the rectangles
        """
        for circle in self.circles:
            top_left = osmgpsmap.MapPoint.new_degrees(circle[1] + circle[0],
                                                   circle[2] - circle[0])
            bottom_right = osmgpsmap.MapPoint.new_degrees(circle[1] - circle[0],
                                                       circle[2] + circle[0])
            crd_x, crd_y = gpsmap.convert_geographic_to_screen(top_left)
            crd_x2, crd_y2 = gpsmap.convert_geographic_to_screen(bottom_right)
            width = float(crd_x2 - crd_x)
            height = float(crd_y2 - crd_y)
            ctx.set_line_width(3.0)
            ctx.set_source_rgba(0.0, 0.0, 0.0, 0.8)
            ctx.scale(1.0, (height/width))
            #ctx.arc(float(crd_x + crd_x2)/2, float(crd_y + crd_y2)/2, width, 0.0, 2*pi)
            # TODO : placement bug : waiting bug correction on osm-gps-map
            ctx.arc(float(crd_x + crd_x2)/2, float(crd_y+height*(height/width)/2), width, 0.0, 2*pi)
            ctx.stroke()

        for rectangle in self.rectangles:
            top_left, bottom_right = rectangle
            ctx.set_source_rgba(0.0, 0.0, 0.0, 0.8)
            ctx.set_line_width(3.0)
            crd_x, crd_y = gpsmap.convert_geographic_to_screen(top_left)
            crd_x2, crd_y2 = gpsmap.convert_geographic_to_screen(bottom_right)
            # be sure when can select a region in all case.
            if ( crd_x < crd_x2 ):
                if ( crd_y < crd_y2 ):
                    ctx.rectangle(crd_x, crd_y, crd_x2 - crd_x, crd_y2 - crd_y)
                else:
                    ctx.rectangle(crd_x, crd_y2, crd_x2 - crd_x, crd_y - crd_y2)
            else:
                if ( crd_y < crd_y2 ):
                    ctx.rectangle(crd_x2, crd_y, crd_x - crd_x2, crd_y2 - crd_y)
                else:
                    ctx.rectangle(crd_x2, crd_y2, crd_x - crd_x2, crd_y - crd_y2)
            ctx.stroke()

    def do_render(self, gpsmap):
        """
        render the layer
        """
        pass

    def do_busy(self):
        """
        set the map busy
        """
        return False

    def do_button_press(self, gpsmap, gdkeventbutton):
        """
        Someone press a button
        """
        return False

GObject.type_register(SelectionLayer)

