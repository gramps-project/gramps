# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011       Serge Noiraud
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
import sys
import os
import gobject

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("maps.osmgpsmap")

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
import constants
from gen.ggettext import sgettext as _
from gen.ggettext import ngettext
from config import config

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
GEOGRAPHY_PATH = os.path.join(const.HOME_DIR, "maps")

#-------------------------------------------------------------------------
#
# osmGpsMap
#
#-------------------------------------------------------------------------

try:
    import osmgpsmap
except:
    raise

class DummyMapNoGpsPoint(osmgpsmap.GpsMap):
    def do_draw_gps_point(self, drawable):
        pass
gobject.type_register(DummyMapNoGpsPoint)

class DummyLayer(gobject.GObject, osmgpsmap.GpsMapLayer):
    def __init__(self):
        gobject.GObject.__init__(self)

    def do_draw(self, gpsmap, gdkdrawable):
        pass

    def do_render(self, gpsmap):
        pass

    def do_busy(self):
        return False

    def do_button_press(self, gpsmap, gdkeventbutton):
        return False
gobject.type_register(DummyLayer)

class SelectionLayer(gobject.GObject, osmgpsmap.GpsMapLayer):
    def __init__(self):
        gobject.GObject.__init__(self)
        self.circles = []

    def add_circle(self, r, lat, lon):
        self.circles.append((r, lat, lon))

    def do_draw(self, gpsmap, drawable):
        gc = drawable.new_gc()
        for circle in self.circles:
            top_left = osmgpsmap.point_new_degrees(circle[1] + circle[0],
                                                   circle[2] - circle[0])
            bottom_right = osmgpsmap.point_new_degrees(circle[1] - circle[0],
                                                       circle[2] + circle[0])
            x, y = gpsmap.convert_geographic_to_screen(top_left)
            x2, y2 = gpsmap.convert_geographic_to_screen(bottom_right)
            drawable.draw_arc(gc, False, x, y, x2 - x, y2 - y, 0, 360*64)

    def do_render(self, gpsmap):
        pass

    def do_busy(self):
        return False

    def do_button_press(self, gpsmap, gdkeventbutton):
        return False
gobject.type_register(SelectionLayer)

class osmGpsMap():
    def __init__(self):
        self.vbox = None
        self.cross_map = None
        self.osm = None
        self.show_tooltips = True
        self.selection_layer = None

    def build_widget(self):
        self.vbox = gtk.VBox(False, 0)
        cache_path = os.path.join(const.HOME_DIR, 'maps')
        if not os.path.isdir(cache_path):
            try:
                os.mkdir(cache_path, 0750)
            except:
                ErrorDialog(_("Can't create tiles cache directory %s") %
                             cache_path )
                return self.vbox

        self.change_map(None,config.get("geography.map_service"))
        return self.vbox

    def change_map(self, obj, map_type):
        if obj is not None:
            self.osm.layer_remove_all()
            self.osm.image_remove_all()
            self.vbox.remove(self.osm)
            self.osm.destroy()
        tiles_path=os.path.join(GEOGRAPHY_PATH, constants.tiles_path[map_type])
        if not os.path.isdir(tiles_path):
            try:
                os.mkdir(tiles_path, 0750)
            except:
                ErrorDialog(_("Can't create tiles cache directory for '%s'.") %
                             constants.map_title[map_type])
        config.set("geography.map_service", map_type)
        self.current_map = map_type
        if 0:
            self.osm = DummyMapNoGpsPoint()
        else:
            self.osm = osmgpsmap.GpsMap(tile_cache=tiles_path,
                                        map_source=constants.map_type[map_type])
        current_map = osmgpsmap.GpsMapOsd( show_dpad=False, show_zoom=True)
        self.osm.layer_add(current_map)
        self.osm.layer_add(DummyLayer())
        self.selection_layer = self.add_selection_layer()
        self.cross_map = osmgpsmap.GpsMapOsd( show_crosshair=False)
        self.set_crosshair(config.get("geography.show_cross"))
        self.osm.set_center_and_zoom(config.get("geography.center-lat"),
                                     config.get("geography.center-lon"),
                                     config.get("geography.zoom") )

        self.osm.connect('button_release_event', self.map_clicked)
        self.osm.connect('changed', self.zoom_changed)
        self.osm.connect("motion-notify-event", self.motion_event)
        self.osm.show()
        self.vbox.pack_start(self.osm)
        if obj is not None:
            self._createmap(None)

    def add_selection_layer(self):
        selection_layer = SelectionLayer()
        self.osm.layer_add(selection_layer)
        return selection_layer

    def get_selection_layer(self):
        return self.selection_layer

    def remove_layer(self, layer):
        self.osm.layer_remove(layer)

    def zoom_changed(self, zoom):
        config.set("geography.zoom",self.osm.props.zoom)
        self.save_center(self.osm.props.latitude, self.osm.props.longitude)

    def motion_event(self, osmmap, event):
        """
        Show the place name if found on the status bar
        """
        current = osmgpsmap.point_new_degrees(0.0,0.0)
        osmmap.convert_screen_to_geographic(int(event.x), int(event.y), current)
        lat, lon = current.get_degrees()

    def save_center(self, lat, lon):
        """
        Save the longitude and lontitude in case we switch between maps.
        """
        config.set("geography.center-lat",lat)
        config.set("geography.center-lon",lon)

    def map_clicked(self, osm, event):
        lat,lon = self.osm.get_event_location(event).get_degrees()
        if event.button == 1:
            # do we click on a marker ?
            marker = self.is_there_a_marker_here(event, lat, lon)
        elif event.button == 3:
            self.build_nav_menu(osm, event, lat, lon )
        else:
            self.save_center(lat,lon)

    def is_there_a_marker_here(self, lat, lon):
        raise NotImplementedError

    def set_crosshair(self,active):
        """
        Show or hide the crosshair ?
        """
        if active:
            self.cross_map = osmgpsmap.GpsMapOsd( show_crosshair=True)
            self.osm.layer_add( self.cross_map )
            # The two following are to force the map to update
            self.osm.zoom_in()
            self.osm.zoom_out()
        else:
            self.osm.layer_remove(self.cross_map)
        pass
