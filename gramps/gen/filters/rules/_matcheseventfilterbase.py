#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Benny Malengier
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
# Typing modules
#
# -------------------------------------------------------------------------
from ...lib.eventbase import EventBase
from ...db import Database


# -------------------------------------------------------------------------
#
# MatchesEventFilter
#
# -------------------------------------------------------------------------
class MatchesEventFilterBase(MatchesFilterBase):
    """
    Rule that checks against another filter.

    This is a base rule for subclassing by specific objects.
    Subclasses need to define the namespace class attribute.

    """

    labels = ["Event filter name:"]
    name = "Objects with events matching the <event filter>"
    description = "Matches objects who have events that match a certain" " event filter"
    category = _("General filters")

    # we want to have this filter show event filters
    namespace = "Event"

    def prepare(self, db: Database, user):
        MatchesFilterBase.prepare(self, db, user)
        self.MEF_filt = self.find_filter()

    def apply_to_one(self, db: Database, object: EventBase) -> bool:
        if self.MEF_filt is None:
            return False

        eventlist = [x.ref for x in object.event_ref_list]
        for eventhandle in eventlist:
            # check if event in event filter
            event = db.get_event_from_handle(eventhandle)
            if self.MEF_filt.apply_to_one(db, event):
                return True
        return False
