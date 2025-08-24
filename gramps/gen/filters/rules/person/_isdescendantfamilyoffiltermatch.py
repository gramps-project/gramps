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
from typing import Set

from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ._isdescendantfamilyof import IsDescendantFamilyOf
from ._matchesfilter import MatchesFilter
from ....utils.graph import find_descendants
from ....types import PersonHandle
from ....db.generic import Database
from ....lib import Person


# -------------------------------------------------------------------------
#
# IsDescendantFamilyOfFilterMatch
#
# -------------------------------------------------------------------------
class IsDescendantFamilyOfFilterMatch(IsDescendantFamilyOf):
    """Rule that checks for a person that is a descendant
    of someone matched by a filter"""

    labels = [_("Filter name:")]
    name = _("Descendant family members of <filter> match")
    category = _("Descendant filters")
    description = _(
        "Matches people that are descendants or the spouse "
        "of anybody matched by a filter"
    )

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[PersonHandle] = set()

        self.matchfilt = MatchesFilter(self.list[0:1])
        self.matchfilt.requestprepare(db, user)
        if user:
            user.begin_progress(
                self.category,
                _("Retrieving all sub-filter matches"),
                db.get_number_of_people(),
            )
        # Must use db.iter_people() rather that db._iter_raw_person_data()
        # because of proxies:
        for person in db.iter_people():
            if user:
                user.step_progress()
            if self.matchfilt.apply_to_one(db, person):
                self.add_matches(person)
        if user:
            user.end_progress()

    def reset(self):
        self.matchfilt.requestreset()
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles

    def add_matches(self, person: Person):
        """Add the person and their descendants to the selected handles."""
        if not person:
            return
        try:
            # Add the person themselves
            self.selected_handles.add(person.handle)

            # Add all descendants
            descendants = find_descendants(self.db, [person.handle], inclusive=False)
            self.selected_handles.update(descendants)

            # Add spouses of descendants
            self.add_spouses_of_descendants(descendants)
        except:
            pass

    def add_spouses_of_descendants(self, descendants: Set[PersonHandle]):
        """Add spouses of all descendants to the selected handles."""
        for person_handle in descendants:
            person = self.db.get_person_from_handle(person_handle)
            if person:
                for family_handle in person.family_list:
                    family = self.db.get_family_from_handle(family_handle)
                    if family:
                        # Add spouse
                        if person.handle == family.father_handle:
                            spouse_handle = family.mother_handle
                        else:
                            spouse_handle = family.father_handle
                        if spouse_handle:
                            self.selected_handles.add(spouse_handle)
