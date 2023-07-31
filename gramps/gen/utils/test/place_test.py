#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  B. Malengier
# Copyright (C) 2009  Swoon on bug tracker
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
# Standard python modules
#
# -------------------------------------------------------------------------
import unittest
import math

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..place import conv_lat_lon


# -------------------------------------------------------------------------
#
# PlaceTest class
#
# -------------------------------------------------------------------------
class PlaceTest(unittest.TestCase):
    def _test_formats_success(self, lat, lon):
        for format_ in ["D.D4", "D.D8", "DEG", "DEG-:", "RT90", "GEDCOM"]:
            res1, res2 = conv_lat_lon(lat, lon, format_)
            self.assertIsNotNone(res1, "Failed for %s %s" % (lat, lon))
            self.assertIsNotNone(res2, "Failed for %s %s" % (lat, lon))

        for format_ in ["ISO-D", "ISO-DM", "ISO-DMS"]:
            res = conv_lat_lon(lat, lon, format_)
            self.assertIsNotNone(res, "Failed for %s %s" % (lat, lon))

    def _test_formats_fail(self, lat, lon):
        res1, res2 = conv_lat_lon(lat, lon)
        self.assertIsNone(res1, "Expected failure for %s %s" % (lat, lon))
        self.assertIsNone(res2, "Expected failure for %s %s" % (lat, lon))

    def test_decimal(self):
        lat, lon = "50.849888888888", "2.885897222222"
        self._test_formats_success(lat, lon)

    def test_dms(self):
        lat, lon = " 50°50'59.60\"N", "  2°53'9.23\"E"
        self._test_formats_success(lat, lon)

    def test_colon(self):
        lat, lon = " 50 : 50 : 59.60 ", " -2:53 : 9.23   "
        self._test_formats_success(lat, lon)

        lat, lon = "+50:1", "-2:1:2"
        self._test_formats_success(lat, lon)

    def test_bad_latitude(self):
        lat, lon = " dummy", "  2#53 ' 9.23  \"  E "
        self._test_formats_fail(lat, lon)

    def test_bad_longitude(self):
        lat, lon = " 50:50: 59.60", "  d u m my"
        self._test_formats_fail(lat, lon)

    def test_dm_ds(self):
        lat, lon = " 50°59.60'N", "  2°53'E"
        self._test_formats_success(lat, lon)

    def test_both_in_latitude(self):
        lat, lon = " 11° 11' 11\" N, 11° 11' 11\" O", " "
        self._test_formats_fail(lat, lon)

    def test_very_small_negative(self):
        lat, lon = "-0.00006", "-0.00006"
        self._test_formats_success(lat, lon)

    def test_missing_direction(self):
        lat, lon = ' 50°59.60"', "  2°53'E"
        self._test_formats_fail(lat, lon)

    def test_wrong_direction(self):
        lat, lon = ' 50°59.60"E', "  2°53'N"
        self._test_formats_fail(lat, lon)

        lat, lon = ' 50°59.99"E', "  2°59'59.99\"N"
        self._test_formats_fail(lat, lon)

    def test_precision(self):
        lat, lon = " 50°59'59.99\"S", "  2°59'59.99\"E"
        self._test_formats_success(lat, lon)

        lat, lon = "N50.849888888888", "E2.885897222222"
        self._test_formats_success(lat, lon)

    def test_large_latitude(self):
        lat, lon = "90.849888888888", "2.885897222222"
        self._test_formats_fail(lat, lon)

        lat, lon = "-91.2", "-1"
        self._test_formats_fail(lat, lon)

    def test_extreme_values(self):
        lat, lon = "90", "-180"
        self._test_formats_success(lat, lon)

        lat, lon = "90° 00' 00.00\" S ", "179° 59'59.99\"W"
        self._test_formats_success(lat, lon)

        lat, lon = "90° 00' 00.00\" N", "180° 00'00.00\" E"
        self._test_formats_fail(lat, lon)

        lat, lon = "90: 00: 00.00 ", "-179: 59:59.99"
        self._test_formats_success(lat, lon)

        lat, lon = "90° 00' 00.00\" N", "180:00:00.00"
        self._test_formats_fail(lat, lon)

        lat, lon = "90", "180"
        self._test_formats_fail(lat, lon)

        lat, lon = " 89°59'60\"N", "  2°53'W"
        self._test_formats_fail(lat, lon)

        lat, lon = " 89°60'00\"N", "  2°53'W"
        self._test_formats_fail(lat, lon)

        lat, lon = " 89.1°40'00\"N", "  2°53'W"
        self._test_formats_fail(lat, lon)

        lat, lon = " 89°40'00\"N", "  2°53.1'W"
        self._test_formats_success(lat, lon)

        lat, lon = "+61° 43' 60.00\"", "+17° 7' 60.00\""
        self._test_formats_fail(lat, lon)

    def test_zero_crossing(self):
        lat, lon = "0", "0"
        self._test_formats_success(lat, lon)

    def test_near_equator(self):
        lat, lon = ' 1°1"N', "  1°1'E"
        self._test_formats_success(lat, lon)

    def test_roundoff(self):
        lat, lon = " 1°59.999'N", "  1°59.999'E"
        self._test_formats_success(lat, lon)

        lat, lon = " 1°59'59.9999\"N", "  1°59'59.9999\"E"
        self._test_formats_success(lat, lon)

        lat, lon = "89°59'59.9999\"S", "179°59'59.9999\"W"
        self._test_formats_success(lat, lon)

        lat, lon = "89°59'59.9999\"N", "179°59'59.9999\"E"
        self._test_formats_success(lat, lon)

    def test_number_of_decimals(self):
        lat, lon = "89°59'59.99999999\"N", "179°59'59.99999999\"E"
        self._test_formats_success(lat, lon)

    def test_quote_notation(self):
        lat, lon = "89°59'59.99'' N", "179°59'59.99''E"
        self._test_formats_success(lat, lon)

    def test_decimal_localization(self):
        lat, lon = "50.849888888888", "2,885897222222"
        self._test_formats_fail(lat, lon)

        lat, lon = "89°59'59.9999\"S", "179°59'59,9999\"W"
        self._test_formats_fail(lat, lon)

        lat, lon = "89°59'1.599,999\"S", "179°59'59,9999\"W"
        self._test_formats_fail(lat, lon)

    def test_large_longitude(self):
        lat, lon = "81.2", "-182.3"
        self._test_formats_fail(lat, lon)

    def test_bad_sign(self):
        lat, lon = "++50:10:1", "2:1:2"
        self._test_formats_fail(lat, lon)

        lat, lon = "-50:10:1", "-+2:1:2"
        self._test_formats_fail(lat, lon)

    def test_missing_minute(self):
        lat, lon = "-50::1", "-2:1:2"
        self._test_formats_fail(lat, lon)

        lat, lon = "+50:", "-2:1:2"
        self._test_formats_fail(lat, lon)

    def test_extra_whitespace(self):
        lat, lon = "- 50  : 2 : 1 ", "-2:1:2"
        self._test_formats_success(lat, lon)

        lat, lon = "+ 50:2 :  1", "-2:1:2"
        self._test_formats_success(lat, lon)

    def test_sign_and_direction(self):
        lat, lon = "+61° 44' 00.00\"N", "+17° 8' 00.00\"E"
        self._test_formats_success(lat, lon)

    def test_extra_colon(self):
        lat, lon = "+50: 0 : 1 : 1", "-2:1:2"
        self._test_formats_fail(lat, lon)

    def test_leading_colon(self):
        lat, lon = ": 0 : 1 : 1", ":1:2"
        self._test_formats_fail(lat, lon)

    def test_degree_symbol(self):
        lat, lon = "N 50º52'21.92\"", "E 124º52'21.92\""
        self._test_formats_success(lat, lon)

        lat, lon = "S 50º52'21.92\"", "W 124º52'21.92\""
        self._test_formats_success(lat, lon)

    def test_RT90_conversion(self):
        """A given lat/lon is converted to RT90 and back"""
        x, y = conv_lat_lon("59:40:9.09", "12:58:57.74", "RT90")
        lat, lon = conv_SWED_RT90_WGS84(float(x), float(y))

        expetced_lat = 59.0 + 40.0 / 60.0 + 9.09 / 3600.0
        expetced_lon = 12.0 + 58.0 / 60.0 + 57.74 / 3600.0

        self.assertAlmostEqual(lat, expetced_lat, places=3)
        self.assertAlmostEqual(lon, expetced_lon, places=3)


