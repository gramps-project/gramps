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
Geography for two families
"""
# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import operator
from math import hypot

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import EventRoleType, EventType
from gramps.gen.config import config
from gramps.gen.datehandler import displayer
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.place import conv_lat_lon
from gramps.gui.views.bookmarks import FamilyBookmarks
from gramps.plugins.lib.maps import constants
from gramps.plugins.lib.maps.geography import GeoGraphyView
from gramps.gui.selectors import SelectorFactory

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
_ = glocale.translation.gettext
_LOG = logging.getLogger("GeoGraphy.geofamilyclose")

_UI_DEF = [
    """
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
""",
    """
      <section id='CommonEdit' groups='RW'>
        <item>
          <attribute name="action">win.PrintView</attribute>
          <attribute name="label" translatable="yes">Print...</attribute>
        </item>
      </section>
""",
    """
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
"""
    % _("Organize Bookmarks"),  # Following are the Toolbar items
    """
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">"""
    """Go to the previous object in the history</property>
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
        <property name="tooltip_text" translatable="yes">"""
    """Go to the next object in the history</property>
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
        <property name="tooltip_text" translatable="yes">"""
    """Go to the home person</property>
        <property name="label" translatable="yes">_Home</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-family</property>
        <property name="action-name">win.RefFamily</property>
        <property name="tooltip_text" translatable="yes">"""
    """Select the family which is the reference for life ways</property>
        <property name="label" translatable="yes">reference _Family</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
""",
    """
    <placeholder id='BarCommonEdit'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">document-print</property>
        <property name="action-name">win.PrintView</property>
        <property name="tooltip_text" translatable="yes">"""
    """Print or save the Map</property>
        <property name="label" translatable="yes">Print...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
    """,
]

# pylint: disable=no-member
# pylint: disable=unused-variable
# pylint: disable=unused-argument


