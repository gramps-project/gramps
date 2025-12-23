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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
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
from .. import Rule


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import cast

from ....lib import Person
from ....db import Database
from ....types import EventHandle


# -------------------------------------------------------------------------
# "People with incomplete events"
# -------------------------------------------------------------------------
class PersonWithIncompleteEvent(Rule):
    """People with incomplete events"""

    name = _("People with incomplete events")
    description = _("Matches people with missing date or place in an event")
    category = _("Event filters")

    def prepare(self, db: Database, user):
        if db.can_use_fast_selects():
            self.selected_handles = set(
                list(
                    db.select_from_person(
                        what="person.handle",
                        where="item in person.event_ref_list and item.ref == event.handle and (not event.place or not event.date)",
                    )
                )
            )

    def apply_to_one(self, db: Database, person: Person) -> bool:
        if db.can_use_fast_selects():
            return person.handle in self.selected_handles
        else:
            for event_ref in person.event_ref_list:
                if event_ref and event_ref.ref:
                    event = db.get_event_from_handle(cast(EventHandle, event_ref.ref))
                    if not event.place:
                        return True
                    if not event.date:
                        return True
            return False
