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

# Slovenian version 2010 by Bernard Banko, based on croatian one by Josip

"""
Slovenian-specific classes for parsing and displaying dates.
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
# Slovenian parser
#
#-------------------------------------------------------------------------
class DateParserSL(DateParser):
    """
    Converts a text string into a Date object
    """
    month_to_int = DateParser.month_to_int
    
    month_to_int["januar"] = 1
    month_to_int["januarja"] = 1
    month_to_int["januarjem"] = 1
    month_to_int["jan"] = 1
    month_to_int["i"] = 1
    
    month_to_int["februar"] = 2
    month_to_int["februarjem"] = 2
    month_to_int["februarja"] = 2
    month_to_int["feb"] = 2
    month_to_int["ii"]  = 2
    
    month_to_int["mar"] = 3
    month_to_int["marcem"] = 3
    month_to_int["marec"] = 3
    month_to_int["marca"] = 3
    month_to_int["iii"]  = 3
    
    month_to_int["apr"] = 4
    month_to_int["april"] = 4
    month_to_int["aprilom"] = 4
    month_to_int["aprila"] = 4
    month_to_int["iv"]  = 4

    month_to_int["maj"] = 5
    month_to_int["maja"] = 5
    month_to_int["majem"] = 5
    month_to_int["v"]  = 5
    
    month_to_int["jun"] = 6
    month_to_int["junij"] = 6
    month_to_int["junijem"] = 6
    month_to_int["junija"] = 6
    month_to_int["vi"]  = 6

    month_to_int["jul"]  = 7
    month_to_int["julij"]  = 7
    month_to_int["julijem"]  = 7
    month_to_int["julija"]  = 7
    month_to_int["vii"]  = 7
    
    month_to_int["avg"]  = 8
    month_to_int["avgust"]  = 8
    month_to_int["avgustom"]  = 8
    month_to_int["avgusta"]  = 8
    month_to_int["viii"]  = 8
    
    month_to_int["sep"]  = 9
    month_to_int["sept"]  = 9
    month_to_int["september"]  = 9
    month_to_int["septembrom"]  = 9
    month_to_int["septembra"]  = 9
    month_to_int["ix"]  = 9
    
    month_to_int["okt"]  = 10
    month_to_int["oktober"]  = 10
    month_to_int["oktobrom"]  = 10
    month_to_int["oktobra"]  = 10
    month_to_int["x"]  = 10
    
    month_to_int["nov"]  = 11
    month_to_int["november"]  = 11
    month_to_int["novembrom"]  = 11
    month_to_int["novembra"]  = 11
    month_to_int["xi"]  = 11
    
    month_to_int["dec"]  = 12
    month_to_int["december"]  = 12
    month_to_int["decembrom"]  = 12
    month_to_int["decembra"]  = 12
    month_to_int["xii"]  = 12
    
    modifier_to_int = {
        'pred'   : Date.MOD_BEFORE, 
        'pr.'    : Date.MOD_BEFORE,
        'po'     : Date.MOD_AFTER,
        'okoli'  : Date.MOD_ABOUT,
        'okrog'  : Date.MOD_ABOUT,
        'okr.'   : Date.MOD_ABOUT,
        'ok.'    : Date.MOD_ABOUT,
        'cca.'   : Date.MOD_ABOUT,
        'cca'    : Date.MOD_ABOUT,                      
        'circa'  : Date.MOD_ABOUT, 
        'ca.'    : Date.MOD_ABOUT, 
        }

    calendar_to_int = {
        'gregorijanski'  : Date.CAL_GREGORIAN,
        'greg.'          : Date.CAL_GREGORIAN,
        'julijanski'     : Date.CAL_JULIAN,
        'jul.'           : Date.CAL_JULIAN,
        'hebrejski'      : Date.CAL_HEBREW,
        'hebr.'          : Date.CAL_HEBREW,
        'islamski'       : Date.CAL_ISLAMIC,
        'isl.'           : Date.CAL_ISLAMIC,
        'francoski republikanski': Date.CAL_FRENCH,
        'franc.'         : Date.CAL_FRENCH,
        'perzijski'      : Date.CAL_PERSIAN,
        'perz. '         : Date.CAL_PERSIAN,
        'švedski'        : Date.CAL_SWEDISH, 
        'šved.'          : Date.CAL_SWEDISH, 
        }

    quality_to_int = {
        'približno'   : Date.QUAL_ESTIMATED,
        'pribl.'      : Date.QUAL_ESTIMATED,
        'izračunano'  : Date.QUAL_CALCULATED,
        'izrač.'        : Date.QUAL_CALCULATED,
        }

    bce = ["pred našim štetjem", "pred Kristusom",
           "p.n.š.", "p. n. š.", "pr.Kr.", "pr. Kr."] + DateParser.bce

    def init_strings(self):
        """
        compiles regular expression strings for matching dates
        """
        DateParser.init_strings(self)
        # match 'Day. MONTH year.' format with or without dots
        self._text2 = re.compile('(\d+)?\.?\s*?%s\.?\s*((\d+)(/\d+)?)?\s*\.?$'
                                % self._mon_str, re.IGNORECASE)
        # match Day.Month.Year.
        self._numeric  = re.compile("((\d+)[/\.-])?\s*((\d+)[/\.-])?\s*(\d+)\.?$")
       
        self._span  = re.compile("od\s+(?P<start>.+)\s+do\s+(?P<stop>.+)", 
                                re.IGNORECASE)
        self._range = re.compile(
                            "med\s+(?P<start>.+)\s+in\s+(?P<stop>.+)", 
                            re.IGNORECASE)
        self._jtext2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?'\
                                % self._jmon_str, re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Slovenian display
#
#-------------------------------------------------------------------------
class DateDisplaySL(DateDisplay):
    """
    Slovenian language date display class. 
    """
    long_months = ( "", "januarja", "februarja", "marca","aprila",
        "maja", "junija", "julija", "avgusta", "septembra",
        "oktobra", "novembra", "decembra" 
        )
   
    short_months = ( "", "jan", "feb", "mar", "apr", "maj", "jun",
        "jul", "avg", "sep", "okt", "nov", "dec"
        )
    
    calendar = (
        "", "julijanski", "hebrejski", 
        "francoski republikanski", "perzijski", "islamski",
        "švedski" 
        )

    _mod_str = ("", "pred ", "po ", "okrog ", "", "", "")

    _qual_str = ("", "približno ", "izračunano ")
    
    _bce_str = "%s p.n.š."

    formats = (
        "ISO (leto-mm-dd)", 
        "številčno", 
        "dan. mes. leto",
        "dan. mesec leto"
        )
         
    def _display_gregorian(self, date_val):
        """
        display gregorian calendar date in different format
        """
        year = self._slash_year(date_val[2], date_val[3])
        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
            # D. M. YYYY
            if date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == 0 and date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self._tformat.replace('%m', str(date_val[1]))
                    value = value.replace('%d', str(date_val[0]))
                    value = value.replace('%Y', str(date_val[2]))
                    value = value.replace('-', '. ')
        elif self.format == 2:
            # D. mon. YYYY
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s. %s" % (self.short_months[date_val[1]], year)
            else:
                value = "%d. %s. %s" % (date_val[0],
                                        self.short_months[date_val[1]], year)
        else:
            # D. month YYYY
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s." % year
                else:
                   value = "%s %s" % (self.long_months[date_val[1]], year)
            else:
                value = "%d. %s %s" % (
                  date_val[0],self.long_months[date_val[1]], year)
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
            return "%sod %s do %s%s" % (qual_str, d_1, d_2, scal)
        elif mod == Date.MOD_RANGE:
            d_1 = self.display_cal[cal](start)
            d_2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            date_string = "%smed %s in %s%s" % (qual_str, d_1, d_2, scal)
            date_string = date_string.replace("a ","em ") #to correct declination
            date_string = date_string.replace("lem ","lom ")
            date_string = date_string.replace("rem ","rom ")
            date_string = date_string.replace("tem ","tom ")
            return date_string
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            date_string = "%s%s%s%s" % (qual_str, self._mod_str[mod], text, scal)
        return date_string

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(("sl", "SL", "sl_SI", "slovenščina", "slovenian", "Slovenian", 
                 "sl_SI.UTF8", "sl_SI.UTF-8", "sl_SI.utf-8", "sl_SI.utf8"),
                                    DateParserSL, DateDisplaySL)
