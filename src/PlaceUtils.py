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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id:PlaceUtils.py 9912 2008-01-22 09:17:46Z acraphae $


#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------


#-------------------------------------------------------------------------
#
# begin localisation part
#
#-------------------------------------------------------------------------

# translation of N/S/E/W, make sure translator understands
degrees = "1"
North = _("%(north_latitude)s N") % {'north_latitude' : degrees}
South = _("%(south_latitude)s S") % {'south_latitude' : degrees}
East  = _("%(east_longitude)s E") % {'east_longitude' : degrees}
West  = _("%(west_longitude)s W") % {'west_longitude' : degrees}

# extract letters we really need
North = North.replace("1"," ").strip()
South = South.replace("1"," ").strip()
East  = East.replace("1"," ").strip()
West  = West.replace("1"," ").strip()

# build dictionary with translation en to local language
translate_en_loc = {}
translate_en_loc['N'] = North
translate_en_loc['S'] = South
translate_en_loc['E'] = East
translate_en_loc['W'] = West

# keep translation only if it does not conflict with english
if 'N' == South or 'S' == North or 'E' == West or 'W' == East:
    translate_en_loc['N'] = 'N'
    translate_en_loc['S'] = 'S'
    translate_en_loc['E'] = 'E'
    translate_en_loc['W'] = 'W'
# end localisation part


#------------------
#
# helper functions
#
#------------------

def __convert_structure_to_float(sign, degs, mins=0, secs=0.0) :
    """helper function which converts a structure to a nice
    representation
    """
    v = float(degs) 
    if mins is not None:
        v += float(mins) / 60.
    if secs is not None:
        v += secs / 3600.
    if sign == "-":
        v = v * -1.

    return v

def __convert_using_float_repr(stringValue):
    """ helper function that tries to convert the string using the float
    representation
    """
    try : 
        v = float(stringValue)      
        return v
    except ValueError :
        return None;

def __convert_using_colon_repr(stringValue):
    """ helper function that tries to convert the string using the colon
    representation
    """
    if stringValue.find(r':') == -1 :
        return None

    l = stringValue.split(':')
    if len(l) < 2 or len(l) > 3:
        return None
    l[0]=l[0].strip()
    # if no characters before ':' nothing useful is input!
    if len(l[0]) == 0:
        return None
    if l[0][0] == '-':
        sign = '-'
        l[0]=l[0][1:]
    else:
        sign = '+'
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
    secs=0.
    if len(l) == 3:
        try:
            secs = float(l[2])
            if secs < 0. or secs >= 60.:
                return None
        except:
            return None

    return __convert_structure_to_float(sign, degs, mins, secs)

def __convert_using_classic_repr(stringValue, typedeg):
    """helper function that tries to convert the string using the colon
    representation
    """
    if stringValue.find(r'_') != -1:
        return None    # not a valid lat or lon

    #exchange some characters
    stringValue = stringValue.replace(u'°',r'_')
    #allow to input ° as #, UTF-8 code c2b00a
    stringValue = stringValue.replace(u'º',r'_')
    #allow to input º as #, UTF-8 code c2ba0a
    stringValue = stringValue.replace(r'#',r'_')
    #allow to input " as ''
    stringValue = stringValue.replace(r"''",r'"')
    #allow some special unicode symbols
    stringValue = stringValue.replace(u'\u2033',r'"')
    stringValue = stringValue.replace(u'\u2032',r"'")
    #ignore spaces, a regex with \s* would be better here...
    stringValue = stringValue.replace(r' ', r'')
    stringValue = stringValue.replace(r'\t', r'')

    # get the degrees, must be present
    if stringValue.find(r'_') == -1:
        return None
    l = stringValue.split(r'_')
    if len(l) != 2:
        return None

    try: 
        degs = int(l[0])  #degrees must be integer value
        if degs < 0:
            return None
    except:
        return None
    # next: minutes might be present once
    l2 = l[1].split(r"'")
    l3 = l2
    mins = 0
    if len(l2) > 2:
        return None
    if len(l2) == 2:
        l3 = [l2[1],]
        try:
            mins = int(l2[0]) #minutes must be integer value
            if mins < 0 or mins >= 60:
                return None
        except:
            return None
    # next: seconds might be present once
    l3 = l3[0].split(r'"')
    last = l3[0]
    secs = 0.
    if len(l3) > 2:
        return None 
    if len(l3) == 2:
        last = l3[1]
        try:
            secs = float(l3[0])
            if secs < 0. or secs >= 60.:
                return None
        except:
            return None
    # last entry should be the direction
    if typedeg == 'lat':
        if last == 'N':
            sign = '+'
        elif last == 'S':
            sign = '-'
        else:
            return None
    elif typedeg == 'lon':
        if last == 'E':
            sign = '+'
        elif last == 'W':
            sign = '-'
        else:
            return None
    else:
        return None

    return __convert_structure_to_float(sign, degs, mins, secs)

