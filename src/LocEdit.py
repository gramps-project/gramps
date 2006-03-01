#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsDisplay
import DisplayState

from WindowUtils import GladeIf
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# LocationEditor class
#
#-------------------------------------------------------------------------
class LocationEditor(DisplayState.ManagedWindow):

    def __init__(self,dbstate,uistate,track,location,callback):
        DisplayState.ManagedWindow.__init__(self, uistate, track, location)

        self.location = location
        self.top = gtk.glade.XML(const.gladeFile, "loc_edit","gramps")
        self.gladeif = GladeIf(self.top)
        
        self.window = self.top.get_widget("loc_edit")
        self.city   = self.top.get_widget("city")
        self.state  = self.top.get_widget("state")
        self.postal = self.top.get_widget("postal")
        self.phone = self.top.get_widget("phone")
        self.parish = self.top.get_widget("parish")
        self.county = self.top.get_widget("county")
        self.country = self.top.get_widget("country")
        self.callback = callback

        Utils.set_titles(self.window, self.top.get_widget('title'),
                         _('Location Editor'))

        if location != None:
            self.city.set_text(location.get_city())
            self.county.set_text(location.get_county())
            self.country.set_text(location.get_country())
            self.state.set_text(location.get_state())
            self.phone.set_text(location.get_phone())
            self.postal.set_text(location.get_postal_code())
            self.parish.set_text(location.get_parish())

        self.gladeif.connect('loc_edit','delete_event',self.on_delete_event)
        self.gladeif.connect('button119','clicked',self.close_window)
        self.gladeif.connect('button118','clicked',self.on_ok_clicked)
        self.gladeif.connect('button128','clicked',self.on_help_clicked)
        
        self.show()

    def on_delete_event(self,obj,b):
        self.gladeif.close()
        self.close()

    def close_window(self,obj):
        self.gladeif.close()
        self.close()
        
    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-edit-complete')

    def on_ok_clicked(self,obj):
        city = unicode(self.city.get_text())
        county = unicode(self.county.get_text())
        country = unicode(self.country.get_text())
        state = unicode(self.state.get_text())
        phone = unicode(self.phone.get_text())
        postal = unicode(self.postal.get_text())
        parish = unicode(self.parish.get_text())
        
        self.update_location(city,parish,county,state,phone,postal,country)
        self.callback(self.location)
        self.close(obj)

    def update_location(self,city,parish,county,state,phone,postal,country):
        if self.location.get_city() != city:
            self.location.set_city(city)

        if self.location.get_parish() != parish:
            self.location.set_parish(parish)

        if self.location.get_county() != county:
            self.location.set_county(county)

        if self.location.get_state() != state:
            self.location.set_state(state)

        if self.location.get_phone() != phone:
            self.location.set_phone(phone)

        if self.location.get_postal_code() != postal:
            self.location.set_postal_code(postal)

        if self.location.get_country() != country:
            self.location.set_country(country)
