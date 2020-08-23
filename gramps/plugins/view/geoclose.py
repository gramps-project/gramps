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
Geography for two persons
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
import operator
from gi.repository import Gtk
from math import hypot
from html import escape

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("GeoGraphy.geoclose")

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import EventRoleType, EventType
from gramps.gen.config import config
from gramps.gen.datehandler import displayer, get_date
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.place import conv_lat_lon
from gramps.gui.views.bookmarks import PersonBookmarks
from gramps.plugins.lib.maps import constants
from gramps.plugins.lib.maps.geography import GeoGraphyView
from gramps.gui.selectors import SelectorFactory
from gramps.gen.utils.db import (get_birth_or_fallback, get_death_or_fallback)
from gramps.gui.uimanager import ActionGroup

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

_UI_DEF = [
    '''
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
      <section>
        <item>
          <attribute name="action">win.HomePerson</attribute>
          <attribute name="label" translatable="yes">_Home</attribute>
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
        <property name="tooltip_text" translatable="yes">'''
    '''Go to the previous object in the history</property>
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
        <property name="tooltip_text" translatable="yes">'''
    '''Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-home</property>
        <property name="action-name">win.HomePerson</property>
        <property name="tooltip_text" translatable="yes">'''
    '''Go to the home person</property>
        <property name="label" translatable="yes">_Home</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-person</property>
        <property name="action-name">win.RefPerson</property>
        <property name="tooltip_text" translatable="yes">'''
    '''Select the person which is the reference for life ways</property>
        <property name="label" translatable="yes">reference _Person</property>
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
        <property name="tooltip_text" translatable="yes">'''
    '''Print or save the Map</property>
        <property name="label" translatable="yes">Print...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
    ''']

# pylint: disable=no-member
# pylint: disable=unused-argument

