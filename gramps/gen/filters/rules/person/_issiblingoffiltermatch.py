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
# IsSiblingOfFilterMatch
#
# -------------------------------------------------------------------------
class IsSiblingOfFilterMatch(Rule):
    """Rule that checks for siblings of someone matched by a filter"""

    labels = [_("Filter name:")]
    name = _("Siblings of <filter> match")
    category = _("Family filters")
    description = _("Matches siblings of anybody matched by a filter")

    def prepare(self, db: Database, user):
        self.db = db
        self.selected_handles: Set[str] = set()
        self.matchfilt = MatchesFilter(self.list)
        self.matchfilt.requestprepare(db, user)
        if user:
            user.begin_progress(
                self.category,
                _("Retrieving all sub-filter matches"),
                db.get_number_of_people(),
            )
        for person in db.iter_people():
            if user:
                user.step_progress()
            if self.matchfilt.apply_to_one(db, person):
                self.init_list(person)
        if user:
            user.end_progress()

    def reset(self):
        self.matchfilt.requestreset()
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles

    def init_list(self, person: Person):
        if not person:
            return
        fam_id = (
            person.parent_family_list[0] if len(person.parent_family_list) > 0 else None
        )
        if fam_id:
            fam = self.db.get_family_from_handle(fam_id)
            if fam:
                self.selected_handles.update(
                    child_ref.ref
                    for child_ref in fam.child_ref_list
                    if child_ref and child_ref.ref != person.handle
                )
