#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2016       Nick Hall
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

"""
Rule that checks for a family that is a descendant of a specified family.
"""
# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Set
from ....lib import Family
from ....db import Database


_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# IsDescendantOf
#
# -------------------------------------------------------------------------
class IsDescendantOf(Rule):
    """
    Rule that checks for a family that is a descendant of a specified family.
    """

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Descendant families of <family>")
    category = _("General filters")
    description = _("Matches descendant families of the specified family")

    def prepare(self, db: Database, user):
        self.selected_handles: Set[str] = set()
        first = False if int(self.list[1]) else True
        root_family = db.get_family_from_gramps_id(self.list[0])
        self.init_list(db, root_family, first)

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, family: Family) -> bool:
        return family.handle in self.selected_handles

    def init_list(self, db: Database, family: Family | None, first: bool) -> None:
        """
        Initialise family handle list.
        """
        if not family:
            return
        if not first:
            self.selected_handles.add(family.handle)

        for child_ref in family.child_ref_list:
            child = db.get_person_from_handle(child_ref.ref)
            if child:
                for family_handle in child.family_list:
                    child_family = db.get_family_from_handle(family_handle)
                    self.init_list(db, child_family, False)
