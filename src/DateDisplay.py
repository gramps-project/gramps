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

"""
U.S English date display class. Should serve as the base class for all
localized tasks.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

import Date
import locale
from gettext import gettext as _


class DateDisplay:

    # determine the code set returned by nl_langinfo
    _codeset = locale.nl_langinfo(locale.CODESET)
    
    # get month information from nl_langinfo. Since nl_langinfo
    # returns data in the code set specified by the user, and
    # gnome wants unicode, we need to convert each string from
    # the native code set into unicode
    _months = (
        "",
        unicode(locale.nl_langinfo(locale.MON_1),_codeset),
        unicode(locale.nl_langinfo(locale.MON_2),_codeset),
        unicode(locale.nl_langinfo(locale.MON_3),_codeset),
        unicode(locale.nl_langinfo(locale.MON_4),_codeset),
        unicode(locale.nl_langinfo(locale.MON_5),_codeset),
        unicode(locale.nl_langinfo(locale.MON_6),_codeset),
        unicode(locale.nl_langinfo(locale.MON_7),_codeset),
        unicode(locale.nl_langinfo(locale.MON_8),_codeset),
        unicode(locale.nl_langinfo(locale.MON_9),_codeset),
        unicode(locale.nl_langinfo(locale.MON_10),_codeset),
        unicode(locale.nl_langinfo(locale.MON_11),_codeset),
        unicode(locale.nl_langinfo(locale.MON_12),_codeset),
        )

    _MONS = (
        "",
        unicode(locale.nl_langinfo(locale.ABMON_1),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_2),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_3),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_4),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_5),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_6),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_7),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_8),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_9),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_10),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_11),_codeset),
        unicode(locale.nl_langinfo(locale.ABMON_12),_codeset),
        )

    _tformat = locale.nl_langinfo(locale.D_FMT).replace('%y','%Y')
    
    _hebrew = (
        "", "Tishri", "Heshvan", "Kislev", "Tevet", "Shevat",
        "AdarI", "AdarII", "Nisan", "Iyyar", "Sivan", "Tammuz",
        "Av", "Elul"
        )
    
    _french = (
        '',           u'Vend\xc3\xa9miaire', 'Brumaire',
        'Frimaire',   u'Niv\xc3\xb4se',      u'Pluvi\xc3\xb4se',
        u'Vent\xc3\xb4se', 'Germinal',       u'Flor\xc3\xa9al',
        'Prairial',   'Messidor',       'Thermidor',
        'Fructidor',  'Extra'
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
            # self._bce_str is a localizes string that prints B.C.E. at the apropriate place
            format_string = self._bce_str
        else:
            format_string = "%s"
            
        if slash:
            year = "%d/%d" % (val,(val%10)+1)
        else:
            year = "%d" % (val)
        
        return format_string % year
        
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
            value = self.display_iso(date_val)
        elif self.format == 1:
            if date_val[0] == 0 and date_val[1] == 0:
                value = str(date_val[2])
            else:
                value = self._tformat.replace('%m',str(date_val[1]))
                value = value.replace('%d',str(date_val[0]))
                value = value.replace('%Y',str(date_val[2]))
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
        return value

    def _display_julian(self,date_val):
        # Julian date display is the same as Gregorian
        return self._display_gregorian(date_val)

    def _display_calendar(self,date_val,month_list):
        year = date_val[2]
        if self.format == 0 or self.format == 1:
            return self.display_iso(date_val)
        else:
            if date_val[0] == 0:
                if date_val[1] == 0:
                    return year
                else:
                    return "%s %d" % (month_list[date_val[1]],year)
            else:
                return "%s %d, %s" % (month_list[date_val[1]],date_val[0],year)

    def _display_french(self,date_val):
        return self._display_calendar(date_val,self._french)

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
        _("YYYY-MM-DD (ISO)"), _("Numerical"), _("Month Day, Year"),
        _("MON DAY, YEAR"), _("Day Month Year"), _("DAY MON YEAR")
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
