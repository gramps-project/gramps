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
Rule to check for a person who has a relationship event with a particular value.
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
from ....lib import Person
from ....db import Database


# -------------------------------------------------------------------------
#
# HasFamilyEvent
#
# -------------------------------------------------------------------------
class HasFamilyEvent(Rule):
    """
    Rule to check for a person who has a relationship event with a particular value.
    """

    labels = [_("Family event:"), _("Date:"), _("Place:"), _("Description:")]
    name = _("People with the family <event>")
    description = _("Matches people with a family event of a particular value")
    category = _("Event filters")
    allow_regex = True

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.date = None
        self.event_type = None

    def prepare(self, db: Database, user):
        if self.list[0]:
            self.event_type = EventType()
            self.event_type.set_from_xml_str(self.list[0])
        try:
            if self.list[1]:
                self.date = parser.parse(self.list[1])
        except:
            pass

    def apply_to_one(self, db: Database, person: Person) -> bool:
        for handle in person.family_list:
            family = db.get_family_from_handle(handle)
            for event_ref in family.event_ref_list:
                event = db.get_event_from_handle(event_ref.ref)
                val = 1
                if self.event_type and event.type != self.event_type:
                    val = 0
                if self.list[3]:
                    if not self.match_substring(3, event.description):
                        val = 0
                if self.date:
                    if not event.date.match(self.date):
                        val = 0
                if self.list[2]:
                    place_id = event.place
                    if place_id:
                        place = db.get_place_from_handle(place_id)
                        place_title = place_displayer.display(db, place)
                        if not self.match_substring(2, place_title):
                            val = 0
                    else:
                        val = 0

                if val == 1:
                    return True
        return False
