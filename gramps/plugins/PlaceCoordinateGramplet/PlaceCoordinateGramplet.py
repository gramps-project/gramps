# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015       Christian Schulze
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

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------

try:
    from gi.repository import OsmGpsMap as osmgpsmap
except:
    raise
from gi.repository import Gtk
import gi
gi.require_version('GeocodeGlib', '1.0')
from gi.repository import GeocodeGlib
from gramps.gui.display import display_url

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
#from gramps.gen.const import GRAMPS_LOCALE as glocale
#_ = glocale.get_addon_translator(__file__).gettext
from gramps.gui.plug.quick import run_quick_report_by_name, get_quick_report_list
from gramps.gen.plug  import (CATEGORY_QR_PLACE)
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.db import DbTxn
from gramps.gen.config import config

def generate_address_string(location_information, entries=['building', 'street', 'area', 'town', 'county', 'state', 'country']):
    name = []
    if 'building' in entries and 'building' in location_information and 'street' in entries and 'street' in location_information:
        entries.remove('building')
        entries.remove('street')
        name.append(location_information['street'] +
                    ' ' + location_information['building'])
    if 'county' in entries and 'county' in location_information and 'town' in entries and 'town' in location_information:
        if location_information['town'] in location_information['county']:
            entries.remove('county')

    for entry in entries:
        if entry in location_information:
            name.append(location_information[entry])
    return ", ".join(name)

#------------------------------------------------------------------------
#
# PlaceCoordinateGramplet class
#
#------------------------------------------------------------------------


class PlaceCoordinateGramplet(Gramplet):
    def active_changed(self, handle):
        self.update()

    def post_init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()
        self.connect_signal('Place', self._active_changed)
        #OsmGps.__init__(self)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        grid = Gtk.Grid()
        self.view = grid
#        self.view.add(grid)

        i = 1
        grid.attach(Gtk.Label(_("Search for:")), 1, i, 1, 1)
        self.entry_name = Gtk.Entry()
        grid.attach(self.entry_name, 2, 1, 2, 1)
        self.searchButton = Gtk.Button(label=_("Go"))
        self.searchButton.connect("clicked", self.on_searchButton_clicked)
        grid.attach(self.searchButton, 4, i, 2, 1)

        i += 1
        grid.attach(Gtk.Label(_("Found place:")), 1, i, 1, 1)
        self.entry_foundName = Gtk.Entry()
        self.entry_foundName.set_editable(False)
        self.entry_foundName.set_text(_("Nothing has been searched yet"))
        self.entry_foundName.set_width_chars(100)
        grid.attach(self.entry_foundName, 2, i, 3, 1)

        i += 1
        grid.attach(Gtk.Label(_("Latitude:")), 1, i, 1, 1)
        self.entry_lat = Gtk.Entry()
        grid.attach(self.entry_lat, 2, i, 1, 1)
        grid.attach(Gtk.Label(_("Longitude:")), 3, i, 1, 1)
        self.entry_long = Gtk.Entry()
        grid.attach(self.entry_long, 4, i, 1, 1)

        i += 1
        self.showInBrowserButton = Gtk.Button(
            label=_("Show found place externally in Google Maps"))
        self.showInBrowserButton.connect(
            "clicked", self.on_showInBrowserButton_clicked)
        grid.attach(self.showInBrowserButton, 1, i, 4, 1)

        i += 1
        self.place_id_label = Gtk.Label(_(""))
        self.place_id_label.set_halign(Gtk.Align.START)
        grid.attach(self.place_id_label, 1, i, 4, 1)

        i += 1
        grid.attach(Gtk.Label(_("Postal-Code:")), 1, i, 1, 1)
        self.entry_code = Gtk.Entry()
        self.entry_code.set_editable(False)
        grid.attach(self.entry_code, 2, i, 3, 1)

        i += 1
        grid.attach(Gtk.Label(_("Latitude:")), 1, i, 1, 1)
        self.entry_lat_db = Gtk.Entry()
        self.entry_lat_db.set_editable(False)
        grid.attach(self.entry_lat_db, 2, i, 1, 1)
        grid.attach(Gtk.Label(_("Longitude:")), 3, i, 1, 1)
        self.entry_long_db = Gtk.Entry()
        self.entry_long_db.set_editable(False)
        grid.attach(self.entry_long_db, 4, i, 1, 1)

        i += 1
        self.fromMapButton = Gtk.Button(
            label=_("Take last clicked position from Geography map"))
        self.fromMapButton.connect("clicked", self.on_fromMapButton_clicked)
        grid.attach(self.fromMapButton, 1, i, 1, 1)
        self.fromDBButton = Gtk.Button(label=_("Search location from DB"))
        self.fromDBButton.connect("clicked", self.on_fromDBButton_clicked)
        grid.attach(self.fromDBButton, 2, i, 1, 1)
        self.applyButton = Gtk.Button(
            label=_("Apply geo location to Database"))
        self.applyButton.connect("clicked", self.on_apply_clicked)
        grid.attach(self.applyButton, 3, i, 2, 1)

        grid.show_all()
        return self.view

    def on_showInBrowserButton_clicked(self, widget):
        if len(self.entry_lat.get_text()) > 0 and len(self.entry_long.get_text()) > 0:
            path = "http://maps.google.com/maps?q=%s,%s" % (
                self.entry_lat.get_text(), self.entry_long.get_text())
            display_url(path)

    def on_searchButton_clicked(self, widget):
        lat = config.get("geography.center-lat")
        lon = config.get("geography.center-lon")
