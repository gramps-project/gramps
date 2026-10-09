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
EditPredictedRelationship editor dialog.
"""

from gi.repository import Gtk

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gramps.gen.lib import NoteType
from ..glade import Glade
from ..widgets import MonitoredEntry
from .editsecondary import EditSecondary
from .displaytabs import CitationEmbedList, NoteTab

_SIDE_LABELS = [
    _("Unknown"),
    _("Maternal"),
    _("Paternal"),
    _("Both"),
]

_FOH_LABELS = [
    _("Unknown"),
    _("Half"),
    _("Full"),
]


def _str_to_float(s):
    try:
        return float(s.strip()) if s.strip() else 0.0
    except ValueError:
        return 0.0


def _str_to_int(s):
    try:
        return int(s.strip()) if s.strip() else 0
    except ValueError:
        return 0


def _float_to_str(f):
    return str(f) if f else ""


def _int_to_str(i):
    return str(i) if i else ""


# -------------------------------------------------------------------------
#
# EditPredictedRelationship
#
# -------------------------------------------------------------------------
class EditPredictedRelationship(EditSecondary):
    """Mini-dialog for editing a single PredictedRelationship secondary object."""

    def __init__(self, dbstate, uistate, track, relationship, callback):
        EditSecondary.__init__(self, dbstate, uistate, track, relationship, callback)

    def _local_init(self):
        self.top = Glade(filename="editpredictedrelationship.glade")
        self.set_window(
            self.top.toplevel,
            None,
            _("Predicted Relationship Editor"),
        )
        self.setup_configs("interface.predictedrelationship", 560, 420)
        self.ok_button = self.top.get_object("ok")

    def _setup_fields(self):
        self.description_field = MonitoredEntry(
            self.top.get_object("description"),
            self.obj.set_description,
            self.obj.get_description,
            self.db.readonly,
        )

        self.subject_mrca_gens_field = MonitoredEntry(
            self.top.get_object("subject_mrca_gens"),
            lambda x: self.obj.set_subject_mrca_gens(_str_to_int(x)),
            lambda: _int_to_str(self.obj.get_subject_mrca_gens()),
            self.db.readonly,
        )

        self.match_mrca_gens_field = MonitoredEntry(
            self.top.get_object("match_mrca_gens"),
            lambda x: self.obj.set_match_mrca_gens(_str_to_int(x)),
            lambda: _int_to_str(self.obj.get_match_mrca_gens()),
            self.db.readonly,
        )

        self.probability_field = MonitoredEntry(
            self.top.get_object("probability"),
            lambda x: self.obj.set_probability(_str_to_float(x)),
            lambda: _float_to_str(self.obj.get_probability()),
            self.db.readonly,
        )

        subject_combo = self.top.get_object("subject_side")
        for label in _SIDE_LABELS:
            subject_combo.append_text(label)
        subject_combo.set_active(self.obj.get_subject_side())
        subject_combo.connect("changed", self._on_subject_side_changed)
        subject_combo.set_sensitive(not self.db.readonly)

        match_combo = self.top.get_object("match_side")
        for label in _SIDE_LABELS:
            match_combo.append_text(label)
        match_combo.set_active(self.obj.get_match_side())
        match_combo.connect("changed", self._on_match_side_changed)
        match_combo.set_sensitive(not self.db.readonly)

        foh_combo = self.top.get_object("full_or_half")
        for label in _FOH_LABELS:
            foh_combo.append_text(label)
        foh_combo.set_active(self.obj.get_full_or_half())
        foh_combo.connect("changed", self._on_full_or_half_changed)
        foh_combo.set_sensitive(not self.db.readonly)

    def _on_subject_side_changed(self, combo):
        self.obj.set_subject_side(combo.get_active())

    def _on_match_side_changed(self, combo):
        self.obj.set_match_side(combo.get_active())

    def _on_full_or_half_changed(self, combo):
        self.obj.set_full_or_half(combo.get_active())

    def _create_tabbed_pages(self):
        notebook = Gtk.Notebook()

        self.note_list = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_note_list(),
            "predictedrelationship_editor_notes",
            notetype=NoteType.GENERAL,
        )
        self._add_tab(notebook, self.note_list)

        self.citation_list = CitationEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_citation_list(),
            "predictedrelationship_editor_citations",
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
        return (_("Predicted Relationship"), _("Predicted Relationship Editor"))

    def save(self, *obj):
        if self.callback:
            self.callback(self.obj)
        self.close()
