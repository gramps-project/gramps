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

# $Id:_Date_lt.py 9912 2008-01-22 09:17:46Z acraphae $

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
from _DateParser import DateParser
from _DateDisplay import DateDisplay
from _DateHandler import register_datehandler

#-------------------------------------------------------------------------
#
# Lithuanian parser
#
#-------------------------------------------------------------------------
class DateParserLT(DateParser):

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
        u'prancuzų respublikos': Date.CAL_FRENCH, 
        u'r'                 : Date.CAL_FRENCH, 
        u'persų'             : Date.CAL_PERSIAN, 
        u'p'             : Date.CAL_PERSIAN, 
        u'swedish'      : Date.CAL_SWEDISH, 
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

#-------------------------------------------------------------------------
#
# Lithuanian displayer
#
#-------------------------------------------------------------------------
class DateDisplayLT(DateDisplay):
    """
    Lithuanian language date display class. 
    """
    # TODO: Translate these month strings:
    long_months = ( u"January", u"February", u"March", u"April", u"May", 
                    u"June", u"July", u"August", u"September", u"October", 
                    u"November", u"December" )
    
    short_months = ( u"Jan", u"Feb", u"Mar", u"Apr", u"May", u"Jun", u"Jul", 
                     u"Aug", u"Sep", u"Oct", u"Nov", u"Dec" )
    
    calendar = (
        u"", u" (julijaus)", 
        u" (hebrajų)", 
        u" (prancuzų respublikos)", 
        u" (persų)", 
        u" (islamo)", 
        u" (swedish)" 
        )

    _mod_str = (u"", 
        u"prieš ", 
        u"po ", 
        u"apie ", 
        u"", u"", u"")
    
    _qual_str = (u"", u"apytikriai ", u"apskaičiuota ")

    formats = (
        "YYYY-MM-DD (ISO)", "Skaitmeninis", "Mėnuo Diena, Metai", 
        "Mėn DD, YYYY", "Diena Mėnuo Metai", "DD Mėn YYYY"
        )

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
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%s%s %s %s %s%s" % (qual_str, u'nuo', d1, u'iki', 
                                        d2, self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%s%s %s %s %s%s" % (qual_str, u'tarp', d1, u'ir', 
                                        d2, self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, 
                                 self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('lt_LT', 'lt', 'lithuanian', 'Lithuanian'), DateParserLT, DateDisplayLT)
