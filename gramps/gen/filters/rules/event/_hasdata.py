#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Gary Burton
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
Rules that check for events containing particular values.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
from ....datehandler import parser
from ....display.place import displayer as place_displayer
from ....lib.eventtype import EventType
from .. import Rule

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Event
from ....db import Database


# -------------------------------------------------------------------------
#
# HasData
#
# -------------------------------------------------------------------------
class HasData(Rule):
    """
    Rule that checks for an event containing particular values.
    """

    labels = [_("Event type:"), _("Date:"), _("Place:"), _("Description:")]
    name = _("Events with <data>")
    description = _("Matches events with data of a particular value")
    category = _("General filters")
    allow_regex = True

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.event_type = None
        self.date = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things we only want to do once.
        """
        self.event_type = self.list[0]
        self.date = self.list[1]

        if self.event_type:
            self.event_type = EventType()
            self.event_type.set_from_xml_str(self.list[0])

        if self.date:
            self.date = parser.parse(self.date)

    def apply_to_one(self, db: Database, obj: Event) -> bool:
        """
        Apply the rule. Return True on a match.
        """
        if self.event_type and obj.type != self.event_type:
            # No match
            return False

        if self.date and not obj.date.match(self.date):
            # No match
            return False

        if self.list[2]:
            place_id = obj.place
            if place_id:
                place = db.get_place_from_handle(place_id)
                place_title = place_displayer.display(db, place)
                if not self.match_substring(2, place_title):
                    # No match
                    return False
            else:
                # No place attached to event
                return False

        if not self.match_substring(3, obj.description):
            # No match
            return False

        # All conditions matched
        return True
