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
import os
import logging
import xml.etree.ElementTree as ETree
from gi.repository import GObject

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
_LOG = logging.getLogger("maps.libkml")


class Kml(GObject.GObject):
    """
    This is the library used to read kml files
    * Allowed : points, paths and polygons.

    * One point : name, (latitude, longitude)
    * One path  : name, [ (latitude, longitude), (latitude, longitude), ...]
    * One polygon : name, type, color,
    *               [ (latitude, longitude), (latitude, longitude), ...]

    * Some kml files use the altitude. We don't use it.

    """

    def __init__(self, kml_file):
        """
        Initialize the library
        The access right and validity of the kmlfile must be verified
        before this method.
        """
        GObject.GObject.__init__(self)
        self.tag = ""
        self.name = ""
        self.color = ""
        self.transparency = ""
        self.type = ""
        self.points = []
        self.markers = []
        self.paths = []
        self.polygons = []
        self.tree = ETree.parse(kml_file)
        root = self.tree.getroot()
        self.tag = root.tag.replace("}kml", "}")
        _LOG.debug("Tag version of kml file %s is %s", kml_file, self.tag)
        fname, dummy_extension = os.path.splitext(kml_file)
        dummy_fdir, self.kmlfile = os.path.split(fname)

    def set_default(self):
        """
        Set all the default value for the marker
        """
        self.name = self.kmlfile
        self.type = None
        self.color = None
        self.transparency = None

    def get_color(self, attributes):
        """
        Get the color for this marker
        """
        pass

    def get_transparency(self, attributes):
        """
        Get the transparency for this marker
        """
        pass

    def get_coordinates(self, attributes):
        """
        Get all the coordinates for this marker
        """
        self.points = []
        for point in attributes.text.split():
            try:
                (longitude, latitude, dummy_altitude) = point.split(",")
            except:
                (longitude, latitude) = point.split(",")
            self.points.append((float(latitude), float(longitude)))

    def get_linear_ring(self, attributes):
        """
        Get all the coordinates for this marker
        """
        for sub_attribute in attributes:
            if sub_attribute.tag == self.tag + "coordinates":
                self.get_coordinates(sub_attribute)

    def get_polygon_outer_boundary(self, attributes):
        """
        This function get the coordinates used to draw a filled polygon.
        """
        self.type = "OuterPolygon"
        for sub_attribute in attributes:
            if sub_attribute.tag == self.tag + "LinearRing":
                self.get_linear_ring(sub_attribute)

    def get_polygon_inner_boundary(self, attributes):
        """
        This function get the coordinates used to draw a hole inside
        a filled polygon.
        """
        self.type = "InnerPolygon"
        for sub_attribute in attributes:
            if sub_attribute.tag == self.tag + "LinearRing":
                self.get_linear_ring(sub_attribute)

    def get_polygon(self, attributes):
        """
        Get all the coordinates for the polygon
        """
        for sub_attribute in attributes:
            if sub_attribute.tag == self.tag + "outerBoundaryIs":
                self.get_polygon_outer_boundary(sub_attribute)
                self.polygons.append(
                    (self.name, self.type, self.color, self.transparency, self.points)
                )
            if sub_attribute.tag == self.tag + "innerBoundaryIs":
                self.get_polygon_inner_boundary(sub_attribute)
                self.polygons.append(
                    (self.name, self.type, self.color, self.transparency, self.points)
                )
            if sub_attribute.tag == self.tag + "LinearRing":
                self.get_linear_ring(sub_attribute)
                self.type = "Polygon"
                self.polygons.append(
                    (self.name, self.type, self.color, self.transparency, self.points)
                )

    def get_point(self, attributes):
        """
        Get all the coordinates for this marker
        """
        self.type = "Point"
        for sub_attribute in attributes:
            if sub_attribute.tag == self.tag + "coordinates":
                self.get_coordinates(sub_attribute)

    def get_path(self, attributes):
        """
        Get all the coordinates for this marker
        """
        self.type = "Path"
        for sub_attribute in attributes:
            if sub_attribute.tag == self.tag + "coordinates":
                self.get_coordinates(sub_attribute)
                self.paths.append(
                    (self.name, self.type, self.color, self.transparency, self.points)
                )

    def get_multi_geometry(self, attributes):
        """
        Do we have some sub structures ?
        """
        for sub_attribute in attributes:
            if sub_attribute.tag == self.tag + "Polygon":
                self.get_polygon(sub_attribute)
            if sub_attribute.tag == self.tag + "LineString":
                self.get_path(sub_attribute)

    def add_kml(self):
        """
        Add a kml file.
        """
        line_strings = self.tree.findall(".//" + self.tag + "Placemark")
        for attributes in line_strings:
            self.points = []
            self.set_default()
            for sub_attribute in attributes:
                if sub_attribute.tag == self.tag + "name":
                    self.name = sub_attribute.text
                if sub_attribute.tag == self.tag + "Polygon":
                    self.get_polygon(sub_attribute)
                if sub_attribute.tag == self.tag + "LineString":
                    self.get_path(sub_attribute)
                if sub_attribute.tag == self.tag + "MultiGeometry":
                    self.get_multi_geometry(sub_attribute)
        return (self.paths, self.polygons)

    def add_points(self):
        """
        Add points or markers
        """
        line_strings = self.tree.findall(".//" + self.tag + "Placemark")
        self.markers = []
        for attributes in line_strings:
            self.points = []
            self.set_default()
            for sub_attribute in attributes:
                if sub_attribute.tag == self.tag + "name":
                    self.name = sub_attribute.text
                if sub_attribute.tag == self.tag + "Point":
                    self.get_point(sub_attribute)
                    self.markers.append((self.name, self.points))
        return self.markers


GObject.type_register(Kml)
