# -*- coding: iso-8859-1 -*- 
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
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

"""
U.S English date display class. Should serve as the base class for all
localized tasks.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".DateDisplay")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from RelLib import Date
import GrampsLocale

#-------------------------------------------------------------------------
#
# DateDisplay
#
#-------------------------------------------------------------------------
class DateDisplay:

    _months = GrampsLocale.long_months
    _MONS   = GrampsLocale.short_months

    _tformat = GrampsLocale.tformat

    _hebrew = (
        "", "Tishri", "Heshvan", "Kislev", "Tevet", "Shevat",
        "AdarI", "AdarII", "Nisan", "Iyyar", "Sivan", "Tammuz",
        "Av", "Elul"
        )
    
    _french = (
        '',
        unicode("Vendémiaire",'latin-1'),
        'Brumaire',
        'Frimaire',
        unicode("Nivôse",'latin-1'),
        unicode("Pluviôse",'latin-1'),
        unicode("Ventôse",'latin-1'),
        'Germinal',
        unicode("Floréal",'latin-1'),
        'Prairial',
        'Messidor',
        'Thermidor',
        'Fructidor',
        'Extra'
        )
    
    _persian = (
        "", "Farvardin", "Ordibehesht", "Khordad", "Tir",
        "Mordad", "Shahrivar", "Mehr", "Aban", "Azar",
        "Dey", "Bahman", "Esfand"
        )
    
    _islamic = (
        "", "Muharram", "Safar", "Rabi`al-Awwal", "Rabi`ath-Thani",
        "Jumada l-Ula", "Jumada t-Tania", "Rajab", "Sha`ban",
        "Ramadan", "Shawwal", "Dhu l-Qa`da", "Dhu l-Hijja"
        )

    formats = ("YYYY-MM-DD (ISO)",)

    calendar = (
        ""," (Julian)"," (Hebrew)"," (French Republican)",
        " (Persian)"," (Islamic)"
        )
    
    _mod_str = ("","before ","after ","about ","","","")

    _qual_str = ("","estimated ","calculated ")
    
    _bce_str = "%s B.C.E."

    def __init__(self,format=None):
        self.display_cal = [
            self._display_gregorian,
            self._display_julian,
            self._display_hebrew,
            self._display_french,
            self._display_persian,
            self._display_islamic,
            ]

        self.verify_format(format)
        if format == None:
            self.format = 0
        else:
            self.format = format

    def set_format(self,format):
        self.format = format

    def verify_format(self,format):
        pass

    def quote_display(self,date):
        """
        Similar to the display task, except that if the value is a text only
        value, it is enclosed in quotes.
        """
        if date.get_modifier() == Date.MOD_TEXTONLY:
            return '"%s"' % self.display(date)
        else:
            return self.display(date)

    def display(self,date):
        """
        Returns a text string representing the date.
        """
        mod = date.get_modifier()
        cal = date.get_calendar()
        qual = date.get_quality()
        start = date.get_start_date()

        qual_str = self._qual_str[qual]
        
        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN or mod == Date.MOD_RANGE:
            d1 = self.display_iso(start)
            d2 = self.display_iso(date.get_stop_date())
            return "%s %s - %s%s" % (qual_str,d1,d2,self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_iso(start)
            d2 = self.display_iso(date.get_stop_date())
            return "%s %s - %s%s" % (qual_str,d1,d2,self.calendar[cal])
        else:
            text = self.display_iso(start)
            return "%s%s%s%s" % (qual_str,self._mod_str[mod],text,self.calendar[cal])

    def _slash_year(self,val,slash):
        if val < 0:
            val = - val
            
        if slash:
            year = "%d/%d" % (val,(val%10)+1)
        else:
            year = "%d" % (val)
        
        return year
        
    def display_iso(self,date_val):
        # YYYY-MM-DD (ISO)
        year = self._slash_year(date_val[2],date_val[3])
        if date_val[0] == 0:
            if date_val[1] == 0:
                value = year
            else:
                value = "%s-%02d" % (year,date_val[1])
        else:
            value = "%s-%02d-%02d" % (year,date_val[1],date_val[0])
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    def text_display(self,date):
        """
        Similar to the display task, except that if the value is a text only
        value, it is enclosed in quotes.
        """
        return date.get_text()
        

    def _display_gregorian(self,date_val):
        year = self._slash_year(date_val[2],date_val[3])
        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
            if date_val[0] == 0 and date_val[1] == 0:
                value = str(date_val[2])
            else:
                value = self._tformat.replace('%m',str(date_val[1]))
                value = value.replace('%d',str(date_val[0]))
                value = value.replace('%Y',str(abs(date_val[2])))
                value = value.replace('-','/')
        elif self.format == 2:
            # Month Day, Year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self._months[date_val[1]],year)
            else:
                value = "%s %d, %s" % (self._months[date_val[1]],date_val[0],year)
        elif self.format == 3:
            # MON Day, Year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self._MONS[date_val[1]],year)
            else:
                value = "%s %d, %s" % (self._MONS[date_val[1]],date_val[0],year)
        elif self.format == 4:
            # Day Month Year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self._months[date_val[1]],year)
            else:
                value = "%d %s %s" % (date_val[0],self._months[date_val[1]],year)
        else:
            # Day MON Year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self._MONS[date_val[1]],year)
            else:
                value = "%d %s %s" % (date_val[0],self._MONS[date_val[1]],year)
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    def _display_julian(self,date_val):
        # Julian date display is the same as Gregorian
        return self._display_gregorian(date_val)

    def _display_calendar(self,date_val,month_list):
        year = abs(date_val[2])
        if self.format == 0 or self.format == 1:
            return self.display_iso(date_val)
        else:
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = u"%s %d" % (month_list[date_val[1]],year)
            else:
                value = u"%s %d, %s" % (month_list[date_val[1]],date_val[0],year)
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    def _display_french(self,date_val):
        year = abs(date_val[2])
        if self.format == 0 or self.format == 1:
            return self.display_iso(date_val)
        else:
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = u"%s %d" % (self._french[date_val[1]],year)
            else:
                value = u"%d %s %s" % (date_val[0],self._french[date_val[1]],year)
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    def _display_hebrew(self,date_val):
        return self._display_calendar(date_val,self._hebrew)

    def _display_persian(self,date_val):
        return self._display_calendar(date_val,self._persian)

    def _display_islamic(self,date_val):
        return self._display_calendar(date_val,self._islamic)

class DateDisplayEn(DateDisplay):
    """
    English language date display class. 
    """

    formats = (
        "YYYY-MM-DD (ISO)", "Numerical", "Month Day, Year",
        "MON DAY, YEAR", "Day Month Year", "DAY MON YEAR"
        )

    def __init__(self,format=None):
        """
        Creates a DateDisplay class that converts a Date object to a string
        of the desired format. The format value must correspond to the format
        list value (DateDisplay.format[]).
        """

        DateDisplay.__init__(self,format)

    def display(self,date):
        """
        Returns a text string representing the date.
        """
        mod = date.get_modifier()
        cal = date.get_calendar()
        qual = date.get_quality()
        start = date.get_start_date()

        qual_str = self._qual_str[qual]
        
        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%sfrom %s to %s%s" % (qual_str,d1,d2,self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%sbetween %s and %s%s" % (qual_str,d1,d2,
                                              self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str,self._mod_str[mod],
                                 text,self.calendar[cal])
