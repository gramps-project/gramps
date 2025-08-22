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
Rule that checks for a family that is an ancestor of a specified family.
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
from ....utils.parallel import get_person_ancestors

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Set
from ....lib import Family
from ....db import Database
from ....types import PersonHandle


_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# IsAncestorOf
#
# -------------------------------------------------------------------------
class IsAncestorOf(Rule):
    """
    Rule that checks for a family that is an ancestor of a specified family.
    """

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Ancestor families of <family>")
    category = _("General filters")
    description = _("Matches ancestor families of the specified family")

    def prepare(self, db: Database, user):
        self.selected_handles: Set[PersonHandle] = set()
        try:
            inclusive = False if int(self.list[1]) else True
        except IndexError:
            inclusive = True

        root_family = db.get_family_from_gramps_id(self.list[0])
        if root_family:
            # Get the parents of the root family
            parents = []
            if root_family.father_handle:
                father = db.get_person_from_handle(root_family.father_handle)
                if father:
                    parents.append(father)
            if root_family.mother_handle:
                mother = db.get_person_from_handle(root_family.mother_handle)
                if mother:
                    parents.append(mother)

            if parents:
                # Use parallel ancestor functionality to get all ancestor persons
                ancestor_person_handles = get_person_ancestors(db, parents)

                # Convert ancestor persons to their parent families
                ancestor_families = set()
                for person_handle in ancestor_person_handles:
                    person = db.get_person_from_handle(PersonHandle(person_handle))
                    if person and person.parent_family_list:
                        # Add the family where this person is a child
                        family_handle = person.parent_family_list[0]
                        ancestor_families.add(family_handle)

                self.selected_handles.update(ancestor_families)

                # Add the root family if inclusive mode
                if inclusive:
                    self.selected_handles.add(root_family.handle)

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, family: Family) -> bool:
        return family.handle in self.selected_handles
