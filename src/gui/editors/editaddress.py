#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
#               2009       Gary Burton
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
The EditAddress module provides the EditAddress class. This provides a
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
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from editsecondary import EditSecondary
from gen.lib import NoteType
from glade import Glade
from displaytabs import SourceEmbedList, NoteTab
from gui.widgets import MonitoredDate, MonitoredEntry, PrivacyButton

#-------------------------------------------------------------------------
#
# EditAddress class
#
#-------------------------------------------------------------------------
class EditAddress(EditSecondary):
    """
    Displays a dialog that allows the user to edit an address.
    """


    def __init__(self, dbstate, uistate, track, addr, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        addr - The address that is to be edited
        """
        EditSecondary.__init__(self, dbstate, uistate, track, addr, callback)

    def _local_init(self):
        self.width_key = 'interface.address-width'
        self.height_key = 'interface.address-height'
        
        self.top = Glade()
        self.set_window(self.top.toplevel,
                        self.top.get_object("title"),
                        _('Address Editor'))

    def _setup_fields(self):
        self.addr_start = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_stat"), 
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)
            
        self.street = MonitoredEntry(
            self.top.get_object("street"), self.obj.set_street,
            self.obj.get_street, self.db.readonly)

        self.city = MonitoredEntry(
            self.top.get_object("city"), self.obj.set_city,
            self.obj.get_city, self.db.readonly)

        self.state = MonitoredEntry(
            self.top.get_object("state"), self.obj.set_state,
            self.obj.get_state, self.db.readonly)

        self.country = MonitoredEntry(
            self.top.get_object("country"), self.obj.set_country,
            self.obj.get_country, self.db.readonly)

        self.postal = MonitoredEntry(
            self.top.get_object("postal"), self.obj.set_postal_code,
            self.obj.get_postal_code, self.db.readonly)

        self.phone = MonitoredEntry(
            self.top.get_object("phone"), self.obj.set_phone,
            self.obj.get_phone, self.db.readonly)
            
        self.priv = PrivacyButton(self.top.get_object("private"),
                                  self.obj, self.db.readonly)

    def _connect_signals(self):
        self.define_help_button(self.top.get_object('help'))
        self.define_cancel_button(self.top.get_object('cancel'))
        self.define_ok_button(self.top.get_object('ok'),self.save)

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.
        """
        
        notebook = gtk.Notebook()
        
        self.srcref_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate,self.track,self.obj))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_list(),
                    notetype=NoteType.ADDRESS))

        self._setup_notebook_tabs( notebook)
        notebook.show_all()
        self.top.get_object('vbox').pack_start(notebook,True)

    def build_menu_names(self, obj):
        return (_('Address'),_('Address Editor'))

    def save(self,*obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Address data structure.
        """
        if self.callback:
            self.callback(self.obj)
        self.close()
