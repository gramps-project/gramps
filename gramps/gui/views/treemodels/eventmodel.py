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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import cgi
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
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.datehandler import format_time, get_date, get_date_valid
from gramps.gen.lib import Event, EventType
from gramps.gen.utils.db import get_participant_from_event
from gramps.gen.config import config
from gramps.gen.constfunc import cuni
from .flatbasemodel import FlatBaseModel

#-------------------------------------------------------------------------
#
# COLUMN constants
#
#-------------------------------------------------------------------------
COLUMN_HANDLE      = 0
COLUMN_ID          = 1
COLUMN_TYPE        = 2
COLUMN_DATE        = 3
COLUMN_DESCRIPTION = 4
COLUMN_PLACE       = 5
COLUMN_CHANGE      = 10
COLUMN_PRIV        = 11

INVALID_DATE_FORMAT = config.get('preferences.invalid-date-format')

#-------------------------------------------------------------------------
#
# EventModel
#
#-------------------------------------------------------------------------
class EventModel(FlatBaseModel):

    def __init__(self, db, scol=0, order=Gtk.SortType.ASCENDING, search=None,
                 skip=set(), sort_map=None):
        self.gen_cursor = db.get_event_cursor
        self.map = db.get_raw_event_data
        
        self.fmap = [
            self.column_description,
            self.column_id,
            self.column_type,
            self.column_date,
            self.column_place,
            self.column_private,
            self.column_change,
            self.column_participant,
            self.column_handle,
            self.column_tooltip,
            ]
        self.smap = [
            self.column_description,
            self.column_id,
            self.column_type,
            self.sort_date,
            self.column_place,
            self.column_private,
            self.sort_change,
            self.column_participant,
            self.column_handle,
            self.column_tooltip,
            ]
        FlatBaseModel.__init__(self, db, scol, order, tooltip_column=8,
                           search=search, skip=skip, sort_map=sort_map)

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

    def do_get_n_columns(self):
        return len(self.fmap)+1

    def column_description(self,data):
        return data[COLUMN_DESCRIPTION]

    def column_participant(self,data):
        return get_participant_from_event(self.db, data[COLUMN_HANDLE])
        
    def column_place(self,data):
        if data[COLUMN_PLACE]:
            return self.db.get_place_from_handle(data[COLUMN_PLACE]).get_title()
        else:
            return ''

    def column_type(self,data):
        return cuni(EventType(data[COLUMN_TYPE]))

    def column_id(self,data):
        return cuni(data[COLUMN_ID])

    def column_date(self,data):
        if data[COLUMN_DATE]:
            event = Event()
            event.unserialize(data)
            date_str =  get_date(event)
            if date_str != "":
                retval = cgi.escape(date_str)
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

    def column_handle(self,data):
        return cuni(data[COLUMN_HANDLE])

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

    def column_tooltip(self,data):
        return cuni('Event tooltip')
