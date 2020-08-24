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
import os
from math import pi, sin, atanh, floor

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import time
import logging
_LOG = logging.getLogger("maps.osmgps")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.plugins.lib.maps import constants
from .dummylayer import DummyLayer
from .dummynogps import DummyMapNoGpsPoint
from .selectionlayer import SelectionLayer
from .lifewaylayer import LifeWayLayer
from .markerlayer import MarkerLayer
from .datelayer import DateLayer
from .messagelayer import MessageLayer
from .kmllayer import KmlLayer
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.config import config
from gramps.gui.dialog import ErrorDialog
from gramps.gen.constfunc import get_env_var
from gramps.gen.const import VERSION_DIR

#-------------------------------------------------------------------------
#
# OsmGps
#
#-------------------------------------------------------------------------

try:
    import gi
    gi.require_version('OsmGpsMap', '1.0')
    from gi.repository import OsmGpsMap as osmgpsmap
except:
    raise

# pylint: disable=unused-argument
# pylint: disable=no-member
# pylint: disable=maybe-no-member

def lon2pixel(zoom, longitude, size):
    """
    pixel_x = (2^zoom * size * longitude) / 2PI + (2^zoom * size) / 2
    """
    value = ((longitude * size * (2**zoom)) / (2*pi)) + ((2**zoom) * size / 2)
    return int(value)

def lat2pixel(zoom, latitude, size):
    """
    http://manialabs.wordpress.com/2013/01/26/converting-latitude-and-longitude-to-map-tile-in-mercator-projection/

    pixel_y = -(2^zoom * size * lat_m) / 2PI + (2^zoom * size) / 2
    """
    lat_m = atanh(sin(latitude))
    value = -((lat_m * size * (2**zoom)) / (2*pi)) + ((2**zoom) * (size/2))
    return int(value)

