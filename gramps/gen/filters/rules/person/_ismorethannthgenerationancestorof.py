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
from ....utils.graph import find_ancestors


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
        """Use the unified find_ancestors function"""
        self.db = db
        self.selected_handles: Set[PersonHandle] = set()
        person = db.get_person_from_gramps_id(self.list[0])
        if person:
            # Original uses base-1: gen 1=root, 2=parents, 3=grandparents
            # Our function uses base-0: gen 0=root, 1=parents, 2=grandparents
            # Original logic: if gen > N, include the ancestor
            # So we want ancestors at generation N+1 and beyond in base-1
            # Convert to base-0: (N+1) - 1 = N
            min_generation = int(self.list[1])
            self.selected_handles = find_ancestors(
                db, [person.handle], min_generation=min_generation, inclusive=False
            )

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db, person: Person) -> bool:
        return person.handle in self.selected_handles
