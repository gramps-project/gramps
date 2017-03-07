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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import locale
from ..const import GRAMPS_LOCALE as glocale

"""
Some OS environments do not support the locale.nl_langinfo() method
of determing month names and other date related information.

If nl_langinfo fails, that means we have to resort to shinanigans with
strftime.

Since these routines return values encoded into selected character
set, we have to convert to unicode.
"""
codeset = glocale.encoding

try:

    # here only for the upgrade tool, see _datestrings.py __main__
    _deprecated_long_months = (
        "",
        locale.nl_langinfo(locale.MON_1),
        locale.nl_langinfo(locale.MON_2),
        locale.nl_langinfo(locale.MON_3),
        locale.nl_langinfo(locale.MON_4),
        locale.nl_langinfo(locale.MON_5),
        locale.nl_langinfo(locale.MON_6),
        locale.nl_langinfo(locale.MON_7),
        locale.nl_langinfo(locale.MON_8),
        locale.nl_langinfo(locale.MON_9),
        locale.nl_langinfo(locale.MON_10),
        locale.nl_langinfo(locale.MON_11),
        locale.nl_langinfo(locale.MON_12),
        )

    _deprecated_short_months = (
        "",
        locale.nl_langinfo(locale.ABMON_1),
        locale.nl_langinfo(locale.ABMON_2),
        locale.nl_langinfo(locale.ABMON_3),
        locale.nl_langinfo(locale.ABMON_4),
        locale.nl_langinfo(locale.ABMON_5),
        locale.nl_langinfo(locale.ABMON_6),
        locale.nl_langinfo(locale.ABMON_7),
        locale.nl_langinfo(locale.ABMON_8),
        locale.nl_langinfo(locale.ABMON_9),
        locale.nl_langinfo(locale.ABMON_10),
        locale.nl_langinfo(locale.ABMON_11),
        locale.nl_langinfo(locale.ABMON_12),
        )

    # Gramps day number: Sunday => 1, Monday => 2, etc
    # "Return name of the n-th day of the week. Warning:
    #  This follows the US convention of DAY_1 being Sunday,
    #  not the international convention (ISO 8601) that Monday
    #  is the first day of the week."
    # see http://docs.python.org/library/locale.html
    _deprecated_long_days = (
        "",
        locale.nl_langinfo(locale.DAY_1), # Sunday
        locale.nl_langinfo(locale.DAY_2), # Monday
        locale.nl_langinfo(locale.DAY_3), # Tuesday
        locale.nl_langinfo(locale.DAY_4), # Wednesday
        locale.nl_langinfo(locale.DAY_5), # Thursday
        locale.nl_langinfo(locale.DAY_6), # Friday
        locale.nl_langinfo(locale.DAY_7), # Saturday
        )

    _deprecated_short_days = (
        "",
        locale.nl_langinfo(locale.ABDAY_1), # Sunday
        locale.nl_langinfo(locale.ABDAY_2), # Monday
        locale.nl_langinfo(locale.ABDAY_3), # Tuesday
        locale.nl_langinfo(locale.ABDAY_4), # Wednesday
        locale.nl_langinfo(locale.ABDAY_5), # Thursday
        locale.nl_langinfo(locale.ABDAY_6), # Friday
        locale.nl_langinfo(locale.ABDAY_7), # Saturday
        )

    tformat = locale.nl_langinfo(locale.D_FMT).replace('%y','%Y')
    # Gramps treats dates with '-' as ISO format, so replace separator on
    # locale dates that use '-' to prevent confict
    tformat = tformat.replace('-', '/')

except:
    import time

    _deprecated_long_months = (
        "",
        time.strftime('%B',(1,1,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,2,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,3,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,4,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,5,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,6,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,7,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,8,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,9,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,10,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,11,1,1,1,1,1,1,1)),
        time.strftime('%B',(1,12,1,1,1,1,1,1,1)),
       )

    _deprecated_short_months = (
        "",
        time.strftime('%b',(1,1,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,2,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,3,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,4,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,5,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,6,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,7,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,8,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,9,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,10,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,11,1,1,1,1,1,1,1)),
        time.strftime('%b',(1,12,1,1,1,1,1,1,1)),
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
    _deprecated_long_days = (
        "",
        time.strftime('%A',(1,1,1,1,1,1,6,1,1)), # Sunday
        time.strftime('%A',(1,1,1,1,1,1,0,1,1)), # Monday
        time.strftime('%A',(1,1,1,1,1,1,1,1,1)), # Tuesday
        time.strftime('%A',(1,1,1,1,1,1,2,1,1)), # Wednesday
        time.strftime('%A',(1,1,1,1,1,1,3,1,1)), # Thursday
        time.strftime('%A',(1,1,1,1,1,1,4,1,1)), # Friday
        time.strftime('%A',(1,1,1,1,1,1,5,1,1)), # Saturday
        )

    _deprecated_short_days = (
        "",
        time.strftime('%a',(1,1,1,1,1,1,6,1,1)), # Sunday
        time.strftime('%a',(1,1,1,1,1,1,0,1,1)), # Monday
        time.strftime('%a',(1,1,1,1,1,1,1,1,1)), # Tuesday
        time.strftime('%a',(1,1,1,1,1,1,2,1,1)), # Wednesday
        time.strftime('%a',(1,1,1,1,1,1,3,1,1)), # Thursday
        time.strftime('%a',(1,1,1,1,1,1,4,1,1)), # Friday
        time.strftime('%a',(1,1,1,1,1,1,5,1,1)), # Saturday
        )

    # depending on the locale, the value returned for 20th Feb 2009 could be
    # of the format '20/2/2009', '20/02/2009', '20.2.2009', '20.02.2009',
    # '20-2-2009', '20-02-2009', '2009/02/20', '2009.02.20', '2009-02-20',
    # '09-02-20' hence to reduce the possible values to test, make sure month
    # is double digit also day should be double digit, preferably greater than
    # 12 for human readablity

    timestr = time.strftime('%x',(2005,10,25,1,1,1,1,1,1))

    # Gramps treats dates with '-' as ISO format, so replace separator on
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
