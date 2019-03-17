#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2015       Nick Hall
# Copyright (C) 2019       Paul Culley
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gi.repository import GLib

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import LocationType
from gramps.gen.errors import WindowActiveError
from ..editlocationtype import EditLocationType
from .placetypemodel import PlaceTypeModel
from .embeddedlist import EmbeddedList, TEXT_COL
_ = glocale.translation.gettext


#-------------------------------------------------------------------------
#
# PlaceTypeEmbedList
#
#-------------------------------------------------------------------------
class PlaceTypeEmbedList(EmbeddedList):

    _HANDLE_COL = 2

    _MSG = {
        'add'   : _('Create and add a new place type'),
        'del'   : _('Remove the existing place type'),
        'edit'  : _('Edit the selected place type'),
        'up'    : _('Move the selected place type upwards'),
        'down'  : _('Move the selected place type downwards'),
    }

    #index = column in model. Value =
    #  (type, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Type'), 0, 250, TEXT_COL, -1, None),
        (_('Date'), 1, 250, TEXT_COL, -1, None),
    ]

    def __init__(self, dbstate, uistate, track, data, update):
        self.data = data
        self.update = update
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Types'), PlaceTypeModel,
                              move_buttons=True)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1))

    def add_button_clicked(self, obj):
        """
        Called when the Add button is clicked.
        """
        ptype = LocationType()
        try:
            EditLocationType(self.dbstate, self.uistate, self.track,
                             ptype, self.add_callback)
        except WindowActiveError:
            return

    def add_callback(self, ptype):
        """
        Called to update the screen when a new place type is added.
        """
        data = self.get_data()
        data.append(ptype)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        """
        Called with the Edit button is clicked.
        """
        ptype = self.get_selected()
        if ptype:
            try:
                EditLocationType(self.dbstate, self.uistate, self.track,
                                 ptype, self.edit_callback)
            except WindowActiveError:
                return

    def edit_callback(self, ptype):
        """
        Called to update the screen when the place type changes.
        """
        self.rebuild()

    def post_rebuild(self, prebuildpath):
        self.update()
