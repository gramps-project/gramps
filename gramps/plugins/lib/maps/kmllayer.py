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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: dummynogps.py 20708 2012-11-27 04:31:14Z paul-franklin $

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os,sys
from gi.repository import GObject
import operator
from math import *
import xml.etree.ElementTree as ETree

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("maps.kmllayer")
#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
import cairo
from gi.repository import Pango, PangoCairo

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

class KmlLayer(GObject.GObject, osmgpsmap.MapLayer):
    """
    This is the layer used to display kml files over the map
    * Allowed : points, paths and polygons.

    * One point : name, (latitude, longitude)
    * One path  : name, [ (latitude, longitude), (latitude, longitude), ...]
    * One polygon : name, fill, [ (latitude, longitude), (latitude, longitude), ...]
    """
    def __init__(self):
        """
        Initialize the layer
        """
        GObject.GObject.__init__(self)
        self.dots = []
        self.paths = []
        self.polygons = []
        self.tag = ""
        self.name = ""
        self.type = ""
        self.points = []

    def clear(self):
        """
        reset the layer attributes.
        """
        self.dots = []
        self.paths = []
        self.polygons = []
        self.name = ""

    def polygon(self, attributes):
        self.points = []
        for subAttribute in attributes:
            if subAttribute.tag == self.tag + 'outerBoundaryIs':
                for subsubAttribute in subAttribute:
                    if subsubAttribute.tag == self.tag + 'LinearRing':
                        for subsubsubAttribute in subsubAttribute:
                            if subsubsubAttribute.tag == self.tag + 'coordinates':
                                for point in subsubsubAttribute.text.split():
                                    try:
                                        (longitude, latitude, altitude) = point.split(',')
                                    except:
                                        (longitude, latitude) = point.split(',')
                                    self.points.append((float(latitude), float(longitude)))
            if subAttribute.tag == self.tag + 'innerBoundaryIs':
                for subsubAttribute in subAttribute:
                    if subsubAttribute.tag == self.tag + 'LinearRing':
                        for subsubsubAttribute in subsubAttribute:
                            if subsubsubAttribute.tag == self.tag + 'coordinates':
                                for point in subsubsubAttribute.text.split():
                                    try:
                                        (longitude, latitude, altitude) = point.split(',')
                                    except:
                                        (longitude, latitude) = point.split(',')
                                    self.points.append((float(latitude), float(longitude)))
            if subAttribute.tag == self.tag + 'LinearRing':
                for subsubAttribute in subAttribute:
                    if subsubAttribute.tag == self.tag + 'coordinates':
                        for point in subsubAttribute.text.split():
                            try:
                                (longitude, latitude, altitude) = point.split(',')
                            except:
                                (longitude, latitude) = point.split(',')
                            self.points.append((float(latitude), float(longitude)))

    def add_kml(self, kml_file):
        """
        Add a kml file.
        The access right and validity must be verified before this method.
        """
        tree = ETree.parse(kml_file)
        root = tree.getroot()
        self.tag = root.tag.replace('}kml','}')
        _LOG.debug("Tag version of kml file %s is %s" % (kml_file, self.tag))
        fname, extension = os.path.splitext(kml_file)
        fdir, kmlfile = os.path.split(fname)
        self.index = -1
        lineStrings = tree.findall('.//' + self.tag + 'Placemark')
        for attributes in lineStrings:
            for subAttribute in attributes:
                if subAttribute.tag == self.tag + 'name':
                    self.name = subAttribute.text
                if subAttribute.tag == self.tag + 'Polygon':
                    self.type = 'Polygon'
                    self.points = []
                    self.polygon(subAttribute)
                    if self.name == "":
                        self.polygons.append((kmlfile, self.points))
                    else:
                        self.polygons.append((self.name, self.points))
                if subAttribute.tag == self.tag + 'Point':
                    self.type = 'Point'
                    self.points = []
                    for subsubAttribute in subAttribute:
                        if subsubAttribute.tag == self.tag + 'coordinates':
                            for point in subsubAttribute.text.split():
                                try:
                                    (longitude, latitude, altitude) = point.split(',')
                                except:
                                    (longitude, latitude) = point.split(',')
                                self.points.append((float(latitude), float(longitude)))
                    if self.name == "":
                        self.dots.append((kmlfile, self.points))
                    else:
                        self.dots.append((self.name, self.points))
                if subAttribute.tag == self.tag + 'LineString':
                    self.type = 'Path'
                    self.points = [] 
                    for subsubAttribute in subAttribute:
                        if subsubAttribute.tag == self.tag + 'coordinates':
                            for point in subsubAttribute.text.split():
                                try:
                                    (longitude, latitude, altitude) = point.split(',')
                                except:
                                    (longitude, latitude) = point.split(',')
                                self.points.append((float(latitude), float(longitude)))
                    if self.name == "":
                        self.paths.append((kmlfile, self.points))
                    else:
                        self.paths.append((self.name, self.points))

    def do_draw(self, gpsmap, ctx):
        """
        Draw all the messages
        """
        color1 = Gdk.color_parse('red')
        color2 = Gdk.color_parse('blue')
        # We don't display self.dots. use markers.
        for polygon in self.polygons:
            (name, points) = polygon
            map_points = []
            for point in points:
                conv_pt = osmgpsmap.MapPoint.new_degrees(point[0], point[1])
                coord_x, coord_y = gpsmap.convert_geographic_to_screen(conv_pt)
                map_points.append((coord_x, coord_y))
            first = True
            ctx.save()
            ctx.set_source_rgba(float(color2.red / 65535.0),
                                float(color2.green / 65535.0),
                                float(color2.blue / 65535.0),
                                0.3) # transparency
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
            ctx.fill()
            ctx.restore()
        for path in self.paths:
            (name, points) = path
            map_points = []
            for point in points:
                conv_pt = osmgpsmap.MapPoint.new_degrees(point[0], point[1])
                coord_x, coord_y = gpsmap.convert_geographic_to_screen(conv_pt)
                map_points.append((coord_x, coord_y))
            first = True
            ctx.save()
            ctx.set_source_rgba(float(color1.red / 65535.0),
                                float(color1.green / 65535.0),
                                float(color1.blue / 65535.0),
                                0.5) # transparency
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

GObject.type_register(KmlLayer)
