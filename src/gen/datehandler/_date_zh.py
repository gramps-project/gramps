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

import re

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

from gen.lib import Date
from _dateparser import DateParser
from _datedisplay import DateDisplay
from _datehandler import register_datehandler

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
        u'before' : Date.MOD_BEFORE, u'bef'    : Date.MOD_BEFORE,
        u'bef.'   : Date.MOD_BEFORE, u'after'  : Date.MOD_AFTER,
        u'aft'    : Date.MOD_AFTER,  u'aft.'   : Date.MOD_AFTER,
        u'about'  : Date.MOD_ABOUT,  u'abt.'   : Date.MOD_ABOUT,
        u'abt'    : Date.MOD_ABOUT,  u'circa'  : Date.MOD_ABOUT,
        u'c.'     : Date.MOD_ABOUT,  u'around' : Date.MOD_ABOUT,
        }

    month_to_int = DateParser.month_to_int

    month_to_int[u"正"] = 1
    month_to_int[u"一"] = 1
    month_to_int[u"zhēngyuè"] = 1
    month_to_int[u"二"] = 2
    month_to_int[u"èryuè"] = 2
    month_to_int[u"三"] = 3
    month_to_int[u"sānyuè"] = 3
    month_to_int[u"四"] = 4
    month_to_int[u"sìyuè"] = 4
    month_to_int[u"五"] = 5
    month_to_int[u"wǔyuè"] = 5
    month_to_int[u"六"] = 6
    month_to_int[u"liùyuè"] = 6
    month_to_int[u"七"] = 7
    month_to_int[u"qīyuè"] = 7
    month_to_int[u"八"] = 8
    month_to_int[u"bāyuè"] = 8
    month_to_int[u"九"] = 9
    month_to_int[u"jiǔyuè"] = 9
    month_to_int[u"十"] = 10
    month_to_int[u"shíyuè"] = 10
    month_to_int[u"十一"] = 11
    month_to_int[u"shíyīyuè"] = 11
    month_to_int[u"十二"] = 12
    month_to_int[u"shí'èryuè"] = 12
    month_to_int[u"假閏"] = 13
    month_to_int[u"jiǎ rùn yùe"] = 13
    
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
        u'estimated'  : Date.QUAL_ESTIMATED,
        u'est.'       : Date.QUAL_ESTIMATED,
        u'est'        : Date.QUAL_ESTIMATED,
        u'calc.'      : Date.QUAL_CALCULATED,
        u'calc'       : Date.QUAL_CALCULATED,
        u'calculated' : Date.QUAL_CALCULATED,
        }
        
    # translate english strings into chinese

    bce = [u"before calendar", u"negative year"] + DateParser.bce

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

        self._span     = re.compile(u"(from)\s+(?P<start>.+)\s+to\s+(?P<stop>.+)",
                                    re.IGNORECASE)
        self._range    = re.compile(u"(bet|bet.|between)\s+(?P<start>.+)\s+and\s+(?P<stop>.+)",
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
 
    long_months = ( u"", u"January", u"February", u"March", u"April", u"May", 
                    u"June", u"July", u"August", u"September", u"October", 
                    u"November", u"December" )
    
    short_months = ( u"", u"Jan", u"Feb", u"Mar", u"Apr", u"May", u"Jun",
                     u"Jul", u"Aug", u"Sep", u"Oct", u"Nov", u"Dec" )

    calendar = (
        "", u"Julian", u"Hebrew", u"French Republican", 
        u"Persian", u"Islamic", u"Swedish" 
        )

    _mod_str = ("", u"before ", u"after ", u"around ", "", "", "")

    _qual_str = ("", u"estimated ", u"calculated ", "")

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
            return "%s%s %s %s %s%s" % (qual_str, u'from', date1, u'to', 
            date2, scal)
        elif mod == Date.MOD_RANGE:
            date1 = self.display_cal[cal](start)
            date2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            # translate english strings into chinese
            return "%s%s %s %s %s%s" % (qual_str, u'between', date1, u'and',
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
