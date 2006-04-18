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

# $Id: _EditChildRef.py 6282 2006-04-06 22:02:46Z rshura $

"""
The EditChildRef module provides the EditChildRef class. This provides a
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
import const
from _EditSecondary import EditSecondary

from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# EditChildRef class
#
#-------------------------------------------------------------------------
class EditChildRef(EditSecondary):
    """
    Displays a dialog that allows the user to edit an address.
    """
    def __init__(self, dbstate, uistate, track, childref, callback):
        """
        Displays the dialog box.

        parent - The class that called the ChildRef editor.
        addr - The address that is to be edited
        """
        EditSecondary.__init__(self, dbstate, uistate, track,
                               childref, callback)

    def _local_init(self):
        self.top = gtk.glade.XML(const.gladeFile, "cref_edit","gramps")
        self.define_top_level(self.top.get_widget("cref_edit"),
                              self.top.get_widget("title"),
                              _('Child Reference Editor'))

    def _setup_fields(self):

        self.frel = MonitoredDataType(
            self.top.get_widget('frel'),
            self.obj.set_father_relation,
            self.obj.get_father_relation,
            )

        self.mrel = MonitoredDataType(
            self.top.get_widget('mrel'),
            self.obj.set_mother_relation,
            self.obj.get_mother_relation,
            )
            
        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.obj,
            self.db.readonly)

    def _connect_signals(self):
        self.define_help_button(self.top.get_widget('help'),'adv-ad')
        self.define_cancel_button(self.top.get_widget('cancel'))
        self.define_ok_button(self.top.get_widget('ok'),self.save)

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        """
        
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
        self.top.get_widget('vbox').pack_start(notebook,True)

    def build_menu_names(self,obj):
        return (_('ChildRef'),_('ChildRef Editor'))

    def save(self,*obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the ChildRef data structure.
        """
        if self.callback:
            self.callback(self.obj)
        self.close_window(obj)

