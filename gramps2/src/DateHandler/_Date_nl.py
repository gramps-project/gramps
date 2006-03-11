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

# Written by Benny Malengier
# Last change 2005/12/05:
# Correspond  naming of dates with actual action, so for abbreviation
# of month given by mnd. not MAAND
# Also less possibilities

"""
Dutch-specific classes for parsing and displaying dates.
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
# Dutch parser
#
#-------------------------------------------------------------------------
class DateParserNL(DateParser):

    month_to_int = DateParser.month_to_int
    # Always add dutch and flemish name variants
    # no matter what the current locale is
    month_to_int[u"januari"] = 1
    month_to_int[u"jan"]    = 1
    # Add other common latin, local and historical variants  
    month_to_int[u"januaris"] = 1
    month_to_int[u"feber"]  = 2
    month_to_int[u"februaris"]  = 2
    month_to_int[u"merz"]  = 3
    month_to_int[u"aprilis"]  = 4
    month_to_int[u"maius"]  = 5
    month_to_int[u"junius"]  = 6
    month_to_int[u"julius"]  = 7
    month_to_int[u"augst"]  = 8
    month_to_int[u"7ber"]  = 9
    month_to_int[u"7bris"]  = 9
    month_to_int[u"8ber"]  = 10
    month_to_int[u"8bris"]  = 10
    month_to_int[u"9ber"]  = 11
    month_to_int[u"9bris"]  = 11
    month_to_int[u"10ber"]  = 12
    month_to_int[u"10bris"]  = 12
    month_to_int[u"xber"]  = 12
    month_to_int[u"xbris"]  = 12
    
    modifier_to_int = {
        u'voor'    : Date.MOD_BEFORE, 
        u'na'      : Date.MOD_AFTER,
        u'tegen'   : Date.MOD_ABOUT,
        u'om'      : Date.MOD_ABOUT,
        u'rond'    : Date.MOD_ABOUT,
        u'circa'   : Date.MOD_ABOUT,
        u'ca.'     : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        u'Gregoriaans'    : Date.CAL_GREGORIAN,
        u'Greg.'          : Date.CAL_GREGORIAN,
        u'Juliaans'       : Date.CAL_JULIAN,
        u'Jul.'           : Date.CAL_JULIAN,
        u'Hebreeuws'      : Date.CAL_HEBREW,
        u'Hebr.'          : Date.CAL_HEBREW,
        u'Islamitisch'      : Date.CAL_ISLAMIC,
        u'Isl.'           : Date.CAL_ISLAMIC,
        u'Franse republiek': Date.CAL_FRENCH,
        u'Fran.'         : Date.CAL_FRENCH,
        u'Persisch'       : Date.CAL_PERSIAN,
        }

    quality_to_int = {
        u'geschat' : Date.QUAL_ESTIMATED,
        u'gesch.'    : Date.QUAL_ESTIMATED,
        u'berekend' : Date.QUAL_CALCULATED,
        u'ber.'      : Date.QUAL_CALCULATED,
        }

    bce = DateParser.bce + ["voor onze tijdrekening",
                            "voor Christus",
                            "v\. Chr\."]
    
    def init_strings(self):
        DateParser.init_strings(self)
        self._span = re.compile("(van)\s+(?P<start>.+)\s+(tot)\s+(?P<stop>.+)",
                                re.IGNORECASE)
        self._range = re.compile("tussen\s+(?P<start>.+)\s+en\s+(?P<stop>.+)",
                                 re.IGNORECASE)
        self._text2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?'
                                 % self._mon_str,
                                 re.IGNORECASE)
        self._jtext2= re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?'
                                 % self._jmon_str,
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Dutch display
#
#-------------------------------------------------------------------------
class DateDisplayNL(DateDisplay):

    calendar = (
        "", u" (Juliaans)", u" (Hebreeuws)", 
        u" (Franse Republiek)", u" (Persisch)", u" (Islamitisch)"
        )

    _mod_str = ("",u"voor ",u"na ",u"rond ","","","")
    
    _qual_str = ("",u"geschat ",u"berekend ")
    
    _bce_str = "%s v. Chr."

    formats = (
        "JJJJ-MM-DD (ISO)", "Numerisch DD/MM/JJ", "Maand Dag, Jaar",
        "Mnd. Dag Jaar", "Dag Maand Jaar", "Dag Mnd. Jaar"
        )

    def _display_gregorian(self,date_val):
        year = self._slash_year(date_val[2],date_val[3])
        if self.format == 0:
            return self.display_iso(date_val)
        elif self.format == 1:
	    # Numeric
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
            # Mnd Day, Year
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
            # Day Mnd Year
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
            return "%s%s %s %s %s%s" % (qual_str,u'van',d1,u'tot',d2,self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%stussen %s en %s%s" % (qual_str,d1,d2,self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str,self._mod_str[mod],text,self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('nl_NL','dutch','nl_BE','nl'),
                     DateParserNL, DateDisplayNL)
