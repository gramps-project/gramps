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
import utils
from RelLib import *

from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# AddressEditor class
#
#-------------------------------------------------------------------------
class AddressEditor:

    def __init__(self,parent,addr):
        self.parent = parent
        self.addr = addr
        self.top = libglade.GladeXML(const.editPersonFile, "addr_edit")
        self.window = self.top.get_widget("addr_edit")
        self.addr_start  = self.top.get_widget("address_start")
        self.street = self.top.get_widget("street")
        self.city = self.top.get_widget("city")
        self.state = self.top.get_widget("state")
        self.country = self.top.get_widget("country")
        self.postal = self.top.get_widget("postal")
        self.note_field = self.top.get_widget("addr_note")
        self.priv = self.top.get_widget("priv")

        if self.addr:
            self.srcreflist = self.addr.getSourceRefList()
        else:
            self.srcreflist = []

        name = parent.person.getPrimaryName().getName()
        text = _("Address Editor for %s") % name
        self.top.get_widget("addrTitle").set_text(text)

        # Typing CR selects OK button
        self.window.editable_enters(self.addr_start);
        self.window.editable_enters(self.street);
        self.window.editable_enters(self.city);
        self.window.editable_enters(self.state);
        self.window.editable_enters(self.country);
        self.window.editable_enters(self.postal);
        self.window.editable_enters(self.note_field);
        
        if self.addr != None:
            self.addr_start.set_text(self.addr.getDate())
            self.street.set_text(self.addr.getStreet())
            self.city.set_text(self.addr.getCity())
            self.state.set_text(self.addr.getState())
            self.country.set_text(self.addr.getCountry())
            self.postal.set_text(self.addr.getPostal())
                 
            self.priv.set_active(self.addr.getPrivacy())
            self.note_field.set_point(0)
            self.note_field.insert_defaults(self.addr.getNote())
            self.note_field.set_word_wrap(1)

        self.top.signal_autoconnect({
            "destroy_passed_object"   : utils.destroy_passed_object,
            "on_addr_edit_ok_clicked" : self.on_addr_edit_ok_clicked,
            "on_source_clicked"       : self.on_addr_source_clicked
            })

    def on_addr_source_clicked(self,obj):
        import Sources
        Sources.SourceSelector(self.srcreflist,self.parent,src_changed)

    def on_addr_edit_ok_clicked(self,obj):
        date = self.addr_start.get_text()
        street = self.street.get_text()
        city = self.city.get_text()
        state = self.state.get_text()
        country = self.country.get_text()
        postal = self.postal.get_text()
        note = self.note_field.get_chars(0,-1)
        priv = self.priv.get_active()
        
        if self.addr == None:
            self.addr = Address()
            self.addr.setSourceRefList(self.srcreflist)
            self.parent.plist.append(self.addr)
            
        self.update_address(date,street,city,state,country,postal,note,priv)
        self.parent.redraw_addr_list()
        utils.destroy_passed_object(obj)

    def update_address(self,date,street,city,state,country,postal,note,priv):
        d = Date()
        d.set(date)

        if self.addr.getDate() != d.getDate():
            self.addr.setDate(date)
            self.parent.lists_changed = 1
        
        if self.addr.getState() != state:
            self.addr.setState(state)
            self.parent.lists_changed = 1

        if self.addr.getStreet() != street:
            self.addr.setStreet(street)
            self.parent.lists_changed = 1

        if self.addr.getCountry() != country:
            self.addr.setCountry(country)
            self.parent.lists_changed = 1

        if self.addr.getCity() != city:
            self.addr.setCity(city)
            self.parent.lists_changed = 1

        if self.addr.getPostal() != postal:
            self.addr.setPostal(postal)
            self.parent.lists_changed = 1

        if self.addr.getNote() != note:
            self.addr.setNote(note)
            self.parent.lists_changed = 1

        if self.addr.getPrivacy() != priv:
            self.addr.setPrivacy(priv)
            self.parent.lists_changed = 1

def src_changed(parent):
    parent.lists_changed = 1
