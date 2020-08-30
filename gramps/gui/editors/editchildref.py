#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
The EditChildRef module provides the EditChildRef class.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import pickle

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from .editsecondary import EditSecondary
from gramps.gen.lib import NoteType
from gramps.gen.errors import WindowActiveError
from ..glade import Glade
from ..ddtargets import DdTargets
from .displaytabs import CitationEmbedList, NoteTab
from ..widgets import MonitoredDataType, PrivacyButton
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.const import URL_MANUAL_SECT1

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT1
WIKI_HELP_SEC = _('Child_Reference_Editor', 'manual')

_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3

#-------------------------------------------------------------------------
#
# EditChildRef class
#
#-------------------------------------------------------------------------
class EditChildRef(EditSecondary):
    """
    Displays a dialog that allows the user to edit a child reference.
    """

    def __init__(self, name, dbstate, uistate, track, childref, callback):
        """
        Displays the dialog box.

        childref - The child reference that is to be edited
        """
        self.name = name
        EditSecondary.__init__(self, dbstate, uistate, track,
                               childref, callback)

    def _local_init(self):

        self.top = Glade()
        self.set_window(self.top.toplevel,
                        self.top.get_object("title"),
                        self.name,
                        _('Child Reference Editor'))
        self.setup_configs('interface.child-ref', 600, 450)

        self.ok_button = self.top.get_object('ok')
        self.edit_button = self.top.get_object('edit')
        self.name_label = self.top.get_object('name')
        self.name_label.set_text(self.name)

        # Set the drag action from the label
        self.label_event_box = self.top.get_object('name_event_box')
        self.label_event_box.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                             [DdTargets.PERSON_LINK.target()],
                                             Gdk.DragAction.COPY)
        self.label_event_box.drag_source_set_icon_name('gramps-person')
        self.label_event_box.connect('drag_data_get', self.drag_data_get)

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
        self.define_cancel_button(self.top.get_object('cancel'))
        self.define_ok_button(self.ok_button, self.save)
        self.edit_button.connect('button-press-event', self.edit_child)
        self.edit_button.connect('key-press-event', self.edit_child)
        self.define_help_button(self.top.get_object('help'),
                WIKI_HELP_PAGE, WIKI_HELP_SEC)

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('person-update', self.person_change)
        self._add_db_signal('person-rebuild', self.close)
        self._add_db_signal('person-delete', self.check_for_close)

    def drag_data_get(self, widget, context, sel_data, info, time):
        # get the selected object, returning if not is defined
        if not self.obj.ref:
            return
        if info == DdTargets.PERSON_LINK.app_id:
            data = (DdTargets.PERSON_LINK.drag_type, id(self), self.obj.ref, 0)
            sel_data.set(DdTargets.PERSON_LINK.atom_drag_type, 8, pickle.dumps(data))

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.
        """
        notebook = Gtk.Notebook()

        self.srcref_list = CitationEmbedList(self.dbstate,
                                             self.uistate,
                                             self.track,
                                             self.obj.get_citation_list())
        self._add_tab(notebook, self.srcref_list)
        self.track_ref_for_deletion("srcref_list")

        self.note_tab = NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_list(),
                    notetype=NoteType.CHILDREF)
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self._setup_notebook_tabs( notebook)
        notebook.show_all()
        self.top.get_object('vbox').pack_start(notebook, True, True, 0)

    def _post_init(self):
        self.ok_button.grab_focus()

    def build_menu_names(self, obj):
        return (_('Child Reference'),_('Child Reference Editor'))

    def edit_child(self, obj,event):
        if button_activated(event, _LEFT_BUTTON):
            from .editperson import EditPerson
            handle = self.obj.ref
            try:
                person = self.db.get_person_from_handle(handle)
                EditPerson(self.dbstate, self.uistate,
                           self.track, person)
            except WindowActiveError:
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
    if (event.type == Gdk.EventType.BUTTON_PRESS and
        event.button == mouse_button) or \
       (event.type == Gdk.EventType.KEY_PRESS and
        event.keyval in (_RETURN, _KP_ENTER)):
        return True
    else:
        return False

