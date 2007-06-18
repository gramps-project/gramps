#                                                     -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# $Id$

# Written by Benny Malengier

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _


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

#-------------------------------------------------------------------------
#
# conversion function
#
#-------------------------------------------------------------------------

def conv_lat_lon(latitude, longitude, format="D.D4"):
    """
    Converts given string latitude and longitude to a required format. 
    Possible formats:
        'D.D4'    : degree notation, 4 decimals 
                    eg +12.0154 , -124.3647
        'D.D8'    : degree notation, 8 decimals (precision like ISO-DMS) 
                    eg +12.01543265 , -124.36473268
        'DEG'     : degree, minutes, seconds notation
                    eg 50°52'21.92''N , 124°52'21.92''E
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

    #-------------------------------------------------------------------------
    # begin internal function converting one input to float
    #-------------------------------------------------------------------------
    def convert_float_val(val, typedeg = "lat"):
        # function converting input to float, recognizing decimal input, or 
        # degree notation input. Only english input
        # There is no check on maximum/minimum of degree
        # In case of degree minutes seconds direction input,
        # it is checked that degree >0, 0<= minutes <= 60,
        # 0<= seconds <= 60, direction is in the directions dic.
        v = None
        sign = None
        secs = None
        mins = None
        degs = None
        error = False

        #change , to . so that , input works in non , localization
        #this is no problem, as a number like 100,000.20 cannot appear in 
        #lat/lon
        try : 
            test = float('10,11')
        except ValueError :
            #change 10,11 into 10.11
            #if point is already present in val, we can do nothing
            if val.find(r'.') == -1 :
                val = val.replace( r',',r'.')
        try : 
            test = float('10.11')
        except ValueError :
            #change 10.11 into 10,11
            #if comma is already present in val, we can do nothing
            if val.find(r',') == -1 :
                val = val.replace( r'.',r',')
        
        try: 
            v = float(val)      #decimal notation, now float
        except ValueError:
            # look for : notation
            if val.find(r':') != -1 :
                l = val.split(':')
                if len(l) < 2 or  len(l) > 3:
                    error = True
                l[0]=l[0].strip()
                if l[0][0] == '-':
                    sign = '-'
                    l[0]=l[0][1:]
                else:
                    sign = '+'
                try:
                    degs = int(l[0])
                    if degs < 0:
                        error = True
                except:
                    error = True
                try:
                    mins = int(l[1])
                    if mins < 0 or mins >= 60:
                        error = True
                except:
                    error = True
                secs=0.
                if len(l) == 3:
                    try:
                        secs = float(l[2])
                        if secs < 0. or secs >= 60.:
                            error = True
                    except:
                        error = True

            # if nothing found yet, look for classical notation
            if val.find(r'_') != -1:
                error = True   # not a valid lat or lon
            val = val.replace( r'°',r'_')
            #allow to input ° as #
            val = val.replace( r'#',r'_')
            #allow to input " as ''
            val = val.replace( r"''",r'"')
            #ignore spaces
            val = val.replace(r'\s*', r'')
            # get the degrees, must be present
            if val.find(r'_') != -1:
                l = val.split('_')
                if len(l) != 2:
                    error = True
                else:
                    try: 
                        degs = int(l[0])  #degrees must be integer value
                        if degs < 0:
                            error = True
                    except:
                        error = True
                    # next: minutes might be present once
                    l2 = l[1].split(r"'")
                    l3 = l2
                    mins = 0
                    if len(l2) > 2:
                        error = True 
                    if len(l2) == 2:
                        l3 = [l2[1],]
                        try:
                            mins = int(l2[0]) #minutes must be integer value
                            if mins < 0 or mins >= 60:
                                error = True
                        except:
                            error = True
                    # next: seconds might be present once
                    l3 = l3[0].split(r'"')
                    last = l3[0]
                    secs = 0.
                    if len(l3) > 2:
                        error = True 
                    if len(l3) == 2:
                        last = l3[1]
                        try:
                            secs = float(l3[0])
                            if secs < 0. or secs >= 60.:
                                error = True
                        except:
                            error = True
                # last entry should be the direction
                last = last.strip()             #remove leading/trailing spaces
                if typedeg == 'lat':
                    if last == 'N':
                        sign = '+'
                    elif last == 'S':
                        sign = '-'
                    else:
                        error = True
                if typedeg == 'lon':
                    if last == 'E':
                        sign = '+'
                    elif last == 'W':
                        sign = '-'
                    else:
                        error = True
            # degs should have a value now
            if degs == None:
                error = True  

        if error:
            return None
        if v != None:
            return v
        #we have a degree notation, convert to float
        v = float(degs) 
        if secs != None:
            v += secs / 3600.
        if mins != None:
            v += float(mins) / 60.
        if sign =="-":
            v = v * -1.

        return v
    #-------------------------------------------------------------------------
    # end internal function converting one input to float
    #-------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------
    # begin convert function
    #-------------------------------------------------------------------------
    
    # we start the function changing latitude/longitude in english
    if latitude.find('N') == -1 and latitude.find('S') == -1:
        # entry is not in english, convert to english
        latitude = latitude.replace(translate_en_loc['N'],'N')
        latitude = latitude.replace(translate_en_loc['S'],'S')
    if longitude.find('E') == -1 and longitude.find('W') == -1:
        # entry is not in english, convert to english
        longitude = longitude.replace(translate_en_loc['W'],'W')
        longitude = longitude.replace(translate_en_loc['E'],'E')

    # convert to float
    lat_float = convert_float_val(latitude,  'lat')
    lon_float = convert_float_val(longitude, 'lon')
    
    # give output (localized if needed)
    if lat_float == None or lon_float == None:
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
    # end convert function
    #-------------------------------------------------------------------------



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
    lat, lon = ' 50°50\'59.60"N', '  2°53\'9.23"E'
    test_formats_success(lat,lon)
    lat, lon = ' 50 : 50 : 59.60 ', ' -2:53 : 9.23   '
    test_formats_success(lat,lon)
    lat, lon = ' dummy', '  2#53 \' 9.23  "  E '
    test_formats_fail(lat,lon)
    lat, lon = ' 50:50: 59.60', '  d u m my'
    test_formats_fail(lat,lon)
    lat, lon =  ' 50°59.60"N', '  2°53\'E'
    test_formats_success(lat,lon)
    # very small negative
    lat, lon =  '-0.00006', '-0.00006'
    test_formats_success(lat,lon)
    # missing direction N/S
    lat, lon =  ' 50°59.60"', '  2°53\'E'
    test_formats_fail(lat,lon)
    # wrong direction on latitude
    lat, lon =  ' 50°59.60"E', '  2°53\'N'
    test_formats_fail(lat,lon)
    # same as above
    lat, lon =  ' 50°59.99"E', '  2°59\'59.99"N'
    test_formats_fail(lat,lon)
    # test precision
    lat, lon =  ' 50°59.99"S', '  2°59\'59.99"E'
    test_formats_success(lat,lon)
    # to large value of lat
    lat, lon =  '90.849888888888', '2.885897222222'
    test_formats_fail(lat,lon)
    # extreme values allowed
    lat, lon =  '90', '-180'
    test_formats_success(lat,lon)
    # extreme values allowed
    lat, lon =  '90° 00\' 00.00" S ', '179° 59\'59.99"W'
    test_formats_success(lat,lon)
    # extreme value not allowed
    lat, lon =  '90° 00\' 00.00" N', '180° 00\'00.00" E'
    test_formats_fail(lat,lon)
    # extreme values allowed
    lat, lon =  '90: 00: 00.00 ', '-179: 59:59.99'
    test_formats_success(lat,lon)
    # extreme value not allowed
    lat, lon =  '90° 00\' 00.00" N', '180:00:00.00'
    test_formats_fail(lat,lon)
    # extreme values not allowed
    lat, lon =  '90', '180'
    test_formats_fail(lat,lon)
    lat, lon =  ' 89°59\'60"N', '  2°53\'W'
    test_formats_fail(lat,lon)
    lat, lon =  ' 89°60\'00"N', '  2°53\'W'
    test_formats_fail(lat,lon)
    lat, lon =  ' 89.1°40\'00"N', '  2°53\'W'
    test_formats_fail(lat,lon)
    lat, lon =  ' 89°40\'00"N', '  2°53.1\'W'
    test_formats_fail(lat,lon)
    lat, lon =  '0', '0'
    test_formats_success(lat,lon,
            "Special 0 value, crossing 0-meridian and equator")
    # small values close to equator
    lat, lon =  ' 1°1"N', '  1°1\'E'
    test_formats_success(lat,lon)
    # roundoff
    lat, lon =  ' 1°59.999"N', '  1°59.999"E'
    test_formats_success(lat,lon,'Examples of round off and how it behaves')
    lat, lon =  ' 1°59\'59.9999"N', '  1°59\'59.9999"E'
    test_formats_success(lat,lon,'Examples of round off and how it behaves')
    lat, lon =  '89°59\'59.9999"S', '179°59\'59.9999"W'
    test_formats_success(lat,lon,'Examples of round off and how it behaves')
    lat, lon =  '89°59\'59.9999"N', '179°59\'59.9999"E'
    test_formats_success(lat,lon,'Examples of round off and how it behaves')
    #insane number of decimals:
    lat, lon =  '89°59\'59.99999999"N', '179°59\'59.99999999"E'
    test_formats_success(lat,lon,'Examples of round off and how it begaves')
    #recognise '' as seconds "
    lat, lon =  '89°59\'59.99\'\' N', '179°59\'59.99\'\'E'
    test_formats_success(lat,lon, "input \" as ''")
    #test localisation of , and . as delimiter
    lat, lon = '50.849888888888', '2,885897222222'
    test_formats_success(lat,lon, 'localisation of . and , ')
    lat, lon =  '89°59\'59.9999"S', '179°59\'59,9999"W'
    test_formats_success(lat,lon, 'localisation of . and , ')
    lat, lon =  '89°59\'1.599,999"S', '179°59\'59,9999"W'
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
    lat, lon = '+61° 43\' 60.00"', '+17° 7\' 60.00"'
    test_formats_fail(lat,lon)
    lat, lon = '+61° 44\' 00.00"N', '+17° 8\' 00.00"E'
    test_formats_success(lat,lon)

