#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2010       Raphael Ackermann
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
# Standard Python modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from . import Rule


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Set
from ...types import PrimaryObjectHandle, PrimaryObject
from ...db import Database


# -------------------------------------------------------------------------
#
# HasIdOf
#
# -------------------------------------------------------------------------
class HasGrampsId(Rule):
    """Rule that checks for an object with a specific Gramps ID."""

    labels = [_("ID:")]
    name = "Object with <Id>"
    description = "Matches objects with a specified Gramps ID"
    category = _("General filters")
    selected_handles: Set[PrimaryObjectHandle] = set([])

    def apply_to_one(self, db: Database, obj: PrimaryObject) -> bool:
        """
        apply the rule on the obj.
        return true if the rule passes, false otherwise.
        """
        return obj.handle in self.selected_handles

    def reset(self):
        self.selected_handles.clear()
