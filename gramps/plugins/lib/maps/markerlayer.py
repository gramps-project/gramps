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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
from gi.repository import GObject
from math import *

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("maps.marker")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
import cairo

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import time
import logging
_LOG = logging.getLogger("GeoGraphy.markerlayer")

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

class MarkerLayer(GObject.GObject, osmgpsmap.MapLayer):
    """
    This is the layer used to display the markers.
    """
    def __init__(self):
        """
        Initialize the layer
        """
        GObject.GObject.__init__(self)
        self.markers = []
        self.max_references = 0
        self.max_places = 0
        self.nb_ref_by_places = 0
        self.max_value = 0
        self.min_value = 9999

    def clear_markers(self):
        """
        reset the layer attributes.
        """
        self.markers = []
        self.max_references = 0
        self.max_places = 0
        self.nb_ref_by_places = 0
        self.max_value = 0
        self.min_value = 9999

    def add_marker(self, points, image, count):
        """
        Add a marker.
        Set minimum value, maximum value for the markers
        Set the average value too.
        We calculate that here, to minimize the overhead at markers drawing
        """
        self.markers.append((points, image, count))
        self.max_references += count
        self.max_places += 1
        if count > self.max_value:
            self.max_value = count
        if count < self.min_value:
            self.min_value = count
        self.nb_ref_by_places = self.max_references / self.max_places

    def do_draw(self, gpsmap, ctx):
        """
        Draw all markers here. Calculate where to draw the marker.
        Depending of the average, minimum and maximum value, resize the marker.
        We use cairo to resize the marker.
        """
        max_interval = self.max_value - self.nb_ref_by_places
        min_interval = self.nb_ref_by_places - self.min_value  
        if max_interval == 0: # This to avoid divide by zero
            max_interval = 0.01
        if min_interval == 0: # This to avoid divide by zero
            min_interval = 0.01
        _LOG.debug("%s" % time.strftime("start drawing   : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))
        for marker in self.markers:
            ctx.save()
            # the icon size in 48, so the standard icon size is 0.6 * 48 = 28.8
            size = 0.6
            mark = float(marker[2])
            if mark > self.nb_ref_by_places:
                # at maximum, we'll have an icon size = (0.6 + 0.3) * 48 = 43.2
                size += (0.3 * ((mark - self.nb_ref_by_places)
                                 / max_interval) )
            else:
                # at minimum, we'll have an icon size = (0.6 - 0.3) * 48 = 14.4
                size -= (0.3 * ((self.nb_ref_by_places - mark)
                                 / min_interval) )

            conv_pt = osmgpsmap.MapPoint.new_degrees(float(marker[0][0]),
                                                  float(marker[0][1]))
            coord_x, coord_y = gpsmap.convert_geographic_to_screen(conv_pt)
            ctx.translate(coord_x, coord_y)
            ctx.scale( size, size)
            # below, we try to place exactly the marker depending on its size.
            # Normaly, the left top corner of the image is set to the coordinates.
            # The tip of the pin which should be at the marker position is at
            # 3/18 of the width and to the height of the image.
            # So we shift the image position.
            posY = - int( 48 * size + 0.5 ) - 10
            posX = - int(( 48 * size ) / 6 + 0.5 ) - 10
            ctx.set_source_surface(marker[1], posX, posY)
            ctx.paint()
            ctx.restore()
        _LOG.debug("%s" % time.strftime("end drawing     : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))

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

GObject.type_register(MarkerLayer)

