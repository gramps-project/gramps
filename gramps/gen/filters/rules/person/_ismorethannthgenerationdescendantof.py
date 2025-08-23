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
from ....utils.family_tree_traversal import get_person_descendants


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Set
from ....lib import Person
from ....db import Database


# -------------------------------------------------------------------------
#
# IsMoreThanNthGenerationDescendantOf
#
# -------------------------------------------------------------------------
class IsMoreThanNthGenerationDescendantOf(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    at least N generations away"""

    labels = [_("ID:"), _("Number of generations:")]
    name = _("Descendants of <person> at least <N> generations away")
    category = _("Descendant filters")
    description = _(
        "Matches people that are descendants of a specified "
        "person at least N generations away"
    )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[str] = set()
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            if root_person:
                min_generations = int(self.list[1])
                # Use family tree traversal to get all descendants
                # Then filter to only include those at least min_generations away
                all_descendants = get_person_descendants(
                    db=db,
                    persons=[root_person],
                    max_depth=None,  # Get all descendants
                    include_root=False,  # Don't include the root person
                    use_parallel=True,
                    max_threads=4,
                )

                # Filter descendants by generation using depth tracking
                self._filter_descendants_by_generation(
                    db, root_person, all_descendants, min_generations
                )
        except (ValueError, IndexError):
            pass

    def _filter_descendants_by_generation(
        self,
        db: Database,
        root_person: Person,
        all_descendants: Set[str],
        min_generations: int,
    ):
        """Filter descendants to only include those at least min_generations away."""
        # Use BFS to determine generation depth for each descendant
        visited = set()
        work_queue = [(root_person.handle, 0)]  # (handle, depth)

        while work_queue:
            handle, depth = work_queue.pop(0)
            if handle in visited:
                continue
            visited.add(handle)

            # Only add to results if it's a descendant and meets generation requirement
            if handle in all_descendants and depth >= min_generations:
                self.selected_handles.add(handle)

            # Continue traversal to next generation
            person = db.get_person_from_handle(handle)
            if person:
                # Get child families
                for family_handle in person.family_list:
                    family = db.get_family_from_handle(family_handle)
                    if family:
                        for child_ref in family.child_ref_list:
                            child_handle = child_ref.ref
                            if child_handle and child_handle not in visited:
                                work_queue.append((child_handle, depth + 1))

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles
