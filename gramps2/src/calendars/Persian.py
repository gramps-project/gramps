#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  Donald N. Allingham
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
"""
Gregorian calendar module for GRAMPS. 

The original algorithms for this module came from Scott E. Lee's
C implementation. The original C source can be found at Scott's
web site at http://www.scottlee.com
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import math

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import Calendar
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Persian
#
#-------------------------------------------------------------------------
class Persian(Calendar.Calendar):
    """Persian Calendar"""

    EPOCH = 1948320.5
    SDN_475_1_1 = 2121446

    MONTHS = [ "Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad",
               "Shahrivar", "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand" ]

    M2NUM = {
        "farvardin" : 1,   "ordibehesht" : 2,     "khordad" : 3,
        "tir" : 4,         "mordad" : 5,          "shahrivar" : 6,
        "mehr" : 7,        "aban" : 8,            "azar" : 9,
        "dey" : 10,        "bahman" : 11,         "esfand" : 12
        }

    NAME = "Persian"
    TNAME = _("Persian")

    def quote_display(self,year,month,day,mode):
        return "%s (%s)" % (self.display(year,month,day,mode),Persian.NAME)

    def set_month_string(self,text):
        try:
            return Persian.M2NUM[unicode(text.lower())]
        except KeyError:
            return Calendar.UNDEF

    def month(self,val):
        try:
            return Persian.MONTHS[val-1]
        except:
            return "Illegal Month"

    def get_sdn(self,year, month, day):
        if year >= 0:
            epbase = year - 474
        else:
            epbase = year - 473
        
        epyear = 474 + epbase % 2820

        if month <= 7:
            v1 = (month - 1) * 31
        else:
            v1 = ((month - 1) * 30) + 6
        v2 = math.floor(((epyear * 682) - 110) / 2816)
        v3 = (epyear - 1) * 365 + day
        v4 = math.floor(epbase / 2820) * 1029983
        
        return int(math.ceil(v1 + v2 + v3 + v4 + Persian.EPOCH - 1))

    def get_ymd(self,sdn):
        sdn = math.floor(sdn) + 0.5
        
        depoch = sdn - self.get_sdn(475,1,1)
        cycle = math.floor(depoch / 1029983)
        cyear = depoch % 1029983
        if cyear == 1029982:
            ycycle = 2820
        else:
            aux1 = math.floor(cyear / 366)
            aux2 = cyear % 366
            ycycle = math.floor(((2134 * aux1) + (2816 * aux2) + 2815) / 1028522) + aux1 + 1;
            
        year = ycycle + (2820 * cycle) + 474
        if year <= 0:
            year = year - 1;

        yday = sdn - self.get_sdn(year, 1, 1) + 1
        if yday < 186:
            month = math.ceil(yday / 31)
        else:
            month = math.ceil((yday - 6) / 30)
        day = (sdn - self.get_sdn(year, month, 1)) + 1
        return (int(year), int(month), int(day))

Calendar.register(Persian)
