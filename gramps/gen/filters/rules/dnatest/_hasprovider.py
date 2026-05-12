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
from ....lib.dnaprovidertype import DNAProviderType
from .. import Rule
from ....db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# HasProvider
#
# -------------------------------------------------------------------------
class HasProvider(Rule):
    """Rule that checks for a DNA test from a specific provider."""

    labels = [_("Provider:")]
    name = _("DNA tests with provider <provider>")
    description = _("Matches DNA tests from the specified provider")
    category = _("DNA test filters")

    def prepare(self, db: Database, user):
        self._provider = DNAProviderType()
        if self.list[0]:
            self._provider.set_from_xml_str(self.list[0])

    def apply_to_one(self, db: Database, dnatest) -> bool:
        if not self.list[0]:
            return True
        return dnatest.provider == self._provider
