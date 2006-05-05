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
from _NameModel import NameModel
from _EmbeddedList import EmbeddedList

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class NameEmbedList(EmbeddedList):

    _HANDLE_COL = 2
    _DND_TYPE   = DdTargets.NAME

    _column_names = [
        (_('Name'), 0, 250), 
        (_('Type'), 1, 100), 
        ]
    
    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track, 
                              _('Names'), NameModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1))

    def add_button_clicked(self, obj):
        name = RelLib.Name()
        try:
            from Editors import EditName
            
            EditName(self.dbstate, self.uistate, self.track, 
                     name, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self, name):
        self.get_data().append(name)
        self.rebuild()

    def edit_button_clicked(self, obj):
        name = self.get_selected()
        if name:
            try:
                from Editors import EditName
                
                EditName(self.dbstate, self.uistate, self.track, 
                         name, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self, name):
        self.rebuild()
