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
_LOG = logging.getLogger("maps.libkml")

class Kml(GObject.GObject):
    """
    This is the library used to read kml files
    * Allowed : points, paths and polygons.

    * One point : name, (latitude, longitude)
    * One path  : name, [ (latitude, longitude), (latitude, longitude), ...]
    * One polygon : name, type, color, [ (latitude, longitude), (latitude, longitude), ...]

    * Some kml files use the altitude. We don't use it.

    """
    def __init__(self, kml_file):
        """
        Initialize the library
        The access right and validity of the kmlfile must be verified before this method.
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
        self.tag = root.tag.replace('}kml','}')
        _LOG.debug("Tag version of kml file %s is %s" % (kml_file, self.tag))
        fname, extension = os.path.splitext(kml_file)
        fdir, self.kmlfile = os.path.split(fname)

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
                (longitude, latitude, altitude) = point.split(',')
            except:
                (longitude, latitude) = point.split(',')
            self.points.append((float(latitude), float(longitude)))

    def get_linear_ring(self, attributes):
        """
        Get all the coordinates for this marker
        """
        for subAttribute in attributes:
            if subAttribute.tag == self.tag + 'coordinates':
                self.get_coordinates(subAttribute)

    def get_polygon_outer_boundary(self, attributes):
        """
        This function get the coordinates used to draw a filled polygon.
        """
        self.type = 'OuterPolygon'
        for subAttribute in attributes:
            if subAttribute.tag == self.tag + 'LinearRing':
                self.get_linear_ring(subAttribute)

    def get_polygon_inner_boundary(self, attributes):
        """
        This function get the coordinates used to draw a hole inside a filled polygon.
        """
        self.type = 'InnerPolygon'
        for subAttribute in attributes:
            if subAttribute.tag == self.tag + 'LinearRing':
                self.get_linear_ring(subAttribute)

    def get_polygon(self, attributes):
        """
        Get all the coordinates for the polygon
        """
        for subAttribute in attributes:
            if subAttribute.tag == self.tag + 'outerBoundaryIs':
                self.get_polygon_outer_boundary(subAttribute)
                self.polygons.append((self.name,
                                      self.type,
                                      self.color,
                                      self.transparency,
                                      self.points))
            if subAttribute.tag == self.tag + 'innerBoundaryIs':
                self.get_polygon_inner_boundary(subAttribute)
                self.polygons.append((self.name,
                                      self.type,
                                      self.color,
                                      self.transparency,
                                      self.points))
            if subAttribute.tag == self.tag + 'LinearRing':
                self.get_linear_ring(subAttribute)
                self.type = 'Polygon'
                self.polygons.append((self.name,
                                      self.type,
                                      self.color,
                                      self.transparency,
                                      self.points))

    def get_point(self, attributes):
        """
        Get all the coordinates for this marker
        """
        self.type = 'Point'
        for subAttribute in attributes:
            if subAttribute.tag == self.tag + 'coordinates':
                self.get_coordinates(subAttribute)

    def get_path(self, attributes):
        """
        Get all the coordinates for this marker
        """
        self.type = 'Path'
        for subAttribute in attributes:
            if subAttribute.tag == self.tag + 'coordinates':
                self.get_coordinates(subAttribute)
                self.paths.append((self.name,
                                   self.type,
                                   self.color,
                                   self.transparency,
                                   self.points))

    def get_multi_geometry(self, attributes):
        for subAttribute in attributes:
            if subAttribute.tag == self.tag + 'Polygon':
                self.polygon(subAttribute)
            if subAttribute.tag == self.tag + 'LineString':
                self.get_path(subAttribute)

    def add_kml(self):
        """
        Add a kml file.
        """
        lineStrings = self.tree.findall('.//' + self.tag + 'Placemark')
        for attributes in lineStrings:
            self.points = []
            self.set_default()
            for subAttribute in attributes:
                if subAttribute.tag == self.tag + 'name':
                    self.name = subAttribute.text
                if subAttribute.tag == self.tag + 'Polygon':
                    self.get_polygon(subAttribute)
                if subAttribute.tag == self.tag + 'LineString':
                    self.get_path(subAttribute)
                if subAttribute.tag == self.tag + 'MultiGeometry':
                    self.get_multi_geometry(subAttribute)
        return (self.paths, self.polygons)

    def add_points(self):
        """
        Add points or markers
        """
        lineStrings = self.tree.findall('.//' + self.tag + 'Placemark')
        self.markers = []
        for attributes in lineStrings:
            self.points = []
            self.set_default()
            for subAttribute in attributes:
                if subAttribute.tag == self.tag + 'name':
                    self.name = subAttribute.text
                if subsubAttribute.tag == self.tag + 'Point':
                    self.get_point(subsubAttribute)
                    self.markers.append((self.name, self.points))
        return self.markers

GObject.type_register(Kml)
