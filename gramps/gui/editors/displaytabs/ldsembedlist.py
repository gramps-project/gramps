#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
from gi.repository import GObject, GLib

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from gramps.gen.lib import LdsOrd
from gramps.gen.errors import WindowActiveError
from .ldsmodel import LdsModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
class LdsEmbedList(EmbeddedList):
    _HANDLE_COL = 7
    #    _DND_TYPE = DdTargets.ADDRESS

    _MSG = {
        "add": _("Create and add a new LDS ordinance"),
        "del": _("Remove the existing LDS ordinance"),
        "edit": _("Edit the selected LDS ordinance"),
        "up": _("Move the selected LDS ordinance upwards"),
        "down": _("Move the selected LDS ordinance downwards"),
    }

    # index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_("Type"), 0, 150, TEXT_COL, -1, None),
        (_("Date"), 1, 150, MARKUP_COL, -1, None),
        (_("Status"), 3, 75, TEXT_COL, -1, None),
        (_("Temple"), 2, 200, TEXT_COL, -1, None),
        (_("Place"), 4, 100, TEXT_COL, -1, None),
        (_("Source"), 5, 30, ICON_COL, -1, "gramps-source"),
        (_("Private"), 6, 30, ICON_COL, -1, "gramps-lock"),
    ]

    def __init__(self, dbstate, uistate, track, data, config_key):
        self.data = data
        EmbeddedList.__init__(
            self,
            dbstate,
            uistate,
            track,
            _("_LDS"),
            LdsModel,
            config_key,
            move_buttons=True,
        )

    def get_editor(self):
        from .. import EditLdsOrd

        return EditLdsOrd

    def new_data(self):
        return LdsOrd()

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 5), (1, 6), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4))

    def add_button_clicked(self, obj):
        try:
            self.get_editor()(
                self.dbstate,
                self.uistate,
                self.track,
                self.new_data(),
                self.add_callback,
            )
        except WindowActiveError:
            pass

    def add_callback(self, name):
        data = self.get_data()
        data.append(name)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        lds = self.get_selected()
        if lds:
            try:
                self.get_editor()(
                    self.dbstate, self.uistate, self.track, lds, self.edit_callback
                )
            except WindowActiveError:
                pass

    def edit_callback(self, name):
        self.rebuild()
