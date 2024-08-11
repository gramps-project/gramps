#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Zsolt Foldvari
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

"The ValidatedComboEntry widget class."

__all__ = ["ValidatedComboEntry"]

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".widgets.validatedcomboentry")

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk


# -------------------------------------------------------------------------
#
# ValidatedComboEntry class
#
# -------------------------------------------------------------------------
class ValidatedComboEntry(Gtk.ComboBox):
    """
    A ComboBoxEntry widget with validation.

    ValidatedComboEntry may have data type other then string, and is set
    with the ``datatype`` contructor parameter.

    Its behaviour is different from Gtk.ComboBoxEntry in the way how
    the entry part of the widget is handled. While Gtk.ComboBoxEntry
    emits the 'changed' signal immediatelly the text in the entry is
    changed, ValidatedComboEntry emits the signal only after the text is
    activated (enter is pressed, the focus is moved out) and validated.

    Validation function is an optional feature and activated only if a
    validator function is given at instantiation.

    The entry can be set as editable or not editable using the
    :meth:`set_entry_editable` method.
    """

    __gtype_name__ = "ValidatedComboEntry"

    def __init__(self, datatype, model=None, column=-1, validator=None, width=-1):
        Gtk.ComboBox.__init__(self)
        self.set_model(model)

        self._entry = Gtk.Entry()
        self._entry.set_width_chars(width)
        # <hack description="set the GTK_ENTRY(self._entry)->is_cell_renderer
        # flag to TRUE in order to tell the entry to fill its allocation.">
        dummy_event = Gdk.Event()
        self._entry.start_editing(dummy_event)
        # </hack>
        self.add(self._entry)
        self._entry.show()

        self._text_renderer = Gtk.CellRendererText()
        self.pack_start(self._text_renderer, False)

        self._data_type = datatype
        self._data_column = -1
        self.set_data_column(column)

        self._active_text = ""
        self._active_data = None
        self.set_active(-1)

        self._validator = validator

        self._entry.connect("activate", self._on_entry_activate)
        self._entry.connect("focus-in-event", self._on_entry_focus_in_event)
        self._entry.connect("focus-out-event", self._on_entry_focus_out_event)
        self._entry.connect("key-press-event", self._on_entry_key_press_event)
        self.connect("changed", self._on_changed)
        self._internal_change = False

        self._has_frame_changed()
        self.connect("notify", self._on_notify)

    # Virtual overriden methods

    def do_mnemonic_activate(self, group_cycling):
        self._entry.grab_focus()
        return True

    def do_grab_focus(self):
        self._entry.grab_focus()

    # Signal handlers

    def _on_entry_activate(self, entry):
        """
        Signal handler.

        Called when the entry is activated.
        """
        self._entry_changed(entry)

    def _on_entry_focus_in_event(self, widget, event):
        """
        Signal handler.

        Called when the focus enters the entry, and is used for saving
        the entry's text for later comparison.
        """
        self._text_on_focus_in = self._entry.get_text()

    def _on_entry_focus_out_event(self, widget, event):
        """
        Signal handler.

        Called when the focus leaves the entry.
        """
        if self._entry.get_text() != self._text_on_focus_in:
            self._entry_changed(widget)

    def _on_entry_key_press_event(self, entry, event):
        """
        Signal handler.

        Its purpose is to handle escape button.
        """
        # FIXME Escape never reaches here, the dialog eats it, I assume.
        if event.keyval == Gdk.KEY_Escape:
            entry.set_text(self._active_text)
            entry.set_position(-1)
            return True

        return False

    def _on_changed(self, combobox):
        """
        Signal handler.

        Called when the active row is changed in the combo box.
        """
        if self._internal_change:
            return

        iter = self.get_active_iter()
        if iter:
            model = self.get_model()
            self._active_data = model.get_value(iter, self._data_column)
            self._active_text = str(self._active_data)
            self._entry.set_text(self._active_text)

    def _on_notify(self, object, gparamspec):
        """
        Signal handler.

        Called whenever a property of the object is changed.
        """
        if gparamspec and gparamspec.name == "has-frame":
            self._has_frame_changed()

    # Private methods

    def _entry_changed(self, entry):
        new_text = entry.get_text()

        try:
            new_data = self._data_type(new_text)

            if (self._validator is not None) and not self._validator(new_data):
                raise ValueError
        except ValueError:
            entry.set_text(self._active_text)
            entry.set_position(-1)
            return

        self._active_text = new_text
        self._active_data = new_data

        self._internal_change = True
        new_iter = self._is_in_model(new_data)
        if new_iter is None:
            if self.get_active_iter() is None:
                # allows response when changing between two non-model values
                self.set_active(0)
            self.set_active(-1)
        else:
            self.set_active_iter(new_iter)
        self._internal_change = False

    def _has_frame_changed(self):
        has_frame = self.get_property("has-frame")
        self._entry.set_has_frame(has_frame)

    def _is_in_model(self, data):
        """
        Check if given data is in the model or not.

        :param data: data value to check
        :type data: depends on the actual data type of the object
        :returns: position of 'data' in the model
        :rtype: Gtk.TreeIter or None
        """
        model = self.get_model()

        iter = model.get_iter_first()
        while iter:
            if model.get_value(iter, self._data_column) == data:
                break
            iter = model.iter_next(iter)

        return iter

    # Public methods

    def set_data_column(self, data_column):
        if data_column < 0:
            return

        model = self.get_model()
        if model is None:
            return

        if data_column > model.get_n_columns():
            return

        if self._data_column == -1:
            self._data_column = data_column
            self.add_attribute(self._text_renderer, "text", data_column)

    def get_data_column(self):
        return self._data_column

    def set_active_data(self, data):
        # set it via entry so that it will be also validated
        if self._entry:
            self._entry.set_text(str(data))
            self._entry_changed(self._entry)

    def get_active_data(self):
        return self._active_data

    def set_entry_editable(self, is_editable):
        self._entry.set_editable(is_editable)
