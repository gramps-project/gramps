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

#-------------------------------------------------------------------------
# "Families with incomplete events"
#-------------------------------------------------------------------------
class FamilyWithIncompleteEvent(Rule):
    """Families with incomplete events"""

    name = _('Families with incomplete events')
    description = _("Matches people with missing date or "
                    "place in an event of the family")
    category = _('Event filters')

    def apply(self,db,person):
        for family_handle in person.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            if family:
                for event_ref in family.get_event_ref_list():
                    if event_ref:
                        event = db.get_event_from_handle(event_ref.ref)
                        if not event.get_place_handle():
                            return True
                        if not event.get_date_object():
                            return True
        return False
