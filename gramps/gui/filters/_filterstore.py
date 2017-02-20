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

#-------------------------------------------------------------------------
#
# GTK
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.filters import CustomFilters

#-------------------------------------------------------------------------
#
# FilterStore
#
#-------------------------------------------------------------------------
class FilterStore(Gtk.ListStore):

    def __init__(self, local_filters=[], namespace="generic", default=""):
        Gtk.ListStore.__init__(self, str)
        self.list_map = []
        self.def_index = 0

        cnt = 0
        for filt in local_filters:
            name = filt.get_name()
            self.append(row=[name])
            self.list_map.append(filt)
            if default != "" and default == name:
                self.def_index = cnt
            cnt += 1

        for filt in CustomFilters.get_filters(namespace):
            name = _(filt.get_name())
            self.append(row=[name])
            self.list_map.append(filt)
            if default != "" and default == name:
                self.def_index = cnt
            cnt += 1

    def default_index(self):
        return self.def_index

    def get_filter(self, index):
        return self.list_map[index]
