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

"""
Date parsing class. Serves as the base class for any localized
date parsing class. The default, base class provides parsing for
English.
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
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".DateParser")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib import Date, DateError
import GrampsLocale

#-------------------------------------------------------------------------
#
# Top-level module functions
#
#-------------------------------------------------------------------------
_max_days  = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
_leap_days = [ 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]

def gregorian_valid(date_tuple):
    """ Checks if date_tuple is a valid date in Gregorian Calendar  """
    day = date_tuple[0]
    month = date_tuple[1]
    valid = True
    try:
        if month > 12:
            valid = False
        elif calendar.isleap(date_tuple[2]):
            if day > _leap_days[month-1]:
                valid = False
        elif day > _max_days[month-1]:
            valid = False
    except:
        valid = False
    return valid

def julian_valid(date_tuple):
    """ Checks if date_tuple is a valid date in Julian Calendar """
    day = date_tuple[0]
    month = date_tuple[1]
    valid = True
    try:
        if month > 12:
            valid = False
        elif (date_tuple[2]) % 4 == 0:
            # julian always have leapyear every 4 year
            if day > _leap_days[month-1]:
                valid = False
        elif day > _max_days[month-1]:
            valid = False
    except:
        valid = False
    return valid

def swedish_valid(date_tuple):
    """ Checks if date_tuple is a valid date in Swedish Calendar """
    valid = gregorian_valid(date_tuple)
    # not sure how <= and >= works with tuples???
    date_tuple = (date_tuple[2], date_tuple[1], date_tuple[0])
    if date_tuple <= (1700, 2, 28):
        valid = False 
    if date_tuple == (1700, 2, 29):  # leapday 1700 was skipped
        valid = False 
    if date_tuple == (1712, 2, 30):  # extra day was inserted 1712
        valid = True 
    if date_tuple >= (1712, 3, 1):   # back to julian
        valid = False
    return valid

def french_valid(date_tuple):
    """ Checks if date_tuple is a valid date in French Calendar """
    valid = True
    # year 1 starts on 22.9.1792
    if date_tuple[2] < 1:
        valid = False       
    return valid

#-------------------------------------------------------------------------
#
# Parser class
#
#-------------------------------------------------------------------------
class DateParser:
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    _fmt_parse = re.compile(".*%(\S).*%(\S).*%(\S).*")

    # RFC-2822 only uses capitalized English abbreviated names, no locales.
    _rfc_days = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')
    _rfc_mons_to_int = {
        'Jan' : 1,  'Feb' : 2,  'Mar' : 3,  'Apr' : 4,
        'May' : 5,  'Jun' : 6,  'Jul' : 7,  'Aug' : 8,
        'Sep' : 9,  'Oct' : 10, 'Nov' : 11, 'Dec' : 12,
        }

    month_to_int = GrampsLocale.month_to_int

    # modifiers before the date
    modifier_to_int = {
        'before' : Date.MOD_BEFORE, 'bef'    : Date.MOD_BEFORE,
        'bef.'   : Date.MOD_BEFORE, 'after'  : Date.MOD_AFTER,
        'aft'    : Date.MOD_AFTER,  'aft.'   : Date.MOD_AFTER,
        'about'  : Date.MOD_ABOUT,  'abt.'   : Date.MOD_ABOUT,
        'abt'    : Date.MOD_ABOUT,  'circa'  : Date.MOD_ABOUT,
        'c.'     : Date.MOD_ABOUT,  'around' : Date.MOD_ABOUT,
        }
    # in some languages some of above listed modifiers are after the date,
    # in that case the subclass should put them into this dictionary instead
    modifier_after_to_int = {}

    hebrew_to_int = {
        "tishri"  : 1,   "heshvan" : 2,   "kislev"  : 3,
        "tevet"   : 4,   "shevat"  : 5,   "adari"   : 6,
        "adarii"  : 7,   "nisan"   : 8,   "iyyar"   : 9,
        "sivan"   : 10,  "tammuz"  : 11,  "av"      : 12,
        "elul"    : 13,
        }

    french_to_int = {
        u'vendémiaire'  : 1,    u'brumaire'   : 2,
        u'frimaire'     : 3,    u'nivôse': 4,
        u'pluviôse'     : 5,    u'ventôse' : 6,
        u'germinal'     : 7,    u'floréal' : 8,
        u'prairial'     : 9,    u'messidor'   : 10,
        u'thermidor'    : 11,   u'fructidor'  : 12,
        u'extra'        : 13
        }

    islamic_to_int = {
        "muharram"           : 1,  "muharram ul haram"  : 1,
        "safar"              : 2,  "rabi`al-awwal"      : 3,
        "rabi'l"             : 3,  "rabi`ul-akhir"      : 4,
        "rabi`ath-thani"     : 4,  "rabi` ath-thani"    : 4,
        "rabi`al-thaany"     : 4,  "rabi` al-thaany"    : 4,
        "rabi' ii"           : 4,  "jumada l-ula"       : 5,
        "jumaada-ul-awwal"   : 5,  "jumaada i"          : 5,
        "jumada t-tania"     : 6,  "jumaada-ul-akhir"   : 6,
        "jumaada al-thaany"  : 6,  "jumaada ii"         : 5,
        "rajab"              : 7,  "sha`ban"            : 8,
        "sha`aban"           : 8,  "ramadan"            : 9,
        "ramadhan"           : 9,  "shawwal"            : 10,
        "dhu l-qa`da"        : 11, "dhu qadah"          : 11,
        "thw al-qi`dah"      : 11, "dhu l-hijja"        : 12,
        "dhu hijja"          : 12, "thw al-hijjah"      : 12,
        }

    persian_to_int = {
        "farvardin"   : 1,  "ordibehesht" : 2,
        "khordad"     : 3,  "tir"         : 4,
        "mordad"      : 5,  "shahrivar"   : 6,
        "mehr"        : 7,  "aban"        : 8,
        "azar"        : 9,  "dey"         : 10,
        "bahman"      : 11, "esfand"      : 12,
        }

    swedish_to_int = {
        "januari"    :  1, "februari"   :  2,
        "mars"       :  3, "april"      :  4,
        "maj"        :  5, "juni"       :  6,
        "juli"       :  7, "augisti"    :  8,
        "september"  :  9, "oktober"    : 10,
        "november"   : 11, "december"   : 12,
        }
        

    bce = ["B.C.E.", "B.C.E", "BCE", "B.C.", "B.C", "BC" ]

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

    newyear_to_int = {
        "jan1":  Date.NEWYEAR_JAN1,
        "mar1":  Date.NEWYEAR_MAR1,
        "mar25": Date.NEWYEAR_MAR25, 
        "sep1" : Date.NEWYEAR_SEP1,
        }
    
    quality_to_int = {
        'estimated'  : Date.QUAL_ESTIMATED,
        'est.'       : Date.QUAL_ESTIMATED,
        'est'        : Date.QUAL_ESTIMATED,
        'calc.'      : Date.QUAL_CALCULATED,
        'calc'       : Date.QUAL_CALCULATED,
        'calculated' : Date.QUAL_CALCULATED,
        }
    
    def __init__(self):
        self.init_strings()
        self.parser = {
            Date.CAL_GREGORIAN : self._parse_gregorian,
            Date.CAL_JULIAN    : self._parse_julian,
            Date.CAL_FRENCH    : self._parse_french,
            Date.CAL_PERSIAN   : self._parse_persian,
            Date.CAL_HEBREW    : self._parse_hebrew,
            Date.CAL_ISLAMIC   : self._parse_islamic,
            Date.CAL_SWEDISH   : self._parse_swedish,
            }

        fmt = GrampsLocale.tformat
        match = self._fmt_parse.match(fmt.lower())
        if match:
            self.dmy = (match.groups() == ('d', 'm', 'y') or \
                       match.groups() == ('d', 'b', 'y'))
            self.ymd = (match.groups() == ('y', 'm', 'd') or \
                       match.groups() == ('y', 'b', 'd'))
        else:
            self.dmy = True
            self.ymd = False

    def re_longest_first(self, keys):
        """
        returns a string for a RE group which contains the given keys
        sorted so that longest keys match first.  Any '.' characters
        are quoted.
        """
        keys.sort(lambda x, y: cmp(len(y), len(x)))
        return '(' + '|'.join([key.replace('.', '\.') for key in keys]) + ')'

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
        self._rfc_mon_str  = '(' + '|'.join(self._rfc_mons_to_int.keys()) + ')'
        self._rfc_day_str  = '(' + '|'.join(self._rfc_days) + ')'

        self._bce_str = self.re_longest_first(self.bce)
        self._qual_str = self.re_longest_first(self.quality_to_int.keys())
        self._mod_str = self.re_longest_first(self.modifier_to_int.keys())
        self._mod_after_str = self.re_longest_first(
            self.modifier_after_to_int.keys())

        self._mon_str  = self.re_longest_first(self.month_to_int.keys())
        self._jmon_str = self.re_longest_first(self.hebrew_to_int.keys())
        self._fmon_str = self.re_longest_first(self.french_to_int.keys())
        self._pmon_str = self.re_longest_first(self.persian_to_int.keys())
        self._imon_str = self.re_longest_first(self.islamic_to_int.keys())
        self._smon_str = self.re_longest_first(self.swedish_to_int.keys())
        self._cal_str  = self.re_longest_first(self.calendar_to_int.keys())
        self._ny_str = self.re_longest_first(self.newyear_to_int.keys())

        # bce, calendar type and quality may be either at the end or at
        # the beginning of the given date string, therefore they will
        # be parsed from the middle and will be in match.group(2).
        self._bce_re   = re.compile("(.*)\s+%s( ?.*)" % self._bce_str)

        self._cal      = re.compile("(.*)\s+\(%s\)( ?.*)" % self._cal_str,
                                    re.IGNORECASE)
        self._calny    = re.compile("(.*)\s+\(%s,%s\)( ?.*)" % (self._cal_str,
                                                                self._ny_str),
                                   re.IGNORECASE)
        self._ny    = re.compile("(.*)\s+\(%s\)( ?.*)" % self._ny_str,
                                 re.IGNORECASE)
        self._qual     = re.compile("(.* ?)%s\s+(.+)" % self._qual_str,
                                    re.IGNORECASE)
        
        self._span     = re.compile("(from)\s+(?P<start>.+)\s+to\s+(?P<stop>.+)",
                                    re.IGNORECASE)
        self._range    = re.compile("(bet|bet.|between)\s+(?P<start>.+)\s+and\s+(?P<stop>.+)",
                                    re.IGNORECASE)
        self._modifier = re.compile('%s\s+(.*)' % self._mod_str,
                                    re.IGNORECASE)
        self._modifier_after = re.compile('(.*)\s+%s' % self._mod_after_str,
                                          re.IGNORECASE)
        self._abt2     = re.compile('<(.*)>', re.IGNORECASE)
        self._text     = re.compile('%s\.?\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$' % self._mon_str,
                                    re.IGNORECASE)
        self._text2    = re.compile('(\d+)?\s+?%s\.?\s*((\d+)(/\d+)?)?\s*$' % self._mon_str,
                                    re.IGNORECASE)
        self._jtext    = re.compile('%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$' % self._jmon_str,
                                    re.IGNORECASE)
        self._jtext2   = re.compile('(\d+)?\s+?%s\s*((\d+)(/\d+)?)?\s*$' % self._jmon_str,
                                    re.IGNORECASE)
        self._ftext    = re.compile('%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$' % self._fmon_str,
                                    re.IGNORECASE)
        self._ftext2   = re.compile('(\d+)?\s+?%s\s*((\d+)(/\d+)?)?\s*$' % self._fmon_str,
                                    re.IGNORECASE)
        self._ptext    = re.compile('%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$' % self._pmon_str,
                                    re.IGNORECASE)
        self._ptext2   = re.compile('(\d+)?\s+?%s\s*((\d+)(/\d+)?)?\s*$' % self._pmon_str,
                                    re.IGNORECASE)
        self._itext    = re.compile('%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$' % self._imon_str,
                                    re.IGNORECASE)
        self._itext2   = re.compile('(\d+)?\s+?%s\s*((\d+)(/\d+)?)?\s*$' % self._imon_str,
                                    re.IGNORECASE)
        self._stext     = re.compile('%s\.?\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$' % self._smon_str,
                                    re.IGNORECASE)
        self._stext2    = re.compile('(\d+)?\s+?%s\.?\s*((\d+)(/\d+)?)?\s*$' % self._smon_str,
                                    re.IGNORECASE)
        self._numeric  = re.compile("((\d+)[/\.]\s*)?((\d+)[/\.]\s*)?(\d+)\s*$")
        self._iso      = re.compile("(\d+)(/(\d+))?-(\d+)-(\d+)\s*$")
        self._rfc      = re.compile("(%s,)?\s+(\d|\d\d)\s+%s\s+(\d+)\s+\d\d:\d\d(:\d\d)?\s+(\+|-)\d\d\d\d" 
                                    % (self._rfc_day_str, self._rfc_mon_str))

    def _get_int(self, val):
        """
        Convert the string to an integer if the value is not None. If the
        value is None, a zero is returned
        """
        if val is None:
            return 0
        else:
            return int(val)

    def _parse_hebrew(self, text):
        return self._parse_calendar(text, self._jtext, self._jtext2,
                                    self.hebrew_to_int)

    def _parse_islamic(self, text):
        return self._parse_calendar(text, self._itext, self._itext2,
                                    self.islamic_to_int)

    def _parse_persian(self, text):
        return self._parse_calendar(text, self._ptext, self._ptext2,
                                    self.persian_to_int)

    def _parse_french(self, text):
        return self._parse_calendar(text, self._ftext, self._ftext2,
                                    self.french_to_int, french_valid)

    def _parse_gregorian(self, text):
        return self._parse_calendar(text, self._text, self._text2,
                                    self.month_to_int, gregorian_valid)

    def _parse_julian(self, text):
        return self._parse_calendar(text, self._text, self._text2,
                                    self.month_to_int, julian_valid)

    def _parse_swedish(self, text):
        return self._parse_calendar(text, self._stext, self._stext2,
                                    self.swedish_to_int,swedish_valid)

                             
    def _parse_calendar(self, text, regex1, regex2, mmap, check=None):
        match = regex1.match(text.lower())
        if match:
            groups = match.groups()
            if groups[0] is None:
                m = 0
            else:
                m = mmap[groups[0].lower()]

            if groups[2] is None:
                y = self._get_int(groups[1])
                d = 0
                s = False
            else:
                d = self._get_int(groups[1])
                if groups[4] is not None: # slash year "/80"
                    y = int(groups[3]) + 1 # fullyear + 1
                    s = True
                else: # regular, non-slash date
                    y = int(groups[3])
                    s = False
            value = (d, m, y, s)
            if check and not check((d, m, y)):
                value = Date.EMPTY
            return value

        match = regex2.match(text.lower())
        if match:
            groups = match.groups()
            if groups[1] is None:
                m = 0
            else:
                m = mmap[groups[1].lower()]

            d = self._get_int(groups[0])

            if groups[2] is None:
                y = None
                s = False
            else:
                if groups[4] is not None: # slash year digit
                    y = int(groups[3]) + 1 # fullyear + 1
                    s = True
                else:
                    y = int(groups[3])
                    s = False
            value = (d, m, y, s)
            if check and not check((d, m, y)):
                value = Date.EMPTY
            return value
        
        return Date.EMPTY
    
    def _parse_subdate(self, text, subparser=None):
        """
        Convert only the date portion of a date.
        """
        if subparser is None:
            subparser = self._parse_gregorian

        if subparser == self._parse_gregorian:
            check = gregorian_valid

        elif subparser == self._parse_julian:
            check = julian_valid

        elif subparser == self._parse_swedish:
            check = swedish_valid

        elif subparser == self._parse_french:
            check = french_valid
        else:
            check = None

        value = subparser(text)
        if value != Date.EMPTY:
            return value
        # if 8 digits are entered and month and day in range
        # assume yyyymmdd and convert to yyyy-mm-dd
        if len(text) == 8 and text.isdigit() \
            and (int(text[4:6]) in range(1,13)) \
            and (int(text[6:8]) in range(1,32)):
            text = text[0:4] + "-" + text[4:6] + "-" + text[6:8]
        match = self._iso.match(text)
        if match:
            groups = match.groups()
            y = self._get_int(groups[0])
            m = self._get_int(groups[3])
            d = self._get_int(groups[4])
            if check and not check((d, m, y)):
                return Date.EMPTY
            if groups[2]: # slash year digit
                return (d, m, y + 1, True)
            else:
                return (d, m, y, False)

        match = self._rfc.match(text)
        if match:
            groups = match.groups()
            d = self._get_int(groups[2])
            m = self._rfc_mons_to_int[groups[3]]
            y = self._get_int(groups[4])
            value = (d, m, y, False)
            if check and not check((d, m, y)):
                value = Date.EMPTY
            return value

        match = self._numeric.match(text)
        if match:
            groups = match.groups()
            if self.ymd:
                # '1789' and ymd: incomplete date
                if groups[1] is None:
                    y = self._get_int(groups[4])
                    m = 0
                    d = 0
                else:
                    y = self._get_int(groups[1])
                    m = self._get_int(groups[3])
                    d = self._get_int(groups[4])
            else:
                y = self._get_int(groups[4])
                if self.dmy:
                    m = self._get_int(groups[3])
                    d = self._get_int(groups[1])
                else:
                    m = self._get_int(groups[1])
                    d = self._get_int(groups[3])
            value = (d, m, y, False)
            if check and not check((d, m, y)):
                value = Date.EMPTY
            return value
        
        return Date.EMPTY

    def match_calendar(self, text, cal):
        """
        Try parsing calendar.
        
        Return calendar index and the text with calendar removed.
        """
        match = self._cal.match(text)
        if match:
            cal = self.calendar_to_int[match.group(2).lower()]
            text = match.group(1) + match.group(3)
        return (text, cal)

    def match_calendar_newyear(self, text, cal, newyear):
        """
        Try parsing calendar and newyear code.
        
        Return newyear index and the text with calendar removed.
        """
        match = self._calny.match(text)
        if match:
            cal = self.calendar_to_int[match.group(2).lower()]
            newyear = self.newyear_to_int[match.group(3).lower()]
            text = match.group(1) + match.group(4)
        return (text, cal, newyear)

    def match_newyear(self, text, newyear):
        """
        Try parsing calendar and newyear code.
        
        Return newyear index and the text with calendar removed.
        """
        match = self._ny.match(text)
        if match:
            newyear = self.newyear_to_int[match.group(2).lower()]
            text = match.group(1) + match.group(3)
        return (text, newyear)

    def match_quality(self, text, qual):
        """
        Try matching quality.
        
        Return quality index and the text with quality removed.
        """
        match = self._qual.match(text)
        if match:
            qual = self.quality_to_int[match.group(2).lower()]
            text = match.group(1) + match.group(3)
        return (text, qual)

    def match_span(self, text, cal, ny, qual, date):
        """
        Try matching span date.
        
        On success, set the date and return 1. On failure return 0.
        """
        match = self._span.match(text)
        if match:
            text_parser = self.parser[cal]
            (text1, bc1) = self.match_bce(match.group('start'))
            start = self._parse_subdate(text1, text_parser)
            if bc1:
                start = self.invert_year(start)

            (text2, bc2) = self.match_bce(match.group('stop'))
            stop = self._parse_subdate(text2, text_parser)
            if bc2:
                stop = self.invert_year(stop)

            date.set(qual, Date.MOD_SPAN, cal, start + stop, newyear=ny)
            return 1
        return 0

    def match_range(self, text, cal, ny, qual, date):
        """
        Try matching range date.
        
        On success, set the date and return 1. On failure return 0.
        """
        match = self._range.match(text)
        if match:
            text_parser = self.parser[cal]
            (text1, bc1) = self.match_bce(match.group('start'))
            start = self._parse_subdate(text1, text_parser)
            if bc1:
                start = self.invert_year(start)

            (text2, bc2) = self.match_bce(match.group('stop'))
            stop = self._parse_subdate(text2, text_parser)
            if bc2:
                stop = self.invert_year(stop)
            
            date.set(qual, Date.MOD_RANGE, cal, start + stop, newyear=ny)
            return 1
        return 0

    def match_bce(self, text):
        """
        Try matching BCE qualifier.
        
        Return BCE (True/False) and the text with matched part removed.
        """
        match = self._bce_re.match(text)
        bc = False
        if match:
        # bce is in the match.group(2)
            try:
                text = match.group(1) + match.group(3)
            except:
                print "ERROR MATCH:", match.groups()
            bc = True
        return (text, bc)

    def match_modifier(self, text, cal, ny, qual, bc, date):
        """
        Try matching date with modifier.
        
        On success, set the date and return 1. On failure return 0.
        """
        # modifiers before the date
        match = self._modifier.match(text)
        if match:
            grps = match.groups()
            start = self._parse_subdate(grps[1], self.parser[cal])
            mod = self.modifier_to_int.get(grps[0].lower(), Date.MOD_NONE)
            if start == Date.EMPTY:
                date.set_modifier(Date.MOD_TEXTONLY)
                date.set_text_value(text)
            elif bc:
                date.set(qual, mod, cal, self.invert_year(start), newyear=ny)
            else:
                date.set(qual, mod, cal, start, newyear=ny)
            return True
        # modifiers after the date
        if self.modifier_after_to_int:
            match = self._modifier_after.match(text)
            if match:
                grps = match.groups()
                start = self._parse_subdate(grps[0], self.parser[cal])
                mod = self.modifier_after_to_int.get(grps[1].lower(),
                                                     Date.MOD_NONE)
                if bc:
                    date.set(qual, mod, cal, self.invert_year(start), newyear=ny)
                else:
                    date.set(qual, mod, cal, start, newyear=ny)
                return True
        match = self._abt2.match(text)
        if match:
            grps = match.groups()
            start = self._parse_subdate(grps[0])
            mod = Date.MOD_ABOUT
            if bc:
                date.set(qual, mod, cal, self.invert_year(start), newyear=ny)
            else:
                date.set(qual, mod, cal, start, newyear=ny)
            return True
        return False

    def set_date(self, date, text):
        """
        Parses the text and sets the date according to the parsing.
        """
        text = text.strip() # otherwise spaces can make it a bad date
        date.set_text_value(text)
        qual = Date.QUAL_NONE
        cal  = Date.CAL_GREGORIAN
        newyear = Date.NEWYEAR_JAN1
        
        (text, cal, newyear) = self.match_calendar_newyear(text, cal, newyear)
        (text, newyear) = self.match_newyear(text, newyear)
        (text, cal) = self.match_calendar(text, cal)
        (text, qual) = self.match_quality(text, qual)

        if self.match_span(text, cal, newyear, qual, date):
            return
        if self.match_range(text, cal, newyear, qual, date):
            return

        (text, bc) = self.match_bce(text)
        if self.match_modifier(text, cal, newyear, qual, bc, date):
            return

        try:
            subdate = self._parse_subdate(text, self.parser[cal])
            if subdate == Date.EMPTY and text != "":
                date.set_as_text(text)
                return
        except:
            date.set_as_text(text)
            return

        if bc:
            date.set(qual, Date.MOD_NONE, cal, self.invert_year(subdate), newyear=newyear)
        else:
            date.set(qual, Date.MOD_NONE, cal, subdate, newyear=newyear)

    def invert_year(self, subdate):
        return (subdate[0], subdate[1], -subdate[2], subdate[3])
    
    def parse(self, text):
        """
        Parses the text, returning a Date object.
        """
        new_date = Date()
        try:
            self.set_date(new_date, text)
        except DateError:
            new_date.set_as_text(text)
        return new_date
