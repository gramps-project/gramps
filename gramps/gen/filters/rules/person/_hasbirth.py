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
from ....datehandler import parser
from ....display.place import displayer as place_displayer
from ....lib.eventtype import EventType
from ....lib.eventroletype import EventRoleType
from .. import Rule


# -------------------------------------------------------------------------
#
# HasBirth
#
# -------------------------------------------------------------------------
class HasBirth(Rule):
    """Rule that checks for a person with a birth of a particular value"""

    labels = [_("Date:"), _("Place:"), _("Description:")]
    name = _("People with the <birth data>")
    description = _("Matches people with birth data of a particular value")
    category = _("Event filters")
    allow_regex = True

    def prepare(self, db, user):
        if self.list[0]:
            self.date = parser.parse(self.list[0])
        else:
            self.date = None

    def apply(self, db, person):
        for event_ref in person.get_event_ref_list():
            if not event_ref:
                continue
            elif event_ref.role != EventRoleType.PRIMARY:
                # Only match primaries, no witnesses
                continue
            event = db.get_event_from_handle(event_ref.ref)
            if event.get_type() != EventType.BIRTH:
                # No match: wrong type
                continue
            if not self.match_substring(2, event.get_description()):
                # No match: wrong description
                continue
            if self.date:
                if not event.get_date_object().match(self.date):
                    # No match: wrong date
                    continue
            if self.list[1]:
                place_id = event.get_place_handle()
                if place_id:
                    place = db.get_place_from_handle(place_id)
                    place_title = place_displayer.display(db, place)
                    if not self.match_substring(1, place_title):
                        # No match: wrong place
                        continue
                else:
                    # No match: event has no place, but place specified
                    continue
            # This event matched: exit positive
            return True
        # Nothing matched: exit negative
        return False
