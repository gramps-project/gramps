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
# HasDNAMatch
#
# -------------------------------------------------------------------------
class HasDNAMatch(Rule):
    """Rule that checks for a person linked to at least one DNA match."""

    labels = []
    name = _("People with a DNA match")
    description = _(
        "Matches people linked to a DNA test that takes part in at least one "
        "DNA match"
    )
    category = _("DNA match filters")

    def prepare(self, db: Database, user):
        test_to_person: dict[str, str] = {}
        for handle, data in db._iter_raw_dnatest_data():
            if data.person_handle:
                test_to_person[handle] = data.person_handle

        self.person_handles: set[str] = set()
        for _handle, data in db._iter_raw_dnamatch_data():
            for test_handle in (data.subject_test_handle, data.match_test_handle):
                person_handle = test_to_person.get(test_handle)
                if person_handle:
                    self.person_handles.add(person_handle)

    def apply_to_one(self, db: Database, person) -> bool:
        return person.handle in self.person_handles
