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
from __future__ import annotations
from collections import deque
from typing import Set
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....utils.parallel import FamilyTreeProcessor


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Person
from ....db import Database


# -------------------------------------------------------------------------
#
# IsDescendantOf
#
# -------------------------------------------------------------------------
class IsDescendantOf(Rule):
    """Rule that checks for a person that is a descendant
    of a specified person"""

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Descendants of <person>")
    category = _("Descendant filters")
    description = _("Matches all descendants for the specified person")

    def __init__(self, list):
        super().__init__(list)
        # Initialize parallel processor with configurable settings
        self._parallel_processor = FamilyTreeProcessor(
            max_threads=4,
            min_families_for_parallel=5,
            enable_caching=True,
            cache_size=1000,
        )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[str] = set()
        try:
            first = False if int(self.list[1]) else True
        except IndexError:
            first = True
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            if root_person:
                self.init_list(root_person, first)
        except:
            pass

    def reset(self):
        self.selected_handles.clear()
        self._parallel_processor.clear_caches()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles

    def init_list(self, root_person: Person, first: bool) -> None:
        """
        Optimized descendant traversal using breadth-first search with caching
        and optional parallel processing for large family trees.
        """
        if not root_person:
            return

        # Use BFS queue instead of recursion
        queue = deque([(root_person, first)])
        visited = set()

        while queue:
            person, is_first = queue.popleft()

            if not person or person.handle in visited:
                continue

            visited.add(person.handle)

            if not is_first:
                self.selected_handles.add(person.handle)

            # Batch process family references
            family_handles = list(person.family_list)
            child_handles = []
            self._parallel_processor.process_person_families(
                self.db, family_handles, None, child_handles
            )

            # Add children to queue
            for child_handle in child_handles:
                if child_handle not in visited:
                    child = self._parallel_processor.get_person_cached(
                        self.db, child_handle
                    )
                    if child:
                        queue.append((child, False))
