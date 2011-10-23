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
# DateHandler/_Date_da.py
# $Id$
#

"""
Danish-specific classes for parsing and displaying dates.
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
# Danish parser class
#
#-------------------------------------------------------------------------
class DateParserDa(DateParser):
    """
    Convert a text string into a Date object, expecting a date
    notation in the Danish language. If the date cannot be converted, 
    the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        u'før'    : Date.MOD_BEFORE, 
        u'inden'  : Date.MOD_BEFORE, 
        u'efter'   : Date.MOD_AFTER, 
        u'omkring' : Date.MOD_ABOUT, 
        u'ca.'     : Date.MOD_ABOUT
        }

    bce = ["f Kr"]

    calendar_to_int = {
        u'gregoriansk   '      : Date.CAL_GREGORIAN, 
        u'g'                   : Date.CAL_GREGORIAN, 
        u'juliansk'            : Date.CAL_JULIAN, 
        u'j'                   : Date.CAL_JULIAN, 
        u'hebraisk'            : Date.CAL_HEBREW, 
        u'h'                   : Date.CAL_HEBREW, 
        u'islamisk'            : Date.CAL_ISLAMIC, 
        u'muslimsk'            : Date.CAL_ISLAMIC, 
        u'i'                   : Date.CAL_ISLAMIC, 
        u'fransk'              : Date.CAL_FRENCH, 
        u'fransk republikansk' : Date.CAL_FRENCH, 
        u'f'                   : Date.CAL_FRENCH, 
        u'persisk'             : Date.CAL_PERSIAN, 
        u'p'                   : Date.CAL_PERSIAN, 
        u'svensk'              : Date.CAL_SWEDISH, 
        u's'                   : Date.CAL_SWEDISH, 
        }
    
    quality_to_int = {
        u'estimeret' : Date.QUAL_ESTIMATED, 
        u'beregnet'   : Date.QUAL_CALCULATED, 
        }
    
    def init_strings(self):
        DateParser.init_strings(self)
        self._span     = re.compile(u"(fra)?\s*(?P<start>.+)\s*(til|--|–)\s*(?P<stop>.+)", 
                                    re.IGNORECASE)
        self._range    = re.compile(u"(mellem)\s+(?P<start>.+)\s+og\s+(?P<stop>.+)", 
                                    re.IGNORECASE)

#-------------------------------------------------------------------------
#
# Danish display class
#
#-------------------------------------------------------------------------
class DateDisplayDa(DateDisplay):
    """
    Danish language date display class. 
    """

    long_months = ( u"", u"januar", u"februar", u"marts", u"april", u"maj", 
                    u"juni", u"juli", u"august", u"september", u"oktober", 
                    u"november", u"december" )
    
    short_months = ( u"", u"jan", u"feb", u"mar", u"apr", u"maj", u"jun", 
                     u"jul", u"aug", u"sep", u"okt", u"nov", u"dec" )

    formats = (
        u"ÅÅÅÅ-MM-DD (ISO)", 
        u"Numerisk", 
        u"Måned dag, år", 
        u"Md Dag År", 
        u"Dag måned år", 
        u"Dag md År", 
        )

    calendar = (
        "", 
        "juliansk", 
        "hebraisk", 
        "fransk republikansk", 
        "persisk", 
        "islamisk", 
        "svensk" 
        )
    
    _mod_str = ("", u"før ", u"efter ", u"ca. ", "", "", "")

    _qual_str = ("", u"beregnet ", u"beregnet ")
    
    _bce_str = "%s f. Kr."

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
            return u""
        elif mod == Date.MOD_SPAN:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return u"%sfra %s til %s%s" % (qual_str, d1, d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return u"%smellem %s og %s%s" % (qual_str, d1, d2, 
                                              scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return u"%s%s%s%s" % (qual_str, self._mod_str[mod], 
                                 text, scal)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------
register_datehandler(('da_DK', 'da', 'dansk', 'Danish'), DateParserDa, DateDisplayDa)
