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
Rule matching people who are witnesses in any event.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
from ....lib.eventroletype import EventRoleType
from ....lib.eventtype import EventType
from .. import Rule

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Person
from ....db import Database


_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# IsWitness
#
# -------------------------------------------------------------------------
class IsWitness(Rule):
    """
    Rule matching people who are witnesses in any event.
    """

    labels = [_("Event type:")]
    name = _("Witnesses")
    description = _("Matches people who are witnesses in any event")
    category = _("Event filters")

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.event_type = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things only want to do once.
        """
        if self.list[0]:
            self.event_type = EventType()
            self.event_type.set_from_xml_str(self.list[0])

    def apply_to_one(self, db: Database, obj: Person) -> bool:
        """
        Apply the rule. Return True on a match.
        """
        for event_ref in obj.event_ref_list:
            if event_ref.role.value == EventRoleType.WITNESS:
                # This is the witness.
                # If event type was given, then check it.
                if self.event_type:
                    event = db.get_event_from_handle(event_ref.ref)
                    if event.type == self.event_type:
                        return True
                else:
                    # event type was not specified, we're returning a match
                    return True
        return False
