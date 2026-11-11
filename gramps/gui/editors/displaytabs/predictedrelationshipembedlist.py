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
from gramps.gen.lib import PredictedRelationship
from .embeddedlist import EmbeddedList, TEXT_COL, ICON_COL

# -------------------------------------------------------------------------
#
# PredictedRelationshipModel
#
# -------------------------------------------------------------------------
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


def _side_label(side):
    return _SIDE_LABELS[side] if 0 <= side < len(_SIDE_LABELS) else str(side)


class PredictedRelationshipModel(Gtk.ListStore):
    def __init__(self, relationship_list, db):
        # columns: description, subject_side, match_side, foh, probability,
        #          has_citations, object
        Gtk.ListStore.__init__(self, str, str, str, str, str, bool, object)
        self.db = db
        for rel in relationship_list:
            foh = rel.get_full_or_half()
            foh_label = _FOH_LABELS[foh] if 0 <= foh < len(_FOH_LABELS) else str(foh)
            prob = rel.get_probability()
            prob_str = ("%g%%" % prob) if prob else ""
            self.append(
                [
                    rel.get_description(),
                    _side_label(rel.get_subject_side()),
                    _side_label(rel.get_match_side()),
                    foh_label,
                    prob_str,
                    rel.has_citations(),
                    rel,
                ]
            )


# -------------------------------------------------------------------------
#
# PredictedRelationshipEmbedList
#
# -------------------------------------------------------------------------
class PredictedRelationshipEmbedList(EmbeddedList):
    _HANDLE_COL = 6
    _DND_TYPE = None

    _MSG = {
        "add": _("Create and add a new predicted relationship"),
        "del": _("Remove the selected predicted relationship"),
        "edit": _("Edit the selected predicted relationship"),
        "up": _("Move the selected predicted relationship upwards"),
        "down": _("Move the selected predicted relationship downwards"),
    }

    _column_names = [
        (_("Description"), 0, 250, TEXT_COL, -1, None),
        (_("Subject side"), 1, 100, TEXT_COL, -1, None),
        (_("Match side"), 2, 100, TEXT_COL, -1, None),
        (_("Full/Half"), 3, 80, TEXT_COL, -1, None),
        (_("Probability"), 4, 90, TEXT_COL, -1, None),
        (_("Source"), 5, 30, ICON_COL, -1, "gramps-source"),
    ]

    def __init__(self, dbstate, uistate, track, data, config_key):
        self.data = data
        EmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            _("_Predicted Relationships"),
            PredictedRelationshipModel,
            config_key,
            move_buttons=True,
        )

    def get_editor(self):
        from .. import EditPredictedRelationship

        return EditPredictedRelationship

    def get_icon_name(self):
        return "gramps-person"

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 5), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4))

    def add_button_clicked(self, obj):
        rel = PredictedRelationship()
        try:
            self.get_editor()(
                self.dbstate,
                self.uistate,
                self.track,
                rel,
                self.add_callback,
            )
        except WindowActiveError:
            pass

    def add_callback(self, rel):
        data = self.get_data()
        data.append(rel)
        self.changed = True
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        rel = self.get_selected()
        if rel:
            try:
                self.get_editor()(
                    self.dbstate,
                    self.uistate,
                    self.track,
                    rel,
                    self.edit_callback,
                )
            except WindowActiveError:
                pass

    def edit_callback(self, rel):
        self.changed = True
        self.rebuild()
