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
from gen.ggettext import sgettext as _
from gen.ggettext import ngettext
import sys
import os
import gobject
import time

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".geography")

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
import gen.lib
import Utils
from gui.views.navigationview import NavigationView
from libformatting import FormattingHelper
import Errors
import Bookmarks
import const
import constfunc
from grampsmaps import *
import constants
from config import config
from gui.editors import EditPlace, EditEvent, EditFamily, EditPerson
from gui.selectors.selectplace import SelectPlace

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
GEOGRAPHY_PATH = os.path.join(const.HOME_DIR, "maps")

#-------------------------------------------------------------------------
#
# Functions
#
#-------------------------------------------------------------------------
def _get_sign(value):
    """
    return 1 if we have a negative number, 0 in other case
    """
    if value < 0.0:
        return 1
    else:
        return 0

def _get_zoom_lat(value):
    """
    return the zoom value for latitude depending on the distance.
    """
    zoomlat = 1
    for i, distance in enumerate([80.0, 40.0, 20.0, 10.0, 3.0,
                           2.0, 1.0, 0.5, 0.2, 0.1]):
        if value < distance:
            zoomlat = i+1
    return zoomlat + 3

def _get_zoom_long(value):
    """
    return the zoom value for longitude depending on the distance.
    """
    zoomlong = 1
    for i, distance in enumerate([120.0, 60.0, 30.0, 15.0, 7.0,
                           4.0, 2.0, 1.0, .5, .2, .1]):
        if value < distance:
            zoomlong = i+1
    return zoomlong + 3

