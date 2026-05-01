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

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gi.repository import GLib, Gtk

from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import DNASegment
from .embeddedlist import EmbeddedList, TEXT_COL


# -------------------------------------------------------------------------
#
# DNASegmentModel
#
# -------------------------------------------------------------------------
_PHASE_LABELS = [
    _("Unassigned"),
    _("Unknown"),
    _("Maternal"),
    _("Paternal"),
]


class DNASegmentModel(Gtk.ListStore):
    def __init__(self, segment_list, db):
        # columns: chromosome, start_bp, end_bp, shared_cm, snp_count, phase, object
        Gtk.ListStore.__init__(self, str, str, str, str, str, str, object)
        self.db = db
        for seg in segment_list:
            phase = seg.get_phase()
            phase_label = (
                _PHASE_LABELS[phase]
                if 0 <= phase < len(_PHASE_LABELS)
                else str(phase)
            )
            start = str(seg.get_start_bp()) if seg.get_start_bp() else ""
            end = str(seg.get_end_bp()) if seg.get_end_bp() else ""
            cm = str(seg.get_shared_cm()) if seg.get_shared_cm() else ""
            snps = str(seg.get_snp_count()) if seg.get_snp_count() else ""
            self.append(
                [
                    seg.get_chromosome(),
                    start,
                    end,
                    cm,
                    snps,
                    phase_label,
                    seg,
                ]
            )


# -------------------------------------------------------------------------
#
# DNASegmentEmbedList
#
# -------------------------------------------------------------------------
class DNASegmentEmbedList(EmbeddedList):
    _HANDLE_COL = 6
    _DND_TYPE = None

    _MSG = {
        "add": _("Create and add a new segment"),
        "del": _("Remove the selected segment"),
        "edit": _("Edit the selected segment"),
        "up": _("Move the selected segment upwards"),
        "down": _("Move the selected segment downwards"),
    }

    _column_names = [
        (_("Chr"), 0, 50, TEXT_COL, -1, None),
        (_("Start"), 1, 100, TEXT_COL, -1, None),
        (_("End"), 2, 100, TEXT_COL, -1, None),
        (_("cM"), 3, 70, TEXT_COL, -1, None),
        (_("SNPs"), 4, 70, TEXT_COL, -1, None),
        (_("Phase"), 5, 90, TEXT_COL, -1, None),
    ]

    def __init__(self, dbstate, uistate, track, data, config_key):
        self.data = data
        EmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            _("_Segments"),
            DNASegmentModel,
            config_key,
            move_buttons=True,
        )

    def get_editor(self):
        from .. import EditDNASegment

        return EditDNASegment

    def get_icon_name(self):
        return "gramps-media"

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5))

    def add_button_clicked(self, obj):
        seg = DNASegment()
        try:
            self.get_editor()(
                self.dbstate,
                self.uistate,
                self.track,
                seg,
                self.add_callback,
            )
        except WindowActiveError:
            pass

    def add_callback(self, seg):
        data = self.get_data()
        data.append(seg)
        self.changed = True
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        seg = self.get_selected()
        if seg:
            try:
                self.get_editor()(
                    self.dbstate,
                    self.uistate,
                    self.track,
                    seg,
                    self.edit_callback,
                )
            except WindowActiveError:
                pass

    def edit_callback(self, seg):
        self.changed = True
        self.rebuild()
