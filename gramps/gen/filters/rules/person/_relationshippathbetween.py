#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
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
from ....utils.graph import find_ancestors_iterative, find_descendants

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Person
from ....db import Database
from ....types import PersonHandle
from ....user import UserBase


# -------------------------------------------------------------------------
#
# RelationshipPathBetween
#
# -------------------------------------------------------------------------
class RelationshipPathBetween(Rule):
    """Rule that matches ancestors of two persons back to their common ancestor."""

    labels = [_("ID:"), _("ID:")]
    name = _("Relationship path between <persons>")
    category = _("Relationship filters")
    description = _(
        "Matches the ancestors of two persons back "
        "to a common ancestor, producing the relationship "
        "path between two persons."
    )

    def prepare(self, db: Database, user: UserBase) -> None:
        self.db = db
        self.selected_handles: set[PersonHandle] = set()
        root1 = db.get_person_from_gramps_id(self.list[0])
        root2 = db.get_person_from_gramps_id(self.list[1])
        if root1 and root2:
            self._init_list(db, root1.handle, root2.handle)

    def reset(self) -> None:
        """Clear the selected handle set."""
        self.selected_handles.clear()

    def _init_list(
        self, db: Database, p1_handle: PersonHandle, p2_handle: PersonHandle
    ) -> None:
        """Populate selected_handles with all persons on the path between p1 and p2."""
        first_map: dict[PersonHandle, int] = {}
        second_map: dict[PersonHandle, int] = {}

        for handle, gen in find_ancestors_iterative(
            db, [p1_handle], inclusive=True, include_all_parent_families=False
        ):
            first_map[handle] = gen

        for handle, gen in find_ancestors_iterative(
            db, [p2_handle], inclusive=True, include_all_parent_families=False
        ):
            second_map[handle] = gen

        first_set = set(first_map)
        second_set = set(second_map)

        common: list[PersonHandle] = []
        rank = 9999999
        for person_handle in first_set & second_set:
            new_rank = first_map[person_handle]
            if new_rank < rank:
                rank = new_rank
                common = [person_handle]
            elif new_rank == rank:
                common.append(person_handle)

        path1: set[PersonHandle] = {p1_handle}
        path2: set[PersonHandle] = {p2_handle}
        for person_handle in common:
            desc = find_descendants(
                db, [person_handle], inclusive=False, include_all_families=True
            )
            path1.update(desc & first_set)
            path2.update(desc & second_set)

        self.selected_handles.update(path1, path2, common)

    def apply_to_one(self, db: Database, person: Person) -> bool:
        """Return True if this person is on the relationship path."""
        return person.handle in self.selected_handles
