#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2015       Nick Hall
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

_ = glocale.translation.sgettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from ....utils.location import located_in


# -------------------------------------------------------------------------
#
# IsEnclosedBy
#
# -------------------------------------------------------------------------
class IsEnclosedBy(Rule):
    """
    Rule that checks for a place enclosed by another place
    """

    labels = [_("ID:"), _("Inclusive:")]
    name = _("Places enclosed by another place")
    description = _("Matches a place enclosed by a particular place")
    category = _("General filters")

    def prepare(self, db, user):
        self.handle = None
        place = db.get_place_from_gramps_id(self.list[0])
        if place:
            self.handle = place.handle

    def apply(self, db, place):
        if self.handle is None:
            return False
        if self.list[1] == "1" and place.handle == self.handle:
            return True
        if located_in(db, place.handle, self.handle):
            return True
        return False
