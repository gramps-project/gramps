#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       B. Malengier
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
# python
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
from pango import WEIGHT_NORMAL, WEIGHT_BOLD
import cgi

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import DateHandler
import config

#-------------------------------------------------------------------------
#
# Globals
#
#-------------------------------------------------------------------------
invalid_date_format = config.get('preferences.invalid-date-format')

#-------------------------------------------------------------------------
#
# EventRefModel
#
#-------------------------------------------------------------------------
class EventRefModel(gtk.TreeStore):
    #index of the working group
    _ROOTINDEX = 0 
    _GROUPSTRING = _('%(groupname)s - %(groupnumber)d')
    
    COL_DESCR = (0, str)
    COL_TYPE = (1, str)
    COL_GID = (2, str)
    COL_DATE = (3, str)
    COL_PLACE = (4, str)
    COL_ROLE = (5, str)
    COL_SORTDATE = (6, str)
    COL_EVENTREF = (7, object)
    COL_FONTWEIGHT = (8, int)
    
    COLS = (COL_DESCR, COL_TYPE, COL_GID, COL_DATE, COL_PLACE, COL_ROLE, 
            COL_SORTDATE, COL_EVENTREF, COL_FONTWEIGHT)

    def __init__(self, event_list, db, groups):
        """
        @param event_list: A list of lists, every entry is a group, the entries
            in a group are the data that needs to be shown subordinate to the 
            group
        @param db: a database objects that can be used to obtain info
        @param groups: a list of (key, name) tuples. key is a key for the group
            that might be used. name is the name for the group.
        """
        typeobjs = (x[1] for x in self.COLS)
        gtk.TreeStore.__init__(self, *typeobjs)
        self.db = db
        self.groups = groups
        for index, group in enumerate(event_list):
            parentiter = self.append(None, row=self.row_group(index, group))
            for eventref in group:
                event = db.get_event_from_handle(eventref.ref)
                self.append(parentiter, row = self.row(index, eventref, event))

    def row_group(self, index, group):
        name = self.namegroup(index, len(group))
        return [name, '', '', '', '', '', '', (index, None), WEIGHT_BOLD]

    def namegroup(self, groupindex, length):
        return self._GROUPSTRING % {'groupname': self.groups[groupindex][1],
                                    'groupnumber': length}

    def row(self, index, eventref, event):
        return [event.get_description(),
                str(event.get_type()),
                event.get_gramps_id(), 
                self.column_date(eventref), 
                self.column_place(eventref), 
                self.column_role(eventref), 
                self.column_sort_date(eventref),
                (index, eventref),
                self.colweight(index),
               ]
    
    def colweight(self, index):
        return WEIGHT_NORMAL

    def column_role(self, event_ref):
        return str(event_ref.get_role())

    def column_date(self, event_ref):
        event = self.db.get_event_from_handle(event_ref.ref)
        retval = DateHandler.get_date(event)
        if not DateHandler.get_date_valid(event):
            return invalid_date_format % cgi.escape(retval)
        else:
            return retval

    def column_sort_date(self, event_ref):
        event = self.db.get_event_from_handle(event_ref.ref)
        date = event.get_date_object()
        if date:
            return "%09d" % date.get_sort_value()
        else:
            return ""

    def column_place(self, event_ref):
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""
