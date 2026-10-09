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
# HasDNAMatchWithSharedAncestor
#
# -------------------------------------------------------------------------
class HasDNAMatchWithSharedAncestor(Rule):
    """Rule that checks for a person linked to a DNA match that records a shared
    ancestor entry meeting all of the given criteria.

    Each criterion is optional; a blank criterion places no constraint. A match
    qualifies when one shared ancestor entry satisfies every supplied criterion
    at once, and the person is then matched through either kit of that match."""

    labels = [_("Person ID:"), _("Ancestor confidence:")]
    name = _("People with a DNA match recording <person> as a shared ancestor")
    description = _(
        "Matches people linked to a DNA test whose DNA match records the given "
        "person as a shared ancestor, optionally at the given confidence level"
    )
    category = _("DNA match filters")

    def prepare(self, db: Database, user):
        self._person_required = bool(self.list[0])
        self._person_handle = None
        if self._person_required:
            person = db.get_person_from_gramps_id(self.list[0])
            self._person_handle = person.handle if person else None
        self._confidence = int(self.list[1]) if self.list[1] else None

        self.person_handles: set[str] = set()
        if self._person_required and self._person_handle is None:
            return

        test_to_person: dict[str, str] = {}
        for handle, data in db._iter_raw_dnatest_data():
            if data.person_handle:
                test_to_person[handle] = data.person_handle

        for dnamatch in db.iter_dnamatches():
            if not self._match_has_shared_ancestor(dnamatch):
                continue
            for test_handle in (
                dnamatch.subject_test_handle,
                dnamatch.match_test_handle,
            ):
                person_handle = test_to_person.get(test_handle)
                if person_handle:
                    self.person_handles.add(person_handle)

    def _match_has_shared_ancestor(self, dnamatch) -> bool:
        for shared_ancestor in dnamatch.shared_ancestor_list:
            if (
                self._person_required
                and shared_ancestor.person_handle != self._person_handle
            ):
                continue
            if (
                self._confidence is not None
                and shared_ancestor.confidence != self._confidence
            ):
                continue
            return True
        return False

    def apply_to_one(self, db: Database, person) -> bool:
        return person.handle in self.person_handles
