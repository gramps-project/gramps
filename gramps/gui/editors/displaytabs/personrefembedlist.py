#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2018       Alois Poettker
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

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gi.repository import GLib, GObject, Gtk

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

from gramps.gen.lib import PersonRef
from gramps.gen.errors import WindowActiveError

from .personrefmodel import PersonRefModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL

from ...ddtargets import DdTargets

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class PersonRefEmbedList(EmbeddedList):

    _HANDLE_COL = 4
    _DND_TYPE   = DdTargets.PERSONREF
    _DND_EXTRA = DdTargets.PERSON_LINK

    _MSG = {
        'add'   : _('Create and add a new association'),
        'del'   : _('Remove the existing association'),
        'edit'  : _('Edit the selected association'),
        'merge' : _('Merge two existing association'),
        'up'    : _('Move the selected association upwards'),
        'down'  : _('Move the selected association downwards'),
    }

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text
    _column_names = [
        (_('Name'), 0, 250, TEXT_COL, -1, None),
        (_('ID'), 1, 100, TEXT_COL, -1, None),
        (_('Association'), 2, 100, TEXT_COL, -1, None),
        (_('Private'),     3,  30, ICON_COL, -1, 'gramps-lock')
        ]

    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('_Associations'), PersonRefModel,
                              merge_button=True, move_buttons=True)

        # Gtk mode to allow multiple selection of list entries
        self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)

    def _selection_changed(self, obj=None):
        """
        Callback method called after user selection of a row
        Overwrites method in buttontab.py
        """
        # picks the actual selected rows
        self.selected_list = []   # Selection list (eg. multiselection)
        if self.selection.get_mode() == Gtk.SelectionMode.MULTIPLE:
            (model, pathlist) = self.selection.get_selected_rows()
            for path in pathlist:
                iter_ = model.get_iter(path)
                if iter_ is not None:
                    handle = model.get_value(iter_, self._HANDLE_COL)   # PersonRefHandle
                    if not handle in self.selected_list:
                        self.selected_list.append(handle)

        # manage the sensitivity of several buttons
        btn = True if len(self.selected_list) > 0 else False
        self.edit_btn.set_sensitive(btn)
        self.del_btn.set_sensitive(btn)

        merge_btn = True if len(self.selected_list) == 2 else False
        self.merge_btn.set_sensitive(merge_btn)

    def get_ref_editor(self):
        from .. import EditPersonRef
        return EditPersonRef

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1,3), (1, 0), (1, 1), (1, 2))

    def add_button_clicked(self, obj):
        from .. import EditPersonRef
        try:
            ref = PersonRef()
            ref.rel = _('Godfather')
            EditPersonRef(
                self.dbstate, self.uistate, self.track,
                ref, self.add_callback)
        except WindowActiveError:
            pass

    def add_callback(self, obj):
        data = self.get_data()
        data.append(obj)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        from .. import EditPersonRef
        ref = self.get_selected()
        if ref:
            try:
                EditPersonRef(
                    self.dbstate, self.uistate, self.track,
                    ref, self.edit_callback)
            except WindowActiveError:
                pass

    def edit_callback(self, obj):
        self.rebuild()

    def merge_button_clicked(self, obj):
        """
        Method called with the Merge button is clicked.
        """
        self.action = ''   # reset event action
        # double check for properly work; see _selection_changed
        if len(self.selected_list) != 2:
            return

        # process merge through addition of objects
        # combines all privacies, citations and notes in first association
        try:
            # Privacy
            self.selected_list[0].private = \
                self.selected_list[0].private or self.selected_list[1].private
            # Citations
            phoenix = self.selected_list[0].citation_list
            titanic = self.selected_list[1].citation_list
            for addendum in titanic:
                if addendum not in phoenix:
                    phoenix.append(addendum)
            # Notes
            phoenix = self.selected_list[0].note_list
            titanic = self.selected_list[1].note_list
            for addendum in titanic:
                if addendum not in phoenix:
                    phoenix.append(addendum)

            # cleaning up
            for handle in self.data:
                if handle == self.selected_list[1]:
                    self.data.remove(handle)
                    break
            self.rebuild()

        except WindowActiveError:
            pass

    def _handle_drag(self, row, obj):
        """
        An event reference that is from a drag and drop has
        an unknown event reference type
        """
        from .. import EditPersonRef
        try:
            ref = PersonRef(obj)
            ref.rel = _('Unknown')
            EditPersonRef(
                self.dbstate, self.uistate, self.track,
                ref, self.add_callback)
        except WindowActiveError:
            pass

    def handle_extra_type(self, objtype, obj):
        """
        Called when a person is dropped onto the list.  objtype will be
        'person-link' and obj will contain a person handle.
        """
        person = self.dbstate.db.get_person_from_handle(obj)

        from .. import EditPersonRef
        try:
            ref = PersonRef()
            ref.rel = _('Unknown')
            if person:
                ref.ref = person.get_handle()
            EditPersonRef(
                self.dbstate, self.uistate, self.track,
                ref, self.add_callback)
        except WindowActiveError:
            pass