class OsmGps:
    """
    This class is used to create a map
    """
    def __init__(self, uistate):
        """
        Initialize the map
        """
        self.vbox = None
        self.cross_map = None
        self.osm = None
        self.show_tooltips = True
        self.zone_selection = False
        self.selection_layer = None
        self.lifeway_layer = None
        self.marker_layer = None
        self.date_layer = None
        self.message_layer = None
        self.kml_layer = None
        self.context_id = 0
        self.begin_selection = None
        self.end_selection = None
        self.current_map = None
        self.places_found = None
        self.uistate = uistate

    def build_widget(self):
        """
        create the vbox
        """
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        cache_path = config.get('geography.path')
        if not os.path.isdir(cache_path):
            try:
                os.makedirs(cache_path, 0o755) # create dir like mkdir -p
            except:
                ErrorDialog(_("Can't create "
                              "tiles cache directory %s") % cache_path,
                            parent=self.uistate.window)
                gini = os.path.join(VERSION_DIR, 'gramps.ini')
                ErrorDialog(_("You must verify and change the tiles cache"
                              "\n..."
                              "\n[geography]"
                              "\n..."
                              "\npath='bad/path'"
                              "\n..."
                              "\nin the gramps.ini file :\n%s"
                              "\n\nBefore to change the gramps.ini file, "
                              "you need to close gramps"
                              "\n\nThe next errors will be normal") % gini,
                            parent=self.uistate.window)
                return None

        self.change_map(None, config.get("geography.map_service"))
        return self.vbox

    def change_map(self, obj, map_type):
        """
        Change the current map
        """
        if map_type == constants.PERSONAL:
            map_source = config.get('geography.personal-map')
            if map_source == "":
                return
            name = constants.TILES_PATH[map_type]
            self.change_new_map(name, map_source)
            config.set("geography.map_service", map_type)
            self.current_map = map_type
            return
        if obj is not None:
            self.osm.layer_remove_all()
            self.osm.image_remove_all()
            self.vbox.remove(self.osm)
            self.osm.destroy()
        tiles_path = os.path.join(config.get('geography.path'),
                                  constants.TILES_PATH[map_type])
        if not os.path.isdir(tiles_path):
            try:
                os.makedirs(tiles_path, 0o755) # create dir like mkdir -p
            except:
                ErrorDialog(_("Can't create "
                              "tiles cache directory for '%s'.") %
                              constants.MAP_TITLE[map_type],
                            parent=self.uistate.window)
        config.set("geography.map_service", map_type)
        self.current_map = map_type
        http_proxy = get_env_var('http_proxy')
        if 0:
            self.osm = DummyMapNoGpsPoint()
        else:
            if http_proxy:
                self.osm = osmgpsmap.Map(tile_cache=tiles_path,
                                         proxy_uri=http_proxy,
                                         map_source=constants.MAP_TYPE[
                                                                      map_type])
            else:
                self.osm = osmgpsmap.Map(tile_cache=tiles_path,
                                         map_source=constants.MAP_TYPE[
                                                                      map_type])
        self.osm.props.tile_cache = osmgpsmap.MAP_CACHE_AUTO
        current_map = osmgpsmap.MapOsd(show_dpad=False, show_zoom=True)
        self.end_selection = None
        self.osm.layer_add(current_map)
        self.osm.layer_add(DummyLayer())
        self.selection_layer = self.add_selection_layer()
        self.kml_layer = self.add_kml_layer()
        self.lifeway_layer = self.add_lifeway_layer()
        self.marker_layer = self.add_marker_layer()
        self.date_layer = self.add_date_layer()
        self.message_layer = self.add_message_layer()
        self.cross_map = osmgpsmap.MapOsd(show_crosshair=False)
        self.set_crosshair(config.get("geography.show_cross"))
        self.osm.set_center_and_zoom(config.get("geography.center-lat"),
                                     config.get("geography.center-lon"),
                                     config.get("geography.zoom"))

        self.osm.connect('button_release_event', self.map_clicked)
        self.osm.connect('button_press_event', self.map_clicked)
        self.osm.connect("motion-notify-event", self.motion_event)
        self.osm.connect('changed', self.zoom_changed)
        self.update_shortcuts(True)
        self.osm.show()
        self.vbox.pack_start(self.osm, True, True, 0)
        self.goto_handle(handle=None)

    def change_new_map(self, name, map_source):
        """
        Change the current map with a new provider
        This map is not supported by osm-gps-map

        name       : the name of the provider
        map_source : the url to search for tiles
        """
        try:
            self.osm.layer_remove_all()
            self.osm.image_remove_all()
            self.vbox.remove(self.osm)
            self.osm.destroy()
        except:
            pass
        tiles_path = os.path.join(config.get('geography.path'), name)
        if not os.path.isdir(tiles_path):
            try:
                os.makedirs(tiles_path, 0o755) # create dir like mkdir -p
            except:
                ErrorDialog(_("Can't create "
                              "tiles cache directory for '%s'.") %
                              constants.MAP_TITLE[self.current_map],
                            parent=self.uistate.window)
        http_proxy = get_env_var('http_proxy')
        if 0:
            self.osm = DummyMapNoGpsPoint()
        else:
            if http_proxy:
                self.osm = osmgpsmap.Map(tile_cache=tiles_path,
                                         proxy_uri=http_proxy,
                                         repo_uri=map_source)
            else:
                self.osm = osmgpsmap.Map(tile_cache=tiles_path,
                                         repo_uri=map_source)
        self.osm.props.tile_cache = osmgpsmap.MAP_CACHE_AUTO
        current_map = osmgpsmap.MapOsd(show_dpad=False, show_zoom=True)
        self.end_selection = None
        self.osm.layer_add(current_map)
        self.osm.layer_add(DummyLayer())
        self.selection_layer = self.add_selection_layer()
        self.kml_layer = self.add_kml_layer()
        self.lifeway_layer = self.add_lifeway_layer()
        self.marker_layer = self.add_marker_layer()
        self.date_layer = self.add_date_layer()
        self.message_layer = self.add_message_layer()
        self.cross_map = osmgpsmap.MapOsd(show_crosshair=False)
        self.set_crosshair(config.get("geography.show_cross"))
        self.osm.set_center_and_zoom(config.get("geography.center-lat"),
                                     config.get("geography.center-lon"),
                                     config.get("geography.zoom"))

        self.osm.connect('button_release_event', self.map_clicked)
        self.osm.connect('button_press_event', self.map_clicked)
        self.osm.connect("motion-notify-event", self.motion_event)
        self.osm.connect('changed', self.zoom_changed)
        self.update_shortcuts(True)
        self.osm.show()
        self.vbox.pack_start(self.osm, True, True, 0)
        self.goto_handle(handle=None)

    def reload_tiles(self):
        """
        We need to reload all visible tiles for the current map
        """
        map_idx = config.get("geography.map_service")
        map_name = constants.TILES_PATH[map_idx]
        map_path = os.path.join(config.get('geography.path'), map_name)
        # get the top left corner and bottom right corner
        bbox = self.osm.get_bbox()
        pt1 = bbox[0]
        pt2 = bbox[1]
        self.zoom = config.get("geography.zoom")
        tile_size = float(256)
        if map_idx != constants.PERSONAL:
            # get the file extension depending on the map provider
            img_format = self.osm.source_get_image_format(map_idx)
        else:
            filename = config.get("geography.personal-map")
            img_format = os.path.splitext(filename)[1]
        # calculate the number of images to download in rows and columns
        pt1_x = floor(lon2pixel(self.zoom, pt1.rlon, tile_size) / tile_size)
        pt1_y = floor(lat2pixel(self.zoom, pt1.rlat, tile_size) / tile_size)
        pt2_x = floor(lon2pixel(self.zoom, pt2.rlon, tile_size) / tile_size)
        pt2_y = floor(lat2pixel(self.zoom, pt2.rlat, tile_size) / tile_size)
        for ptx_i in range(pt1_x, pt2_x):
            for pty_j in range(pt1_y, pt2_y):
                tile_path = "%s%c%d%c%d%c%d.%s" % (map_path, os.sep, self.zoom,
                                                   os.sep, ptx_i, os.sep, pty_j,
                                                   img_format)
                _LOG.debug("file removed : %s", tile_path)
                try:
                    os.unlink(tile_path)
                except:
                    # The tile doesn't exist because it is in the load queue.
                    # That occurs when zooming.
                    pass
        self.osm.download_maps(pt1, pt2, self.zoom, self.zoom)

    def update_shortcuts(self, arg):
        """
        connect the keyboard or the keypad for shortcuts
        arg is mandatory because this function is also called by
        the checkbox button
        """
        config.set('geography.use-keypad',
                         self._config.get('geography.use-keypad'))
        if config.get('geography.use-keypad'):
            self.osm.set_keyboard_shortcut(osmgpsmap.MapKey_t.ZOOMIN,
                                           Gdk.keyval_from_name("KP_Add"))
            self.osm.set_keyboard_shortcut(osmgpsmap.MapKey_t.ZOOMOUT,
                                           Gdk.keyval_from_name("KP_Subtract"))
        else:
            self.osm.set_keyboard_shortcut(osmgpsmap.MapKey_t.ZOOMIN,
                                           Gdk.keyval_from_name("plus"))
            self.osm.set_keyboard_shortcut(osmgpsmap.MapKey_t.ZOOMOUT,
                                           Gdk.keyval_from_name("minus"))

        self.osm.set_keyboard_shortcut(osmgpsmap.MapKey_t.UP,
                                       Gdk.keyval_from_name("Up"))
        self.osm.set_keyboard_shortcut(osmgpsmap.MapKey_t.DOWN,
                                       Gdk.keyval_from_name("Down"))
        self.osm.set_keyboard_shortcut(osmgpsmap.MapKey_t.LEFT,
                                       Gdk.keyval_from_name("Left"))
        self.osm.set_keyboard_shortcut(osmgpsmap.MapKey_t.RIGHT,
                                       Gdk.keyval_from_name("Right"))

        # For shortcuts work, we must grab the focus
        self.osm.grab_focus()

    def add_selection_layer(self):
        """
        add the selection layer
        """
        selection_layer = SelectionLayer()
        self.osm.layer_add(selection_layer)
        return selection_layer

    def get_selection_layer(self):
        """
        get the selection layer
        """
        return self.selection_layer

    def add_kml_layer(self):
        """
        add the kml layer to the map
        """
        kml_layer = KmlLayer()
        self.osm.layer_add(kml_layer)
        return kml_layer

    def get_kml_layer(self):
        """
        get the kml layer
        """
        return self.kml_layer

    def add_message_layer(self):
        """
        add the message layer to the map
        """
        message_layer = MessageLayer()
        self.osm.layer_add(message_layer)
        return message_layer

    def get_message_layer(self):
        """
        get the message layer
        """
        return self.message_layer

    def add_date_layer(self):
        """
        add the date layer to the map
        """
        date_layer = DateLayer()
        self.osm.layer_add(date_layer)
        return date_layer

    def get_date_layer(self):
        """
        get the date layer
        """
        return self.date_layer

    def add_marker_layer(self):
        """
        add the marker layer
        """
        marker_layer = MarkerLayer()
        self.osm.layer_add(marker_layer)
        return marker_layer

    def get_marker_layer(self):
        """
        get the marker layer
        """
        return self.marker_layer

    def add_lifeway_layer(self):
        """
        add the track or life ways layer
        """
        lifeway_layer = LifeWayLayer()
        self.osm.layer_add(lifeway_layer)
        return lifeway_layer

    def get_lifeway_layer(self):
        """
        get the track or life ways layer
        """
        return self.lifeway_layer

    def remove_layer(self, layer):
        """
        remove the specified layer
        """
        self.osm.layer_remove(layer)

    def zoom_changed(self, zoom):
        """
        save the zoom and the position
        """
        config.set("geography.zoom", self.osm.props.zoom)
        self.save_center(self.osm.props.latitude, self.osm.props.longitude)

    def motion_event(self, osmmap, event):
        """
        Moving during selection
        """
        current = osmmap.convert_screen_to_geographic(int(event.x),
                                                      int(event.y))
        lat, lon = current.get_degrees()
        if self.zone_selection:
            # We draw a rectangle to show the selected region.
            layer = self.get_selection_layer()
            if layer:
                self.osm.layer_remove(layer)
            self.selection_layer = self.add_selection_layer()
            if self.end_selection == None:
                self.selection_layer.add_rectangle(self.begin_selection,
                                                   current)
            else:
                self.selection_layer.add_rectangle(self.begin_selection,
                                                   self.end_selection)
        else:
            places = self.is_there_a_place_here(lat, lon)
            mess = ""
            for plc in places:
                if mess != "":
                    mess += " || "
                mess += plc[0]
            self.uistate.status.pop(self.context_id)
            self.context_id = self.uistate.status.push(1, mess)

    def save_center(self, lat, lon):
        """
        Save the longitude and lontitude in case we switch between maps.
        """
        _LOG.debug("save_center : %s,%s", lat, lon)
        if (-90.0 < lat < +90.0) and (-180.0 < lon < +180.0):
            config.set("geography.center-lat", lat)
            config.set("geography.center-lon", lon)
        else:
            _LOG.debug("save_center : new coordinates : %s,%s", lat, lon)
            _LOG.debug("save_center : old coordinates : %s,%s", lat, lon)
            # osmgpsmap bug ? reset to prior values to avoid osmgpsmap problems.
            self.osm.set_center_and_zoom(config.get("geography.center-lat"),
                                         config.get("geography.center-lon"),
                                         config.get("geography.zoom"))

    def activate_selection_zoom(self, osm, event):
        """
        Zoom when in zone selection
        """
        if self.end_selection is not None:
            self._autozoom()
        return True

    def map_clicked(self, osm, event):
        """
        Someone click on the map. Look at if we have a marker.
        mouse button 1 : zone selection or marker selection
        mouse button 2 : begin zone selection
        mouse button 3 : call the menu
        """
        self.osm.grab_focus()
        lat, lon = self.osm.get_event_location(event).get_degrees()
        current = osm.convert_screen_to_geographic(int(event.x), int(event.y))
        lat, lon = current.get_degrees()
        if event.button == 1 and event.type == Gdk.EventType.BUTTON_PRESS:
            if self.end_selection is not None:
                self.activate_selection_zoom(osm, event)
                self.end_selection = None
            else:
                # do we click on a marker ?
                self.is_there_a_marker_here(event, lat, lon)
        elif event.button == 2 and event.type == Gdk.EventType.BUTTON_PRESS:
            self.begin_selection = current
            self.end_selection = None
            self.zone_selection = True
        elif event.button == 2 and event.type == Gdk.EventType.BUTTON_RELEASE:
            self.end_selection = current
            self.zone_selection = False
        elif Gdk.Event.triggers_context_menu(event):
            self.build_nav_menu(osm, event, lat, lon)
        else:
            self.save_center(lat, lon)

    def is_there_a_place_here(self, lat, lon):
        """
        Is there a place at this position ?
        If too many places, this function is very time consuming
        """
        mark_selected = []
        if self.no_show_places_in_status_bar:
            return mark_selected
        oldplace = ""
        _LOG.debug("%s", time.strftime("start is_there_a_place_here : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))
        for mark in self.places_found:
            # as we are not precise with our hand, reduce the precision
            # depending on the zoom.
            if mark[0] != oldplace:
                oldplace = mark[0]
                precision = {
                              1 : '%3.0f', 2 : '%3.1f', 3 : '%3.1f',
                              4 : '%3.1f', 5 : '%3.2f', 6 : '%3.2f',
                              7 : '%3.2f', 8 : '%3.3f', 9 : '%3.3f',
                             10 : '%3.3f', 11 : '%3.3f', 12 : '%3.3f',
                             13 : '%3.3f', 14 : '%3.4f', 15 : '%3.4f',
                             16 : '%3.4f', 17 : '%3.4f', 18 : '%3.4f'
                             }.get(config.get("geography.zoom"), '%3.1f')
                shift = {
                          1 : 5.0, 2 : 5.0, 3 : 3.0,
                          4 : 1.0, 5 : 0.5, 6 : 0.3, 7 : 0.15,
                          8 : 0.06, 9 : 0.03, 10 : 0.015,
                         11 : 0.005, 12 : 0.003, 13 : 0.001,
                         14 : 0.0005, 15 : 0.0003, 16 : 0.0001,
                         17 : 0.0001, 18 : 0.0001
                         }.get(config.get("geography.zoom"), 5.0)
                latp = precision % lat
                lonp = precision % lon
                mlatp = precision % float(mark[1])
                mlonp = precision % float(mark[2])
                latok = lonok = False
                if (float(mlatp) >= (float(latp) - shift)) and \
                   (float(mlatp) <= (float(latp) + shift)):
                    latok = True
                if (float(mlonp) >= (float(lonp) - shift)) and \
                   (float(mlonp) <= (float(lonp) + shift)):
                    lonok = True
                if latok and lonok:
                    mark_selected.append(mark)
        _LOG.debug("%s", time.strftime("  end is_there_a_place_here : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))
        return mark_selected

    def build_nav_menu(self, osm, event, lat, lon):
        """
        Must be implemented in the caller class
        """
        raise NotImplementedError

    def is_there_a_marker_here(self, event, lat, lon):
        """
        Must be implemented in the caller class
        """
        raise NotImplementedError

    def set_crosshair(self, active):
        """
        Show or hide the crosshair ?
        """
        if active:
            self.osm.layer_remove(self.cross_map)
            self.cross_map = osmgpsmap.MapOsd(show_crosshair=True)
            self.osm.layer_add(self.cross_map)
        else:
            self.osm.layer_remove(self.cross_map)
            self.cross_map = osmgpsmap.MapOsd(show_crosshair=False)
            self.osm.layer_add(self.cross_map)
