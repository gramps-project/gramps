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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gi.repository import GObject, GLib

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.lib import Location
from gramps.gen.errors import WindowActiveError
from ...ddtargets import DdTargets
from .locationmodel import LocationModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class LocationEmbedList(EmbeddedList):

    _HANDLE_COL = 6
    _DND_TYPE = DdTargets.LOCATION

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Street'),         0, 150, TEXT_COL, -1, None),
        (_('Locality'),       1, 100, TEXT_COL, -1, None),
        (_('City'),           2, 100, TEXT_COL, -1, None),
        (_('County'),         3, 100, TEXT_COL, -1, None),
        (_('State'),          4, 100, TEXT_COL, -1, None),
        (_('Country'),        5, 75, TEXT_COL, -1, None),
        ]

    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Alternate _Locations'), LocationModel,
                              move_buttons=True)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5))

    def add_button_clicked(self, obj):
        loc = Location()
        try:
            from .. import EditLocation
            EditLocation(self.dbstate, self.uistate, self.track,
                         loc, self.add_callback)
        except WindowActiveError:
            pass

    def add_callback(self, name):
        data = self.get_data()
        data.append(name)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        loc = self.get_selected()
        if loc:
            try:
                from .. import EditLocation
                EditLocation(self.dbstate, self.uistate, self.track,
                             loc, self.edit_callback)
            except WindowActiveError:
                pass

    def edit_callback(self, name):
        self.rebuild()
