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
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import Spell
import Errors

from DisplayTabs import log
from _NoteModel import NoteModel
from _EmbeddedList import EmbeddedList
from Editors import EditNote

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------
class NoteTab(EmbeddedList):

    _HANDLE_COL = 2

    _column_names = [
        (_('Type'), 0, 100), 
        (_('Preview'), 1, 200), 
        ]

    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track, 
                              _("Notes"), NoteModel)

    def get_editor(self):
        pass

    def get_user_values(self):
        return []

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1))

    def add_button_clicked(self, obj):
        note = RelLib.Note()
        try:
            EditNote(self.dbstate, self.uistate, [], note)
        except Errors.WindowActiveError:
            pass

    def add_callback(self, name):
        self.get_data().append(name)
        self.changed = True
        self.rebuild()

    def edit_button_clicked(self, obj):
        handle = self.get_selected()
        if handle:
            note = self.dbstate.db.get_note_from_handle(handle)
            try:
                EditNote(self.dbstate, self.uistate, [], note)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self, name):
        self.changed = True
        self.rebuild()
