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

_ = glocale.translation.gettext
from gi.repository import GLib

from gramps.gen.lib import DNAAttribute
from gramps.gen.errors import WindowActiveError
from ...ddtargets import DdTargets
from .srcattrmodel import SrcAttrModel
from .embeddedlist import EmbeddedList, TEXT_COL, ICON_COL, TEXT_EDIT_COL

# Common Y-STR marker names and mtDNA region names suggested in the type
# dropdown. Merged with any custom strings already stored in the database.
_DEFAULT_ATTR_TYPES = [
    "DYS393",
    "DYS390",
    "HVR1",
    "Coding",
]


class DNATestAttrEmbedList(EmbeddedList):
    """Attribute tab for DNA test records."""

    _HANDLE_COL = 3
    _DND_TYPE = DdTargets.DNAATTRIBUTE

    _MSG = {
        "add": _("Create and add a new attribute"),
        "del": _("Remove the existing attribute"),
        "edit": _("Edit the selected attribute"),
        "up": _("Move the selected attribute upwards"),
        "down": _("Move the selected attribute downwards"),
    }

    _column_names = [
        (_("Type"), 0, 300, TEXT_COL, -1, None),
        (_("Value"), 1, -1, TEXT_EDIT_COL, -1, None),
        (_("Private"), 2, 30, ICON_COL, -1, "gramps-lock"),
    ]

    def __init__(self, dbstate, uistate, track, data, config_key):
        self.data = data
        EmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            _("_Attributes"),
            SrcAttrModel,
            config_key,
            move_buttons=True,
        )

    def get_editor(self):
        from .. import EditSrcAttribute

        return EditSrcAttribute

    def get_user_values(self):
        db_values = self.dbstate.db.get_dnatest_attribute_types()
        return sorted(set(db_values) | set(_DEFAULT_ATTR_TYPES))

    def get_icon_name(self):
        return "gramps-attribute"

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 2), (1, 0), (1, 1))

    def setup_editable_col(self):
        self.edit_col_funcs = {
            1: {"edit_start": self.on_value_edit_start, "edited": self.on_value_edited}
        }

    def on_value_edit_start(self, cellr, celle, path, colnr):
        pass

    def on_value_edited(self, cell, path, new_text, colnr):
        node = self.model.get_iter(path)
        self.model.set_value(node, colnr, new_text)
        path = int(path)
        attr = self.data[path]
        attr.set_value(new_text)

    def add_button_clicked(self, obj):
        attr = DNAAttribute()
        try:
            self.get_editor()(
                self.dbstate,
                self.uistate,
                self.track,
                attr,
                "",
                self.get_user_values(),
                self.add_callback,
            )
        except WindowActiveError:
            pass

    def add_callback(self, name):
        data = self.get_data()
        data.append(name)
        self.changed = True
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        attr = self.get_selected()
        if attr:
            try:
                self.get_editor()(
                    self.dbstate,
                    self.uistate,
                    self.track,
                    attr,
                    "",
                    self.get_user_values(),
                    self.edit_callback,
                )
            except WindowActiveError:
                pass

    def edit_callback(self, name):
        self.changed = True
        self.rebuild()
