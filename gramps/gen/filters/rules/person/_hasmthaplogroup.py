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
# HasMtHaplogroup
#
# -------------------------------------------------------------------------
class HasMtHaplogroup(Rule):
    """Rule that checks for a person with a DNA test that has a matching
    mtDNA haplogroup."""

    labels = [_("Haplogroup:")]
    name = _("People with a DNA test mtDNA haplogroup containing <text>")
    description = _(
        "Matches people linked to a DNA test whose mtDNA haplogroup contains "
        "the given text"
    )
    category = _("DNA test filters")

    def prepare(self, db: Database, user):
        text = self.list[0].upper()
        self.person_handles: set[str] = set()
        for dnatest in db.iter_dnatests():
            if not dnatest.person_handle:
                continue
            if dnatest.mt_haplogroup.upper().find(text) != -1:
                self.person_handles.add(dnatest.person_handle)

    def apply_to_one(self, db: Database, person) -> bool:
        return person.handle in self.person_handles
