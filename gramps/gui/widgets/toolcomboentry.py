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

"ToolComboEntry class."

__all__ = ["ToolComboEntry"]

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.toolcomboentry")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
#from gi.repository import GObject
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .valuetoolitem import ValueToolItem
from .shortlistcomboentry import ShortlistComboEntry

#-------------------------------------------------------------------------
#
# ToolComboEntry class
#
#-------------------------------------------------------------------------
class ToolComboEntry(ValueToolItem):
    """Tool bar item containing a ShortlistComboEntry widget."""
    __gtype_name__ = "ToolComboEntry"

    def _create_widget(self, items, editable, shortlist=True, validator=None):
        self.set_border_width(2)
        self.set_homogeneous(False)
        self.set_expand(False)

        combo = ShortlistComboEntry(items, shortlist, validator)
        if (Gtk.MAJOR_VERSION, Gtk.MINOR_VERSION) < (3, 20):
            combo.set_focus_on_click(False)
        else:
            Gtk.Widget.set_focus_on_click(combo, False)
        combo.set_entry_editable(editable)
        combo.show()
        self.add(combo)

        combo.connect('changed', self._on_widget_changed)

    def set_value(self, value):
        self.get_child().set_active_data(value)

    def get_value(self):
        return self.get_child().get_active_data()
