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
# MatchesMatchTestFilter
#
# -------------------------------------------------------------------------
class MatchesMatchTestFilter(MatchesFilterBase):
    """Rule that checks for a DNA match whose match kit matches a DNA test filter."""

    labels = [_("DNA test filter name:")]
    name = _("DNA matches whose match kit matches the <DNA test filter>")
    description = _(
        "Matches DNA matches whose match DNA test is matched by the "
        "specified DNA test filter name"
    )
    category = _("DNA test filters")

    # we want to have this filter show DNA test filters
    namespace = "DNATest"

    def apply_to_one(self, db: Database, dnamatch) -> bool:
        handle = dnamatch.match_test_handle
        if handle is None:
            return False
        filt = self.find_filter()
        if filt:
            dnatest = db.get_dnatest_from_handle(handle)
            if dnatest:
                return filt.apply_to_one(db, dnatest)
        return False
