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
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gi.repository import GObject

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
from gramps.gen.lib import PlaceRef
from gramps.gen.errors import WindowActiveError
from ...ddtargets import DdTargets
from .placerefmodel import PlaceRefModel
from .embeddedlist import EmbeddedList, TEXT_COL

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class PlaceRefEmbedList(EmbeddedList):

    _HANDLE_COL = 4
    #_DND_TYPE = DdTargets.PLACEREF
    
    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('ID'),   0, 75, TEXT_COL, -1, None), 
        (_('Name'), 1, 250, TEXT_COL, -1, None), 
        (_('Type'), 2, 100, TEXT_COL, -1, None), 
        (_('Date'), 3, 150, TEXT_COL, -1, None), 
        ]
    
    def __init__(self, dbstate, uistate, track, data, handle):
        self.data = data
        self.handle = handle
        EmbeddedList.__init__(self, dbstate, uistate, track, 
                              _('Parents'), PlaceRefModel, 
                              move_buttons=True)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2), (1, 3))

    def add_button_clicked(self, obj):
        placeref = PlaceRef()
        try:
            from .. import EditPlaceRef
            EditPlaceRef(self.dbstate, self.uistate, self.track, 
                         placeref, self.handle, self.add_callback)
        except WindowActiveError:
            pass

    def add_callback(self, name):
        data = self.get_data()
        data.append(name)
        self.rebuild()
        GObject.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        placeref = self.get_selected()
        if placeref:
            try:
                from .. import EditPlaceRef
                EditPlaceRef(self.dbstate, self.uistate, self.track, 
                             placeref, self.handle, self.edit_callback)
            except WindowActiveError:
                pass

    def edit_callback(self, name):
        self.rebuild()
