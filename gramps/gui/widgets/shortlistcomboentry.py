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

"ShortlistComboEntry class."

__all__ = ["ShortlistComboEntry"]

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".widgets.shortlistcomboentry")

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .validatedcomboentry import ValidatedComboEntry

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

_GTYPE = {
    str: GObject.TYPE_STRING,
    int: GObject.TYPE_INT64,
    float: GObject.TYPE_FLOAT,
}

(
    COLUMN_ITEM,
    COLUMN_IS_SEP,
) = list(range(2))


# -------------------------------------------------------------------------
#
# ShortlistComboEntry class
#
# -------------------------------------------------------------------------
class ShortlistComboEntry(ValidatedComboEntry):
    """A ComboboxEntry class with optional shortlist."""

    __gtype_name__ = "ShortlistComboEntry"

    def __init__(self):
        pass

    def init(self, items, shortlist=True, validator=None):
        if not items:
            raise ValueError

        data_type = items[0].__class__
        gtype = _GTYPE.get(data_type, GObject.TYPE_PYOBJECT)

        # create the model and insert the items
        model = Gtk.ListStore(gtype, GObject.TYPE_BOOLEAN)
        maxlen = -1
        for item in items:
            if len(str(item)) > maxlen:
                maxlen = len(str(item))
            model.append((item, False))

        width = -1  # default width
        if 1 < maxlen < 4:
            width = 4
        elif 1 < maxlen < 10:
            width = maxlen + 1
        ValidatedComboEntry.__init__(
            self, data_type, model, COLUMN_ITEM, validator, width=width
        )
        if shortlist:
            self._shortlist = []
            self.connect("changed", self._on_combobox_changed)

        self.set_row_separator_func(self._is_row_separator, None)

    def _on_combobox_changed(self, combobox):
        if self._internal_change:
            return

        if self.get_active_iter():
            model = self.get_model()

            # if first item on shortlist insert a separator row
            if not self._shortlist:
                model.prepend((None, True))

            # remove the existing shortlist from the model
            iter = model.get_iter_first()
            for n in self._shortlist:
                model.remove(iter)

            # update shortlist
            if self._active_data in self._shortlist:
                self._shortlist.remove(self._active_data)
            self._shortlist.append(self._active_data)
            self._shortlist = self._shortlist[-5:]

            # prepend shortlist to model
            for data in self._shortlist:
                model.prepend((data, False))

    def _is_row_separator(self, model, iter, data=None):
        return model.get_value(iter, COLUMN_IS_SEP)
