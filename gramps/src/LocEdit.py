#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
from RelLib import *

from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# LocationEditor class
#
#-------------------------------------------------------------------------
class LocationEditor:

    def __init__(self,parent,location):
        self.parent = parent
        self.location = location
        self.top = libglade.GladeXML(const.dialogFile, "loc_edit")
        self.window = self.top.get_widget("loc_edit")
        self.city   = self.top.get_widget("city")
        self.state  = self.top.get_widget("state")
        self.parish = self.top.get_widget("parish")
        self.county = self.top.get_widget("county")
        self.country = self.top.get_widget("country")

        # Typing CR selects OK button
        self.window.editable_enters(self.city);
        self.window.editable_enters(self.parish);
        self.window.editable_enters(self.county);
        self.window.editable_enters(self.state);
        self.window.editable_enters(self.country);

        if parent.place:
            name = _("Location Editor for %s") % parent.place.get_title()
        else:
            name = _("Location Editor")
            
        self.top.get_widget("locationTitle").set_text(name) 

        if location != None:
            self.city.set_text(location.get_city())
            self.county.set_text(location.get_county())
            self.country.set_text(location.get_country())
            self.state.set_text(location.get_state())
            self.parish.set_text(location.get_parish())

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_loc_edit_ok_clicked" : self.on_location_edit_ok_clicked
            })

    def on_location_edit_ok_clicked(self,obj):
        self.location = self.location

        city = self.city.get_text()
        county = self.county.get_text()
        country = self.country.get_text()
        state = self.state.get_text()
        parish = self.parish.get_text()
        
        if self.location == None:
            self.location = Location()
            self.parent.llist.append(self.location)
        
        self.update_location(city,parish,county,state,country)
        
        self.parent.redraw_location_list()
        Utils.destroy_passed_object(obj)

    def update_location(self,city,parish,county,state,country):
        if self.location.get_city() != city:
            self.location.set_city(city)
            self.parent.lists_changed = 1

        if self.location.get_parish() != parish:
            self.location.set_parish(parish)
            self.parent.lists_changed = 1

        if self.location.get_county() != county:
            self.location.set_county(county)
            self.parent.lists_changed = 1

        if self.location.get_state() != state:
            self.location.set_state(state)
            self.parent.lists_changed = 1

        if self.location.get_country() != country:
            self.location.set_country(country)
            self.parent.lists_changed = 1

