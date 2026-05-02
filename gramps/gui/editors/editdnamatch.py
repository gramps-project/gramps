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
EditDNAMatch, EditSharedAncestor, and EditDNASegment editor dialogs.
"""

from gi.repository import Gtk

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.lib import DNAMatch, DNASegment, NoteType, SharedAncestor
from gramps.gen.db import DbTxn
from ..display import display_help
from .editprimary import EditPrimary
from .editsecondary import EditSecondary
from .objectentries import DNATestEntry, PersonEntry
from ..glade import Glade
from ..dialog import ErrorDialog
from .displaytabs import (
    DNAMatchAttrEmbedList,
    CitationEmbedList,
    NoteTab,
    GalleryTab,
)
from .displaytabs.sharedancestorembedlist import SharedAncestorEmbedList
from .displaytabs.dnasegmentembedlist import DNASegmentEmbedList
from ..widgets import (
    MonitoredEntry,
    PrivacyButton,
    MonitoredTagList,
)

WIKI_HELP_PAGE = URL_MANUAL_PAGE
WIKI_HELP_SEC = _("DNA_Match_Editor", "manual")

# Chromosomes for the segment editor combo
_CHROMOSOMES = [str(i) for i in range(1, 23)] + ["X", "Y", "MT"]

# Phase labels indexed by DNASegment.PHASE_* constants
_PHASE_LABELS = [
    _("Unassigned"),
    _("Unknown"),
    _("Maternal"),
    _("Paternal"),
]

# Confidence labels indexed by SharedAncestor.CONF_* constants
_CONFIDENCE_LABELS = [
    _("Possible"),
    _("Probable"),
    _("Confirmed"),
    _("Rejected"),
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
# EditDNASegment
#
# -------------------------------------------------------------------------
class EditDNASegment(EditSecondary):
    """Mini-dialog for editing a single DNASegment secondary object."""

    def __init__(self, dbstate, uistate, track, segment, callback):
        EditSecondary.__init__(self, dbstate, uistate, track, segment, callback)

    def _local_init(self):
        self.top = Glade(filename="editdnasegment.glade")
        self.set_window(
            self.top.toplevel,
            None,
            _("DNA Segment Editor"),
        )
        self.setup_configs("interface.dnasegment", 480, 280)
        self.ok_button = self.top.get_object("ok")

    def _setup_fields(self):
        # Populate chromosome combo
        combo = self.top.get_object("chromosome")
        for chrom in _CHROMOSOMES:
            combo.append_text(chrom)
        chrom_val = self.obj.get_chromosome()
        if chrom_val in _CHROMOSOMES:
            combo.set_active(_CHROMOSOMES.index(chrom_val))
        else:
            combo.set_active(0)
        combo.connect("changed", self._on_chromosome_changed)
        combo.set_sensitive(not self.db.readonly)

        self.start_bp_field = MonitoredEntry(
            self.top.get_object("start_bp"),
            lambda x: self.obj.set_start_bp(_str_to_int(x)),
            lambda: _int_to_str(self.obj.get_start_bp()),
            self.db.readonly,
        )

        self.end_bp_field = MonitoredEntry(
            self.top.get_object("end_bp"),
            lambda x: self.obj.set_end_bp(_str_to_int(x)),
            lambda: _int_to_str(self.obj.get_end_bp()),
            self.db.readonly,
        )

        self.start_rsid_field = MonitoredEntry(
            self.top.get_object("start_rsid"),
            lambda x: self.obj.set_start_rsid(x.strip() or None),
            lambda: self.obj.get_start_rsid() or "",
            self.db.readonly,
        )

        self.end_rsid_field = MonitoredEntry(
            self.top.get_object("end_rsid"),
            lambda x: self.obj.set_end_rsid(x.strip() or None),
            lambda: self.obj.get_end_rsid() or "",
            self.db.readonly,
        )

        self.shared_cm_field = MonitoredEntry(
            self.top.get_object("shared_cm"),
            lambda x: self.obj.set_shared_cm(_str_to_float(x)),
            lambda: _float_to_str(self.obj.get_shared_cm()),
            self.db.readonly,
        )

        self.snp_count_field = MonitoredEntry(
            self.top.get_object("snp_count"),
            lambda x: self.obj.set_snp_count(_str_to_int(x)),
            lambda: _int_to_str(self.obj.get_snp_count()),
            self.db.readonly,
        )

        # Populate phase combo
        phase_combo = self.top.get_object("phase")
        for label in _PHASE_LABELS:
            phase_combo.append_text(label)
        phase_combo.set_active(self.obj.get_phase())
        phase_combo.connect("changed", self._on_phase_changed)
        phase_combo.set_sensitive(not self.db.readonly)

    def _on_chromosome_changed(self, combo):
        idx = combo.get_active()
        if 0 <= idx < len(_CHROMOSOMES):
            self.obj.set_chromosome(_CHROMOSOMES[idx])

    def _on_phase_changed(self, combo):
        self.obj.set_phase(combo.get_active())

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object("cancel"))
        self.define_ok_button(self.ok_button, self.save)

    def build_menu_names(self, obj):
        return (_("DNA Segment"), _("DNA Segment Editor"))

    def save(self, *obj):
        if self.callback:
            self.callback(self.obj)
        self.close()


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

        # Populate confidence combo
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


# -------------------------------------------------------------------------
#
# EditDNAMatch
#
# -------------------------------------------------------------------------
class EditDNAMatch(EditPrimary):
    def __init__(self, dbstate, uistate, track, dnamatch, callback=None):
        EditPrimary.__init__(
            self,
            dbstate,
            uistate,
            track,
            dnamatch,
            dbstate.db.get_dnamatch_from_handle,
            dbstate.db.get_dnamatch_from_gramps_id,
            callback,
        )

    def empty_object(self):
        return DNAMatch()

    def get_menu_title(self):
        handle = self.obj.get_handle()
        if handle:
            cm = self.obj.get_shared_cm()
            title = ("%.1f cM" % cm) if cm else str(self.obj.gramps_id)
            return _("DNA Match: %s") % title
        return _("New DNA Match")

    def _local_init(self):
        self.top = Glade()
        self.set_window(self.top.toplevel, None, self.get_menu_title())
        self.setup_configs("interface.dnamatch", 640, 520)

        self.subject_share_btn = self.top.get_object("select_subject_test")
        self.subject_add_del_btn = self.top.get_object("add_del_subject_test")
        self.match_share_btn = self.top.get_object("select_match_test")
        self.match_add_del_btn = self.top.get_object("add_del_match_test")

    def _connect_signals(self):
        self.top.get_object("cancel").connect("clicked", self.close)
        self.top.get_object("help").connect("clicked", self.help_clicked)
        self.ok_button = self.top.get_object("ok")
        self.ok_button.set_sensitive(not self.db.readonly)
        self.ok_button.connect("clicked", self.save)

    def _connect_db_signals(self):
        self._add_db_signal("dnamatch-rebuild", self._do_close)
        self._add_db_signal("dnamatch-delete", self.check_for_close)
        self._add_db_signal("dnatest-delete", self._dnatest_delete)

    def _setup_fields(self):
        self.subject_test_field = DNATestEntry(
            self.dbstate,
            self.uistate,
            self.track,
            self.top.get_object("subject_test_label"),
            self.top.get_object("subject_test_event_box"),
            self.obj.set_subject_test_handle,
            self.obj.get_subject_test_handle,
            self.subject_add_del_btn,
            self.subject_share_btn,
        )

        self.match_test_field = DNATestEntry(
            self.dbstate,
            self.uistate,
            self.track,
            self.top.get_object("match_test_label"),
            self.top.get_object("match_test_event_box"),
            self.obj.set_match_test_handle,
            self.obj.get_match_test_handle,
            self.match_add_del_btn,
            self.match_share_btn,
        )

        self.shared_cm_field = MonitoredEntry(
            self.top.get_object("shared_cm"),
            lambda x: self.obj.set_shared_cm(_str_to_float(x)),
            lambda: _float_to_str(self.obj.get_shared_cm()),
            self.db.readonly,
        )

        self.largest_segment_cm_field = MonitoredEntry(
            self.top.get_object("largest_segment_cm"),
            lambda x: self.obj.set_largest_segment_cm(_str_to_float(x)),
            lambda: _float_to_str(self.obj.get_largest_segment_cm()),
            self.db.readonly,
        )

        self.percent_shared_field = MonitoredEntry(
            self.top.get_object("percent_shared"),
            lambda x: self.obj.set_percent_shared(_str_to_float(x)),
            lambda: _float_to_str(self.obj.get_percent_shared()),
            self.db.readonly,
        )

        self.segment_count_field = MonitoredEntry(
            self.top.get_object("segment_count"),
            lambda x: self.obj.set_segment_count(_str_to_int(x)),
            lambda: _int_to_str(self.obj.get_segment_count()),
            self.db.readonly,
        )

        self.predicted_relationship_field = MonitoredEntry(
            self.top.get_object("predicted_relationship"),
            self.obj.set_predicted_relationship,
            self.obj.get_predicted_relationship,
            self.db.readonly,
        )

        self.predicted_generations_field = MonitoredEntry(
            self.top.get_object("predicted_generations"),
            lambda x: self.obj.set_predicted_generations(
                float(x.strip()) if x.strip() else None
            ),
            lambda: (
                str(self.obj.get_predicted_generations())
                if self.obj.get_predicted_generations() is not None
                else ""
            ),
            self.db.readonly,
        )

        self.gid = MonitoredEntry(
            self.top.get_object("gid"),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly,
        )

        self.tags = MonitoredTagList(
            self.top.get_object("tag_label"),
            self.top.get_object("tag_button"),
            self.obj.set_tag_list,
            self.obj.get_tag_list,
            self.db,
            self.uistate,
            self.track,
            self.db.readonly,
        )

        self.priv = PrivacyButton(
            self.top.get_object("private"), self.obj, self.db.readonly
        )

    def _create_tabbed_pages(self):
        notebook = Gtk.Notebook()

        self.shared_ancestor_list = SharedAncestorEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_shared_ancestor_list(),
            "dnamatch_editor_shared_ancestors",
        )
        self._add_tab(notebook, self.shared_ancestor_list)

        self.segment_list = DNASegmentEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_segment_list(),
            "dnamatch_editor_segments",
        )
        self._add_tab(notebook, self.segment_list)

        self.attr_list = DNAMatchAttrEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_attribute_list(),
            "dnamatch_editor_attributes",
        )
        self._add_tab(notebook, self.attr_list)

        self.note_list = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_note_list(),
            "dnamatch_editor_notes",
            notetype=NoteType.GENERAL,
        )
        self._add_tab(notebook, self.note_list)

        self.gallery_list = GalleryTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_media_list(),
        )
        self._add_tab(notebook, self.gallery_list)

        self.citation_list = CitationEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_citation_list(),
            "dnamatch_editor_citations",
            self.get_menu_title(),
        )
        self._add_tab(notebook, self.citation_list)

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.top.get_object("vbox").pack_start(notebook, True, True, 0)

        self.track_ref_for_deletion("shared_ancestor_list")
        self.track_ref_for_deletion("segment_list")
        self.track_ref_for_deletion("attr_list")
        self.track_ref_for_deletion("note_list")
        self.track_ref_for_deletion("gallery_list")
        self.track_ref_for_deletion("citation_list")

    def build_menu_names(self, dnamatch):
        return (_("Edit DNA Match"), self.get_menu_title())

    def help_clicked(self, obj):
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def save(self, *obj):
        self.ok_button.set_sensitive(False)

        if self.object_is_empty():
            ErrorDialog(
                _("Cannot save DNA match"),
                _(
                    "No data exists for this DNA match. Please "
                    "enter data or cancel the edit."
                ),
                parent=self.window,
            )
            self.ok_button.set_sensitive(True)
            return

        uses_dupe_id, id = self._uses_duplicate_id()
        if uses_dupe_id:
            prim_object = self.get_from_gramps_id(id)
            name = prim_object.gramps_id
            msg1 = _("Cannot save DNA match. ID already exists.")
            msg2 = _(
                "You have attempted to use the existing Gramps ID with "
                "value %(id)s. This value is already used by "
                "'%(prim_object)s'. Please enter a different ID or leave "
                "blank to get the next available ID value."
            ) % {"id": id, "prim_object": name}
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        if not self.obj.handle:
            with DbTxn(
                _("Add DNA Match (%s)") % self.obj.get_gramps_id(), self.db
            ) as trans:
                self.db.add_dnamatch(self.obj, trans)
        else:
            if self.data_has_changed():
                with DbTxn(
                    _("Edit DNA Match (%s)") % self.obj.get_gramps_id(), self.db
                ) as trans:
                    if not self.obj.get_gramps_id():
                        self.obj.set_gramps_id(
                            self.db.find_next_dnamatch_gramps_id()
                        )
                    self.db.commit_dnamatch(self.obj, trans)

        self._do_close()
        if self.callback:
            self.callback(self.obj)

    def _dnatest_delete(self, handle_list):
        sub = self.obj.get_subject_test_handle()
        mat = self.obj.get_match_test_handle()
        if sub in handle_list or mat in handle_list:
            self.close()
