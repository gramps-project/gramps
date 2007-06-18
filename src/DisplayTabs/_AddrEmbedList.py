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
from _AddressModel import AddressModel
from _EmbeddedList import EmbeddedList

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class AddrEmbedList(EmbeddedList):

    _HANDLE_COL = 5
    _DND_TYPE   = DdTargets.ADDRESS

    _column_names = [
        (_('Date'),    0, 150), 
        (_('Address'), 1, 225), 
        (_('City'),    2, 100), 
        (_('State'),   3, 100), 
        (_('Country'), 4, 75), 
        ]
    
    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track, 
                              _('Addresses'), AddressModel)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2), (1, 3), (1, 4))

    def add_button_clicked(self, obj):
        addr = RelLib.Address()
        try:
            from Editors import EditAddress
            
            EditAddress(self.dbstate, self.uistate, self.track, 
                        addr, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self, name):
        self.get_data().append(name)
        self.rebuild()

    def edit_button_clicked(self, obj):
        addr = self.get_selected()
        if addr:
            try:
                from Editors import EditAddress
                
                EditAddress(self.dbstate, self.uistate, self.track, 
                            addr, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self, name):
        self.rebuild()
