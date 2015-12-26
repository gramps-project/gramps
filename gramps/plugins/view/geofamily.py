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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Geography for one family
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
import sys
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
_LOG = logging.getLogger("GeoGraphy.geofamily")

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.lib import EventRoleType, EventType
from gramps.gen.config import config
from gramps.gen.datehandler import displayer
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.place import conv_lat_lon
from gramps.gui.views.pageview import PageView
from gramps.gui.editors import EditPlace
from gramps.gui.selectors.selectplace import SelectPlace
from gramps.gui.filters.sidebar import FamilySidebarFilter
from gramps.gui.views.navigationview import NavigationView
from gramps.gui.views.bookmarks import FamilyBookmarks
from gramps.plugins.lib.maps.geography import GeoGraphyView

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
class GeoFamily(GeoGraphyView):
    """
    The view used to render person map.
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        GeoGraphyView.__init__(self, _('Family places map'),
                                      pdata, dbstate, uistate, 
                                      FamilyBookmarks,
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
        self.additional_uis.append(self.additional_ui())
        self.no_show_places_in_status_bar = False

    def get_title(self):
        """
        Used to set the titlebar in the configuration window.
        """
        return _('GeoFamily')

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
        return 'Family'

    def goto_handle(self, handle=None):
        """
        Rebuild the tree with the given person handle as the root.
        """
        self.build_tree()

    def build_tree(self):
        """
        This is called by the parent class when the view becomes visible. Since
        all handling of visibility is now in rebuild_trees, see that for more
        information.
        """
        if self.uistate.get_active('Family'):
            self._createmap(self.uistate.get_active('Family'))
        else:
            self._createmap(self.uistate.get_active('Person'))

    def _createpersonmarkers(self, dbstate, person, comment, fam_id):
        """
        Create all markers for the specified person.
        """
        self.cal = config.get('preferences.calendar-format-report')
        latitude = longitude = ""
        if person:
            # For each event, if we have a place, set a marker.
            for event_ref in person.get_event_ref_list():
                if not event_ref:
                    continue
                role = event_ref.get_role()
                event = dbstate.db.get_event_from_handle(event_ref.ref)
                eyear = event.get_date_object().to_calendar(self.cal).get_year()
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
                        if ( longitude and latitude ):
                            if not self._present_in_places_list(2, str(descr1 + descr + str(evt))):
                                self._append_to_places_list(descr,
                                    str(descr1 + descr + str(evt)),
                                    _nd.display(person),
                                    latitude, longitude,
                                    role, eyear,
                                    event.get_type(),
                                    person.gramps_id,
                                    place.gramps_id,
                                    event.gramps_id,
                                    fam_id
                                    )
                        else:
                            self._append_to_places_without_coord(
                                                        place.gramps_id, descr)
            family_list = person.get_family_handle_list()
            for family_hdl in family_list:
                family = self.dbstate.db.get_family_from_handle(family_hdl)
                if family is not None:
                    for event_ref in family.get_event_ref_list():
                        if event_ref:
                            event = dbstate.db.get_event_from_handle(event_ref.ref)
                            role = event_ref.get_role()
                            if event.get_place_handle():
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
                                        (father_name, mother_name) = self._get_father_and_mother_name(event)
                                        descr1 = "%s : %s - " % ( evt, father_name )
                                        descr1 = "%s%s" % ( descr1, mother_name )
                                        eyear = event.get_date_object().to_calendar(self.cal).get_year()
                                        if ( longitude and latitude ):
                                            if not self._present_in_places_list(2, str(descr1 + descr + str(evt))):
                                                self._append_to_places_list(descr,
                                                    str(descr1 + descr + str(evt)),
                                                    _nd.display(person),
                                                    latitude, longitude,
                                                    role, eyear,
                                                    event.get_type(),
                                                    person.gramps_id,
                                                    place.gramps_id,
                                                    event.gramps_id,
                                                    family.gramps_id
                                                    )
                                        else:
                                            self._append_to_places_without_coord( place.gramps_id, descr)

    def family_label(self,family):
        if family is None:
            return "Unknown"
        f = self.dbstate.db.get_person_from_handle(
            family.get_father_handle())
        m = self.dbstate.db.get_person_from_handle(
            family.get_mother_handle())
        if f and m:
            label = _("%(gramps_id)s : %(father)s and %(mother)s") % {
                'father' : _nd.display(f),
                'mother' : _nd.display(m),
                'gramps_id' : family.gramps_id,
                }
        elif f:
            label = "%(gramps_id)s : %(father)s" % {
                'father' : _nd.display(f),
                'gramps_id' : family.gramps_id,
                }
        elif m:
            label = "%(gramps_id)s : %(mother)s" % {
                'mother' : _nd.display(m),
                'gramps_id' : family.gramps_id,
                }
        else:
            # No translation for bare gramps_id
            label = "%(gramps_id)s :" % {
                'gramps_id' : family.gramps_id,
                }
        return label
 
    def _createmap_for_one_family(self, family):
        """
        Create all markers for one family : all event's places with a lat/lon.
        """
        dbstate = self.dbstate
        self.message_layer.add_message(_("Family places for %s") % self.family_label(family))
        try:
            person = dbstate.db.get_person_from_handle(family.get_father_handle())
        except:
            return
        family_id = family.gramps_id
        if person is None: # family without father ?
            person = dbstate.db.get_person_from_handle(family.get_mother_handle())
        if person is None:
            person = dbstate.db.get_person_from_handle(self.uistate.get_active('Person'))
        if person is not None:
            family_list = person.get_family_handle_list()
            if len(family_list) > 0:
                fhandle = family_list[0] # first is primary
                fam = dbstate.db.get_family_from_handle(fhandle)
                handle = fam.get_father_handle()
                father = dbstate.db.get_person_from_handle(handle)
                if father:
                    comment = _("Father : %(id)s : %(name)s") % {'id': father.gramps_id,
                                                        'name': _nd.display(father) }
                    self._createpersonmarkers(dbstate, father,
                                              comment, family_id)
                handle = fam.get_mother_handle()
                mother = dbstate.db.get_person_from_handle(handle)
                if mother:
                    comment = _("Mother : %(id)s : %(name)s") % {'id': mother.gramps_id,
                                                        'name': _nd.display(mother) }
                    self._createpersonmarkers(dbstate, mother,
                                              comment, family_id)
                index = 0
                child_ref_list = fam.get_child_ref_list()
                if child_ref_list:
                    for child_ref in child_ref_list:
                        child = dbstate.db.get_person_from_handle(child_ref.ref)
                        if child:
                            index += 1
                            comment = _("Child : %(id)s - %(index)d "
                                        ": %(name)s") % {
                                            'id'    : child.gramps_id,
                                            'index' : index,
                                            'name'  : _nd.display(child)
                                         }
                            self._createpersonmarkers(dbstate, child,
                                                      comment, family_id)
            else:
                comment = _("Person : %(id)s %(name)s has no family.") % {
                                'id' : person.gramps_id ,
                                'name' : _nd.display(person)
                                }
                self._createpersonmarkers(dbstate, person, comment, family_id)

    def _createmap(self, family_x):
        """
        Create all markers for each people's event in the database which has 
        a lat/lon.
        """
        self.place_list = []
        self.place_without_coordinates = []
        self.places_found = []
        self.nbplaces = 0
        self.nbmarkers = 0
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        self.message_layer.clear_messages()
        family = self.dbstate.db.get_family_from_handle(family_x)
        if family is None:
            person = self.dbstate.db.get_person_from_handle(self.uistate.get_active('Person'))
            if not person:
                return
            family_list = person.get_family_handle_list()
            for family_hdl in family_list:
                family = self.dbstate.db.get_family_from_handle(family_hdl)
                if family is not None:
                    self._createmap_for_one_family(family)
        else:
            self._createmap_for_one_family(family)
        self.sort = sorted(self.place_list,
                           key=operator.itemgetter(3, 4, 6)
                          )
        self._create_markers()

    def add_event_bubble_message(self, event, lat, lon, mark, menu):
        self.itemoption = Gtk.Menu()
        itemoption = self.itemoption
        itemoption.show()
        menu.set_submenu(itemoption)
        modify = Gtk.MenuItem(label=_("Edit Family"))
        modify.show()
        modify.connect("activate", self.edit_family, event, lat, lon, mark)
        itemoption.append(modify)
        modify = Gtk.MenuItem(label=_("Edit Person"))
        modify.show()
        modify.connect("activate", self.edit_person, event, lat, lon, mark)
        itemoption.append(modify)
        modify = Gtk.MenuItem(label=_("Edit Event"))
        modify.show()
        modify.connect("activate", self.edit_event, event, lat, lon, mark)
        itemoption.append(modify)
        center = Gtk.MenuItem(label=_("Center on this place"))
        center.show()
        center.connect("activate", self.center_here, event, lat, lon, mark)
        itemoption.append(center)

    def bubble_message(self, event, lat, lon, marks):
        self.menu = Gtk.Menu()
        menu = self.menu
        menu.set_title("family")
        message = ""
        oldplace = ""
        prevmark = None
        for mark in marks:
            if message != "":
                add_item = Gtk.MenuItem(label=message)
                add_item.show()
                menu.append(add_item)
                self.add_event_bubble_message(event, lat, lon,
                                              prevmark, add_item)
            if mark[0] != oldplace:
                message = "%s :" % mark[0]
                self.add_place_bubble_message(event, lat, lon,
                                              marks, menu, message, mark)
                oldplace = mark[0]
            evt = self.dbstate.db.get_event_from_gramps_id(mark[10])
            # format the date as described in preferences.
            date = displayer.display(evt.get_date_object())
            if date == "":
                date = _("Unknown")
            if ( mark[5] == EventRoleType.PRIMARY ):
                message = "(%s) %s : %s" % ( date, mark[7], mark[1] )
            elif ( mark[5] == EventRoleType.FAMILY ):
                evt = self.dbstate.db.get_event_from_gramps_id(mark[10])
                (father_name, mother_name) = self._get_father_and_mother_name(evt)
                message = "(%s) %s : %s - %s" % ( date, mark[7], father_name, mother_name )
            else:
                evt = self.dbstate.db.get_event_from_gramps_id(mark[10])
                descr = evt.get_description()
                if descr == "":
                    descr = _('No description')
                message = "(%s) %s => %s" % ( date, mark[5], descr)
            prevmark = mark
        add_item = Gtk.MenuItem(label=message)
        add_item.show()
        menu.append(add_item)
        self.add_event_bubble_message(event, lat, lon, prevmark, add_item)
        menu.popup(None, None, None,
                   None, event.button, event.time)
        return 1

    def add_specific_menu(self, menu, event, lat, lon): 
        """ 
        Add specific entry to the navigation menu.
        """ 
        return

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Family Filter",),
                ())