def __convert_float_val(val, typedeg = "lat"):
    # function converting input to float, recognizing decimal input, or 
    # degree notation input. Only english input
    # There is no check on maximum/minimum of degree
    # In case of degree minutes seconds direction input,
    # it is checked that degree >0, 0<= minutes <= 60,
    # 0<= seconds <= 60, direction is in the directions dic.

    #change , to . so that , input works in non , localization
    #this is no problem, as a number like 100,000.20 cannot appear in 
    #lat/lon
    #change XX,YY into XX.YY 
    if val.find(r'.') == -1 :
        val = val.replace(u',', u'.')
    
    # format: XX.YYYY
    v = __convert_using_float_repr(val) 
    if v is not None:
        return v

    # format: XX:YY:ZZ
    v = __convert_using_colon_repr(val) 
    if v is not None : 
        return v

    # format: XX° YY' ZZ" [NSWE]
    v = __convert_using_classic_repr(val, typedeg) 
    if v is not None : 
        return v
    
    # no format succeeded
    return None

#-------------------------------------------------------------------------
#
# conversion function
#
#-------------------------------------------------------------------------

def conv_lat_lon(latitude, longitude, format="D.D4"):
    """
    Convert given string latitude and longitude to a required format. 
    Possible formats:
        'D.D4'    : degree notation, 4 decimals 
                    eg +12.0154 , -124.3647
        'D.D8'    : degree notation, 8 decimals (precision like ISO-DMS) 
                    eg +12.01543265 , -124.36473268
        'DEG'     : degree, minutes, seconds notation
                    eg 50°52'21.92''N , 124°52'21.92''E ° has UTF-8 code c2b00a
                    or N 50º52'21.92" E 124º52'21.92"   º has UTF-8 code c2ba0a
        'DEG-:'   : degree, minutes, seconds notation with :
                    eg -50:52:21.92 , 124:52:21.92
        'ISO-D'   : ISO 6709 degree notation i.e. ±DD.DDDD±DDD.DDDD
        'ISO-DM'  : ISO 6709 degree, minutes notation 
                    i.e. ±DDMM.MMM±DDDMM.MMM
        'ISO-DMS' : ISO 6709 degree, minutes, seconds notation 
                    i.e. ±DDMMSS.SS±DDDMMSS.SS
    Return value: a tuple of 2 strings, or a string (for ISO formats)
    If conversion fails: returns: (None, None)  or None (for ISO formats)
    Some generalities:
        -90 <= latitude <= +90 with +00 the equator
        -180 <= longitude < +180 with +000 prime meridian
                                  and -180   180th meridian
    """

    # we start the function changing latitude/longitude in english
    if latitude.find('N') == -1 and latitude.find('S') == -1:
        # entry is not in english, convert to english
        latitude = latitude.replace(translate_en_loc['N'],'N')
        latitude = latitude.replace(translate_en_loc['S'],'S')
    if longitude.find('E') == -1 and longitude.find('W') == -1:
        # entry is not in english, convert to english
        longitude = longitude.replace(translate_en_loc['W'],'W')
        longitude = longitude.replace(translate_en_loc['E'],'E')

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
    lat_float = __convert_float_val(latitude,  'lat')
    lon_float = __convert_float_val(longitude, 'lon')

    # give output (localized if needed)
    if lat_float is None or lon_float is None:
        if format == "ISO-D" or format == "ISO-DM" or format == "ISO-DMS":
            return None
        else:
            return (None, None)
    if lat_float > 90. or lat_float < -90. \
           or lon_float >= 180. or lon_float < -180.:
        if format == "ISO-D" or format == "ISO-DM" or format == "ISO-DMS":
            return None
        else:
            return (None, None)
    
    if format == "D.D4":
        # correct possible roundoff error
        str_lon = "%.4f" % (lon_float)
        if str_lon == "180.0000":
            str_lon ="-180.0000"
        return ("%.4f" % lat_float , str_lon)

    if format == "D.D8":
        # correct possible roundoff error
        str_lon = "%.8f" % (lon_float)
        if str_lon == "180.00000000":
            str_lon ="-180.00000000"
        return ("%.8f" % lat_float , str_lon)
    
    
    deg_lat = int(lat_float)
    deg_lon = int(lon_float)
    min_lat = int(60.   * (lat_float - float(deg_lat)                       ))
    min_lon = int(60.   * (lon_float - float(deg_lon)                       ))
    sec_lat = 3600. * (lat_float - float(deg_lat) - float(min_lat) / 60.)
    sec_lon = 3600. * (lon_float - float(deg_lon) - float(min_lon) / 60.)

    # dump minus sign on all, store minus sign. Carefull: int(-0.8)=0 !!
    if (deg_lat) < 0:
        deg_lat = -1 * deg_lat
    if (min_lat) < 0:
        min_lat = -1 * min_lat
    if (sec_lat) < 0.:
        sec_lat = -1. * sec_lat
    if (deg_lon) < 0:
        deg_lon = -1 * deg_lon
    if (min_lon) < 0:
        min_lon = -1 * min_lon
    if (sec_lon) < 0.:
        sec_lon = -1. * sec_lon
    # keep sign as -1* 0 = +0, so 0°2'S is given correct sign in ISO
    sign_lat = "+"
    dir_lat = ""
    if lat_float >= 0.:
        dir_lat = translate_en_loc['N']
    else:
        dir_lat = translate_en_loc['S']
        sign_lat= "-"
    sign_lon= "+"
    dir_lon = ""
    if lon_float >= 0.:
        dir_lon = translate_en_loc['E']
    else:
        dir_lon = translate_en_loc['W']
        sign_lon= "-"
    
    if format == "DEG":
        str_lat = ("%d°%02d'%05.2f\"" % (deg_lat, min_lat, sec_lat)) + dir_lat
        str_lon = ("%d°%02d'%05.2f\"" % (deg_lon, min_lon, sec_lon)) + dir_lon
        # correct possible roundoff error in seconds
        if str_lat[-6-len(dir_lat)] == '6':
            if min_lat == 59:
                str_lat = ("%d°%02d'%05.2f\"" % (deg_lat+1, 0, 0.)) + dir_lat
            else:
                str_lat = ("%d°%02d'%05.2f\"" % (deg_lat, min_lat+1, 0.)) \
                          + dir_lat
        if str_lon[-6-len(dir_lon)] == '6':
            if min_lon == 59:
                if deg_lon == 179 and sign_lon == "+":
                    str_lon = ("%d°%02d'%05.2f\"" % (180, 0, 0.)) \
                              + translate_en_loc['W']
                else:
                    str_lon = ("%d°%02d'%05.2f\"" % (deg_lon+1, 0, 0.)) \
                              + dir_lon
            else:
                str_lon = ("%d°%02d'%05.2f\"" % (deg_lon, min_lon+1, 0.)) \
                          + dir_lon

        return  (str_lat, str_lon)

    if format == "DEG-:":
        if sign_lat=="+":
            sign_lat = ""
        sign_lon_h = sign_lon
        if sign_lon=="+":
            sign_lon_h = ""
        str_lat = sign_lat + ("%d:%02d:%05.2f" % (deg_lat, min_lat, sec_lat))
        str_lon = sign_lon_h + ("%d:%02d:%05.2f" % (deg_lon, min_lon, sec_lon))

        # correct possible roundoff error in seconds
      
        if str_lat[-5] == '6':
            if min_lat == 59:
                str_lat = sign_lat + ("%d:%02d:%05.2f" % (deg_lat+1, 0, 0.))
            else:
                str_lat = sign_lat + \
                          ("%d:%02d:%05.2f" % (deg_lat, min_lat+1, 0.))
        if str_lon[-5] == '6':
            if min_lon == 59:
                if deg_lon == 179 and sign_lon == "+":
                    str_lon = '-' + ("%d:%02d:%05.2f" % (180, 0, 0.))
                else:
                    str_lon = sign_lon_h + \
                              ("%d:%02d:%05.2f" % (deg_lon+1, 0, 0.))
            else:
                str_lon = sign_lon_h + \
                          ("%d:%02d:%05.2f" % (deg_lon, min_lon+1, 0.))
          
        return (str_lat, str_lon)

    if format == "ISO-D":  # ±DD.DDDD±DDD.DDDD
        str_lon = "%+09.4f" % (lon_float)
        # correct possible roundoff error
        if str_lon == "+180.0000":
            str_lon = "-180.0000"
        return ("%+08.4f" % lat_float) + str_lon

    if format == "ISO-DM":  # ±DDMM.MMM±DDDMM.MMM
        min_fl_lat = float(min_lat)+ sec_lat/60.
        min_fl_lon = float(min_lon)+ sec_lon/60.
        str_lat = sign_lat + ("%02d%06.3f" % (deg_lat, min_fl_lat))
        str_lon = sign_lon + ("%03d%06.3f" % (deg_lon, min_fl_lon))
        # correct possible roundoff error
        if str_lat[3:] == "60.000":
            str_lat = sign_lat + ("%02d%06.3f" % (deg_lat+1, 0.))
        if str_lon[4:] == "60.000":
            if deg_lon == 179 and sign_lon == "+":
                str_lon = "-" + ("%03d%06.3f" % (180, 0.))
            else:
                str_lon = sign_lon + ("%03d%06.3f" % (deg_lon+1, 0.))
        return str_lat + str_lon 

    if format == "ISO-DMS":  # ±DDMMSS.SS±DDDMMSS.SS
        str_lat = sign_lat + ("%02d%02d%06.3f" % (deg_lat, min_lat, sec_lat))
        str_lon = sign_lon + ("%03d%02d%06.3f" % (deg_lon, min_lon, sec_lon))
        # correct possible roundoff error
        if str_lat[5:] == "60.000": 
            if min_lat == 59:
                str_lat = sign_lat + ("%02d%02d%06.3f" % (deg_lat+1, 0, 0.))
            else:
                str_lat = sign_lat + \
                          ("%02d%02d%06.3f" % (deg_lat, min_lat +1, 0.))
        if str_lon[6:] == "60.000": 
            if min_lon == 59:
                if deg_lon == 179 and sign_lon == "+":
                    str_lon = "-" + ("%03d%02d%06.3f" % (180, 0, 0))
                else:
                    str_lon = sign_lon + \
                              ("%03d%02d%06.3f" % (deg_lon+1, 0, 0.))
            else:
                str_lon = sign_lon + \
                          ("%03d%02d%06.3f" % (deg_lon, min_lon+1, 0.))
        return str_lat + str_lon



