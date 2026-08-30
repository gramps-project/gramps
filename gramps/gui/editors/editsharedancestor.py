#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
EditSharedAncestor editor dialog.
"""

from gi.repository import Gtk

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gramps.gen.lib import NoteType
from ..glade import Glade
from ..widgets import MonitoredEntry
from .editsecondary import EditSecondary
from .objectentries import PersonEntry
from .displaytabs import CitationEmbedList, NoteTab

_CONFIDENCE_LABELS = [
    _("Possible"),
    _("Probable"),
    _("Confirmed"),
    _("Rejected"),
]


# -------------------------------------------------------------------------
#
# EditSharedAncestor
#
# -------------------------------------------------------------------------
class EditSharedAncestor(EditSecondary):
    """Mini-dialog for editing a single SharedAncestor secondary object."""

    def __init__(self, dbstate, uistate, track, ancestor, callback):
        EditSecondary.__init__(self, dbstate, uistate, track, ancestor, callback)

    def _local_init(self):
        self.top = Glade(filename="editsharedancestor.glade")
        self.set_window(
            self.top.toplevel,
            None,
            _("Shared Ancestor Editor"),
        )
        self.setup_configs("interface.sharedancestor", 560, 420)
        self.ok_button = self.top.get_object("ok")

        self.share_btn = self.top.get_object("select_person")
        self.add_del_btn = self.top.get_object("add_del_person")

    def _setup_fields(self):
        self.person_field = PersonEntry(
            self.dbstate,
            self.uistate,
            self.track,
            self.top.get_object("person_label"),
            self.top.get_object("person_event_box"),
            self.obj.set_person_handle,
            self.obj.get_person_handle,
            self.add_del_btn,
            self.share_btn,
        )

        self.description_field = MonitoredEntry(
            self.top.get_object("description"),
            self.obj.set_description,
            self.obj.get_description,
            self.db.readonly,
        )

        combo = self.top.get_object("confidence")
        for label in _CONFIDENCE_LABELS:
            combo.append_text(label)
        combo.set_active(self.obj.get_confidence())
        combo.connect("changed", self._on_confidence_changed)
        combo.set_sensitive(not self.db.readonly)

    def _on_confidence_changed(self, combo):
        self.obj.set_confidence(combo.get_active())

    def _create_tabbed_pages(self):
        notebook = Gtk.Notebook()

        self.note_list = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_note_list(),
            "sharedancestor_editor_notes",
            notetype=NoteType.GENERAL,
        )
        self._add_tab(notebook, self.note_list)

        self.citation_list = CitationEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_citation_list(),
            "sharedancestor_editor_citations",
        )
        self._add_tab(notebook, self.citation_list)

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.top.get_object("vbox").pack_start(notebook, True, True, 0)

        self.track_ref_for_deletion("note_list")
        self.track_ref_for_deletion("citation_list")

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object("cancel"))
        self.define_ok_button(self.ok_button, self.save)

    def build_menu_names(self, obj):
        return (_("Shared Ancestor"), _("Shared Ancestor Editor"))

    def save(self, *obj):
        if self.callback:
            self.callback(self.obj)
        self.close()
