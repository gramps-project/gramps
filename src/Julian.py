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
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Julian
#
#-------------------------------------------------------------------------
class Julian(Calendar.Calendar):
    """Julian calendar"""

    SDN_OFFSET        = 32083
    DAYS_PER_5_MONTHS = 153
    DAYS_PER_4_YEARS  = 1461

    NAME = "Julian"
    TNAME = _("Julian")

    def quote_display(self,year,month,day,mode):
        return "%s (%s)" % (self.display(year,month,day,mode),Julian.NAME)

    def mlen(self):
        return 3

    def get_ymd(self,sdn):
        """Converts an SDN number to a Julian date"""
        if sdn <= 0 :
            return (0,0,0)

        temp = (sdn + Julian.SDN_OFFSET) * 4 - 1

        # Calculate the year and day of year (1 <= dayOfYear <= 366)
        year = temp / Julian.DAYS_PER_4_YEARS
        dayOfYear = (temp % Julian.DAYS_PER_4_YEARS) / 4 + 1

        # Calculate the month and day of month
        temp = dayOfYear * 5 - 3;
        month = temp / Julian.DAYS_PER_5_MONTHS;
        day = (temp % Julian.DAYS_PER_5_MONTHS) / 5 + 1;
        
        # Convert to the normal beginning of the year
        if month < 10:
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
        """Converts a Julian calendar date to an SDN number"""

        # check for invalid dates
        if iyear==0 or iyear<-4713 or imonth<=0 or imonth>12 or iday<=0 or iday>31:
            return 0

        # check for dates before SDN 1 (Jan 2, 4713 B.C.)
        if iyear == -4713:
            if imonth == 1 and iday == 1:
                return 0

        # Make year always a positive number
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

        return (year*Julian.DAYS_PER_4_YEARS)/4 + \
               (month*Julian.DAYS_PER_5_MONTHS+2)/5 + \
               iday - Julian.SDN_OFFSET

Calendar.register(Julian)
