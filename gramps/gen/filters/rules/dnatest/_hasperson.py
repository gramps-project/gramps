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
# HasPerson
#
# -------------------------------------------------------------------------
class HasPerson(Rule):
    """Rule that checks for a DNA test linked to a specific person."""

    labels = [_("Person ID:")]
    name = _("DNA tests linked to <person>")
    description = _("Matches DNA tests linked to the specified person")
    category = _("Person filters")

    def prepare(self, db: Database, user):
        self.person_handle = None
        person = db.get_person_from_gramps_id(self.list[0])
        if person:
            self.person_handle = person.handle

    def apply_to_one(self, db: Database, dnatest) -> bool:
        if self.person_handle is None:
            return False
        return dnatest.person_handle == self.person_handle
