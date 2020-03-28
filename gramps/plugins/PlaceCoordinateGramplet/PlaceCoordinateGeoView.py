# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2014 Christian Schulze
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
Geography for places
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
import sys
import time
import operator
from gi.repository import Gdk
KEY_TAB = Gdk.KEY_Tab
import socket
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("GeoGraphy.geoplaces")

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.lib import EventType
from gramps.gen.config import config
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.place import conv_lat_lon
from gramps.gui.views.pageview import PageView
from gramps.gui.editors import EditPlace
from gramps.gui.selectors.selectplace import SelectPlace
from gramps.gui.filters.sidebar import PlaceSidebarFilter
from gramps.gui.views.navigationview import NavigationView
from gramps.gui.views.bookmarks import PlaceBookmarks
from gramps.plugins.lib.maps.geography import GeoGraphyView
from gramps.gen.lib import EventType, Place, PlaceType, PlaceRef
from gramps.gen.errors import WindowActiveError

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

from gramps.plugins.lib.maps import constants

_UI_DEF = '''\
<ui>
<menubar name="MenuBar">
<menu action="GoMenu">
  <placeholder name="CommonGo">
    <menuitem action="Back"/>
    <menuitem action="Forward"/>
    <separator/>
  </placeholder>
</menu>
<menu action="EditMenu">
  <placeholder name="CommonEdit">
    <menuitem action="PrintView"/>
  </placeholder>
</menu>
<menu action="BookMenu">
  <placeholder name="AddEditBook">
    <menuitem action="AddBook"/>
    <menuitem action="EditBook"/>
  </placeholder>
</menu>
</menubar>
<toolbar name="ToolBar">
<placeholder name="CommonNavigation">
  <toolitem action="Back"/>  
  <toolitem action="Forward"/>  
</placeholder>
<placeholder name="CommonEdit">
  <toolitem action="PrintView"/>
</placeholder>
</toolbar>
</ui>
'''

