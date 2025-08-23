#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....utils.family_tree_traversal import create_family_tree_traversal


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Set
from ....lib import Person
from ....db import Database
from ....types import PersonHandle


# -------------------------------------------------------------------------
#
# IsMoreThanNthGenerationAncestorOf
#
# -------------------------------------------------------------------------
class IsMoreThanNthGenerationAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person
    at least N generations away"""

    labels = [_("ID:"), _("Number of generations:")]
    name = _("Ancestors of <person> at least <N> generations away")
    category = _("Ancestral filters")
    description = _(
        "Matches people that are ancestors "
        "of a specified person at least N generations away"
    )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[PersonHandle] = set()
        person = db.get_person_from_gramps_id(self.list[0])
        if person:
            try:
                min_generations = int(self.list[1])
                # Use family tree traversal functionality with unlimited depth,
                # then filter by generation
                traversal = create_family_tree_traversal()
                all_ancestors = traversal.get_person_ancestors(db, [person])

                # Filter ancestors by generation using the traversal module's depth tracking
                self._filter_ancestors_by_generation(
                    db, person, all_ancestors, min_generations
                )
            except (ValueError, IndexError):
                pass

    def _filter_ancestors_by_generation(
        self,
        db: Database,
        root_person: Person,
        all_ancestors: Set[str],
        min_generations: int,
    ):
        """Filter ancestors to only include those at least min_generations away."""
        # Use family tree traversal with depth tracking to determine generation depth
        from ....utils.family_tree_traversal import FamilyTreeTraversal

        traversal = FamilyTreeTraversal(use_parallel=True, max_threads=4)

        # Get all ancestors with depth information
        # We'll use a custom approach to track depths
        # Note: In the original implementation, generation 1 was the root person
        # So ancestors at least N generations away should have depth >= N
        visited = set()
        work_queue = [
            (root_person.handle, 1)
        ]  # (handle, generation) - generation 1 is root
        generation_map = {}

        while work_queue:
            handle, gen = work_queue.pop(0)
            if handle in visited:
                continue
            visited.add(handle)
            generation_map[handle] = gen

            # Only add to results if it's an ancestor and meets generation requirement
            # Original logic: gen > min_generations means at least min_generations away
            if handle in all_ancestors and gen > min_generations:
                self.selected_handles.add(handle)

            # Continue traversal to next generation
            person = db.get_person_from_handle(handle)
            if person:
                # Get parent families
                for family_handle in person.parent_family_list:
                    family = db.get_family_from_handle(family_handle)
                    if family:
                        for parent_handle in [
                            family.father_handle,
                            family.mother_handle,
                        ]:
                            if parent_handle and parent_handle not in visited:
                                work_queue.append((parent_handle, gen + 1))

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db, person: Person) -> bool:
        return person.handle in self.selected_handles
