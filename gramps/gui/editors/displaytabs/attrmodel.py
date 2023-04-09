#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"""AttrModel"""

# -------------------------------------------------------------------------
#
# Python libraries
#
# -------------------------------------------------------------------------
from html import escape

# -------------------------------------------------------------------------
#
# GTK libraries
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from gramps.gen.datehandler import get_date, get_date_valid
from gramps.gen.config import config

# -------------------------------------------------------------------------
#
# Globals
#
# -------------------------------------------------------------------------
invalid_date_format = config.get("preferences.invalid-date-format")


# -------------------------------------------------------------------------
#
# AttrModel
#
# -------------------------------------------------------------------------
class AttrModel(Gtk.ListStore):
    """
    Attribute model.
    """

    def __init__(self, attr_list, db):
        Gtk.ListStore.__init__(self, str, str, str, bool, bool, str, object)
        self.db = db
        for attr in attr_list:
            self.append(
                row=[
                    str(attr.get_type()),
                    attr.get_value(),
                    self.column_date(attr),
                    attr.has_citations(),
                    attr.get_privacy(),
                    self.column_sort_date(attr),
                    attr,
                ]
            )

    def column_date(self, attr):
        """
        Return rendered column date.
        """
        retval = get_date(attr)
        if not get_date_valid(attr):
            return invalid_date_format % escape(retval)
        return retval

    def column_sort_date(self, attr):
        """
        Return date in sortable format.
        """
        date = attr.get_date_object()
        if date:
            return "%09d" % date.get_sort_value()
        return ""
