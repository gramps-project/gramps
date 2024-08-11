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

__all__ = ["MenuItemWithData", "add_menuitem"]

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".widgets.menuitem")

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# MenuItemWithData class
#
# -------------------------------------------------------------------------


class MenuItemWithData(Gtk.MenuItem):
    """A MenuItem that stores a data property. As set_data in GTK3 is not
    working, this is a workaround to have set_data"""

    data = GObject.Property(type=object)

    def __init__(self, label=""):
        Gtk.MenuItem.__init__(self, label=label)

    def set_data(self, data):
        self.data = data

    def get_data(self, _=None):
        """obtain the data, for backward compat, we allow a dummy argument"""
        return self.data


def add_menuitem(menu, msg, obj, func):
    """
    add a menuitem to menu with label msg, which activates func, and has data
    obj
    """
    item = MenuItemWithData(label=msg)
    item.set_data(obj)
    item.connect("activate", func)
    item.show()
    menu.append(item)
