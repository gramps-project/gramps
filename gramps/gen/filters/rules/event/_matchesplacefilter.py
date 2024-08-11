#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .._matchesfilterbase import MatchesFilterBase


# -------------------------------------------------------------------------
#
# MatchesFilter
#
# -------------------------------------------------------------------------
class MatchesPlaceFilter(MatchesFilterBase):
    """
    Rule that checks against another filter.

    This is a base rule for subclassing by specific objects.
    Subclasses need to define the namespace class attribute.
    """

    labels = [_("Place filter name:")]
    name = _("Events of places matching the <place filter>")
    description = _(
        "Matches events that occurred at places that match the "
        "specified place filter name"
    )
    category = _("General filters")
    # we want to have this filter show place filters
    namespace = "Place"

    def apply(self, db, event):
        filt = self.find_filter()
        if filt:
            handle = event.get_place_handle()
            if handle and filt.check(db, handle):
                return True
        return False
