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
Tree model for the DNA Matches list view.
"""

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".gui.dnamatchmodel")

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
from .flatbasemodel import FlatBaseModel


# -------------------------------------------------------------------------
#
# DNAMatchModel
#
# -------------------------------------------------------------------------
class DNAMatchModel(FlatBaseModel):
    """
    Flat list model for DNA match objects.

    Column order matches the COL_* constants in DNAMatchView:
      0  Gramps ID
      1  Subject person (via subject_test_handle -> DNATest -> person)
      2  Match account name (via match_test_handle -> DNATest.account_name)
      3  Match person (via match_test_handle -> DNATest -> person)
      4  Shared cM
      5  Largest segment cM
      6  Segment count
      7  Predicted relationship
      8  Predicted generations
      9  Shared ancestors count
     10  Private
     11  Tags
     12  Last changed
     13  Tag color (model-only, not displayed)
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
        self.gen_cursor = db.get_dnamatch_cursor
        self.get_handles = db.get_dnamatch_handles
        self.map = db.get_raw_dnamatch_data
        self.fmap = [
            self.column_id,
            self.column_subject_person,
            self.column_match_account,
            self.column_match_person,
            self.column_shared_cm,
            self.column_largest_seg,
            self.column_seg_count,
            self.column_predicted_rel,
            self.column_pred_gen,
            self.column_shared_ancestors,
            self.column_private,
            self.column_tags,
            self.column_change,
            self.column_tag_color,
        ]
        self.smap = [
            self.column_id,
            self.column_subject_person,
            self.column_match_account,
            self.column_match_person,
            self.sort_shared_cm,
            self.sort_largest_seg,
            self.sort_seg_count,
            self.column_predicted_rel,
            self.sort_pred_gen,
            self.sort_shared_ancestors,
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
        return 13

    def on_get_n_columns(self):
        return len(self.fmap) + 1

    def column_id(self, data):
        return data.gramps_id

    def _get_dnatest_person_name(self, test_handle):
        """
        Return the primary name of the person linked to a DNATest handle.
        """
        if not test_handle:
            return ""
        test = self.db.get_dnatest_from_handle(test_handle)
        if test:
            person_handle = test.get_person_handle()
            if person_handle:
                person = self.db.get_person_from_handle(person_handle)
                if person:
                    return name_displayer.display(person)
        return ""

    def column_subject_person(self, data):
        handle = data.handle
        cached, value = self.get_cached_value(handle, "SUBJ_PERSON")
        if not cached:
            value = self._get_dnatest_person_name(data.subject_test_handle)
            self.set_cached_value(handle, "SUBJ_PERSON", value)
        return value

    def column_match_account(self, data):
        handle = data.handle
        cached, value = self.get_cached_value(handle, "MATCH_ACCOUNT")
        if not cached:
            value = ""
            test_handle = data.match_test_handle
            if test_handle:
                test = self.db.get_dnatest_from_handle(test_handle)
                if test:
                    value = test.get_account_name()
            self.set_cached_value(handle, "MATCH_ACCOUNT", value)
        return value

    def column_match_person(self, data):
        handle = data.handle
        cached, value = self.get_cached_value(handle, "MATCH_PERSON")
        if not cached:
            value = self._get_dnatest_person_name(data.match_test_handle)
            self.set_cached_value(handle, "MATCH_PERSON", value)
        return value

    def _fmt_float(self, val):
        if not val:
            return ""
        return "%.2f" % val

    def column_shared_cm(self, data):
        return self._fmt_float(data.shared_cm)

    def sort_shared_cm(self, data):
        return "%015.4f" % (data.shared_cm or 0.0)

    def column_largest_seg(self, data):
        return self._fmt_float(data.largest_segment_cm)

    def sort_largest_seg(self, data):
        return "%015.4f" % (data.largest_segment_cm or 0.0)

    def column_seg_count(self, data):
        val = data.segment_count
        if not val:
            return ""
        return str(int(val))

    def sort_seg_count(self, data):
        return "%010d" % (int(data.segment_count) if data.segment_count else 0)

    def column_predicted_rel(self, data):
        return data.predicted_relationship or ""

    def column_pred_gen(self, data):
        val = data.predicted_generations
        if val is None:
            return ""
        return "%.1f" % val

    def sort_pred_gen(self, data):
        val = data.predicted_generations
        if val is None:
            return "99999.0"
        return "%010.4f" % val

    def column_shared_ancestors(self, data):
        lst = data.shared_ancestor_list
        if not lst:
            return ""
        return str(len(lst))

    def sort_shared_ancestors(self, data):
        lst = data.shared_ancestor_list
        return "%010d" % (len(lst) if lst else 0)

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
