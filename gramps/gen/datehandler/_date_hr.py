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
# $Id$
#

# Croatian version 2008 by Josip

"""
Croatian-specific classes for parsing and displaying dates.
"""
from __future__ import unicode_literals
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
from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

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
    
    month_to_int["siječanj"] = 1
    month_to_int["siječnja"] = 1
    month_to_int["sij"] = 1
    month_to_int["januar"] = 1
    month_to_int["januara"] = 1
    month_to_int["i"] = 1
    
    month_to_int["veljača"] = 2
    month_to_int["veljače"] = 2
    month_to_int["velj"] = 2
    month_to_int["februar"] = 2
    month_to_int["februara"] = 2
    month_to_int["ii"]  = 2
    
    month_to_int["ožujak"] = 3
    month_to_int["ožujka"] = 3
    month_to_int["ožu"] = 3
    month_to_int["mart"] = 3
    month_to_int["marta"] = 3
    month_to_int["iii"]  = 3
    
    month_to_int["travanj"] = 4
    month_to_int["travnja"] = 4
    month_to_int["tra"] = 4
    month_to_int["april"] = 4
    month_to_int["aprila"] = 4
    month_to_int["iv"]  = 4

    month_to_int["svibanj"] = 5
    month_to_int["svibnja"] = 5
    month_to_int["svi"] = 5
    month_to_int["maj"] = 5
    month_to_int["maja"] = 5
    month_to_int["v"]  = 5
    
    month_to_int["lipanj"] = 6
    month_to_int["lipnja"] = 6
    month_to_int["lip"] = 6
    month_to_int["jun"] = 6
    month_to_int["juna"] = 6
    month_to_int["vi"]  = 6

    month_to_int["srpanj"]  = 7
    month_to_int["srpnja"]  = 7
    month_to_int["srp"]  = 7
    month_to_int["juli"]  = 7
    month_to_int["jula"]  = 7
    month_to_int["vii"]  = 7
    
    month_to_int["kolovoz"]  = 8
    month_to_int["kolovoza"]  = 8
    month_to_int["kol"]  = 8
    month_to_int["august"]  = 8
    month_to_int["augusta"]  = 8
    month_to_int["viii"]  = 8
    
    month_to_int["rujan"]  = 9
    month_to_int["rujna"]  = 9
    month_to_int["ruj"]  = 9
    month_to_int["septembar"]  = 9
    month_to_int["septembra"]  = 9
    month_to_int["ix"]  = 9
    month_to_int["7ber"]  = 9
    
    month_to_int["listopad"]  = 10
    month_to_int["listopada"]  = 10
    month_to_int["lis"]  = 10
    month_to_int["oktobar"]  = 10
    month_to_int["oktobra"]  = 10
    month_to_int["x"]  = 10
    month_to_int["8ber"]  = 10
    
    month_to_int["studeni"]  = 11
    month_to_int["studenog"]  = 11
    month_to_int["stu"]  = 11
    month_to_int["novembar"]  = 11
    month_to_int["novembra"]  = 11
    month_to_int["xi"]  = 11
    month_to_int["9ber"]  = 11
    
    month_to_int["prosinac"]  = 12
    month_to_int["prosinca"]  = 12
    month_to_int["pro"]  = 12
    month_to_int["decembar"]  = 12
    month_to_int["decembra"]  = 12
    month_to_int["xii"]  = 12
    
    modifier_to_int = {
        'prije'    : Date.MOD_BEFORE, 
        'pr. '    : Date.MOD_BEFORE,
        'poslije'   : Date.MOD_AFTER,
        'po. '   : Date.MOD_AFTER,
        'okolo'  : Date.MOD_ABOUT,
        'ok. '     : Date.MOD_ABOUT,
       
        }

    calendar_to_int = {
        'gregorijanski'  : Date.CAL_GREGORIAN,
        'greg.'          : Date.CAL_GREGORIAN,
        'julijanski'     : Date.CAL_JULIAN,
        'jul.'           : Date.CAL_JULIAN,
        'hebrejski'      : Date.CAL_HEBREW,
        'hebr.'          : Date.CAL_HEBREW,
        'islamski'      : Date.CAL_ISLAMIC,
        'isl.'           : Date.CAL_ISLAMIC,
        'francuski republikanski': Date.CAL_FRENCH,
        'franc.'         : Date.CAL_FRENCH,
        'perzijski'       : Date.CAL_PERSIAN,
        'perz. '       : Date.CAL_PERSIAN,
        'švedski'      : Date.CAL_SWEDISH, 
        's'            : Date.CAL_SWEDISH, 
        }

    quality_to_int = {
        'približno' : Date.QUAL_ESTIMATED,
        'prb.'      : Date.QUAL_ESTIMATED,
        'izračunato'  : Date.QUAL_CALCULATED,
        'izr.'       : Date.QUAL_CALCULATED,
        }

    bce = ["prije nove ere", "prije Krista",
           "p.n.e."] + DateParser.bce

    def init_strings(self):
        """
        compiles regular expression strings for matching dates
        """
        DateParser.init_strings(self)
        # match 'Day. MONTH year.' format with or without dots
        self._text2 = re.compile('(\d+)?\.?\s*?%s\.?\s*((\d+)(/\d+)?)?\s*\.?$'
                                % self._mon_str, re.IGNORECASE)
        # match Day.Month.Year.
        self._numeric  = re.compile(
                                    "((\d+)[/\. ])?\s*((\d+)[/\.])?\s*(\d+)\.?$"
                                    )
        self._span  = re.compile("(od)\s+(?P<start>.+)\s+(do)\s+(?P<stop>.+)", 
                                re.IGNORECASE)
        self._range = re.compile(
                            "(između)\s+(?P<start>.+)\s+(i)\s+(?P<stop>.+)", 
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
    Croatian language date display class. 
    """
    long_months = ( "", 
        "siječnja",
        "veljače",
        "ožujka",
        "travnja",
        "svibnja",
        "lipnja",
        "srpnja",
        "kolovoza",
        "rujna",
        "listopada",
        "studenog",
        "prosinca" 
        )
    
    #currently unused
    short_months = ( "", "sij", "velj", "ožu", "tra", "svi", "lip",
        "srp", "kol", "ruj", "lis", "stu", "pro"
        )
    
    calendar = (
        "", "julijanski", "hebrejski", 
        "francuski republikanski", "perzijski", "islamski",
        "swedish" 
        )

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
                    value = "%s." % year
                else:
                    value = "%s %s." % (self.long_months[date_val[1]], year)
            else:
                value = "%d. %s %s." % (date_val[0], 
                                self.long_months[date_val[1]], year)
        else:
            # Day RomanMon Year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s." % year
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
        newyear = date.get_new_year()

        qual_str = self._qual_str[qual]
        
        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN:
            d_1 = self.display_cal[cal](start)
            d_2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'od', d_1, 'do', d_2,
                                                            scal)
        elif mod == Date.MOD_RANGE:
            d_1 = self.display_cal[cal](start)
            d_2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'između', d_1, 'i', d_2, 
                                                            scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, 
                                                scal)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('hr', 'HR', 'croatian', 'Croatian', 'hrvatski', 'hr_HR'),
                                    DateParserHR, DateDisplayHR)
