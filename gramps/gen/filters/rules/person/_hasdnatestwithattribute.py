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
from ....lib.dnaattrtype import DNAAttributeType
from .._hasattributebase import HasAttributeBase
from ....db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# HasDNATestWithAttribute
#
# -------------------------------------------------------------------------
class HasDNATestWithAttribute(HasAttributeBase):
    """Rule that checks for a person with a DNA test having a given attribute."""

    attribute_class = DNAAttributeType
    labels = [_("DNA test attribute:"), _("Value:")]
    name = _("People with a DNA test with the <attribute>")
    description = _(
        "Matches people linked to a DNA test with the attribute of a "
        "particular value"
    )
    category = _("DNA test filters")

    def prepare(self, db: Database, user):
        super().prepare(db, user)
        self.person_handles: set[str] = set()
        if not self.attribute_type:
            return
        for dnatest in db.iter_dnatests():
            if not dnatest.person_handle:
                continue
            for attribute in dnatest.attribute_list:
                if attribute.type == self.attribute_type and self.match_substring(
                    1, attribute.value
                ):
                    self.person_handles.add(dnatest.person_handle)
                    break

    def apply_to_one(self, db: Database, person) -> bool:
        return person.handle in self.person_handles
