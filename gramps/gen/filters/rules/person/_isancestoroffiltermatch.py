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
from ._isancestorof import IsAncestorOf
from ._matchesfilter import MatchesFilter
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
# IsAncestorOfFilterMatch
#
# -------------------------------------------------------------------------
class IsAncestorOfFilterMatch(IsAncestorOf):
    """Rule that checks for a person that is an ancestor of
    someone matched by a filter"""

    labels = [_("Filter name:")]
    name = _("Ancestors of <filter> match")
    category = _("Ancestral filters")
    description = _(
        "Matches people that are ancestors " "of anybody matched by a filter"
    )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[str] = set()
        try:
            if int(self.list[1]):
                inclusive = False
            else:
                inclusive = True
        except IndexError:
            inclusive = False

        self.filt = MatchesFilter(self.list[0:1])
        self.filt.requestprepare(db, user)
        if user:
            user.begin_progress(
                self.category,
                _("Retrieving all sub-filter matches"),
                db.get_number_of_people(),
            )

        # Collect all matching persons first
        matching_persons = []
        for person in db.iter_people():
            if user:
                user.step_progress()
            if self.filt.apply_to_one(db, person):
                matching_persons.append(person)

        if user:
            user.end_progress()

        # Use parallel ancestor functionality for better performance
        if matching_persons:
            if user:
                user.begin_progress(
                    self.category,
                    _("Finding ancestors"),
                    len(matching_persons),
                )

            # Get ancestors for all matching persons at once
            # Include matching persons if in inclusive mode
            ancestors = get_person_ancestors(db, matching_persons, include_root=False)
            self.selected_handles.update(ancestors)

            # Add the matching persons themselves if inclusive mode
            if inclusive:
                for person in matching_persons:
                    self.selected_handles.add(person.handle)

            if user:
                user.end_progress()

    def reset(self):
        self.filt.requestreset()
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles
