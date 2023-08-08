#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

# -------------------------------------------------------------------------
#
# Python classes
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import GLib

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Note
from ...dbguielement import DbGUIElement
from ...selectors import SelectorFactory
from .notemodel import NoteModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL
from ...ddtargets import DdTargets


# -------------------------------------------------------------------------
#
# NoteTab
#
# -------------------------------------------------------------------------
class NoteTab(EmbeddedList, DbGUIElement):
    """
    Note List display tab for edit dialogs.

    Derives from the EmbeddedList class.
    """

    _HANDLE_COL = 3
    _DND_TYPE = DdTargets.NOTE_LINK

    _MSG = {
        "add": _("Create and add a new note"),
        "del": _("Remove the existing note"),
        "edit": _("Edit the selected note"),
        "share": _("Add an existing note"),
        "up": _("Move the selected note upwards"),
        "down": _("Move the selected note downwards"),
    }

    # index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_("Type"), 0, 100, TEXT_COL, -1, None),
        (_("Preview"), 1, 200, TEXT_COL, -1, None),
        (_("Private"), 2, 30, ICON_COL, -1, "gramps-lock"),
    ]

    def __init__(
        self,
        dbstate,
        uistate,
        track,
        data,
        config_key,
        callertitle=None,
        notetype=None,
    ):
        self.data = data
        self.callertitle = callertitle
        self.notetype = notetype
        EmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            _("_Notes"),
            NoteModel,
            config_key,
            share_button=True,
            move_buttons=True,
        )
        DbGUIElement.__init__(self, dbstate.db)
        self.callman.register_handles({"note": self.data})

    def _connect_db_signals(self):
        """
        Implement base class DbGUIElement method
        """
        # note: note-rebuild closes the editors, so no need to connect to it
        self.callman.register_callbacks(
            {
                "note-delete": self.note_delete,  # delete a note we track
                "note-update": self.note_update,  # change a note we track
            }
        )
        self.callman.connect_all(keys=["note"])

    def get_editor(self):
        pass

    def get_user_values(self):
        return []

    def get_data(self):
        """
        Return the data associated with display tab
        """
        return self.data

    def column_order(self):
        """
        Return the column order of the columns in the display tab.
        """
        return ((1, 2), (1, 0), (1, 1))

    def add_button_clicked(self, obj):
        """
        Create a new Note instance and call the EditNote editor with the new
        note.

        Called when the Add button is clicked.
        If the window already exists (WindowActiveError), we ignore it.
        This prevents the dialog from coming up twice on the same object.
        """
        note = Note()
        if self.notetype:
            note.set_type(self.notetype)
        try:
            from .. import EditNote

            EditNote(
                self.dbstate,
                self.uistate,
                self.track,
                note,
                self.add_callback,
                self.callertitle,
                extratype=[self.notetype],
            )
        except WindowActiveError:
            pass

    def add_callback(self, name):
        """
        Called to update the screen when a new note is added
        """
        data = self.get_data()
        data.append(name)
        self.callman.register_handles({"note": [name]})
        self.changed = True
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        """
        Get the selected Note instance and call the EditNote editor with the
        note.

        Called when the Edit button is clicked.
        If the window already exists (WindowActiveError), we ignore it.
        This prevents the dialog from coming up twice on the same object.
        """
        handle = self.get_selected()
        if handle:
            note = self.dbstate.db.get_note_from_handle(handle)
            try:
                from .. import EditNote

                EditNote(
                    self.dbstate,
                    self.uistate,
                    self.track,
                    note,
                    callertitle=self.callertitle,
                    extratype=[self.notetype],
                )
            except WindowActiveError:
                pass

    def share_button_clicked(self, obj):
        SelectNote = SelectorFactory("Note")

        sel = SelectNote(self.dbstate, self.uistate, self.track)
        note = sel.run()
        if note:
            self.add_callback(note.handle)

    def get_icon_name(self):
        """
        Return the stock-id icon name associated with the display tab
        """
        return "gramps-notes"

    def note_delete(self, del_note_handle_list):
        """
        Outside of this tab note objects have been deleted. Check if tab
        and object must be changed.
        Note: delete of object will cause reference on database to be removed,
            so this method need not do this
        """
        rebuild = False
        for handle in del_note_handle_list:
            while self.data.count(handle) > 0:
                self.data.remove(handle)
                rebuild = True
        if rebuild:
            self.rebuild()

    def note_update(self, upd_note_handle_list):
        """
        Outside of this tab note objects have been updated. Check if tab
        and object must be updated.
        """
        for handle in upd_note_handle_list:
            if handle in self.data:
                self.rebuild()
                break
