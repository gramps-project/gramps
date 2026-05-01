#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

from .backrefmodel import BackRefModel
from .backreflist import BackRefList


# -------------------------------------------------------------------------
#
# DNATestBackRefList
#
# -------------------------------------------------------------------------
class DNATestBackRefList(BackRefList):
    def __init__(self, dbstate, uistate, track, obj, config_key, callback=None):
        BackRefList.__init__(
            self, dbstate, uistate, track, obj, BackRefModel, config_key, callback
        )

    def get_icon_name(self):
        return "gramps-family"