#-------------------------------------------------------------------------
#
# GeoView
#
#-------------------------------------------------------------------------
class GeoClose(GeoGraphyView):
    """
    The view used to render person map.
    """
    CONFIGSETTINGS = (
        ('geography.path', constants.GEOGRAPHY_PATH),

        ('geography.zoom', 10),
        ('geography.zoom_when_center', 12),
        ('geography.show_cross', True),
        ('geography.lock', False),
        ('geography.center-lat', 0.0),
        ('geography.center-lon', 0.0),
        ('geography.use-keypad', True),
        ('geography.personal-map', ""),

        ('geography.map_service', constants.OPENSTREETMAP),
        ('geography.max_places', 5000),

        # specific to geoclose :

        ('geography.color1', 'blue'),
        ('geography.color2', 'green'),
        ('geography.maximum_meeting_zone', 5),

        )

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        GeoGraphyView.__init__(self, _("Have they been able to meet?"),
                                      pdata, dbstate, uistate,
                                      PersonBookmarks,
                                      nav_group)
        self.dbstate = dbstate
        self.uistate = uistate
        self.place_list = []
        self.all_place_list = []
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        self.refperson = None
        self.refperson_bookmark = None
        self.nbplaces = 0
        self.nbmarkers = 0
        self.sort = []
        self.tracks = []
        self.additional_uis.append(self.additional_ui())
        self.ref_person = None
        self.skip_list = []
        self.track = []
        self.place_list_active = []
        self.place_list_ref = []
        self.cal = config.get('preferences.calendar-format-report')
        self.no_show_places_in_status_bar = False
        self.add_item = None
        self.newmenu = None
        self.config_meeting_slider = None

    def get_title(self):
        """
        Used to set the titlebar in the configuration window.
        """
        return _('GeoClose')

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered
        as a stock icon.
        """
        return 'gramps-relation'

    def get_viewtype_stock(self):
        """Type of view in category
        """
        return 'geo-show-family'

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
        return 'Person'

    def goto_handle(self, handle=None):
        """
        Rebuild the tree with the given person handle as the root.
        """
        self.place_list_active = []
        self.place_list_ref = []
        self.all_place_list = []
        self.sort = []
        self.places_found = []
        self.nbmarkers = 0
        self.nbplaces = 0
        self.place_without_coordinates = []
        self.remove_all_gps()
        self.remove_all_markers()
        self.lifeway_layer.clear_ways()
        self.message_layer.clear_messages()
        self.message_layer.set_font_attributes(None, None, None)
        active = self.get_active()
        if active:
            indiv1 = self.dbstate.db.get_person_from_handle(active)
            color = self._config.get('geography.color2')
            self._createmap(indiv1, color, self.place_list_active, False)
        if self.refperson:
            color = self._config.get('geography.color1')
            self.message_layer.add_message(
                         _("Reference : %(name)s ( %(birth)s - %(death)s )") % {
                                 'name': _nd.display(self.refperson),
                                 'birth': self.birth(self.refperson),
                                 'death': self.death(self.refperson)})
            if indiv1:
                self.message_layer.add_message(
                         _("The other : %(name)s ( %(birth)s - %(death)s )") % {
                                 'name': _nd.display(indiv1),
                                 'birth': self.birth(indiv1),
                                 'death': self.death(indiv1)})
            else:
                self.message_layer.add_message(_("The other person is unknown"))
            self._createmap(self.refperson, color, self.place_list_ref, True)
            if self.refperson_bookmark is None:
                self.refperson_bookmark = self.refperson.get_handle()
                self.add_bookmark_from_popup(None, self.refperson_bookmark)
        else:
            self.message_layer.add_message(
                                     _("You must choose one reference person."))
            self.message_layer.add_message(_("Go to the person view and select "
                                             "the people you want to compare. "
                                             "Return to this view and use the"
                                             " history."))
        self.possible_meeting(self.place_list_ref, self.place_list_active)
        self.uistate.modify_statusbar(self.dbstate)

    def birth(self, person):
        """
        return "" or the birth date of the person
        """
        birth = get_birth_or_fallback(self.dbstate.db, person)
        if birth and birth.get_type() != EventType.BIRTH:
            sdate = get_date(birth)
            if sdate:
                bdate = "<i>%s</i>" % escape(sdate)
            else:
                bdate = ""
        elif birth:
            bdate = escape(get_date(birth))
        else:
            bdate = ""
        return bdate

    def death(self, person):
        """
        return "" or the death date of the person
        """
        death = get_death_or_fallback(self.dbstate.db, person)
        if death and death.get_type() != EventType.DEATH:
            sdate = get_date(death)
            if sdate:
                ddate = "<i>%s</i>" % escape(sdate)
            else:
                ddate = ""
        elif death:
            ddate = escape(get_date(death))
        else:
            ddate = ""
        return ddate

    def define_actions(self):
        """
        Define action for the reference person button.
        """
        GeoGraphyView.define_actions(self)
        self._add_action('RefPerson', self.select_person)

    def select_person(self, *obj):
        """
        Open a selection box to choose the ref person.
        """
        self.track = []
        self.skip_list = []
        self.refperson = None
        self.refperson_bookmark = None
        selectperson = SelectorFactory('Person')
        sel = selectperson(self.dbstate, self.uistate, self.track,
                           _("Select the person which will be our reference."),
                           skip=self.skip_list)
        self.refperson = sel.run()
        self.goto_handle(None)

    def build_tree(self):
        """
        This is called by the parent class when the view becomes visible. Since
        all handling of visibility is now in rebuild_trees, see that for more
        information.
        """
        self.lifeway_layer.clear_ways()
        if not self.dbstate.is_open():
            return
        active = self.get_active()
        if active:
            person = self.dbstate.db.get_person_from_handle(active)
            if person is None:
                self.goto_handle(None)
            else:
                self.goto_handle(handle=person)
        else:
            self.goto_handle(None)

    def draw(self, menu, marks, color, reference):
        """
        Create all moves for the people's event.
        """
        points = []
        mark = None
        for mark in marks:
            startlat = float(mark[3])
            startlon = float(mark[4])
            not_stored = True
            for idx in range(0, len(points)):
                if points[idx][0] == startlat and points[idx][1] == startlon:
                    not_stored = False
            if not_stored:
                points.append((startlat, startlon))
        self.lifeway_layer.add_way(points, color)
        if reference:
            self.lifeway_layer.add_way_ref(points, 'orange',
                 float(self._config.get("geography.maximum_meeting_zone")) / 10)
        return False

    def possible_meeting(self, place_list_ref, place_list_active):
        """
        Try to see if two persons can be to the same place during their life.
        If yes, show a marker with the dates foe each person.
        """
        radius = float(self._config.get("geography.maximum_meeting_zone")/10.0)
        for ref in place_list_ref:
            for act in place_list_active:
                if (hypot(float(act[3])-float(ref[3]),
                          float(act[4])-float(ref[4])) <= radius) == True:
                    # we are in the meeting zone
                    self.add_marker(None, None, act[3], act[4], act[7], True, 1)
                    self.all_place_list.append(act)
                    self.add_marker(None, None, ref[3], ref[4], ref[7], True, 1)
                    self.all_place_list.append(ref)

    def _createmap(self, person, color, place_list, reference):
        """
        Create all markers for each people's event in the database which has
        a lat/lon.
        """
        dbstate = self.dbstate
        self.cal = config.get('preferences.calendar-format-report')
        self.place_list = place_list
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        latitude = ""
        longitude = ""
        if person is not None:
            # For each event, if we have a place, set a marker.
            for event_ref in person.get_event_ref_list():
                if not event_ref:
                    continue
                event = dbstate.db.get_event_from_handle(event_ref.ref)
                role = event_ref.get_role()
                try:
                    date = event.get_date_object().to_calendar(self.cal)
                except:
                    continue
                eyear = str("%04d" % date.get_year()) + \
                          str("%02d" % date.get_month()) + \
                          str("%02d" % date.get_day())
                place_handle = event.get_place_handle()
                if place_handle:
                    place = dbstate.db.get_place_from_handle(place_handle)
                    if place:
                        longitude = place.get_longitude()
                        latitude = place.get_latitude()
                        latitude, longitude = conv_lat_lon(latitude,
                                                           longitude, "D.D8")
                        descr = _pd.display(dbstate.db, place)
                        evt = EventType(event.get_type())
                        descr1 = _("%(eventtype)s : %(name)s") % {
                                        'eventtype': evt,
                                        'name': _nd.display(person)}
                        # place.get_longitude and place.get_latitude return
                        # one string. We have coordinates when the two values
                        # contains non null string.
                        if longitude and latitude:
                            self._append_to_places_list(descr, evt,
                                                        _nd.display(person),
                                                        latitude, longitude,
                                                        descr1, eyear,
                                                        event.get_type(),
                                                        person.gramps_id,
                                                        place.gramps_id,
                                                        event.gramps_id,
                                                        role
                                                        )
                        else:
                            self._append_to_places_without_coord(
                                                        place.gramps_id, descr)
            family_list = person.get_family_handle_list()
            descr1 = " - "
            for family_hdl in family_list:
                family = self.dbstate.db.get_family_from_handle(family_hdl)
                if family is not None:
                    fhandle = family_list[0] # first is primary
                    fam = dbstate.db.get_family_from_handle(fhandle)
                    handle = fam.get_father_handle()
                    descr1 = " - "
                    if handle:
                        father = dbstate.db.get_person_from_handle(handle)
                        if father:
                            descr1 = "%s - " % _nd.display(father)
                    handle = fam.get_mother_handle()
                    if handle:
                        mother = dbstate.db.get_person_from_handle(handle)
                        if mother:
                            descr1 = "%s%s" % (descr1, _nd.display(mother))
                    for event_ref in family.get_event_ref_list():
                        if event_ref:
                            event = dbstate.db.get_event_from_handle(
                                            event_ref.ref)
                            role = event_ref.get_role()
                            if event.get_place_handle():
                                place_handle = event.get_place_handle()
                                if place_handle:
                                    place = dbstate.db.get_place_from_handle(
                                                    place_handle)
                                    if place:
                                        longitude = place.get_longitude()
                                        latitude = place.get_latitude()
                                        latitude, longitude = conv_lat_lon(
                                                  latitude, longitude, "D.D8")
                                        descr = _pd.display(dbstate.db, place)
                                        evt = EventType(event.get_type())
                                        eyear = str(
         "%04d" % event.get_date_object().to_calendar(self.cal).get_year()) + \
     str("%02d" % event.get_date_object().to_calendar(self.cal).get_month()) + \
     str("%02d" % event.get_date_object().to_calendar(self.cal).get_day())
                                        if longitude and latitude:
                                            self._append_to_places_list(descr,
                                                 evt, _nd.display(person),
                                                 latitude, longitude,
                                                 descr1, eyear,
                                                 event.get_type(),
                                                 person.gramps_id,
                                                 place.gramps_id,
                                                 event.gramps_id,
                                                 role
                                                 )
                                        else:
                                            self._append_to_places_without_coord(place.gramps_id, descr)

            sort1 = sorted(self.place_list, key=operator.itemgetter(6))
            self.draw(None, sort1, color, reference)
            # merge with the last results
            merge_list = []
            for the_list in self.sort, sort1:
                merge_list += the_list
            self.sort = sorted(merge_list, key=operator.itemgetter(6))

    def bubble_message(self, event, lat, lon, marks):
        """
        Create the menu for the selected marker
        """
        self.newmenu = Gtk.Menu()
        menu = self.newmenu
        events = []
        message = ""
        oldplace = ""
        prevmark = None
        for mark in marks:
            for plce in self.all_place_list:
                if plce[3] == mark[3] and plce[4] == mark[4]:
                    if plce[10] in events:
                        continue
                    else:
                        events.append(plce[10])

                    if plce[0] != oldplace:
                        message = "%s :" % plce[0]
                        self.add_place_bubble_message(event, lat, lon,
                                                      marks, menu,
                                                      message, plce)
                        oldplace = plce[0]
                        message = ""
                    evt = self.dbstate.db.get_event_from_gramps_id(plce[10])
                    # format the date as described in preferences.
                    date = displayer.display(evt.get_date_object())
                    if date == "":
                        date = _("Unknown")
                    if plce[11] == EventRoleType.PRIMARY:
                        message = "(%s) %s : %s" % (date, plce[2], plce[1])
                    elif plce[11] == EventRoleType.FAMILY:
                        (father_name,
                         mother_name) = self._get_father_and_mother_name(evt)
                        message = "(%s) %s : %s - %s" % (date, plce[7],
                                                         father_name,
                                                         mother_name)
                    else:
                        descr = evt.get_description()
                        if descr == "":
                            descr = _('No description')
                        message = "(%s) %s => %s" % (date, plce[11], descr)
                    prevmark = plce
                    self.add_item = Gtk.MenuItem(label=message)
                    add_item = self.add_item
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
                    menu.show()
                    menu.popup(None, None, None,
                               None, event.button, event.time)
        return 0

    def add_specific_menu(self, menu, event, lat, lon):
        """
        Add specific entry to the navigation menu.
        """
        add_item = Gtk.MenuItem()
        add_item.show()
        menu.append(add_item)
        add_item = Gtk.MenuItem(
                        label=_("Choose and bookmark the new reference person"))
        add_item.connect("activate", self.select_person)
        add_item.show()
        menu.append(add_item)
        return

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Person Filter",),
                ())

    def specific_options(self, configdialog):
        """
        Add specific entry to the preference menu.
        Must be done in the associated view.
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        configdialog.add_text(grid,
                _('The meeting zone probability radius.\n'
                  'The colored zone is approximative.\n'
                  'The meeting zone is only shown for the reference person.\n'
                  'The value 9 means about 42 miles or 67 kms.\n'
                  'The value 1 means about 4.6 miles or 7.5 kms.\n'
                  'The value is in tenth of degree.'),
                1, line_wrap=False)
        self.config_meeting_slider = configdialog.add_slider(grid,
                "",
                2, 'geography.maximum_meeting_zone',
                (1, 9))
        return _('The selection parameters'), grid

    def config_connect(self):
        """
        used to monitor changes in the ini file
        """
        self._config.connect('geography.maximum_meeting_zone',
                          self.cb_update_meeting_radius)

    def cb_update_meeting_radius(self, client, cnxn_id, entry, data):
        """
        Called when the radius change
        """
        self.goto_handle(handle=None)

