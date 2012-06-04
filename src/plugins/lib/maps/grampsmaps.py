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
from QuestionDialog import ErrorDialog
import gui.utils

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
        self.rectangles = []

    def add_circle(self, r, lat, lon):
        self.circles.append((r, lat, lon))

    def add_rectangle(self, p1, p2):
        self.rectangles.append((p1, p2))

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
        for rectangle in self.rectangles:
            top_left, bottom_right = rectangle
            x, y = gpsmap.convert_geographic_to_screen(top_left)
            x2, y2 = gpsmap.convert_geographic_to_screen(bottom_right)
            # be sure when can select a region in all case.
            if ( x < x2 ):
                if ( y < y2 ):
                    drawable.draw_rectangle(gc, False, x, y, x2 - x, y2 - y)
                else:
                    drawable.draw_rectangle(gc, False, x, y2, x2 - x, y - y2)
            else:
                if ( y < y2 ):
                    drawable.draw_rectangle(gc, False, x2, y, x - x2, y2 - y)
                else:
                    drawable.draw_rectangle(gc, False, x2, y2, x - x2, y - y2)

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
        self.zone_selection = False
        self.selection_layer = None
        self.context_id = 0
        self.begin_selection = None
        self.end_selection = None

    def build_widget(self):
        self.vbox = gtk.VBox(False, 0)
        cache_path = config.get('geography.path')
        if not os.path.isdir(cache_path):
            try:
                os.makedirs(cache_path, 0755) # create dir like mkdir -p
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
        tiles_path=os.path.join(config.get('geography.path'), constants.tiles_path[map_type])
        if not os.path.isdir(tiles_path):
            try:
                os.makedirs(tiles_path, 0755) # create dir like mkdir -p
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
        self.end_selection = None
        self.osm.layer_add(current_map)
        self.osm.layer_add(DummyLayer())
        self.selection_layer = self.add_selection_layer()
        self.cross_map = osmgpsmap.GpsMapOsd( show_crosshair=False)
        self.set_crosshair(config.get("geography.show_cross"))
        self.osm.set_center_and_zoom(config.get("geography.center-lat"),
                                     config.get("geography.center-lon"),
                                     config.get("geography.zoom") )

        self.osm.connect('button_release_event', self.map_clicked)
        self.osm.connect('button_press_event', self.map_clicked)
        self.osm.connect("motion-notify-event", self.motion_event)
        self.osm.connect('changed', self.zoom_changed)
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
        if self.zone_selection:
                # We draw a rectangle to show the selected region.
                layer = self.get_selection_layer()
                if layer:
                    self.osm.layer_remove(layer)
                self.selection_layer = self.add_selection_layer()
                if self.end_selection == None:
                    self.selection_layer.add_rectangle(self.begin_selection, current)
                else:
                    self.selection_layer.add_rectangle(self.begin_selection, self.end_selection)
        else:
            places = self.is_there_a_place_here(lat, lon)
            mess = ""
            for p in places:
                if mess != "":
                    mess += " || "
                mess += p[0]
            self.uistate.status.pop(self.context_id)
            self.context_id = self.uistate.status.push(1, mess)

    def save_center(self, lat, lon):
        """
        Save the longitude and lontitude in case we switch between maps.
        """
        _LOG.debug("save_center : %s,%s" % (lat, lon) )
        if ( -90.0 < lat < +90.0 ) and ( -180.0 < lon < +180.0 ):
            config.set("geography.center-lat",lat)
            config.set("geography.center-lon",lon)
        else:
            _LOG.debug("save_center : new coordinates : %s,%s" % (lat, lon) )
            _LOG.debug("save_center : old coordinates : %s,%s" % (lat, lon) )
            # osmgpsmap bug ? reset to prior values to avoid osmgpsmap problems.
            self.osm.set_center_and_zoom(config.get("geography.center-lat"),
                                         config.get("geography.center-lon"),
                                         config.get("geography.zoom") )

    def activate_selection_zoom(self, osm, event):
        if self.end_selection is not None:
            self._autozoom()
        return True

    def map_clicked(self, osm, event):
        lat,lon = self.osm.get_event_location(event).get_degrees()
        current = osmgpsmap.point_new_degrees(0.0,0.0)
        osm.convert_screen_to_geographic(int(event.x), int(event.y), current)
        lat, lon = current.get_degrees()
        if event.button == 1:
            if self.end_selection is not None:
                self.activate_selection_zoom(osm, event)
                self.end_selection = None
            else:
                # do we click on a marker ?
                marker = self.is_there_a_marker_here(event, lat, lon)
        elif event.button == 2 and event.type == gtk.gdk.BUTTON_PRESS:
                self.begin_selection = current
                self.end_selection = None
                self.zone_selection = True
        elif event.button == 2 and event.type == gtk.gdk.BUTTON_RELEASE:
                self.end_selection = current
                self.zone_selection = False
        elif gui.utils.is_right_click(event):
            self.build_nav_menu(osm, event, lat, lon )
        else:
            self.save_center(lat,lon)

    def is_there_a_place_here(self, lat, lon):
        """
        Is there a place at this position ?
        """
        found = False
        mark_selected = []
        oldplace = ""
        for mark in self.places_found:
            # as we are not precise with our hand, reduce the precision
            # depending on the zoom.
            if mark[0] != oldplace:
                oldplace = mark[0]
                precision = {
                              1 : '%3.0f', 2 : '%3.1f', 3 : '%3.1f', 4 : '%3.1f',
                              5 : '%3.2f', 6 : '%3.2f', 7 : '%3.2f', 8 : '%3.3f',
                              9 : '%3.3f', 10 : '%3.3f', 11 : '%3.3f', 12 : '%3.3f',
                             13 : '%3.3f', 14 : '%3.4f', 15 : '%3.4f', 16 : '%3.4f',
                             17 : '%3.4f', 18 : '%3.4f'
                             }.get(config.get("geography.zoom"), '%3.1f')
                shift = {
                          1 : 5.0, 2 : 5.0, 3 : 3.0,
                          4 : 1.0, 5 : 0.5, 6 : 0.3, 7 : 0.15,
                          8 : 0.06, 9 : 0.03, 10 : 0.015,
                         11 : 0.005, 12 : 0.003, 13 : 0.001,
                         14 : 0.0005, 15 : 0.0003, 16 : 0.0001,
                         17 : 0.0001, 18 : 0.0001
                         }.get(config.get("geography.zoom"), 5.0)
                latp  = precision % lat
                lonp  = precision % lon
                mlatp = precision % float(mark[1])
                mlonp = precision % float(mark[2])
                latok = lonok = False
                if (float(mlatp) >= (float(latp) - shift) ) and \
                   (float(mlatp) <= (float(latp) + shift) ):
                    latok = True
                if (float(mlonp) >= (float(lonp) - shift) ) and \
                   (float(mlonp) <= (float(lonp) + shift) ):
                    lonok = True
                if latok and lonok:
                    mark_selected.append(mark)
                    found = True
        return mark_selected

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
