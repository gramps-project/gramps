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
from geopy.geocoders import Nominatim
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
        self.view=grid
#        self.view.add(grid)
        
        grid.attach(Gtk.Label(_("Search for:")),1,1,1,1)
        self.entry_name = Gtk.Entry()
        grid.attach(self.entry_name,2,1,3,1)
        
        grid.attach(Gtk.Label(_("Found place:")),1,2,1,1)
        self.entry_foundName = Gtk.Entry()
        self.entry_foundName.set_editable(False)
        self.entry_foundName.set_text(_("Nothing has been searched yet"))
        self.entry_foundName.set_width_chars(100)
        grid.attach(self.entry_foundName,2,2,3,1)

        grid.attach(Gtk.Label(_("Latitude:")),1,3,1,1)
        self.entry_lat = Gtk.Entry()
        grid.attach(self.entry_lat,2,3,1,1)
        grid.attach(Gtk.Label(_("Longitude:")),3,3,1,1)
        self.entry_long = Gtk.Entry()
        grid.attach(self.entry_long,4,3,1,1)
        
        grid.attach(Gtk.Label(_("Postal-Code:")),1,4,1,1)
        self.entry_code = Gtk.Entry()
        grid.attach(self.entry_code,2,4,3,1)

        self.searchButton = Gtk.Button(label=_("Search"))
        self.searchButton.connect("clicked", self.on_searchButton_clicked)
        grid.attach(self.searchButton,1,5,2,1)
        self.fromMapButton = Gtk.Button(label=_("Take last clicked position from Geography map"))
        self.fromMapButton.connect("clicked", self.on_fromMapButton_clicked)
        grid.attach(self.fromMapButton,1,6,2,1)
        self.showInBrowserButton = Gtk.Button(label=_("Show"))
        self.showInBrowserButton.connect("clicked", self.on_showInBrowserButton_clicked)
        grid.attach(self.showInBrowserButton,3,5,2,1)
        self.applyButton = Gtk.Button(label=_("Apply to Database"))
        self.applyButton.connect("clicked", self.on_apply_clicked)
        grid.attach(self.applyButton,3,6,2,1)
        
        grid.show_all()
        return self.view

    def on_showInBrowserButton_clicked(self, widget):
        path = "http://maps.google.com/maps?q=%s,%s" % (self.entry_lat.get_text(), self.entry_long.get_text())
        display_url(path)
        
    def on_searchButton_clicked(self, widget):
        lat=config.get("geography.center-lat")
        lon=config.get("geography.center-lon")
#        self.osm.grab_focus()
        geolocator = Nominatim()
        try :
            location = geolocator.geocode(self.entry_name.get_text())
            if location:
                self.entry_lat.set_text("%.8f" % location.latitude)
                self.entry_long.set_text("%.8f" % location.longitude)
                self.entry_foundName.set_text(location.address)
            else:
                self.entry_foundName.set_text(_("The place was not found. You may clarify the search keywords."))
        except:
            self.entry_foundName.set_text(_("Failed to search for the coordinates due to some unexpected error"))
            
    def on_fromMapButton_clicked(self, widget):
        latitude=config.get("geography.center-lat")
        longitude=config.get("geography.center-lon")
        self.entry_lat.set_text("%.8f" % latitude)
        self.entry_long.set_text("%.8f" % longitude)
#        self.osm.grab_focus()
        geolocator = Nominatim()
        try :
            location = geolocator.reverse(self.entry_lat.get_text()+", "+self.entry_long.get_text())
            if location:
                self.entry_foundName.set_text(location.address)
            else:
                self.entry_foundName.set_text(_("The place was not identified."))
        except:
            self.entry_foundName.set_text(_("The place was not identified."))
                
    def on_apply_clicked(self, widget):
        active_handle = self.get_active('Place')
        if active_handle:
            place = self.dbstate.db.get_place_from_handle(active_handle)
            if place:
                place.set_latitude(self.entry_lat.get_text())
                place.set_longitude(self.entry_long.get_text())
                if (len(self.entry_code.get_text())>0):
                    place.set_code(self.entry_code.get_text())
                with DbTxn(_("Extract Place data"), self.dbstate.db, batch=True) as self.trans:
                    self.dbstate.db.commit_place(place,self.trans)
                    self.dbstate.emit("place-update", ([active_handle],))

    def db_changed(self):
        self.update()

    def update_data(self, active_handle):
        if active_handle:
            place = self.dbstate.db.get_place_from_handle(active_handle)
            if place:
                descr = place_displayer.display(self.dbstate.db, place)
                self.entry_foundName.set_text(_("Nothing has been searched yet"))
                code = place.get_code()
                if len(place.lat)>0:
                    self.entry_lat.set_text(place.lat)
                else:
                    self.entry_lat.set_text("")
                if len(place.long)>0:
                    self.entry_long.set_text(place.long)
                else:
                    self.entry_long.set_text("")
                if len(code)>0:
                    self.entry_code.set_text(code)
                else:
                    self.entry_code.set_text("")
                self.entry_name.set_text(descr+", "+code)
                return True;
        self.entry_foundName.set_text("")
        self.entry_lat.set_text("")
        self.entry_long.set_text("")
        self.entry_code.set_text("")
        self.entry_name.set_text(_("No place is active"))
        return False;

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

