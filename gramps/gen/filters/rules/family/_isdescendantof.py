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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
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
from ....utils.graph import find_descendants
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
        try:
            inclusive = False if int(self.list[1]) else True
        except IndexError:
            inclusive = True
        root_family = db.get_family_from_gramps_id(self.list[0])
        if root_family:
            # Get all family members (parents and children)
            family_members = []
            if root_family.father_handle:
                family_members.append(root_family.father_handle)
            if root_family.mother_handle:
                family_members.append(root_family.mother_handle)
            for child_ref in root_family.child_ref_list:
                if child_ref.ref:
                    family_members.append(child_ref.ref)

            # Find descendants of all family members
            descendants = find_descendants(db, family_members, inclusive=inclusive)

            # Get all families that contain any of these descendants
            for person_handle in descendants:
                person = db.get_person_from_handle(person_handle)
                if person:
                    for family_handle in person.family_list:
                        self.selected_handles.add(family_handle)

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, family: Family) -> bool:
        return family.handle in self.selected_handles
