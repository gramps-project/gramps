# -*- coding: utf-8 -*-
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
# FrenchRepublic
#
#-------------------------------------------------------------------------
class FrenchRepublic(Calendar.Calendar):
    """French Republic Calendar"""

    SDN_OFFSET         = 2375474
    DAYS_PER_4_YEARS   = 1461
    DAYS_PER_MONTH     = 30
    FIRST_VALID        = 2375840
    LAST_VALID         = 2380952

    MONTHS = [
        unicode("Vendémiaire",'latin-1'),  unicode("Brumaire",'latin-1'),
        unicode("Frimaire",'latin-1'),     unicode("Nivôse",'latin-1'),
        unicode("Pluviôse",'latin-1'),     unicode("Ventôse",'latin-1'),
        unicode("Germinal",'latin-1'),     unicode("Floréal",'latin-1'),
        unicode("Prairial",'latin-1'),     unicode("Messidor",'latin-1'),
        unicode("Thermidor",'latin-1'),    unicode("Fructidor",'latin-1'),
        unicode("Extra",'latin-1'),]

    M2NUM = {
        "vend" : 1, "brum" : 2, "frim" : 3, "nivo" : 4, "pluv" : 5, "vent" : 6,
        "germ" : 7, "flor" : 8, "prai" : 9, "mess" :10, "ther" :11, "fruc" :12,
        "extr" : 13,"comp" :13, unicode("nivô",'latin-1') : 4
        }

    NAME = "French Republican"
    TNAME = _("French Republican")

    def quote_display(self,year,month,day,mode):
        return "%s (%s)" % (self.display(year,month,day,mode),FrenchRepublic.NAME)

    def mlen(self):
        return 4

    def month(self,val):
        try:
            return FrenchRepublic.MONTHS[val-1]
        except:
            return "Illegal Month"

    def set_month_string(self,text):
        val = (unicode(text)[0:4]).lower()
        try:
            return FrenchRepublic.M2NUM[val]
        except KeyError:
            return Calendar.UNDEF

    def get_sdn(self,y,m,d):
        """Converts a French Republican Calendar date to an SDN number"""
        if (y < 1 or y > 14 or m < 1 or m > 13 or d < 1 or d > 30):
            return 0
        return (y*FrenchRepublic.DAYS_PER_4_YEARS)/4 + \
               (m-1)*FrenchRepublic.DAYS_PER_MONTH + \
               d + FrenchRepublic.SDN_OFFSET

    def get_ymd(self,sdn):
        """Converts an SDN number to a French Republican Calendar date"""
        if (sdn < FrenchRepublic.FIRST_VALID or sdn > FrenchRepublic.LAST_VALID) :
            return (0,0,0)
        temp = (sdn-FrenchRepublic.SDN_OFFSET)*4 - 1
        year = temp/FrenchRepublic.DAYS_PER_4_YEARS
        dayOfYear = (temp%FrenchRepublic.DAYS_PER_4_YEARS)/4
        month = (dayOfYear/FrenchRepublic.DAYS_PER_MONTH)+1
        day = (dayOfYear%FrenchRepublic.DAYS_PER_MONTH)+1
        return (year,month,day)

Calendar.register(FrenchRepublic)