#-------------------------------------------------------------------------
#
# GeoView
#
#-------------------------------------------------------------------------
class PlaceCoordinateGeoView(GeoGraphyView):
    """
    The view used to render places map.
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        GeoGraphyView.__init__(self, _('Places map'),
                                      pdata, dbstate, uistate, 
                                      PlaceBookmarks,
                                      nav_group)
        self.dbstate = dbstate
        self.uistate = uistate
        self.place_list = []
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        self.nbplaces = 0
        self.nbmarkers = 0
        self.sort = []
        self.generic_filter = None
        self.additional_uis.append(self.additional_ui())
        self.no_show_places_in_status_bar = False
#        self.connect_signal('Place', self._active_changed)
#    def active_changed(self, handle):
#        self.update()

    def get_title(self):
        """
        Used to set the titlebar in the configuration window.
        """
        return _('PlaceCoordinateGeoView')

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered 
        as a stock icon.
        """
        return 'geo-show-place'
    
    def get_viewtype_stock(self):
        """Type of view in category
        """
        return 'geo-show-place'

    def additional_ui(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
        return _UI_DEF

    def navigation_type(self):
        """
        Indicates the navigation type. Navigation type can be the string
        name of any of the primary objects.
        """
        return 'Place'

    def goto_handle(self, handle=None):
        """
        Rebuild the tree with the given places handle as the root.
        """
        if (handle==None):
            return
        place = self.dbstate.db.get_place_from_handle(handle)
        if ( place.get_latitude() != "" and place.get_longitude() != "" ):
            try:
                self.goto_place(place, float(place.get_latitude()), float(place.get_longitude()))
            except:
                "dann halt nicht"
#        self.places_found = []
#        self.build_tree()

    def show_all_places(self, menu, event, lat, lon):
        """
        Ask to show all places.
        """
        self._createmap(None)

    def build_tree(self):
        """
        This is called by the parent class when the view becomes visible. Since
        all handling of visibility is now in rebuild_trees, see that for more
        information.
        """
        active = self.uistate.get_active('Place')
        if active:
            self._createmap(active)
        else:
            self._createmap(None)

    def _create_one_place(self,place):
        """
        Create one entry for one place with a lat/lon.
        """
        if place is None:
            return
        if self.nbplaces >= self._config.get("geography.max_places"):
            return
        descr = _pd.display(self.dbstate.db, place)
        longitude = place.get_longitude()
        latitude = place.get_latitude()
        latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
        # place.get_longitude and place.get_latitude return
        # one string. We have coordinates when the two values
        # contains non null string.
        if ( longitude and latitude ):
            self._append_to_places_list(descr, None, "",
                                        latitude, longitude,
                                        None, None,
                                        EventType.UNKNOWN,
                                        None, # person.gramps_id
                                        place.gramps_id,
                                        None, # event.gramps_id
                                        None # family.gramps_id
                                       )
        else:
            self._append_to_places_without_coord(place.gramps_id, descr)

    def _createmap(self,place_x):
        """
        Create all markers for each people's event in the database which has 
        a lat/lon.
        """
        dbstate = self.dbstate
        self.cal = config.get('preferences.calendar-format-report')
        self.place_list = []
        self.place_without_coordinates = []
        self.minlat = 0.0
        self.maxlat = 0.0
        self.minlon = 0.0
        self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        self.without = 0
        latitude = ""
        longitude = ""
        self.nbmarkers = 0
        self.nbplaces = 0
        self.message_layer.clear_messages()
        self.message_layer.clear_font_attributes()
        self.no_show_places_in_status_bar = False
        # base "villes de france" : 38101 places :
        # createmap : 8'50"; create_markers : 1'23"
        # base "villes de france" : 38101 places :
        # createmap : 8'50"; create_markers : 0'07" with pixbuf optimization
        # base "villes de france" : 38101 places :
        # gramps 3.4 python 2.7 ( draw_markers are estimated when we move the map)
        # 38101 places : createmap : 04'32"; create_markers : 0'04"; draw markers : N/A :: 0'03"
        # 65598 places : createmap : 10'03"; create_markers : 0'07"; draw markers : N/A :: 0'05"
        # gramps 3.5 python 2.7 new marker layer
        # 38101 places : createmap : 03'09"; create_markers : 0'01"; draw markers : 0'04"
        # 65598 places : createmap : 08'48"; create_markers : 0'01"; draw markers : 0'07"
        _LOG.debug("%s" % time.strftime("start createmap : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))
        if self.generic_filter:
            place_list = self.generic_filter.apply(dbstate.db)
            for place_handle in place_list:
                place = dbstate.db.get_place_from_handle(place_handle)
                self._create_one_place(place)
        else:
            try:
                places_handle = dbstate.db.get_place_handles()
            except:
                return
            for place_hdl in places_handle:
                place = dbstate.db.get_place_from_handle(place_hdl)
                self._create_one_place(place)
        _LOG.debug(" stop createmap.")
        _LOG.debug("%s" % time.strftime("begin sort : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))
        self.sort = sorted(self.place_list,
                           key=operator.itemgetter(0)
                          )
        _LOG.debug("%s" % time.strftime("  end sort : "
                   "%a %d %b %Y %H:%M:%S", time.gmtime()))
        if self.nbmarkers > 500 : # performance issue. Is it the good value ?
            self.message_layer.add_message(
                 _("The place name in the status bar is disabled."))
            self.no_show_places_in_status_bar = True
        if self.nbplaces >= self._config.get("geography.max_places") :
            self.message_layer.set_font_attributes(None,None,"red")
            self.message_layer.add_message(
                 _("The maximum number of places is reached (%d)." %
                   self._config.get("geography.max_places")))
            self.message_layer.add_message(
                 _("Some information are missing."))
            self.message_layer.add_message(
                 _("Please, use filtering to reduce this number."))
            self.message_layer.add_message(
                 _("You can modify this value in the geography option."))
            self.message_layer.add_message(
                 _("In this case, it may take time to show all markers."))

        oldlock=config.get("geography.lock")
        config.set("geography.lock",True)
        self._create_markers()
        config.set("geography.lock",oldlock)

    def __add_place(self, menu, plat, plon):
        """
        Add a new place using longitude and latitude of location centered
        on the map
        """
        new_place = Place()
        new_place.set_latitude(str(plat))
        new_place.set_longitude(str(plon))
        try:
            EditPlace(self.dbstate, self.uistate, [], new_place)
            self.add_marker(None, None, plat, plon, None, True, 0)
        except WindowActiveError:
            pass
        
    def __link_place(self, menu, event, lat, lon):
        """
        Link an existing place using longitude and latitude of location centered
        on the map
        If we have a place history, we must show all places to avoid an empty
        place selection in the PlaceSelection.
        """
        if self.uistate.get_active('Place'):
            self._createmap(None)
        selector = SelectPlace(self.dbstate, self.uistate, [])
        place = selector.run()
        if place:
            place.set_latitude("%.8f" % lat)
            place.set_longitude("%.8f" % lon)
            EditPlace(self.dbstate, self.uistate, [], place)

    def __edit_place(self, menu, handle):
        """
        Edit the selected place at the marker position
        """
        place = self.dbstate.db.get_place_from_handle(handle)
        try:
            EditPlace(self.dbstate, self.uistate, [], place)
        except WindowActiveError:
            pass

    def build_nav_menu(self, obj, event, lat, lon):
        """
        Builds the menu for actions on the map.
        """

        self.menu = Gtk.Menu()
        menu = self.menu
        menu.set_title(_('Map Menu'))

        if config.get("geography.show_cross"):
            title = _('Remove cross hair')
        else:
            title = _('Add cross hair')
        add_item = Gtk.MenuItem(label=title)
        add_item.connect("activate", self.config_crosshair, event, lat , lon)
        add_item.show()
        menu.append(add_item)

        add_item = Gtk.MenuItem(label=_("Add place"))
        add_item.connect("activate", self.__add_place, lat , lon)
        add_item.show()
        menu.append(add_item)

        add_item = Gtk.MenuItem(label=_("Link place"))
        add_item.connect("activate", self.__link_place, event, lat , lon)
        add_item.show()
        menu.append(add_item)

        # Add specific module menu
        self.add_specific_menu(menu, event, lat, lon)
        # Add a separator line
        add_item = Gtk.MenuItem()
        add_item.show()
        menu.append(add_item)

        map_name = constants.map_title[config.get("geography.map_service")]
        title = _("Replace '%(map)s' by =>") % {
                   'map' : map_name
                  }
        add_item = Gtk.MenuItem(label=title)
        add_item.show()
        menu.append(add_item)

        self.changemap = Gtk.Menu()
        changemap = self.changemap
        changemap.set_title(title)
        changemap.show()
        add_item.set_submenu(changemap)
        # show in the map menu all available providers
        for map in constants.map_type:
            changemapitem = Gtk.MenuItem(label=constants.map_title[map])
            changemapitem.show()
            changemapitem.connect("activate", self.change_map, map)
            changemap.append(changemapitem)

        clear_text = _("Clear the '%(map)s' tiles cache.") % {
                   'map' : map_name
                  }
        self.clearmap = Gtk.MenuItem(label=clear_text)
        clearmap = self.clearmap
        clearmap.connect("activate", self.clear_map, constants.tiles_path[config.get("geography.map_service")])

        clearmap.show()
        menu.append(clearmap)

        found = False
        mark_selected = []
        self.uistate.set_busy_cursor(True)
        for mark in self.sort:
            # as we are not precise with our hand, reduce the precision
            # depending on the zoom.
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
            mlatp = precision % float(mark[3])
            mlonp = precision % float(mark[4])
            latok = lonok = False
            _LOG.debug(" compare latitude : %s with %s (precision = %s)"
                       " place='%s'" % (float(mark[3]), lat, precision,
                                        mark[0]))
            _LOG.debug("compare longitude : %s with %s (precision = %s)"
                       " zoom=%d" % (float(mark[4]), lon, precision,
                                     config.get("geography.zoom")))
            if (float(mlatp) >= (float(latp) - shift) ) and \
               (float(mlatp) <= (float(latp) + shift) ):
                latok = True
            if (float(mlonp) >= (float(lonp) - shift) ) and \
               (float(mlonp) <= (float(lonp) + shift) ):
                lonok = True
            if latok and lonok:
                mark_selected.append(mark)
                found = True

        message = ""
        prevmark = None
                            
        if found:
            for mark in mark_selected:
                if message != "":
                    place = self.dbstate.db.get_place_from_gramps_id(mark[9])
                    hdle = place.get_handle()
                    add_item = Gtk.MenuItem(label=message)
                    add_item.show()
                    menu.append(add_item)
                    self.itemoption = Gtk.Menu()
                    itemoption = self.itemoption
                    itemoption.set_title(message)
                    itemoption.show()
                    add_item.set_submenu(itemoption)
                    modify = Gtk.MenuItem(label=_("Edit Place"))
                    modify.show()
                    modify.connect("activate", self.__edit_place,
                                   hdle)
                    itemoption.append(modify)
                    center = Gtk.MenuItem(label=_("Center on this place"))
                    center.show()
                    center.connect("activate", self.goto_place_and_select, hdle,
                                   mark[3], mark[4])
                    itemoption.append(center)
                message = "%s" % mark[0]
                prevmark = mark
            add_item = Gtk.MenuItem(label=message)
            add_item.show()
            menu.append(add_item)
            self.itemoption = Gtk.Menu()
            itemoption = self.itemoption
            itemoption.set_title(message)
            itemoption.show()
            add_item.set_submenu(itemoption)
        menu.popup(None, None, None,
                   None, event.button, event.time)
        
        self.uistate.set_busy_cursor(False)
        
        menu.show()
        menu.popup(None, None, None,
                   None, event.button, event.time)
        return 1
        
    def bubble_message(self, event, lat, lon, marks):
        mark=marks[0]
        place = self.dbstate.db.get_place_from_gramps_id(mark[9])
        hdle = place.get_handle()
        self.uistate.set_active(hdle, 'Place', self.nav_group)
        return 1

    def add_specific_menu(self, menu, event, lat, lon): 
        """ 
        Add specific entry to the navigation menu.
        """ 
        add_item = Gtk.MenuItem(label=_("Centering on Place"))
        add_item.show()
        menu.append(add_item)
        self.itemoption = Gtk.Menu()
        itemoption = self.itemoption
        itemoption.set_title(_("Centering on Place"))
        itemoption.show()
        add_item.set_submenu(itemoption)
        oldplace = ""
        for mark in self.sort:
            if mark[0] != oldplace:
                oldplace = mark[0]
                modify = Gtk.MenuItem(label=mark[0])
                modify.show()
                place = self.dbstate.db.get_place_from_gramps_id(mark[9])
                hdle = place.get_handle()
                modify.connect("activate", self.goto_place_and_select, hdle, 
                               float(mark[3]), float(mark[4]))
                itemoption.append(modify)

    def goto_place_and_select(self, obj, placehandle, lat, lon):
        """
        Center the map on latitude, longitude.
        """
        self.uistate.set_active(placehandle, 'Place', self.nav_group)
        self.osm.set_center_and_zoom(lat, lon, config.get("geography.zoom"))
        
    def goto_place(self, obj, lat, lon):
        """
        Center the map on latitude, longitude.
        """
        self.osm.set_center_and_zoom(lat, lon, config.get("geography.zoom"))

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("PlaceCoordinateGramplet",),
                ())
