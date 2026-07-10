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
# SharesSegmentWithMatch
#
# -------------------------------------------------------------------------
class SharesSegmentWithMatch(Rule):
    """Rule that checks for a DNA match sharing an overlapping segment with a
    given other DNA match.

    Two segments overlap when they lie on the same chromosome and their base
    pair ranges intersect. Segments without position data are ignored, and the
    target match is excluded from its own results."""

    labels = [_("ID:")]
    name = _("DNA matches sharing a segment with <match>")
    description = _(
        "Matches DNA matches with a segment overlapping a segment of the "
        "specified DNA match"
    )
    category = _("DNA match filters")

    def prepare(self, db: Database, user):
        self.target_handle = None
        # list of (chromosome, start_bp, end_bp) for the target's located segments
        self.target_segments: list[tuple[str, int, int]] = []
        target = db.get_dnamatch_from_gramps_id(self.list[0])
        if not target:
            return
        self.target_handle = target.handle
        for segment in target.segment_list:
            if segment.end_bp:
                self.target_segments.append(
                    (segment.chromosome.upper(), segment.start_bp, segment.end_bp)
                )

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        if not self.target_segments:
            return False
        if dnamatch.handle == self.target_handle:
            return False
        for segment in dnamatch.segment_list:
            if not segment.end_bp:
                continue
            chromosome = segment.chromosome.upper()
            start = segment.start_bp
            end = segment.end_bp
            for target_chromosome, target_start, target_end in self.target_segments:
                if (
                    chromosome == target_chromosome
                    and start <= target_end
                    and target_start <= end
                ):
                    return True
        return False
