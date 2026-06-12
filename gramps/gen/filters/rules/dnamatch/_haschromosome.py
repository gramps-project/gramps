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
# HasChromosome
#
# -------------------------------------------------------------------------
class HasChromosome(Rule):
    """Rule that checks for a DNA match with a segment on a given chromosome."""

    labels = [_("Chromosome:")]
    name = _("DNA matches with a segment on chromosome <chromosome>")
    description = _(
        "Matches DNA matches containing at least one segment on the given chromosome"
    )
    category = _("DNA match filters")

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        if not self.list[0]:
            return True
        chromosome = self.list[0].upper()
        for segment in dnamatch.segment_list:
            if segment.chromosome.upper() == chromosome:
                return True
        return False
