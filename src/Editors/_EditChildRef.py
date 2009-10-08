#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
from _EditSecondary import EditSecondary
from gen.lib import NoteType
import Errors
import config
from glade import Glade
from DisplayTabs import SourceEmbedList, NoteTab
from widgets import MonitoredDataType, PrivacyButton
from BasicUtils import name_displayer

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

_RETURN = gtk.gdk.keyval_from_name("Return")
_KP_ENTER = gtk.gdk.keyval_from_name("KP_Enter")
_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3

#-------------------------------------------------------------------------
#
# EditChildRef class
#
#-------------------------------------------------------------------------
class EditChildRef(EditSecondary):
    """
    Displays a dialog that allows the user to edit an address.
    """
    def __init__(self, name, dbstate, uistate, track, childref, callback):
        """
        Displays the dialog box.

        parent - The class that called the ChildRef editor.
        addr - The address that is to be edited
        """
        self.name = name
        EditSecondary.__init__(self, dbstate, uistate, track,
                               childref, callback)

    def _local_init(self):
        self.width_key = 'interface.child-ref-width'
        self.height_key = 'interface.child-ref-height'

        self.top = Glade()
        self.set_window(self.top.toplevel,
                        self.top.get_object("title"),
                        self.name,
                        _('Child Reference Editor'))

        self.ok_button = self.top.get_object('ok')
        self.edit_button = self.top.get_object('edit')
        self.name_label = self.top.get_object('name')
        self.name_label.set_text(self.name)

    def _setup_fields(self):
        self.frel = MonitoredDataType(
            self.top.get_object('frel'),
            self.obj.set_father_relation,
            self.obj.get_father_relation,
            self.db.readonly,
            self.db.get_child_reference_types()
            )

        self.mrel = MonitoredDataType(
            self.top.get_object('mrel'),
            self.obj.set_mother_relation,
            self.obj.get_mother_relation,
            self.db.readonly,
            self.db.get_child_reference_types()
            )
            
        self.priv = PrivacyButton(
            self.top.get_object("private"),
            self.obj,
            self.db.readonly)

    def _connect_signals(self):
        self.define_help_button(self.top.get_object('help'))
        self.define_cancel_button(self.top.get_object('cancel'))
        self.define_ok_button(self.ok_button, self.save)
        self.edit_button.connect('button-press-event', self.edit_child)
        self.edit_button.connect('key-press-event', self.edit_child)
    
    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected. 
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('person-update', self.person_change)
        self._add_db_signal('person-rebuild', self.close)
        self._add_db_signal('person-delete', self.check_for_close)

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
                    notetype=NoteType.CHILDREF))

        self._setup_notebook_tabs( notebook)
        notebook.show_all()
        self.top.get_object('vbox').pack_start(notebook,True)

    def _post_init(self): 
        self.ok_button.grab_focus()

    def build_menu_names(self, obj):
        return (_('Child Reference'),_('Child Reference Editor'))

    def edit_child(self, obj,event):
        if button_activated(event, _LEFT_BUTTON):
            from _EditPerson import EditPerson
            handle = self.obj.ref
            try:
                person = self.db.get_person_from_handle(handle)
                EditPerson(self.dbstate, self.uistate,
                           self.track, person)
            except Errors.WindowActiveError:
                pass

    def person_change(self, handles):
        # check to see if the handle matches the current object
        if self.obj.ref in handles:
            p = self.dbstate.db.get_person_from_handle(self.obj.ref)
            self.name = name_displayer.display(p)
            self.name_label.set_text(self.name)

    def save(self,*obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the ChildRef data structure.
        """
        if self.callback:
            self.callback(self.obj)
        self.close()

    def check_for_close(self, handles):
        """
        Callback method for delete signals. 
        If there is a delete signal of the primary object we are editing, the
        editor (and all child windows spawned) should be closed
        """
        if self.obj.ref in handles:
            self.close()

def button_activated(event, mouse_button):
    if (event.type == gtk.gdk.BUTTON_PRESS and \
        event.button == mouse_button) or \
       (event.type == gtk.gdk.KEY_PRESS and \
        event.keyval in (_RETURN, _KP_ENTER)):
        return True
    else:
        return False