def conv_SWED_RT90_WGS84(X, Y):
    """
    Input is X and Y coordinates in RT90 as float
    Output is lat and long in degrees, float as tuple
    """
    # Some constants used for conversion to/from Swedish RT90
    f = 1.0 / 298.257222101
    e2 = f * (2.0 - f)
    n = f / (2.0 - f)
    L0 = math.radians(15.8062845294)  # 15 deg 48 min 22.624306 sec
    k0 = 1.00000561024
    a = 6378137.0  # meter
    at = a / (1.0 + n) * (1.0 + 1.0 / 4.0 * pow(n, 2) + 1.0 / 64.0 * pow(n, 4))
    FN = -667.711  # m
    FE = 1500064.274  # m

    xi = (X - FN) / (k0 * at)
    eta = (Y - FE) / (k0 * at)
    D1 = (
        1.0 / 2.0 * n
        - 2.0 / 3.0 * pow(n, 2)
        + 37.0 / 96.0 * pow(n, 3)
        - 1.0 / 360.0 * pow(n, 4)
    )
    D2 = 1.0 / 48.0 * pow(n, 2) + 1.0 / 15.0 * pow(n, 3) - 437.0 / 1440.0 * pow(n, 4)
    D3 = 17.0 / 480.0 * pow(n, 3) - 37.0 / 840.0 * pow(n, 4)
    D4 = 4397.0 / 161280.0 * pow(n, 4)
    xip = (
        xi
        - D1 * math.sin(2.0 * xi) * math.cosh(2.0 * eta)
        - D2 * math.sin(4.0 * xi) * math.cosh(4.0 * eta)
        - D3 * math.sin(6.0 * xi) * math.cosh(6.0 * eta)
        - D4 * math.sin(8.0 * xi) * math.cosh(8.0 * eta)
    )
    etap = (
        eta
        - D1 * math.cos(2.0 * xi) * math.sinh(2.0 * eta)
        - D2 * math.cos(4.0 * xi) * math.sinh(4.0 * eta)
        - D3 * math.cos(6.0 * xi) * math.sinh(6.0 * eta)
        - D4 * math.cos(8.0 * xi) * math.sinh(8.0 * eta)
    )
    psi = math.asin(math.sin(xip) / math.cosh(etap))
    DL = math.atan2(math.sinh(etap), math.cos(xip))
    LON = L0 + DL
    A = e2 + pow(e2, 2) + pow(e2, 3) + pow(e2, 4)
    B = -1.0 / 6.0 * (7.0 * pow(e2, 2) + 17 * pow(e2, 3) + 30 * pow(e2, 4))
    C = 1.0 / 120.0 * (224.0 * pow(e2, 3) + 889.0 * pow(e2, 4))
    D = 1.0 / 1260.0 * (4279.0 * pow(e2, 4))
    E = (
        A
        + B * pow(math.sin(psi), 2)
        + C * pow(math.sin(psi), 4)
        + D * pow(math.sin(psi), 6)
    )
    LAT = psi + math.sin(psi) * math.cos(psi) * E
    LAT = math.degrees(LAT)
    LON = math.degrees(LON)
    return LAT, LON


if __name__ == "__main__":
    unittest.main()
