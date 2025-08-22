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
from ....utils.family_tree_traversal import FamilyTreeTraversal
from ....types import PersonHandle


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
        # Initialize family tree traversal with configurable settings
        self._traversal = FamilyTreeTraversal(
            use_parallel=True,
            max_threads=4,
        )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[PersonHandle] = set()
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

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles

    def init_list(
        self, root_person: Person, first: bool, max_depth: int | None = None
    ) -> None:
        """
        Optimized descendant traversal using family tree traversal
        with automatic fallback to sequential processing.
        """
        if not root_person:
            return

        # Use family tree traversal for better performance
        if not first:
            # Inclusive mode: include root person and all descendants
            descendant_handles = self._traversal.get_person_descendants(
                db=self.db,
                persons=[root_person],
                max_depth=max_depth,
                include_root=True,
            )
            self.selected_handles.update(descendant_handles)
        else:
            # Exclusive mode: exclude root person, include only descendants
            # Start from root person's children and get all their descendants
            descendant_handles = self._traversal.get_person_descendants(
                db=self.db,
                persons=[root_person],
                max_depth=max_depth,
                include_root=False,
            )
            self.selected_handles.update(descendant_handles)
