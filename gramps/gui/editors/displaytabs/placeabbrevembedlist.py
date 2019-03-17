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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GLib

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import PlaceAbbrev
from gramps.gen.errors import WindowActiveError
from ..editplaceabbrev import EditPlaceAbbrev
from .placeabbrevmodel import PlaceAbbrevModel
from .embeddedlist import EmbeddedList, TEXT_COL
_ = glocale.translation.gettext


#-------------------------------------------------------------------------
#
# PlaceAbbrevEmbedList
#
#-------------------------------------------------------------------------
class PlaceAbbrevEmbedList(EmbeddedList):

    _HANDLE_COL = 2

    _MSG = {
        'add'   : _('Create and add a new place abbreviation'),
        'del'   : _('Remove the existing place abbreviation'),
        'edit'  : _('Edit the selected place abbreviation'),
        'up'    : _('Move the selected place abbreviation upwards'),
        'down'  : _('Move the selected place abbreviation downwards'),
    }

    #index = column in model. Value =
    #  (abbreviation, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Abbreviation'), 0, 250, TEXT_COL, -1, None),
        (_('Type'), 1, 200, TEXT_COL, -1, None),
    ]

    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Abbreviations'), PlaceAbbrevModel,
                              move_buttons=True)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1))

    def add_button_clicked(self, obj):
        """
        Called when the Add button is clicked.
        """
        pabbrev = PlaceAbbrev()
        try:
            EditPlaceAbbrev(self.dbstate, self.uistate, self.track,
                            pabbrev, self.add_callback)
        except WindowActiveError:
            return

    def add_callback(self, pabbrev):
        """
        Called to update the screen when a new place abbreviation is added.
        """
        data = self.get_data()
        data.append(pabbrev)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        """
        Called with the Edit button is clicked.
        """
        pabbrev = self.get_selected()
        if pabbrev:
            try:
                EditPlaceAbbrev(self.dbstate, self.uistate, self.track,
                                pabbrev, self.edit_callback)
            except WindowActiveError:
                return

    def edit_callback(self, abbreviation):
        """
        Called to update the screen when the place abbreviation changes.
        """
        self.rebuild()
