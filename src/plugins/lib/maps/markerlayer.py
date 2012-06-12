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
_LOG = logging.getLogger("maps.marker")

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

class MarkerLayer(gobject.GObject, osmgpsmap.GpsMapLayer):
    """
    This is the layer used to display the markers.
    """
    def __init__(self):
        """
        Initialize the layer
        """
        gobject.GObject.__init__(self)
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
        Add a track or life marker.
        """
        self.markers.append((points, image, count))
        self.max_references += count
        self.max_places += 1
        if count > self.max_value:
            self.max_value = count
        if count < self.min_value:
            self.min_value = count
        self.nb_ref_by_places = self.max_references / self.max_places

    def do_draw(self, gpsmap, drawable):
        """
        Draw all tracks or life markers.
        """
        ctx = drawable.cairo_create()
        max_interval = self.max_value - self.nb_ref_by_places
        min_interval = self.nb_ref_by_places - self.min_value  
        if min_interval == 0:
            min_interval = 0.01
        for marker in self.markers:
            ctx.save()
            # the icon size in 48, so the standard icon size is 0.6 * 48 = 28.8
            size = 0.6
            if float(marker[2]) > self.nb_ref_by_places:
                # at maximum, we'll have an icon size = (0.6 + 0.3) * 48 = 43.2
                size += ( 0.3 * ( ( float(marker[2]) - self.nb_ref_by_places )/ max_interval) )
            else:
                # at minimum, we'll have an icon size = (0.6 - 0.3) * 48 = 14.4
                size -= ( 0.3 * ( ( self.nb_ref_by_places - float(marker[2]) )/ min_interval) )

            conv_pt = osmgpsmap.point_new_degrees(float(marker[0][0]),
                                                  float(marker[0][1]))
            coord_x, coord_y = gpsmap.convert_geographic_to_screen(conv_pt)
            ctx.translate(coord_x, coord_y)
            ctx.scale( size, size)
            # below, we must found one solution to place exactly the marker
            # depending on its size. Normaly, the left top of the image is set to the coordinates
            # The tip of the pin which should be at the marker position is at 3/18 of the width.
            # rounding problem ?
            posY = - (( 48 * size + 5 ) / ( 16.0 / 18.0 )) - 2
            posX = - (( 48 * size + 5 ) / 6 ) - 2 # 6 <= 3/18 = 1/6
            ctx.set_source_pixbuf(marker[1], posX, posY)
            ctx.paint()
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

gobject.type_register(MarkerLayer)

