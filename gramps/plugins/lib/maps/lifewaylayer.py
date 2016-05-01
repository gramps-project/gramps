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
from math import pi

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
from gi.repository import Gdk
import cairo

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
    import gi
    gi.require_version('OsmGpsMap', '1.0')
    from gi.repository import OsmGpsMap as osmgpsmap
except:
    raise

# pylint: disable=unused-argument

class LifeWayLayer(GObject.GObject, osmgpsmap.MapLayer):
    """
    This is the layer used to display tracks or the life way for one or several
    individuals.
    """
    def __init__(self):
        """
        Initialize the layer
        """
        GObject.GObject.__init__(self)
        self.lifeways_ref = []
        self.lifeways = []
        self.comments = []

    def clear_ways(self):
        """
        reset the layer attributes.
        """
        self.lifeways_ref = []
        self.lifeways = []
        self.comments = []

    def add_way_ref(self, points, color, radius):
        """
        Add a track or life way.
        alpha is the transparence
        radius is the size of the track.
        """
        if isinstance(color, str):
            color = Gdk.color_parse(color)
        self.lifeways_ref.append((points, color, radius))

    def add_way(self, points, color):
        """
        Add a track or life way.
        """
        if isinstance(color, str):
            color = Gdk.color_parse(color)
        self.lifeways.append((points, color))

    def do_draw(self, gpsmap, ctx):
        """
        Draw all tracks or life ways.
        """
        for lifeway in self.lifeways_ref:
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.set_line_width(3)
            color = lifeway[1]
            ctx.set_source_rgba(float(color.red / 65535.0),
                                float(color.green / 65535.0),
                                float(color.blue / 65535.0),
                                0.1) # transparency
            rds = float(lifeway[2])
            for point in lifeway[0]:
                conv_pt1 = osmgpsmap.MapPoint.new_degrees(point[0], point[1])
                coord_x1, coord_y1 = gpsmap.convert_geographic_to_screen(
                                                                       conv_pt1)
                conv_pt2 = osmgpsmap.MapPoint.new_degrees(point[0]+rds,
                                                          point[1])
                coord_x2, coord_y2 = gpsmap.convert_geographic_to_screen(
                                                                       conv_pt2)
                coy = abs(coord_y2-coord_y1)
                conv_pt2 = osmgpsmap.MapPoint.new_degrees(point[0],
                                                          point[1]+rds)
                coord_x2, coord_y2 = gpsmap.convert_geographic_to_screen(
                                                                       conv_pt2)
                cox = abs(coord_x2-coord_x1)
                cox = cox if cox > 1.2 else 1.2
                coy = coy if coy > 1.2 else 1.2
                coz = abs(1.0 / float(cox) * float(coy))
                coz = coz if coz > 1.2 else 1.2
                ctx.save()
                ctx.scale(1.0, coz)
                ctx.move_to(coord_x1, coord_y1)
                ctx.translate(coord_x1, coord_y1/coz)
                ctx.arc(0.0, 0.0, cox, 0.0, 2*pi)
                ctx.fill()
                ctx.set_source_rgba(1.0, 0.0, 0.0, 0.5)
                ctx.set_line_width(2.0)
                ctx.arc(0.0, 0.0, cox, 0.0, 2*pi)
                ctx.stroke()
                ctx.restore()

        for lifeway in self.lifeways:
            ctx.set_operator(cairo.OPERATOR_ATOP)
            ctx.set_line_width(3.0)
            map_points = []
            for point in lifeway[0]:
                conv_pt = osmgpsmap.MapPoint.new_degrees(point[0], point[1])
                coord_x, coord_y = gpsmap.convert_geographic_to_screen(conv_pt)
                map_points.append((coord_x, coord_y))
            color = lifeway[1]
            ctx.set_source_rgb(float(color.red / 65535.0),
                               float(color.green / 65535.0),
                               float(color.blue / 65535.0))
            first = True
            for idx_pt in range(0, len(map_points)):
                if first:
                    first = False
                    ctx.move_to(map_points[idx_pt][0], map_points[idx_pt][1])
                else:
                    ctx.line_to(map_points[idx_pt][0], map_points[idx_pt][1])
            ctx.stroke()
            if len(map_points) == 1: # We have only one point
                crdx = map_points[0][0]
                crdy = map_points[0][1]
                ctx.move_to(crdx, crdy)
                ctx.line_to(crdx + 1, crdy + 1)
                ctx.stroke()

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

GObject.type_register(LifeWayLayer)

