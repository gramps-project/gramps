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
from math import *

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
        self.lifeways_ref = []
        self.lifeways = []
        self.lifeways_comment = []
        self.comments = []

    def clear_ways(self):
        """
        reset the layer attributes.
        """
        self.lifeways_ref = []
        self.lifeways = []
        self.lifeways_comment = []
        self.comments = []

    def add_way_ref(self, points, color, radius):
        """
        Add a track or life way.
        alpha is the transparence
        radius is the size of the track.
        """
        self.lifeways_ref.append((points, color, radius))

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
        ctx = drawable.cairo_create()
        for lifeway in self.lifeways_ref:
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.set_line_width(3)
            color = gtk.gdk.color_parse(lifeway[1])
            ctx.set_source_rgba(color.red / 65535,
                               color.green / 65535,
                               color.blue / 65535,
                               0.1) # transparency
            ggc = drawable.new_gc()
            rds = float(lifeway[2])
            for point in lifeway[0]:
                conv_pt1 = osmgpsmap.point_new_degrees(point[0], point[1])
                coord_x1, coord_y1 = gpsmap.convert_geographic_to_screen(conv_pt1)
                conv_pt2 = osmgpsmap.point_new_degrees(point[0]+rds, point[1])
                coord_x2, coord_y2 = gpsmap.convert_geographic_to_screen(conv_pt2)
                coy = abs(coord_y2-coord_y1)
                conv_pt2 = osmgpsmap.point_new_degrees(point[0], point[1]+rds)
                coord_x2, coord_y2 = gpsmap.convert_geographic_to_screen(conv_pt2)
                cox = abs(coord_x2-coord_x1)
                cox = cox if cox > 0.001 else 0.001
                coy = coy if coy > 0.001 else 0.001
                coz = abs( 1.0 / float(cox) * float(coy) )
                coz = coz if coz > 0.001 else 0.001
                ctx.save()
                ctx.scale(1.0,coz)
                ctx.move_to(coord_x1, coord_y1)
                ctx.translate(coord_x1, coord_y1/coz)
                ctx.arc(0.0, 0.0, cox, 0.0, 2*pi)
                ctx.fill()
                ctx.restore()
                top_left = osmgpsmap.point_new_degrees(point[0] + lifeway[2],
                                                       point[1] - lifeway[2])
                bottom_right = osmgpsmap.point_new_degrees(point[0] - lifeway[2],
                                                           point[1] + lifeway[2])
                crd_x, crd_y = gpsmap.convert_geographic_to_screen(top_left)
                crd_x2, crd_y2 = gpsmap.convert_geographic_to_screen(bottom_right)
                drawable.draw_arc(ggc, False, crd_x, crd_y, crd_x2 - crd_x,
                                  crd_y2 - crd_y, 0, 360*64)

        for lifeway in self.lifeways:
            ctx.set_operator(cairo.OPERATOR_ATOP)
            ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0)
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
            if len(map_points) == 1 : # We have only one point
                crdx = map_points[0][0]
                crdy = map_points[0][1]
                ctx.move_to(crdx, crdy)
                ctx.line_to(crdx + 1, crdy + 1)
                ctx.stroke()

        for comment in self.lifeways_comment:
            ctx = drawable.cairo_create()
            # Does the following font is available for all language ? Is it the good one ?
            ctx.select_font_face("Purisa",
                                 cairo.FONT_SLANT_NORMAL,
                                 cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(13)
            points = comment[0]
            conv_pt = osmgpsmap.point_new_degrees(points[0][0], points[0][1])
            if len(points) > 1 :
                crd_x = -(points[0][0] - points[len(points)-1][0] )/2
                crd_y = -(points[0][1] - points[len(points)-1][1] )/2
                conv_pt = osmgpsmap.point_new_degrees(points[0][0]+crd_x, points[0][1]+crd_y)
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

