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
French-specific classes for parsing and displaying dates.
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
# French parser
#
#-------------------------------------------------------------------------
class DateParserFR(DateParser):

    modifier_to_int = {
        'avant'    : Date.MOD_BEFORE, 
        'av.'      : Date.MOD_BEFORE, 
        'av'       : Date.MOD_BEFORE, 
        'après' : Date.MOD_AFTER,
        'ap.'    : Date.MOD_AFTER,
        'ap'     : Date.MOD_AFTER,
        'env.'   : Date.MOD_ABOUT,
        'env'    : Date.MOD_ABOUT,
        'circa'  : Date.MOD_ABOUT,
        'c.'     : Date.MOD_ABOUT,
        'vers'   : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        'grégorien'      : Date.CAL_GREGORIAN,
        'g'                     : Date.CAL_GREGORIAN,
        'julien'                : Date.CAL_JULIAN,
        'j'                     : Date.CAL_JULIAN,
        'hébreu'         : Date.CAL_HEBREW,
        'h'                     : Date.CAL_HEBREW,
        'islamique'             : Date.CAL_ISLAMIC,
        'i'                     : Date.CAL_ISLAMIC,
        'révolutionnaire': Date.CAL_FRENCH,
        'r'                     : Date.CAL_FRENCH,
        'perse'                 : Date.CAL_PERSIAN,
        'p'                     : Date.CAL_PERSIAN,
        }

    quality_to_int = {
        'estimated'  : Date.QUAL_ESTIMATED,
        'est.'       : Date.QUAL_ESTIMATED,
        'est'        : Date.QUAL_ESTIMATED,
        'calc.'      : Date.QUAL_CALCULATED,
        'calc'       : Date.QUAL_CALCULATED,
        'calculated' : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        self._span     = re.compile("(de)\s+(.+)\s+(à)\s+(.+)",
                           re.IGNORECASE)
        self._range    = re.compile("(ent.|ent|entre)\s+(.+)\s+(et)\s+(.+)",
                           re.IGNORECASE)

#-------------------------------------------------------------------------
#
# French display
#
#-------------------------------------------------------------------------
class DateDisplayFR(DateDisplay):

    calendar = (
        "", " (Julien)", " (Hébreu)", 
        " (Révolutionnaire)", " (Perse)", " (Islamique)"
        )

    _mod_str = ("","avant ","après ","vers ","","","")
    
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
            return "%sde %s à %s%s" % (qual_str,d1,d2,self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%sentre %s et %s%s" % (qual_str,d1,d2,self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str,self._mod_str[mod],text,self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
from DateHandler import _lang_to_parser, _lang_to_display
for lang_str in ('fr_FR','fr_FR.iso88591','fr_FR.utf8','french'):
    _lang_to_parser[lang_str] = DateParserFR
    _lang_to_display[lang_str] = DateDisplayFR
