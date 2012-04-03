# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011  Serge Noiraud
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

# $Id: geoperson.py 18338 2011-10-16 20:21:22Z paul-franklin $

"""
Geography for two persons
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _
import operator
import gtk

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
import gen.lib
import config
import DateHandler
from gen.display.name import displayer as _nd
from PlaceUtils import conv_lat_lon
from gui.views.navigationview import NavigationView
import Bookmarks
from maps import constants
from maps.geography import GeoGraphyView
from gui.selectors import SelectorFactory

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

_UI_DEF = '''\
<ui>
<menubar name="MenuBar">
<menu action="GoMenu">
  <placeholder name="CommonGo">
    <menuitem action="Back"/>
    <menuitem action="Forward"/>
    <separator/>
    <menuitem action="HomePerson"/>
    <separator/>
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
  <toolitem action="HomePerson"/>
  <toolitem action="RefPerson"/>
</placeholder>
</toolbar>
</ui>
'''

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

        ('geography.map_service', constants.OPENSTREETMAP),

        # specific to geoclose :

        ('geography.color1', 'red'),
        ('geography.color2', 'green'),

        )

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        GeoGraphyView.__init__(self, _("Have they been able to meet?"),
                                      pdata, dbstate, uistate, 
                                      dbstate.db.get_bookmarks(), 
                                      Bookmarks.PersonBookmarks,
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
        return 'geo-show-family'
    
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

    def get_bookmarks(self):
        """
        Return the bookmark object
        """
        return self.dbstate.db.get_bookmarks()

    def goto_handle(self, handle=None):
        """
        Rebuild the tree with the given person handle as the root.
        """
        self.place_list_active = []
        self.place_list_ref = []
        self.all_place_list = []
        self.place_without_coordinates = []
        self.remove_all_gps()
        self.remove_all_markers()
        self.lifeway_layer.clear_ways()
        if self.refperson:
            color = self._config.get('geography.color1')
            self._createmap(self.refperson, color, self.place_list_ref)
        active = self.get_active()
        self.init_new_compare()
        if active:
            p1 = self.dbstate.db.get_person_from_handle(active)
            self.change_active(active)
            color = self._config.get('geography.color2')
            self._createmap(p1, color, self.place_list_active)
        self.possible_meeting(self.place_list_ref, self.place_list_active)
        self.uistate.modify_statusbar(self.dbstate)

    def define_actions(self):
        """
        Define action for the reference person button.
        """
        NavigationView.define_actions(self)

        self.ref_person = gtk.ActionGroup(self.title + '/Selection')
        self.ref_person.add_actions([
            ('RefPerson', 'gramps-person', _('_RefPerson'), None ,
            _("Select the person which is the reference for life ways"),
            self.selectPerson),
            ])
        self._add_action_group(self.ref_person)

    def selectPerson(self, obj):
        """
        Open a selection box to choose the ref person.
        """
        self.track = []
        self.skip_list = []
        SelectPerson = SelectorFactory('Person')
        sel = SelectPerson(self.dbstate, self.uistate, self.track,
                           _("Select Child"), skip=self.skip_list)
        self.refperson = sel.run()
        self.goto_handle(None)

    def build_tree(self):
        """
        This is called by the parent class when the view becomes visible. Since
        all handling of visibility is now in rebuild_trees, see that for more
        information.
        """
        active = self.get_active()
        person = self.dbstate.db.get_person_from_handle(active)
        self.lifeway_layer.clear_ways()
        self.init_new_compare()
        self.goto_handle(handle=person)

    def draw(self, menu, marks, color):
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
        if mark:
            self.lifeway_layer.add_text(points, mark[1])
        return False

    def possible_meeting(self, place_list_ref, place_list_active):
        """
        Try to see if two persons can be to the same place during their life.
        If yes, show a marker with the dates foe each person.
        """
        for ref in place_list_ref:
            for act in place_list_active:
                if (ref[3] == act[3] and ref[4] == act[4]):
                    self.add_marker(None, None, act[3], act[4], act[7], True)
                    self.all_place_list.append(act)
                    self.add_marker(None, None, ref[3], ref[4], ref[7], True)
                    self.all_place_list.append(ref)

    def _createmap(self, person, color, place_list):
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
                eyear = str("%04d" % event.get_date_object().to_calendar(self.cal).get_year()) + \
                          str("%02d" % event.get_date_object().to_calendar(self.cal).get_month()) + \
                          str("%02d" % event.get_date_object().to_calendar(self.cal).get_day())
                place_handle = event.get_place_handle()
                if place_handle:
                    place = dbstate.db.get_place_from_handle(place_handle)
                    if place:
                        longitude = place.get_longitude()
                        latitude = place.get_latitude()
                        latitude, longitude = conv_lat_lon(latitude,
                                                           longitude, "D.D8")
                        descr = place.get_title()
                        evt = gen.lib.EventType(event.get_type())
                        descr1 = _("%(eventtype)s : %(name)s") % {
                                        'eventtype': evt,
                                        'name': _nd.display(person)}
                        # place.get_longitude and place.get_latitude return
                        # one string. We have coordinates when the two values
                        # contains non null string.
                        if ( longitude and latitude ):
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
                    father = dbstate.db.get_person_from_handle(handle)
                    if father:
                        descr1 = "%s - " % _nd.display(father)
                    handle = fam.get_mother_handle()
                    mother = dbstate.db.get_person_from_handle(handle)
                    if mother:
                        descr1 = "%s%s" % ( descr1, _nd.display(mother))
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
                                        descr = place.get_title()
                                        evt = gen.lib.EventType(
                                                  event.get_type())
                                        eyear = str("%04d" % event.get_date_object().to_calendar(self.cal).get_year()) + \
                                                  str("%02d" % event.get_date_object().to_calendar(self.cal).get_month()) + \
                                                  str("%02d" % event.get_date_object().to_calendar(self.cal).get_day())
                                        if ( longitude and latitude ):
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
                                            self._append_to_places_without_coord( place.gramps_id, descr)

            self.sort = sorted(self.place_list,
                               key=operator.itemgetter(6)
                              )
            self.draw(None, self.sort, color)

    def init_new_compare(self):
        """
        Initialize.
        """
        self.place_list = []
        self.sort = []
        self.place_without_coordinates = []

    def bubble_message(self, event, lat, lon, marks):
        """
        Create the menu for the selected marker
        """
        menu = gtk.Menu()
        menu.set_title("person")
        events = []
        message = ""
        oldplace = ""
        prevmark = None
        for mark in marks:
            for plce in self.all_place_list:
                if (plce[3] == mark[3] and plce[4] == mark[4]):
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
                    date = DateHandler.displayer.display(evt.get_date_object())
                    if date == "":
                        date = _("Unknown")
                    if ( plce[11] == gen.lib.EventRoleType.PRIMARY ):
                        message = "(%s) %s : %s" % ( date, plce[2], plce[1] )
                    elif ( plce[11] == gen.lib.EventRoleType.FAMILY ):
                        (father_name, mother_name) = self._get_father_and_mother_name(evt)
                        message = "(%s) %s : %s - %s" % (date, plce[7],
                                                         father_name,
                                                         mother_name )
                    else:
                        descr = evt.get_description()
                        if descr == "":
                            descr = _('No description')
                        message = "(%s) %s => %s" % ( date, plce[11], descr)
                    prevmark = plce
                    add_item = gtk.MenuItem(message)
                    add_item.show()
                    menu.append(add_item)
                    itemoption = gtk.Menu()
                    itemoption.set_title(message)
                    itemoption.show()
                    add_item.set_submenu(itemoption)
                    modify = gtk.MenuItem(_("Edit Event"))
                    modify.show()
                    modify.connect("activate", self.edit_event,
                                   event, lat, lon, prevmark)
                    itemoption.append(modify)
                    center = gtk.MenuItem(_("Center on this place"))
                    center.show()
                    center.connect("activate", self.center_here,
                                   event, lat, lon, prevmark)
                    itemoption.append(center)
                    menu.show()
                    menu.popup(None, None, None, 0, event.time)
        return 0

    def add_specific_menu(self, menu, event, lat, lon): 
        """ 
        Add specific entry to the navigation menu.
        """ 
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
        table = gtk.Table(2, 2)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        configdialog.add_text(table,
                _('No option for this plugin'),
                1)
        return _('The animation parameters'), table
