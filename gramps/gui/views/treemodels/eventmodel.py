#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2024       Doug Blank
# Copyright (C) 2026       Doug Blank
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

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
from html import escape
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
from gramps.gen.datehandler import format_time, get_date, get_date_valid
from gramps.gen.db.generic import Cursor
from gramps.gen.lib import Event, EventType
from gramps.gen.lib.json_utils import data_to_object
from gramps.gen.utils.db import get_participant_from_event
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.config import config
from .flatbasemodel import FlatBaseModel
from .treebasemodel import TreeBaseModel
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

INVALID_DATE_FORMAT = config.get("preferences.invalid-date-format")


# -------------------------------------------------------------------------
#
# EventBaseModel
#
# -------------------------------------------------------------------------
class EventBaseModel:
    """
    Column definitions shared by the flat (:class:`EventModel`) and
    hierarchical (:class:`EventTreeModel`) event models.
    """

    def __init__(self, db):
        self.gen_cursor = db.get_event_cursor
        self.map = db.get_raw_event_data

        self.fmap = [
            self.column_description,
            self.column_id,
            self.column_type,
            self.column_date,
            self.column_place,
            self.column_private,
            self.column_tags,
            self.column_change,
            self.column_participant,
            self.column_tag_color,
        ]
        self.smap = [
            self.column_description,
            self.column_id,
            self.column_type,
            self.sort_date,
            self.column_place,
            self.column_private,
            self.column_tags,
            self.sort_change,
            self.column_participant,
            self.column_tag_color,
        ]

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.map = None
        self.fmap = None
        self.smap = None

    def color_column(self):
        """
        Return the color column.
        """
        return 9

    def on_get_n_columns(self):
        return len(self.fmap) + 1

    def column_description(self, data):
        return data.description

    def column_participant(self, data):
        handle = data.handle
        cached, value = self.get_cached_value(handle, "PARTICIPANT")
        if not cached:
            value = get_participant_from_event(
                self.db, data.handle, all_=True
            )  # all participants
            self.set_cached_value(handle, "PARTICIPANT", value)
        return value

    def column_place(self, data):
        if data.place:
            cached, value = self.get_cached_value(data.handle, "PLACE")
            if not cached:
                event = data_to_object(data)
                value = place_displayer.display_event(self.db, event)
                self.set_cached_value(data.handle, "PLACE", value)
            return value
        else:
            return ""

    def column_type(self, data):
        return EventType.get_str(data.type)

    def column_id(self, data):
        return data.gramps_id

    def column_date(self, data):
        if data.date:
            event = data_to_object(data)
            date_str = get_date(event)
            if date_str != "":
                retval = escape(date_str)
            else:
                retval = ""
            if not get_date_valid(event):
                return INVALID_DATE_FORMAT % retval
            else:
                return retval
        return ""

    def sort_date(self, data):
        if data.date:
            event = data_to_object(data)
            retval = "%09d" % event.get_date_object().get_sort_key()
            if not get_date_valid(event):
                return INVALID_DATE_FORMAT % retval
            else:
                return retval

        return ""

    def column_private(self, data):
        if data.private:
            return "gramps-lock"
        else:
            # There is a problem returning None here.
            return ""

    def sort_change(self, data):
        return "%012x" % data.change

    def column_change(self, data):
        return format_time(data.change)

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
        tag_handle = data.handle
        cached, tag_color = self.get_cached_value(tag_handle, "TAG_COLOR")
        if not cached:
            tag_color = ""
            tag_priority = None
            for handle in data.tag_list:
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
        tag_list = list(map(self.get_tag_name, data.tag_list))
        # TODO for Arabic, should the next line's comma be translated?
        return ", ".join(sorted(tag_list, key=glocale.sort_key))


# -------------------------------------------------------------------------
#
# EventModel
#
# -------------------------------------------------------------------------
class EventModel(EventBaseModel, FlatBaseModel):
    """
    Flat event model.
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
        EventBaseModel.__init__(self, db)
        FlatBaseModel.__init__(
            self, db, uistate, scol, order, search=search, skip=skip, sort_map=sort_map
        )

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        EventBaseModel.destroy(self)
        FlatBaseModel.destroy(self)


# -------------------------------------------------------------------------
#
# EventTreeModel
#
# -------------------------------------------------------------------------
class EventTreeModel(EventBaseModel, TreeBaseModel):
    """
    Hierarchical event model, showing sub-events under their super-event.

    An event with more than one super-event (``super_event_list``) is
    placed under the first one; the "Part of" tab in the event editor
    remains the authoritative view of every super-event relationship.
    This mirrors how :class:`~.placemodel.PlaceTreeModel` places a Place
    under only the first of its ``placeref_list`` entries.
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
        EventBaseModel.__init__(self, db)
        TreeBaseModel.__init__(
            self,
            db,
            uistate,
            scol=scol,
            order=order,
            search=search,
            skip=skip,
            sort_map=sort_map,
            nrgroups=1,
            group_can_have_handle=True,
        )

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        EventBaseModel.destroy(self)
        TreeBaseModel.destroy(self)

    def _set_base_data(self):
        """See TreeBaseModel; most has been set in EventBaseModel.__init__."""
        self.number_items = self.db.get_number_of_events
        self.gen_cursor = self._get_event_tree_cursor

    def _get_event_tree_cursor(self):
        return Cursor(self._iter_event_tree_data)

    def _iter_event_tree_data(self):
        """
        Yield (handle, data) for every event, parents before children, so
        that TreeBaseModel.add_row can place each event under its primary
        super-event. Events unreachable from a root (e.g. a data-entry
        cycle that slipped past the editor's guard) are yielded last,
        rather than silently dropped.
        """
        all_data = dict(self.db.get_event_cursor())
        children = {}
        roots = []
        for handle, data in all_data.items():
            super_list = data.super_event_list
            parent = super_list[0] if super_list else None
            if parent not in all_data:
                parent = None
            if parent is None:
                roots.append(handle)
            else:
                children.setdefault(parent, []).append(handle)

        visited = set()
        queue = list(roots)
        while queue:
            handle = queue.pop(0)
            if handle in visited:
                continue
            visited.add(handle)
            yield (handle, all_data[handle])
            queue.extend(children.get(handle, []))

        for handle, data in all_data.items():
            if handle not in visited:
                yield (handle, data)

    def get_tree_levels(self):
        """
        Return the headings of the levels in the hierarchy.
        """
        return [_("Event")]

    def add_row(self, handle, data):
        """
        Add a node to the node map for a single event.

        handle      The handle of the gramps object.
        data        The object data.
        """
        sort_key = self.sort_func(data)
        super_list = data.super_event_list
        parent = super_list[0] if super_list else None

        # Add the node as a root node if the parent is not in the tree.
        # This will happen when the view is filtered.
        if not self._get_node(parent):
            parent = None

        self.add_node(parent, handle, sort_key, handle, add_parent=False)
