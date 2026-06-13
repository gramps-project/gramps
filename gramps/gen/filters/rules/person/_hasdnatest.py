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
from ....lib.dnatesttype import DNATestType
from .. import Rule
from ....db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# HasDNATest
#
# -------------------------------------------------------------------------
class HasDNATest(Rule):
    """Rule that checks for a person with a DNA test that meets all of the
    given criteria.

    Each criterion is optional; a blank criterion places no constraint. A person
    matches when one of their DNA tests satisfies every supplied criterion at
    once. With no criteria, any person with at least one DNA test matches."""

    labels = [_("Provider:"), _("Test type:")]
    name = _("People with a DNA test matching the given criteria")
    description = _(
        "Matches people linked to a DNA test that meets all of the given "
        "provider and test type criteria"
    )
    category = _("DNA test filters")

    def prepare(self, db: Database, user):
        self._provider = DNAProviderType()
        if self.list[0]:
            self._provider.set_from_xml_str(self.list[0])
        self._test_type = DNATestType()
        if self.list[1]:
            self._test_type.set_from_xml_str(self.list[1])

        self.person_handles: set[str] = set()
        for dnatest in db.iter_dnatests():
            if not dnatest.person_handle:
                continue
            if self.list[0] and dnatest.provider != self._provider:
                continue
            if self.list[1] and dnatest.test_type != self._test_type:
                continue
            self.person_handles.add(dnatest.person_handle)

    def apply_to_one(self, db: Database, person) -> bool:
        return person.handle in self.person_handles
