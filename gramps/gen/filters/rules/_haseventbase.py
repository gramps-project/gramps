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

"""
Rule that checks for an event with a particular value.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale
from ...datehandler import parser
from ...display.place import displayer as place_displayer
from ...lib.eventtype import EventType
from ...utils.db import get_participant_from_event
from . import Rule

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ...lib import Event
from ...db import Database


# -------------------------------------------------------------------------
#
# HasEventBase
#
# -------------------------------------------------------------------------
class HasEventBase(Rule):
    """
    Rule that checks for an event with a particular value.
    """

    labels = ["Event type:", "Date:", "Place:", "Description:", "Main Participants:"]
    name = "Events matching parameters"
    description = "Matches events with particular parameters"
    category = _("Event filters")
    allow_regex = True

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.date = None
        self.event_type = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things that should only be done once.
        """
        if self.list[0]:
            self.event_type = EventType()
            self.event_type.set_from_xml_str(self.list[0])
        try:
            if self.list[1]:
                self.date = parser.parse(self.list[1])
        except:
            pass

    def apply_to_one(self, db: Database, event: Event) -> bool:
        """
        Apply the rule. Return True if a match.
        """
        if self.event_type:
            if self.event_type.is_custom() and self.use_regex:
                if self.regex[0].search(str(event.type)) is None:
                    return False
            elif event.type != self.event_type:
                return False

        if not self.match_substring(3, event.description):
            return False

        if self.date:
            if not event.date.match(self.date):
                return False

        if self.list[2]:
            place_id = event.place
            if place_id:
                place = db.get_place_from_handle(place_id)
                place_title = place_displayer.display(db, place)
                if not self.match_substring(2, place_title):
                    return False
            else:
                return False

        if not self.match_substring(
            4, get_participant_from_event(db, event.handle, all_=True)
        ):
            return False

        return True