# -------------------------------------------------------------------------
#
# GeoView
#
# -------------------------------------------------------------------------
class GeoFamClose(GeoGraphyView):
    """
    The view used to render family's map.
    """

    CONFIGSETTINGS = (
        ("geography.path", constants.GEOGRAPHY_PATH),
        ("geography.zoom", 10),
        ("geography.zoom_when_center", 12),
        ("geography.show_cross", True),
        ("geography.lock", False),
        ("geography.center-lat", 0.0),
        ("geography.center-lon", 0.0),
        ("geography.use-keypad", True),
        ("geography.personal-map", ""),
        ("geography.map_service", constants.OPENSTREETMAP),
        ("geography.max_places", 5000),
        # specific to geoclose :
        ("geography.color1", "blue"),
        ("geography.color2", "green"),
        ("geography.maximum_meeting_zone", 5),
    )

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        GeoGraphyView.__init__(
            self,
            _("Have these two families been able to meet?"),
            pdata,
            dbstate,
            uistate,
            FamilyBookmarks,
            nav_group,
        )
        self.dbstate = dbstate
        self.uistate = uistate
        self.place_list = []
        self.all_place_list = []
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        self.reffamily = None
        self.reffamily_bookmark = None
        self.nbplaces = 0
        self.nbmarkers = 0
        self.sort = []
        self.tracks = []
        self.additional_uis.append(self.additional_ui())
        self.ref_family = None
        self.skip_list = []
        self.track = []
        self.place_list_active = []
        self.place_list_ref = []
        self.cal = config.get("preferences.calendar-format-report")
        self.no_show_places_in_status_bar = False
        self.config_meeting_slider = None
        self.dbstate.connect("database-changed", self.reset_change_db)

    def reset_change_db(self, dummy_dbase):
        """
        Used to reset the family reference
        """
        self.reffamily = None

    def get_title(self):
        """
        Used to set the titlebar in the configuration window.
        """
        return _("GeoFamClose")

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered
        as a stock icon.
        """
        return "geo-show-family"

    def get_viewtype_stock(self):
        """Type of view in category"""
        return "geo-show-family"

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
        return "Family"

    def family_label(self, family):
        """
        Create the family label depending on existence of father and mother
        """
        if family is None:
            return "Unknown"
        father = mother = None
        hdl = family.get_father_handle()
        if hdl:
            father = self.dbstate.db.get_person_from_handle(hdl)
        hdl = family.get_mother_handle()
        if hdl:
            mother = self.dbstate.db.get_person_from_handle(hdl)
        if father and mother:
            label = _("%(gramps_id)s : %(father)s and %(mother)s") % {
                "father": _nd.display(father),
                "mother": _nd.display(mother),
                "gramps_id": family.gramps_id,
            }
        elif father:
            label = "%(gramps_id)s : %(father)s" % {
                "father": _nd.display(father),
                "gramps_id": family.gramps_id,
            }
        elif mother:
            label = "%(gramps_id)s : %(mother)s" % {
                "mother": _nd.display(mother),
                "gramps_id": family.gramps_id,
            }
        else:
            # No translation for bare gramps_id
            label = "%(gramps_id)s :" % {
                "gramps_id": family.gramps_id,
            }
        return label

    def goto_handle(self, handle=None):
        """
        Rebuild the tree with the given family handle as reference.
        """
        if self.osm is None:
            return
        self.place_list_active = []
        self.place_list_ref = []
        self.all_place_list = []
        self.sort = []
        self.places_found = []
        self.place_without_coordinates = []
        self.nbmarkers = 0
        self.nbplaces = 0
        self.remove_all_gps()
        self.remove_all_markers()
        self.lifeway_layer.clear_ways()
        self.message_layer.clear_messages()
        self.message_layer.set_font_attributes(None, None, None)
        active = self.get_active()
        family = None
        if active:
            family = self.dbstate.db.get_family_from_handle(active)
            color = self._config.get("geography.color2")
            self._createmap(family, color, self.place_list_active, False)
        if self.reffamily:
            color = self._config.get("geography.color1")
            self._createmap(self.reffamily, color, self.place_list_ref, True)
            self.message_layer.add_message(
                _("Family reference : %s") % self.family_label(self.reffamily)
            )
            if family:
                self.message_layer.add_message(
                    _("The other family : %s") % self.family_label(family)
                )
            else:
                self.message_layer.add_message(
                    _("The other family : %s") % _("Unknown")
                )
            if self.reffamily_bookmark is None:
                self.reffamily_bookmark = self.reffamily.get_handle()
                self.add_bookmark_from_popup(None, self.reffamily_bookmark)
        else:
            self.message_layer.add_message(_("You must choose one reference family."))
            self.message_layer.add_message(
                _(
                    "Go to the family view and select "
                    "the families you want to compare. "
                    "Return to this view and use the history."
                )
            )
        if family is not None:
            self._possible_family_meeting(self.reffamily, family)
        self.uistate.modify_statusbar(self.dbstate)

    def define_actions(self):
        """
        Define action for the reference family button.
        """
        GeoGraphyView.define_actions(self)
        self._add_action("RefFamily", self.select_family)

    def select_family(self, *obj):
        """
        Open a selection box to choose the ref family.
        """
        self.track = []
        self.skip_list = []
        self.ref_family = None
        self.reffamily_bookmark = None
        select_family = SelectorFactory("Family")
        sel = select_family(self.dbstate, self.uistate)
        self.reffamily = sel.run()
        self.goto_handle(None)

    def build_tree(self):
        """
        This is called by the parent class when the view becomes visible. Since
        all handling of visibility is now in rebuild_trees, see that for more
        information.
        """
        if self.osm is None:
            return
        self.lifeway_layer.clear_ways()
        if not self.dbstate.is_open():
            return
        active = self.get_active()
        if active:
            family = self.dbstate.db.get_family_from_handle(active)
            if family is None:
                self.goto_handle(None)
            else:
                self.goto_handle(handle=family)
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
            self.lifeway_layer.add_way_ref(
                points,
                "orange",
                float(self._config.get("geography.maximum_meeting_zone")) / 10,
            )
        return False

    def _place_list_for_person(self, person):
        """
        get place list for one person
        """
        place_list = []
        for event in self.sort:
            if event[1] == _nd.display(person):
                place_list.append(event)
        return place_list

    def possible_meeting(self, ref_person, person):
        """
        Try to see if two persons can be to the same place during their life.
        If yes, show a marker with the dates for each person.
        """
        self.place_list_ref = self._place_list_for_person(ref_person)
        self.place_list_active = self._place_list_for_person(person)
        radius = float(self._config.get("geography.maximum_meeting_zone") / 10.0)
        for ref in self.place_list_ref:
            for act in self.place_list_active:
                if (
                    hypot(float(act[3]) - float(ref[3]), float(act[4]) - float(ref[4]))
                    <= radius
                ):
                    # we are in the meeting zone
                    self.add_marker(None, None, act[3], act[4], act[7], True, 1)
                    self.all_place_list.append(act)
                    self.add_marker(None, None, ref[3], ref[4], ref[7], True, 1)
                    self.all_place_list.append(ref)

    def _expose_persone_to_family(self, ref_person, family):
        """
        try to search one or more meeting zone for all persons of one family
        with one reference person
        """
        dbstate = self.dbstate
        try:
            person = dbstate.db.get_person_from_handle(family.get_father_handle())
        except Exception:
            return
        if person is None:  # family without father ?
            person = dbstate.db.get_person_from_handle(family.get_mother_handle())
        if person is not None:
            family_list = person.get_family_handle_list()
            if len(family_list) > 0:
                fhandle = family_list[0]  # first is primary
                fam = dbstate.db.get_family_from_handle(fhandle)
                father = mother = None
                handle = fam.get_father_handle()
                if handle:
                    father = dbstate.db.get_person_from_handle(handle)
                if father:
                    self.possible_meeting(father, ref_person)
                handle = fam.get_mother_handle()
                if handle:
                    mother = dbstate.db.get_person_from_handle(handle)
                if mother:
                    self.possible_meeting(mother, ref_person)
                child_ref_list = fam.get_child_ref_list()
                if child_ref_list:
                    for child_ref in child_ref_list:
                        child = dbstate.db.get_person_from_handle(child_ref.ref)
                        if child:
                            self.possible_meeting(child, ref_person)
            else:
                self.possible_meeting(person, ref_person)

    def _possible_family_meeting(self, reference, family):
        """
        try to expose each person of the reference family to the second family
        """
        dbstate = self.dbstate
        person = None
        try:
            person = dbstate.db.get_person_from_handle(reference.get_father_handle())
        except Exception:
            return
        if person is None:  # family without father ?
            handle = reference.get_mother_handle()
            if handle:
                person = dbstate.db.get_person_from_handle(handle)
        if person is None:
            handle = self.uistate.get_active("Person")
            if handle:
                person = dbstate.db.get_person_from_handle(handle)
        if person is not None:
            family_list = person.get_family_handle_list()
            if len(family_list) > 0:
                fhandle = family_list[0]  # first is primary
                fam = dbstate.db.get_family_from_handle(fhandle)
                father = mother = None
                handle = fam.get_father_handle()
                if handle:
                    father = dbstate.db.get_person_from_handle(handle)
                if father:
                    self._expose_persone_to_family(father, family)
                handle = fam.get_mother_handle()
                if handle:
                    mother = dbstate.db.get_person_from_handle(handle)
                if mother:
                    self._expose_persone_to_family(mother, family)
                child_ref_list = fam.get_child_ref_list()
                if child_ref_list:
                    for child_ref in child_ref_list:
                        child = dbstate.db.get_person_from_handle(child_ref.ref)
                        if child:
                            self._expose_persone_to_family(child, family)
            else:
                self._expose_persone_to_family(person, family)

    def _createmap_for_one_person(self, person, color, place_list, reference):
        """
        Create all markers for each people's event in the database which has
        a lat/lon.
        """
        self.place_list = []
        dbstate = self.dbstate
        if person is not None:
            # For each event, if we have a place, set a marker.
            for event_ref in person.get_event_ref_list():
                if not event_ref:
                    continue
                event = dbstate.db.get_event_from_handle(event_ref.ref)
                role = event_ref.get_role()
                try:
                    date = event.get_date_object().to_calendar(self.cal)
                except Exception:
                    continue
                eyear = (
                    str("%04d" % date.get_year())
                    + str("%02d" % date.get_month())
                    + str("%02d" % date.get_day())
                )
                place_handle = event.get_place_handle()
                if place_handle:
                    place = dbstate.db.get_place_from_handle(place_handle)
                    if place:
                        longitude = place.get_longitude()
                        latitude = place.get_latitude()
                        latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
                        descr = _pd.display(dbstate.db, place)
                        evt = EventType(event.get_type())
                        descr1 = _("%(eventtype)s : %(name)s") % {
                            "eventtype": evt,
                            "name": _nd.display(person),
                        }
                        # place.get_longitude and place.get_latitude return
                        # one string. We have coordinates when the two values
                        # contains non null string.
                        if longitude and latitude:
                            self._append_to_places_list(
                                descr,
                                evt,
                                _nd.display(person),
                                latitude,
                                longitude,
                                descr1,
                                eyear,
                                event.get_type(),
                                person.gramps_id,
                                place.gramps_id,
                                event.gramps_id,
                                role,
                            )
                        else:
                            self._append_to_places_without_coord(place.gramps_id, descr)
            family_list = person.get_family_handle_list()
            descr1 = " - "
            for family_hdl in family_list:
                family = self.dbstate.db.get_family_from_handle(family_hdl)
                if family is not None:
                    fhandle = family_list[0]  # first is primary
                    father = mother = None
                    fam = dbstate.db.get_family_from_handle(fhandle)
                    handle = fam.get_father_handle()
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
                            event = dbstate.db.get_event_from_handle(event_ref.ref)
                            role = event_ref.get_role()
                            if event.get_place_handle():
                                place_handle = event.get_place_handle()
                                if place_handle:
                                    place = dbstate.db.get_place_from_handle(
                                        place_handle
                                    )
                                    if place:
                                        longitude = place.get_longitude()
                                        latitude = place.get_latitude()
                                        latitude, longitude = conv_lat_lon(
                                            latitude, longitude, "D.D8"
                                        )
                                        descr = _pd.display(dbstate.db, place)
                                        evt = EventType(event.get_type())
                                        eyear = (
                                            str(
                                                "%04d"
                                                % event.get_date_object()
                                                .to_calendar(self.cal)
                                                .get_year()
                                            )
                                            + str(
                                                "%02d"
                                                % event.get_date_object()
                                                .to_calendar(self.cal)
                                                .get_month()
                                            )
                                            + str(
                                                "%02d"
                                                % event.get_date_object()
                                                .to_calendar(self.cal)
                                                .get_day()
                                            )
                                        )
                                        if longitude and latitude:
                                            self._append_to_places_list(
                                                descr,
                                                evt,
                                                _nd.display(person),
                                                latitude,
                                                longitude,
                                                descr1,
                                                eyear,
                                                event.get_type(),
                                                person.gramps_id,
                                                place.gramps_id,
                                                event.gramps_id,
                                                role,
                                            )
                                        else:
                                            self._append_to_places_without_coord(
                                                place.gramps_id, descr
                                            )

            sort1 = sorted(self.place_list, key=operator.itemgetter(6))
            self.draw(None, sort1, color, reference)
            # merge with the last results
            merge_list = []
            for the_list in self.sort, sort1:
                merge_list += the_list
            self.sort = sorted(merge_list, key=operator.itemgetter(6))

    def _createmap_for_one_family(self, family, color, place_list, reference):
        """
        Create all markers for one family : all event's places with a lat/lon.
        """
        dbstate = self.dbstate
        person = None
        try:
            person = dbstate.db.get_person_from_handle(family.get_father_handle())
        except Exception:
            return
        if person is None:  # family without father ?
            handle = family.get_mother_handle()
            if handle:
                person = dbstate.db.get_person_from_handle(handle)
        if person is None:
            handle = self.uistate.get_active("Person")
            if handle:
                person = dbstate.db.get_person_from_handle(handle)
        if person is not None:
            family_list = person.get_family_handle_list()
            if len(family_list) > 0:
                fhandle = family_list[0]  # first is primary
                fam = dbstate.db.get_family_from_handle(fhandle)
                father = mother = None
                handle = fam.get_father_handle()
                if handle:
                    father = dbstate.db.get_person_from_handle(handle)
                if father:
                    comment = _("Father : %(id)s : %(name)s") % {
                        "id": father.gramps_id,
                        "name": _nd.display(father),
                    }
                    self._createmap_for_one_person(father, color, place_list, reference)
                handle = fam.get_mother_handle()
                if handle:
                    mother = dbstate.db.get_person_from_handle(handle)
                if mother:
                    comment = _("Mother : %(id)s : %(name)s") % {
                        "id": mother.gramps_id,
                        "name": _nd.display(mother),
                    }
                    self._createmap_for_one_person(mother, color, place_list, reference)
                index = 0
                child_ref_list = fam.get_child_ref_list()
                if child_ref_list:
                    for child_ref in child_ref_list:
                        child = dbstate.db.get_person_from_handle(child_ref.ref)
                        if child:
                            index += 1
                            comment = _("Child : %(id)s - %(index)d " ": %(name)s") % {
                                "id": child.gramps_id,
                                "index": index,
                                "name": _nd.display(child),
                            }
                            self._createmap_for_one_person(
                                child, color, place_list, reference
                            )
            else:
                comment = _("Person : %(id)s %(name)s has no family.") % {
                    "id": person.gramps_id,
                    "name": _nd.display(person),
                }
                self._createmap_for_one_person(person, color, place_list, reference)

    def _createmap(self, family_x, color, place_list, reference):
        """
        Create all markers for each family's person in the database which has
        a lat/lon.
        """
        dbstate = self.dbstate
        self.cal = config.get("preferences.calendar-format-report")
        self.place_list = place_list
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        # self.minyear = 9999
        # self.maxyear = 0
        latitude = ""
        longitude = ""
        self.place_list = []
        self.place_without_coordinates = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        # family = self.dbstate.db.get_family_from_handle(family_x)
        family = family_x
        if family is None:
            handle = self.uistate.get_active("Person")
            person = None
            if handle:
                person = self.dbstate.db.get_family_from_handle(handle)
            if not person:
                return
            family_list = person.get_family_handle_list()
            for family_hdl in family_list:
                family = self.dbstate.db.get_family_from_handle(family_hdl)
                if family is not None:
                    self._createmap_for_one_family(family, color, place_list, reference)
        else:
            self._createmap_for_one_family(family, color, place_list, reference)
        # self._create_markers()

    def bubble_message(self, event, lat, lon, marks):
        """
        Create the menu for the selected marker
        """
        self.menu = Gtk.Menu()
        menu = self.menu
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
                        self.add_place_bubble_message(
                            event, lat, lon, marks, menu, message, plce
                        )
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
                        (father_name, mother_name) = self._get_father_and_mother_name(
                            evt
                        )
                        message = "(%s) %s : %s - %s" % (
                            date,
                            plce[7],
                            father_name,
                            mother_name,
                        )
                    else:
                        descr = evt.get_description()
                        if descr == "":
                            descr = _("No description")
                        message = "(%s) %s => %s" % (date, plce[11], descr)
                    prevmark = plce
                    add_item = Gtk.MenuItem(label=message)
                    add_item.show()
                    menu.append(add_item)
                    self.itemoption = Gtk.Menu()
                    itemoption = self.itemoption
                    itemoption.show()
                    add_item.set_submenu(itemoption)
                    modify = Gtk.MenuItem(label=_("Edit Event"))
                    modify.show()
                    modify.connect(
                        "activate", self.edit_event, event, lat, lon, prevmark
                    )
                    itemoption.append(modify)
                    center = Gtk.MenuItem(label=_("Center on this place"))
                    center.show()
                    center.connect(
                        "activate", self.center_here, event, lat, lon, prevmark
                    )
                    itemoption.append(center)
                    menu.show()
                    menu.popup_at_pointer(event)
        return 0

    def add_specific_menu(self, menu, event, lat, lon):
        """
        Add specific entry to the navigation menu.
        """
        menu.append(Gtk.SeparatorMenuItem())
        add_item = Gtk.MenuItem(label=_("Choose and bookmark the new reference family"))
        add_item.connect("activate", self.select_family)
        menu.append(add_item)
        return

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Person Filter",), ())

    def specific_options(self, configdialog):
        """
        Add specific entry to the preference menu.
        Must be done in the associated view.
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        configdialog.add_text(
            grid,
            _(
                "The meeting zone probability radius.\n"
                "The colored zone is approximative.\n"
                "The meeting zone is only shown for the reference family.\n"
                "The value 9 means about 42 miles or 67 kms.\n"
                "The value 1 means about 4.6 miles or 7.5 kms.\n"
                "The value is in tenth of degree."
            ),
            1,
            line_wrap=False,
        )
        self.config_meeting_slider = configdialog.add_slider(
            grid, "", 2, "geography.maximum_meeting_zone", (1, 9)
        )
        return _("The selection parameters"), grid

    def config_connect(self):
        """
        used to monitor changes in the ini file
        """
        self._config.connect(
            "geography.maximum_meeting_zone", self.cb_update_meeting_radius
        )

    def cb_update_meeting_radius(self, client, cnxn_id, entry, data):
        """
        Called when the radius change
        """
        self.goto_handle(handle=None)
