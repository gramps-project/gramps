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
try:
    set()
except:
    from sets import Set as set

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
import const
import ToolTips
import GrampsLocale
import DateHandler
import RelLib
from _BaseModel import BaseModel

#-------------------------------------------------------------------------
#
# EventModel
#
#-------------------------------------------------------------------------
class EventModel(BaseModel):

    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set()):
        self.gen_cursor = db.get_event_cursor
        self.map = db.get_raw_event_data
        
        self.fmap = [
            self.column_description,
            self.column_id,
            self.column_type,
            self.column_date,
            self.column_place,
            self.column_cause,
            self.column_change,
            self.column_handle,
            self.column_tooltip,
            ]
        self.smap = [
            self.column_description,
            self.column_id,
            self.column_type,
            self.column_date,
            self.column_place,
            self.column_cause,
            self.sort_change,
            self.column_handle,
            self.column_tooltip,
            ]
        BaseModel.__init__(self, db, scol, order, tooltip_column=8,
                           search=search, skip=skip)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_description(self,data):
        return data[4]

    def column_cause(self,data):
        return data[6]

    def column_place(self,data):
        if data[5]:
            return self.db.get_place_from_handle(data[5]).get_title()
        else:
            return u''

    def column_type(self,data):
        return str(RelLib.EventType(data[2]))

    def column_id(self,data):
        return unicode(data[1])

    def column_date(self,data):
        if data[3]:
            event = RelLib.Event()
            event.unserialize(data)
            return DateHandler.get_date(event)
        return u''

    def column_handle(self,data):
        return unicode(data[0])

    def sort_change(self,data):
        return "%012x" % data[10]

    def column_change(self,data):
        return unicode(time.strftime('%x %X',time.localtime(data[10])),
                       GrampsLocale.codeset)

    def column_tooltip(self,data):
        try:
            t = ToolTips.TipFromFunction(self.db, lambda: self.db.get_event_from_handle(data[0]))
        except:
            log.error("Failed to create tooltip.", exc_info=True)
        return t
