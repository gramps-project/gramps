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

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import re
import math
import logging
import gi
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.dialog import WarningDialog
from gramps.gen.utils.location import get_main_location
from gramps.gen.lib import PlaceType
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.display.place import displayer as _pd
from .osmgps import OsmGps

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
try:
    gi.require_version("GeocodeGlib", "1.0")
    from gi.repository import GeocodeGlib

    GEOCODEGLIB = True
except:
    GEOCODEGLIB = False

# -------------------------------------------------------------------------
#
# Functions and variables
#
# -------------------------------------------------------------------------
PLACE_REGEXP = re.compile('<span background="green">(.*)</span>')
PLACE_STRING = '<span background="green">%s</span>'
GEOCODE_REGEXP = re.compile('<span background="red">(.*)</span>')
GEOCODE_STRING = '<span background="red">%s</span>'

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
_LOG = logging.getLogger("maps.placeselection")
_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# PlaceSelection
#
# -------------------------------------------------------------------------
class PlaceSelection(ManagedWindow, OsmGps):
    """
    We show a selection box for possible places in a region of the map.
    We can select the diameter of the region which is a circle.
    Depending of this region, we can show the possible choice.
    We select the value depending of our need which open the EditPlace box.
    """

    def __init__(
        self, uistate, dbstate, maps, layer, places, lat, lon, function, oldvalue=None
    ):
        """
        Place Selection initialization
        """
        try:
            ManagedWindow.__init__(self, uistate, [], PlaceSelection)
        except WindowActiveError:
            return
        OsmGps.__init__(self, uistate)
        self.uistate = uistate
        self.dbstate = dbstate
        self.places = []
        self.lat = lat
        self.lon = lon
        self.osm = maps
        self.radius = 1.0
        self.circle = None
        self.oldvalue = oldvalue
        self.place_list = places
        self.function = function
        self.selection_layer = layer
        self.layer = layer
        self.warning = False
        dlg = Gtk.Dialog(
            title=_("Place Selection in a region"), transient_for=uistate.window
        )
        dlg.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.set_window(dlg, None, _("Place Selection in a region"), None)
        mylabel = _(
            "Choose the radius of the selection.\n"
            "On the map you should see a circle or an"
            " oval depending on the latitude."
        )
        mylabel += _(
            "\nIn the following table you may have :"
            "\n - a green row related to a selected place."
        )
        if GEOCODEGLIB:
            mylabel += _("\n - a red row related to a geocoding result.")
        label = Gtk.Label(label=mylabel)
        label.set_valign(Gtk.Align.END)
        self.window.vbox.pack_start(label, False, True, 0)
        adj = Gtk.Adjustment(
            value=1.0,
            lower=0.1,
            upper=3.0,
            step_increment=0.1,
            page_increment=0,
            page_size=0,
        )
        # default value is 1.0, minimum is 0.1 and max is 3.0
        slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
        slider.set_digits(1)
        slider.set_value_pos(Gtk.PositionType.BOTTOM)
        slider.connect("value-changed", self.slider_change, self.lat, self.lon)
        self.window.vbox.pack_start(slider, False, True, 0)
        self.vadjust = Gtk.Adjustment(page_size=15)
        self.scroll = Gtk.ScrolledWindow(vadjustment=self.vadjust)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_shadow_type(Gtk.ShadowType.IN)
        self.plist = Gtk.ListStore(str, str, str, str, str)
        self.choices = Gtk.TreeView(model=self.plist)
        self.scroll.add(self.choices)
        self.renderer = Gtk.CellRendererText()
        self.tvcol1 = Gtk.TreeViewColumn(_("Country"), self.renderer, markup=0)
        self.tvcol2 = Gtk.TreeViewColumn(_("State"), self.renderer, markup=1)
        self.tvcol3 = Gtk.TreeViewColumn(_("County"), self.renderer, markup=2)
        self.tvcol4 = Gtk.TreeViewColumn(_("Other"), self.renderer, markup=3)
        self.tvcol1.set_sort_column_id(0)
        self.tvcol2.set_sort_column_id(1)
        self.tvcol3.set_sort_column_id(2)
        self.tvcol4.set_sort_column_id(3)
        self.choices.append_column(self.tvcol1)
        self.choices.append_column(self.tvcol2)
        self.choices.append_column(self.tvcol3)
        self.choices.append_column(self.tvcol4)
        self.window.vbox.pack_start(self.scroll, True, True, 0)
        self.label2 = Gtk.Label()
        self.label2.set_markup(
            '<span background="green" foreground="black"'
            ">%s</span>"
            % _(
                "The green values in the row correspond " "to the current place values."
            )
        )
        self.label2.set_valign(Gtk.Align.END)
        self.window.vbox.pack_start(self.label2, False, True, 0)
        self.window.set_default_size(400, 300)
        self.choices.connect("row-activated", self.selection, function)
        self.window.connect("response", self.close)
        self.window.show_all()
        self.show()
        self.label2.hide()
        self.slider_change(None, lat, lon)

    def close(self, *obj):
        """
        Close the selection place editor
        """
        self.hide_the_region()
        ManagedWindow.close(self, *obj)

    def slider_change(self, obj, lat, lon):
        """
        Display on the map a circle in which we select all the places
        inside this region.
        """
        self.radius = obj.get_value() if obj else 1.0
        self.show_the_region(self.radius)
        self.match(lat, lon)
        self.plist.clear()
        if self.oldvalue != None:
            # The old values are always in the first row.
            # In this case, we change the color of the row.
            # display the associated message
            self.label2.show()
            place = self.dbstate.db.get_place_from_handle(self.oldvalue)
            loc = get_main_location(self.dbstate.db, place)
            self.plist.append(
                (
                    PLACE_STRING % loc.get(PlaceType.COUNTRY, ""),
                    PLACE_STRING % loc.get(PlaceType.STATE, ""),
                    PLACE_STRING % loc.get(PlaceType.COUNTY, ""),
                    PLACE_STRING % _("Other"),
                    self.oldvalue,
                )
            )
        for place in self.places:
            self.plist.append((place[0], place[1], place[2], place[3], place[4]))
        # here, we could add value from geography names services ...
        if GEOCODEGLIB:
            loc = GeocodeGlib.Location.new(lat, lon, 0)
            obj = GeocodeGlib.Reverse.new_for_location(loc)
            try:
                result = GeocodeGlib.Reverse.resolve(obj)
                self.plist.append(
                    (
                        GEOCODE_STRING % result.get_country(),
                        GEOCODE_STRING % result.get_state(),
                        GEOCODE_STRING % result.get_town(),
                        GEOCODE_STRING % result.get_name(),
                        "",
                    )
                )
            except:
                pass

        # if we found no place, we must create a default place.
        self.plist.append((_("New place with empty fields"), "", "...", "", None))

    def hide_the_region(self):
        """
        Hide the layer which contains the circle
        """
        layer = self.get_selection_layer()
        if layer:
            self.remove_layer(layer)

    def show_the_region(self, rds):
        """
        Show a circle in which we select the places.
        """
        # circle (rds)
        self.hide_the_region()
        self.selection_layer = self.add_selection_layer()
        self.selection_layer.add_circle(rds / 2.0, self.lat, self.lon)

    def get_location(self, gramps_id):
        """
        get location values
        """
        parent_place = None
        country = state = county = other = ""
        place = self.dbstate.db.get_place_from_gramps_id(gramps_id)
        place_name = place.name.get_value()
        parent_list = place.get_placeref_list()
        while parent_list:
            place = self.dbstate.db.get_place_from_handle(parent_list[0].ref)
            parent_list = place.get_placeref_list()
            if int(place.get_type()) == PlaceType.COUNTY:
                county = place.name.get_value()
                if parent_place is None:
                    parent_place = place.get_handle()
            elif int(place.get_type()) == PlaceType.STATE:
                state = place.name.get_value()
                if parent_place is None:
                    parent_place = place.get_handle()
            elif int(place.get_type()) == PlaceType.COUNTRY:
                country = place.name.get_value()
                if parent_place is None:
                    parent_place = place.get_handle()
            else:
                other = place.name.get_value()
                if parent_place is None:
                    parent_place = place.get_handle()
        return (country, state, county, place_name, other)

    def match(self, lat, lon):
        """
        coordinates matching.
        """
        rds = float(self.radius)
        self.places = []

        # place
        for entry in self.place_list:
            if math.hypot(lat - float(entry[3]), lon - float(entry[4])) <= rds:
                # Do we already have this place ? avoid duplicates
                (country, state, county, place, other) = self.get_location(entry[9])
                if not [country, state, county, place, other] in self.places:
                    self.places.append([country, state, county, place, other])
        self.warning = False
        for place in self.dbstate.db.iter_places():
            latn = place.get_latitude()
            lonn = place.get_longitude()
            if latn and lonn:
                latn, dummy_ignore = conv_lat_lon(latn, "0", "D.D8")
                if not latn:
                    if not self.warning:
                        self.close()
                    warn1 = _("you have a wrong latitude for:")
                    warn2 = _pd.display(self.dbstate.db, place) + "\n\n<b>"
                    warn2 += _("Please, correct this before linking") + "</b>"
                    WarningDialog(warn1, warn2, parent=self.uistate.window)
                    self.warning = True
                    continue
                dummy_ignore, lonn = conv_lat_lon("0", lonn, "D.D8")
                if not lonn:
                    if not self.warning:
                        self.close()
                    warn1 = _("you have a wrong longitude for:") + "\n"
                    warn2 = _pd.display(self.dbstate.db, place) + "\n\n<b>"
                    warn2 += _("Please, correct this before linking") + "</b>"
                    WarningDialog(warn1, warn2, parent=self.uistate.window)
                    self.warning = True
                    continue
                if math.hypot(lat - float(latn), lon - float(lonn)) <= rds:
                    (country, state, county, place, other) = self.get_location(
                        place.get_gramps_id()
                    )
                    if not [country, state, county, place, other] in self.places:
                        self.places.append([country, state, county, place, other])

    def selection(self, obj, index, column, function):
        """
        get location values and call the real function : add_place, edit_place
        """
        dummy_obj = obj
        dummy_col = column
        dummy_fct = function
        # TODO : self.plist unsubscriptable
        self.function(self.plist[index], self.lat, self.lon)

    def untag_text(self, text, tag):
        """
        suppress the green or red color tag.
        if tag = 0 : PLACE_REGEXP
        if tag = 1 : GEOCODE_REGEXP
        """

        if tag:
            regtag = GEOCODE_REGEXP
        else:
            regtag = PLACE_REGEXP

        match = regtag.match(text)
        if match:
            without_tags = match.groups()[0]
            return without_tags
        return text
