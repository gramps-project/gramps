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
from ....lib.dnatesttype import DNATestType
from .. import Rule
from ....db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# HasTestType
#
# -------------------------------------------------------------------------
class HasTestType(Rule):
    """Rule that checks for a DNA test of a specific test type."""

    labels = [_("Test type:")]
    name = _("DNA tests of type <type>")
    description = _("Matches DNA tests of the specified test type")
    category = _("DNA test filters")

    def prepare(self, db: Database, user):
        self._test_type = DNATestType()
        if self.list[0]:
            self._test_type.set_from_xml_str(self.list[0])

    def apply_to_one(self, db: Database, dnatest) -> bool:
        if not self.list[0]:
            return True
        return dnatest.test_type == self._test_type
