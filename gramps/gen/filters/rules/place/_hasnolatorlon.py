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
# gen.filters.rules/Place/_HasNoLatOrLon.py


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
from ....lib import Place
from ....db import Database


# -------------------------------------------------------------------------
#
# HasNoLatOrLon
#
# -------------------------------------------------------------------------
class HasNoLatOrLon(Rule):
    """Rule that checks if Latitude or Longitude are not given"""

    labels = []
    name = _("Places with no latitude or longitude given")
    description = _("Matches places with empty latitude or longitude")
    category = _("Position filters")

    def apply_to_one(self, db: Database, place: Place) -> bool:
        if place.lat.strip() and place.long.strip():
            return False
        return True
