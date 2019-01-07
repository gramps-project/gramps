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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .. import Rule
from ....lib.eventroletype import EventRoleType
from ....lib.eventtype import EventType

#-------------------------------------------------------------------------
# "Witnesses"
#-------------------------------------------------------------------------
class IsWitness(Rule):
    """Witnesses"""

    labels = [_('Event type:')]
    name = _('Witnesses')
    description = _("Matches people who are witnesses in any event")
    category = _('Event filters')

    def apply(self,db,person):
        for event_ref in person.event_ref_list:
            if event_ref and event_ref.role == EventRoleType.WITNESS:
                # This is the witness.
                # If event type was given, then check it.
                if self.list[0]:
                    event = db.get_event_from_handle(event_ref.ref)
                    specified_type = EventType()
                    specified_type.set_from_xml_str(self.list[0])
                    if event.type == specified_type:
                        return True
                else:
                    # event type was not specified, we're returning a match
                    return True
        return False
