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
from gramps.gen.utils.db import dnatest_short_label
from .flatbasemodel import FlatBaseModel

_ = glocale.translation.sgettext


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
      1  Subject test (person name or account name + provider)
      2  Match test (person name or account name + provider)
      3  Shared cM
      4  Weighted shared cM
      5  Largest segment cM
      6  Weighted largest segment cM
      7  Percent shared
      8  Segment count
      9  Predicted relationship, with probability and alternative count
     10  Shared ancestors count
     11  Private
     12  Tags
     13  Last changed
     14  Tag color (model-only, not displayed)
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
            self.column_subject_test,
            self.column_match_test,
            self.column_shared_cm,
            self.column_shared_cm_weighted,
            self.column_largest_seg,
            self.column_largest_seg_weighted,
            self.column_percent_shared,
            self.column_seg_count,
            self.column_predicted_rel,
            self.column_shared_ancestors,
            self.column_private,
            self.column_tags,
            self.column_change,
            self.column_tag_color,
        ]
        self.smap = [
            self.column_id,
            self.column_subject_test,
            self.column_match_test,
            self.sort_shared_cm,
            self.sort_shared_cm_weighted,
            self.sort_largest_seg,
            self.sort_largest_seg_weighted,
            self.sort_percent_shared,
            self.sort_seg_count,
            self.column_predicted_rel,
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
        return 14

    def on_get_n_columns(self):
        return len(self.fmap) + 1

    def column_id(self, data):
        return data.gramps_id

    def column_subject_test(self, data):
        handle = data.handle
        cached, value = self.get_cached_value(handle, "SUBJ_TEST")
        if not cached:
            value = (
                dnatest_short_label(self.db, data.subject_test_handle)
                if data.subject_test_handle
                else ""
            )
            self.set_cached_value(handle, "SUBJ_TEST", value)
        return value

    def column_match_test(self, data):
        handle = data.handle
        cached, value = self.get_cached_value(handle, "MATCH_TEST")
        if not cached:
            value = (
                dnatest_short_label(self.db, data.match_test_handle)
                if data.match_test_handle
                else ""
            )
            self.set_cached_value(handle, "MATCH_TEST", value)
        return value

    def _fmt_float(self, val):
        if not val:
            return ""
        return "%.2f" % val

    def column_shared_cm(self, data):
        return self._fmt_float(data.shared_cm)

    def sort_shared_cm(self, data):
        return "%015.4f" % (data.shared_cm or 0.0)

    def column_shared_cm_weighted(self, data):
        return self._fmt_float(data.shared_cm_weighted)

    def sort_shared_cm_weighted(self, data):
        return "%015.4f" % (data.shared_cm_weighted or 0.0)

    def column_largest_seg(self, data):
        return self._fmt_float(data.largest_segment_cm)

    def sort_largest_seg(self, data):
        return "%015.4f" % (data.largest_segment_cm or 0.0)

    def column_largest_seg_weighted(self, data):
        return self._fmt_float(data.largest_segment_cm_weighted)

    def sort_largest_seg_weighted(self, data):
        return "%015.4f" % (data.largest_segment_cm_weighted or 0.0)

    def column_percent_shared(self, data):
        val = data.percent_shared
        if not val:
            return ""
        return "%g%%" % val

    def sort_percent_shared(self, data):
        return "%015.4f" % (data.percent_shared or 0.0)

    def column_seg_count(self, data):
        val = data.segment_count
        if not val:
            return ""
        return str(int(val))

    def sort_seg_count(self, data):
        return "%010d" % (int(data.segment_count) if data.segment_count else 0)

    def _primary_prediction(self, data):
        """
        Return the prediction the row describes.

        A match may hold several predictions when the relationship is
        uncertain. The most probable one is shown, falling back to the first
        when no prediction carries a probability.
        """
        lst = data.predicted_relationship_list
        if not lst:
            return None
        best = None
        for rel in lst:
            if rel.probability and (best is None or rel.probability > best.probability):
                best = rel
        return best if best is not None else lst[0]

    def column_predicted_rel(self, data):
        rel = self._primary_prediction(data)
        if rel is None:
            return ""
        text = rel.description or _("(unnamed)")
        if rel.probability:
            text += " (%g%%)" % rel.probability
        count = len(data.predicted_relationship_list) - 1
        if count:
            text += " (+%d)" % count
        return text

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
