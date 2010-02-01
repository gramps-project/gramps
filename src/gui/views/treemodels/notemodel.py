#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
_LOG = logging.getLogger(".gui.notemodel")

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
from gui.views.treemodels.flatbasemodel import FlatBaseModel
from gen.lib import (Note, NoteType, MarkerType, StyledText)

#-------------------------------------------------------------------------
#
# NoteModel
#
#-------------------------------------------------------------------------
class NoteModel(FlatBaseModel):
    """
    """
    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):
        """Setup initial values for instance variables."""
        self.gen_cursor = db.get_note_cursor
        self.map = db.get_raw_note_data
        self.fmap = [
            self.column_preview,
            self.column_id,
            self.column_type,
            self.column_marker,
            self.column_change,
            self.column_handle,
            self.column_marker_color
        ]
        self.smap = [
            self.column_preview,
            self.column_id,
            self.column_type,
            self.column_marker,
            self.column_change,
            self.column_handle,
            self.column_marker_color
        ]
        self.marker_color_column = 6
        FlatBaseModel.__init__(self, db, scol, order, search=search,
                           skip=skip, sort_map=sort_map)

    def on_get_n_columns(self):
        """Return the column number of the Note tab."""
        return len(self.fmap) + 1

    def column_handle(self, data):
        """Return the handle of the Note."""
        return data[Note.POS_HANDLE]

    def column_id(self, data):
        """Return the id of the Note."""
        return unicode(data[Note.POS_ID])

    def column_type(self, data):
        """Return the type of the Note in readable format."""
        temp = NoteType()
        temp.set(data[Note.POS_TYPE])
        return unicode(str(temp))

    def column_marker(self, data):
        """Return the marker type of the Note in readable format."""
        temp = MarkerType()
        temp.set(data[Note.POS_MARKER])
        return unicode(str(temp))
    
    def column_preview(self, data):
        """Return a shortend version of the Note's text."""
        #data is the encoding in the database, make it a unicode object
        #for universal work
        note = unicode(data[Note.POS_TEXT][StyledText.POS_TEXT])
        note = " ".join(note.split())
        if len(note) > 80:
            return note[:80] + "..."
        else:
            return note

    def column_marker_color(self, data):
        """Return the color of the Note's marker type if exist."""
        try:
            col = data[Note.POS_MARKER][MarkerType.POS_VALUE]
            if col == MarkerType.COMPLETE:
                return self.complete_color
            elif col == MarkerType.TODO_TYPE:
                return self.todo_color
            elif col == MarkerType.CUSTOM:
                return self.custom_color
            else:
                return None
        except IndexError:
            return None

    def column_change(self,data):
        return unicode(time.strftime('%x %X',time.localtime(
                            data[Note.POS_CHANGE])), GrampsLocale.codeset)
