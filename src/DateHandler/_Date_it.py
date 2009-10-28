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

# Italian version, 2009 (derived from the catalan version)

"""
Italian-specific classes for parsing and displaying dates.
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
# Italian parser
#
#-------------------------------------------------------------------------
class DateParserIT(DateParser):

    modifier_to_int = {
        u'prima del'            : Date.MOD_BEFORE, 
        u'prima'                : Date.MOD_BEFORE, 
        u'dopo del'             : Date.MOD_AFTER, 
        u'dopo'                 : Date.MOD_AFTER, 
        u'approssimativamente'  : Date.MOD_ABOUT, 
        u'apross.'              : Date.MOD_ABOUT, 
        u'apross'               : Date.MOD_ABOUT, 
        u'circa il'             : Date.MOD_ABOUT, 
        u'circa'                : Date.MOD_ABOUT, 
        u'ca.'                  : Date.MOD_ABOUT, 
        u'ca'                   : Date.MOD_ABOUT, 
        u'c.'                   : Date.MOD_ABOUT, 
        }

    calendar_to_int = {
        u'gregoriano'    : Date.CAL_GREGORIAN, 
        u'g'             : Date.CAL_GREGORIAN, 
        u'giuliano'      : Date.CAL_JULIAN, 
        u'j'             : Date.CAL_JULIAN, 
        u'ebraico'       : Date.CAL_HEBREW, 
        u'e'             : Date.CAL_HEBREW, 
        u'islamico'      : Date.CAL_ISLAMIC, 
        u'i'             : Date.CAL_ISLAMIC, 
        u'rivoluzionario': Date.CAL_FRENCH, 
        u'r'             : Date.CAL_FRENCH, 
        u'persiano'      : Date.CAL_PERSIAN, 
        u'p'             : Date.CAL_PERSIAN, 
        u'svedese'      : Date.CAL_SWEDISH, 
        u's'            : Date.CAL_SWEDISH, 
        }

    quality_to_int = {
        u'stimata'   : Date.QUAL_ESTIMATED, 
        u'st.'       : Date.QUAL_ESTIMATED, 
        u'st'        : Date.QUAL_ESTIMATED, 
        u'calcolata' : Date.QUAL_CALCULATED, 
        u'calc.'     : Date.QUAL_CALCULATED,  
        u'calc'      : Date.QUAL_CALCULATED, 
        }

    def init_strings(self):
        DateParser.init_strings(self)
        _span_1 = [u'dal', u'da']
        _span_2 = [u'al', u'a']
        _range_1 = [u'tra', u'fra']
        _range_2 = [u'e']
        self._span  = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" % 
                                 ('|'.join(_span_1), '|'.join(_span_2)), 
                                 re.IGNORECASE)
        self._range = re.compile("(%s)\s+(?P<start>.+)\s+(%s)\s+(?P<stop>.+)" %
                                 ('|'.join(_range_1), '|'.join(_range_2)), 
                                 re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Italian display
#
#-------------------------------------------------------------------------
class DateDisplayIT(DateDisplay):
    """
    Italian language date display class. 
    """
    # TODO: Translate these month strings:
    long_months = ( u"", u"January", u"February", u"March", u"April", u"May", 
                    u"June", u"July", u"August", u"September", u"October", 
                    u"November", u"December" )
    
    short_months = ( u"", u"Jan", u"Feb", u"Mar", u"Apr", u"May", u"Jun", 
                     u"Jul", u"Aug", u"Sep", u"Oct", u"Nov", u"Dec" )
    
    calendar = (
        "", u" (Giuliano)", u" (Ebraico)", 
        u" (Rivoluzionario)", u" (Persiano)", u" (Islamico)", 
        u" (Svedese)" 
        )

    _mod_str = ("", u"prima del ", u"dopo del ", u"circa il ", "", "", "")

    _qual_str = ("", "stimata ", "calcolata ")

    french = (
        u'', 
        u'vendemmiaio', 
        u'brumaio', 
        u'frimaio', 
        u'nevoso', 
        u'piovoso', 
        u'ventoso', 
        u'germile', 
        u'fiorile', 
        u'pratile', 
        u'messidoro', 
        u'termidoro', 
        u'fruttidoro', 
        u'extra', 
        )
    
    formats = (
        "AAAA-MM-DD (ISO)", "Numerico", "Mese Giorno Anno", 
        "MES Giorno, Anno", "Giorno Mese Anno", "Giorno MES Anno"
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
            return "%s%s %s %s %s%s" % (qual_str, u'dal', d1, u'al', d2, self.calendar[cal])
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            return "%s%s %s %s %s%s" % (qual_str, u'tra', d1, u'e', d2, self.calendar[cal])
        else:
            text = self.display_cal[date.get_calendar()](start)
            return "%s%s%s%s" % (qual_str, self._mod_str[mod], text, self.calendar[cal])

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('it_IT', 'it', 'italian', 'Italian', 'it_CH'), 
    DateParserIT, DateDisplayIT)
