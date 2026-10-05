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
    """Rule that checks for a DNA test with a matching mtDNA haplogroup."""

    labels = [_("Haplogroup:")]
    name = _("DNA tests with an mtDNA haplogroup containing <text>")
    description = _("Matches DNA tests whose mtDNA haplogroup contains the given text")
    category = _("DNA test filters")

    def apply_to_one(self, db: Database, dnatest) -> bool:
        return dnatest.mt_haplogroup.upper().find(self.list[0].upper()) != -1
