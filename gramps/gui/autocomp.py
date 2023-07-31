#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

"""
Provide autocompletion functionality.
"""

# -------------------------------------------------------------------------
#
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


def fill_combo(combo, data_list):
    """
    Fill a combo box with completion data
    """
    store = Gtk.ListStore(GObject.TYPE_STRING)

    for data in data_list:
        if data:
            store.append(row=[data])

    combo.set_model(store)
    combo.set_entry_text_column(0)
    completion = Gtk.EntryCompletion()
    completion.set_model(store)
    completion.set_minimum_key_length(1)
    completion.set_text_column(0)
    combo.get_child().set_completion(completion)


def fill_entry(entry, data_list):
    """
    Fill a entry with completion data
    """

    store = Gtk.ListStore(GObject.TYPE_STRING)

    for data in data_list:
        if data:
            store.append(row=[data])

    completion = Gtk.EntryCompletion()
    completion.set_model(store)
    completion.set_minimum_key_length(1)
    completion.set_text_column(0)
    entry.set_completion(completion)


# -------------------------------------------------------------------------
#
# StandardCustomSelector class
#
# -------------------------------------------------------------------------
class StandardCustomSelector:
    """
    This class provides an interface to selecting from the predefined
    options or entering custom string.

    The typical usage should be:
        type_sel = StandardCustomSelector(mapping,None,custom_key,active_key)
        whatever_table.attach(type_sel,...)
    or
        type_sel = StandardCustomSelector(mapping,cbe,custom_key,active_key)
    with the existing ComboBoxEntry cbe.

    To set up the combo box, specify the active key at creation time,
    or later (or with custom text) use:
        type_sel.set_values(i,s)

    and later, when or before the dialog is closed, do:
        (i,s) = type_sel.get_values()

    to obtain the tuple of (int,str) corresponding to the user selection.

    No selection will return (custom_key,'') if the custom key is given,
    or (None,'') if it is not given.

    The active_key determines the default selection that will be displayed
    upon widget creation. If omitted, the entry will be empty. If present,
    then no selection on the user's part will return the
    (active_key,mapping[active_key]) tuple.

    """

    def __init__(
        self,
        mapping,
        cbe=None,
        custom_key=None,
        active_key=None,
        additional=None,
        menu=None,
    ):
        """
        Constructor for the StandardCustomSelector class.

        :param cbe: Existing ComboBoxEntry widget to use.
        :type cbe: Gtk.ComboBoxEntry
        :param mapping: The mapping between integer and string constants.
        :type mapping:  dict
        :param custom_key: The key corresponding to the custom string entry
        :type custom_key:  int
        :param active_key: The key for the entry to make active upon creation
        :type active_key:  int
        """

        # set variables
        self.mapping = mapping
        self.custom_key = custom_key
        self.active_key = active_key
        self.active_index = 0
        self.additional = additional
        self.menu = menu

        # create combo box entry
        if cbe:
            assert cbe.get_has_entry()
            self.selector = cbe
        else:
            self.selector = Gtk.ComboBox(has_entry=True)

        # create models
        if menu:
            self.store = self.create_menu()
            completion_store = self.create_list()
        else:
            self.store = self.create_list()
            completion_store = self.store

        self.selector.set_model(self.store)
        self.selector.set_entry_text_column(1)

        if menu:
            for cell in self.selector.get_cells():
                self.selector.add_attribute(cell, "sensitive", 2)

        # renderer = Gtk.CellRendererText()
        # self.selector.pack_start(renderer, True)
        # self.selector.add_attribute(renderer, 'text', 1)
        # if self.active_key is not None:
        # self.selector.set_active(self.active_index)

        # make autocompletion work
        completion = Gtk.EntryCompletion()
        completion.set_model(completion_store)
        completion.set_minimum_key_length(1)
        completion.set_text_column(1)
        self.selector.get_child().set_completion(completion)

    def create_menu(self):
        """
        Create a model and fill it with a two-level tree corresponding to the
        menu.
        """
        store = Gtk.TreeStore(int, str, bool)
        for heading, items in self.menu:
            if self.active_key in items:
                parent = None
            else:
                parent = store.append(None, row=[None, _(heading), False])
            for item in items:
                store.append(parent, row=[item, self.mapping[item], True])

        if self.additional:
            parent = store.append(None, row=[None, _("Custom"), False])
            for event_type in self.additional:
                key, value = self.get_key_and_value(event_type)
                store.append(parent, row=[key, value, True])

        return store

    def create_list(self):
        """
        Create a model and fill it with a sorted flat list.
        """
        store = Gtk.ListStore(int, str)
        keys = sorted(self.mapping, key=self.by_value)
        index = 0
        for key in keys:
            if key != self.custom_key:
                store.append(row=[key, self.mapping[key]])
                if key == self.active_key:
                    self.active_index = index
                index += 1

        if self.additional:
            for event_type in self.additional:
                key, value = self.get_key_and_value(event_type)
                store.append(row=[key, value])
                if key == self.active_key:
                    self.active_index = index
                index += 1

        return store

    def by_value(self, val):
        """
        Method for sorting keys based on the values.
        """
        return glocale.sort_key(self.mapping[val])

    def get_values(self):
        """
        Get selected values.

        :returns: Returns (int,str) tuple corresponding to the selection.
        :rtype: tuple
        """
        active_iter = self.selector.get_active_iter()
        if active_iter:
            int_val = self.store.get_value(active_iter, 0)
            str_val = self.store.get_value(active_iter, 1)
            if str_val != self.mapping[int_val]:
                str_val = self.selector.get_child().get_text().strip()
        else:
            int_val = self.custom_key
            str_val = self.selector.get_child().get_text().strip()
        if str_val in iter(self.mapping.values()):
            for key in self.mapping:
                if str_val == self.mapping[key]:
                    int_val = key
                    break
        else:
            int_val = self.custom_key
        return (int_val, str_val)

    def set_values(self, val):
        """
        Set values according to given tuple.

        :param val: (int,str) tuple with the values to set.
        :type val: tuple
        """
        key, text = val
        if key in self.mapping and key != self.custom_key:
            self.store.foreach(self.set_int_value, key)
        elif self.custom_key is not None:
            self.selector.get_child().set_text(text)
        else:
            print("StandardCustomSelector.set(): Option not available:", val)

    def set_int_value(self, model, path, node, val):
        if model.get_value(node, 0) == val:
            self.selector.set_active_iter(node)
            return True
        return False

    def get_key_and_value(self, event_type):
        """
        Return the key and value for the given event type.  The event type may be
        a string representing a custom type, an (int, str) tuple or an EventType
        instance.
        """
        if isinstance(event_type, str):
            return (self.custom_key, event_type)
        elif isinstance(event_type, tuple):
            if event_type[1]:
                return (event_type[0], event_type[1])
        else:
            return (int(event_type), str(event_type))
