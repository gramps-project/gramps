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

"""
This module is the base class for all geography view module
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
import re
import time
import logging
import gi
from gi.repository import GLib

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import OsmGpsMap as osmgpsmap

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import EventType, Place, PlaceRef, PlaceName
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gui.views.navigationview import NavigationView
from gramps.gen.utils.libformatting import FormattingHelper
from gramps.gen.errors import WindowActiveError
from gramps.gen.const import HOME_DIR
from gramps.gen.config import config
from gramps.gui.editors import EditPlace, EditEvent, EditFamily, EditPerson
from gramps.gui.selectors.selectplace import SelectPlace
from gramps.gen.utils.file import media_path_full
from gramps.gen.const import GRAMPS_LOCALE as glocale

from . import constants
from .osmgps import OsmGps
from .selectionlayer import SelectionLayer
from .placeselection import PlaceSelection
from .cairoprint import CairoPrintSave
from .libkml import Kml
gi.require_version('OsmGpsMap', '1.0')
_ = glocale.translation.sgettext

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
_LOG = logging.getLogger("maps.geography")

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
GEOGRAPHY_PATH = os.path.join(HOME_DIR, "maps")

#-------------------------------------------------------------------------
#
# Functions and variables
#
#-------------------------------------------------------------------------
PLACE_REGEXP = re.compile('<span background="green">(.*)</span>')
PLACE_STRING = '<span background="green">%s</span>'

def _get_sign(value):
    """
    return 1 if we have a negative number, 0 in other case
    """
    if value < 0.0:
        return 1
    else:
        return 0

#-------------------------------------------------------------------------
#
# GeoGraphyView
#
#-------------------------------------------------------------------------
class GeoGraphyView(OsmGps, NavigationView):
    """
    View for pedigree tree.
    Displays the ancestors of a selected individual.
    """
    #settings in the config file
    CONFIGSETTINGS = (
        ('geography.path', GEOGRAPHY_PATH),

        ('geography.zoom', 10),
        ('geography.zoom_when_center', 12),
        ('geography.show_cross', True),
        ('geography.lock', False),
        ('geography.center-lat', 0.0),
        ('geography.center-lon', 0.0),

        ('geography.map_service', constants.OPENSTREETMAP),
        ('geography.max_places', 5000),
        ('geography.use-keypad', True),
        ('geography.personal-map', ""),
        )

    def __init__(self, title, pdata, dbstate, uistate,
                 bm_type, nav_group):
        NavigationView.__init__(self, title, pdata, dbstate, uistate,
                                bm_type, nav_group)

        OsmGps.__init__(self, uistate)
        self.dbstate = dbstate
        self.dbstate.connect('database-changed', self.change_db)
        self.dbstate.connect('no-database', self.clear_view)
        self.default_text = "Enter location here!"
        self.centerlon = config.get("geography.center-lon")
        self.centerlat = config.get("geography.center-lat")
        self.zoom = config.get("geography.zoom")
        self.lock = config.get("geography.lock")
        if config.get('geography.path') == "":
            config.set('geography.path', GEOGRAPHY_PATH)
        if not config.is_set('geography.personal-map'):
            config.set('geography.personal-map', "")

        self.uistate = uistate
        self.uistate.connect('font-changed', self.font_changed)
        self.uistate.connect('nameformat-changed', self.build_tree)
        self.format_helper = FormattingHelper(self.dbstate, self.uistate)
        self.centerlat = self.centerlon = 0.0
        self.cross_map = None
        self.current_map = None
        self.without = 0
        self.place_list = []
        self.places_found = []
        self.select_fct = None
        self.geo_mainmap = None
        self.reloadtiles = None
        theme = Gtk.IconTheme.get_default()
        self.geo_mainmap = theme.load_surface('gramps-geo-mainmap', 48, 1,
                                              None, 0)
        self.geo_altmap = theme.load_surface('gramps-geo-altmap', 48, 1,
                                             None, 0)
        self.sort = []
        self.geo_othermap = {}
        for ident in (EventType.BIRTH,
                      EventType.DEATH,
                      EventType.MARRIAGE):
            icon = constants.ICONS.get(int(ident))
            self.geo_othermap[ident] = theme.load_surface(icon, 48, 1, None, 0)
        self.maxyear = 0
        self.minyear = 9999
        self.maxlat = 0.0
        self.minlat = 0.0
        self.maxlon = 0.0
        self.minlon = 0.0
        self.longt = 0.0
        self.latit = 0.0
        self.itemoption = None
        self.menu = None
        self.mark = None
        self.path_entry = None
        self.changemap = None
        self.clearmap = None
        self.nbplaces = 0
        self.nbmarkers = 0
        self.place_without_coordinates = []

    def font_changed(self):
        """
        The font or the death symbol changed.
        """
        self.build_tree()

    def add_bookmark(self, menu):
        """
        Add the place to the bookmark
        """
        dummy_menu = menu
        mlist = self.selected_handles()
        if mlist:
            self.bookmarks.add(mlist[0])
        else:
            from gramps.gui.dialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"),
                _("A bookmark could not be set because "
                  "no one was selected."),
                parent=self.uistate.window)

    def add_bookmark_from_popup(self, menu, handle):
        """
        Add the place to the bookmark from the popup menu
        """
        dummy_menu = menu
        if handle:
            self.uistate.set_active(handle, self.navigation_type())
            self.bookmarks.add(handle)
            self.bookmarks.redraw()
        else:
            from gramps.gui.dialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"),
                _("A bookmark could not be set because "
                  "no one was selected."),
                parent=self.uistate.window)

    def change_page(self):
        """
        Called when the page changes.
        """
        NavigationView.change_page(self)
        self.uistate.clear_filter_results()
        self.end_selection = None
        if self.osm:
            self.osm.grab_focus()
            self.set_crosshair(config.get("geography.show_cross"))

    def do_size_request(self, requisition):
        """
        Overridden method to handle size request events.
        """
        requisition.width = 400
        requisition.height = 300

    def do_get_preferred_width(self):
        """ GTK3 uses width for height sizing model. This method will
            override the virtual method
        """
        req = Gtk.Requisition()
        self.do_size_request(req)
        return req.width, req.width

    def do_get_preferred_height(self):
        """ GTK3 uses width for height sizing model. This method will
            override the virtual method
        """
        req = Gtk.Requisition()
        self.do_size_request(req)
        return req.height, req.height

    def on_delete(self):
        """
        Save all modified environment
        """
        NavigationView.on_delete(self)
        self._config.save()

    def clear_view(self):
        """
        Clear the map: places, markers, tracks, messages...
        """
        self.place_list = []
        self.remove_all_markers()
        self.remove_all_gps()
        self.remove_all_tracks()
        self.message_layer.clear_messages()

    def change_db(self, dbse):
        """
        Callback associated with DbState. Whenever the database
        changes, this task is called. In this case, we rebuild the
        columns, and connect signals to the connected database. Tree
        is no need to store the database, since we will get the value
        from self.state.db
        """
        dummy_dbse = dbse
        if self.active:
            self.bookmarks.redraw()
        self.build_tree()
        if self.osm:
            self.osm.grab_focus()
            self.set_crosshair(config.get("geography.show_cross"))

    def can_configure(self):
        """
        See :class:`~gui.views.pageview.PageView
        :return: bool
        """
        return True

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required.
        As this function is overriden in some plugins, we need to call
        another method.
        """
        NavigationView.define_actions(self)
        self._add_action('PrintView', self.printview, '<PRIMARY><SHIFT>P')

    def config_connect(self):
        """
        Overwriten from  :class:`~gui.views.pageview.PageView method
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """
        self._config.connect("geography.path",
                             self.set_path)
        self._config.connect("geography.zoom_when_center",
                             self.set_zoom_when_center)

    def set_path(self, client, cnxn_id, entry, data):
        """
        All geography views must have the same path for maps
        """
        dummy_client = client
        dummy_cnxn_id = cnxn_id
        dummy_data = data
        config.set("geography.path", entry)

    def set_zoom_when_center(self, client, cnxn_id, entry, data):
        """
        All geography views must have the same zoom_when_center for maps
        """
        dummy_client = client
        dummy_cnxn_id = cnxn_id
        dummy_data = data
        config.set("geography.zoom_when_center", int(entry))

    #-------------------------------------------------------------------------
    #
    # Map Menu
    #
    #-------------------------------------------------------------------------
    def build_nav_menu(self, osm, event, lat, lon):
        """
        Builds the menu for actions on the map.
        """
        self.menu = Gtk.Menu()
        menu = self.menu

        if config.get("geography.show_cross"):
            title = _('Remove cross hair')
        else:
            title = _('Add cross hair')
        add_item = Gtk.MenuItem(label=title)
        add_item.connect("activate", self.config_crosshair, event, lat, lon)
        add_item.show()
        menu.append(add_item)

        if config.get("geography.lock"):
            title = _('Unlock zoom and position')
        else:
            title = _('Lock zoom and position')
        add_item = Gtk.MenuItem(label=title)
        add_item.connect("activate", self.config_zoom_and_position,
                         event, lat, lon)
        add_item.show()
        menu.append(add_item)

        add_item = Gtk.MenuItem(label=_("Add place"))
        add_item.connect("activate", self.add_place, event, lat, lon)
        add_item.show()
        menu.append(add_item)

        add_item = Gtk.MenuItem(label=_("Link place"))
        add_item.connect("activate", self.link_place, event, lat, lon)
        add_item.show()
        menu.append(add_item)

        add_item = Gtk.MenuItem(label=_("Add place from kml"))
        add_item.connect("activate", self.add_place_from_kml, event, lat, lon)
        add_item.show()
        menu.append(add_item)

        add_item = Gtk.MenuItem(label=_("Center here"))
        add_item.connect("activate", self.set_center, event, lat, lon)
        add_item.show()
        menu.append(add_item)

        # Add specific module menu
        self.add_specific_menu(menu, event, lat, lon)
        # Add a separator line
        add_item = Gtk.MenuItem()
        add_item.show()
        menu.append(add_item)

        map_name = constants.MAP_TITLE[config.get("geography.map_service")]
        title = _("Replace '%(map)s' by =>") % {'map' : map_name}
        add_item = Gtk.MenuItem(label=title)
        add_item.show()
        menu.append(add_item)

        self.changemap = Gtk.Menu()
        changemap = self.changemap
        changemap.show()
        add_item.set_submenu(changemap)
        # show in the map menu all available providers
        for my_map in constants.MAP_TYPE:
            changemapitem = Gtk.MenuItem(label=constants.MAP_TITLE[my_map])
            changemapitem.show()
            changemapitem.connect("activate", self.change_map, my_map)
            changemap.append(changemapitem)

        reload_text = _("Reload all visible tiles for '%(map)s'.") % {
            'map' : map_name}
        self.reloadtiles = Gtk.MenuItem(label=reload_text)
        reloadtiles = self.reloadtiles
        reloadtiles.connect("activate", self.reload_visible_tiles)

        reloadtiles.show()
        menu.append(reloadtiles)

        clear_text = _("Clear the '%(map)s' tiles cache.") % {
            'map' : map_name}
        self.clearmap = Gtk.MenuItem(label=clear_text)
        clearmap = self.clearmap
        clearmap.connect("activate", self.clear_map,
                         constants.TILES_PATH[config.get(
                             "geography.map_service")])

        clearmap.show()
        menu.append(clearmap)
        menu.show()
        menu.popup(None, None, None,
                   None, event.button, event.time)
        return 1

    def reload_visible_tiles(self, menu):
        """
        We need to reload all visible tiles for the current map
        """
        dummy_menu = menu
        self.reload_tiles()

    def clear_map(self, menu, the_map):
        """
        We need to clean the tiles cache for the current map
        """
        dummy_menu = menu
        import shutil

        path = "%s%c%s" % (config.get('geography.path'), os.sep, the_map)
        shutil.rmtree(path, ignore_errors=True)

    def add_specific_menu(self, menu, event, lat, lon):
        """
        Add specific entry to the navigation menu.
        Must be done in the associated menu.
        """
        raise NotImplementedError

    def set_center(self, menu, event, lat, lon):
        """
        Center the map at the new position then save it.
        """
        dummy_menu = menu
        dummy_event = event
        self.osm.set_center_and_zoom(lat, lon,
                                     config.get("geography.zoom_when_center"))
        self.save_center(lat, lon)

    #-------------------------------------------------------------------------
    #
    # Markers management
    #
    #-------------------------------------------------------------------------
    def is_there_a_marker_here(self, event, lat, lon):
        """
        Is there a marker at this position ?
        """
        found = False
        mark_selected = []
        self.uistate.set_busy_cursor(True)
        for mark in self.sort:
            # as we are not precise with our hand, reduce the precision
            # depending on the zoom.
            precision = {1 : '%3.0f', 2 : '%3.1f', 3 : '%3.1f', 4 : '%3.1f',
                         5 : '%3.2f', 6 : '%3.2f', 7 : '%3.2f', 8 : '%3.3f',
                         9 : '%3.3f', 10 : '%3.3f', 11 : '%3.3f', 12 : '%3.3f',
                         13 : '%3.3f', 14 : '%3.4f', 15 : '%3.4f', 16 : '%3.4f',
                         17 : '%3.4f', 18 : '%3.4f'
                        }.get(config.get("geography.zoom"), '%3.1f')
            shift = {1 : 5.0, 2 : 5.0, 3 : 3.0,
                     4 : 1.0, 5 : 0.5, 6 : 0.3, 7 : 0.15,
                     8 : 0.06, 9 : 0.03, 10 : 0.015,
                     11 : 0.005, 12 : 0.003, 13 : 0.001,
                     14 : 0.0005, 15 : 0.0003, 16 : 0.0001,
                     17 : 0.0001, 18 : 0.0001
                    }.get(config.get("geography.zoom"), 5.0)
            latp = precision % lat
            lonp = precision % lon
            mlatp = precision % float(mark[3])
            mlonp = precision % float(mark[4])
            latok = lonok = False
            _LOG.debug(" compare latitude : %s with %s (precision = %s)"
                       " place='%s'", float(mark[3]), lat, precision, mark[0])
            _LOG.debug("compare longitude : %s with %s (precision = %s)"
                       " zoom=%d", float(mark[4]), lon, precision,
                       config.get("geography.zoom"))
            if (float(mlatp) >= (float(latp) - shift)) and \
               (float(mlatp) <= (float(latp) + shift)):
                latok = True
            if (float(mlonp) >= (float(lonp) - shift)) and \
               (float(mlonp) <= (float(lonp) + shift)):
                lonok = True
            if latok and lonok:
                mark_selected.append(mark)
                found = True
        if found:
            self.bubble_message(event, lat, lon, mark_selected)
        self.uistate.set_busy_cursor(False)

    def bubble_message(self, event, lat, lon, mark):
        """
        Display the bubble message. depends on the view.
        """
        raise NotImplementedError

    def add_selection_layer(self):
        """
        add the selection layer
        """
        selection_layer = SelectionLayer()
        self.osm.layer_add(selection_layer)
        return selection_layer

    def remove_layer(self, layer):
        """
        Remove the specified layer
        """
        self.osm.remove_layer(layer)

    def add_marker(self, menu, event, lat, lon, event_type, differtype,
                   count, color=None):
        """
        Add a new marker
        """
        dummy_menu = menu
        dummy_event = event
        mapservice = config.get('geography.map_service')
        if (mapservice in (constants.OPENSTREETMAP,
                           constants.OPENSTREETMAP_RENDERER)):
            default_image = self.geo_mainmap
        else:
            default_image = self.geo_altmap
        value = default_image
        if event_type is not None:
            value = self.geo_othermap.get(int(event_type), default_image)
        if differtype:                   # in case multiple evts
            value = default_image # we use default icon.
        self.marker_layer.add_marker((float(lat), float(lon)), value,
                                     count, color=color)

    def remove_all_gps(self):
        """
        Remove all gps points on the map
        """
        self.osm.gps_clear()

    def remove_all_tracks(self):
        """
        Remove all tracks on the map
        """
        self.osm.track_remove_all()

    def remove_all_markers(self):
        """
        Remove all markers on the map
        """
        self.marker_layer.clear_markers()

    def _present_in_places_list(self, index, string):
        """
        Search a string in place_list depending index
        """
        found = any(p[index] == string for p in self.place_list)
        return found

    def _append_to_places_list(self, place, evttype, name, lat,
                               longit, descr, year, icontype,
                               gramps_id, place_id, event_id, family_id,
                               color=None
                              ):
        """
        Create a list of places with coordinates.
        """
        found = any(p[0] == place for p in self.places_found)
        if not found and (self.nbplaces <
                          self._config.get("geography.max_places")):
            # We only show the first "geography.max_places".
            # over 3000 or 4000 places, the geography become unusable.
            # In this case, filter the places ...
            self.nbplaces += 1
            self.places_found.append([place, lat, longit])
        self.place_list.append([place, name, evttype, lat,
                                longit, descr, year, icontype,
                                gramps_id, place_id, event_id, family_id,
                                color
                               ])
        self.nbmarkers += 1
        tfa = float(lat)
        tfb = float(longit)
        if year is not None:
            tfc = int(year)
            if tfc != 0:
                if tfc < self.minyear:
                    self.minyear = tfc
                if tfc > self.maxyear:
                    self.maxyear = tfc
        tfa += 0.00000001 if tfa >= 0 else -0.00000001
        tfb += 0.00000001 if tfb >= 0 else -0.00000001
        if self.minlat == 0.0 or tfa < self.minlat:
            self.minlat = tfa
        if self.maxlat == 0.0 or tfa > self.maxlat:
            self.maxlat = tfa
        if self.minlon == 0.0 or tfb < self.minlon:
            self.minlon = tfb
        if self.maxlon == 0.0 or tfb > self.maxlon:
            self.maxlon = tfb

    def _append_to_places_without_coord(self, gid, place):
        """
        Create a list of places without coordinates.
        """
        if [gid, place] not in self.place_without_coordinates:
            self.place_without_coordinates.append([gid, place])
            self.without += 1

    def _create_markers(self):
        """
        Create all markers for the specified person.
        """
        if self.marker_layer is None:
            return
        self.remove_all_markers()
        self.remove_all_gps()
        self.remove_all_tracks()
        if (self.current_map is not None and
                self.current_map != config.get("geography.map_service")):
            self.change_map(self.osm, config.get("geography.map_service"))
        last = ""
        current = ""
        differtype = False
        lat = 0.0
        lon = 0.0
        icon = None
        count = 0
        colour = None
        self.uistate.set_busy_cursor(True)
        _LOG.debug("%s", time.strftime("start create_marker : "
                                       "%a %d %b %Y %H:%M:%S", time.gmtime()))
        for mark in self.sort:
            current = ([mark[3], mark[4]])
            if last == "":
                last = current
                lat = mark[3]
                lon = mark[4]
                icon = mark[7]
                colour = mark[12]
                differtype = False
                count = 1
                continue
            if last != current:
                self.add_marker(None, None, lat, lon, icon, differtype,
                                count, color=colour)
                differtype = False
                count = 1
                last = current
                lat = mark[3]
                lon = mark[4]
                icon = mark[7]
                colour = mark[12]
            else: # This marker already exists. add info.
                count += 1
                if icon != mark[7]:
                    differtype = True
        if lat != 0.0 and lon != 0.0:
            self.add_marker(None, None, lat, lon, icon, differtype,
                            count, color=colour)
            self._set_center_and_zoom()
        _LOG.debug("%s", time.strftime(" stop create_marker : "
                                       "%a %d %b %Y %H:%M:%S", time.gmtime()))
        self.uistate.set_busy_cursor(False)

    def _visible_marker(self, lat, lon):
        """
        Is this marker in the visible area ?
        """
        bbox = self.osm.get_bbox()
        s_lon = lon + 10.0
        s_lat = lat + 10.0
        pt1 = bbox[0]
        s_bbox_lat1 = pt1.rlat + 10.0
        s_bbox_lon1 = pt1.rlon + 10.0
        pt2 = bbox[1]
        s_bbox_lat2 = pt2.rlat + 10.0
        s_bbox_lon2 = pt2.rlon + 10.0
        result = ((s_bbox_lat1 > s_lat > s_bbox_lat2) and
                  (s_bbox_lon1 < s_lon < s_bbox_lon2))
        return result

    def _autozoom_in(self, lvl, p1lat, p1lon, p2lat, p2lon):
        """
        We zoom in until at least one marker missing.
        """
        if ((self._visible_marker(p1lat, p1lon)
             and self._visible_marker(p2lat, p2lon)) and lvl < 18):
            lvl += 1
            self.osm.set_zoom(lvl)
            GLib.timeout_add(int(50), self._autozoom_in, lvl,
                             p1lat, p1lon, p2lat, p2lon)
        else:
            GLib.timeout_add(int(50), self._autozoom_out, lvl,
                             p1lat, p1lon, p2lat, p2lon)

    def _autozoom_out(self, lvl, p1lat, p1lon, p2lat, p2lon):
        """
        We zoom out until all markers visible.
        """
        if (not (self._visible_marker(p1lat, p1lon)
                 and self._visible_marker(p2lat, p2lon)) and lvl > 1):
            lvl -= 1
            self.osm.set_zoom(lvl)
            GLib.timeout_add(int(50), self._autozoom_out, lvl,
                             p1lat, p1lon, p2lat, p2lon)
        else:
            layer = self.get_selection_layer()
            if layer:
                self.osm.layer_remove(layer)

    def _autozoom(self):
        """
        Try to put all markers on the map.  we start at current zoom.
        If all markers are present, continue to zoom.
        If some markers are missing : return to the zoom - 1
        We must use function called by timeout to force map updates.
        """
        level_start = self.osm.props.zoom
        p1lat, p1lon = self.begin_selection.get_degrees()
        p2lat, p2lon = self.end_selection.get_degrees()
        lat = p1lat + (p2lat - p1lat) / 2
        lon = p1lon + (p2lon - p1lon) / 2
        # We center the map on the center of the region
        self.osm.set_center(lat, lon)
        self.save_center(lat, lon)
        p1lat = self.begin_selection.rlat
        p1lon = self.begin_selection.rlon
        p2lat = self.end_selection.rlat
        p2lon = self.end_selection.rlon
        # We zoom in until at least one marker missing.
        GLib.timeout_add(int(50), self._autozoom_in, level_start,
                         p1lat, p1lon, p2lat, p2lon)

    def _set_center_and_zoom(self):
        """
        Calculate the zoom.
        The best should be an auto zoom to have all markers on the screen.
        need some works here.
        we start at zoom 1 until zoom y ( for this a preference )
        If all markers are present, continue to zoom.
        If some markers are missing : return to the zoom - 1
        The following is too complex. In some case, all markers are not present.
        """
        # Select the center of the map and the zoom
        current = osmgpsmap.MapPoint.new_degrees(self.minlat, self.minlon)
        self.end_selection = current
        current = osmgpsmap.MapPoint.new_degrees(self.maxlat, self.maxlon)
        self.begin_selection = current
        if config.get("geography.lock"):
            self.osm.set_center_and_zoom(config.get("geography.center-lat"),
                                         config.get("geography.center-lon"),
                                         config.get("geography.zoom"))
        else:
            self._autozoom()
            config.set("geography.zoom", self.osm.props.zoom)
        self.end_selection = None

    def _get_father_and_mother_name(self, event):
        """
        Return the father and mother name of a family event
        """
        dbstate = self.dbstate
        family_list = [
            dbstate.db.get_family_from_handle(ref_handle)
            for (ref_type, ref_handle) in
            dbstate.db.find_backlink_handles(event.handle)
            if ref_type == 'Family']
        fnam = mnam = _("Unknown")
        if family_list:
            for family in family_list:
                father = mother = None
                handle = family.get_father_handle()
                if handle:
                    father = dbstate.db.get_person_from_handle(handle)
                handle = family.get_mother_handle()
                if handle:
                    mother = dbstate.db.get_person_from_handle(handle)
                fnam = _nd.display(father) if father else _("Unknown")
                mnam = _nd.display(mother) if mother else _("Unknown")
        return (fnam, mnam)

    #-------------------------------------------------------------------------
    #
    # KML functionalities
    #
    #-------------------------------------------------------------------------
    def load_kml_files(self, obj):
        """
        obj can be an event, a person or a place
        """
        media_list = obj.get_media_list()
        if media_list:
            for media_ref in media_list:
                object_handle = media_ref.get_reference_handle()
                media_obj = self.dbstate.db.get_media_from_handle(object_handle)
                path = media_obj.get_path()
                dummy_name, extension = os.path.splitext(path)
                if extension == ".kml":
                    path = media_path_full(self.dbstate.db, path)
                    if os.path.isfile(path):
                        self.kml_layer.add_kml(path)

    #-------------------------------------------------------------------------
    #
    # Printing functionalities
    #
    #-------------------------------------------------------------------------
    def printview(self, *obj):
        """
        Print or save the view that is currently shown
        """
        dummy_obj = obj
        if Gtk.MAJOR_VERSION == 3 and Gtk.MINOR_VERSION < 11:
            from gramps.gui.dialog import WarningDialog
            WarningDialog(
                _("You can't use the print functionality"),
                _("Your Gtk version is too old."),
                parent=self.uistate.window)
            return

        req = self.osm.get_allocation()
        widthpx = req.width
        heightpx = req.height
        prt = CairoPrintSave(widthpx, heightpx, self.osm.do_draw, self.osm)
        prt.run()

    #-------------------------------------------------------------------------
    #
    # Specific functionalities
    #
    #-------------------------------------------------------------------------
    def center_here(self, menu, event, lat, lon, mark):
        """
        Center the map at the marker position
        """
        dummy_lat = lat
        dummy_lon = lon
        self.set_center(menu, event, float(mark[3]), float(mark[4]))

    def add_place_bubble_message(self, event, lat, lon, marks,
                                 menu, message, mark):
        """
        Create the place menu of a marker
        """
        dummy_marks = marks
        add_item = Gtk.MenuItem()
        add_item.show()
        menu.append(add_item)
        add_item = Gtk.MenuItem(label=message)
        add_item.show()
        menu.append(add_item)
        self.itemoption = Gtk.Menu()
        itemoption = self.itemoption
        itemoption.show()
        add_item.set_submenu(itemoption)
        modify = Gtk.MenuItem(label=_("Edit Place"))
        modify.show()
        modify.connect("activate", self.edit_place, event, lat, lon, mark)
        itemoption.append(modify)
        center = Gtk.MenuItem(label=_("Center on this place"))
        center.show()
        center.connect("activate", self.center_here, event, lat, lon, mark)
        itemoption.append(center)
        add_item = Gtk.MenuItem()
        add_item.show()
        menu.append(add_item)

    def edit_place(self, menu, event, lat, lon, mark):
        """
        Edit the selected place at the marker position
        """
        dummy_menu = menu
        dummy_event = event
        self.mark = mark
        place = self.dbstate.db.get_place_from_gramps_id(self.mark[9])
        parent_list = place.get_placeref_list()
        if parent_list:
            parent = parent_list[0].ref
        else:
            parent = None
        self.select_fct = PlaceSelection(self.uistate, self.dbstate, self.osm,
                                         self.selection_layer, self.place_list,
                                         lat, lon, self.__edit_place, parent)

    def edit_person(self, menu, event, lat, lon, mark):
        """
        Edit the selected person at the marker position
        """
        dummy_menu = menu
        dummy_event = event
        dummy_lat = lat
        dummy_lon = lon
        _LOG.debug("edit_person : %s", mark[8])
        # need to add code here to edit the person.
        person = self.dbstate.db.get_person_from_gramps_id(mark[8])
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except WindowActiveError:
            pass

    def edit_family(self, menu, event, lat, lon, mark):
        """
        Edit the selected family at the marker position
        """
        dummy_menu = menu
        dummy_event = event
        dummy_lat = lat
        dummy_lon = lon
        _LOG.debug("edit_family : %s", mark[11])
        family = self.dbstate.db.get_family_from_gramps_id(mark[11])
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass

    def edit_event(self, menu, event, lat, lon, mark):
        """
        Edit the selected event at the marker position
        """
        dummy_menu = menu
        dummy_lat = lat
        dummy_lon = lon
        _LOG.debug("edit_event : %s", mark[10])
        event = self.dbstate.db.get_event_from_gramps_id(mark[10])
        try:
            EditEvent(self.dbstate, self.uistate, [], event)
        except WindowActiveError:
            pass

    def add_place(self, menu, event, lat, lon):
        """
        Add a new place using longitude and latitude of location centered
        on the map
        """
        dummy_menu = menu
        dummy_event = event
        self.select_fct = PlaceSelection(self.uistate, self.dbstate, self.osm,
                                         self.selection_layer, self.place_list,
                                         lat, lon, self.__add_place)

    def add_place_from_kml(self, menu, event, lat, lon):
        """
        Add new place(s) from a kml file

        1 - ask for a kml file ?
        2 - Read the kml file.
        3 - create the place(s) with name and title found in the kml marker.

        """
        dummy_menu = menu
        dummy_event = event
        dummy_lat = lat
        dummy_lon = lon
        # Ask for the kml file
        filtering = Gtk.FileFilter()
        filtering.add_pattern("*.kml")
        kml = Gtk.FileChooserDialog(
            title=_("Select a kml file used to add places"),
            action=Gtk.FileChooserAction.OPEN,
            transient_for=self.uistate.window)
        kml.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL,
                        _('_Apply'), Gtk.ResponseType.OK)
        mpath = HOME_DIR
        kml.set_current_folder(os.path.dirname(mpath))
        kml.set_filter(filtering)

        status = kml.run()
        if status == Gtk.ResponseType.OK:
            val = kml.get_filename()
            if val:
                kmlfile = Kml(val)
                points = kmlfile.add_points()
                for place in points:
                    (name, coords) = place
                    latlong = coords.pop()
                    (lat, lon) = latlong
                    place_name = PlaceName()
                    place_name.set_value(name)
                    new_place = Place()
                    new_place.set_name(place_name)
                    new_place.set_title(name)
                    new_place.set_latitude(str(lat))
                    new_place.set_longitude(str(lon))
                    try:
                        EditPlace(self.dbstate, self.uistate, [], new_place)
                    except WindowActiveError:
                        pass
        kml.destroy()

    def place_exists(self, place_name):
        """
        Do we have already this place in our database ?
        return the handle for this place.
        """
        found = None
        place_name = place_name.replace('-', ' ').lower()
        for place in self.dbstate.db.iter_places():
            if place.name.get_value().lower() == place_name:
                found = place.handle
                break
        return found

    def link_place(self, menu, event, lat, lon):
        """
        Link an existing place using longitude and latitude of location centered
        on the map
        If we have a place history, we must show all places to avoid an empty
        place selection in the PlaceSelection.
        """
        dummy_menu = menu
        dummy_event = event
        selector = SelectPlace(self.dbstate, self.uistate, [])
        place = selector.run()
        if place:
            parent_list = place.get_placeref_list()
            if parent_list:
                parent = parent_list[0].ref
            else:
                parent = None
            places_handle = self.dbstate.db.iter_place_handles()
            nb_places = 0
            gids = ""
            place_title = _pd.display(self.dbstate.db, place)
            for place_hdl in places_handle:
                plce = self.dbstate.db.get_place_from_handle(place_hdl)
                plce_title = _pd.display(self.dbstate.db, plce)
                if plce_title == place_title:
                    nb_places += 1
                    if gids == "":
                        gids = plce.gramps_id
                    else:
                        # TODO for Arabic, should the next comma be translated?
                        gids = gids + ", " + plce.gramps_id
            if nb_places > 1:
                from gramps.gui.dialog import WarningDialog
                ptitle = place_title
                WarningDialog(
                    _('You have at least two places with the same title.'),
                    _("The title of the places is:\n%(title)s\n"
                      "The following places are similar: %(gid)s\n"
                      "You should eiher rename the places or merge them.\n\n"
                      "%(bold_start)s"
                      "I can't proceed with your request"
                      "%(bold_end)s.\n") % {'bold_start' : '<b>',
                                            'bold_end'   : '</b>',
                                            'title': '<b>' + ptitle + '</b>',
                                            'gid': gids},
                    parent=self.uistate.window)
            else:
                self.mark = [None, None, None, None, None, None, None,
                             None, None, place.gramps_id, None, None]
                self.select_fct = PlaceSelection(self.uistate,
                                                 self.dbstate,
                                                 self.osm,
                                                 self.selection_layer,
                                                 self.place_list,
                                                 lat,
                                                 lon,
                                                 self.__edit_place,
                                                 parent)

    def __add_place(self, parent, plat, plon):
        """
        Add a new place using longitude and latitude of location centered
        on the map
        """
        self.select_fct.close()
        new_place = Place()
        new_place.set_latitude(str(plat))
        new_place.set_longitude(str(plon))
        if parent:
            if isinstance(parent, Place):
                placeref = PlaceRef()
                placeref.ref = parent
                new_place.add_placeref(placeref)
            elif isinstance(parent, gi.overrides.Gtk.TreeModelRow):
                # We are here because we selected a place from geocoding
                # parent[0] : country
                # parent[1] : state
                # parent[2] : town
                # parent[3] : name
                value = PlaceSelection.untag_text(parent[2], 1)
                plname = PlaceName()
                plname.set_value(value)
                handle = self.place_exists(value)
                if handle:
                    # The town already exists. We create a place with name
                    placeref = PlaceRef()
                    placeref.ref = handle
                    new_place.add_placeref(placeref)
                    value = PlaceSelection.untag_text(parent[3], 1)
                    plname.set_value(value)
                new_place.set_name(plname)
            else:
                found = None
                for place in self.dbstate.db.iter_places():
                    found = place
                    if place.name.get_value() == parent:
                        break
                placeref = PlaceRef()
                placeref.ref = found.get_handle()
                new_place.add_placeref(placeref)
        try:
            EditPlace(self.dbstate, self.uistate, [], new_place)
            self.add_marker(None, None, plat, plon, None, True, 0)
        except WindowActiveError:
            pass

    def __edit_place(self, parent, plat, plon):
        """
        Edit the selected place at the marker position
        """
        dummy_parent = parent
        self.select_fct.close()
        place = self.dbstate.db.get_place_from_gramps_id(self.mark[9])
        place.set_latitude(str(plat))
        place.set_longitude(str(plon))
        try:
            EditPlace(self.dbstate, self.uistate, [], place)
        except WindowActiveError:
            pass

    def __link_place(self, parent, plat, plon):
        """
        Link an existing place using longitude and latitude of location centered
        on the map
        """
        selector = SelectPlace(self.dbstate, self.uistate, [])
        place = selector.run()
        if place:
            self.select_fct.close()
            place.set_latitude(str(plat))
            place.set_longitude(str(plon))
            if parent:
                placeref = PlaceRef()
                placeref.ref = parent
                place.add_placeref(placeref)
            try:
                EditPlace(self.dbstate, self.uistate, [], place)
                self.add_marker(None, None, plat, plon, None, True, 0)
            except WindowActiveError:
                pass

    #-------------------------------------------------------------------------
    #
    # Geography preferences
    #
    #-------------------------------------------------------------------------
    def _get_configure_page_funcs(self):
        """
        The function which is used to create the configuration window.
        """
        return [self.map_options, self.specific_options]

    def config_zoom_and_position(self, client, cnxn_id, entry, data):
        """
        Do we need to lock the zoom and position ?
        """
        dummy_client = client
        dummy_cnxn_id = cnxn_id
        dummy_entry = entry
        dummy_data = data
        if config.get("geography.lock"):
            config.set("geography.lock", False)
            self._set_center_and_zoom()
        else:
            config.set("geography.lock", True)
        self.lock = config.get("geography.lock")

    def config_crosshair(self, client, cnxn_id, entry, data):
        """
        We asked to change the crosshair.
        """
        dummy_client = client
        dummy_cnxn_id = cnxn_id
        dummy_entry = entry
        dummy_data = data
        if config.get("geography.show_cross"):
            config.set("geography.show_cross", False)
        else:
            config.set("geography.show_cross", True)
        self.set_crosshair(config.get("geography.show_cross"))

    def specific_options(self, configdialog):
        """
        Add specific entry to the preference menu.
        Must be done in the associated view.
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        configdialog.add_text(grid, _('Nothing for this view.'), 0)
        return _('Specific parameters'), grid

    def map_options(self, configdialog):
        """
        Function that builds the widget in the configuration dialog
        for the map options.
        """
        self._config.set('geography.path', config.get('geography.path'))
        self._config.set('geography.zoom_when_center',
                         config.get('geography.zoom_when_center'))
        self._config.set('geography.max_places',
                         self._config.get('geography.max_places'))
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        self.path_entry = Gtk.Entry()
        configdialog.add_path_box(grid,
                                  _('Where to save the tiles for offline'
                                    ' mode.'),
                                  0, self.path_entry,
                                  config.get('geography.path'),
                                  self.set_tilepath, self.select_tilepath)
        configdialog.add_text(grid,
                              _('If you have no more space in your file system.'
                                ' You can remove all tiles placed in the above'
                                ' path.\nBe careful! If you have no internet,'
                                ' you\'ll get no map.'),
                              2, line_wrap=False)
        configdialog.add_slider(grid, _('Zoom used when centering'),
                                3, 'geography.zoom_when_center',
                                (2, 16))
        configdialog.add_slider(grid, _('The maximum number of places to show'),
                                4, 'geography.max_places',
                                (1000, 10000))
        configdialog.add_checkbox(grid,
                                  _('Use keypad for shortcuts :\nEither we '
                                    'choose the + and - from the keypad if we '
                                    'select this,\nor we use the characters '
                                    'from the keyboard.'),
                                  5, 'geography.use-keypad',
                                  extra_callback=self.update_shortcuts)
        label = configdialog.add_text(
            grid,
            _('If you want to use a specific map provider,'
              ' You can set the following field to the'
              ' provider\'s url.\ni.e:\n'
              'http://tile.stamen.com/toner/#Z/#X/#Y.png\n'
              'http://tile.stamen.com/terrain/#Z/#X/#Y.jpg\n'
              'http://tile.stamen.com/watercolor/#Z/#X/#Y.jpg\n'
              'http://tile.xn--pnvkarte-m4a.de/tilegen/#Z/#X/#Y.png\n'
             ),
            6, line_wrap=False)
        # set the possibility to copy/paste the urls
        label.set_selectable(True)
        start = label.get_text().find("http")
        end = label.get_text().find("http", start + 1)
        label.select_region(start, end)
        url = configdialog.add_entry(grid, _("Personal map"),
                                     7, 'geography.personal-map',
                                     self.choosen_map,
                                    )
        if config.get('geography.personal-map') != "":
            url.set_text(config.get('geography.personal-map'))
        return _('The map'), grid

    def choosen_map(self, *obj):
        """
        Save the provider map path in the config section.
        """
        map_source = obj[0].get_text()
        name = constants.TILES_PATH[constants.PERSONAL]
        print(self.current_map, constants.PERSONAL,
              map_source, config.get('geography.personal-map'))
        config.set('geography.personal-map', map_source)
        self.clear_map(None, name)
        if map_source == "":
            print("reset osm")
            config.set("geography.map_service", constants.OPENSTREETMAP)
            self.change_map(self.osm, config.get("geography.map_service"))
            self.reload_tiles()
            return
        if map_source != config.get('geography.personal-map'):
            print("set personal")
            config.set("geography.map_service", constants.PERSONAL)
            self.change_new_map(name, map_source)
            self.reload_tiles()

    def set_tilepath(self, *obj):
        """
        Save the tile path in the config section.
        """
        dummy_obj = obj
        if self.path_entry.get_text().strip():
            config.set('geography.path', self.path_entry.get_text())
        else:
            config.set('geography.path', GEOGRAPHY_PATH)

    def select_tilepath(self, *obj):
        """
        Call a file chooser selection box to select the tile path.
        """
        dummy_obj = obj
        selected_dir = Gtk.FileChooserDialog(
            title=_("Select tile cache directory for offline mode"),
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            transient_for=self.uistate.window)
        selected_dir.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL,
                                 _('_Apply'), Gtk.ResponseType.OK)
        mpath = config.get('geography.path')
        if not mpath:
            mpath = HOME_DIR
        selected_dir.set_current_folder(os.path.dirname(mpath))

        status = selected_dir.run()
        if status == Gtk.ResponseType.OK:
            val = selected_dir.get_filename()
            if val:
                self.path_entry.set_text(val)
        selected_dir.destroy()
