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

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from html import escape
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.datehandler import format_time, get_date, get_date_valid
from gramps.gen.lib import Event, EventType
from gramps.gen.utils.db import get_participant_from_event
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.config import config
from .flatbasemodel import FlatBaseModel
from gramps.gen.const import GRAMPS_LOCALE as glocale

#-------------------------------------------------------------------------
#
# Positions in raw data structure
#
#-------------------------------------------------------------------------
COLUMN_HANDLE = 0
COLUMN_ID = 1
COLUMN_TYPE = 2
COLUMN_DATE = 3
COLUMN_DESCRIPTION = 4
COLUMN_PLACE = 5
COLUMN_CHANGE = 10
COLUMN_TAGS = 11
COLUMN_PRIV = 12

INVALID_DATE_FORMAT = config.get('preferences.invalid-date-format')

#-------------------------------------------------------------------------
#
# EventModel
#
#-------------------------------------------------------------------------
class EventModel(FlatBaseModel):

    def __init__(self, db, uistate, scol=0, order=Gtk.SortType.ASCENDING,
                 search=None, skip=set(), sort_map=None):
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
            self.column_tag_color
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
            self.column_tag_color
           ]
        FlatBaseModel.__init__(self, db, uistate, scol, order, search=search,
                               skip=skip, sort_map=sort_map)

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
        return 9

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_description(self,data):
        return data[COLUMN_DESCRIPTION]

    def column_participant(self,data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "PARTICIPANT")
        if not cached:
            value = get_participant_from_event(self.db, data[COLUMN_HANDLE],
                                               all_=True) # all participants
            self.set_cached_value(handle, "PARTICIPANT", value)
        return value

    def column_place(self,data):
        if data[COLUMN_PLACE]:
            cached, value = self.get_cached_value(data[0], "PLACE")
            if not cached:
                event = Event()
                event.unserialize(data)
                value = place_displayer.display_event(self.db, event)
                self.set_cached_value(data[0], "PLACE", value)
            return value
        else:
            return ''

    def column_type(self,data):
        return str(EventType(data[COLUMN_TYPE]))

    def column_id(self,data):
        return data[COLUMN_ID]

    def column_date(self,data):
        if data[COLUMN_DATE]:
            event = Event()
            event.unserialize(data)
            date_str = get_date(event)
            if date_str != "":
                retval = escape(date_str)
            if not get_date_valid(event):
                return INVALID_DATE_FORMAT % retval
            else:
                return retval
        return ''

    def sort_date(self,data):
        if data[COLUMN_DATE]:
            event = Event()
            event.unserialize(data)
            retval = "%09d" % event.get_date_object().get_sort_value()
            if not get_date_valid(event):
                return INVALID_DATE_FORMAT % retval
            else:
                return retval

        return ''

    def column_private(self, data):
        if data[COLUMN_PRIV]:
            return 'gramps-lock'
        else:
            # There is a problem returning None here.
            return ''

    def sort_change(self,data):
        return "%012x" % data[COLUMN_CHANGE]

    def column_change(self,data):
        return format_time(data[COLUMN_CHANGE])

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
            for handle in data[COLUMN_TAGS]:
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
        tag_list = list(map(self.get_tag_name, data[COLUMN_TAGS]))
        # TODO for Arabic, should the next line's comma be translated?
        return ', '.join(sorted(tag_list, key=glocale.sort_key))
