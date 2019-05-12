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
Filter rule to match persons with a particular event.
"""
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
from ....lib.eventroletype import EventRoleType
from .._haseventbase import HasEventBase

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasEvent(HasEventBase):
    """Rule that checks for a person with a particular value"""

    labels = [ _('Personal event:'),
                    _('Date:'),
                    _('Place:'),
                    _('Description:'),
                    _('Main Participants:'),
                    _('Primary Role:') ]
    name = _('People with the personal <event>')
    description = _("Matches people with a personal event of a particular "
                    "value")

    def apply(self, dbase, person):
        for event_ref in person.get_event_ref_list():
            if not event_ref:
                continue
            if int(self.list[5]) and event_ref.role != EventRoleType.PRIMARY:
                # Only match primaries, no witnesses
                continue
            event = dbase.get_event_from_handle(event_ref.ref)
            if HasEventBase.apply(self, dbase, event):
                return True
        return False
