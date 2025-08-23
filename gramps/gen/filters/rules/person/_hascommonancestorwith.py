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
from ....utils.family_tree_traversal import get_person_ancestors


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Dict, Set
from ....lib import Person
from ....db import Database


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

    def prepare(self, db: Database, user):
        self.db = db
        # For each(!) person we keep track of who their ancestors
        # are, in a set(). So we only have to compute a person's
        # ancestor list once.
        # Start with filling the cache for root person (gramps_id in self.list[0])
        self.ancestor_cache: Dict[str, Set[str]] = {}
        root_person = db.get_person_from_gramps_id(self.list[0])
        if root_person:
            self.add_ancs(db, root_person)
            self.with_people = [root_person.handle]
        else:
            self.with_people = []

    def add_ancs(self, db: Database, person: Person):
        if person and person.handle not in self.ancestor_cache:
            # Use family tree traversal to get all ancestors
            ancestors = get_person_ancestors(
                db=db,
                persons=[person],
                max_depth=None,  # Get all ancestors
                include_root=True,  # Include the person themselves
                use_parallel=True,
                max_threads=4,
            )
            self.ancestor_cache[person.handle] = ancestors

    def reset(self):
        self.ancestor_cache = {}

    def has_common_ancestor(self, other: Person):
        for handle in self.with_people:
            left_and = (
                handle in self.ancestor_cache and self.ancestor_cache[handle]
            )  # type: ignore
            right_and = (
                other
                and other.handle in self.ancestor_cache
                and self.ancestor_cache[other.handle]
            )  # type: ignore
            if left_and.intersection(right_and):  # type: ignore
                return True
        return False

    def apply_to_one(self, db: Database, person: Person) -> bool:
        if person and person.handle not in self.ancestor_cache:
            self.add_ancs(db, person)

        return self.has_common_ancestor(person)
