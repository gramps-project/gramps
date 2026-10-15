#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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

from ....const import GRAMPS_LOCALE as glocale
from .. import Rule
from ....db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# IsSharedAncestorInDNAMatchesOf
#
# -------------------------------------------------------------------------
class IsSharedAncestorInDNAMatchesOf(Rule):
    """Rule that checks for a person recorded as a shared ancestor in the DNA
    matches of a selected person.

    The selected person is matched through either kit of each DNA match they
    take part in. The confidence criterion is optional; a blank value matches a
    shared ancestor entry at any confidence level."""

    labels = [_("Person ID:"), _("Ancestor confidence:")]
    name = _("People who are a shared ancestor in the DNA matches of <person>")
    description = _(
        "Matches people recorded as a shared ancestor in the DNA matches of "
        "the selected person, optionally at the given confidence level"
    )
    category = _("DNA match filters")

    def prepare(self, db: Database, user):
        self._confidence = int(self.list[1]) if self.list[1] else None

        self.person_handles: set[str] = set()
        person = db.get_person_from_gramps_id(self.list[0])
        if not person:
            return

        own_test_handles = {
            handle
            for handle, data in db._iter_raw_dnatest_data()
            if data.person_handle == person.handle
        }
        if not own_test_handles:
            return

        for dnamatch in db.iter_dnamatches():
            if (
                dnamatch.subject_test_handle not in own_test_handles
                and dnamatch.match_test_handle not in own_test_handles
            ):
                continue
            for shared_ancestor in dnamatch.shared_ancestor_list:
                if not shared_ancestor.person_handle:
                    continue
                if (
                    self._confidence is not None
                    and shared_ancestor.confidence != self._confidence
                ):
                    continue
                self.person_handles.add(shared_ancestor.person_handle)

    def apply_to_one(self, db: Database, person) -> bool:
        return person.handle in self.person_handles
