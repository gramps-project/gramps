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
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
import math

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
#
# begin localisation part
#
# -------------------------------------------------------------------------

# translation of N/S/E/W, make sure translator understands
degrees = "1"
North = _("%(north_latitude)s N") % {"north_latitude": degrees}
South = _("%(south_latitude)s S") % {"south_latitude": degrees}
East = _("%(east_longitude)s E") % {"east_longitude": degrees}
West = _("%(west_longitude)s W") % {"west_longitude": degrees}

# extract letters we really need
North = North.replace("1", " ").strip()
South = South.replace("1", " ").strip()
East = East.replace("1", " ").strip()
West = West.replace("1", " ").strip()

# build dictionary with translation en to local language
translate_en_loc = {}
translate_en_loc["N"] = North
translate_en_loc["S"] = South
translate_en_loc["E"] = East
translate_en_loc["W"] = West

# keep translation only if it does not conflict with english
if "N" == South or "S" == North or "E" == West or "W" == East:
    translate_en_loc["N"] = "N"
    translate_en_loc["S"] = "S"
    translate_en_loc["E"] = "E"
    translate_en_loc["W"] = "W"
# end localisation part


def _T_(value, context=""):  # enable deferred translations
    return "%s\x04%s" % (context, value) if context else value


coord_formats = (
    # format #0 'DEG'       degree, minutes, seconds notation
    _T_("DEG"),
    # format #1 'DEG-:'     degree, minutes, seconds notation with :
    _T_("DEG-:"),
    # format #2 'D.D4'      degree notation, 4 decimals
    _T_("D.D4"),
    # format #3 'D.D8'      degree notation, 8 decimals (precision like ISO-DMS)
    _T_("D.D8"),
    # format #4 'RT90'      Output format for the Swedish coordinate system RT90
    _T_("RT90"),
    # output display not implemented for the following formats:
    # 'ISO-D'     ISO 6709 degree notation i.e. ±DD.DDDD±DDD.DDDD
    # 'ISO-DM'    ISO 6709 degree, minutes notation
    # 'ISO-DMS'   ISO 6709 degree, minutes, seconds notation
)

coord_formats_desc = (
    _("Degree, minutes, seconds notation"),
    _("Degree, minutes, seconds notation with :"),
    _("Degree notation, 4 decimals"),
    _("Degree notation, 8 decimals (precision like ISO-DMS)"),
    _("Output format for the Swedish coordinate system RT90"),
)

# ------------------
#
# helper functions
#
# ------------------


def __convert_structure_to_float(sign, degs, mins=0, secs=0.0):
    """helper function which converts a structure to a nice
    representation
    """
    v = float(degs)
    if mins is not None:
        v += float(mins) / 60.0
    if secs is not None:
        v += secs / 3600.0
    return -v if sign == "-" else v


def __convert_using_float_repr(stringValue):
    """helper function that tries to convert the string using the float
    representation
    """
    try:
        v = float(stringValue)
        return v
    except ValueError:
        return None


def __convert_using_colon_repr(stringValue):
    """helper function that tries to convert the string using the colon
    representation
    """
    if stringValue.find(r":") == -1:
        return None

    l = stringValue.split(":")
    if len(l) < 2 or len(l) > 3:
        return None
    l[0] = l[0].strip()
    # if no characters before ':' nothing useful is input!
    if len(l[0]) == 0:
        return None
    if l[0][0] in ["+", "-"]:
        sign = l[0][0]
        l[0] = l[0][1:].strip()
        # regard a second sign as an error
        if l[0][0] in ["+", "-"]:
            return None
    else:
        sign = "+"
    try:
        degs = int(l[0])
        if degs < 0:
            return None
    except:
        return None
    try:
        mins = int(l[1])
        if mins < 0 or mins >= 60:
            return None
    except:
        return None
    secs = 0.0
    if len(l) == 3:
        try:
            secs = float(l[2])
            if secs < 0.0 or secs >= 60.0:
                return None
        except:
            return None

    return __convert_structure_to_float(sign, degs, mins, secs)


