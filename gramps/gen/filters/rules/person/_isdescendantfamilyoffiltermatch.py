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
from ....types import PersonHandle
from ....db.generic import Database
from ....user import User


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

    def prepare(self, db: Database, user: User):
        self.db = db
        self.selected_handles: Set[PersonHandle] = set()

        self.matchfilt = MatchesFilter(self.list[0:1])
        self.matchfilt.requestprepare(db, user)
        if user:
            user.begin_progress(
                self.category,
                _("Retrieving all sub-filter matches"),
                db.get_number_of_people(),
                can_cancel=True,
            )
        for handle, person in db._iter_raw_person_data():
            if user:
                user.step_progress()
                if user.get_cancelled():
                    break
            if self.matchfilt.apply_to_one(db, person):
                self.add_matches(person, user)
        if user:
            user.end_progress()

    def reset(self):
        self.matchfilt.requestreset()
        self.selected_handles.clear()
