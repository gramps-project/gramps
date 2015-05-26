#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2014-2015  Nick Hall
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

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.datehandler import get_date

#-------------------------------------------------------------------------
#
# PlaceNameModel
#
#-------------------------------------------------------------------------
class PlaceNameModel(Gtk.ListStore):

    def __init__(self, obj_list, db):
        Gtk.ListStore.__init__(self, str, str, str, object)
        self.db = db
        for obj in obj_list:
            self.append(row=[obj.get_value(),
                             get_date(obj),
                             obj.get_language(),
                             obj,
                             ])
