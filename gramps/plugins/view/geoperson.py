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
Geography for one person
"""
# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import operator

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
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GLib
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import EventRoleType, EventType
from gramps.gen.config import config
from gramps.gen.datehandler import displayer
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.place import conv_lat_lon
from gramps.gui.views.bookmarks import PersonBookmarks
from gramps.plugins.lib.maps import constants
from gramps.plugins.lib.maps.geography import GeoGraphyView

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
_LOG = logging.getLogger("GeoGraphy.geoperson")
KEY_TAB = Gdk.KEY_Tab
_ = glocale.translation.gettext

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
        <property name="label" translatable="yes">reference _Family</property>
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
# pylint: disable=maybe-no-member
# pylint: disable=unused-variable
# pylint: disable=unused-argument


# -------------------------------------------------------------------------
#
# GeoView
#
# -------------------------------------------------------------------------
class GeoPerson(GeoGraphyView):
    """
    The view used to render person map.
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
        # ('geography.gps_mode', GPS_DISABLED),
        # ('geography.gps_update_rate', float(1.0)),
        # ('geography.max_gps_zoom', 16),
        # ('geography.gps_increment', GPS_INCREMENT),
        ("geography.map_service", constants.OPENSTREETMAP),
        ("geography.max_places", 5000),
        # specific to geoperson :
        ("geography.steps", 20),
        ("geography.maximum_lon_lat", 30),
        ("geography.speed", 100),
    )

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        GeoGraphyView.__init__(
            self,
            _("Person places map"),
            pdata,
            dbstate,
            uistate,
            PersonBookmarks,
            nav_group,
        )
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
        self.already_started = False
        self.large_move = False
        self.cal = None

    def get_title(self):
        """
        Used to set the titlebar in the configuration window.
        """
        return _("GeoPerson")

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered
        as a stock icon.
        """
        return "geo-show-person"

    def get_viewtype_stock(self):
        """Type of view in category"""
        return "geo-show-person"

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
        return "Person"

    def goto_handle(self, handle=None):
        """
        Rebuild the tree with the given person handle as the root.
        """
        if self.osm is None:
            return
        active = self.get_active()
        self._createmap(None)
        self.uistate.modify_statusbar(self.dbstate)

    def build_tree(self):
        """
        This is called by the parent class when the view becomes visible. Since
        all handling of visibility is now in rebuild_trees, see that for more
        information.
        """
        pass

    def animate(self, menu, marks, index, stepyear):
        """
        Create all movements for the people's event.
        Yes, you can see the person moving.
        """
        if self.stop:  # no more database. stop to work
            return
        if len(marks) == 0:
            self.already_started = False
            return False
        i = int(index)
        next_i = i + 1
        if next_i == len(marks):
            self.already_started = False
            return False
        startlat = float(marks[i][3])
        startlon = float(marks[i][4])
        heading = 1
        if index == 0 and stepyear == 0:
            self.remove_all_gps()
            self.large_move = False
            self.osm.gps_add(startlat, startlon, heading)
        endlat = float(marks[next_i][3])
        endlon = float(marks[next_i][4])
        max_lon_lat = float(self._config.get("geography.maximum_lon_lat")) / 10
        if stepyear < 9000:
            if (abs(float(endlat) - float(startlat)) > max_lon_lat) or (
                abs(float(endlon) - float(startlon)) > max_lon_lat
            ):
                self.large_move = True
                stepyear = 9000
            else:
                self.large_move = False
        # year format = YYYYMMDD ( for sort )
        startyear = str(marks[i][6])[0:4]
        endyear = str(marks[next_i][6])[0:4]
        endmov = str(marks[len(marks) - 1][6])[0:4]
        years = int(endyear) - int(startyear)
        if years < 1:
            years = 1
        if stepyear > 8999:
            latstep = (endlat - startlat) / self._config.get("geography.steps")
            lonstep = (endlon - startlon) / self._config.get("geography.steps")
            startlat += latstep * (stepyear - 8999)
            startlon += lonstep * (stepyear - 8999)
        else:
            latstep = (endlat - startlat) / years
            lonstep = (endlon - startlon) / years
            stepyear = 1 if stepyear < 1 else stepyear
            startlat += latstep * stepyear
            startlon += lonstep * stepyear
        self.osm.gps_add(startlat, startlon, heading)
        stepyear += 1
        difflat = round(
            (startlat - endlat) if startlat > endlat else (endlat - startlat), 8
        )
        difflon = round(
            (startlon - endlon) if startlon > endlon else (endlon - startlon), 8
        )
        if difflat == 0.0 and difflon == 0.0:
            i += 1
            self.large_move = False
            stepyear = 1
        # if geography.speed = 100 => 100ms => 1s per 10 years.
        # For a 100 years person, it takes 10 secondes.
        # if large_move, one step is the difflat or difflon / geography.steps
        # in this case, stepyear is >= 9000
        # large move means longitude or latitude differences greater than
        # geography.maximum_lon_lat degrees.
        GLib.timeout_add(
            int(self._config.get("geography.speed")),
            self.animate,
            menu,
            marks,
            i,
            stepyear,
        )
        return False

    def _createmap(self, active):
        """
        Create all markers for each people's event in the database which has
        a lat/lon.
        @param: active is mandatory but unused in this view. Fix : 10088
        """
        if self.osm is None:
            return
        dbstate = self.dbstate
        self.cal = config.get("preferences.calendar-format-report")
        self.place_list = []
        self.place_without_coordinates = []
        self.places_found = []
        self.minlat = self.maxlat = self.minlon = self.maxlon = 0.0
        self.minyear = 9999
        self.maxyear = 0
        latitude = ""
        longitude = ""
        self.nbplaces = 0
        self.nbmarkers = 0
        self.message_layer.clear_messages()
        self.message_layer.set_font_attributes(None, None, None)
        self.kml_layer.clear()
        person_handle = self.uistate.get_active("Person")
        person = None
        if person_handle:
            person = dbstate.db.get_person_from_handle(person_handle)
        if person is not None:
            # For each event, if we have a place, set a marker.
            self.load_kml_files(person)
            self.message_layer.add_message(
                _("Person places for %s") % _nd.display(person)
            )
            for event_ref in person.get_event_ref_list():
                if not event_ref:
                    continue
                event = dbstate.db.get_event_from_handle(event_ref.ref)
                self.load_kml_files(event)
                role = event_ref.get_role()
                eyear = (
                    str(
                        "%04d"
                        % event.get_date_object().to_calendar(self.cal).get_year()
                    )
                    + str(
                        "%02d"
                        % event.get_date_object().to_calendar(self.cal).get_month()
                    )
                    + str(
                        "%02d" % event.get_date_object().to_calendar(self.cal).get_day()
                    )
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
                        self.load_kml_files(place)
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
            for family_hdl in family_list:
                family = self.dbstate.db.get_family_from_handle(family_hdl)
                if family is not None:
                    fhandle = family_list[0]  # first is primary
                    fam = dbstate.db.get_family_from_handle(fhandle)
                    father = mother = None
                    handle = fam.get_father_handle()
                    if handle:
                        father = dbstate.db.get_person_from_handle(handle)
                    descr1 = " - "
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
                            self.load_kml_files(event)
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
                                        (latitude, longitude) = conv_lat_lon(
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
                                        self.load_kml_files(place)
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

            self.sort = sorted(self.place_list, key=operator.itemgetter(6))
            self._create_markers()

    def bubble_message(self, event, lat, lon, marks):
        self.menu = Gtk.Menu()
        menu = self.menu
        message = ""
        oldplace = ""
        prevmark = None
        for mark in marks:
            if oldplace != "":
                add_item = Gtk.MenuItem(label=message)
                add_item.show()
                menu.append(add_item)
                self.itemoption = Gtk.Menu()
                itemoption = self.itemoption
                itemoption.show()
                message = ""
                add_item.set_submenu(itemoption)
                modify = Gtk.MenuItem(label=_("Edit Event"))
                modify.show()
                modify.connect("activate", self.edit_event, event, lat, lon, prevmark)
                itemoption.append(modify)
                center = Gtk.MenuItem(label=_("Center on this place"))
                center.show()
                center.connect("activate", self.center_here, event, lat, lon, prevmark)
                itemoption.append(center)
            if mark[0] != oldplace:
                if message != "":
                    add_item = Gtk.MenuItem()
                    add_item.show()
                    menu.append(add_item)
                    self.itemoption = Gtk.Menu()
                    itemoption = self.itemoption
                    itemoption.show()
                    message = ""
                    add_item.set_submenu(itemoption)
                    modify = Gtk.MenuItem(label=_("Edit Event"))
                    modify.show()
                    modify.connect("activate", self.edit_event, event, lat, lon, mark)
                    itemoption.append(modify)
                    center = Gtk.MenuItem(label=_("Center on this place"))
                    center.show()
                    center.connect("activate", self.center_here, event, lat, lon, mark)
                    itemoption.append(center)
                message = "%s :" % mark[0]
                self.add_place_bubble_message(
                    event, lat, lon, marks, menu, message, mark
                )
                oldplace = mark[0]
                message = ""
            evt = self.dbstate.db.get_event_from_gramps_id(mark[10])
            # format the date as described in preferences.
            date = displayer.display(evt.get_date_object())
            if date == "":
                date = _("Unknown")
            if mark[11] == EventRoleType.PRIMARY:
                message = "(%s) %s : %s" % (date, mark[2], mark[1])
            elif mark[11] == EventRoleType.FAMILY:
                (father_name, mother_name) = self._get_father_and_mother_name(evt)
                message = "(%s) %s : %s - %s" % (
                    date,
                    mark[7],
                    father_name,
                    mother_name,
                )
            else:
                descr = evt.get_description()
                if descr == "":
                    descr = _("No description")
                message = "(%s) %s => %s" % (date, mark[11], descr)
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
        menu.show()
        menu.popup_at_pointer(event)
        return 1

    def add_specific_menu(self, menu, event, lat, lon):
        """
        Add specific entry to the navigation menu.
        """
        menu.append(Gtk.SeparatorMenuItem())
        add_item = Gtk.MenuItem(label=_("Animate"))
        add_item.connect("activate", self.animate, self.sort, 0, 0)
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
            _("Animation speed in milliseconds (big value means slower)"),
            1,
            line_wrap=False,
        )
        configdialog.add_slider(grid, "", 2, "geography.speed", (100, 1000))
        configdialog.add_text(
            grid,
            _("How many steps between two markers when we are on large move ?"),
            3,
            line_wrap=False,
        )
        configdialog.add_slider(grid, "", 4, "geography.steps", (10, 100))
        configdialog.add_text(
            grid,
            _(
                "The minimum latitude/longitude to select large move.\n"
                "The value is in tenth of degree."
            ),
            5,
            line_wrap=False,
        )
        configdialog.add_slider(grid, "", 6, "geography.maximum_lon_lat", (5, 50))
        return _("The animation parameters"), grid
