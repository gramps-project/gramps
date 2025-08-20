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
from typing import Set, List

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

    labels = [_("ID:"), _("Inclusive:"), _("Max Depth:")]
    name = _("Descendant families of <family>")
    category = _("General filters")
    description = _("Matches descendant families of the specified family")

    def __init__(self, list):
        super().__init__(list)
        # Initialize parallel processor with configurable settings
        self._parallel_processor = FamilyTreeProcessor(
            max_threads=4,
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
            root_family = db.get_family_from_gramps_id(self.list[0])
            if root_family:
                self.init_list(db, root_family, first, max_depth)
        except:
            pass

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, family: Family) -> bool:
        return family.handle in self.selected_handles

    def init_list(
        self, db: Database, root_family: Family, first: bool, max_depth: int | None
    ) -> None:
        """
        Optimized descendant family traversal using parallel breadth-first search
        with caching and parallel queue processing.
        """
        if not root_family:
            return

        # Use parallel descendant traversal for better performance
        if not first:
            # Get all descendant families using parallel traversal with max_depth
            descendant_handles = self._parallel_processor.get_family_descendants(
                db=db,
                families=[root_family],
                max_depth=max_depth,
            )
            self.selected_handles.update(descendant_handles)
        else:
            # For inclusive mode, we need to process the root family's children
            # and then get their families in parallel
            child_handles = [child_ref.ref for child_ref in root_family.child_ref_list]
            if child_handles:
                # Get family handles for all children in parallel
                family_handles = self._parallel_processor.process_child_families(
                    db, child_handles
                )

                # Use parallel traversal for descendant families with max_depth
                family_objects = [
                    self.db.get_family_from_handle(handle)
                    for handle in family_handles
                    if handle
                ]
                descendant_handles = self._parallel_processor.get_family_descendants(
                    db=db,
                    families=family_objects,
                    max_depth=max_depth,
                )
                self.selected_handles.update(descendant_handles)

    def _get_family_children(self, family: Family) -> List[str]:
        """
        Get child handles from a family for parallel traversal.

        Args:
            family: Family object

        Returns:
            List of child handles
        """
        if not family:
            return []

        # Get child handles
        child_handles = [child_ref.ref for child_ref in family.child_ref_list]

        # Get family handles for these children in parallel
        if child_handles:
            return self._parallel_processor.process_child_families(
                self.db, child_handles
            )

        return []
