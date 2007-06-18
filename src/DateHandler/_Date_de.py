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
German-specific classes for parsing and displaying dates.
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
# French parser
#
#-------------------------------------------------------------------------
class DateParserDE(DateParser):

    month_to_int = DateParser.month_to_int
    # Always add german and austrian name variants no matter what the current locale is
    month_to_int[u"januar"] = 1
    month_to_int[u"jan"]    = 1
    month_to_int[u"jänner"] = 1
    month_to_int[u"jän"]    = 1
    # Add other common latin, local and historical variants  
    month_to_int[u"januaris"] = 1
    month_to_int[u"jenner"] = 1
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
        u'vor'    : Date.MOD_BEFORE, 
        u'nach'   : Date.MOD_AFTER,
        u'gegen'  : Date.MOD_ABOUT,
        u'um'     : Date.MOD_ABOUT,
        u'etwa'   : Date.MOD_ABOUT,
        u'circa'  : Date.MOD_ABOUT,
        u'ca.'  : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        u'gregorianisch'  : Date.CAL_GREGORIAN,
        u'greg.'          : Date.CAL_GREGORIAN,
        u'julianisch'     : Date.CAL_JULIAN,
        u'jul.'           : Date.CAL_JULIAN,
        u'hebräisch'      : Date.CAL_HEBREW,
        u'hebr.'          : Date.CAL_HEBREW,
        u'islamisch'      : Date.CAL_ISLAMIC,
        u'isl.'           : Date.CAL_ISLAMIC,
        u'französisch republikanisch': Date.CAL_FRENCH,
        u'franz.'         : Date.CAL_FRENCH,
        u'persisch'       : Date.CAL_PERSIAN,
        }

    quality_to_int = {
        u'geschätzt' : Date.QUAL_ESTIMATED,
        u'gesch.'    : Date.QUAL_ESTIMATED,
        u'errechnet' : Date.QUAL_CALCULATED,
        u'berechnet' : Date.QUAL_CALCULATED,
        u'ber.'      : Date.QUAL_CALCULATED,
        }

    bce = ["vor unserer Zeitrechnung", "vor unserer Zeit",
           "vor der Zeitrechnung", "vor der Zeit",
           "v. u. Z.", "v. d. Z.", "v.u.Z.", "v.d.Z.", 
           "vor Christi Geburt", "vor Christus", "v. Chr."] + DateParser.bce
    
    def init_strings(self):
        DateParser.init_strings(self)
        self._span  = re.compile("(von|vom)\s+(?P<start>.+)\s+(bis)\s+(?P<stop>.+)",re.IGNORECASE)
        self._range = re.compile("zwischen\s+(?P<start>.+)\s+und\s+(?P<stop>.+)", re.IGNORECASE)
        self._text2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?' % self._mon_str,
                                 re.IGNORECASE)
        self._jtext2= re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?' % self._jmon_str,
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# French display
#
#-------------------------------------------------------------------------
class DateDisplayDE(DateDisplay):

    calendar = (
        "", u" (julianisch)", u" (hebräisch)", 
        u" (französisch republikanisch)", u" (persisch)", u" (islamisch)"
        )

    _mod_str = ("",u"vor ",u"nach ",u"etwa ","","","")
    
    _qual_str = ("",u"geschätzt ",u"errechnet ")
    
    _bce_str = "%s v. u. Z."

    formats = (
        "JJJJ-MM-DD (ISO)", "Numerisch", "Monat Tag Jahr",
        "MONAT Tag Jahr", "Tag. Monat Jahr", "Tag. MONAT Jahr"
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
                value = "%d. %s %s" % (date_val[0],self._months[date_val[1]],year)
        else:
            # Day MON Year
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self._MONS[date_val[1]],year)
            else:
                value = "%d. %s %s" % (date_val[0],self._MONS[date_val[1]],year)
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
            return "%s%s %s %s %s%s" % (qual_str,u'von',d1,u'bis',d2,self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%szwischen %s und %s%s" % (qual_str,d1,d2,self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str,self._mod_str[mod],text,self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('de_DE','german','de_AT','de_CH',
                      'de_LI','de_LU','de_BE','de'),
                     DateParserDE, DateDisplayDE)
