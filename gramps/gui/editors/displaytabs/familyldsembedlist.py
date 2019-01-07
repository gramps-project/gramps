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

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from .embeddedlist import TEXT_COL, MARKUP_COL, ICON_COL
from .ldsembedlist import LdsEmbedList
from gramps.gen.lib import LdsOrd

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class FamilyLdsEmbedList(LdsEmbedList):

    _HANDLE_COL = 6
#    _DND_TYPE = DdTargets.ADDRESS

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Type'),    0, 150, TEXT_COL, -1, None),
        (_('Date'),    1, 150, MARKUP_COL, -1, None),
        (_('Status'),  3, 75, TEXT_COL, -1, None),
        (_('Temple'),  2, 200, TEXT_COL, -1, None),
        (_('Place'),   3, 100, TEXT_COL, -1, None),
        (_('Private'), 5,  30, ICON_COL, -1, 'gramps-lock')
        ]

    def __init__(self, dbstate, uistate, track, data):
        LdsEmbedList.__init__(self, dbstate, uistate, track, data)

    def get_editor(self):
        from .. import EditFamilyLdsOrd
        return EditFamilyLdsOrd

    def new_data(self):
        lds = LdsOrd()
        lds.set_type(LdsOrd.SEAL_TO_SPOUSE)
        return lds
