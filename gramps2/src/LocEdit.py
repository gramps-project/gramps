#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

# $Id$

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib

from gettext import gettext as _

#-------------------------------------------------------------------------
#
# LocationEditor class
#
#-------------------------------------------------------------------------
class LocationEditor:

    def __init__(self,parent,location,parent_window=None):
        self.parent = parent
        self.location = location
        self.top = gtk.glade.XML(const.dialogFile, "loc_edit","gramps")
        self.window = self.top.get_widget("loc_edit")
        self.city   = self.top.get_widget("city")
        self.state  = self.top.get_widget("state")
        self.parish = self.top.get_widget("parish")
        self.county = self.top.get_widget("county")
        self.country = self.top.get_widget("country")

        Utils.set_titles(self.window, self.top.get_widget('title'),
                         _('Location Editor'))

        if location != None:
            self.city.set_text(location.get_city())
            self.county.set_text(location.get_county())
            self.country.set_text(location.get_country())
            self.state.set_text(location.get_state())
            self.parish.set_text(location.get_parish())

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "on_help_loc_clicked" : self.on_help_clicked,
           })

        if parent_window:
            self.window.set_transient_for(parent_window)
        self.val = self.window.run()
        if self.val == gtk.RESPONSE_OK:
            self.on_location_edit_ok_clicked()
        self.window.destroy()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')
        self.val = self.window.run()

    def on_location_edit_ok_clicked(self):
        self.location = self.location

        city = self.city.get_text()
        county = self.county.get_text()
        country = self.country.get_text()
        state = self.state.get_text()
        parish = self.parish.get_text()
        
        if self.location == None:
            self.location = RelLib.Location()
            self.parent.llist.append(self.location)
        
        self.update_location(city,parish,county,state,country)
        
        self.parent.redraw_location_list()

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
