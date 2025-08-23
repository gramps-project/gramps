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
from ....utils.family_tree_traversal import get_person_descendants_with_min_depth


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
# IsMoreThanNthGenerationDescendantOf
#
# -------------------------------------------------------------------------
class IsMoreThanNthGenerationDescendantOf(Rule):
    """Rule that checks for a person that is a descendant of a specified person
    at least N generations away"""

    labels = [_("ID:"), _("Number of generations:")]
    name = _("Descendants of <person> at least <N> generations away")
    category = _("Descendant filters")
    description = _(
        "Matches people that are descendants of a specified "
        "person at least N generations away"
    )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[PersonHandle] = set()
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            if root_person:
                min_generations = int(self.list[1])
                # Use standardized family tree traversal to find descendants
                # beyond the specified generation depth
                # Note: family tree traversal uses depth 0 for root, but original generation counting
                # uses generation 1 for root. So we need to adjust for this difference.
                # We want descendants MORE than N generations away, so min_depth = min_generations
                self.selected_handles = get_person_descendants_with_min_depth(
                    db=self.db,
                    persons=[root_person],
                    min_depth=min_generations,  # No +1 needed, just use min_generations directly
                    max_depth=None,  # No maximum depth limit
                    include_root=False,  # Don't include the root person
                    use_parallel=db.supports_parallel_reads(),
                    max_threads=db.get_database_config("parallel", "max_threads"),
                )
        except (ValueError, IndexError):
            pass

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles
