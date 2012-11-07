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
#

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------

"""
Chinese-specific classes for parsing and displaying dates.
"""
from __future__ import unicode_literals
import re

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

#-------------------------------------------------------------------------
#
# Chinese parser
#
#-------------------------------------------------------------------------
class DateParserZH(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """
    
    # translate english strings into chinese
    
    modifier_to_int = {
        'before' : Date.MOD_BEFORE, 'bef'    : Date.MOD_BEFORE,
        'bef.'   : Date.MOD_BEFORE, 'after'  : Date.MOD_AFTER,
        'aft'    : Date.MOD_AFTER,  'aft.'   : Date.MOD_AFTER,
        'about'  : Date.MOD_ABOUT,  'abt.'   : Date.MOD_ABOUT,
        'abt'    : Date.MOD_ABOUT,  'circa'  : Date.MOD_ABOUT,
        'c.'     : Date.MOD_ABOUT,  'around' : Date.MOD_ABOUT,
        }

    month_to_int = DateParser.month_to_int

    month_to_int["正"] = 1
    month_to_int["一"] = 1
    month_to_int["zhēngyuè"] = 1
    month_to_int["二"] = 2
    month_to_int["èryuè"] = 2
    month_to_int["三"] = 3
    month_to_int["sānyuè"] = 3
    month_to_int["四"] = 4
    month_to_int["sìyuè"] = 4
    month_to_int["五"] = 5
    month_to_int["wǔyuè"] = 5
    month_to_int["六"] = 6
    month_to_int["liùyuè"] = 6
    month_to_int["七"] = 7
    month_to_int["qīyuè"] = 7
    month_to_int["八"] = 8
    month_to_int["bāyuè"] = 8
    month_to_int["九"] = 9
    month_to_int["jiǔyuè"] = 9
    month_to_int["十"] = 10
    month_to_int["shíyuè"] = 10
    month_to_int["十一"] = 11
    month_to_int["shíyīyuè"] = 11
    month_to_int["十二"] = 12
    month_to_int["shí'èryuè"] = 12
    month_to_int["假閏"] = 13
    month_to_int["jiǎ rùn yùe"] = 13
    
    # translate english strings into chinese
    
    calendar_to_int = {
        'gregorian'        : Date.CAL_GREGORIAN,
        'g'                : Date.CAL_GREGORIAN,
        'julian'           : Date.CAL_JULIAN,
        'j'                : Date.CAL_JULIAN,
        'hebrew'           : Date.CAL_HEBREW,
        'h'                : Date.CAL_HEBREW,
        'islamic'          : Date.CAL_ISLAMIC,
        'i'                : Date.CAL_ISLAMIC,
        'french'           : Date.CAL_FRENCH,
        'french republican': Date.CAL_FRENCH,
        'f'                : Date.CAL_FRENCH,
        'persian'          : Date.CAL_PERSIAN,
        'p'                : Date.CAL_PERSIAN, 
        'swedish'          : Date.CAL_SWEDISH,
        's'                : Date.CAL_SWEDISH,
        }
        
    # translate english strings into chinese

    quality_to_int = {
        'estimated'  : Date.QUAL_ESTIMATED,
        'est.'       : Date.QUAL_ESTIMATED,
        'est'        : Date.QUAL_ESTIMATED,
        'calc.'      : Date.QUAL_CALCULATED,
        'calc'       : Date.QUAL_CALCULATED,
        'calculated' : Date.QUAL_CALCULATED,
        }
        
    # translate english strings into chinese

    bce = ["before calendar", "negative year"] + DateParser.bce

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.
        
        Most of the re's in most languages can stay as is. span and range
        most likely will need to change. Whatever change is done, this method
        may be called first as DateParser.init_strings(self) so that the
        invariant expresions don't need to be repeteadly coded. All differences
        can be coded after DateParser.init_strings(self) call, that way they
        override stuff from this method. See DateParserRU() as an example.
        """
        DateParser.init_strings(self)
        
        # day: 日 ; month : 月 ; year : 年

        # See DateParser class; translate english strings (from/to, between/and) into chinese
        # do not translate <start> and <stop>

        self._span     = re.compile("(from)\s+(?P<start>.+)\s+to\s+(?P<stop>.+)",
                                    re.IGNORECASE)
        self._range    = re.compile("(bet|bet.|between)\s+(?P<start>.+)\s+and\s+(?P<stop>.+)",
                                    re.IGNORECASE)
                                    
    #def _parse_lunisolar(self, date_val=text):
        #text = text.strip() # otherwise spaces can make it a bad date
        #date = Date(self._qual_str, self._mod_str, self._cal_str, text, self._ny_str)
        #return unicode(text)
                               
#-------------------------------------------------------------------------
#
# Chinese display
#
#-------------------------------------------------------------------------
class DateDisplayZH(DateDisplay):
    """
    Chinese language date display class. 
    """

    # translate english strings into chinese
 
    long_months = ( "", "January", "February", "March", "April", "May", 
                    "June", "July", "August", "September", "October", 
                    "November", "December" )
    
    short_months = ( "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" )

    calendar = (
        "", "Julian", "Hebrew", "French Republican", 
        "Persian", "Islamic", "Swedish" 
        )

    _mod_str = ("", "before ", "after ", "around ", "", "", "")

    _qual_str = ("", "estimated ", "calculated ", "")

    _bce_str = "%s B.C.E."


    def display(self, date):
        """
        Return a text string representing the date.
        """

        mod = date.get_modifier()
        cal = date.get_calendar()
        qual = date.get_quality()
        start = date.get_start_date()
        newyear = date.get_new_year()

        qual_str = (self._qual_str)[qual]

        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN:
            date1 = self.display_cal[cal](start)
            date2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            # translate english strings into chinese
            return "%s%s %s %s %s%s" % (qual_str, 'from', date1, 'to', 
            date2, scal)
        elif mod == Date.MOD_RANGE:
            date1 = self.display_cal[cal](start)
            date2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            # translate english strings into chinese
            return "%s%s %s %s %s%s" % (qual_str, 'between', date1, 'and',
                    date2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, (self._mod_str)[mod], text, 
            scal)

    #def _display_chinese(self, date_val):
        #self._tformat = '%Y年%m月%d日'
        #year = self._slash_year(date_val[2], date_val[3])
        #if date_val[3]:
            #return self.display_iso(date_val)
        #else:
            #if date_val[0] == date_val[1] == 0:
                #value = u'%Y年' % date_val[2]
            #else:
                #value = self._tformat.replace('%m月', str(self.lunisolar[date_val[1]]))
                #value = u'%m月' % date_val[1]
                #value = u'%d日' % date_val[0]
                #value = u'%Y年' % date_val[2]


#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------

register_datehandler(('zh_CN', 'zh_TW', 'zh_SG', 'zh_HK', 'zh', 'chinese', 'Chinese'), 
                       DateParserZH, DateDisplayZH)
