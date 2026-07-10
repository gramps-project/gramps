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
# MatchesBothTestsOf
#
# -------------------------------------------------------------------------
class MatchesBothTestsOf(Rule):
    """Rule that checks for a DNA test that matches both tests of a given match.

    Given the DNA match X between tests A and B, this finds the tests that have
    a DNA match with A and a DNA match with B, the shared matches that
    triangulate against both ends of X. The two tests of X are excluded from
    the result. Matches are stored once per pair, so each match is examined
    from both of its kit sides."""

    labels = [_("DNA match ID:")]
    name = _("DNA tests that match both tests of <DNA match>")
    description = _(
        "Matches DNA tests that have a DNA match with each of the two tests of "
        "the specified DNA match"
    )
    category = _("DNA match filters")

    def prepare(self, db: Database, user):
        self.test_handles: set[str] = set()
        match = db.get_dnamatch_from_gramps_id(self.list[0])
        if not match:
            return
        test_a = match.subject_test_handle
        test_b = match.match_test_handle
        if not test_a or not test_b:
            return

        matches_a: set[str] = set()
        matches_b: set[str] = set()
        for dnamatch in db.iter_dnamatches():
            subject = dnamatch.subject_test_handle
            other = dnamatch.match_test_handle
            if not subject or not other:
                continue
            if subject == test_a:
                matches_a.add(other)
            elif other == test_a:
                matches_a.add(subject)
            if subject == test_b:
                matches_b.add(other)
            elif other == test_b:
                matches_b.add(subject)

        self.test_handles = (matches_a & matches_b) - {test_a, test_b}

    def apply_to_one(self, db: Database, dnatest) -> bool:
        return dnatest.handle in self.test_handles
