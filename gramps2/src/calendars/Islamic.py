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
# Islamic
#
#-------------------------------------------------------------------------
class Islamic(Calendar.Calendar):
    """Islamic calendar"""

    EPOCH = 1948439.5

    MONTHS = [
        "Muharram",     "Safar",          "Rabi`al-Awwal", "Rabi`ath-Thani",
        "Jumada l-Ula", "Jumada t-Tania", "Rajab",         "Sha`ban",
        "Ramadan",      "Shawwal",        "Dhu l-Qa`da",   "Dhu l-Hijja"
        ]

    M2NUM = {
        "muharram" : 1,       "safar" : 2,         "rabi`al-awwal" : 3,
        "rabi`ath-thani" : 4, "jumada l-ula" : 5 , "jumada t-tania" : 6,
        "rajab" : 7,          "sha`ban" : 8,       "ramadan" : 9,
        "shawwal" : 10,       "dhu l-qa`da" : 11,  "dhu l-hijja" : 12
        }

    NAME = "Islamic"
    TNAME = _("Islamic")

    def quote_display(self,year,month,day,mode):
        return "%s (%s)" % (self.display(year,month,day,mode),Islamic.NAME)

    def set_month_string(self,text):
        try:
            return Islamic.M2NUM[unicode(text.lower())]
        except KeyError:
            return Calendar.UNDEF

    def month(self,val):
        try:
            return Islamic.MONTHS[val-1]
        except:
            return "Illegal Month"

    def get_sdn(self,year, month, day):
        v1 = math.ceil(29.5 * (month - 1))
        v2 = (year - 1) * 354
        v3 = math.floor((3 + (11 *year)) / 30)

        return int(math.ceil((day + v1 + v2 + v3 + Islamic.EPOCH) - 1))

    def get_ymd(self,sdn):
        sdn = math.floor(sdn) + 0.5
        year = int(math.floor(((30*(sdn-Islamic.EPOCH))+10646)/10631))
        month = int(min(12, math.ceil((sdn-(29+self.get_sdn(year,1,1)))/29.5) + 1))
        day = int((sdn - self.get_sdn(year,month,1)) + 1)
        return (year,month,day)

Calendar.register(Islamic)
