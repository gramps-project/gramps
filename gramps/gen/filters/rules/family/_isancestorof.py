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
from typing import Set
from ....lib import Family
from ....db import Database
from ....types import FamilyHandle


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

        This method uses the new family_tree_traversal module to find ancestor families,
        which supports both sequential and parallel processing.
        """
        if not family:
            return

        # Import the family tree traversal module
        from ....utils.family_tree_traversal import get_family_ancestors

        # Use the new family tree traversal to get ancestor families
        # The include_root parameter corresponds to the inclusive parameter
        ancestor_handles = get_family_ancestors(
            db=db,
            families=[family],
            max_depth=None,  # No depth limit for this filter
            include_root=inclusive,
            use_parallel=db.supports_parallel_reads(),
            max_threads=db.get_database_config("parallel", "max_threads"),
        )

        # Convert the set of handles to our selected_handles set
        self.selected_handles = ancestor_handles
