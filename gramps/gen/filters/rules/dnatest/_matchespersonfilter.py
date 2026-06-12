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
from .. import MatchesFilterBase
from ....db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# MatchesPersonFilter
#
# -------------------------------------------------------------------------
class MatchesPersonFilter(MatchesFilterBase):
    """Rule that checks for a DNA test linked to a person matching a filter."""

    labels = [_("Person filter name:")]
    name = _("DNA tests linked to people matching the <person filter>")
    description = _(
        "Matches DNA tests linked to a person matched by the specified "
        "person filter name"
    )

    # we want to have this filter show person filters
    namespace = "Person"

    def apply_to_one(self, db: Database, dnatest) -> bool:
        if dnatest.person_handle is None:
            return False
        filt = self.find_filter()
        if filt:
            person = db.get_person_from_handle(dnatest.person_handle)
            if person:
                return filt.apply_to_one(db, person)
        return False
