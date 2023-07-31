#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Benny Malengier
# Copyright (C) 2011       Tim G L Lyons
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from . import MatchesFilterBase


# -------------------------------------------------------------------------
#
# MatchesFilter
#
# -------------------------------------------------------------------------
class MatchesSourceFilterBase(MatchesFilterBase):
    """
    Rule that checks against another filter.
    """

    labels = [_("Source filter name:")]
    name = "Objects with source matching the <source filter>"
    description = (
        "Matches objects with sources that match the " "specified source filter name"
    )
    category = _("Citation/source filters")

    # we want to have this filter show source filters
    namespace = "Source"

    def prepare(self, db, user):
        MatchesFilterBase.prepare(self, db, user)
        self.MSF_filt = self.find_filter()

    def apply(self, db, object):
        if self.MSF_filt is None:
            return False

        for citation_handle in object.get_citation_list():
            citation = db.get_citation_from_handle(citation_handle)
            sourcehandle = citation.get_reference_handle()
            if self.MSF_filt.check(db, sourcehandle):
                return True
        return False
