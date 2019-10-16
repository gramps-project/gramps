# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011-2016  Serge Noiraud
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
Geography for events
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import operator
from gi.repository import Gdk
KEY_TAB = Gdk.KEY_Tab
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("GeoGraphy.geoevents")

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.lib import EventType
from gramps.gen.config import config
from gramps.gen.datehandler import displayer
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.place import conv_lat_lon
from gramps.gui.views.bookmarks import EventBookmarks
from gramps.plugins.lib.maps.geography import GeoGraphyView
from gramps.gui.utils import ProgressMeter

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

_UI_DEF = ['''
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">_Forward</attribute>
        </item>
      </section>
      </placeholder>
    ''',
    '''
      <section id='CommonEdit' groups='RW'>
        <item>
          <attribute name="action">win.PrintView</attribute>
          <attribute name="label" translatable="yes">Print...</attribute>
        </item>
      </section>
    ''',
    '''
      <section id="AddEditBook">
        <item>
          <attribute name="action">win.AddBook</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.EditBook</attribute>
          <attribute name="label" translatable="no">%s...</attribute>
        </item>
      </section>
    ''' % _('Organize Bookmarks'),  # Following are the Toolbar items
    '''
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">Go to the previous object in the history</property>
        <property name="label" translatable="yes">_Back</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-next</property>
        <property name="action-name">win.Forward</property>
        <property name="tooltip_text" translatable="yes">Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
    ''',
    '''
    <placeholder id='BarCommonEdit'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">document-print</property>
        <property name="action-name">win.PrintView</property>
        <property name="tooltip_text" translatable="yes">Print or save the Map</property>
        <property name="label" translatable="yes">Print...</property>
        <property name="use-underline">True</property>
       </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
    ''']

# pylint: disable=unused-argument
# pylint: disable=no-member
# pylint: disable=maybe-no-member

