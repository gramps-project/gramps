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
from __future__ import annotations
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


# -------------------------------------------------------------------------
#
# IsAncestorOf
#
# -------------------------------------------------------------------------
class IsAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person"""

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Ancestors of <person>")
    category = _("Ancestral filters")
    description = _("Matches people that are ancestors of a specified person")

    def prepare(self, db: Database, user):
        """Assume that if 'Inclusive' not defined, assume inclusive"""
        self.db = db
        self.selected_handles: Set[str] = set()
        try:
            inclusive = False if int(self.list[1]) else True
        except IndexError:
            inclusive = True
        try:
            root_person = db.get_person_from_gramps_id(self.list[0])
            if root_person:
                # Use family tree traversal functionality for better performance
                # The original logic: first=True (inclusive) means DON'T include root person
                # first=False (exclusive) means DO include root person
                # So we need to invert the inclusive parameter
                ancestors = get_person_ancestors(
                    db,
                    use_parallel=db.supports_parallel_reads(),
                    max_threads=db.get_database_config("parallel", "max_threads"),
                    persons=[root_person],
                    include_root=not inclusive,
                )
                self.selected_handles.update(ancestors)
        except Exception:
            pass

    def reset(self):
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles
