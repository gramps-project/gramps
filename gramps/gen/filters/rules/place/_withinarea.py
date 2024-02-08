"""
 WithinArea : used to verify if a place is contained in a specific area
"""

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2015       Nick Hall
# Copyright (C) 2017-      Serge Noiraud
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

from math import pi, cos, hypot
import re

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.errors import FilterError
from ....const import GRAMPS_LOCALE as glocale
from .. import Rule
from ....utils.place import conv_lat_lon

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# WithinArea
#
# -------------------------------------------------------------------------
class WithinArea(Rule):
    """
    Rule that checks for a place within an area
    """

    labels = [_("ID:"), _("Value:"), _("Units:")]
    name = _("Places within an area")
    description = _("Matches places within a given distance of another place")
    category = _("Position filters")
    handle = None
    radius = None
    latitude = None
    longitude = None

    def prepare(self, db, user):
        ref_place = db.get_place_from_gramps_id(self.list[0])
        self.handle = None
        self.radius = None
        self.latitude = None
        self.longitude = None
        if ref_place:
            self.handle = ref_place.handle
            latitude = ref_place.get_latitude()
            if latitude == "":
                latitude = None
                return
            longitude = ref_place.get_longitude()
            self.latitude, self.longitude = conv_lat_lon(latitude, longitude, "D.D8")
            if self.latitude is None or self.longitude is None:
                raise FilterError(
                    _("Cannot use the filter 'within area'"),
                    _(
                        "The place you selected contains bad"
                        " coordinates. Please, run the tool "
                        "'clean input data'"
                    ),
                )

            val = self.list[1]
            if isinstance(val, str):
                val = re.sub(r"\D", "", val)  # suppress all alpha characters
            value = int(val)
            unit = int(self.list[2])
            # earth perimeter in kilometers for latitude
            # 2 * pi * (6371 * cos(latitude/180*pi))
            # so 1 degree correspond to the result above / 360
            earth_perimeter = 2 * pi * (6371 * cos(float(self.latitude) / 180 * pi))
            if unit == 0:  # kilometers
                self.radius = float(value / (earth_perimeter / 360))
            elif unit == 1:  # miles
                self.radius = float((value / (earth_perimeter / 360)) / 0.62138)
            else:  # degrees
                self.radius = float(value)
            self.radius = self.radius / 2

    def apply(self, dummy_db, place):
        if self.handle is None:
            return False
        if self.latitude is None:
            return False
        if self.longitude is None:
            return False
        if place:
            lat = place.get_latitude()
            lon = place.get_longitude()
        if lat and lon:
            latit, longit = conv_lat_lon(lat, lon, "D.D8")
            if latit is None or longit is None:
                return False
            if (
                hypot(
                    float(self.latitude) - float(latit),
                    float(self.longitude) - float(longit),
                )
                <= self.radius
            ):
                return True
        return False
