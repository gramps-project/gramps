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
# HasMatchPerson
#
# -------------------------------------------------------------------------
class HasMatchPerson(Rule):
    """Rule that checks for a DNA match whose match kit belongs to a person."""

    labels = [_("Person ID:")]
    name = _("DNA matches whose match kit belongs to <person>")
    description = _(
        "Matches DNA matches whose match kit is linked to the specified person"
    )
    category = _("Person filters")

    def prepare(self, db: Database, user):
        self.test_handles: set[str] = set()
        person = db.get_person_from_gramps_id(self.list[0])
        if not person:
            return
        for handle, data in db._iter_raw_dnatest_data():
            if data.person_handle == person.handle:
                self.test_handles.add(handle)

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        return dnamatch.match_test_handle in self.test_handles
