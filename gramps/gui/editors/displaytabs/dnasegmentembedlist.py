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
_ORIGIN_LABELS = [
    _("Unassigned"),
    _("Unknown"),
    _("Maternal"),
    _("Paternal"),
]

_IBD_STATE_LABELS = [
    _("Unknown"),
    _("HIR"),
    _("FIR"),
]

_CHROMOSOME_RANK = {"X": 23, "Y": 24, "MT": 25}


def _chromosome_sort_key(chromosome):
    """Return a key ordering the numbered chromosomes first, then X, Y and MT."""
    text = (chromosome or "").strip().upper()
    if text.isdigit():
        return "%03d" % int(text)
    if text in _CHROMOSOME_RANK:
        return "%03d" % _CHROMOSOME_RANK[text]
    return "999%s" % text


class DNASegmentModel(Gtk.ListStore):
    """
    List store backing the segment tab of the DNA match editor.

    The displayed columns hold formatted text. Each numeric field also has a
    sort column holding a padded key, so the tree view orders the rows by
    value rather than by the text form.
    """

    COL_SORT_CHROMOSOME = 8
    COL_SORT_START = 9
    COL_SORT_END = 10
    COL_SORT_SHARED_CM = 11
    COL_SORT_SNP_COUNT = 12

    def __init__(self, segment_list, db):
        # columns: chromosome, start_bp, end_bp, shared_cm, snp_count, origin,
        # ibd_state, object, then the sort keys for the numeric columns
        Gtk.ListStore.__init__(
            self,
            str,
            str,
            str,
            str,
            str,
            str,
            str,
            object,
            str,
            str,
            str,
            str,
            str,
        )
        self.db = db
        for seg in segment_list:
            origin = seg.get_origin()
            origin_label = (
                _ORIGIN_LABELS[origin]
                if 0 <= origin < len(_ORIGIN_LABELS)
                else str(origin)
            )
            ibd = seg.get_ibd_state()
            ibd_label = (
                _IBD_STATE_LABELS[ibd]
                if 0 <= ibd < len(_IBD_STATE_LABELS)
                else str(ibd)
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
                    origin_label,
                    ibd_label,
                    seg,
                    _chromosome_sort_key(seg.get_chromosome()),
                    "%012d" % (seg.get_start_bp() or 0),
                    "%012d" % (seg.get_end_bp() or 0),
                    "%015.4f" % (seg.get_shared_cm() or 0.0),
                    "%010d" % (seg.get_snp_count() or 0),
                ]
            )


# -------------------------------------------------------------------------
#
# DNASegmentEmbedList
#
# -------------------------------------------------------------------------
class DNASegmentEmbedList(EmbeddedList):
    _HANDLE_COL = 7
    _DND_TYPE = None

    _MSG = {
        "add": _("Create and add a new segment"),
        "del": _("Remove the selected segment"),
        "edit": _("Edit the selected segment"),
        "up": _("Move the selected segment upwards"),
        "down": _("Move the selected segment downwards"),
    }

    # index = column in model, value = (name, sortcol in model, width,
    # markup/text, weight_col, icon)
    _column_names = [
        (_("Chr"), DNASegmentModel.COL_SORT_CHROMOSOME, 50, TEXT_COL, -1, None),
        (_("Start"), DNASegmentModel.COL_SORT_START, 100, TEXT_COL, -1, None),
        (_("End"), DNASegmentModel.COL_SORT_END, 100, TEXT_COL, -1, None),
        (_("cM"), DNASegmentModel.COL_SORT_SHARED_CM, 70, TEXT_COL, -1, None),
        (_("SNPs"), DNASegmentModel.COL_SORT_SNP_COUNT, 70, TEXT_COL, -1, None),
        (_("Origin"), 5, 90, TEXT_COL, -1, None),
        (_("IBD"), 6, 70, TEXT_COL, -1, None),
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
        return ((1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6))

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
