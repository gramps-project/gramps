# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Donald N. Allingham
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
Russian-specific classes for parsing and displaying dates.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import re
import calendar

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
# Russian parser
#
#-------------------------------------------------------------------------
class DateParserRU(DateParser):

    modifier_to_int = {
        'до'    : Date.MOD_BEFORE, 
        'по'    : Date.MOD_BEFORE,
        'после' : Date.MOD_AFTER,
        'п.'    : Date.MOD_AFTER,
        'п'    : Date.MOD_AFTER,
        'с'     : Date.MOD_AFTER,
        'ок' : Date.MOD_ABOUT,
        'ок.'   : Date.MOD_ABOUT,
        'около'    : Date.MOD_ABOUT,
        'примерно'  : Date.MOD_ABOUT,
        'прим'     : Date.MOD_ABOUT,
        'прим.'     : Date.MOD_ABOUT,
        'приблизительно'  : Date.MOD_ABOUT,
        'приб.'  : Date.MOD_ABOUT,
        'прибл.'  : Date.MOD_ABOUT,
        'приб'  : Date.MOD_ABOUT,
        'прибл'  : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        'григорианский'   : Date.CAL_GREGORIAN,
        'г'                 : Date.CAL_GREGORIAN,
        'юлианский'            : Date.CAL_JULIAN,
        'ю'                 : Date.CAL_JULIAN,
        'еврейский'         : Date.CAL_HEBREW,
        'е'         : Date.CAL_HEBREW,
        'исламский'         : Date.CAL_ISLAMIC,
        'и'                 : Date.CAL_ISLAMIC,
        'республиканский': Date.CAL_FRENCH,
        'р'                 : Date.CAL_FRENCH,
        'персидский'             : Date.CAL_PERSIAN,
        'п'             : Date.CAL_PERSIAN,
        }

    quality_to_int = {
        'оценено'  : Date.QUAL_ESTIMATED,
        'оцен.'       : Date.QUAL_ESTIMATED,
        'оц.'        : Date.QUAL_ESTIMATED,
        'оцен'       : Date.QUAL_ESTIMATED,
        'оц'        : Date.QUAL_ESTIMATED,
        'вычислено'      : Date.QUAL_CALCULATED,
        'вычисл.'       : Date.QUAL_CALCULATED,
        'выч.' : Date.QUAL_CALCULATED,
        'вычисл'       : Date.QUAL_CALCULATED,
        'выч' : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        self._span     = re.compile("(с|от)\s+(.+)\s+(по|до)\s+(.+)",
                           re.IGNORECASE)
        self._range    = re.compile("(между|меж|меж.)\s+(.+)\s+(и)\s+(.+)",
                           re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Russian displayer
#
#-------------------------------------------------------------------------
class DateDisplayRU(DateDisplay):

    calendar = (
        "", " (юлианский)", 
        " (еврейский)", 
        " (республиканский)", 
        " (персидский)", 
        " (исламский)"
        )

    _mod_str = ("","до ",
        "после ",
        "около ","","","")
    
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
            return "%sс %s по %s%s" % (qual_str,d1,d2,self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%sмежду %s и %s%s" % (qual_str,d1,d2,self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str,self._mod_str[mod],text,self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
from DateHandler import _lang_to_parser, _lang_to_display
for lang_str in ('ru_RU','ru_RU.koi8r','ru_RU.utf8','russian'):
    _lang_to_parser[lang_str] = DateParserRU
    _lang_to_display[lang_str] = DateDisplayRU
