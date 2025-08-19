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
from collections import deque
from typing import Set

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....const import GRAMPS_LOCALE as glocale
from ....utils.parallel import FamilyTreeProcessor

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
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

    def __init__(self, list):
        super().__init__(list)
        # Initialize parallel processor with configurable settings
        self._parallel_processor = FamilyTreeProcessor(
            max_threads=4,
            min_families_for_parallel=3,  # Lower threshold for family processing
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
            root_family = db.get_family_from_gramps_id(self.list[0])
            if root_family:
                self.init_list(db, root_family, first)
        except:
            pass

    def reset(self):
        self.selected_handles.clear()
        self._parallel_processor.clear_caches()

    def apply_to_one(self, db: Database, family: Family) -> bool:
        return family.handle in self.selected_handles

    def init_list(self, db: Database, root_family: Family, first: bool) -> None:
        """
        Optimized descendant family traversal using breadth-first search with caching
        and optional parallel processing for large family trees.
        """
        if not root_family:
            return

        # Use BFS queue instead of recursion
        queue = deque([(root_family, first)])
        visited = set()

        while queue:
            family, is_first = queue.popleft()

            if not family or family.handle in visited:
                continue

            visited.add(family.handle)

            if not is_first:
                self.selected_handles.add(family.handle)

            # Process children and their families
            child_handles = [child_ref.ref for child_ref in family.child_ref_list]
            family_handles = []
            self._parallel_processor.process_child_families(
                db, child_handles, family_handles
            )

            # Add child families to queue
            for family_handle in family_handles:
                if family_handle not in visited:
                    child_family = self._parallel_processor.get_family_cached(
                        db, family_handle
                    )
                    if child_family:
                        queue.append((child_family, False))
