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
from ....utils.family_tree_traversal import get_person_ancestors_with_min_depth


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Set
from ....lib import Person
from ....db import Database
from ....types import PersonHandle


# -------------------------------------------------------------------------
#
# IsMoreThanNthGenerationAncestorOf
#
# -------------------------------------------------------------------------
class IsMoreThanNthGenerationAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person
    at least N generations away"""

    labels = [_("ID:"), _("Number of generations:")]
    name = _("Ancestors of <person> at least <N> generations away")
    category = _("Ancestral filters")
    description = _(
        "Matches people that are ancestors "
        "of a specified person at least N generations away"
    )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[PersonHandle] = set()
        person = db.get_person_from_gramps_id(self.list[0])
        if person:
            try:
                min_generations = int(self.list[1])
                # Use standardized family tree traversal to find ancestors
                # beyond the specified generation depth
                self.selected_handles = get_person_ancestors_with_min_depth(
                    db=self.db,
                    persons=[person],
                    min_depth=min_generations
                    + 1,  # +1 because we want ancestors MORE than N generations away
                    max_depth=None,  # No maximum depth limit
                    include_root=False,  # Don't include the root person
                )
            except (ValueError, IndexError):
                pass

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db, person: Person) -> bool:
        return person.handle in self.selected_handles
