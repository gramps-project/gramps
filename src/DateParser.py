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

"""
U.S. English date parsing class. Serves as the base class for any localized
date parsing class.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

import re
import time
import locale

import Date


class DateParser:
    """
    Converts a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    # determine the code set returned by nl_langinfo
    _codeset = locale.nl_langinfo(locale.CODESET)

    month_to_int = {
        unicode(locale.nl_langinfo(locale.MON_1),_codeset).lower()   : 1,
        unicode(locale.nl_langinfo(locale.ABMON_1),_codeset).lower() : 1,
        unicode(locale.nl_langinfo(locale.MON_2),_codeset).lower()   : 2,
        unicode(locale.nl_langinfo(locale.ABMON_2),_codeset).lower() : 2,
        unicode(locale.nl_langinfo(locale.MON_3),_codeset).lower()   : 3,
        unicode(locale.nl_langinfo(locale.ABMON_3),_codeset).lower() : 3,
        unicode(locale.nl_langinfo(locale.MON_4),_codeset).lower()   : 4,
        unicode(locale.nl_langinfo(locale.ABMON_4),_codeset).lower() : 4,
        unicode(locale.nl_langinfo(locale.MON_5),_codeset).lower()   : 5,
        unicode(locale.nl_langinfo(locale.ABMON_5),_codeset).lower() : 5,
        unicode(locale.nl_langinfo(locale.MON_6),_codeset).lower()   : 6,
        unicode(locale.nl_langinfo(locale.ABMON_6),_codeset).lower() : 6,
        unicode(locale.nl_langinfo(locale.MON_7),_codeset).lower()   : 7,
        unicode(locale.nl_langinfo(locale.ABMON_7),_codeset).lower() : 7,
        unicode(locale.nl_langinfo(locale.MON_8),_codeset).lower()   : 8,
        unicode(locale.nl_langinfo(locale.ABMON_8),_codeset).lower() : 8,
        unicode(locale.nl_langinfo(locale.MON_9),_codeset).lower()   : 9,
        unicode(locale.nl_langinfo(locale.ABMON_9),_codeset).lower() : 9,
        unicode(locale.nl_langinfo(locale.MON_10),_codeset).lower()  : 10,
        unicode(locale.nl_langinfo(locale.ABMON_10),_codeset).lower(): 10,
        unicode(locale.nl_langinfo(locale.MON_11),_codeset).lower()  : 11,
        unicode(locale.nl_langinfo(locale.ABMON_11),_codeset).lower(): 11,
        unicode(locale.nl_langinfo(locale.MON_12),_codeset).lower()  : 12,
        unicode(locale.nl_langinfo(locale.ABMON_12),_codeset).lower(): 12,
       }

    modifier_to_int = {
        'before'   : Date.MOD_BEFORE,
        'bef'      : Date.MOD_BEFORE,
        'bef.'     : Date.MOD_BEFORE,
        'after'    : Date.MOD_AFTER,
        'aft'      : Date.MOD_AFTER,
        'aft.'     : Date.MOD_AFTER,
        'about'    : Date.MOD_ABOUT,
        'abt.'     : Date.MOD_ABOUT,
        'abt'      : Date.MOD_ABOUT,
        'circa'    : Date.MOD_ABOUT,
        'c.'       : Date.MOD_ABOUT,
        'around'   : Date.MOD_ABOUT,
        }
    
    quality_to_int = {
        'estimated'  : Date.QUAL_ESTIMATED,
        'est.'       : Date.QUAL_ESTIMATED,
        'est'        : Date.QUAL_ESTIMATED,
        'calc.'      : Date.QUAL_CALCULATED,
        'calc'       : Date.QUAL_CALCULATED,
        'calculated' : Date.QUAL_CALCULATED,
        }
    
    _qual_str = '(' + '|'.join(
        [ key.replace('.','\.') for key in quality_to_int.keys() ]
        ) + ')'
    _mod_str  = '(' + '|'.join(
        [ key.replace('.','\.') for key in modifier_to_int.keys() ]
        ) + ')'
    _mon_str  = '(' + '|'.join(month_to_int.keys()) + ')'
    
    _qual     = re.compile("%s\s+(.+)" % _qual_str,re.IGNORECASE)
    _span     = re.compile("from\s+(.+)\s+to\s+(.+)",re.IGNORECASE)
    _range    = re.compile("(bet.|between)\s+(.+)\s+and\s+(.+)",re.IGNORECASE)
    _modifier = re.compile('%s\s+(.*)' % _mod_str,re.IGNORECASE)
    _text     = re.compile('%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?' % _mon_str,re.IGNORECASE)
    _text2    = re.compile('(\d+)?\s+?%s\s*((\d+)(/\d+)?)?' % _mon_str,re.IGNORECASE)
    _range2   = re.compile('%s\s+(\d+)-(\d+)\s*,?\s*((\d+)(/\d+)?)?' % _mon_str,re.IGNORECASE)
    _numeric  = re.compile("((\d+)[/\.])?((\d+)[/\.])?(\d+)")
    _iso      = re.compile("(\d+)-(\d+)-(\d+)")

    def _get_int(self,val):
        """
        Converts the string to an integer if the value is not None. If the
        value is None, a zero is returned
        """
        if val == None:
            return 0
        else:
            return int(val)

    def _parse_subdate(self,text):
        """
        Converts only the date portion of a date.
        """
        try:
            value = time.strptime(text)
            return (value[2],value[1],value[0],False)
        except ValueError:
            pass

        match = self._text.match(text)
        if match:
            groups = match.groups()
            if groups[0] == None:
                m = 0
            else:
                m = self.month_to_int[groups[0].lower()]

            d = self._get_int(groups[1])

            if groups[2] == None:
                y = 0
                s = None
            else:
                y = int(groups[3])
                s = groups[4] != None
            return (d,m,y,s)

        match = self._text2.match(text)
        if match:
            groups = match.groups()
            if groups[1] == None:
                m = 0
            else:
                m = self.month_to_int[groups[1].lower()]

            d = self._get_int(groups[0])

            if groups[2] == None:
                y = 0
                s = None
            else:
                y = int(groups[3])
                s = groups[4] != None
            return (d,m,y,s)

        match = self._iso.match(text)
        if match:
            groups = match.groups()
            y = self._get_int(groups[0])
            m = self._get_int(groups[1])
            d = self._get_int(groups[2])
            return (d,m,y,False)

        match = self._numeric.match(text)
        if match:
            groups = match.groups()
            m = self._get_int(groups[1])
            d = self._get_int(groups[3])
            y = self._get_int(groups[4])
            return (d,m,y,False)

        return Date.EMPTY

    def set_date(self,date,text):
        """
        Parses the text and sets the date according to the parsing.
        """
        date.set_text_value(text)
        qual = Date.QUAL_NONE

        match = self._qual.match(text)
        if match:
            grps = match.groups()
            qual = self.quality_to_int[grps[0].lower()]
            text = grps[1]
    
        match = self._span.match(text)
        if match:
            grps = match.groups()
            start = self._parse_subdate(grps[0])
            stop = self._parse_subdate(grps[1])
            date.set(qual,Date.MOD_SPAN,Date.CAL_GREGORIAN,start + stop)
            return
    
        match = self._range.match(text)
        if match:
            grps = match.groups()
            start = self._parse_subdate(grps[1])
            stop = self._parse_subdate(grps[2])
            date.set(qual,Date.MOD_RANGE,Date.CAL_GREGORIAN,start + stop)
            return

        match = self._range2.match(text)
        if match:
            grps = match.groups()
            m = self.month_to_int[grps[0].lower()]

            d0 = self._get_int(grps[1])
            d1 = self._get_int(grps[2])

            if grps[3] == None:
                y = 0
                s = None
            else:
                y = int(grps[3])
                s = grps[4] != None
            date.set(qual,Date.MOD_RANGE,Date.CAL_GREGORIAN,
                     (d0,m,y,s,d1,m,y,s))
            return
    
        match = self._modifier.match(text)
        if match:
            grps = match.groups()
            start = self._parse_subdate(grps[1])
            mod = self.modifier_to_int.get(grps[0].lower(),Date.MOD_NONE)
            date.set(qual,mod,Date.CAL_GREGORIAN,start)
            return

        subdate = self._parse_subdate(text)
        if subdate == Date.EMPTY:
            date.set_as_text(text)
        else:
            date.set(qual,Date.MOD_NONE,Date.CAL_GREGORIAN,subdate)

    def parse(self,text):
        """
        Parses the text, returning a Date object.
        """
        new_date = Date.Date()
        self.set_date(new_date,text)
        return new_date
