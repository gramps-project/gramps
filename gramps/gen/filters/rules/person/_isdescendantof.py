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
from typing import Set, List
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

    labels = [_("ID:"), _("Inclusive:"), _("Max Depth:")]
    name = _("Descendants of <person>")
    category = _("Descendant filters")
    description = _("Matches all descendants for the specified person")

    def __init__(self, list):
        super().__init__(list)
        # Initialize parallel processor with configurable settings
        self._parallel_processor = FamilyTreeProcessor(
            max_threads=4,
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
            max_depth = (
                int(self.list[2]) if len(self.list) > 2 and self.list[2] else None
            )
        except (IndexError, ValueError):
            max_depth = None
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            if root_person:
                self.init_list(root_person, first, max_depth)
        except:
            pass

    def reset(self):
        self.selected_handles.clear()
        self._parallel_processor.clear_caches()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles

    def init_list(
        self, root_person: Person, first: bool, max_depth: int | None = None
    ) -> None:
        """
        Optimized descendant traversal using parallel breadth-first search
        with caching and parallel queue processing.
        """
        if not root_person:
            return

        # Use parallel descendant traversal for better performance
        if not first:
            # Get all descendants using parallel traversal with max_depth
            descendant_handles = self._parallel_processor.get_person_descendants(
                db=self.db,
                persons=[root_person],
                max_depth=max_depth,
            )
            self.selected_handles.update(descendant_handles)
        else:
            # For inclusive mode, we need to process the root person's children
            # and then get their descendants in parallel
            child_handles = self._get_person_children(root_person)
            if child_handles:
                # Use parallel traversal for descendant persons with max_depth
                child_persons = [
                    self._parallel_processor.get_person_cached(self.db, handle)
                    for handle in child_handles
                    if handle
                ]
                descendant_handles = self._parallel_processor.get_person_descendants(
                    db=self.db,
                    persons=child_persons,
                    max_depth=max_depth,
                )
                self.selected_handles.update(descendant_handles)

    def _get_person_children(self, person: Person) -> List[str]:
        """
        Get child handles from a person for parallel traversal.

        Args:
            person: Person object

        Returns:
            List of child handles
        """
        if not person:
            return []

        # Get family handles for this person
        family_handles = list(person.family_list)

        # Get child handles from all families in parallel
        if family_handles:
            return self._parallel_processor.process_person_families(
                self.db, family_handles
            )

        return []
