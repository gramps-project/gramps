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
from _LdsEmbedList import LdsEmbedList
import gen.lib

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class FamilyLdsEmbedList(LdsEmbedList):

    _HANDLE_COL = 5
#    _DND_TYPE   = DdTargets.ADDRESS

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Type'),    0, 150, 0, -1), 
        (_('Date'),    1, 150, 1, -1), 
        (_('Status'),  3, 75, 0, -1), 
        (_('Temple'),  2, 200, 0, -1), 
        (_('Place'),   3, 100, 0, -1), 
        ]
    
    def __init__(self, dbstate, uistate, track, data):
        LdsEmbedList.__init__(self, dbstate, uistate, track, data)

    def get_editor(self):
        from Editors import EditFamilyLdsOrd
        return EditFamilyLdsOrd
    
    def new_data(self):
        lds = gen.lib.LdsOrd()
        lds.set_type(gen.lib.LdsOrd.SEAL_TO_SPOUSE)
        return lds
