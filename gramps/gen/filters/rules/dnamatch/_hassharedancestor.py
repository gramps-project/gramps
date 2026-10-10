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
# HasSharedAncestor
#
# -------------------------------------------------------------------------
class HasSharedAncestor(Rule):
    """Rule that checks for a DNA match with a shared ancestor entry that meets
    all of the given criteria.

    Each criterion is optional; a blank criterion places no constraint. A match
    succeeds when one shared ancestor entry satisfies every supplied criterion
    at once."""

    labels = [_("Person ID:"), _("Ancestor confidence:")]
    name = _("DNA matches with a shared ancestor entry for <person> at <confidence>")
    description = _(
        "Matches DNA matches with a shared ancestor entry for the given person "
        "and/or at the given confidence level"
    )
    category = _("Person filters")

    def prepare(self, db: Database, user):
        self._person_handle = None
        self._person_required = bool(self.list[0])
        if self._person_required:
            person = db.get_person_from_gramps_id(self.list[0])
            self._person_handle = person.handle if person else None
        self._confidence = int(self.list[1]) if self.list[1] else None

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        if self._person_required and self._person_handle is None:
            return False
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
