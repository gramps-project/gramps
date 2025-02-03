#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013      Nick Hall
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
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....const import GRAMPS_LOCALE as glocale

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
# HasDayOfWeek
#
# -------------------------------------------------------------------------
class HasDayOfWeek(Rule):
    """Rule that matches an event occurring on a particular day of the week."""

    labels = [_("Day of Week:")]
    name = _("Events occurring on a particular day of the week")
    description = _("Matches events occurring on a particular day of the week")
    category = _("General filters")

    def apply_to_one(self, db: Database, event: Event) -> bool:
        if not self.list[0]:
            return False
        else:
            if event.date:
                dow = event.date.get_dow()
                return dow == int(self.list[0])
            return False
