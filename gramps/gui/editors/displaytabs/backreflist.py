#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009-2011  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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

# -------------------------------------------------------------------------
#
# GTK libraries
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from ...widgets import SimpleButton
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL
from ...utils import edit_object


# -------------------------------------------------------------------------
#
# BackRefList
#
# -------------------------------------------------------------------------
class BackRefList(EmbeddedList):
    _HANDLE_COL = 3

    # index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_("Type"), 0, 100, TEXT_COL, -1, None),
        (_("ID"), 1, 75, TEXT_COL, -1, None),
        (_("Name"), 2, 250, TEXT_COL, -1, None),
    ]

    def __init__(
        self, dbstate, uistate, track, obj, refmodel, config_key, callback=None
    ):
        self.obj = obj
        EmbeddedList.__init__(
            self, dbstate, uistate, track, _("_References"), refmodel, config_key
        )
        self._callback = callback
        self.connectid = self.model.connect("row-inserted", self.update_label)
        self.db_connect = []
        for item in [
            "person",
            "family",
            "source",
            "citation",
            "event",
            "media",
            "place",
            "repository",
            "note",
        ]:
            self.db_connect.append(
                self.dbstate.db.connect("%s-delete" % item, self.model.delete_row)
            )
        self.tree.set_reorderable(False)
        self.track_ref_for_deletion("model")

    def update_label(self, *obj):
        if self.model.count > 0:
            self._set_label()
        if self._callback and self.model.count > 1:
            self._callback()

    def right_click(self, obj, event):
        return

    def _cleanup_local_connects(self):
        self.model.disconnect(self.connectid)
        for item in self.db_connect:
            self.dbstate.db.disconnect(item)

    def _cleanup_on_exit(self):
        # model may be destroyed already in closing managedwindow
        if hasattr(self, "model"):
            self.model.destroy()

    def is_empty(self):
        return self.model.count == 0

    def _create_buttons(self, share=False, move=False, jump=False, top_label=None):
        """
        Create a button box consisting of one button: Edit.
        This button box is then appended hbox (self).
        Method has signature of, and overrides create_buttons from _ButtonTab.py
        """
        self.edit_btn = SimpleButton("gtk-edit", self.edit_button_clicked)
        self.edit_btn.set_tooltip_text(_("Edit reference"))

        hbox = Gtk.Box()
        hbox.set_spacing(6)
        hbox.pack_start(self.edit_btn, False, True, 0)
        hbox.show_all()
        self.pack_start(hbox, False, True, 0)

        self.add_btn = None
        self.del_btn = None

        self.track_ref_for_deletion("edit_btn")
        self.track_ref_for_deletion("add_btn")
        self.track_ref_for_deletion("del_btn")

    def _selection_changed(self, obj=None):
        if self.dirty_selection:
            return
        if self.get_selected():
            self.edit_btn.set_sensitive(True)
        else:
            self.edit_btn.set_sensitive(False)

    def get_data(self):
        return self.obj

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2))

    def find_node(self):
        (model, node) = self.selection.get_selected()
        try:
            return (model.get_value(node, 4), model.get_value(node, 3))
        except:
            return (None, None)

    def edit_button_clicked(self, obj):
        (reftype, ref) = self.find_node()
        edit_object(self.dbstate, self.uistate, reftype, ref)
