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
# Gramps Modules
#
#-------------------------------------------------------------------------
import Calendar
from intl import gettext as _

#-------------------------------------------------------------------------
#
# Gregorian
#
#-------------------------------------------------------------------------
class Gregorian(Calendar.Calendar):
    """Gregorian Calendar"""

    SDN_OFFSET         = 32045
    DAYS_PER_5_MONTHS  = 153
    DAYS_PER_4_YEARS   = 1461
    DAYS_PER_400_YEARS = 146097

    NAME = "Gregorian"
    TNAME = _("Gregorian")

    def quote_display(self,year,month,day,mode):
        return self.display(year,month,day,mode)

    def mlen(self):
        return 3

    def get_ymd(self,sdn):
        """Converts an SDN number to a gregorial date"""
        if sdn <= 0:
            return (0,0,0)

        temp = (Gregorian.SDN_OFFSET + sdn) * 4 - 1

        # Calculate the century (year/100)
        century = temp / Gregorian.DAYS_PER_400_YEARS

        # Calculate the year and day of year (1 <= dayOfYear <= 366)

        temp = ((temp % Gregorian.DAYS_PER_400_YEARS) / 4) * 4 + 3
        year = (century * 100) + (temp / Gregorian.DAYS_PER_4_YEARS)
        dayOfYear = (temp % Gregorian.DAYS_PER_4_YEARS) / 4 + 1
        
        # Calculate the month and day of month
        temp = dayOfYear * 5 - 3
        month = temp / Gregorian.DAYS_PER_5_MONTHS
        day = (temp % Gregorian.DAYS_PER_5_MONTHS) / 5 + 1
        
        # Convert to the normal beginning of the year
        if month < 10 :
            month = month + 3
        else:
            year = year + 1
            month = month - 9
            
        # Adjust to the B.C./A.D. type numbering

        year = year - 4800
        if year <= 0:
            year = year - 1

        return (year,month,day)

    def get_sdn(self,iyear,imonth,iday):
        """Converts a gregorian date to an SDN number"""
        # check for invalid dates 
        if iyear==0 or iyear<-4714 or imonth<=0 or imonth>12 or iday<=0 or iday>31:
            return 0

        # check for dates before SDN 1 (Nov 25, 4714 B.C.)
        if iyear == -4714:
            if imonth < 11 or imonth == 11 and iday < 25:
                return 0

        if iyear < 0:
            year = iyear + 4801
        else:
            year = iyear + 4800

        # Adjust the start of the year

        if imonth > 2:
            month = imonth - 3
        else:
            month = imonth + 9
            year = year - 1

        return( ((year / 100) * Gregorian.DAYS_PER_400_YEARS) / 4
                + ((year % 100) * Gregorian.DAYS_PER_4_YEARS) / 4
                + (month * Gregorian.DAYS_PER_5_MONTHS + 2) / 5
                + iday
                - Gregorian.SDN_OFFSET );

    def check(self,year,month,day):
        if year > 2100 or month > 12 or day > 31:
            return 0
        return 1

Calendar.register(Gregorian)
