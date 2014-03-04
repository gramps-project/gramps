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
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.errors import WindowActiveError
from .altnamemodel import AltNameModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL

#-------------------------------------------------------------------------
#
# AltNameEmbedList
#
#-------------------------------------------------------------------------
class AltNameEmbedList(EmbeddedList):

    _HANDLE_COL = 0

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Place Name'), 0, 250, TEXT_COL, -1, None),
        ]

    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Alternative Names'), AltNameModel,
                              move_buttons=True)

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0),)

    def add_button_clicked(self, obj):
        try:
            from .. import EditPlaceName
            EditPlaceName(self.dbstate, self.uistate, self.track,
                          self.get_data(), -1, self.add_callback)
        except WindowActiveError:
            pass

    def add_callback(self, place_name):
        data = self.get_data()
        self.rebuild()
        GObject.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        place_name = self.get_selected()
        if place_name:
            try:
                from .. import EditPlaceName
                data = self.get_data()
                EditPlaceName(self.dbstate, self.uistate, self.track,
                              data, data.index(place_name), self.edit_callback)
            except WindowActiveError:
                pass

    def edit_callback(self, place_name):
        self.rebuild()