def __convert_using_classic_repr(stringValue, typedeg):
    """helper function that tries to convert the string using the colon
    representation
    """
    if stringValue.find(r"_") != -1:
        return None  # not a valid lat or lon

    # exchange some characters
    stringValue = stringValue.replace("°", r"_")
    # allow to input ° as #, UTF-8 code c2b00a
    stringValue = stringValue.replace("º", r"_")
    # allow to input º as #, UTF-8 code c2b a0a
    stringValue = stringValue.replace(r"#", r"_")
    # allow to input " as ''
    stringValue = stringValue.replace(r"''", r'"')
    # allow some special unicode symbols
    stringValue = stringValue.replace("\u2033", r'"')
    stringValue = stringValue.replace("\u2032", r"'")
    # ignore spaces, a regex with \s* would be better here...
    stringValue = stringValue.replace(r" ", r"")
    stringValue = stringValue.replace(r"\t", r"")

    # get the degrees, must be present
    if stringValue.find(r"_") == -1:
        return None
    l = stringValue.split(r"_")
    if len(l) != 2:
        return None

    try:
        degs = int(l[0])  # degrees must be integer value
        if degs < 0:
            return None
    except:
        return None
    # next: minutes might be present once
    l2 = l[1].split(r"'")
    l3 = l2
    mins = 0
    # See if minutes might be decimal?
    # Then no seconds is supposed to be given
    if l2[0].find(r".") > 0:
        # Split in integer and decimal parts
        l4 = l2[0].split(r".")
        # Set integer minutes
        l2[0] = l4[0]
        # Convert the decimal part of minutes to seconds
        try:
            lsecs = float("0." + l4[1]) * 60.0
            # Set the seconds followed by direction letter N/S/W/E
            l2[1] = str(lsecs) + '"' + l2[1]
        except:
            return None

    if len(l2) > 2:
        return None
    if len(l2) == 2:
        l3 = [
            l2[1],
        ]
        try:
            mins = int(l2[0])  # minutes must be integer value
            if mins < 0 or mins >= 60:
                return None
        except:
            return None
    # next: seconds might be present once
    l3 = l3[0].split(r'"')
    last = l3[0]
    secs = 0.0
    if len(l3) > 2:
        return None
    if len(l3) == 2:
        last = l3[1]
        try:
            secs = float(l3[0])
            if secs < 0.0 or secs >= 60.0:
                return None
        except:
            return None
    # last entry should be the direction
    if typedeg == "lat":
        if last == "N":
            sign = "+"
        elif last == "S":
            sign = "-"
        else:
            return None
    elif typedeg == "lon":
        if last == "E":
            sign = "+"
        elif last == "W":
            sign = "-"
        else:
            return None
    else:
        return None

    return __convert_structure_to_float(sign, degs, mins, secs)


def __convert_using_modgedcom_repr(val, typedeg):
    """helper function that tries to convert the string using the
    modified GEDCOM representation where direction [NSEW] is appended
    instead of prepended. This particular representation is the result
    of value normalization done on values passed to this function
    """
    if typedeg == "lat":
        pos = val.find("N")
        if pos >= 0:
            stringValue = val[:pos]
        else:
            pos = val.find("S")
            if pos >= 0:
                stringValue = "-" + val[:pos]
            else:
                return None
    else:
        pos = val.find("E")
        if pos >= 0:
            stringValue = val[:pos]
        else:
            pos = val.find("W")
            if pos >= 0:
                stringValue = "-" + val[:pos]
            else:
                return None
    try:
        v = float(stringValue)
        return v
    except ValueError:
        return None


