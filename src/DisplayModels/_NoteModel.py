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
import logging
import re
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
from _BaseModel import BaseModel
import gen.lib

#-------------------------------------------------------------------------
#
# PlaceModel
#
#-------------------------------------------------------------------------
class NoteModel(BaseModel):

    HANDLE_COL = 4
    _MARKER_COL = 6

    def __init__(self,db,scol=0, order=gtk.SORT_ASCENDING,search=None,
                 skip=set(), sort_map=None):
        self.gen_cursor = db.get_note_cursor
        self.map = db.get_raw_note_data
        self.fmap = [
            self.column_preview,
            self.column_id,
            self.column_type,
            self.column_marker,
            self.column_handle,
            self.column_marker_color
            ]
        self.smap = [
            self.column_preview,
            self.column_id,
            self.column_type,
            self.column_marker,
            self.column_handle,
            self.column_marker_color
            ]
        self.marker_color_column = 5
        BaseModel.__init__(self, db, scol, order,
                           search=search, skip=skip, sort_map=sort_map)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self,data):
        return data[0]

    def column_id(self,data):
        return unicode(data[1])

    def column_type(self,data):
        temp = gen.lib.NoteType()
        temp.set(data[4])
        return unicode(str(temp))

    def column_marker(self, data):
        temp = gen.lib.MarkerType()
        temp.set(data[6])
        return unicode(str(temp))
    
    def column_preview(self,data):
        #data is the encoding in the database, make it a unicode object
        #for universal work
        note = " ".join(unicode(data[2]).split())
        if len(note) > 80:
            return note[:80]+"..."
        else:
            return note

    def column_marker_color(self, data):
        try:
            col = data[NoteModel._MARKER_COL][0]
            if col == gen.lib.MarkerType.COMPLETE:
                return self.complete_color
            elif col == gen.lib.MarkerType.TODO_TYPE:
                return self.todo_color
            elif col == gen.lib.MarkerType.CUSTOM:
                return self.custom_color
        except IndexError:
            pass
        return None
