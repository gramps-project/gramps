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
import time
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import ToolTips
import GrampsLocale
import DateHandler
import RelLib
from _BaseModel import BaseModel

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

#-------------------------------------------------------------------------
#
# EventModel
#
#-------------------------------------------------------------------------
class EventModel(BaseModel):

    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):
        self.gen_cursor = db.get_event_cursor
        self.map = db.get_raw_event_data
        
        self.fmap = [
            self.column_description,
            self.column_id,
            self.column_type,
            self.column_date,
            self.column_place,
            self.column_change,
            self.column_handle,
            self.column_tooltip,
            ]
        self.smap = [
            self.column_description,
            self.column_id,
            self.column_type,
            self.sort_date,
            self.column_place,
            self.sort_change,
            self.column_handle,
            self.column_tooltip,
            ]
        BaseModel.__init__(self, db, scol, order, tooltip_column=8,
                           search=search, skip=skip, sort_map=sort_map)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_description(self,data):
        return data[COLUMN_DESCRIPTION]

    def column_place(self,data):
        if data[COLUMN_PLACE]:
            return self.db.get_place_from_handle(data[COLUMN_PLACE]).get_title()
        else:
            return u''

    def column_type(self,data):
        return str(RelLib.EventType(data[COLUMN_TYPE]))

    def column_id(self,data):
        return unicode(data[COLUMN_ID])

    def column_date(self,data):
        if data[COLUMN_DATE]:
            event = RelLib.Event()
            event.unserialize(data)
            return DateHandler.get_date(event)
        return u''

    def sort_date(self,data):
        if data[COLUMN_DATE]:
            event = RelLib.Event()
            event.unserialize(data)
            return "%09d" % event.get_date_object().get_sort_value()
        return u''

    def column_handle(self,data):
        return unicode(data[COLUMN_HANDLE])

    def sort_change(self,data):
        return "%012x" % data[COLUMN_CHANGE]

    def column_change(self,data):
        return unicode(time.strftime('%x %X',
                                     time.localtime(data[COLUMN_CHANGE])),
                       GrampsLocale.codeset)

    def column_tooltip(self,data):
        try:
            t = ToolTips.TipFromFunction(
                self.db,
                lambda: self.db.get_event_from_handle(data[COLUMN_HANDLE]))
        except:
            log.error("Failed to create tooltip.", exc_info=True)
        return t
