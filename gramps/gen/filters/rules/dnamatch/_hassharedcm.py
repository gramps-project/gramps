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
# HasSharedCm
#
# -------------------------------------------------------------------------
class HasSharedCm(Rule):
    """Rule that checks for a DNA match with shared cM within a given range."""

    labels = [
        _("Minimum cM:"),
        _("Maximum cM:"),
    ]
    name = _("DNA matches with shared cM between <min> and <max>")
    description = _(
        "Matches DNA matches whose total shared cM falls within the specified range"
    )
    category = _("DNA match filters")

    def prepare(self, db: Database, user):
        try:
            self._min_cm = float(self.list[0]) if self.list[0] else None
        except ValueError:
            self._min_cm = None
        try:
            self._max_cm = float(self.list[1]) if self.list[1] else None
        except ValueError:
            self._max_cm = None

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        if self._min_cm is not None and dnamatch.shared_cm < self._min_cm:
            return False
        if self._max_cm is not None and dnamatch.shared_cm > self._max_cm:
            return False
        return True
