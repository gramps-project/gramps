#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

# $Id: _EditAttribute.py 6248 2006-03-31 23:46:34Z dallingham $ 

"""
The EditAttribute module provides the AttributeEditor class. This provides a
mechanism for the user to edit attribute information.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision: 6248 $"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from TransUtils import sgettext as _

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
import const
import Utils
import RelLib
import GrampsDisplay
import lds

from _EditSecondary import EditSecondary

from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# EditAttribute class
#
#-------------------------------------------------------------------------
class EditLdsOrd(EditSecondary):
    """
    Displays a dialog that allows the user to edit an attribute.
    """
    def __init__(self, state, uistate, track, attrib, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        list - list of options for the pop down menu
        """
        EditSecondary.__init__(self, state, uistate, track, attrib, callback)

    def attribute_list(self):
        return Utils.personal_attributes
        
    def _local_init(self):
        self.top = gtk.glade.XML(const.gladeFile, "lds_person_edit","gramps")
        self.define_top_level(self.top.get_widget("lds_person_edit"),
                              self.top.get_widget('title'),
                              _('LDS Ordinance Editor'))

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_widget('cancel'))
        self.define_help_button(self.top.get_widget('help'),'adv-at')
        self.define_ok_button(self.top.get_widget('ok'),self.save)

    def _setup_fields(self):
        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.obj)

        self.date_field = MonitoredDate(
            self.top.get_widget("date"),
            self.top.get_widget("date_stat"),
            self.obj.get_date_object(),
            self.window, self.db.readonly)

        self.place_field = PlaceEntry(
            self.top.get_widget("place"),
            self.obj.get_place_handle(),
            self.dbstate.get_place_completion(),
            self.db.readonly)

        temple_list = []
        for val in lds.temple_codes.keys():
            temple_list.append((lds.temple_codes[val],val))

    def _create_tabbed_pages(self):
        notebook = gtk.Notebook()
        self.srcref_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate, self.track,
                            self.obj.source_list))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_object()))
        
        notebook.show_all()
        vbox = self.top.get_widget('vbox').pack_start(notebook,True)

    def build_menu_names(self, attrib):
        label = _("LDS Ordinance")
        return (label, _('LDS Ordinance Editor'))

    def save(self,*obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Attribute data structure.
        """
        if self.callback:
            self.callback(self.obj)
        self.close_window(obj)

