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
# HasSegmentOverlapping
#
# -------------------------------------------------------------------------
class HasSegmentOverlapping(Rule):
    """Rule that checks for a DNA match with a segment overlapping a given
    chromosome region.

    A segment overlaps the region when it lies on the same chromosome and its
    base pair range intersects the given start and end positions. All three of
    chromosome, start and end are required; otherwise nothing matches."""

    labels = [_("Chromosome:"), _("Start position:"), _("End position:")]
    name = _("DNA matches with a segment overlapping <chromosome> <start> <end>")
    description = _(
        "Matches DNA matches containing a segment that overlaps the given "
        "chromosome region"
    )
    category = _("DNA match filters")

    def prepare(self, db: Database, user):
        self.chromosome = self.list[0].upper()
        try:
            self.start = int(self.list[1]) if self.list[1] else None
        except ValueError:
            self.start = None
        try:
            self.end = int(self.list[2]) if self.list[2] else None
        except ValueError:
            self.end = None
        if self.start is not None and self.end is not None and self.start > self.end:
            self.start, self.end = self.end, self.start

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        if not self.chromosome or self.start is None or self.end is None:
            return False
        for segment in dnamatch.segment_list:
            if not segment.end_bp:
                continue
            if segment.chromosome.upper() != self.chromosome:
                continue
            if segment.start_bp <= self.end and self.start <= segment.end_bp:
                return True
        return False
