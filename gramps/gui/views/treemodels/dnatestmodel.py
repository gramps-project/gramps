#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Tree model for the DNA Tests list view.
"""

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".gui.dnatestmodel")

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
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.lib import DNAProviderType, DNATestType
from .flatbasemodel import FlatBaseModel


# -------------------------------------------------------------------------
#
# DNATestModel
#
# -------------------------------------------------------------------------
class DNATestModel(FlatBaseModel):
    """
    Flat list model for DNA test objects.

    Column order matches the COL_* constants in DNATestView:
      0  Gramps ID
      1  Person
      2  Account name
      3  Provider
      4  Kit ID
      5  Test type
      6  Haplogroup
      7  Private
      8  Tags
      9  Last changed
     10  Tag color (model-only, not displayed)
    """

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
        self.gen_cursor = db.get_dnatest_cursor
        self.get_handles = db.get_dnatest_handles
        self.map = db.get_raw_dnatest_data
        self.fmap = [
            self.column_id,
            self.column_person,
            self.column_account_name,
            self.column_provider,
            self.column_kit_id,
            self.column_test_type,
            self.column_haplogroup,
            self.column_private,
            self.column_tags,
            self.column_change,
            self.column_tag_color,
        ]
        self.smap = [
            self.column_id,
            self.column_person,
            self.column_account_name,
            self.column_provider,
            self.column_kit_id,
            self.column_test_type,
            self.column_haplogroup,
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
        Unset all elements that can prevent garbage collection.
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
        Return the color column index.
        """
        return 10

    def on_get_n_columns(self):
        return len(self.fmap) + 1

    def column_id(self, data):
        return data.gramps_id

    def column_person(self, data):
        handle = data.handle
        cached, value = self.get_cached_value(handle, "PERSON")
        if not cached:
            value = ""
            person_handle = data.person_handle
            if person_handle:
                person = self.db.get_person_from_handle(person_handle)
                if person:
                    value = name_displayer.display(person)
            self.set_cached_value(handle, "PERSON", value)
        return value

    def column_account_name(self, data):
        return data.account_name

    def column_provider(self, data):
        return DNAProviderType.get_str(data.provider)

    def column_kit_id(self, data):
        return data.kit_id

    def column_test_type(self, data):
        return DNATestType.get_str(data.test_type)

    def column_haplogroup(self, data):
        return data.haplogroup

    def column_private(self, data):
        if data.private:
            return "gramps-lock"
        return ""

    def sort_change(self, data):
        return "%012x" % data.change

    def column_change(self, data):
        return format_time(data.change)

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
        tag_handle = data.handle
        cached, tag_color = self.get_cached_value(tag_handle, "TAG_COLOR")
        if not cached:
            tag_color = ""
            tag_priority = None
            for handle in data.tag_list:
                tag = self.db.get_tag_from_handle(handle)
                if tag:
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
        tag_list = list(map(self.get_tag_name, data.tag_list))
        return ", ".join(sorted(tag_list, key=glocale.sort_key))
