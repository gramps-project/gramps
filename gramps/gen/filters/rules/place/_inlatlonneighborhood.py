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
# gen.filters.rules/Place/_InLatLonNeighborhood.py


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
from ....utils.place import conv_lat_lon


# -------------------------------------------------------------------------
#
# InLatLonNeighborhood
#
# -------------------------------------------------------------------------
class InLatLonNeighborhood(Rule):
    """Rule that checks if a place is in the neighborhood of a given
    Latitude or Longitude or"""

    labels = [
        _("Latitude:"),
        _("Longitude:"),
        _("Rectangle height:"),
        _("Rectangle width:"),
    ]
    name = _("Places in neighborhood of given position")
    description = _(
        "Matches places with latitude or longitude positioned in "
        "a rectangle of given height and width (in degrees), and "
        "with middlepoint the given latitude and longitude."
    )
    category = _("Position filters")

    def prepare(self, db, user):
        if self.list[0]:
            try:
                self.halfheight = float(self.list[2]) / 2.0
            except ValueError:
                self.halfheight = None
            if self.halfheight is not None and self.halfheight <= 0.0:
                self.halfheight = None
        else:
            self.halfheight = -1
            # give dummy value
            self.list[0] = "0.0"

        if self.list[1]:
            try:
                self.halfwidth = float(self.list[3]) / 2.0
            except ValueError:
                self.halfwidth = None
            if self.halfwidth is not None and self.halfwidth <= 0.0:
                self.halfwidth = None
        else:
            self.halfwidth = -1
            # give dummy value
            self.list[1] = "0.0"

        # we allow a band instead of a triangle
        self.lat, self.lon = conv_lat_lon(self.list[0], self.list[1], "D.D8")
        if self.lat is not None and self.lon is not None:
            self.lat = float(self.lat)
            self.lon = float(self.lon)
        else:
            self.lat = None
            self.lon = None

        # we define the two squares we must look in
        #    can be 0, so check on None
        if (
            self.lat is not None
            and self.halfheight is not None
            and self.halfheight != -1
        ):
            self.S = self.lat + self.halfheight
            if self.S > 90.0:
                self.S = 90.0
            self.N = self.lat - self.halfheight
            if self.N < -90.0:
                self.N = -90.0
        self.doublesquares = False
        if self.lon is not None and self.halfwidth is not None and self.halfwidth != -1:
            if self.halfwidth >= 180.0:
                # the entire longitude is allowed, reset values
                self.lon = 0.0
                self.E = 180.0
                self.W = -180.0
            else:
                self.E = self.lon + self.halfwidth
                self.W = self.lon - self.halfwidth
                if self.E > 180.0:
                    # we need to check in two squares:
                    self.doublesquares = True
                    self.E2 = self.E - 360.0
                    self.W2 = -180.0
                    self.E = 180
                if self.W < -180.0:
                    # we need to check in two squares:
                    self.doublesquares = True
                    self.W2 = self.W + 360.0
                    self.E2 = 180.0
                    self.W = -180

    def apply(self, db, place):
        if self.halfheight == -1 and self.halfwidth == -1:
            return False

        # when given, must be valid
        if self.lat is None or self.lon is None:
            return False

        # if height/width given, they must be valid
        if self.halfheight is None or self.halfwidth is None:
            return False

        # now we know at least one is given in the filter and is valid

        # the place we look at must have lat AND lon entered
        if not (place.get_latitude().strip and place.get_longitude().strip()):
            return False

        latpl, lonpl = conv_lat_lon(place.get_latitude(), place.get_longitude(), "D.D8")
        if latpl and lonpl:
            latpl = float(latpl)
            lonpl = float(lonpl)
            if self.halfheight != -1:
                # check lat
                if latpl < self.N or latpl > self.S:
                    return False

            if self.halfwidth != -1:
                # check lon: more difficult, we may cross the 180/-180 boundary
                # and must keep counting
                if self.doublesquares:
                    # two squares to look in :
                    if (lonpl < self.W or lonpl > self.E) and (
                        lonpl < self.W2 or lonpl > self.E2
                    ):
                        return False
                elif lonpl < self.W or lonpl > self.E:
                    return False

            return True

        return False
