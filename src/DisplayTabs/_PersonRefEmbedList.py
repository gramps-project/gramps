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
import RelLib
import Errors
from DdTargets import DdTargets
from _PersonRefModel import PersonRefModel
from _EmbeddedList import EmbeddedList

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class PersonRefEmbedList(EmbeddedList):

    _HANDLE_COL = 3
    _DND_TYPE   = DdTargets.PERSONREF

    _column_names = [
        (_('Name'),    0, 250), 
        (_('ID'),  1, 100), 
        (_('Association'),   2, 100), 
        ]
    
    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track, 
                              _('Associations'), PersonRefModel)

    def get_ref_editor(self):
        from Editors import EditPersonRef
        return EditPersonRef

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2))

    def add_button_clicked(self, obj):
        from Editors import EditPersonRef

        try:
            ref = RelLib.PersonRef()
            ref.rel = _('Godfather')
            EditPersonRef(
                self.dbstate, self.uistate, self.track,
                ref, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self, obj):
        self.get_data().append(obj)
        self.rebuild()

    def edit_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            try:
                from Editors import EditPersonRef
                EditPersonRef(
                    self.dbstate, self.uistate, self.track,
                    ref, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self, obj):
        self.rebuild()

    def _handle_drag(self, row, obj):
        """
        And event reference that is from a drag and drop has
        an unknown event reference type
        """
        try:
            from Editors import EditPersonRef
            ref = RelLib.PersonRef(obj)
            ref.rel = _('Unknown')
            EditPersonRef(
                self.dbstate, self.uistate, self.track,
                ref, self.add_callback)
        except Errors.WindowActiveError:
            pass