#        self.osm.grab_focus()
        try:
            location_ = GeocodeGlib.Forward.new_for_string(
                self.entry_name.get_text())
            try:
                result = location_.search()
            except:
                result = None
            if result:
                result = result[0]  # use the first result
                location_information = dict((p.name, result.get_property(
                    p.name)) for p in result.list_properties() if result.get_property(p.name))
                geo_loc = location_information['location']

                self.entry_lat.set_text("%.10f" % geo_loc.get_latitude())
                self.entry_long.set_text("%.10f" % geo_loc.get_longitude())
                self.entry_foundName.set_text(
                    generate_address_string(location_information))
            else:
                self.entry_foundName.set_text(
                    _("The place was not found. You may clarify the search keywords."))
        except:
            self.entry_foundName.set_text(
                _("Failed to search for the coordinates due to some unexpected error"))

    def on_fromMapButton_clicked(self, widget):
        latitude = config.get("geography.center-lat")
        longitude = config.get("geography.center-lon")
        self.entry_lat.set_text("%.8f" % latitude)
        self.entry_long.set_text("%.8f" % longitude)
        # self.osm.grab_focus()

        try:
            loc = GeocodeGlib.Location.new(latitude, longitude, 0)
            obj = GeocodeGlib.Reverse.new_for_location(loc)
            result = GeocodeGlib.Reverse.resolve(obj)
            location_information = dict((p.name, result.get_property(
                p.name)) for p in result.list_properties() if result.get_property(p.name))
            self.entry_foundName.set_text(
                generate_address_string(location_information))
        except:
            self.entry_foundName.set_text(_("The place was not identified."))

    def on_fromDBButton_clicked(self, widget):
        latitude = config.get("geography.center-lat")
        longitude = config.get("geography.center-lon")
        latitude = self.entry_lat_db.get_text()
        longitude = self.entry_long_db.get_text()
        self.entry_lat.set_text(self.entry_lat_db.get_text())
        self.entry_long.set_text(self.entry_long_db.get_text())
        latitude = latitude.replace('N', '+')
        latitude = latitude.replace('S', '-')
        latitude = float(latitude)
        longitude = longitude.replace('E', '+')
        longitude = longitude.replace('W', '-')
        longitude = float(longitude)
        # self.osm.grab_focus()

        try:
            loc = GeocodeGlib.Location.new(latitude, longitude, 0)
            obj = GeocodeGlib.Reverse.new_for_location(loc)
            result = GeocodeGlib.Reverse.resolve(obj)
            location_information = dict((p.name, result.get_property(
                p.name)) for p in result.list_properties() if result.get_property(p.name))
            self.entry_foundName.set_text(
                generate_address_string(location_information))
        except:
            self.entry_foundName.set_text(_("The place was not identified."))

    def on_apply_clicked(self, widget):
        active_handle = self.get_active('Place')
        if active_handle:
            place = self.dbstate.db.get_place_from_handle(active_handle)
            if place:
                place.set_latitude(self.entry_lat.get_text())
                place.set_longitude(self.entry_long.get_text())
                # if (len(self.entry_code.get_text())>0):
                #     place.set_code(self.entry_code.get_text())
                with DbTxn(_("Edit Place (%s)") % place.title,
                           self.dbstate.db) as trans:
                    if not place.get_gramps_id():
                        place.set_gramps_id(
                            self.db.find_next_place_gramps_id())
                    self.dbstate.db.commit_place(place, trans)
                    #self.dbstate.emit("database-changed", ([active_handle],))

    def db_changed(self):
        self.update()

    def update_data(self, active_handle):
        if active_handle:
            place = self.dbstate.db.get_place_from_handle(active_handle)
            if place:
                self.place_id_label.set_text(
                    f"DB entry [{place.gramps_id}] {place_displayer.display(self.dbstate.db, place)}:")
                descr = place_displayer.display(self.dbstate.db, place)
                self.entry_foundName.set_text(
                    _("Nothing has been searched yet"))
                code = place.get_code()
                if len(place.lat) > 0:
                    self.entry_lat_db.set_text(place.lat)
                else:
                    self.entry_lat_db.set_text("")
                self.entry_lat.set_text("")
                if len(place.long) > 0:
                    self.entry_long_db.set_text(place.long)
                else:
                    self.entry_long_db.set_text("")
                self.entry_long.set_text("")
                if len(code) > 0:
                    self.entry_code.set_text(code)
                else:
                    self.entry_code.set_text("")
                self.entry_name.set_text(descr)  # +", "+code)
                return True
        self.entry_foundName.set_text("")
        self.entry_lat.set_text("")
        self.entry_long.set_text("")
        self.entry_code.set_text("")
        self.entry_name.set_text(_("No place is active"))
        return False

    def get_has_data(self, active_handle):
        """
        Return True if the gramplet has data, else return False.
        """
        if active_handle:
            place = self.dbstate.db.get_place_from_handle(active_handle)
            if place:
                    return True
        return False

    def update_has_data(self):
        """
        Update the has_data indicator when gramplet is not visible.
        """
        active_handle = self.get_active('Place')
        if active_handle:
            self.set_has_data(self.get_has_data(active_handle))
        else:
            self.set_has_data(False)

    def main(self):
        active_handle = self.get_active('Place')
        if active_handle:
            self.set_has_data(self.update_data(active_handle))
        else:
            self.set_has_data(False)
