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

# $Id: grampsmaps.py 18399 2011-11-02 17:15:20Z noirauds $

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
import gobject

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("maps.lifeway")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import const
import cairo

#-------------------------------------------------------------------------
#
# osmGpsMap
#
#-------------------------------------------------------------------------

try:
    import osmgpsmap
except:
    raise

class LifeWayLayer(gobject.GObject, osmgpsmap.GpsMapLayer):
    """
    This is the layer used to display tracks or the life way for one or several
    individuals.
    """
    def __init__(self):
        """
        Initialize the layer
        """
        gobject.GObject.__init__(self)
        self.lifeways = []
        self.lifeways_comment = []
        self.comments = []

    def clear_ways(self):
        """
        reset the layer attributes.
        """
        self.lifeways = []
        self.lifeways_comment = []
        self.comments = []

    def add_way(self, points, color):
        """
        Add a track or life way.
        """
        self.lifeways.append((points, color))

    def add_text(self, points, text):
        """
        Add a text to the track or life way.
        """
        self.lifeways_comment.append((points, text))

    def do_draw(self, gpsmap, drawable):
        """
        Draw all tracks or life ways.
        """
        for lifeway in self.lifeways:
            ctx = drawable.cairo_create()
            ctx.set_line_width(3.0)
            map_points = []
            for point in lifeway[0]:
                conv_pt = osmgpsmap.point_new_degrees(point[0], point[1])
                coord_x, coord_y = gpsmap.convert_geographic_to_screen(conv_pt)
                map_points.append((coord_x, coord_y))
            color = gtk.gdk.color_parse(lifeway[1])
            ctx.set_source_rgb(color.red / 65535,
                               color.green / 65535,
                               color.blue / 65535)
            first = True
            for idx_pt in range(0, len(map_points)):
                if first:
                    first = False
                    ctx.move_to(map_points[idx_pt][0], map_points[idx_pt][1])
                else:
                    ctx.line_to(map_points[idx_pt][0], map_points[idx_pt][1])
            ctx.stroke()

        for comment in self.lifeways_comment:
            ctx = drawable.cairo_create()
            ctx.set_line_width(3.0)
            ctx.select_font_face("Purisa",
                                 cairo.FONT_SLANT_NORMAL,
                                 cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(13)
            points = comment[0]
            conv_pt = osmgpsmap.point_new_degrees(points[0][0], points[0][1])
            coord_x, coord_y = gpsmap.convert_geographic_to_screen(conv_pt)
            ctx.move_to(coord_x, coord_y)
            ctx.show_text(comment[1])

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

gobject.type_register(LifeWayLayer)

