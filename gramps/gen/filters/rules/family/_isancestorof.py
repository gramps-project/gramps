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
# MERCHANTABILITY or FITNESS FOR ANY PARTICULAR PURPOSE.  See the
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


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Set, Tuple
from ....lib import Family, Person
from ....db import Database
from ....types import PersonHandle, FamilyHandle


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
        self.selected_handles: Set[FamilyHandle] = set()
        try:
            inclusive = bool(int(self.list[1]))
        except IndexError:
            inclusive = True

        root_family = db.get_family_from_gramps_id(self.list[0])
        if root_family:
            self.init_list(db, root_family, inclusive)

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, family: Family) -> bool:
        return family.handle in self.selected_handles

    def init_list(self, db: Database, family: Family, inclusive: bool) -> None:
        """
        Initialize the list of ancestor families using the new family tree traversal.

        This method follows the original recursive logic:
        1. Start with the root family
        2. For each parent in the family, get their main parents' family
        3. Recursively traverse up the family tree
        """
        if not family:
            return

        # Use a breadth-first search approach similar to the original recursive logic
        from collections import deque

        # Queue of (family_handle, depth) tuples
        work_queue: deque[Tuple[FamilyHandle, int]] = deque()

        # Track visited families to avoid cycles
        visited_families = set()

        # If inclusive is True, start from the root family
        # If inclusive is False, start from the parent families
        if inclusive:
            work_queue.append((family.handle, 0))  # Start with root family at depth 0
        else:
            # Start from parent families at depth 1
            current_family = db.get_family_from_handle(family.handle)
            if current_family:
                for parent_handle in [
                    current_family.get_father_handle(),
                    current_family.get_mother_handle(),
                ]:
                    if parent_handle:
                        parent = db.get_person_from_handle(parent_handle)
                        if parent:
                            parent_family_handle = (
                                parent.get_main_parents_family_handle()
                            )
                            if parent_family_handle:
                                work_queue.append((parent_family_handle, 1))

        while work_queue:
            family_handle, depth = work_queue.popleft()

            if family_handle in visited_families:
                continue

            visited_families.add(family_handle)

            # Add to results (all families in queue are ancestors)
            self.selected_handles.add(family_handle)

            # Get the family and find its parents
            current_family = db.get_family_from_handle(family_handle)
            if current_family:
                # For each parent in the family, get their main parents' family
                for parent_handle in [
                    current_family.get_father_handle(),
                    current_family.get_mother_handle(),
                ]:
                    if parent_handle:
                        parent = db.get_person_from_handle(parent_handle)
                        if parent:
                            # Get the parent's main parents' family (where they are a child)
                            parent_family_handle = (
                                parent.get_main_parents_family_handle()
                            )
                            if (
                                parent_family_handle
                                and parent_family_handle not in visited_families
                            ):
                                work_queue.append((parent_family_handle, depth + 1))
