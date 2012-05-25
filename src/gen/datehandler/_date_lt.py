# -*- coding: utf-8 -*-
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
Lithuanian-specific classes for parsing and displaying dates.
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
from _dateparser import DateParser
from _datedisplay import DateDisplay
from _datehandler import register_datehandler

#-------------------------------------------------------------------------
#
# Lithuanian parser
#
#-------------------------------------------------------------------------
class DateParserLT(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    month_to_int = DateParser.month_to_int

    # Custom months not the same as long months

    month_to_int[u"sausis"] = 1
    month_to_int[u"vasaris"] = 2
    month_to_int[u"kovas"] = 3
    month_to_int[u"balandis"] = 4
    month_to_int[u"gegužė"] = 5
    month_to_int[u"gegužis"] = 5
    month_to_int[u"birželis"] = 6
    month_to_int[u"liepa"] = 7
    month_to_int[u"rugpjūtis"] = 8
    month_to_int[u"rugsėjis"] = 9
    month_to_int[u"spalis"] = 10
    month_to_int[u"lapkritis"] = 11
    month_to_int[u"gruodis"] = 12
    
    # For not full months
    
    month_to_int[u"saus"] = 1
    month_to_int[u"vasa"] = 2
    month_to_int[u"vasar"] = 2
    month_to_int[u"bala"] = 4
    month_to_int[u"balan"] = 4
    month_to_int[u"baland"] = 4
    month_to_int[u"gegu"] = 5
    month_to_int[u"geguž"] = 5
    month_to_int[u"birž"] = 6
    month_to_int[u"birže"] = 6
    month_to_int[u"biržel"] = 6
    month_to_int[u"liep"] = 7
    month_to_int[u"rugp"] = 8
    month_to_int[u"rugpj"] = 8
    month_to_int[u"rugpjū"] = 8
    month_to_int[u"rugpjūt"] = 8
    month_to_int[u"rugs"] = 9
    month_to_int[u"rugsė"] = 9
    month_to_int[u"rugsėj"] = 9
    month_to_int[u"rugsėjis"] = 9
    month_to_int[u"spal"] = 10
    month_to_int[u"lapk"] = 11
    month_to_int[u"lapkr"] = 11
    month_to_int[u"lapkri"] = 11
    month_to_int[u"lapkrit"] = 11
    month_to_int[u"gru"] = 12
    month_to_int[u"gruo"] = 12
    month_to_int[u"gruod"] = 12

    modifier_to_int = {
        u'prieš'    : Date.MOD_BEFORE, 
        u'po' : Date.MOD_AFTER, 
        u'apie' : Date.MOD_ABOUT, 
        }

    calendar_to_int = {
        u'grigaliaus'   : Date.CAL_GREGORIAN, 
        u'g'                 : Date.CAL_GREGORIAN, 
        u'julijaus'            : Date.CAL_JULIAN, 
        u'j'                 : Date.CAL_JULIAN, 
        u'hebrajų'         : Date.CAL_HEBREW, 
        u'h'         : Date.CAL_HEBREW, 
        u'islamo'         : Date.CAL_ISLAMIC, 
        u'i'                 : Date.CAL_ISLAMIC, 
        u'prancūzų respublikos': Date.CAL_FRENCH, 
        u'r'                 : Date.CAL_FRENCH, 
        u'persų'             : Date.CAL_PERSIAN, 
        u'p'             : Date.CAL_PERSIAN, 
        u'švedų'      : Date.CAL_SWEDISH, 
        u's'            : Date.CAL_SWEDISH, 
        }

    quality_to_int = {
        u'apytikriai'  : Date.QUAL_ESTIMATED, 
        u'apskaičiuota'      : Date.QUAL_CALCULATED, 
        }

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = [u'nuo']
        _span_2 = [u'iki']
        _range_1 = [u'tarp']
        _range_2 = [u'ir']
        self._span     = re.compile(
            "(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" % 
            ('|'.join(_span_1), '|'.join(_span_2)), 
            re.IGNORECASE)
        self._range    = re.compile(
            "(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
            ('|'.join(_range_1), '|'.join(_range_2)), 
            re.IGNORECASE)

#------------------------------------------------------------------------
#
# FIXME: oficial long date format (ex, 2011 m. vasario 4 d.)
#      is not recognized correctly:
#      with self._text2 - day is recognized as year, year - as day
#      with self._iso   - month not recognized, day recognized,
#                         year increased by 1, date treated as double
# TODO: in _DateParser.py in _parse_calendar modify groups
#
#------------------------------------------------------------------------
#
#     # gregorian and julian
#
#        self._text2 = re.compile('(\d+)?\s*?m\.?\s*?%s\.?\s*((\d+)(/\d+)?)?\s*?d?\.?' %
#                                 self._mon_str, re.IGNORECASE)
#        
#        self._iso = re.compile('(\d+)(/\d+)?\s*?m?\.?\s+?%s\.?\s*((\d+))?\s*?d?\.?' %
#                                 self._mon_str, re.IGNORECASE)
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Lithuanian displayer
#
#-------------------------------------------------------------------------
class DateDisplayLT(DateDisplay):
    """
    Lithuanian language date display class. 
    """
   
    long_months = ( u"", u"sausio", u"vasario", u"kovo", u"balandžio", u"gegužės", 
                    u"birželio", u"liepos", u"rugpjūčio", u"rugsėjo", u"spalio", 
                    u"lapkričio", u"gruodžio" )
    
    long_months_vardininkas = ( u"", u"sausis", u"vasaris", u"kovas", u"balandis", u"gegužė", 
                    u"birželis", u"liepa", u"rugpjūtis", u"rugsėjis", u"spalis", 
                    u"lapkritis", u"gruodis" )    
    
    short_months = ( u"", u"Sau", u"Vas", u"Kov", u"Bal", u"Geg", u"Bir", 
                     u"Lie", u"Rgp", u"Rgs", u"Spa", u"Lap", u"Grd" )
    
    calendar = (
        u"", u"julijaus", 
        u"hebrajų", 
        u"prancūzų respublikos", 
        u"persų", 
        u"islamo", 
        u"švedų" 
        )

    _mod_str = (u"", 
        u"prieš ", 
        u"po ", 
        u"apie ", 
        u"", u"", u"")
    
    _qual_str = (u"", u"apytikriai ", u"apskaičiuota ")

    formats = (
        "mmmm-MM-DD (ISO)", "mmmm m. mėnesio diena d.", "Mėn diena, metai")

    def _display_gregorian(self, date_val):
        """
        display gregorian calendar date in different format
        """
        value = self.display_iso(date_val)
        year = self._slash_year(date_val[2], date_val[3])

        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:

            # mmmm m. mėnesio diena d. (YYYY m. month DD d.)

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s m. %s" % (year, self.long_months_vardininkas[date_val[1]])
            else:
                value = "%s m. %s %d d." % (year, self.long_months[date_val[1]],
                                       date_val[0])
        elif self.format == 2:

            # MON Day, Year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.short_months[date_val[1]], year)
            else:
                value = "%s %d, %s" % (self.short_months[date_val[1]],
                                       date_val[0], year)
        
        
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
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, u'nuo', d1, u'iki', 
                                        d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, u'tarp', d1, u'ir', 
                                        d2, scal)
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
register_datehandler(('lt_LT', 'lt', 'lithuanian', 'Lithuanian'), DateParserLT, DateDisplayLT)
