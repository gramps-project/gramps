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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gi.repository import GObject
from gi.repository import GLib

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.lib import PersonRef
from gramps.gen.errors import WindowActiveError
from ...ddtargets import DdTargets
from .personrefmodel import PersonRefModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL
from ...dbguielement import DbGUIElement


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class PersonRefEmbedList(DbGUIElement, EmbeddedList):

    _HANDLE_COL = 4
    _DND_TYPE = DdTargets.PERSONREF
    _DND_EXTRA = DdTargets.PERSON_LINK

    _MSG = {
        'add'   : _('Create and add a new association'),
        'del'   : _('Remove the existing association'),
        'edit'  : _('Edit the selected association'),
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
        DbGUIElement.__init__(self, dbstate.db)
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('_Associations'), PersonRefModel,
                              move_buttons=True)

    def _connect_db_signals(self):
        """
        called on init of DbGUIElement, connect to db as required.
        """
        #note: person-rebuild closes the editors, so no need to connect to it
        self.callman.register_callbacks(
            {'person-update': self.person_change,  # change to person we track
             'person-delete': self.person_delete,  # delete of person we track
             })
        self.callman.connect_all(keys=['person'])

    def person_change(self, *obj):
        """
        Callback method called when a tracked person changes (description
        changes...)
        """
        self.rebuild()

    def person_delete(self, hndls):
        """
        Callback method called when a tracked person is deleted.
        There are two possibilities:
        * a tracked non-workgroup person is deleted, just rebuilding the view
            will correct this.
        * a workgroup person is deleted. The person must be removed from the
            obj so that no inconsistent data is shown.
        """
        for handle in hndls:
            ref_list = [pref.ref for pref in self.data]
            indexlist = []
            last = -1
            while True:
                try:
                    last = ref_list.index(handle, last + 1)
                    indexlist.append(last)
                except ValueError:
                    break
            #remove the deleted workgroup persons from the object
            for index in reversed(indexlist):
                del self.data[index]
        #now rebuild the display tab
        self.rebuild()

    def get_ref_editor(self):
        from .. import EditPersonRef
        return EditPersonRef

    def get_data(self):
        self.callman.register_handles(
            {'person': [pref.ref for pref in self.data]})
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

    def _handle_drag(self, row, obj):
        """
        And event reference that is from a drag and drop has
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
