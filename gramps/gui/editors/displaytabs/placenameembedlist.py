#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2015       Nick Hall
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
from gramps.gen.lib import PlaceName
from gramps.gen.errors import WindowActiveError
from ...ddtargets import DdTargets
from .placenamemodel import PlaceNameModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL

#-------------------------------------------------------------------------
#
# PlaceNameEmbedList
#
#-------------------------------------------------------------------------
class PlaceNameEmbedList(EmbeddedList):

    _HANDLE_COL = 3
    _DND_TYPE = DdTargets.PLACENAME

    _MSG = {
        'add'   : _('Create and add a new place name'),
        'del'   : _('Remove the existing place name'),
        'edit'  : _('Edit the selected place name'),
        'up'    : _('Move the selected place name upwards'),
        'down'  : _('Move the selected place name downwards'),
    }

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Name'), 0, 250, TEXT_COL, -1, None),
        (_('Date'), 1, 250, TEXT_COL, -1, None),
        (_('Language'), 2, 100, TEXT_COL, -1, None),
        ]

    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Alternative Names'), PlaceNameModel,
                              move_buttons=True)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2))

    def add_button_clicked(self, obj):
        """
        Called when the Add button is clicked.
        """
        pname = PlaceName()
        try:
            from .. import EditPlaceName
            EditPlaceName(self.dbstate, self.uistate, self.track,
                          pname, self.add_callback)
        except WindowActiveError:
            return

    def add_callback(self, pname):
        """
        Called to update the screen when a new place name is added.
        """
        data = self.get_data()
        data.append(pname)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        """
        Called with the Edit button is clicked.
        """
        pname = self.get_selected()
        if pname:
            try:
                from .. import EditPlaceName
                EditPlaceName(self.dbstate, self.uistate, self.track,
                              pname, self.edit_callback)
            except WindowActiveError:
                return

    def edit_callback(self, name):
        """
        Called to update the screen when the place name changes.
        """
        self.rebuild()
