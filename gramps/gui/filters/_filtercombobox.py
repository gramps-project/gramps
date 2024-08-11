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
Package providing filtering framework for Gramps.
"""

# -------------------------------------------------------------------------
#
# GTK
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.filters import CustomFilters


# -------------------------------------------------------------------------
#
# FilterComboBox
#
# -------------------------------------------------------------------------
class FilterComboBox(Gtk.ComboBox):
    def set(self, local_filters, default=""):
        self.store = Gtk.ListStore(GObject.TYPE_STRING)
        self.set_model(self.store)
        cell = Gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, "text", 0)

        self.map = {}

        active = 0
        cnt = 0
        for filt in local_filters:
            self.store.append(row=[filt.get_name()])
            self.map[str(filt.get_name())] = filt
            if default != "" and default == filt.get_name():
                active = cnt
            cnt += 1

        # for filt in SystemFilters.get_filters():
        # self.store.append(row=[filt.get_name()])
        # self.map[unicode(filt.get_name())] = filt
        # if default != "" and default == filt.get_name():
        # active = cnt
        # cnt += 1

        for filt in CustomFilters.get_filters():
            self.store.append(row=[filt.get_name()])
            self.map[str(filt.get_name())] = filt
            if default != "" and default == filt.get_name():
                active = cnt
            cnt += 1

        if active:
            self.set_active(active)
        elif len(local_filters):
            self.set_active(2)
        # elif len(SystemFilters.get_filters()):
        # self.set_active(4 + len(local_filters))
        elif len(CustomFilters.get_filters()):
            self.set_active(4 + len(local_filters))
        else:
            self.set_active(0)

    def get_value(self):
        active = self.get_active()
        if active < 0:
            return None
        key = str(self.store[active][0])
        return self.map[key]
