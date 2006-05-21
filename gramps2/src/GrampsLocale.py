# -*- coding: iso-8859-1 -*- 
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2005  Donald N. Allingham
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

"""
Some OS environments do not support the locale.nl_langinfo() method
of determing month names and other date related information.

If nl_langinfo fails, that means we have to resort to shinanigans with
strftime.

Since these routines return values encoded into selected character
set, we have to convert to unicode.
"""

try:
    codeset = locale.nl_langinfo(locale.CODESET)

    month_to_int = {
        unicode(locale.nl_langinfo(locale.MON_1),codeset).lower()   : 1,
        unicode(locale.nl_langinfo(locale.ABMON_1),codeset).lower() : 1,
        unicode(locale.nl_langinfo(locale.MON_2),codeset).lower()   : 2,
        unicode(locale.nl_langinfo(locale.ABMON_2),codeset).lower() : 2,
        unicode(locale.nl_langinfo(locale.MON_3),codeset).lower()   : 3,
        unicode(locale.nl_langinfo(locale.ABMON_3),codeset).lower() : 3,
        unicode(locale.nl_langinfo(locale.MON_4),codeset).lower()   : 4,
        unicode(locale.nl_langinfo(locale.ABMON_4),codeset).lower() : 4,
        unicode(locale.nl_langinfo(locale.MON_5),codeset).lower()   : 5,
        unicode(locale.nl_langinfo(locale.ABMON_5),codeset).lower() : 5,
        unicode(locale.nl_langinfo(locale.MON_6),codeset).lower()   : 6,
        unicode(locale.nl_langinfo(locale.ABMON_6),codeset).lower() : 6,
        unicode(locale.nl_langinfo(locale.MON_7),codeset).lower()   : 7,
        unicode(locale.nl_langinfo(locale.ABMON_7),codeset).lower() : 7,
        unicode(locale.nl_langinfo(locale.MON_8),codeset).lower()   : 8,
        unicode(locale.nl_langinfo(locale.ABMON_8),codeset).lower() : 8,
        unicode(locale.nl_langinfo(locale.MON_9),codeset).lower()   : 9,
        unicode(locale.nl_langinfo(locale.ABMON_9),codeset).lower() : 9,
        unicode(locale.nl_langinfo(locale.MON_10),codeset).lower()  : 10,
        unicode(locale.nl_langinfo(locale.ABMON_10),codeset).lower(): 10,
        unicode(locale.nl_langinfo(locale.MON_11),codeset).lower()  : 11,
        unicode(locale.nl_langinfo(locale.ABMON_11),codeset).lower(): 11,
        unicode(locale.nl_langinfo(locale.MON_12),codeset).lower()  : 12,
        unicode(locale.nl_langinfo(locale.ABMON_12),codeset).lower(): 12,
       }

    long_months = (
        "",
        unicode(locale.nl_langinfo(locale.MON_1),codeset),
        unicode(locale.nl_langinfo(locale.MON_2),codeset),
        unicode(locale.nl_langinfo(locale.MON_3),codeset),
        unicode(locale.nl_langinfo(locale.MON_4),codeset),
        unicode(locale.nl_langinfo(locale.MON_5),codeset),
        unicode(locale.nl_langinfo(locale.MON_6),codeset),
        unicode(locale.nl_langinfo(locale.MON_7),codeset),
        unicode(locale.nl_langinfo(locale.MON_8),codeset),
        unicode(locale.nl_langinfo(locale.MON_9),codeset),
        unicode(locale.nl_langinfo(locale.MON_10),codeset),
        unicode(locale.nl_langinfo(locale.MON_11),codeset),
        unicode(locale.nl_langinfo(locale.MON_12),codeset),
        )

    short_months = (
        "",
        unicode(locale.nl_langinfo(locale.ABMON_1),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_2),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_3),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_4),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_5),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_6),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_7),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_8),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_9),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_10),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_11),codeset),
        unicode(locale.nl_langinfo(locale.ABMON_12),codeset),
        )

    long_days = (
        "",
        unicode(locale.nl_langinfo(locale.DAY_1),codeset),
        unicode(locale.nl_langinfo(locale.DAY_2),codeset),
        unicode(locale.nl_langinfo(locale.DAY_3),codeset),
        unicode(locale.nl_langinfo(locale.DAY_4),codeset),
        unicode(locale.nl_langinfo(locale.DAY_5),codeset),
        unicode(locale.nl_langinfo(locale.DAY_6),codeset),
        unicode(locale.nl_langinfo(locale.DAY_7),codeset),
        )
        
    short_days = (
        "",
        unicode(locale.nl_langinfo(locale.ABDAY_1),codeset),
        unicode(locale.nl_langinfo(locale.ABDAY_2),codeset),
        unicode(locale.nl_langinfo(locale.ABDAY_3),codeset),
        unicode(locale.nl_langinfo(locale.ABDAY_4),codeset),
        unicode(locale.nl_langinfo(locale.ABDAY_5),codeset),
        unicode(locale.nl_langinfo(locale.ABDAY_6),codeset),
        unicode(locale.nl_langinfo(locale.ABDAY_7),codeset),
        )

    tformat = locale.nl_langinfo(locale.D_FMT).replace('%y','%Y')

