#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"""
The AddrEdit module provides the AddressEditor class. This provides a
mechanism for the user to edit address information.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import GrampsDisplay
import const
import Utils
import RelLib
import DisplayState

from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# AddressEditor class
#
#-------------------------------------------------------------------------
class AddressEditor(DisplayState.ManagedWindow):
    """
    Displays a dialog that allows the user to edit an address.
    """
    def __init__(self, dbstate, uistate, track, addr, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        addr - The address that is to be edited
        """

        self.db = dbstate.db
        self.uistate = uistate
        self.dbstate = dbstate
        self.callback = callback
        self.addr = addr

        DisplayState.ManagedWindow.__init__(self, uistate, track, addr)

        if not self.addr:
            self.addr = RelLib.Address()

        # Get the important widgets from the glade description
        self.top = gtk.glade.XML(const.gladeFile, "addr_edit","gramps")
        self.window = self.top.get_widget("addr_edit")

        title_label = self.top.get_widget("title")
        Utils.set_titles(self.window,title_label,_('Address Editor'))

        self._setup_fields()
        self._create_tabbed_pages()
        self._connect_signals()
        self.show()

    def _setup_fields(self):
        self.addr_start = MonitoredDate(
            self.top.get_widget("address_start"), 
            self.top.get_widget("date_stat"), 
            self.addr.get_date_object(),
            self.window, self.db.readonly)
            
        self.street = MonitoredEntry(
            self.top.get_widget("street"), self.addr.set_street,
            self.addr.get_street, self.db.readonly)

        self.city = MonitoredEntry(
            self.top.get_widget("city"), self.addr.set_city,
            self.addr.get_city, self.db.readonly)

        self.state = MonitoredEntry(
            self.top.get_widget("state"), self.addr.set_state,
            self.addr.get_state, self.db.readonly)

        self.country = MonitoredEntry(
            self.top.get_widget("country"), self.addr.set_country,
            self.addr.get_country, self.db.readonly)

        self.postal = MonitoredEntry(
            self.top.get_widget("postal"), self.addr.set_postal_code,
            self.addr.get_postal_code, self.db.readonly)

        self.phone = MonitoredEntry(
            self.top.get_widget("phone"), self.addr.set_phone,
            self.addr.get_phone, self.db.readonly)
            
        self.priv = PrivacyButton(self.top.get_widget("private"),
                                  self.addr, self.db.readonly)

    def _connect_signals(self):
        self.window.connect('delete_event',self.on_delete_event)
        self.top.get_widget('cancel').connect('clicked',self.close_window)
        self.top.get_widget('help').connect('clicked',self.help_clicked)

        okbtn = self.top.get_widget('ok')
        okbtn.connect('clicked',self.ok_clicked)
        okbtn.set_sensitive(not self.db.readonly)

    def _add_page(self,page):
        self.notebook.insert_page(page)
        self.notebook.set_tab_label(page,page.get_tab_widget())
        return page
        
    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        
        """

        vbox = self.top.get_widget('vbox')
        
        self.notebook = gtk.Notebook()

        self.srcref_list = self._add_page(SourceEmbedList(
            self.dbstate,self.uistate, self.track,
            self.addr.source_list))
        self.note_tab = self._add_page(NoteTab(
            self.dbstate, self.uistate, self.track,
            self.addr.get_note_object()))

        self.notebook.show_all()
        vbox.pack_start(self.notebook,True)

    def on_delete_event(self,obj,b):
        self.close()

    def close_window(self,obj):
        self.window.destroy()
        self.close()

    def build_menu_names(self,obj):
        return (_('Address'),_('Address Editor'))

    def help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-ad')

    def ok_clicked(self,obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Address data structure.
        """
        self.callback(self.addr)
        self.close_window(obj)

