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
from ....display.name import displayer as name_displayer
from .. import Rule
from ....db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# HasDNATest
#
# -------------------------------------------------------------------------
class HasDNATest(Rule):
    """
    Rule that matches DNA tests by person name, account name, kit ID, or
    haplogroup.  All supplied fields must match (AND logic).  Empty fields
    are ignored.
    """

    labels = [
        _("Person name:"),
        _("Account name:"),
        _("Kit ID:"),
        _("Haplogroup:"),
    ]
    name = _("DNA tests matching <text>")
    description = _(
        "Matches DNA tests by person name, account name, kit ID, or haplogroup"
    )
    category = _("DNA test filters")
    allow_regex = True

    def apply_to_one(self, db: Database, dnatest) -> bool:
        if self.list[0]:
            person_name = ""
            if dnatest.person_handle:
                person = db.get_person_from_handle(dnatest.person_handle)
                if person:
                    person_name = name_displayer.display(person)
            if not self.match_substring(0, person_name):
                return False

        if self.list[1] and not self.match_substring(1, dnatest.account_name):
            return False

        if self.list[2] and not self.match_substring(2, dnatest.kit_id):
            return False

        if self.list[3] and not self.match_substring(3, dnatest.haplogroup):
            return False

        return True
