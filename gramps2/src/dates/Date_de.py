# -*- coding: utf-8 -*-
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
import Date
from DateParser import DateParser
from DateDisplay import DateDisplay

#-------------------------------------------------------------------------
#
# French parser
#
#-------------------------------------------------------------------------
class DateParserDE(DateParser):

    modifier_to_int = {
        u'vor'    : Date.MOD_BEFORE, 
        u'nach'   : Date.MOD_AFTER,
        u'über'   : Date.MOD_ABOUT,
        u'um'     : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        u'Gregorianisch'  : Date.CAL_GREGORIAN,
        u'Julianisch'     : Date.CAL_JULIAN,
        u'Hebräisch'      : Date.CAL_HEBREW,
        u'Islamisch'      : Date.CAL_ISLAMIC,
        u'Französischer Republikaner': Date.CAL_FRENCH,
        u'Persisch'       : Date.CAL_PERSIAN,
        }

    quality_to_int = {
        u'geschätzt'  : Date.QUAL_ESTIMATED,
        u'errechnet' : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        self._span  = re.compile("(von|vom)\s+(.+)\s+bis\s+(.+)",re.IGNORECASE)
        self._range = re.compile("zwischen\s+(.+)\s+and\s+(.+)", re.IGNORECASE)

#-------------------------------------------------------------------------
#
# French display
#
#-------------------------------------------------------------------------
class DateDisplayDE(DateDisplay):

    calendar = (
        "", u" (Julianisch)", u" (Hebräisch)", 
        u" (Französischer Republikaner)", u" (Persisch)", u" (Islamisch)"
        )

    _mod_str = ("",u"avant ",u"après ",u"vers ","","","")
    
    _qual_str = ("","calculated ","estimated ")

    formats = (
        "JJJJ-MM-DD (ISO)", "Numerisch", "Monat Tag Jahr",
        "MICH Tag Jahr", "Tag Monat Jahr", "Tag MONAT Jahr"
        )

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
            return "%s%s %s %s %s%s" % (qual_str,u'de',d1,u'à',d2,self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%szwischen %s and %s%s" % (qual_str,d1,d2,self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str,self._mod_str[mod],text,self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
from DateHandler import register_datehandler
register_datehandler(('de_DE','german'),DateParserDE, DateDisplayDE)
