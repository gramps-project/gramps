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
from ....utils.graph import find_ancestors

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
# HasCommonAncestorWith
#
# -------------------------------------------------------------------------
class HasCommonAncestorWith(Rule):
    """Rule that checks for a person that has a common ancestor with a specified person"""

    labels = [_("ID:")]
    name = _("People with a common ancestor with <person>")
    category = _("Ancestral filters")
    description = _(
        "Matches people that have a common ancestor " "with a specified person"
    )

    def prepare(self, db: Database, user: UserBase) -> None:
        self.db = db
        self.ancestor_cache: dict[PersonHandle, set[PersonHandle]] = {}
        root_person = db.get_person_from_gramps_id(self.list[0])
        if root_person:
            self._get_ancestors(db, root_person.handle)
            self.with_people: list[PersonHandle] = [root_person.handle]
        else:
            self.with_people = []

    def _get_ancestors(self, db: Database, handle: PersonHandle) -> set[PersonHandle]:
        """
        Return the ancestor set for handle, computing and caching it on first access.

        The set includes handle itself (inclusive traversal) so that a person
        is always considered their own ancestor when checking for overlap.
        All parent families are followed to match the behaviour of the
        original recursive implementation.
        """
        if handle not in self.ancestor_cache:
            self.ancestor_cache[handle] = find_ancestors(
                db, [handle], inclusive=True, include_all_parent_families=True
            )
        return self.ancestor_cache[handle]

    def reset(self) -> None:
        """Reset the ancestor cache."""
        self.ancestor_cache = {}

    def has_common_ancestor(self, other: Person) -> bool:
        """Return True if other shares at least one ancestor with any person in with_people."""
        if not other:
            return False
        other_ancs = self.ancestor_cache.get(other.handle, set())
        for handle in self.with_people:
            root_ancs = self.ancestor_cache.get(handle, set())
            if root_ancs & other_ancs:
                return True
        return False

    def apply_to_one(self, db: Database, person: Person) -> bool:
        """Apply the rule to a single person."""
        if person and person.handle not in self.ancestor_cache:
            self._get_ancestors(db, person.handle)
        return self.has_common_ancestor(person)