#-------------------------------------------------------------------------
#
# GeoView
#
#-------------------------------------------------------------------------
class GeoEvents(GeoGraphyView):
    """
    The view used to render events map.
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        self.window_name = _('Events places map')
        GeoGraphyView.__init__(self, self.window_name,
                                      pdata, dbstate, uistate,
                                      EventBookmarks,
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
        self.show_all = False
        self.cal = None

    def get_title(self):
        """
        Used to set the titlebar in the configuration window.
        """
        return _('GeoEvents')

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered
        as a stock icon.
        """
        return 'geo-show-events'

    def get_viewtype_stock(self):
        """Type of view in category
        """
        return 'geo-show-events'

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
        return 'Event'

    def goto_handle(self, handle=None):
        """
        Rebuild the tree with the given events handle as the root.
        """
        self.places_found = []
        self.build_tree()

    def show_all_events(self, menu, event, lat, lon):
        """
        Ask to show all events.
        """
        self.show_all = True
        self._createmap(None)

    def build_tree(self):
        """
        This is called by the parent class when the view becomes visible. Since
        all handling of visibility is now in rebuild_trees, see that for more
        information.
        """
        if not self.dbstate.is_open():
            return
        active = self.uistate.get_active('Event')
        if active:
            self._createmap(active)
        else:
            self._createmap(None)

    def _createmap_for_one_event(self, event):
        """
        Create all markers for each people's event in the database which has
        a lat/lon.
        """
        dbstate = self.dbstate
        if self.nbplaces >= self._config.get("geography.max_places"):
            return
        descr1 = descr2 = ""
        if event:
            place_handle = event.get_place_handle()
            eventyear = event.get_date_object().to_calendar(self.cal).get_year()
        else:
            place_handle = None
        if place_handle:
            place = dbstate.db.get_place_from_handle(place_handle)
            if place:
                descr1 = _pd.display(dbstate.db, place)
                longitude = place.get_longitude()
                latitude = place.get_latitude()
                latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
                # place.get_longitude and place.get_latitude return
                # one string. We have coordinates when the two values
                # contains non null string.
                if longitude and latitude:
                    person_list = [
                        dbstate.db.get_person_from_handle(ref_handle)
                        for (ref_type, ref_handle) in
                            dbstate.db.find_backlink_handles(event.handle)
                                if ref_type == 'Person'
                                  ]
                    if person_list:
                        for person in person_list:
                            if descr2 == "":
                                descr2 = ("%s") % _nd.display(person)
                            else:
                                descr2 = ("%s - %s") % (descr2,
                                                        _nd.display(person))
                    else:
                        # family list ?
                        family_list = [
                            dbstate.db.get_family_from_handle(ref_handle)
                            for (ref_type, ref_handle) in
                                dbstate.db.find_backlink_handles(event.handle)
                                    if ref_type == 'Family'
                                      ]
                        if family_list:
                            for family in family_list:
                                father = mother = None
                                hdle = family.get_father_handle()
                                if hdle:
                                    father = dbstate.db.get_person_from_handle(
                                                                           hdle)
                                hdle = family.get_mother_handle()
                                if hdle:
                                    mother = dbstate.db.get_person_from_handle(
                                                                           hdle)
                                descr2 = ("%(father)s - %(mother)s") % {
                   'father': _nd.display(father) if father is not None else "?",
                   'mother': _nd.display(mother) if mother is not None else "?"
                                              }
                        else:
                            descr2 = _("incomplete or unreferenced event ?")
                    self._append_to_places_list(descr1, None,
                                                None,
                                                latitude, longitude,
                                                descr2,
                                                eventyear,
                                                event.get_type(),
                                                None, # person.gramps_id
                                                place.gramps_id,
                                                event.gramps_id,
                                                None
                                                )

    def _createmap(self, obj):
        """
        Create all markers for each people's event in the database which has
        a lat/lon.
        """
        dbstate = self.dbstate
        self.place_list = []
        self.places_found = []
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        self.nbmarkers = 0
        self.nbplaces = 0
        self.without = 0
        self.cal = config.get('preferences.calendar-format-report')
        self.message_layer.clear_messages()
        self.message_layer.clear_font_attributes()
        self.no_show_places_in_status_bar = False
        if self.show_all:
            self.show_all = False
            events_handle = dbstate.db.get_event_handles()
            progress = ProgressMeter(self.window_name,
                                     can_cancel=False,
                                     parent=self.uistate.window)
            length = len(events_handle)
            progress.set_pass(_('Selecting all events'), length)
            for event_hdl in events_handle:
                event = dbstate.db.get_event_from_handle(event_hdl)
                self._createmap_for_one_event(event)
                progress.step()
            progress.close()
        elif self.generic_filter:
            user=self.uistate.viewmanager.user
            events_list = self.generic_filter.apply(dbstate.db, user=user)
            progress = ProgressMeter(self.window_name,
                                     can_cancel=False,
                                     parent=self.uistate.window)
            length = len(events_list)
            progress.set_pass(_('Selecting all events'), length)
            for event_handle in events_list:
                event = dbstate.db.get_event_from_handle(event_handle)
                self._createmap_for_one_event(event)
                progress.step()
            progress.close()
        else:
            if obj:
                event = dbstate.db.get_event_from_handle(obj)
                self._createmap_for_one_event(event)
            self.message_layer.add_message(
                 _("Right click on the map and select 'show all events'"
                   " to show all known events with coordinates. "
                   "You can use the history to navigate on the map. "
                   "You can use filtering."))
        self.sort = sorted(self.place_list,
                           key=operator.itemgetter(3, 4, 6)
                          )
        if self.nbmarkers > 500: # performance issue. Is it the good value ?
            self.no_show_places_in_status_bar = True
        self._create_markers()

    def bubble_message(self, event, lat, lon, marks):
        self.menu = Gtk.Menu()
        menu = self.menu
        message = ""
        oldplace = ""
        prevmark = None
        for mark in marks:
            if message != "":
                add_item = Gtk.MenuItem(label=message)
                add_item.show()
                menu.append(add_item)
                self.itemoption = Gtk.Menu()
                itemoption = self.itemoption
                itemoption.show()
                add_item.set_submenu(itemoption)
                modify = Gtk.MenuItem(label=_("Edit Event"))
                modify.show()
                modify.connect("activate", self.edit_event,
                               event, lat, lon, prevmark)
                itemoption.append(modify)
                center = Gtk.MenuItem(label=_("Center on this place"))
                center.show()
                center.connect("activate", self.center_here,
                               event, lat, lon, prevmark)
                itemoption.append(center)
                evt = self.dbstate.db.get_event_from_gramps_id(mark[10])
                hdle = evt.get_handle()
                bookm = Gtk.MenuItem(label=_("Bookmark this event"))
                bookm.show()
                bookm.connect("activate", self.add_bookmark_from_popup, hdle)
                itemoption.append(bookm)
            if mark[0] != oldplace:
                message = "%s :" % mark[0]
                self.add_place_bubble_message(event, lat, lon,
                                              marks, menu, message, mark)
                oldplace = mark[0]
            evt = self.dbstate.db.get_event_from_gramps_id(mark[10])
            # format the date as described in preferences.
            date = displayer.display(evt.get_date_object())
            message = "(%s) %s : %s" % (date, EventType(mark[7]), mark[5])
            prevmark = mark
        add_item = Gtk.MenuItem(label=message)
        add_item.show()
        menu.append(add_item)
        self.itemoption = Gtk.Menu()
        itemoption = self.itemoption
        itemoption.show()
        add_item.set_submenu(itemoption)
        modify = Gtk.MenuItem(label=_("Edit Event"))
        modify.show()
        modify.connect("activate", self.edit_event, event, lat, lon, prevmark)
        itemoption.append(modify)
        center = Gtk.MenuItem(label=_("Center on this place"))
        center.show()
        center.connect("activate", self.center_here, event, lat, lon, prevmark)
        itemoption.append(center)
        evt = self.dbstate.db.get_event_from_gramps_id(mark[10])
        hdle = evt.get_handle()
        bookm = Gtk.MenuItem(label=_("Bookmark this event"))
        bookm.show()
        bookm.connect("activate", self.add_bookmark_from_popup, hdle)
        itemoption.append(bookm)
        menu.popup(None, None, None,
                   None, event.button, event.time)
        return 1

    def add_specific_menu(self, menu, event, lat, lon):
        """
        Add specific entry to the navigation menu.
        """
        add_item = Gtk.MenuItem()
        add_item.show()
        menu.append(add_item)
        add_item = Gtk.MenuItem(label=_("Show all events"))
        add_item.connect("activate", self.show_all_events, event, lat, lon)
        add_item.show()
        menu.append(add_item)
        add_item = Gtk.MenuItem(label=_("Centering on Place"))
        add_item.show()
        menu.append(add_item)
        self.itemoption = Gtk.Menu()
        itemoption = self.itemoption
        itemoption.show()
        add_item.set_submenu(itemoption)
        oldplace = ""
        for mark in self.sort:
            if mark[0] != oldplace:
                oldplace = mark[0]
                modify = Gtk.MenuItem(label=mark[0])
                modify.show()
                modify.connect("activate", self.goto_place,
                               float(mark[3]), float(mark[4]))
                itemoption.append(modify)

    def goto_place(self, obj, lat, lon):
        """
        Center the map on latitude, longitude.
        """
        self.set_center(None, None, lat, lon)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Event Filter",),
                ())