except:
    import time

    codeset = locale.getpreferredencoding()

    month_to_int = {
        unicode(time.strftime('%B',(0,1,1,1,1,1,1,1,1)),codeset).lower() : 1,
        unicode(time.strftime('%b',(0,1,1,1,1,1,1,1,1)),codeset).lower() : 1,
        unicode(time.strftime('%B',(0,2,1,1,1,1,1,1,1)),codeset).lower() : 2,
        unicode(time.strftime('%b',(0,2,1,1,1,1,1,1,1)),codeset).lower() : 2,
        unicode(time.strftime('%B',(0,3,1,1,1,1,1,1,1)),codeset).lower() : 3,
        unicode(time.strftime('%b',(0,3,1,1,1,1,1,1,1)),codeset).lower() : 3,
        unicode(time.strftime('%B',(0,4,1,1,1,1,1,1,1)),codeset).lower() : 4,
        unicode(time.strftime('%b',(0,4,1,1,1,1,1,1,1)),codeset).lower() : 4,
        unicode(time.strftime('%B',(0,5,1,1,1,1,1,1,1)),codeset).lower() : 5,
        unicode(time.strftime('%b',(0,5,1,1,1,1,1,1,1)),codeset).lower() : 5,
        unicode(time.strftime('%B',(0,6,1,1,1,1,1,1,1)),codeset).lower() : 6,
        unicode(time.strftime('%b',(0,6,1,1,1,1,1,1,1)),codeset).lower() : 6,
        unicode(time.strftime('%B',(0,7,1,1,1,1,1,1,1)),codeset).lower() : 7,
        unicode(time.strftime('%b',(0,7,1,1,1,1,1,1,1)),codeset).lower() : 7,
        unicode(time.strftime('%B',(0,8,1,1,1,1,1,1,1)),codeset).lower() : 8,
        unicode(time.strftime('%b',(0,8,1,1,1,1,1,1,1)),codeset).lower() : 8,
        unicode(time.strftime('%B',(0,9,1,1,1,1,1,1,1)),codeset).lower() : 9,
        unicode(time.strftime('%b',(0,9,1,1,1,1,1,1,1)),codeset).lower() : 9,
        unicode(time.strftime('%B',(0,10,1,1,1,1,1,1,1)),codeset).lower() : 10,
        unicode(time.strftime('%b',(0,10,1,1,1,1,1,1,1)),codeset).lower() : 10,
        unicode(time.strftime('%B',(0,11,1,1,1,1,1,1,1)),codeset).lower() : 11,
        unicode(time.strftime('%b',(0,11,1,1,1,1,1,1,1)),codeset).lower() : 11,
        unicode(time.strftime('%B',(0,12,1,1,1,1,1,1,1)),codeset).lower() : 12,
        unicode(time.strftime('%b',(0,12,1,1,1,1,1,1,1)),codeset).lower() : 12,
       }

    long_months = (
        "",
        unicode(time.strftime('%B',(0,1,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,2,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,3,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,4,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,5,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,6,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,7,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,8,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,9,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,10,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,11,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%B',(0,12,1,1,1,1,1,1,1)),codeset),
       )

    short_months = (
        "",
        unicode(time.strftime('%b',(0,1,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,2,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,3,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,4,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,5,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,6,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,7,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,8,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,9,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,10,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,11,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%b',(0,12,1,1,1,1,1,1,1)),codeset),
       )
       
    long_days = (
        "",
        unicode(time.strftime('%A',(0,1,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%A',(0,1,1,1,1,1,2,1,1)),codeset),
        unicode(time.strftime('%A',(0,1,1,1,1,1,3,1,1)),codeset),
        unicode(time.strftime('%A',(0,1,1,1,1,1,4,1,1)),codeset),
        unicode(time.strftime('%A',(0,1,1,1,1,1,5,1,1)),codeset),
        unicode(time.strftime('%A',(0,1,1,1,1,1,6,1,1)),codeset),
        unicode(time.strftime('%A',(0,1,1,1,1,1,7,1,1)),codeset),
        )
        
    short_days = (
        "",
        unicode(time.strftime('%a',(0,1,1,1,1,1,1,1,1)),codeset),
        unicode(time.strftime('%a',(0,1,1,1,1,1,2,1,1)),codeset),
        unicode(time.strftime('%a',(0,1,1,1,1,1,3,1,1)),codeset),
        unicode(time.strftime('%a',(0,1,1,1,1,1,4,1,1)),codeset),
        unicode(time.strftime('%a',(0,1,1,1,1,1,5,1,1)),codeset),
        unicode(time.strftime('%a',(0,1,1,1,1,1,6,1,1)),codeset),
        unicode(time.strftime('%a',(0,1,1,1,1,1,7,1,1)),codeset),
        )

    if time.strftime('%x',(2005,1,2,1,1,1,1,1,1)) == '2/1/2005':
        tformat = '%d/%m/%y'
    else:
        tformat = '%m/%d/%y'

