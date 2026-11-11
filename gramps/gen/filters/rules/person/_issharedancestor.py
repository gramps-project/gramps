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
# IsSharedAncestor
#
# -------------------------------------------------------------------------
class IsSharedAncestor(Rule):
    """Rule that checks for a person recorded as a shared ancestor in a DNA
    match.

    The confidence criterion is optional; a blank value matches a shared
    ancestor entry at any confidence level."""

    labels = [_("Ancestor confidence:")]
    name = _("People who are a shared ancestor in a DNA match")
    description = _(
        "Matches people recorded as a shared ancestor in a DNA match, "
        "optionally at the given confidence level"
    )
    category = _("DNA match filters")

    def prepare(self, db: Database, user):
        self._confidence = int(self.list[0]) if self.list[0] else None

        self.person_handles: set[str] = set()
        for dnamatch in db.iter_dnamatches():
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