#-------------------------------------------------------------------------
#
# GeoGraphyView
#
#-------------------------------------------------------------------------
class GeoGraphyView(osmGpsMap, NavigationView):
    """
    View for pedigree tree.
    Displays the ancestors of a selected individual.
    """
    #settings in the config file
    CONFIGSETTINGS = (
        ('geography.path', GEOGRAPHY_PATH),

        ('geography.zoom', 10),
        ('geography.show_cross', True),
        ('geography.lock', False),
        ('geography.center-lat', 0.0),
        ('geography.center-lon', 0.0),

        #('geography.gps_mode', GPS_DISABLED),
        #('geography.gps_update_rate', float(1.0)),
        #('geography.max_gps_zoom', 16),
        #('geography.gps_increment', GPS_INCREMENT),

        ('geography.map_service', constants.OPENSTREETMAP),
        )

    def __init__(self, title, pdata, dbstate, uistate,
                 get_bookmarks, bm_type, nav_group):
        NavigationView.__init__(self, title, pdata, dbstate, uistate, 
                              get_bookmarks, bm_type, nav_group)

        self.dbstate = dbstate
        self.dbstate.connect('database-changed', self.change_db)
        self.default_text = "Enter location here!"
        self.centerlon = config.get("geography.center-lon")
        self.centerlat = config.get("geography.center-lat")
        self.zoom = config.get("geography.zoom")
        self.lock = config.get("geography.lock")
        if config.get('geography.path') == "" :
            config.set('geography.path', GEOGRAPHY_PATH )
        osmGpsMap.__init__(self)
        
        self.format_helper = FormattingHelper(self.dbstate)
        self.centerlat = self.centerlon = 0.0
        self.cross_map = None
        self.current_map = None
        self.without = 0
        self.geo_mainmap = gtk.gdk.pixbuf_new_from_file_at_size(
            os.path.join(const.ROOT_DIR, "images", "22x22",
                         ('gramps-geo-mainmap' + '.png' )),
                                 22, 22)
        self.geo_altmap = gtk.gdk.pixbuf_new_from_file_at_size(
            os.path.join(const.ROOT_DIR, "images", "22x22",
                         ('gramps-geo-altmap' + '.png' )),
                                 22, 22)
        if ( config.get('geography.map_service') in
            ( constants.OPENSTREETMAP, constants.OPENSTREETMAP_RENDERER )):
            default_image = self.geo_mainmap
        else:
            default_image = self.geo_altmap
        self.geo_othermap = {}
        for id in ( gen.lib.EventType.BIRTH,
                    gen.lib.EventType.DEATH,
                    gen.lib.EventType.MARRIAGE ):
            self.geo_othermap[id] = gtk.gdk.pixbuf_new_from_file_at_size(
                os.path.join(const.ROOT_DIR, "images", "22x22",
                    (constants.ICONS.get(int(id), default_image) + '.png' )),
                    22, 22)
        
    def change_page(self):
        """Called when the page changes."""
        NavigationView.change_page(self)
        self.uistate.clear_filter_results()

    def on_delete(self):
        """
        Save all modified environment
        """
        NavigationView.on_delete(self)
        self._config.save()

    def change_db(self, db):
        """
        Callback associated with DbState. Whenever the database
        changes, this task is called. In this case, we rebuild the
        columns, and connect signals to the connected database. Tree
        is no need to store the database, since we will get the value
        from self.state.db
        """
        self.bookmarks.update_bookmarks(self.dbstate.db.get_bookmarks())
        if self.active:
            self.bookmarks.redraw()

    def can_configure(self):
        """
        See :class:`~gui.views.pageview.PageView 
        :return: bool
        """
        return True

    def config_connect(self):
        """
        Overwriten from  :class:`~gui.views.pageview.PageView method
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """

    #-------------------------------------------------------------------------
    #
    # Map Menu
    #
    #-------------------------------------------------------------------------
    def build_nav_menu(self, obj, event, lat, lon):
        """Builds the menu for actions on the map."""
        menu = gtk.Menu()
        menu.set_title(_('Map Menu'))

        if config.get("geography.show_cross"):
            title = _('Remove cross hair')
        else:
            title = _('Add cross hair')
        add_item = gtk.MenuItem(title)
        add_item.connect("activate", self.config_crosshair, event, lat , lon)
        add_item.show()
        menu.append(add_item)

        if config.get("geography.lock"):
            title = _('Unlock zoom and position')
        else:
            title = _('Lock zoom and position')
        add_item = gtk.MenuItem(title)
        add_item.connect("activate", self.config_zoom_and_position,
                         event, lat , lon)
        add_item.show()
        menu.append(add_item)

        add_item = gtk.MenuItem(_("Add place"))
        add_item.connect("activate", self._add_place, event, lat , lon)
        add_item.show()
        menu.append(add_item)

        add_item = gtk.MenuItem(_("Link place"))
        add_item.connect("activate", self._link_place, event, lat , lon)
        add_item.show()
        menu.append(add_item)

        add_item = gtk.MenuItem(_("Center here"))
        add_item.connect("activate", self.set_center, event, lat , lon)
        add_item.show()
        menu.append(add_item)

        # Add specific module menu
        self.add_specific_menu(menu, event, lat, lon)
        # Add a separator line
        add_item = gtk.MenuItem(None)
        add_item.show()
        menu.append(add_item)

        map_name = constants.map_title[config.get("geography.map_service")]
        title = _("Replace '%(map)s' by =>") % {
                   'map' : map_name
                  }
        add_item = gtk.MenuItem(title)
        add_item.show()
        menu.append(add_item)

        changemap = gtk.Menu()
        changemap.set_title(title)
        changemap.show()
        add_item.set_submenu(changemap)
        # show in the map menu all available providers
        for map in constants.map_type:
            changemapitem = gtk.MenuItem(constants.map_title[map])
            changemapitem.show()
            changemapitem.connect("activate", self.change_map, map)
            changemap.append(changemapitem)
        menu.popup(None, None, None, 0, event.time)
        return 1

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
        self.osm.set_center_and_zoom(lat, lon, 12)
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
        self.uistate.set_busy_cursor(1)
        for mark in self.sort:
            # as we are not precise with our hand, reduce the precision
            # depending on the zoom.
            precision = {
                          1 : '%3.0f', 2 : '%3.0f', 3 : '%3.0f', 4 : '%3.0f',
                          5 : '%3.0f', 6 : '%3.1f', 7 : '%3.1f', 8 : '%3.1f',
                          9 : '%3.1f', 10 : '%3.1f', 11 : '%3.2f', 12 : '%3.2f',
                         13 : '%3.2f', 14 : '%3.3f', 15 : '%3.3f', 16 : '%3.4f',
                         17 : '%3.4f', 18 : '%3.5f'
                         }.get(config.get("geography.zoom"), '%3.1f')
            latp  = precision % lat
            lonp  = precision % lon
            mlatp = precision % float(mark[3])
            mlonp = precision % float(mark[4])
            _LOG.debug(" compare latitude : %s with %s (precision = %s)"
                       " place='%s'" % (float(mark[3]), lat, precision,
                                        mark[0]))
            _LOG.debug("compare longitude : %s with %s (precision = %s)"
                       " zoom=%d" % (float(mark[4]), lon, precision,
                                     config.get("geography.zoom")))
            if mlatp == latp and mlonp == lonp:
                _LOG.debug(" compare latitude : %s with %s OK" % (mlatp, latp))
                _LOG.debug("compare longitude : %s with %s OK" % (mlonp, lonp))
                mark_selected.append(mark)
                found = True
        if found:
            self.bubble_message(event, lat, lon, mark_selected)
        self.uistate.set_busy_cursor(0)

    def bubble_message(self, event, lat, lon, mark):
        """
        Display the bubble message. depends on the view.
        """
        raise NotImplementedError

    def add_marker(self, menu, event, lat, lon, event_type, differtype):
        """
        Add a new marker
        """
        mapservice = config.get('geography.map_service')
        if ( mapservice in ( constants.OPENSTREETMAP,
                             constants.OPENSTREETMAP_RENDERER )):
            default_image = self.geo_mainmap
        else:
            default_image = self.geo_altmap
        value = default_image
        if event_type is not None:
            value = self.geo_othermap.get(int(event_type), default_image)
        if differtype:                   # in case multiple evts
            value = default_image # we use default icon.
        marker = self.osm.image_add_with_alignment(float(lat),
                                                   float(lon), value, 0.2, 1.0)

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
        self.osm.image_remove_all()

    def _present_in_places_list(self, index, string):
        """
        Search a string in place_list depending index
        """
        found = any(p[index] == string for p in self.place_list)
        return found

    def _append_to_places_list(self, place, evttype, name, lat, 
                               longit, descr, year, icontype,
                               gramps_id, place_id, event_id, family_id
                              ):
        """
        Create a list of places with coordinates.
        """
        found = any(p[0] == place for p in self.place_list)
        if not found:
            self.nbplaces += 1
        self.place_list.append([place, name, evttype, lat,
                                longit, descr, year, icontype,
                                gramps_id, place_id, event_id, family_id
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
        if not [gid, place] in self.place_without_coordinates:
            self.place_without_coordinates.append([gid, place])
            self.without += 1

    def _create_markers(self):
        """
        Create all markers for the specified person.
        """
        self.remove_all_markers()
        self.remove_all_gps()
        self.remove_all_tracks()
        if ( self.current_map is not None and
             self.current_map != config.get("geography.map_service") ):
            self.change_map(self.osm, config.get("geography.map_service"))
        last = ""
        current = ""
        differtype = False
        savetype = None
        lat = 0.0
        lon = 0.0
        icon = None
        self.uistate.set_busy_cursor(True)
        _LOG.debug("%s" % time.strftime("start create_marker : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))
        for mark in self.sort:
            current = ([mark[3], mark[4]])
            if last == "":
                last = current
                lat = mark[3]
                lon = mark[4]
                icon = mark[7]
                differtype = False
                continue
            if last != current:
                self.add_marker(None, None, lat, lon, icon, differtype)
                differtype = False
                last = current
                lat = mark[3]
                lon = mark[4]
                icon = mark[7]
                differtype = False
            else: # This marker already exists. add info.
                if ( mark[6] and icon != mark[7] ):
                    differtype = True
        if ( lat != 0.0 and lon != 0.0 ):
            self.add_marker(None, None, lat, lon, icon, differtype)
            self._set_center_and_zoom()
        _LOG.debug("%s" % time.strftime(" stop create_marker : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))
        self.uistate.set_busy_cursor(False)

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
        signminlon = _get_sign(self.minlon)
        signminlat = _get_sign(self.minlat)
        signmaxlon = _get_sign(self.maxlon)
        signmaxlat = _get_sign(self.maxlat)
        # auto zoom ?
        if signminlon == signmaxlon: 
            maxlong = abs(abs(self.minlon) - abs(self.maxlon))
        else:
            maxlong = abs(abs(self.minlon) + abs(self.maxlon))
        if signminlat == signmaxlat:
            maxlat = abs(abs(self.minlat) - abs(self.maxlat))
        else:
            maxlat = abs(abs(self.minlat) + abs(self.maxlat))
        # Calculate the zoom. all places must be displayed on the map.
        zoomlat = _get_zoom_lat(maxlat)
        zoomlong = _get_zoom_long(maxlong)
        self.new_zoom = zoomlat if zoomlat < zoomlong else zoomlong
        self.new_zoom -= 1
        if self.new_zoom < 2:
            self.new_zoom = 2
        # We center the map on a point at the center of all markers
        self.centerlat = maxlat/2
        self.centerlon = maxlong/2
        latit = longt = 0.0
        for mark in self.sort:
            if ( signminlat == signmaxlat ):
                if signminlat == 1: 
                    latit = self.minlat+self.centerlat
                else:
                    latit = self.maxlat-self.centerlat
            elif self.maxlat > self.centerlat:
                latit = self.maxlat-self.centerlat
            else:
                latit = self.minlat+self.centerlat
            if ( signminlon == signmaxlon ):
                if signminlon == 1: 
                    longt = self.minlon+self.centerlon
                else:
                    longt = self.maxlon-self.centerlon
            elif self.maxlon > self.centerlon:
                longt = self.maxlon-self.centerlon
            else:
                longt = self.minlon+self.centerlon
            # all maps: 0.0 for longitude and latitude means no location.
            if latit == longt == 0.0:
                latit = longt = 0.00000001
        self.mustcenter = False
        self.latit = latit
        self.longt = longt
        if not (latit == longt == 0.0):
            self.mustcenter = True
        if config.get("geography.lock"):
            self.osm.set_center_and_zoom(config.get("geography.center-lat"),
                                         config.get("geography.center-lon"),
                                         config.get("geography.zoom") )
        else:
            self.osm.set_center_and_zoom(self.latit, self.longt, self.new_zoom)
            self.save_center(self.latit, self.longt)
            config.set("geography.zoom",self.new_zoom)

    #-------------------------------------------------------------------------
    #
    # Specific functionalities
    #
    #-------------------------------------------------------------------------
    def center_here(self, menu, event, lat, lon, mark): 
        """ 
        Center the map at the marker position
        """ 
        self.set_center(menu, event, float(mark[3]), float(mark[4]))

    def add_place_bubble_message(self, event, lat, lon, marks,
                                 menu, message, mark):
        """
        Create the place menu of a marker
        """
        add_item = gtk.MenuItem()
        add_item.show()
        menu.append(add_item)
        add_item = gtk.MenuItem(message)
        add_item.show()
        menu.append(add_item)
        itemoption = gtk.Menu()
        itemoption.set_title(message)
        itemoption.show()
        add_item.set_submenu(itemoption)
        modify = gtk.MenuItem(_("Edit Place"))
        modify.show()
        modify.connect("activate", self.edit_place, event, lat, lon, mark)
        itemoption.append(modify)
        center = gtk.MenuItem(_("Center on this place"))
        center.show()
        center.connect("activate", self.center_here, event, lat, lon, mark)
        itemoption.append(center)
        add_item = gtk.MenuItem()
        add_item.show()
        menu.append(add_item)

    def edit_place(self, menu, event, lat, lon, mark): 
        """ 
        Edit the selected place at the marker position
        """ 
        _LOG.debug("edit_place : %s" % mark[9])
        # need to add code here to edit the event.
        place = self.dbstate.db.get_place_from_gramps_id(mark[9])
        try:
            EditPlace(self.dbstate, self.uistate, [], place)
        except Errors.WindowActiveError: 
            pass 

    def edit_person(self, menu, event, lat, lon, mark): 
        """ 
        Edit the selected person at the marker position
        """ 
        _LOG.debug("edit_person : %s" % mark[8])
        # need to add code here to edit the person.
        person = self.dbstate.db.get_person_from_gramps_id(mark[8])
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except Errors.WindowActiveError: 
            pass 

    def edit_family(self, menu, event, lat, lon, mark): 
        """ 
        Edit the selected family at the marker position
        """ 
        _LOG.debug("edit_family : %s" % mark[11])
        # need to add code here to edit the family.
        family = self.dbstate.db.get_family_from_gramps_id(mark[11])
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except Errors.WindowActiveError: 
            pass 

    def edit_event(self, menu, event, lat, lon, mark): 
        """ 
        Edit the selected event at the marker position
        """ 
        _LOG.debug("edit_event : %s" % mark[10])
        # need to add code here to edit the event.
        event = self.dbstate.db.get_event_from_gramps_id(mark[10])
        try:
            EditEvent(self.dbstate, self.uistate, [], event)
        except Errors.WindowActiveError: 
            pass 

    def _add_place(self, menu, event, lat, lon): 
        """
        Add a new place using longitude and latitude of location centered
        on the map
        """
        new_place = gen.lib.Place()
        new_place.set_latitude(str(lat))
        new_place.set_longitude(str(lon))
        try:
            EditPlace(self.dbstate, self.uistate, [], new_place)
        except Errors.WindowActiveError: 
            pass 

    def _link_place(self, menu, event, lat, lon): 
        """
        Link an existing place using longitude and latitude of location centered
        on the map
        """
        selector = SelectPlace(self.dbstate, self.uistate, [])
        place = selector.run()
        if place:
            place.set_latitude(str(lat))
            place.set_longitude(str(lon))
            try:
                EditPlace(self.dbstate, self.uistate, [], place)
            except Errors.WindowActiveError: 
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
        return [self.map_options]

    def config_zoom_and_position(self, client, cnxn_id, entry, data):
        """
        Do we need to lock the zoom and position ?
        """
        if config.get("geography.lock"):
            config.set("geography.lock", False)
            self._set_center_and_zoom()
        else:
            config.set("geography.lock", True)
        self.lock = config.get("geography.lock")
        pass

    def config_crosshair(self, client, cnxn_id, entry, data):
        """
        We asked to change the crosshair.
        """
        if config.get("geography.show_cross"):
            config.set("geography.show_cross", False)
        else:
            config.set("geography.show_cross", True)
        self.set_crosshair(config.get("geography.show_cross"))
        pass

    def map_options(self, configdialog):
        """
        Function that builds the widget in the configuration dialog
        for the map options.
        """
        table = gtk.Table(2, 2)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        configdialog.add_text(table,
                _('Where to save the tiles for offline mode.'),
                1)
        configdialog.add_entry(table, '',
                2, 'geography.path')
        configdialog.add_text(table,
                _('If you have no more space in your file system\n'
                  'You can remove all tiles placed in the above path.\n'
                  'Be careful! If you have no internet, you\'ll get no map.'),
                3)
        # there is no button. I need to found a solution for this.
        # it can be very dangerous ! if someone put / in geography.path ...
        # perhaps we need some contrôl on this path :
        # should begin with : /home, /opt, /map, ...
        #configdialog.add_button(table, '', 4, 'geography.clean')
        
        return _('The map'), table
