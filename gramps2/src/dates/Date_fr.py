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
        u'avant'    : Date.MOD_BEFORE, 
        u'av.'      : Date.MOD_BEFORE, 
        u'av'       : Date.MOD_BEFORE, 
        u'après' : Date.MOD_AFTER,
        u'ap.'    : Date.MOD_AFTER,
        u'ap'     : Date.MOD_AFTER,
        u'env.'   : Date.MOD_ABOUT,
        u'env'    : Date.MOD_ABOUT,
        u'circa'  : Date.MOD_ABOUT,
        u'c.'     : Date.MOD_ABOUT,
        u'vers'   : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        u'grégorien'      : Date.CAL_GREGORIAN,
        u'g'                     : Date.CAL_GREGORIAN,
        u'julien'                : Date.CAL_JULIAN,
        u'j'                     : Date.CAL_JULIAN,
        u'hébreu'         : Date.CAL_HEBREW,
        u'h'                     : Date.CAL_HEBREW,
        u'islamique'             : Date.CAL_ISLAMIC,
        u'i'                     : Date.CAL_ISLAMIC,
        u'révolutionnaire': Date.CAL_FRENCH,
        u'r'                     : Date.CAL_FRENCH,
        u'perse'                 : Date.CAL_PERSIAN,
        u'p'                     : Date.CAL_PERSIAN,
        }

    quality_to_int = {
        u'estimated'  : Date.QUAL_ESTIMATED,
        u'est.'       : Date.QUAL_ESTIMATED,
        u'est'        : Date.QUAL_ESTIMATED,
        u'calc.'      : Date.QUAL_CALCULATED,
        u'calc'       : Date.QUAL_CALCULATED,
        u'calculated' : Date.QUAL_CALCULATED,
        }

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = [u'de']
        _span_2 = [u'à']
        _range_1 = [u'ent.',u'ent',u'entre']
        _range_2 = [u'et']
        self._span     = re.compile("(%s)\s+(.+)\s+(%s)\s+(.+)" % 
                                   ('|'.join(_span_1),'|'.join(_span_2)),
                           re.IGNORECASE)
        self._range    = re.compile("(%s)\s+(.+)\s+(%s)\s+(.+)" %
                                   ('|'.join(_range_1),'|'.join(_range_2)),
                           re.IGNORECASE)

#-------------------------------------------------------------------------
#
# French display
#
#-------------------------------------------------------------------------
class DateDisplayFR(DateDisplay):

    calendar = (
        "", u" (Julien)", u" (Hébreu)", 
        u" (Révolutionnaire)", u" (Perse)", u" (Islamique)"
        )

    _mod_str = ("",u"avant ",u"après ",u"vers ","","","")
    
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
            return "%s%s %s %s %s%s" % (qual_str,u'entre',d1,u'et',d2,self.calendar[cal])
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
