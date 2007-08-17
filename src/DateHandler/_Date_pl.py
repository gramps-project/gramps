# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
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

# Polish version 2007 by Piotr Czubaszek

"""
Polish-specific classes for parsing and displaying dates.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import re

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from RelLib import Date
from _DateParser import DateParser
from _DateDisplay import DateDisplay
from _DateHandler import register_datehandler

#-------------------------------------------------------------------------
#
# Polish parser
#
#-------------------------------------------------------------------------
class DateParserPL(DateParser):

    month_to_int = DateParser.month_to_int
    month_to_int[u"styczeń"] = 1
    month_to_int[u"sty"] = 1
    month_to_int[u"I"] = 1
    month_to_int[u"luty"]  = 2
    month_to_int[u"lut"]  = 2
    month_to_int[u"II"]  = 2
    month_to_int[u"marzec"]  = 3
    month_to_int[u"mar"]  = 3
    month_to_int[u"III"]  = 3
    month_to_int[u"kwiecień"]  = 4
    month_to_int[u"kwi"]  = 4
    month_to_int[u"IV"]  = 4
    month_to_int[u"maj"]  = 5
    month_to_int[u"V"]  = 5
    month_to_int[u"czerwiec"]  = 6
    month_to_int[u"cze"]  = 6
    month_to_int[u"VI"]  = 6
    month_to_int[u"lipiec"]  = 7
    month_to_int[u"lip"]  = 7
    month_to_int[u"VII"]  = 7
    month_to_int[u"sierpień"]  = 8
    month_to_int[u"sie"]  = 8
    month_to_int[u"VIII"]  = 8
    month_to_int[u"wrzesień"]  = 9
    month_to_int[u"wrz"]  = 9
    month_to_int[u"IX"]  = 9
    month_to_int[u"październik"]  = 10
    month_to_int[u"paź"]  = 10
    month_to_int[u"X"]  = 10
    month_to_int[u"listopad"]  = 11
    month_to_int[u"lis"]  = 11
    month_to_int[u"XI"]  = 11
    month_to_int[u"grudzień"]  = 12
    month_to_int[u"gru"]  = 12
    month_to_int[u"XII"]  = 12
    
    modifier_to_int = {
        u'przed'    : Date.MOD_BEFORE, 
        u'po'   : Date.MOD_AFTER,
        u'około'  : Date.MOD_ABOUT,
        u'ok.'     : Date.MOD_ABOUT,
        u'circa'  : Date.MOD_ABOUT,
        u'ca.'  : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        u'gregoriański'  : Date.CAL_GREGORIAN,
        u'greg.'          : Date.CAL_GREGORIAN,
        u'juliański'     : Date.CAL_JULIAN,
        u'jul.'           : Date.CAL_JULIAN,
        u'hebrajski'      : Date.CAL_HEBREW,
        u'hebr.'          : Date.CAL_HEBREW,
        u'islamski'      : Date.CAL_ISLAMIC,
        u'isl.'           : Date.CAL_ISLAMIC,
        u'francuski republikański': Date.CAL_FRENCH,
        u'franc.'         : Date.CAL_FRENCH,
        u'perski'       : Date.CAL_PERSIAN,
        }

    quality_to_int = {
        u'szacowany' : Date.QUAL_ESTIMATED,
        u'szac.'      : Date.QUAL_ESTIMATED,
        u'obliczony'  : Date.QUAL_CALCULATED,
        u'obl.'       : Date.QUAL_CALCULATED,
        }

    bce = ["przed naszą erą", "przed Chrystusem",
           "p.n.e."] + DateParser.bce
    
    def init_strings(self):
        DateParser.init_strings(self)
        self._span  = re.compile("(od)\s+(?P<start>.+)\s+(do)\s+(?P<stop>.+)",re.IGNORECASE)
        self._range = re.compile(u"(między)\s+(?P<start>.+)\s+(a)\s+(?P<stop>.+)", re.IGNORECASE)
        self._text2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?' % self._mon_str,
                                 re.IGNORECASE)
        self._jtext2= re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?' % self._jmon_str,
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Polish display
#
#-------------------------------------------------------------------------
class DateDisplayPL(DateDisplay):

    calendar = (
        "", u" (juliański)", u" (hebrajski)", 
        u" (francuski republikański)", u" (perski)", u" (islamski)"
        )

    _mod_str = ("",u"przed ",u"po ",u"ok. ","","","")
    
    _qual_str = ("",u"szacowany ",u"obliczony ")
    
    _bce_str = "%s p.n.e."

    formats = (
        "RRRR-MM-DD (ISO)", "Numeryczny", "Miesiąc Dzień, Rok",
        "Dzień.Miesiąc.Rok", "Dzień Miesiąc Rok", "Dzień MieRzym Rok"
        )
    
    roman_months = (
        "",
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
        "XI",
        "XII"
        )

    def _display_gregorian(self,date_val):
        year = self._slash_year(date_val[2],date_val[3])
        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
            if date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == 0 and date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self._tformat.replace('%m',str(date_val[0]))
                    value = value.replace('%d',str(date_val[1]))
                    value = value.replace('%y',str(date_val[2]))
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
            # Day. Month. Year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%d.%s" % (date_val[1],year)
            else:
                value = "%d.%d.%s" % (date_val[0],date_val[1],year)
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
            # Day RomanMon Year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.roman_months[date_val[1]],year)
            else:
                value = "%d %s %s" % (date_val[0],self.roman_months[date_val[1]],year)
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

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
            return "%s%s %s %s %s%s" % (qual_str,u'od',d1,u'do',d2,self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%s%s %s %s %s%s" % (qual_str,u'między',d1,u'a',d2,self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str,self._mod_str[mod],text,self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('pl_PL','polish','Polish_Poland','pl'),
                     DateParserPL, DateDisplayPL)
