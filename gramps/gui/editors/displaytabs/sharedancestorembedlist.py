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
from gramps.gen.lib import SharedAncestor
from gramps.gen.display.name import displayer as name_displayer
from .embeddedlist import EmbeddedList, TEXT_COL, ICON_COL


# -------------------------------------------------------------------------
#
# SharedAncestorModel
#
# -------------------------------------------------------------------------
_CONFIDENCE_LABELS = [
    _("Possible"),
    _("Probable"),
    _("Confirmed"),
    _("Rejected"),
]


class SharedAncestorModel(Gtk.ListStore):
    def __init__(self, ancestor_list, db):
        # columns: person_display, description, confidence_label, has_citations, object
        Gtk.ListStore.__init__(self, str, str, str, bool, object)
        self.db = db
        for anc in ancestor_list:
            handle = anc.get_person_handle()
            if handle:
                person = db.get_person_from_handle(handle)
                person_name = (
                    name_displayer.display(person) if person else _("Unknown")
                )
            else:
                person_name = _("(unidentified)")
            conf = anc.get_confidence()
            conf_label = (
                _CONFIDENCE_LABELS[conf]
                if 0 <= conf < len(_CONFIDENCE_LABELS)
                else str(conf)
            )
            self.append(
                [
                    person_name,
                    anc.get_description(),
                    conf_label,
                    anc.has_citations(),
                    anc,
                ]
            )


# -------------------------------------------------------------------------
#
# SharedAncestorEmbedList
#
# -------------------------------------------------------------------------
class SharedAncestorEmbedList(EmbeddedList):
    _HANDLE_COL = 4
    _DND_TYPE = None

    _MSG = {
        "add": _("Create and add a new shared ancestor"),
        "del": _("Remove the selected shared ancestor"),
        "edit": _("Edit the selected shared ancestor"),
        "up": _("Move the selected shared ancestor upwards"),
        "down": _("Move the selected shared ancestor downwards"),
    }

    _column_names = [
        (_("Person"), 0, 250, TEXT_COL, -1, None),
        (_("Description"), 1, 200, TEXT_COL, -1, None),
        (_("Confidence"), 2, 100, TEXT_COL, -1, None),
        (_("Source"), 3, 30, ICON_COL, -1, "gramps-source"),
    ]

    def __init__(self, dbstate, uistate, track, data, config_key):
        self.data = data
        EmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            _("_Shared Ancestors"),
            SharedAncestorModel,
            config_key,
            move_buttons=True,
        )

    def get_editor(self):
        from .. import EditSharedAncestor

        return EditSharedAncestor

    def get_icon_name(self):
        return "gramps-person"

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 3), (1, 0), (1, 1), (1, 2))

    def add_button_clicked(self, obj):
        anc = SharedAncestor()
        try:
            self.get_editor()(
                self.dbstate,
                self.uistate,
                self.track,
                anc,
                self.add_callback,
            )
        except WindowActiveError:
            pass

    def add_callback(self, anc):
        data = self.get_data()
        data.append(anc)
        self.changed = True
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        anc = self.get_selected()
        if anc:
            try:
                self.get_editor()(
                    self.dbstate,
                    self.uistate,
                    self.track,
                    anc,
                    self.edit_callback,
                )
            except WindowActiveError:
                pass

    def edit_callback(self, anc):
        self.changed = True
        self.rebuild()
