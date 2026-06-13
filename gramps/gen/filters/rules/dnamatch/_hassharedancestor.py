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
    """Rule that checks for a DNA match with a shared ancestor entry for a person."""

    labels = [_("Person ID:")]
    name = _("DNA matches with a shared ancestor entry for <person>")
    description = _(
        "Matches DNA matches with a shared ancestor entry for the specified person"
    )
    category = _("Person filters")

    def prepare(self, db: Database, user):
        person = db.get_person_from_gramps_id(self.list[0])
        self.person_handle = person.handle if person else None

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        if not self.person_handle:
            return False
        for shared_ancestor in dnamatch.shared_ancestor_list:
            if shared_ancestor.person_handle == self.person_handle:
                return True
        return False