#-------------------------------------------------------------------------
#
# For Testing the convert function in this module, apply it as a script:
#     ==> in command line do "python PlaceUtils.py" 
#
#-------------------------------------------------------------------------

if __name__ == '__main__':
    def test_formats_success(lat1,lon1, text=''):
        format0 = "D.D4"
        format1 = "D.D8"
        format2 = "DEG"
        format3 = "DEG-:"
        format4 = "ISO-D"
        format5 = "ISO-DM"
        format6 = "ISO-DMS"
        print "Testing conv_lat_lon function, "+text+':'
        res1, res2 = conv_lat_lon(lat1,lon1,format0)
        print lat1,lon1,"in format",format0, "is   ",res1,res2
        res1, res2 = conv_lat_lon(lat1,lon1,format1)
        print lat1,lon1,"in format",format1, "is   ",res1,res2
        res1, res2 = conv_lat_lon(lat1,lon1,format2)
        print lat1,lon1,"in format",format2, "is    ",res1,res2
        res1, res2 = conv_lat_lon(lat1,lon1,format3)
        print lat1,lon1,"in format",format3, "is  ",res1,res2
        res = conv_lat_lon(lat1,lon1,format4)
        print lat1,lon1,"in format",format4, "is ",res
        res = conv_lat_lon(lat1,lon1,format5)
        print lat1,lon1,"in format",format5, "is",res
        res = conv_lat_lon(lat1,lon1,format6)
        print lat1,lon1,"in format",format6, "is",res,"\n"
    
    def test_formats_fail(lat1,lon1,text=''):
        print "This test should make conv_lat_lon function fail, "+text+":"
        res1, res2 = conv_lat_lon(lat1,lon1)
        print lat1,lon1," fails to convert, result=", res1,res2,"\n"
    
    lat, lon = '50.849888888888', '2.885897222222'
    test_formats_success(lat,lon)
    lat, lon = u' 50°50\'59.60"N', u'  2°53\'9.23"E'
    test_formats_success(lat,lon)
    lat, lon = ' 50 : 50 : 59.60 ', ' -2:53 : 9.23   '
    test_formats_success(lat,lon)
    lat, lon = ' dummy', '  2#53 \' 9.23  "  E '
    test_formats_fail(lat,lon)
    lat, lon = ' 50:50: 59.60', '  d u m my'
    test_formats_fail(lat,lon)
    lat, lon =  u' 50°59.60"N', u'  2°53\'E'
    test_formats_success(lat,lon)
    lat, lon =  u' 11° 11\' 11" N, 11° 11\' 11" O', ' '
    test_formats_fail(lat,lon)
    # very small negative
    lat, lon =  '-0.00006', '-0.00006'
    test_formats_success(lat,lon)
    # missing direction N/S
    lat, lon =  u' 50°59.60"', u'  2°53\'E'
    test_formats_fail(lat,lon)
    # wrong direction on latitude
    lat, lon =  u' 50°59.60"E', u'  2°53\'N'
    test_formats_fail(lat,lon)
    # same as above
    lat, lon =  u' 50°59.99"E', u'  2°59\'59.99"N'
    test_formats_fail(lat,lon)
    # test precision
    lat, lon =  u' 50°59.99"S', u'  2°59\'59.99"E'
    test_formats_success(lat,lon)
    # to large value of lat
    lat, lon =  '90.849888888888', '2.885897222222'
    test_formats_fail(lat,lon)
    # extreme values allowed
    lat, lon =  '90', '-180'
    test_formats_success(lat,lon)
    # extreme values allowed
    lat, lon =  u'90° 00\' 00.00" S ', u'179° 59\'59.99"W'
    test_formats_success(lat,lon)
    # extreme value not allowed
    lat, lon =  u'90° 00\' 00.00" N', u'180° 00\'00.00" E'
    test_formats_fail(lat,lon)
    # extreme values allowed
    lat, lon =  '90: 00: 00.00 ', '-179: 59:59.99'
    test_formats_success(lat,lon)
    # extreme value not allowed
    lat, lon =  u'90° 00\' 00.00" N', '180:00:00.00'
    test_formats_fail(lat,lon)
    # extreme values not allowed
    lat, lon =  '90', '180'
    test_formats_fail(lat,lon)
    lat, lon =  u' 89°59\'60"N', u'  2°53\'W'
    test_formats_fail(lat,lon)
    lat, lon =  u' 89°60\'00"N', u'  2°53\'W'
    test_formats_fail(lat,lon)
    lat, lon =  u' 89.1°40\'00"N', u'  2°53\'W'
    test_formats_fail(lat,lon)
    lat, lon =  u' 89°40\'00"N', u'  2°53.1\'W'
    test_formats_fail(lat,lon)
    lat, lon =  '0', '0'
    test_formats_success(lat,lon,
            "Special 0 value, crossing 0-meridian and equator")
    # small values close to equator
    lat, lon =  u' 1°1"N', u'  1°1\'E'
    test_formats_success(lat,lon)
    # roundoff
    lat, lon =  u' 1°59.999"N', u'  1°59.999"E'
    test_formats_success(lat,lon,'Examples of round off and how it behaves')
    lat, lon =  u' 1°59\'59.9999"N', u'  1°59\'59.9999"E'
    test_formats_success(lat,lon,'Examples of round off and how it behaves')
    lat, lon =  u'89°59\'59.9999"S', u'179°59\'59.9999"W'
    test_formats_success(lat,lon,'Examples of round off and how it behaves')
    lat, lon =  u'89°59\'59.9999"N', u'179°59\'59.9999"E'
    test_formats_success(lat,lon,'Examples of round off and how it behaves')
    #insane number of decimals:
    lat, lon =  u'89°59\'59.99999999"N', u'179°59\'59.99999999"E'
    test_formats_success(lat,lon,'Examples of round off and how it begaves')
    #recognise '' as seconds "
    lat, lon =  u'89°59\'59.99\'\' N', u'179°59\'59.99\'\'E'
    test_formats_success(lat,lon, "input \" as ''")
    #test localisation of , and . as delimiter
    lat, lon = '50.849888888888', '2,885897222222'
    test_formats_success(lat,lon, 'localisation of . and , ')
    lat, lon =  u'89°59\'59.9999"S', u'179°59\'59,9999"W'
    test_formats_success(lat,lon, 'localisation of . and , ')
    lat, lon =  u'89°59\'1.599,999"S', u'179°59\'59,9999"W'
    test_formats_fail(lat,lon, 'localisation of . and , ')
    #rest
    lat, lon =  '81.2', '-182.3'
    test_formats_fail(lat,lon)
    lat, lon =  '-91.2', '-1'
    test_formats_fail(lat,lon)
    lat, lon =  '++50:10:1', '2:1:2'
    test_formats_fail(lat,lon)
    lat, lon =  '-50:10:1', '-+2:1:2'
    test_formats_success(lat,lon)
    lat, lon =  '-50::1', '-2:1:2'
    test_formats_fail(lat,lon)
    lat, lon =  '- 50  : 2 : 1 ', '-2:1:2'
    test_formats_success(lat,lon)
    lat, lon =  '+ 50:2 :  1', '-2:1:2'
    test_formats_success(lat,lon)
    lat, lon =  '+50:', '-2:1:2'
    test_formats_fail(lat,lon)
    lat, lon =  '+50:1', '-2:1:2'
    test_formats_success(lat,lon)
    lat, lon =  '+50: 0 : 1 : 1', '-2:1:2'
    test_formats_fail(lat,lon)
    lat, lon = u'+61° 43\' 60.00"', u'+17° 7\' 60.00"'
    test_formats_fail(lat,lon)
    lat, lon = u'+61° 44\' 00.00"N', u'+17° 8\' 00.00"E'
    test_formats_success(lat,lon)
    lat, lon =  ': 0 : 1 : 1', ':1:2'
    test_formats_fail(lat,lon)
    lat, lon = u'N 50º52\'21.92"', u'E 124º52\'21.92"'
    test_formats_success(lat,lon, 'New format with N/E first and another º - character')
    lat, lon = u'S 50º52\'21.92"', u'W 124º52\'21.92"'
    test_formats_success(lat,lon, 'New format with S/W first and another º - character')