def __convert_float_val(val, typedeg="lat"):
    # function converting input to float, recognizing decimal input, or
    # degree notation input. Only english input
    # There is no check on maximum/minimum of degree
    # In case of degree minutes seconds direction input,
    # it is checked that degree >0, 0<= minutes <= 60,
    # 0<= seconds <= 60, direction is in the directions dic.

    # format: XX.YYYY
    v = __convert_using_float_repr(val)
    if v is not None:
        return v

    # format: XX:YY:ZZ
    v = __convert_using_colon_repr(val)
    if v is not None:
        return v

    # format: XX° YY' ZZ" [NSWE]
    v = __convert_using_classic_repr(val, typedeg)
    if v is not None:
        return v

    # format XX.YYYY[NSWE]
    v = __convert_using_modgedcom_repr(val, typedeg)
    if v is not None:
        return v

    # no format succeeded
    return None


# -------------------------------------------------------------------------
#
# conversion function
#
# -------------------------------------------------------------------------


def conv_lat_lon(latitude, longitude, format="D.D4"):
    """
    Convert given string latitude and longitude to a required format.

    :param latitude: Latitude
    :type latitude: string
    :param longitude: Longitude
    :type longitude: string
    :param format: Ouput format
    :type format: string
    :returns: a tuple of 2 strings, or a string (for ISO formats). If
              conversion fails: returns: (None, None)  or None (for ISO formats)

    Possible formats:

    =========   ============================================================
    Format      Description
    =========   ============================================================
    'D.D4'      degree notation, 4 decimals
                eg +12.0154 , -124.3647
    'D.D8'      degree notation, 8 decimals (precision like ISO-DMS)
                eg +12.01543265 , -124.36473268
    'DEG'       degree, minutes, seconds notation
                eg 50°52'21.92''N , 124°52'21.92''E ° has UTF-8 code c2b00a
                or N50º52'21.92" , E14º52'21.92"   º has UTF-8 code c2ba0a
                or N50º52.3456' , E14º52.9876' ; decimal minutes, no seconds
    'DEG-:'     degree, minutes, seconds notation with :
                eg -50:52:21.92 , 124:52:21.92
    'ISO-D'     ISO 6709 degree notation i.e. ±DD.DDDD±DDD.DDDD
    'ISO-DM'    ISO 6709 degree, minutes notation
                i.e. ±DDMM.MMM±DDDMM.MMM
    'ISO-DMS'   ISO 6709 degree, minutes, seconds notation
                i.e. ±DDMMSS.SS±DDDMMSS.SS
    'RT90'      Output format for the Swedish coordinate system RT90
    =========   ============================================================

    Some generalities:

    * -90 <= latitude <= +90 with +00 the equator
    * -180 <= longitude < +180 with +000 prime meridian and -180 the 180th
      meridian
    """

    # we start the function changing latitude/longitude in english
    if latitude.find("N") == -1 and latitude.find("S") == -1:
        # entry is not in english, convert to english
        latitude = latitude.replace(translate_en_loc["N"], "N")
        latitude = latitude.replace(translate_en_loc["S"], "S")
    if longitude.find("E") == -1 and longitude.find("W") == -1:
        # entry is not in english, convert to english
        longitude = longitude.replace(translate_en_loc["W"], "W")
        longitude = longitude.replace(translate_en_loc["E"], "E")

    # take away leading spaces
    latitude = latitude.lstrip()
    longitude = longitude.lstrip()
    # check if first character is alpha i.e. N or S, put it last
    if len(latitude) > 1 and latitude[0].isalpha():
        latitude = latitude[1:] + latitude[0]
    # check if first character is alpha i.e. E or W, put it last
    if len(longitude) > 1 and longitude[0].isalpha():
        longitude = longitude[1:] + longitude[0]

    # convert to float
    lat_float = __convert_float_val(latitude, "lat")
    lon_float = __convert_float_val(longitude, "lon")

    # give output (localized if needed)
    if lat_float is None or lon_float is None:
        if format == "ISO-D" or format == "ISO-DM" or format == "ISO-DMS":
            return None
        else:
            return (None, None)
    if (
        lat_float > 90.0
        or lat_float < -90.0
        or lon_float >= 180.0
        or lon_float < -180.0
    ):
        if format == "ISO-D" or format == "ISO-DM" or format == "ISO-DMS":
            return None
        else:
            return (None, None)

    if format == "D.D4":
        # correct possible roundoff error
        str_lon = "%.4f" % (lon_float)
        if str_lon == "180.0000":
            str_lon = "-180.0000"
        return ("%.4f" % lat_float, str_lon)

    if format == "D.D8" or format == "RT90":
        # correct possible roundoff error
        str_lon = "%.8f" % (lon_float)
        if str_lon == "180.00000000":
            str_lon = "-180.00000000"
        if format == "RT90":
            tx = __conv_WGS84_SWED_RT90(lat_float, lon_float)
            return ("%i" % tx[0], "%i" % tx[1])
        else:
            return ("%.8f" % lat_float, str_lon)

    if format == "GEDCOM":
        # The 5.5.1 spec is inconsistent.  Length is supposedly 5 to 8 chars,
        # but the sample values are longer, using up to 6 fraction digits.
        # As a compromise, we will produce up to 6 fraction digits, but only
        # if necessary
        # correct possible roundoff error
        if lon_float >= 0:
            str_lon = "%.6f" % (lon_float)
            if str_lon == "180.000000":
                str_lon = "W180.000000"
            else:
                str_lon = "E" + str_lon
        else:
            str_lon = "W" + "%.6f" % (-lon_float)
        str_lon = str_lon[:-5] + str_lon[-5:].rstrip("0")
        str_lat = "%s%.6f" % (("N", lat_float) if lat_float >= 0 else ("S", -lat_float))
        str_lat = str_lat[:-5] + str_lat[-5:].rstrip("0")
        return (str_lat, str_lon)

    deg_lat = int(lat_float)
    deg_lon = int(lon_float)
    min_lat = int(60.0 * (lat_float - float(deg_lat)))
    min_lon = int(60.0 * (lon_float - float(deg_lon)))
    sec_lat = 3600.0 * (lat_float - float(deg_lat) - float(min_lat) / 60.0)
    sec_lon = 3600.0 * (lon_float - float(deg_lon) - float(min_lon) / 60.0)

    # dump minus sign on all, store minus sign. Carefull: int(-0.8)=0 !!
    if (deg_lat) < 0:
        deg_lat = -1 * deg_lat
    if (min_lat) < 0:
        min_lat = -1 * min_lat
    if (sec_lat) < 0.0:
        sec_lat = -1.0 * sec_lat
    if (deg_lon) < 0:
        deg_lon = -1 * deg_lon
    if (min_lon) < 0:
        min_lon = -1 * min_lon
    if (sec_lon) < 0.0:
        sec_lon = -1.0 * sec_lon
    # keep sign as -1* 0 = +0, so 0°2'S is given correct sign in ISO
    sign_lat = "+"
    dir_lat = ""
    if lat_float >= 0.0:
        dir_lat = translate_en_loc["N"]
    else:
        dir_lat = translate_en_loc["S"]
        sign_lat = "-"
    sign_lon = "+"
    dir_lon = ""
    if lon_float >= 0.0:
        dir_lon = translate_en_loc["E"]
    else:
        dir_lon = translate_en_loc["W"]
        sign_lon = "-"

    if format == "DEG":
        str_lat = ("%d°%02d'%05.2f\"" % (deg_lat, min_lat, sec_lat)) + dir_lat
        str_lon = ("%d°%02d'%05.2f\"" % (deg_lon, min_lon, sec_lon)) + dir_lon
        # correct possible roundoff error in seconds
        if str_lat[-6 - len(dir_lat)] == "6":
            if min_lat == 59:
                str_lat = ("%d°%02d'%05.2f\"" % (deg_lat + 1, 0, 0.0)) + dir_lat
            else:
                str_lat = ("%d°%02d'%05.2f\"" % (deg_lat, min_lat + 1, 0.0)) + dir_lat
        if str_lon[-6 - len(dir_lon)] == "6":
            if min_lon == 59:
                if deg_lon == 179 and sign_lon == "+":
                    str_lon = ("%d°%02d'%05.2f\"" % (180, 0, 0.0)) + translate_en_loc[
                        "W"
                    ]
                else:
                    str_lon = ("%d°%02d'%05.2f\"" % (deg_lon + 1, 0, 0.0)) + dir_lon
            else:
                str_lon = ("%d°%02d'%05.2f\"" % (deg_lon, min_lon + 1, 0.0)) + dir_lon

        return (str_lat, str_lon)

    if format == "DEG-:":
        if sign_lat == "+":
            sign_lat = ""
        sign_lon_h = sign_lon
        if sign_lon == "+":
            sign_lon_h = ""
        str_lat = sign_lat + ("%d:%02d:%05.2f" % (deg_lat, min_lat, sec_lat))
        str_lon = sign_lon_h + ("%d:%02d:%05.2f" % (deg_lon, min_lon, sec_lon))

        # correct possible roundoff error in seconds

        if str_lat[-5] == "6":
            if min_lat == 59:
                str_lat = sign_lat + ("%d:%02d:%05.2f" % (deg_lat + 1, 0, 0.0))
            else:
                str_lat = sign_lat + ("%d:%02d:%05.2f" % (deg_lat, min_lat + 1, 0.0))
        if str_lon[-5] == "6":
            if min_lon == 59:
                if deg_lon == 179 and sign_lon == "+":
                    str_lon = "-" + ("%d:%02d:%05.2f" % (180, 0, 0.0))
                else:
                    str_lon = sign_lon_h + ("%d:%02d:%05.2f" % (deg_lon + 1, 0, 0.0))
            else:
                str_lon = sign_lon_h + ("%d:%02d:%05.2f" % (deg_lon, min_lon + 1, 0.0))

        return (str_lat, str_lon)

    if format == "ISO-D":  # ±DD.DDDD±DDD.DDDD
        str_lon = "%+09.4f" % (lon_float)
        # correct possible roundoff error
        if str_lon == "+180.0000":
            str_lon = "-180.0000"
        return ("%+08.4f" % lat_float) + str_lon

    if format == "ISO-DM":  # ±DDMM.MMM±DDDMM.MMM
        min_fl_lat = float(min_lat) + sec_lat / 60.0
        min_fl_lon = float(min_lon) + sec_lon / 60.0
        str_lat = sign_lat + ("%02d%06.3f" % (deg_lat, min_fl_lat))
        str_lon = sign_lon + ("%03d%06.3f" % (deg_lon, min_fl_lon))
        # correct possible roundoff error
        if str_lat[3:] == "60.000":
            str_lat = sign_lat + ("%02d%06.3f" % (deg_lat + 1, 0.0))
        if str_lon[4:] == "60.000":
            if deg_lon == 179 and sign_lon == "+":
                str_lon = "-" + ("%03d%06.3f" % (180, 0.0))
            else:
                str_lon = sign_lon + ("%03d%06.3f" % (deg_lon + 1, 0.0))
        return str_lat + str_lon

    if format == "ISO-DMS":  # ±DDMMSS.SS±DDDMMSS.SS
        str_lat = sign_lat + ("%02d%02d%06.3f" % (deg_lat, min_lat, sec_lat))
        str_lon = sign_lon + ("%03d%02d%06.3f" % (deg_lon, min_lon, sec_lon))
        # correct possible roundoff error
        if str_lat[5:] == "60.000":
            if min_lat == 59:
                str_lat = sign_lat + ("%02d%02d%06.3f" % (deg_lat + 1, 0, 0.0))
            else:
                str_lat = sign_lat + ("%02d%02d%06.3f" % (deg_lat, min_lat + 1, 0.0))
        if str_lon[6:] == "60.000":
            if min_lon == 59:
                if deg_lon == 179 and sign_lon == "+":
                    str_lon = "-" + ("%03d%02d%06.3f" % (180, 0, 0))
                else:
                    str_lon = sign_lon + ("%03d%02d%06.3f" % (deg_lon + 1, 0, 0.0))
            else:
                str_lon = sign_lon + ("%03d%02d%06.3f" % (deg_lon, min_lon + 1, 0.0))
        return str_lat + str_lon


