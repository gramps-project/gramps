#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2025       Steve Youngs
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
from gi.repository import GObject

"""
Package providing filtering framework for Gramps.
"""

# -------------------------------------------------------------------------
#
# GTK
#
# -------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from ..utils import no_match_primary_mask

_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")


# -------------------------------------------------------------------------
#
# SearchBar
#
# -------------------------------------------------------------------------
class SearchBar:
    def __init__(self, dbstate, uistate, on_apply, apply_done=None, apply_clear=None):
        self.on_apply_callback = on_apply
        self.apply_done_callback = apply_done
        self.apply_clear_callback = apply_clear
        self.dbstate = dbstate
        self.uistate = uistate
        self.apply_text = ""
        self.visible = False

        self.searchbar = Gtk.Box()
        self.search_text = Gtk.Entry()
        self.find_button = Gtk.Button.new_with_mnemonic(_("_Find"))
        self.clear_button = Gtk.Button.new_with_mnemonic(_("_Clear"))
        self.search_list = Gtk.ComboBox()
        self.search_model = Gtk.ListStore(
            GObject.TYPE_STRING,  # rule name
            GObject.TYPE_INT,  # index of column to search
            GObject.TYPE_BOOLEAN,  # inversion: invert the search result if True
            GObject.TYPE_BOOLEAN,  # type : True = filter, False = search
            GObject.TYPE_PYOBJECT,  # filter object
        )

    def destroy(self):
        """Unset all things that can block garbage collection."""
        self.on_apply_callback = None
        self.apply_done_callback = None
        self.dbstate = None
        self.uistate = None

    def build(self):
        self.searchbar.set_spacing(4)
        self.search_list.connect("changed", self.search_changed)

        self.search_text.connect("key-press-event", self.key_press)
        self.search_text.connect("changed", self.text_changed)

        self.find_button.connect("clicked", self.apply_find_clicked)
        self.find_button.set_sensitive(False)

        self.clear_button.connect("clicked", self.apply_clear)
        self.clear_button.set_sensitive(False)

        self.searchbar.pack_start(self.search_list, False, True, 0)
        self.searchbar.pack_start(self.search_text, True, True, 0)
        self.searchbar.pack_end(self.clear_button, False, True, 0)
        self.searchbar.pack_end(self.find_button, False, True, 0)

        return self.searchbar

    def setup_searches(self, column_data):
        """
        column_data is a list of tuples:
        [(trans_col_name, index, use_exact), ...]
        """
        self.search_model.clear()
        old_value = self.search_list.get_active()

        cell = Gtk.CellRendererText()
        self.search_list.clear()
        self.search_list.pack_start(cell, True)
        self.search_list.add_attribute(cell, "text", 0)

        maxval = 0
        for col, index, exact in column_data:
            if exact:
                rule = _("%s is") % col
            else:
                rule = _("%s contains") % col
            self.search_model.append(row=[rule, index, False, False, None])
            maxval += 1
            if exact:
                rule = _("%s is not") % col
            else:
                rule = _("%s does not contain") % col
            self.search_model.append(row=[rule, index, True, False, None])
            maxval += 1

        self.search_list.set_model(self.search_model)
        if old_value == -1 or old_value >= maxval:
            self.search_list.set_active(0)
        else:
            self.search_list.set_active(old_value)

    def append_filter(self, filter_name, filter):
        self.search_model.append(row=[filter_name, -1, False, True, filter])

    def search_changed(self, obj):
        self.find_button.set_sensitive(True)
        # only make the search_text and clear_button widgets sensitive for searches
        node = self.search_list.get_active_iter()
        type = self.search_model.get_value(node, 3) if node else False
        self.clear_button.set_sensitive(not type)
        self.search_text.set_sensitive(not type)

    def text_changed(self, obj):
        text = obj.get_text()
        if self.apply_text == "" and text == "":
            self.find_button.set_sensitive(False)
            self.clear_button.set_sensitive(False)
        elif self.apply_text == text:
            self.find_button.set_sensitive(False)
            self.clear_button.set_sensitive(True)
        else:
            self.find_button.set_sensitive(True)
            self.clear_button.set_sensitive(True)

    def key_press(self, obj, event):
        if no_match_primary_mask(event.get_state()):
            if event.keyval in (_RETURN, _KP_ENTER):
                self.find_button.set_sensitive(False)
                self.clear_button.set_sensitive(True)
                self.apply_search()
        return False

    def apply_find_clicked(self, obj):
        self.apply_search()

    def apply_clear(self, obj):
        self.search_text.set_text("")
        self.apply_search()
        if self.apply_clear_callback is not None:
            self.apply_clear_callback()

    def get_value(self):
        text = str(self.search_text.get_text()).strip()
        node = self.search_list.get_active_iter()
        index = self.search_model.get_value(node, 1)
        inv = self.search_model.get_value(node, 2)
        type = self.search_model.get_value(node, 3)
        filter = self.search_model.get_value(node, 4)
        return (type, filter, False) if type else (type, (index, text, inv), False)

    def apply_search(self, current_model=None):
        self.apply_text = str(self.search_text.get_text())
        self.find_button.set_sensitive(False)
        self.uistate.status_text(_("Updating display..."))
        self.on_apply_callback()
        self.search_text.grab_focus()
        self.uistate.modify_statusbar(self.dbstate)

    def show(self):
        self.searchbar.show()
        self.visible = True

    def hide(self):
        self.searchbar.hide()
        self.visible = False

    def is_visible(self):
        return self.visible
