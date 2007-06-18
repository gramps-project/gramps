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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Package providing filtering framework for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GTK
#
#-------------------------------------------------------------------------
import gtk
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _GenericFilter import GenericFilter
from Filters import SystemFilters, CustomFilters

#-------------------------------------------------------------------------
#
# FilterStore
#
#-------------------------------------------------------------------------
class FilterStore(gtk.ListStore):

    def __init__(self,local_filters=[], namespace="generic",default=""):
        gtk.ListStore.__init__(self,str)
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

        for filt in SystemFilters.get_filters(namespace) + CustomFilters.get_filters(namespace):
            name = _(filt.get_name())
            self.append(row=[name])
            self.list_map.append(filt)
            if default != "" and default == name:
                self.def_index = cnt
            cnt += 1

    def default_index(self):
        return self.def_index

    def get_filter(self,index):
        return self.list_map[index]
