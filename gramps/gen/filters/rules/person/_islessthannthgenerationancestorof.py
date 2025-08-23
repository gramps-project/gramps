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
from typing import Set
from ....lib import Person
from ....db import Database
from ....types import PersonHandle


# -------------------------------------------------------------------------
#
# IsLessThanNthGenerationAncestorOf
#
# -------------------------------------------------------------------------
class IsLessThanNthGenerationAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person
    not more than N generations away"""

    labels = [_("ID:"), _("Number of generations:")]
    name = _("Ancestors of <person> not more than <N> generations away")
    category = _("Ancestral filters")
    description = _(
        "Matches people that are ancestors "
        "of a specified person not more than N generations away"
    )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[str] = set()
        person = db.get_person_from_gramps_id(self.list[0])
        if person:
            try:
                max_generations = int(self.list[1])
                # Use family tree traversal with depth limiting
                # Note: max_depth in family tree traversal corresponds to generations
                # We want ancestors not more than N generations away, so max_depth = max_generations
                ancestors = get_person_ancestors(
                    db=db,
                    persons=[person],
                    max_depth=max_generations,
                    include_root=False,  # Don't include the root person
                    use_parallel=True,
                    max_threads=4,
                )
                self.selected_handles.update(ancestors)
            except (ValueError, IndexError):
                pass

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles
