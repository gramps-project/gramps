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
EditDNASegment editor dialog.
"""

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from ..glade import Glade
from ..widgets import MonitoredEntry
from .editsecondary import EditSecondary

_CHROMOSOMES = [str(i) for i in range(1, 23)] + ["X", "Y", "MT"]

_PHASE_LABELS = [
    _("Unassigned"),
    _("Unknown"),
    _("Maternal"),
    _("Paternal"),
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
