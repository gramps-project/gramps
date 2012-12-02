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
from gramps.gen.ggettext import gettext as _
from gi.repository import GObject

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
from gramps.gen.lib import Location
from gramps.gen.errors import WindowActiveError
from ...ddtargets import DdTargets
from .locationmodel import LocationModel
from .embeddedlist import EmbeddedList

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class LocationEmbedList(EmbeddedList):

    _HANDLE_COL = 1
    _DND_TYPE   = DdTargets.LOCATION
    
    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Location'),       0, 300, 0, -1), 
        ]
    
    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track, 
                              _('Alternate _Locations'), LocationModel, 
                              move_buttons=True)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0),)

    def add_button_clicked(self, obj):
        loc = Location()
        try:
            from .. import EditLocation
            EditLocation(self.dbstate, self.uistate, self.track, 
                         loc, self.add_callback)
        except WindowActiveError:
            pass

    def add_callback(self, location):
        data = self.get_data()
        data.append(location.handle)
        self.rebuild()
        GObject.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        handle = self.get_selected()
        if handle:
            loc = self.dbstate.db.get_location_from_handle(handle)
            try:
                from .. import EditLocation
                EditLocation(self.dbstate, self.uistate, self.track, 
                             loc, self.edit_callback)
            except WindowActiveError:
                pass

    def edit_callback(self, name):
        self.rebuild()
