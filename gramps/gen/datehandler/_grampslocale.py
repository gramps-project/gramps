# -*- coding: iso-8859-1 -*- 
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2005  Donald N. Allingham
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
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

import locale
import sys
from ..constfunc import mac, win, conv_to_unicode

from gramps.gen.const import GRAMPS_LOCALE as glocale

"""
Some OS environments do not support the locale.nl_langinfo() method
of determing month names and other date related information.

If nl_langinfo fails, that means we have to resort to shinanigans with
strftime.

Since these routines return values encoded into selected character
set, we have to convert to unicode.
"""
if sys.version_info[0] < 3:
    to_uni = conv_to_unicode
else:
    #locale returns unicode in python 3
    to_uni = lambda x, y: x
try:
    codeset = glocale.get_translation().info()["charset"]
except KeyError:
    codeset = "UTF-8"

try:

    month_to_int = {
        to_uni(locale.nl_langinfo(locale.MON_1), codeset).lower()   : 1,
        to_uni(locale.nl_langinfo(locale.ABMON_1), codeset).lower() : 1,
        to_uni(locale.nl_langinfo(locale.MON_2), codeset).lower()   : 2,
        to_uni(locale.nl_langinfo(locale.ABMON_2), codeset).lower() : 2,
        to_uni(locale.nl_langinfo(locale.MON_3), codeset).lower()   : 3,
        to_uni(locale.nl_langinfo(locale.ABMON_3), codeset).lower() : 3,
        to_uni(locale.nl_langinfo(locale.MON_4), codeset).lower()   : 4,
        to_uni(locale.nl_langinfo(locale.ABMON_4), codeset).lower() : 4,
        to_uni(locale.nl_langinfo(locale.MON_5), codeset).lower()   : 5,
        to_uni(locale.nl_langinfo(locale.ABMON_5), codeset).lower() : 5,
        to_uni(locale.nl_langinfo(locale.MON_6), codeset).lower()   : 6,
        to_uni(locale.nl_langinfo(locale.ABMON_6), codeset).lower() : 6,
        to_uni(locale.nl_langinfo(locale.MON_7), codeset).lower()   : 7,
        to_uni(locale.nl_langinfo(locale.ABMON_7), codeset).lower() : 7,
        to_uni(locale.nl_langinfo(locale.MON_8), codeset).lower()   : 8,
        to_uni(locale.nl_langinfo(locale.ABMON_8), codeset).lower() : 8,
        to_uni(locale.nl_langinfo(locale.MON_9), codeset).lower()   : 9,
        to_uni(locale.nl_langinfo(locale.ABMON_9), codeset).lower() : 9,
        to_uni(locale.nl_langinfo(locale.MON_10), codeset).lower()  : 10,
        to_uni(locale.nl_langinfo(locale.ABMON_10), codeset).lower(): 10,
        to_uni(locale.nl_langinfo(locale.MON_11), codeset).lower()  : 11,
        to_uni(locale.nl_langinfo(locale.ABMON_11), codeset).lower(): 11,
        to_uni(locale.nl_langinfo(locale.MON_12), codeset).lower()  : 12,
        to_uni(locale.nl_langinfo(locale.ABMON_12), codeset).lower(): 12,
       }

    long_months = (
        "",
        to_uni(locale.nl_langinfo(locale.MON_1), codeset),
        to_uni(locale.nl_langinfo(locale.MON_2), codeset),
        to_uni(locale.nl_langinfo(locale.MON_3), codeset),
        to_uni(locale.nl_langinfo(locale.MON_4), codeset),
        to_uni(locale.nl_langinfo(locale.MON_5), codeset),
        to_uni(locale.nl_langinfo(locale.MON_6), codeset),
        to_uni(locale.nl_langinfo(locale.MON_7), codeset),
        to_uni(locale.nl_langinfo(locale.MON_8), codeset),
        to_uni(locale.nl_langinfo(locale.MON_9), codeset),
        to_uni(locale.nl_langinfo(locale.MON_10), codeset),
        to_uni(locale.nl_langinfo(locale.MON_11), codeset),
        to_uni(locale.nl_langinfo(locale.MON_12), codeset),
        )

    short_months = (
        "",
        to_uni(locale.nl_langinfo(locale.ABMON_1), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_2), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_3), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_4), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_5), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_6), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_7), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_8), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_9), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_10), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_11), codeset),
        to_uni(locale.nl_langinfo(locale.ABMON_12), codeset),
        )

    # Gramps day number: Sunday => 1, Monday => 2, etc
    # "Return name of the n-th day of the week. Warning:
    #  This follows the US convention of DAY_1 being Sunday,
    #  not the international convention (ISO 8601) that Monday
    #  is the first day of the week."
    # see http://docs.python.org/library/locale.html
    long_days = (
        "",
        to_uni(locale.nl_langinfo(locale.DAY_1), codeset), # Sunday
        to_uni(locale.nl_langinfo(locale.DAY_2), codeset), # Monday
        to_uni(locale.nl_langinfo(locale.DAY_3), codeset), # Tuesday
        to_uni(locale.nl_langinfo(locale.DAY_4), codeset), # Wednesday
        to_uni(locale.nl_langinfo(locale.DAY_5), codeset), # Thursday
        to_uni(locale.nl_langinfo(locale.DAY_6), codeset), # Friday
        to_uni(locale.nl_langinfo(locale.DAY_7), codeset), # Saturday
        )

    short_days = (
        "",
        to_uni(locale.nl_langinfo(locale.ABDAY_1), codeset), # Sunday
        to_uni(locale.nl_langinfo(locale.ABDAY_2), codeset), # Monday
        to_uni(locale.nl_langinfo(locale.ABDAY_3), codeset), # Tuesday
        to_uni(locale.nl_langinfo(locale.ABDAY_4), codeset), # Wednesday
        to_uni(locale.nl_langinfo(locale.ABDAY_5), codeset), # Thursday
        to_uni(locale.nl_langinfo(locale.ABDAY_6), codeset), # Friday
        to_uni(locale.nl_langinfo(locale.ABDAY_7), codeset), # Saturday
        )

    tformat = locale.nl_langinfo(locale.D_FMT).replace('%y','%Y')
    # GRAMPS treats dates with '-' as ISO format, so replace separator on 
    # locale dates that use '-' to prevent confict
    tformat = tformat.replace('-', '/') 