def atanh(x):
    """arctangent hyperbolicus"""
    return 1.0 / 2.0 * math.log((1.0 + x) / (1.0 - x))


def __conv_WGS84_SWED_RT90(lat, lon):
    """
    Input is lat and lon as two float numbers
    Output is X and Y coordinates in RT90
    as a tuple of float numbers

    The code below converts to/from the Swedish RT90 koordinate
    system. The converion functions use "Gauss Conformal Projection
    (Transverse Marcator)" Krüger Formulas.
    The constanst are for the Swedish RT90-system.
    With other constants the conversion should be useful for
    other geographical areas.

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

    # the conversion
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    A = e2
    B = 1.0 / 6.0 * (5.0 * pow(e2, 2) - pow(e2, 3))
    C = 1.0 / 120.0 * (104.0 * pow(e2, 3) - 45.0 * pow(e2, 4))
    D = 1.0 / 1260.0 * (1237.0 * pow(e2, 4))
    DL = lon_rad - L0
    E = (
        A
        + B * pow(math.sin(lat_rad), 2)
        + C * pow(math.sin(lat_rad), 4)
        + D * pow(math.sin(lat_rad), 6)
    )
    psi = lat_rad - math.sin(lat_rad) * math.cos(lat_rad) * E
    xi = math.atan2(math.tan(psi), math.cos(DL))
    eta = atanh(math.cos(psi) * math.sin(DL))
    B1 = (
        1.0 / 2.0 * n
        - 2.0 / 3.0 * pow(n, 2)
        + 5.0 / 16.0 * pow(n, 3)
        + 41.0 / 180.0 * pow(n, 4)
    )
    B2 = 13.0 / 48.0 * pow(n, 2) - 3.0 / 5.0 * pow(n, 3) + 557.0 / 1440.0 * pow(n, 4)
    B3 = 61.0 / 240.0 * pow(n, 3) - 103.0 / 140.0 * pow(n, 4)
    B4 = 49561.0 / 161280.0 * pow(n, 4)
    X = (
        xi
        + B1 * math.sin(2.0 * xi) * math.cosh(2.0 * eta)
        + B2 * math.sin(4.0 * xi) * math.cosh(4.0 * eta)
        + B3 * math.sin(6.0 * xi) * math.cosh(6.0 * eta)
        + B4 * math.sin(8.0 * xi) * math.cosh(8.0 * eta)
    )
    Y = (
        eta
        + B1 * math.cos(2.0 * xi) * math.sinh(2.0 * eta)
        + B2 * math.cos(4.0 * xi) * math.sinh(4.0 * eta)
        + B3 * math.cos(6.0 * xi) * math.sinh(6.0 * eta)
        + B4 * math.cos(8.0 * xi) * math.sinh(8.0 * eta)
    )
    X = X * k0 * at + FN
    Y = Y * k0 * at + FE
    return (X, Y)


def __conv_SWED_RT90_WGS84(X, Y):
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


# -------------------------------------------------------------------------
#
# For Testing the convert function in this module, apply it as a script:
#     ==> in command line do "python PlaceUtils.py"
#
# -------------------------------------------------------------------------

if __name__ == "__main__":

    def test_formats_success(lat1, lon1, text=""):
        format0 = "D.D4"
        format1 = "D.D8"
        format2 = "DEG"
        format3 = "DEG-:"
        format4 = "ISO-D"
        format5 = "ISO-DM"
        format6 = "ISO-DMS"
        format7 = "RT90"
        format8 = "GEDCOM"
        print("Testing conv_lat_lon function, " + text + ":")
        res1, res2 = conv_lat_lon(lat1, lon1, format0)
        print(lat1, lon1, "in format", format0, "is   ", res1, res2)
        res1, res2 = conv_lat_lon(lat1, lon1, format1)
        print(lat1, lon1, "in format", format1, "is   ", res1, res2)
        res1, res2 = conv_lat_lon(lat1, lon1, format2)
        print(lat1, lon1, "in format", format2, "is    ", res1, res2)
        res1, res2 = conv_lat_lon(lat1, lon1, format3)
        print(lat1, lon1, "in format", format3, "is  ", res1, res2)
        res = conv_lat_lon(lat1, lon1, format4)
        print(lat1, lon1, "in format", format4, "is ", res)
        res = conv_lat_lon(lat1, lon1, format5)
        print(lat1, lon1, "in format", format5, "is", res)
        res = conv_lat_lon(lat1, lon1, format6)
        print(lat1, lon1, "in format", format6, "is", res)
        res1, res2 = conv_lat_lon(lat1, lon1, format7)
        print(lat1, lon1, "in format", format7, "is", res1, res2, "\n")
        res1, res2 = conv_lat_lon(lat1, lon1, format8)
        print(lat1, lon1, "in format", format8, "is", res1, res2, "\n")

    def test_formats_fail(lat1, lon1, text=""):
        print("This test should make conv_lat_lon function fail, %s:") % text
        res1, res2 = conv_lat_lon(lat1, lon1)
        print(lat1, lon1, " fails to convert, result=", res1, res2, "\n")

    def test_RT90_conversion():
        """
        a given lat/lon is converted to RT90 and back as a test:
        """
        la = 59.0 + 40.0 / 60.0 + 9.09 / 3600.0
        lo = 12.0 + 58.0 / 60.0 + 57.74 / 3600.0
        x, y = __conv_WGS84_SWED_RT90(la, lo)
        lanew, lonew = __conv_SWED_RT90_WGS84(x, y)
        assert math.fabs(lanew - la) < 1e-6, math.fabs(lanew - la)
        assert math.fabs(lonew - lo) < 1e-6, math.fabs(lonew - lo)

    lat, lon = "50.849888888888", "2.885897222222"
    test_formats_success(lat, lon)
    lat, lon = " 50°50'59.60\"N", "  2°53'9.23\"E"
    test_formats_success(lat, lon)
    lat, lon = " 50 : 50 : 59.60 ", " -2:53 : 9.23   "
    test_formats_success(lat, lon)
    lat, lon = " dummy", "  2#53 ' 9.23  \"  E "
    test_formats_fail(lat, lon)
    lat, lon = " 50:50: 59.60", "  d u m my"
    test_formats_fail(lat, lon)
    lat, lon = ' 50°59.60"N', "  2°53'E"
    test_formats_success(lat, lon)
    lat, lon = " 11° 11' 11\" N, 11° 11' 11\" O", " "
    test_formats_fail(lat, lon)
    # very small negative
    lat, lon = "-0.00006", "-0.00006"
    test_formats_success(lat, lon)
    # missing direction N/S
    lat, lon = ' 50°59.60"', "  2°53'E"
    test_formats_fail(lat, lon)
    # wrong direction on latitude
    lat, lon = ' 50°59.60"E', "  2°53'N"
    test_formats_fail(lat, lon)
    # same as above
    lat, lon = ' 50°59.99"E', "  2°59'59.99\"N"
    test_formats_fail(lat, lon)
    # test precision
    lat, lon = ' 50°59.99"S', "  2°59'59.99\"E"
    test_formats_success(lat, lon)
    lat, lon = "N50.849888888888", "E2.885897222222"
    test_formats_success(lat, lon)
    # to large value of lat
    lat, lon = "90.849888888888", "2.885897222222"
    test_formats_fail(lat, lon)
    # extreme values allowed
    lat, lon = "90", "-180"
    test_formats_success(lat, lon)
    # extreme values allowed
    lat, lon = "90° 00' 00.00\" S ", "179° 59'59.99\"W"
    test_formats_success(lat, lon)
    # extreme value not allowed
    lat, lon = "90° 00' 00.00\" N", "180° 00'00.00\" E"
    test_formats_fail(lat, lon)
    # extreme values allowed
    lat, lon = "90: 00: 00.00 ", "-179: 59:59.99"
    test_formats_success(lat, lon)
    # extreme value not allowed
    lat, lon = "90° 00' 00.00\" N", "180:00:00.00"
    test_formats_fail(lat, lon)
    # extreme values not allowed
    lat, lon = "90", "180"
    test_formats_fail(lat, lon)
    lat, lon = " 89°59'60\"N", "  2°53'W"
    test_formats_fail(lat, lon)
    lat, lon = " 89°60'00\"N", "  2°53'W"
    test_formats_fail(lat, lon)
    lat, lon = " 89.1°40'00\"N", "  2°53'W"
    test_formats_fail(lat, lon)
    lat, lon = " 89°40'00\"N", "  2°53.1'W"
    test_formats_fail(lat, lon)
    lat, lon = "0", "0"
    test_formats_success(lat, lon, "Special 0 value, crossing 0-meridian and equator")
    # small values close to equator
    lat, lon = ' 1°1"N', "  1°1'E"
    test_formats_success(lat, lon)
    # roundoff
    lat, lon = ' 1°59.999"N', '  1°59.999"E'
    test_formats_success(lat, lon, "Examples of round off and how it behaves")
    lat, lon = " 1°59'59.9999\"N", "  1°59'59.9999\"E"
    test_formats_success(lat, lon, "Examples of round off and how it behaves")
    lat, lon = "89°59'59.9999\"S", "179°59'59.9999\"W"
    test_formats_success(lat, lon, "Examples of round off and how it behaves")
    lat, lon = "89°59'59.9999\"N", "179°59'59.9999\"E"
    test_formats_success(lat, lon, "Examples of round off and how it behaves")
    # insane number of decimals:
    lat, lon = "89°59'59.99999999\"N", "179°59'59.99999999\"E"
    test_formats_success(lat, lon, "Examples of round off and how it begaves")
    # recognise '' as seconds "
    lat, lon = "89°59'59.99'' N", "179°59'59.99''E"
    test_formats_success(lat, lon, "input \" as ''")
    # test localisation of , and . as delimiter
    lat, lon = "50.849888888888", "2,885897222222"
    test_formats_success(lat, lon, "localisation of . and , ")
    lat, lon = "89°59'59.9999\"S", "179°59'59,9999\"W"
    test_formats_success(lat, lon, "localisation of . and , ")
    lat, lon = "89°59'1.599,999\"S", "179°59'59,9999\"W"
    test_formats_fail(lat, lon, "localisation of . and , ")
    # rest
    lat, lon = "81.2", "-182.3"
    test_formats_fail(lat, lon)
    lat, lon = "-91.2", "-1"
    test_formats_fail(lat, lon)
    lat, lon = "++50:10:1", "2:1:2"
    test_formats_fail(lat, lon)
    lat, lon = "-50:10:1", "-+2:1:2"
    test_formats_success(lat, lon)
    lat, lon = "-50::1", "-2:1:2"
    test_formats_fail(lat, lon)
    lat, lon = "- 50  : 2 : 1 ", "-2:1:2"
    test_formats_success(lat, lon)
    lat, lon = "+ 50:2 :  1", "-2:1:2"
    test_formats_success(lat, lon)
    lat, lon = "+50:", "-2:1:2"
    test_formats_fail(lat, lon)
    lat, lon = "+50:1", "-2:1:2"
    test_formats_success(lat, lon)
    lat, lon = "+50: 0 : 1 : 1", "-2:1:2"
    test_formats_fail(lat, lon)
    lat, lon = "+61° 43' 60.00\"", "+17° 7' 60.00\""
    test_formats_fail(lat, lon)
    lat, lon = "+61° 44' 00.00\"N", "+17° 8' 00.00\"E"
    test_formats_success(lat, lon)
    lat, lon = ": 0 : 1 : 1", ":1:2"
    test_formats_fail(lat, lon)
    lat, lon = "N 50º52'21.92\"", "E 124º52'21.92\""
    test_formats_success(
        lat, lon, "New format with N/E first and another º - character"
    )
    lat, lon = "S 50º52'21.92\"", "W 124º52'21.92\""
    test_formats_success(
        lat, lon, "New format with S/W first and another º - character"
    )

    test_RT90_conversion()
