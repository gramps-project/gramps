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
"""
The AddrEdit module provides the AddressEditor class. This provides a
mechanism for the user to edit address information.
"""

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
import Date
import RelLib
import Sources

from DateEdit import DateEdit
from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# AddressEditor class
#
#-------------------------------------------------------------------------
class AddressEditor:
    """
    Displays a dialog that allows the user to edit an address.
    """
    def __init__(self,parent,addr):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        addr - The address that is to be edited
        """
        # Get the important widgets from the glade description
        self.top = libglade.GladeXML(const.dialogFile, "addr_edit")
        self.window = self.top.get_widget("addr_edit")
        self.addr_start = self.top.get_widget("address_start")
        self.street = self.top.get_widget("street")
        self.city = self.top.get_widget("city")
        self.state = self.top.get_widget("state")
        self.country = self.top.get_widget("country")
        self.postal = self.top.get_widget("postal")
        self.note_field = self.top.get_widget("addr_note")
        self.priv = self.top.get_widget("priv")
        self.slist = self.top.get_widget("slist")

        self.parent = parent
        self.addr = addr

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
        
        if self.addr:
            self.srcreflist = self.addr.getSourceRefList()
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
        else:
            self.srcreflist = []

        self.sourcetab = Sources.SourceTab(self.srcreflist,self.parent,self.top,self.slist)

        date_stat = self.top.get_widget("date_stat")
        self.date_check = DateEdit(self.addr_start,date_stat)

        self.top.signal_autoconnect({
            "destroy_passed_object"   : Utils.destroy_passed_object,
            "on_addr_edit_ok_clicked" : self.ok_clicked,
            })

    def ok_clicked(self,obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Address data structure.
        """
        date = self.addr_start.get_text()
        street = self.street.get_text()
        city = self.city.get_text()
        state = self.state.get_text()
        country = self.country.get_text()
        postal = self.postal.get_text()
        note = self.note_field.get_chars(0,-1)
        priv = self.priv.get_active()
        
        if self.addr == None:
            self.addr = RelLib.Address()
            self.parent.plist.append(self.addr)
        self.addr.setSourceRefList(self.srcreflist)
            
        self.update(date,street,city,state,country,postal,note,priv)
        self.parent.redraw_addr_list()
        Utils.destroy_passed_object(obj)

    def check(self,get,set,data):
        """Compares a data item, updates if necessary, and sets the
        parents lists_changed flag"""
        if get() != data:
            set(data)
            self.parent.lists_changed = 1
            
    def update(self,date,street,city,state,country,postal,note,priv):
        """Compares the data items, and updates if necessary"""
        d = Date.Date()
        d.set(date)

        if self.addr.getDate() != d.getDate():
            self.addr.setDate(date)
            self.parent.lists_changed = 1
        
        self.check(self.addr.getStreet,self.addr.setStreet,street)
        self.check(self.addr.getCountry,self.addr.setCountry,country)
        self.check(self.addr.getCity,self.addr.setCity,city)
        self.check(self.addr.getState,self.addr.setState,state)
        self.check(self.addr.getPostal,self.addr.setPostal,postal)
        self.check(self.addr.getNote,self.addr.setNote,note)
        self.check(self.addr.getPrivacy,self.addr.setPrivacy,priv)

