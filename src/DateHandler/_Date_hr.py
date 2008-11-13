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

# Croatian version 2008 by Josip

"""
Croatian-specific classes for parsing and displaying dates.
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
from gen.lib import Date
from _DateParser import DateParser
from _DateDisplay import DateDisplay
from _DateHandler import register_datehandler

#-------------------------------------------------------------------------
#
# Croatian parser
#
#-------------------------------------------------------------------------
class DateParserHR(DateParser):
    """
    Converts a text string into a Date object
    """
    month_to_int = DateParser.month_to_int
    
    month_to_int[u"siječanj"] = 1
    month_to_int[u"siječnja"] = 1
    month_to_int[u"sij"] = 1
    month_to_int[u"januar"] = 1
    month_to_int[u"januara"] = 1
    month_to_int[u"i"] = 1
    
    month_to_int[u"veljača"] = 2
    month_to_int[u"veljače"] = 2
    month_to_int[u"velj"] = 2
    month_to_int[u"februar"] = 2
    month_to_int[u"februara"] = 2
    month_to_int[u"ii"]  = 2
    
    month_to_int[u"ožujak"] = 3
    month_to_int[u"ožujka"] = 3
    month_to_int[u"ožu"] = 3
    month_to_int[u"mart"] = 3
    month_to_int[u"marta"] = 3
    month_to_int[u"iii"]  = 3
    
    month_to_int[u"travanj"] = 4
    month_to_int[u"travnja"] = 4
    month_to_int[u"tra"] = 4
    month_to_int[u"april"] = 4
    month_to_int[u"aprila"] = 4
    month_to_int[u"iv"]  = 4

    month_to_int[u"svibanj"] = 5
    month_to_int[u"svibnja"] = 5
    month_to_int[u"svi"] = 5
    month_to_int[u"maj"] = 5
    month_to_int[u"maja"] = 5
    month_to_int[u"v"]  = 5
    
    month_to_int[u"lipanj"] = 6
    month_to_int[u"lipnja"] = 6
    month_to_int[u"lip"] = 6
    month_to_int[u"jun"] = 6
    month_to_int[u"juna"] = 6
    month_to_int[u"vi"]  = 6

    month_to_int[u"srpanj"]  = 7
    month_to_int[u"srpnja"]  = 7
    month_to_int[u"srp"]  = 7
    month_to_int[u"juli"]  = 7
    month_to_int[u"jula"]  = 7
    month_to_int[u"vii"]  = 7
    
    month_to_int[u"kolovoz"]  = 8
    month_to_int[u"kolovoza"]  = 8
    month_to_int[u"kol"]  = 8
    month_to_int[u"august"]  = 8
    month_to_int[u"augusta"]  = 8
    month_to_int[u"viii"]  = 8
    
    month_to_int[u"rujan"]  = 9
    month_to_int[u"rujna"]  = 9
    month_to_int[u"ruj"]  = 9
    month_to_int[u"septembar"]  = 9
    month_to_int[u"septembra"]  = 9
    month_to_int[u"ix"]  = 9
    
    month_to_int[u"listopad"]  = 10
    month_to_int[u"listopada"]  = 10
    month_to_int[u"lis"]  = 10
    month_to_int[u"oktobar"]  = 10
    month_to_int[u"oktobra"]  = 10
    month_to_int[u"x"]  = 10
    
    month_to_int[u"studeni"]  = 11
    month_to_int[u"studenog"]  = 11
    month_to_int[u"stu"]  = 11
    month_to_int[u"novembar"]  = 11
    month_to_int[u"novembra"]  = 11
    month_to_int[u"xi"]  = 11
    
    month_to_int[u"prosinac"]  = 12
    month_to_int[u"prosinca"]  = 12
    month_to_int[u"pro"]  = 12
    month_to_int[u"decembar"]  = 12
    month_to_int[u"decembra"]  = 12
    month_to_int[u"xii"]  = 12
    
    modifier_to_int = {
        u'prije'    : Date.MOD_BEFORE, 
        u'pr. '    : Date.MOD_BEFORE,
        u'poslije'   : Date.MOD_AFTER,
        u'po. '   : Date.MOD_AFTER,
        u'okolo'  : Date.MOD_ABOUT,
        u'ok. '     : Date.MOD_ABOUT,
       
        }

    calendar_to_int = {
        u'gregorijanski'  : Date.CAL_GREGORIAN,
        u'greg.'          : Date.CAL_GREGORIAN,
        u'julijanski'     : Date.CAL_JULIAN,
        u'jul.'           : Date.CAL_JULIAN,
        u'hebrejski'      : Date.CAL_HEBREW,
        u'hebr.'          : Date.CAL_HEBREW,
        u'islamski'      : Date.CAL_ISLAMIC,
        u'isl.'           : Date.CAL_ISLAMIC,
        u'francuski republikanski': Date.CAL_FRENCH,
        u'franc.'         : Date.CAL_FRENCH,
        u'perzijski'       : Date.CAL_PERSIAN,
        u'perz. '       : Date.CAL_PERSIAN
        }

    quality_to_int = {
        u'približno' : Date.QUAL_ESTIMATED,
        u'prb.'      : Date.QUAL_ESTIMATED,
        u'izračunato'  : Date.QUAL_CALCULATED,
        u'izr.'       : Date.QUAL_CALCULATED,
        }

    bce = ["prije nove ere", "prije Krista",
           "p.n.e."] + DateParser.bce

    def init_strings(self):
        """
        compiles regular expression strings for matching dates
        """
        DateParser.init_strings(self)
        # match 'Day. MONTH year.' format with or without dots
        self._text2 = re.compile('(\d+)?\.?\s+?%s\.?\s*((\d+)(/\d+)?)?\s*\.?$'
                                % self._mon_str, re.IGNORECASE)
        # match Day.Month.Year.
        self._numeric  = re.compile(
                                    "((\d+)[/\. ])?\s*((\d+)[/\.])?\s*(\d+)\.?$"
                                    )
        self._span  = re.compile("(od)\s+(?P<start>.+)\s+(do)\s+(?P<stop>.+)", 
                                re.IGNORECASE)
        self._range = re.compile(
                            u"(između)\s+(?P<start>.+)\s+(i)\s+(?P<stop>.+)", 
                            re.IGNORECASE)
        self._jtext2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?'\
                                % self._jmon_str, re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Croatian display
#
#-------------------------------------------------------------------------
class DateDisplayHR(DateDisplay):
    """
    Croatian date display class
    """
    calendar = (
        "", u" (julijanski)", u" (hebrejski)", 
        u" (francuski republikanski)", u" (perzijski)", u" (islamski)")

    _mod_str = ("", "prije ", "poslije ", "okolo ", "", "", "")

    _qual_str = ("", "približno ", "izračunato ")
    
    _bce_str = "%s p.n.e."

    formats = (
        "GGGG-MM-DD (ISO-8601)", 
        "Numerički", 
        "D.M.GGGG.",
        "D. MMMM GGGG.",
        "D. Rb GGGG."
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
        
    hr_months = ("",
        u"siječnja",
        u"veljače",
        u"ožujka",
        u"travnja",
        u"svibnja",
        u"lipnja",
        u"srpnja",
        u"kolovoza",
        u"rujna",
        u"listopada",
        u"studenog",
        u"prosinca"
        )

    def _display_gregorian(self, date_val):
        """
        display gregorian calendar date in different format
        """
        year = self._slash_year(date_val[2], date_val[3])
        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
            if date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == 0 and date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self._tformat.replace('%m', str(date_val[1]))
                    value = value.replace('%d', str(date_val[0]))
                    value = value.replace('%Y', str(abs(date_val[2])))
                    value = value.replace('-', '/')
        elif self.format == 2:
            # Day.Month.Year.
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s.%s." % (date_val[1], year)
            else:
                value = "%s.%d.%s." % (date_val[0], date_val[1], year)
        elif self.format == 3:
            # Day. MONTH year.
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = u"%s." % year
                else:
                    value = u"%s %s." % (self.hr_months[date_val[1]], year)
            else:
                value = u"%d. %s %s." % (date_val[0], 
                                self.hr_months[date_val[1]], year)
        else:
            # Day RomanMon Year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = u"%s." % year
                else:
                    value = "%s %s." % (self.roman_months[date_val[1]], year)
            else:
                value = "%d. %s %s." % (date_val[0],
                                self.roman_months[date_val[1]], year)
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    def display(self, date):
        """
        Return a text string representing the date.
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
            d_1 = self.display_cal[cal](start)
            d_2 = self.display_cal[cal](date.get_stop_date())
            return "%s%s %s %s %s%s" % (qual_str, u'od', d_1, u'do', d_2,
                                                            self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d_1 = self.display_cal[cal](start)
            d_2 = self.display_cal[cal](date.get_stop_date())
            return "%s%s %s %s %s%s" % (qual_str, u'između', d_1, u'i', d_2, 
                                                            self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, 
                                                self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('hr', 'HR', 'croatian', 'Croatian', 'hrvatski', 'hr_HR'),
                                    DateParserHR, DateDisplayHR)
