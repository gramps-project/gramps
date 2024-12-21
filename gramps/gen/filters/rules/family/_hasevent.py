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
Filter rule to match families with a particular event.
"""
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
from .._haseventbase import HasEventBase


# -------------------------------------------------------------------------
#
# HasEvent
#
# -------------------------------------------------------------------------
class HasEvent(HasEventBase):
    """Rule that checks for a family event with a particular value"""

    labels = [
        _("Family event:"),
        _("Date:"),
        _("Place:"),
        _("Description:"),
        _("Main Participants"),
    ]
    name = _("Families with the <event>")
    description = _("Matches families with an event of a particular value")

    def apply_to_one(self, dbase, data):
        family = self.get_object(data)
        for event_ref in data["event_ref_list"]:
            if not event_ref:
                continue
            event_data = dbase.get_raw_event_data(event_ref["ref"])
            if HasEventBase.apply_to_one(self, dbase, event_data):
                return True
        return False
