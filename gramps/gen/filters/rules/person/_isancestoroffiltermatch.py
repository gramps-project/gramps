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
from .. import Rule
from ._matchesfilter import MatchesFilter
from ....utils.graph import find_ancestors


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
class IsAncestorOfFilterMatch(Rule):
    """Rule that checks for a person that is an ancestor of
    someone matched by a filter"""

    labels = [_("Filter name:")]
    name = _("Ancestors of <filter> match")
    category = _("Ancestral filters")
    description = _(
        "Matches people that are ancestors " "of anybody matched by a filter"
    )

    def prepare(self, db: Database, user):
        """Use the unified find_ancestors function"""
        self.db = db
        self.selected_handles: Set[str] = set()
        try:
            inclusive = (
                False if int(self.list[1]) else False
            )  # Default to False (not inclusive)
        except IndexError:
            inclusive = False  # Default to False (not inclusive)

        self.filt = MatchesFilter(self.list[0:1])
        self.filt.requestprepare(db, user)

        # Collect all person handles that match the filter
        matching_handles = []
        if user:
            user.begin_progress(
                self.category,
                _("Retrieving all sub-filter matches"),
                db.get_number_of_people(),
            )
        for person in db.iter_people():
            if user:
                user.step_progress()
            if self.filt.apply_to_one(db, person):
                matching_handles.append(person.handle)
        if user:
            user.end_progress()

        # Find ancestors of all matching people
        if matching_handles:
            self.selected_handles = find_ancestors(
                db, matching_handles, inclusive=inclusive
            )

    def reset(self):
        self.filt.requestreset()
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles
