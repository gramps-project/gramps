# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-now       Serge Noiraud
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
# Python modules
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
import cairo
from gi.repository import Gdk
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from .libkml import Kml

# -------------------------------------------------------------------------
#
# osmGpsMap
#
# -------------------------------------------------------------------------

try:
    import gi
    from gi.repository import OsmGpsMap as osmgpsmap

    gi.require_version("OsmGpsMap", "1.0")
except:
    raise

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
_LOG = logging.getLogger("maps.kmllayer")


class KmlLayer(GObject.GObject, osmgpsmap.MapLayer):
    """
    This is the layer used to display kml files over the map
    * Allowed : points, paths and polygons.

    * One point : name, (latitude, longitude)
    * One path  : name, type, color, transparency,
    *             [ (latitude, longitude), (latitude, longitude), ...]
    * One polygon : name, type, color, transparency,
    *             [ (latitude, longitude), (latitude, longitude), ...]
    """

    def __init__(self):
        """
        Initialize the layer
        """
        GObject.GObject.__init__(self)
        self.paths = []
        self.polygons = []
        self.tag = ""
        self.name = ""
        self.type = ""
        self.points = []
        self.kml = None

    def clear(self):
        """
        reset the layer attributes.
        """
        self.paths = []
        self.polygons = []
        self.name = ""

    def add_kml(self, kml_file):
        """
        Add a kml file.
        The access right and validity must be verified before this method.
        """
        self.kml = Kml(kml_file)
        (paths, polygons) = self.kml.add_kml()
        if paths != []:
            self.paths.append(paths)
        if polygons != []:
            self.polygons.append(polygons)

    def do_draw(self, gpsmap, ctx):
        """
        Draw all the surfaces and paths
        """
        color1 = Gdk.color_parse("red")
        color2 = Gdk.color_parse("blue")
        for polygons in self.polygons:
            for polygon in polygons:
                (dummy_name, ptype, dummy_color, dummy_transparency, points) = polygon
                map_points = []
                for point in points:
                    conv_pt = osmgpsmap.MapPoint.new_degrees(point[0], point[1])
                    (coord_x, coord_y) = gpsmap.convert_geographic_to_screen(conv_pt)
                    map_points.append((coord_x, coord_y))
                first = True
                ctx.save()
                ctx.set_source_rgba(
                    float(color2.red / 65535.0),
                    float(color2.green / 65535.0),
                    float(color2.blue / 65535.0),
                    0.3,
                )  # transparency
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.set_line_join(cairo.LINE_JOIN_ROUND)
                ctx.set_line_width(3)
                ctx.new_path()
                for idx_pt in range(0, len(map_points)):
                    if first:
                        first = False
                        ctx.move_to(map_points[idx_pt][0], map_points[idx_pt][1])
                    else:
                        ctx.line_to(map_points[idx_pt][0], map_points[idx_pt][1])
                ctx.close_path()
                if ptype == "Polygon":
                    ctx.stroke()
                if ptype == "OuterPolygon":
                    ctx.fill()
                if ptype == "InnerPolygon":
                    ctx.set_source_rgba(1.0, 1.0, 1.0, 0.3)
                    ctx.set_operator(cairo.OPERATOR_ADD)
                    ctx.fill()
                ctx.restore()
        for paths in self.paths:
            for path in paths:
                (dummy_name, ptype, dummy_color, dummy_transparency, points) = path
                map_points = []
                for point in points:
                    conv_pt = osmgpsmap.MapPoint.new_degrees(point[0], point[1])
                    (coord_x, coord_y) = gpsmap.convert_geographic_to_screen(conv_pt)
                    map_points.append((coord_x, coord_y))
                first = True
                ctx.save()
                ctx.set_source_rgba(
                    float(color1.red / 65535.0),
                    float(color1.green / 65535.0),
                    float(color1.blue / 65535.0),
                    0.5,
                )  # transparency
                ctx.set_line_width(5)
                ctx.set_operator(cairo.OPERATOR_ATOP)
                for idx_pt in range(0, len(map_points)):
                    if first:
                        first = False
                        ctx.move_to(map_points[idx_pt][0], map_points[idx_pt][1])
                    else:
                        ctx.line_to(map_points[idx_pt][0], map_points[idx_pt][1])
                ctx.stroke()
                ctx.restore()

    def do_render(self, gpsmap):
        """
        render the layer
        """
        dummy_map = gpsmap

    def do_busy(self):
        """
        set the layer busy
        """
        return False

    def do_button_press(self, gpsmap, gdkeventbutton):
        """
        When we press a button.
        """
        dummy_map = gpsmap
        dummy_evt = gdkeventbutton
        return False


GObject.type_register(KmlLayer)
