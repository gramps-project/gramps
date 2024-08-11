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
from gramps.gen.datehandler import format_time
from .flatbasemodel import FlatBaseModel
from gramps.gen.const import GRAMPS_LOCALE as glocale


# -------------------------------------------------------------------------
#
# SourceModel
#
# -------------------------------------------------------------------------
class SourceModel(FlatBaseModel):
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
        self.map = db.get_raw_source_data
        self.gen_cursor = db.get_source_cursor
        self.fmap = [
            self.column_title,
            self.column_id,
            self.column_author,
            self.column_abbrev,
            self.column_pubinfo,
            self.column_private,
            self.column_tags,
            self.column_change,
            self.column_tag_color,
        ]
        self.smap = [
            self.column_title,
            self.column_id,
            self.column_author,
            self.column_abbrev,
            self.column_pubinfo,
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
        self.map = None
        self.fmap = None
        self.smap = None
        FlatBaseModel.destroy(self)

    def color_column(self):
        """
        Return the color column.
        """
        return 8

    def on_get_n_columns(self):
        return len(self.fmap) + 1

    def column_title(self, data):
        return data[2].replace("\n", " ")

    def column_author(self, data):
        return data[3]

    def column_abbrev(self, data):
        return data[7]

    def column_id(self, data):
        return data[1]

    def column_pubinfo(self, data):
        return data[4]

    def column_private(self, data):
        if data[12]:
            return "gramps-lock"
        else:
            # There is a problem returning None here.
            return ""

    def column_change(self, data):
        return format_time(data[8])

    def sort_change(self, data):
        return "%012x" % data[8]

    def get_tag_name(self, tag_handle):
        """
        Return the tag name from the given tag handle.
        """
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
        cached, value = self.get_cached_value(tag_handle, "TAG_COLOR")
        if not cached:
            tag_color = ""
            tag_priority = None
            for handle in data[11]:
                tag = self.db.get_tag_from_handle(handle)
                if tag:
                    this_priority = tag.get_priority()
                    if tag_priority is None or this_priority < tag_priority:
                        tag_color = tag.get_color()
                        tag_priority = this_priority
            value = tag_color
            self.set_cached_value(tag_handle, "TAG_COLOR", value)
        return value

    def column_tags(self, data):
        """
        Return the sorted list of tags.
        """
        tag_list = list(map(self.get_tag_name, data[11]))
        # TODO for Arabic, should the next line's comma be translated?
        return ", ".join(sorted(tag_list, key=glocale.sort_key))
