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
# HasSegment
#
# -------------------------------------------------------------------------
class HasSegment(Rule):
    """Rule that checks for a DNA match containing a single segment that meets
    all of the given criteria.

    Each criterion is optional; a blank criterion places no constraint. A match
    succeeds when one segment satisfies every supplied criterion at once."""

    labels = [
        _("Chromosome:"),
        _("Minimum cM:"),
        _("Minimum SNPs:"),
        _("Phase:"),
        _("IBD state:"),
    ]
    name = _("DNA matches with a segment matching the given criteria")
    description = _(
        "Matches DNA matches containing a segment that meets all of the "
        "given chromosome, cM, SNP, phase and IBD state criteria"
    )
    category = _("DNA match filters")

    def prepare(self, db: Database, user):
        try:
            self._min_cm = float(self.list[1]) if self.list[1] else None
        except ValueError:
            self._min_cm = None
        try:
            self._min_snps = int(self.list[2]) if self.list[2] else None
        except ValueError:
            self._min_snps = None

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        chromosome = self.list[0].upper()
        phase = self.list[3]
        ibd_state = self.list[4]
        for segment in dnamatch.segment_list:
            if chromosome and segment.chromosome.upper() != chromosome:
                continue
            if self._min_cm is not None and segment.shared_cm < self._min_cm:
                continue
            if self._min_snps is not None and segment.snp_count < self._min_snps:
                continue
            if phase != "" and segment.phase != int(phase):
                continue
            if ibd_state != "" and segment.ibd_state != int(ibd_state):
                continue
            return True
        return False
