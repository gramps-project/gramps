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

# Serbian version by Vlada Perić <vlada.peric@gmail.com>, 2009.
# Based on the Croatian DateHandler by Josip

"""
Serbian-specific classes for parsing and displaying dates.
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
# Serbian parser
#
#-------------------------------------------------------------------------
class DateParserSR(DateParser):
    """
    Converts a text string into a Date object
    """
    month_to_int = DateParser.month_to_int
    
    month_to_int[u"januar"]  = 1
    month_to_int[u"januara"] = 1
    month_to_int[u"jan"]     = 1
    month_to_int[u"јан"]     = 1
    month_to_int[u"јануара"] = 1
    month_to_int[u"јануар"]  = 1
    month_to_int[u"i"]       = 1
    
    month_to_int[u"februar"]  = 2
    month_to_int[u"februara"] = 2
    month_to_int[u"feb"]      = 2
    month_to_int[u"феб"]      = 2
    month_to_int[u"фебруар"]  = 2
    month_to_int[u"фебруара"] = 2
    month_to_int[u"ii"]       = 2
    
    month_to_int[u"mart"]  = 3
    month_to_int[u"marta"] = 3
    month_to_int[u"mar"]   = 3
    month_to_int[u"мар"]   = 3
    month_to_int[u"март"]  = 3
    month_to_int[u"марта"] = 3
    month_to_int[u"iii"]   = 3
    
    month_to_int[u"april"]  = 4
    month_to_int[u"aprila"] = 4
    month_to_int[u"apr"]    = 4
    month_to_int[u"апр"]    = 4
    month_to_int[u"април"]  = 4
    month_to_int[u"априла"] = 4
    month_to_int[u"iv"]     = 4

    month_to_int[u"maj"]  = 5
    month_to_int[u"maja"] = 5
    month_to_int[u"мај"]  = 5
    month_to_int[u"маја"] = 5
    month_to_int[u"v"]    = 5
    
    month_to_int[u"jun"]  = 6
    month_to_int[u"juna"] = 6
    month_to_int[u"јун"]  = 6
    month_to_int[u"јуна"] = 6
    month_to_int[u"vi"]   = 6

    month_to_int[u"jul"]  = 7
    month_to_int[u"jula"] = 7
    month_to_int[u"јул"]  = 7
    month_to_int[u"јула"] = 7
    month_to_int[u"vii"]  = 7
    
    month_to_int[u"avgust"]  = 8
    month_to_int[u"avgusta"] = 8
    month_to_int[u"avg"]     = 8
    month_to_int[u"авг"]     = 8
    month_to_int[u"август"]  = 8
    month_to_int[u"августа"] = 8
    month_to_int[u"viii"]    = 8
    
    month_to_int[u"septembar"] = 9
    month_to_int[u"septembra"] = 9
    month_to_int[u"sep"]       = 9
    month_to_int[u"сеп"]       = 9
    month_to_int[u"септембар"] = 9
    month_to_int[u"септембра"] = 9
    month_to_int[u"ix"]        = 9
    
    month_to_int[u"oktobar"]  = 10
    month_to_int[u"oktobra"]  = 10
    month_to_int[u"okt"]      = 10
    month_to_int[u"окт"]      = 10
    month_to_int[u"октобар"]  = 10
    month_to_int[u"октобра"]  = 10
    month_to_int[u"x"]        = 10
    
    month_to_int[u"novembar"]  = 11
    month_to_int[u"novembra"]  = 11
    month_to_int[u"nov"]       = 11
    month_to_int[u"нов"]       = 11
    month_to_int[u"новембар"]  = 11
    month_to_int[u"новембра"]  = 11
    month_to_int[u"xi"]        = 11
    
    month_to_int[u"decembar"]  = 12
    month_to_int[u"decembra"]  = 12
    month_to_int[u"dec"]       = 12
    month_to_int[u"дец"]       = 12
    month_to_int[u"децембар"]  = 12
    month_to_int[u"децембра"]  = 12
    month_to_int[u"xii"]       = 12
    
    modifier_to_int = {
        u'pre'    : Date.MOD_BEFORE, 
        u'posle'  : Date.MOD_AFTER,
        u'oko'    : Date.MOD_ABOUT,
        u'cca'    : Date.MOD_ABOUT,

        u'пре'    : Date.MOD_BEFORE, 
        u'после'  : Date.MOD_AFTER,
        u'око'    : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        u'gregorijanski'  : Date.CAL_GREGORIAN,
        u'greg.'          : Date.CAL_GREGORIAN,
        u'julijanski'     : Date.CAL_JULIAN,
        u'jul.'           : Date.CAL_JULIAN,
        u'hebrejski'      : Date.CAL_HEBREW,
        u'hebr.'          : Date.CAL_HEBREW,
        u'islamski'       : Date.CAL_ISLAMIC,
        u'isl.'           : Date.CAL_ISLAMIC,
        u'francuski republikanski': Date.CAL_FRENCH,
        u'franc.'         : Date.CAL_FRENCH,
        u'persijski'      : Date.CAL_PERSIAN,
        u'pers. '         : Date.CAL_PERSIAN,
        u'švedski'        : Date.CAL_SWEDISH, 
        u'šv.'            : Date.CAL_SWEDISH, 

        u'грегоријански'  : Date.CAL_GREGORIAN,
        u'грег.'          : Date.CAL_GREGORIAN,
        u'јулијански'     : Date.CAL_JULIAN,
        u'јул.'           : Date.CAL_JULIAN,
        u'хебрејски'      : Date.CAL_HEBREW,
        u'хебр.'          : Date.CAL_HEBREW,
        u'исламски'       : Date.CAL_ISLAMIC,
        u'исл.'           : Date.CAL_ISLAMIC,
        u'француски републикански': Date.CAL_FRENCH,
        u'франц.'         : Date.CAL_FRENCH,
        u'персијски'      : Date.CAL_PERSIAN,
        u'перс. '         : Date.CAL_PERSIAN,
        u'шведски'        : Date.CAL_SWEDISH, 
        u'шв'             : Date.CAL_SWEDISH, 
        }

    quality_to_int = {
        u'procenjeno' : Date.QUAL_ESTIMATED,
        u'pro.'       : Date.QUAL_ESTIMATED,
        u'izračunato' : Date.QUAL_CALCULATED,
        u'izr.'       : Date.QUAL_CALCULATED,

        u'процењено'  : Date.QUAL_ESTIMATED,
        u'про.'       : Date.QUAL_ESTIMATED,
        u'израчунато' : Date.QUAL_CALCULATED,
        u'изр.'       : Date.QUAL_CALCULATED,
        }

    bce = [u"пре нове ере", u"пре Христа", u"п.н.е."
           u"pre nove ere", u"pre Hrista", u"p.n.e."] + DateParser.bce

    def init_strings(self):
        """
        compiles regular expression strings for matching dates
        """
        DateParser.init_strings(self)
        # match 'Day. MONTH year.' format with or without dots
        self._text2 = re.compile('(\d+)?\.?\s*?%s\s*((\d+)(/\d+)?)?\.?\s*$'
                                % self._mon_str, re.IGNORECASE)

        # match Day.Month.Year.
        self._numeric  = re.compile("((\d+)[/\. ])?\s*((\d+)[/\.])?\s*(\d+)\.?$")

        _span1 = [u'od', u'од']
        _span2 = [u'do', u'до']
        _range1 = [u'između', u'између']
        _range2 = [u'i', u'и']
        self._span     = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" % 
                                   ('|'.join(_span1),'|'.join(_span2)),
                                   re.IGNORECASE)
        self._range    = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                   ('|'.join(_range1),'|'.join(_range2)),
                                   re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Serbian display
#
#-------------------------------------------------------------------------
class DateDisplaySR_latin(DateDisplay):
    """
    Serbian (latin) date display class
    """
    # TODO: Translate these month strings:
    long_months = ( u"", u"January", u"February", u"March", u"April", u"May", 
                    u"June", u"July", u"August", u"September", u"October", 
                    u"November", u"December" )
    
    short_months = ( u"", u"Jan", u"Feb", u"Mar", u"Apr", u"May", u"Jun", 
                     u"Jul", u"Aug", u"Sep", u"Oct", u"Nov", u"Dec" )
    
    calendar = (
        "", u" (julijanski)", u" (hebrejski)", 
        u" (francuski republikanski)", u" (persijski)", u" (islamski)",
        u" (švedski)" 
        )

    _mod_str = ("", "pre ", "posle ", "oko ", "", "", "")

    _qual_str = ("", "procenjeno ", "izračunato ")
    
    _bce_str = "%s p.n.e."

    formats = (
        "GGGG-MM-DD (ISO-8601)", 
        "Numerički (D.M.GGGG.)", 
        "D. MMM GGGG.",
        "D. Mesec GGGG.",
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
        
    sr_months = ("",
        u"januara",
        u"februara",
        u"marta",
        u"aprila",
        u"maja",
        u"juna",
        u"jula",
        u"avgusta",
        u"septembra",
        u"oktobra",
        u"novembra",
        u"decembra"
        )

    sr_months3 = ("",
        u"jan",
        u"feb",
        u"mar",
        u"apr",
        u"maj",
        u"jun",
        u"jul",
        u"avg",
        u"sep",
        u"okt",
        u"nov",
        u"dec"
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
            # Day. MON Year.
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = u"%s." % year
                else:
                    value = u"%s %s." % (self.sr_months3[date_val[1]], year)
            else:
                value = u"%d. %s %s." % (date_val[0], 
                                self.sr_months3[date_val[1]], year)
        elif self.format == 3:
            # Day. MONTH Year.
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = u"%s." % year
                else:
                    value = u"%s %s." % (self.sr_months[date_val[1]], year)
            else:
                value = u"%d. %s %s." % (date_val[0], 
                                self.sr_months[date_val[1]], year)
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
register_datehandler(('sr', 'serbian', 'srpski', 'sr_RS'),
                                    DateParserSR, DateDisplaySR_latin)