except:
    import time

    month_to_int = {
        to_uni(time.strftime('%B',(0,1,1,1,1,1,1,1,1)), codeset).lower() : 1,
        to_uni(time.strftime('%b',(0,1,1,1,1,1,1,1,1)), codeset).lower() : 1,
        to_uni(time.strftime('%B',(0,2,1,1,1,1,1,1,1)), codeset).lower() : 2,
        to_uni(time.strftime('%b',(0,2,1,1,1,1,1,1,1)), codeset).lower() : 2,
        to_uni(time.strftime('%B',(0,3,1,1,1,1,1,1,1)), codeset).lower() : 3,
        to_uni(time.strftime('%b',(0,3,1,1,1,1,1,1,1)), codeset).lower() : 3,
        to_uni(time.strftime('%B',(0,4,1,1,1,1,1,1,1)), codeset).lower() : 4,
        to_uni(time.strftime('%b',(0,4,1,1,1,1,1,1,1)), codeset).lower() : 4,
        to_uni(time.strftime('%B',(0,5,1,1,1,1,1,1,1)), codeset).lower() : 5,
        to_uni(time.strftime('%b',(0,5,1,1,1,1,1,1,1)), codeset).lower() : 5,
        to_uni(time.strftime('%B',(0,6,1,1,1,1,1,1,1)), codeset).lower() : 6,
        to_uni(time.strftime('%b',(0,6,1,1,1,1,1,1,1)), codeset).lower() : 6,
        to_uni(time.strftime('%B',(0,7,1,1,1,1,1,1,1)), codeset).lower() : 7,
        to_uni(time.strftime('%b',(0,7,1,1,1,1,1,1,1)), codeset).lower() : 7,
        to_uni(time.strftime('%B',(0,8,1,1,1,1,1,1,1)), codeset).lower() : 8,
        to_uni(time.strftime('%b',(0,8,1,1,1,1,1,1,1)), codeset).lower() : 8,
        to_uni(time.strftime('%B',(0,9,1,1,1,1,1,1,1)), codeset).lower() : 9,
        to_uni(time.strftime('%b',(0,9,1,1,1,1,1,1,1)), codeset).lower() : 9,
        to_uni(time.strftime('%B',(0,10,1,1,1,1,1,1,1)), codeset).lower() : 10,
        to_uni(time.strftime('%b',(0,10,1,1,1,1,1,1,1)), codeset).lower() : 10,
        to_uni(time.strftime('%B',(0,11,1,1,1,1,1,1,1)), codeset).lower() : 11,
        to_uni(time.strftime('%b',(0,11,1,1,1,1,1,1,1)), codeset).lower() : 11,
        to_uni(time.strftime('%B',(0,12,1,1,1,1,1,1,1)), codeset).lower() : 12,
        to_uni(time.strftime('%b',(0,12,1,1,1,1,1,1,1)), codeset).lower() : 12,
       }

    long_months = (
        "",
        to_uni(time.strftime('%B',(0,1,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,2,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,3,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,4,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,5,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,6,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,7,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,8,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,9,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,10,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,11,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%B',(0,12,1,1,1,1,1,1,1)), codeset),
       )

    short_months = (
        "",
        to_uni(time.strftime('%b',(0,1,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,2,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,3,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,4,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,5,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,6,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,7,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,8,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,9,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,10,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,11,1,1,1,1,1,1,1)), codeset),
        to_uni(time.strftime('%b',(0,12,1,1,1,1,1,1,1)), codeset),
       )

    # Gramps day number: Sunday => 1, Monday => 2, etc
    # strftime takes a (from the doc of standard Python library "time")
    #  "tuple or struct_time representing a time as returned by gmtime()
    #   or localtime()"
    # see http://docs.python.org/library/time.html
    # The seventh tuple entry returned by gmtime() is the day-of-the-week
    # number. tm_wday => range [0,6], Monday is 0
    # Note. Only the seventh tuple entry matters. The others are
    # just a dummy.
    long_days = (
        "",
        to_uni(time.strftime('%A',(0,1,1,1,1,1,6,1,1)), codeset), # Sunday
        to_uni(time.strftime('%A',(0,1,1,1,1,1,0,1,1)), codeset), # Monday
        to_uni(time.strftime('%A',(0,1,1,1,1,1,1,1,1)), codeset), # Tuesday
        to_uni(time.strftime('%A',(0,1,1,1,1,1,2,1,1)), codeset), # Wednesday
        to_uni(time.strftime('%A',(0,1,1,1,1,1,3,1,1)), codeset), # Thursday
        to_uni(time.strftime('%A',(0,1,1,1,1,1,4,1,1)), codeset), # Friday
        to_uni(time.strftime('%A',(0,1,1,1,1,1,5,1,1)), codeset), # Saturday
        )

    short_days = (
        "",
        to_uni(time.strftime('%a',(0,1,1,1,1,1,6,1,1)), codeset), # Sunday
        to_uni(time.strftime('%a',(0,1,1,1,1,1,0,1,1)), codeset), # Monday
        to_uni(time.strftime('%a',(0,1,1,1,1,1,1,1,1)), codeset), # Tuesday
        to_uni(time.strftime('%a',(0,1,1,1,1,1,2,1,1)), codeset), # Wednesday
        to_uni(time.strftime('%a',(0,1,1,1,1,1,3,1,1)), codeset), # Thursday
        to_uni(time.strftime('%a',(0,1,1,1,1,1,4,1,1)), codeset), # Friday
        to_uni(time.strftime('%a',(0,1,1,1,1,1,5,1,1)), codeset), # Saturday
        )

    # depending on the locale, the value returned for 20th Feb 2009 could be 
    # of the format '20/2/2009', '20/02/2009', '20.2.2009', '20.02.2009', 
    # '20-2-2009', '20-02-2009', '2009/02/20', '2009.02.20', '2009-02-20', 
    # '09-02-20' hence to reduce the possible values to test, make sure month 
    # is double digit also day should be double digit, prefebably greater than
    # 12 for human readablity

    timestr = time.strftime('%x',(2005,10,25,1,1,1,1,1,1)) 
    
    # GRAMPS treats dates with '-' as ISO format, so replace separator on 
    # locale dates that use '-' to prevent confict
    timestr = timestr.replace('-', '/') 
    time2fmt_map = {
        '25/10/2005' : '%d/%m/%Y',
        '10/25/2005' : '%m/%d/%Y',
        '2005/10/25' : '%Y/%m/%d',
        '25.10.2005' : '%d.%m.%Y',
        '10.25.2005' : '%m.%d.%Y',
        '2005.10.25' : '%Y.%m.%d',
        }
    
    try:
        tformat = time2fmt_map[timestr]
    except KeyError as e:
        tformat = '%d/%m/%Y'  #default value
