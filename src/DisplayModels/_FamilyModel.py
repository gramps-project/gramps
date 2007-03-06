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
import const
import ToolTips
import GrampsLocale
from BasicUtils import NameDisplay
import RelLib

from _BaseModel import BaseModel

#-------------------------------------------------------------------------
#
# FamilyModel
#
#-------------------------------------------------------------------------
class FamilyModel(BaseModel):

    _MARKER_COL = 13

    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):
        self.gen_cursor = db.get_family_cursor
        self.map = db.get_raw_family_data
        self.fmap = [
            self.column_id,
            self.column_father,
            self.column_mother,
            self.column_type,
            self.column_change,
            self.column_handle,
            self.column_tooltip,
            self.column_marker_text,
            self.column_marker_color,
            ]
        self.smap = [
            self.column_id,
            self.sort_father,
            self.sort_mother,
            self.column_type,
            self.sort_change,
            self.column_handle,
            self.column_tooltip,
            self.column_marker_text,
            self.column_marker_color,
            ]
        self.marker_color_column = 8
        BaseModel.__init__(self, db, scol, order, tooltip_column=6,
                           search=search, skip=skip, sort_map=sort_map)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self, data):
        return unicode(data[0])

    def column_father(self, data):
        if data[2]:
            person = self.db.get_person_from_handle(data[2])
            return unicode(NameDisplay.displayer.sorted_name(person.primary_name))
        else:
            return u""

    def sort_father(self, data):
        if data[2]:
            person = self.db.get_person_from_handle(data[2])
            return NameDisplay.displayer.sort_string(person.primary_name)
        else:
            return u""

    def column_mother(self, data):
        if data[3]:
            person = self.db.get_person_from_handle(data[3])
            return unicode(NameDisplay.displayer.sorted_name(person.primary_name))
        else:
            return u""

    def sort_mother(self, data):
        if data[3]:
            person = self.db.get_person_from_handle(data[3])
            return NameDisplay.displayer.sort_string(person.primary_name)
        else:
            return u""

    def column_type(self, data):
        return str(RelLib.FamilyRelType(data[5]))

    def column_id(self, data):
        return unicode(data[1])

    def sort_change(self, data):
        return "%012x" % data[13]
    
    def column_change(self, data):
        return unicode(time.strftime('%x %X',time.localtime(data[13])),
                       GrampsLocale.codeset)

    def column_marker_text(self, data):
        try:
            if data[FamilyModel._MARKER_COL]:
                return str(data[FamilyModel._MARKER_COL])
        except IndexError:
            return ""
        return ""

    def column_marker_color(self, data):
        try:
            col = data[FamilyModel._MARKER_COL][0]
            if col == RelLib.MarkerType.COMPLETE:
                return self.complete_color
            elif col == RelLib.MarkerType.TODO_TYPE:
                return self.todo_color
            elif col == RelLib.MarkerType.CUSTOM:
                return self.custom_color
        except IndexError:
            pass
        return None

    def column_tooltip(self,data):
        if const.use_tips:
            try:
                t = ToolTips.TipFromFunction(self.db, lambda:
                                             self.db.get_family_from_handle(data[0]))
            except:
                log.error("Failed to create tooltip.", exc_info=True)
            return t
        else:
            return u''
