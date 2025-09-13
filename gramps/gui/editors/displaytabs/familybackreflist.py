#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       Steve Youngs
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

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from .backrefmodel import BackRefModel
from .backreflist import BackRefList


class FamilyBackRefList(BackRefList):
    def __init__(self, dbstate, uistate, track, obj, config_key, callback=None):
        BackRefList.__init__(
            self,
            dbstate,
            uistate,
            track,
            obj,
            BackRefModel,
            config_key,
            callback=callback,
        )

    def get_icon_name(self):
        return "gramps-relation"
