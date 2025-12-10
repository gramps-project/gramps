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
from typing import Set
from ....lib import Person
from ....db import Database
from ....types import PersonHandle


# -------------------------------------------------------------------------
#
# IsLessThanNthGenerationAncestorOfDefaultPerson
#
# -------------------------------------------------------------------------
class IsLessThanNthGenerationAncestorOfDefaultPerson(Rule):
    # Submitted by Wayne Bergeron
    """Rule that checks for a person that is an ancestor of the default person
    not more than N generations away"""

    labels = [_("Number of generations:")]
    name = _("Ancestors of the Home Person " "not more than <N> generations away")
    category = _("Ancestral filters")
    description = _(
        "Matches ancestors of the Home Person " "not more than N generations away"
    )

    def prepare(self, db: Database, user):
        """Use the unified find_ancestors function"""
        self.db = db
        self.selected_handles: Set[PersonHandle] = set()
        p: Person = db.get_default_person()
        if p:
            # Original uses base-1: gen 1=root, 2=parents, 3=grandparents
            # Our function uses base-0: gen 0=root, 1=parents, 2=grandparents
            # Original logic: includes starting person and ancestors up to gen N
            # So we need to subtract 1 to convert and use inclusive=True
            max_generation = int(self.list[0]) - 1
            self.selected_handles = find_ancestors(
                db, [p.handle], max_generation=max_generation, inclusive=True
            )

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles

    def reset(self):
        self.selected_handles.clear()
