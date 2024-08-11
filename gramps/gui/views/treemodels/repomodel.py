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

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".")

# -------------------------------------------------------------------------
#
# GNOME/GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Address, RepositoryType, Url, UrlType
from gramps.gen.datehandler import format_time
from .flatbasemodel import FlatBaseModel
from gramps.gen.const import GRAMPS_LOCALE as glocale


# -------------------------------------------------------------------------
#
# RepositoryModel
#
# -------------------------------------------------------------------------
class RepositoryModel(FlatBaseModel):
    def __init__(
        self,
        db,
        uistate,
        scol=0,
        order=Gtk.SortType.ASCENDING,
        search=None,
        skip=set(),
        sort_map=None,
    ):
        self.gen_cursor = db.get_repository_cursor
        self.get_handles = db.get_repository_handles
        self.map = db.get_raw_repository_data
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_type,
            self.column_home_url,
            self.column_street,
            self.column_locality,
            self.column_city,
            self.column_state,
            self.column_country,
            self.column_postal_code,
            self.column_email,
            self.column_search_url,
            self.column_private,
            self.column_tags,
            self.column_change,
            self.column_tag_color,
        ]

        self.smap = [
            self.column_name,
            self.column_id,
            self.column_type,
            self.column_home_url,
            self.column_street,
            self.column_locality,
            self.column_city,
            self.column_state,
            self.column_country,
            self.column_postal_code,
            self.column_email,
            self.column_search_url,
            self.column_private,
            self.column_tags,
            self.sort_change,
            self.column_tag_color,
        ]

        FlatBaseModel.__init__(
            self, db, uistate, scol, order, search=search, skip=skip, sort_map=sort_map
        )

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.get_handles = None
        self.map = None
        self.fmap = None
        self.smap = None
        FlatBaseModel.destroy(self)

    def color_column(self):
        """
        Return the color column.
        """
        return 15

    def on_get_n_columns(self):
        return len(self.fmap) + 1

    def column_id(self, data):
        return data[1]

    def column_type(self, data):
        return str(RepositoryType(data[2]))

    def column_name(self, data):
        return data[3]

    def column_city(self, data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_city()
        except:
            pass
        return ""

    def column_street(self, data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_street()
        except:
            pass
        return ""

    def column_locality(self, data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_locality()
        except:
            pass
        return ""

    def column_state(self, data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_state()
        except:
            pass
        return ""

    def column_country(self, data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_country()
        except:
            pass
        return ""

    def column_postal_code(self, data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_postal_code()
        except:
            pass
        return ""

    def column_phone(self, data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_phone()
        except:
            pass
        return ""

    def column_email(self, data):
        if data[6]:
            for i in data[6]:
                url = Url()
                url.unserialize(i)
                if url.get_type() == UrlType.EMAIL:
                    return url.path
        return ""

    def column_search_url(self, data):
        if data[6]:
            for i in data[6]:
                url = Url()
                url.unserialize(i)
                if url.get_type() == UrlType.WEB_SEARCH:
                    return url.path
        return ""

    def column_home_url(self, data):
        if data[6]:
            for i in data[6]:
                url = Url()
                url.unserialize(i)
                if url.get_type() == UrlType.WEB_HOME:
                    return url.path
        return ""

    def column_private(self, data):
        if data[9]:
            return "gramps-lock"
        else:
            # There is a problem returning None here.
            return ""

    def sort_change(self, data):
        return "%012x" % data[7]

    def column_change(self, data):
        return format_time(data[7])

    def get_tag_name(self, tag_handle):
        """
        Return the tag name from the given tag handle.
        """
        # TAG_NAME isn't a column, but we cache it
        cached, value = self.get_cached_value(tag_handle, "TAG_NAME")
        if not cached:
            value = self.db.get_tag_from_handle(tag_handle).get_name()
            self.set_cached_value(tag_handle, "TAG_NAME", value)
        return value

    def column_tag_color(self, data):
        """
        Return the tag color.
        """
        tag_handle = data[0]
        cached, tag_color = self.get_cached_value(tag_handle, "TAG_COLOR")
        if not cached:
            tag_color = ""
            tag_priority = None
            for handle in data[8]:
                tag = self.db.get_tag_from_handle(handle)
                this_priority = tag.get_priority()
                if tag_priority is None or this_priority < tag_priority:
                    tag_color = tag.get_color()
                    tag_priority = this_priority
            self.set_cached_value(tag_handle, "TAG_COLOR", tag_color)
        return tag_color

    def column_tags(self, data):
        """
        Return the sorted list of tags.
        """
        tag_list = list(map(self.get_tag_name, data[8]))
        # TODO for Arabic, should the next line's comma be translated?
        return ", ".join(sorted(tag_list, key=glocale.sort_key))
