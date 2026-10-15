#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Ian Davis
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

from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

from . import MatchesFilterBase

from ...lib.citationbase import CitationBase
from ...db import Database


class MatchesCitationFilterBase(MatchesFilterBase):
    """Rule that checks against a citation filter."""

    labels = [_("Citation filter name:")]
    name = "Objects with citation matching the <citation filter>"
    description = (
        "Matches objects with citations that match the "
        "specified citation filter name"
    )
    category = _("Citation/source filters")

    namespace = "Citation"

    def prepare(self, db: Database, user):
        MatchesFilterBase.prepare(self, db, user)
        self.MCF_filt = self.find_filter()

    def apply_to_one(self, db: Database, object: CitationBase) -> bool:
        if self.MCF_filt is None:
            return False

        for citation_handle in object.citation_list:
            citation = db.get_citation_from_handle(citation_handle)
            if self.MCF_filt.apply_to_one(db, citation):
                return True
        return False
