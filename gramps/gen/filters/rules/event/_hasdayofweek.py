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
# HasDayOfWeek
#
# -------------------------------------------------------------------------
class HasDayOfWeek(Rule):
    """Rule that matches an event occurring on a particular day of the week."""

    labels = [_("Day of Week:")]
    name = _("Events occurring on a particular day of the week")
    description = _("Matches events occurring on a particular day of the week")
    category = _("General filters")

    def apply(self, db, event):
        if not self.list[0]:
            return False
        else:
            dow = event.get_date_object().get_dow()
            return dow == int(self.list[0])
