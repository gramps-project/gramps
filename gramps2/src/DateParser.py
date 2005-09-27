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
Date parsing class. Serves as the base class for any localized
date parsing class. The default, base class provides parsing for
English.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import re
import locale
import calendar

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Date
from Errors import DateError
#-------------------------------------------------------------------------
#
# Top-level module functions
#
#-------------------------------------------------------------------------
_max_days  = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
_leap_days = [ 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]

def gregorian_valid(date_tuple):
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

#-------------------------------------------------------------------------
#
# Parser class
#
#-------------------------------------------------------------------------
class DateParser:
    """
    Converts a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    # determine the code set returned by nl_langinfo
    _codeset = locale.nl_langinfo(locale.CODESET)
    _fmt_parse = re.compile(".*%(\S).*%(\S).*%(\S).*")

    # RFC-2822 only uses capitalized English abbreviated names, no locales.
    _rfc_days = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat')
    _rfc_mons_to_int = {
        'Jan' : 1,  'Feb' : 2,  'Mar' : 3,  'Apr' : 4,
        'May' : 5,  'Jun' : 6,  'Jul' : 7,  'Aug' : 8,
        'Sep' : 9,  'Oct' : 10, 'Nov' : 11, 'Dec' : 12,
        }

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
        u'vend\xc3\xa9miaire'  : 1,    'brumaire'   : 2,
        'frimaire'             : 3,    u'niv\xc3\xb4se  ': 4,
        u'pluvi\xc3\xb4se'     : 5,    u'vent\xc3\xb4se' : 6,
        'germinal'             : 7,    u'flor\xc3\xa9al' : 8,
        'prairial'             : 9,    'messidor'   : 10,
        'thermidor'            : 11,   'fructidor'  : 12,
        'extra'                : 13
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
        "Farvardin"   : 1,  "Ordibehesht" : 2,
        "Khordad"     : 3,  "Tir"         : 4,
        "Mordad"      : 5,  "Shahrivar"   : 6,
        "Mehr"        : 7,  "Aban"        : 8,
        "Azar"        : 9,  "Dey"         : 10,
        "Bahman"      : 11, "Esfand"      : 12,
        }

    bce = ["BC", "B\.C", "B\.C\.", "BCE", "B\.C\.E", "B\.C\.E"]

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
            Date.CAL_GREGORIAN : self._parse_greg_julian,
            Date.CAL_JULIAN    : self._parse_greg_julian,
            Date.CAL_FRENCH    : self._parse_french,
            Date.CAL_PERSIAN   : self._parse_persian,
            Date.CAL_HEBREW    : self._parse_hebrew,
            Date.CAL_ISLAMIC   : self._parse_islamic,
            }

        fmt = locale.nl_langinfo(locale.D_FMT)
        match = self._fmt_parse.match(fmt.lower())
        if match:
            self.dmy = (match.groups() == ('d','m','y'))
        else:
            self.dmy = True
        
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

        self._bce_str = '(' + '|'.join(self.bce) + ')'
    
        self._qual_str = '(' + '|'.join(
            [ key.replace('.','\.') for key in self.quality_to_int.keys() ]
            ) + ')'
        self._mod_str  = '(' + '|'.join(
            [ key.replace('.','\.') for key in self.modifier_to_int.keys() ]
            ) + ')'
        self._mod_after_str  = '(' + '|'.join(
            [ key.replace('.','\.') for key in self.modifier_after_to_int.keys() ]
            ) + ')'

        # Need to reverse-sort the keys, so that April matches before Apr does.
        # Otherwise, 'april 2000' would be matched as 'apr' + garbage ('il 2000')
        _month_keys = self.month_to_int.keys()
        _month_keys.sort()
        _month_keys.reverse()
        self._mon_str  = '(' + '|'.join(_month_keys) + ')'
        self._jmon_str = '(' + '|'.join(self.hebrew_to_int.keys()) + ')'
        self._fmon_str = '(' + '|'.join(self.french_to_int.keys()) + ')'
        self._pmon_str = '(' + '|'.join(self.persian_to_int.keys()) + ')'
        self._cal_str  = '(' + '|'.join(self.calendar_to_int.keys()) + ')'
        self._imon_str = '(' + '|'.join(self.islamic_to_int.keys()) + ')'

        self._bce_re   = re.compile("(.+)\s+%s" % self._bce_str)
    
        self._cal      = re.compile("(.+)\s\(%s\)" % self._cal_str,
                           re.IGNORECASE)
        self._qual     = re.compile("%s\s+(.+)" % self._qual_str,
                           re.IGNORECASE)
        self._span     = re.compile("(from)\s+(?P<start>.+)\s+to\s+(?P<stop>.+)",
                           re.IGNORECASE)
        self._range    = re.compile("(bet|bet.|between)\s+(?P<start>.+)\s+and\s+(?P<stop>.+)",
                           re.IGNORECASE)
        self._modifier = re.compile('%s\s+(.*)' % self._mod_str,
                           re.IGNORECASE)
        self._modifier_after = re.compile('(.*)\s+%s' % self._mod_after_str,
                           re.IGNORECASE)
        self._abt2     = re.compile('<(.*)>',re.IGNORECASE)
        self._text     = re.compile('%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?' % self._mon_str,
                           re.IGNORECASE)
        self._text2    = re.compile('(\d+)?\s+?%s\s*((\d+)(/\d+)?)?' % self._mon_str,
                           re.IGNORECASE)
        self._jtext    = re.compile('%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?' % self._jmon_str,
                           re.IGNORECASE)
        self._jtext2   = re.compile('(\d+)?\s+?%s\s*((\d+)(/\d+)?)?' % self._jmon_str,
                           re.IGNORECASE)
        self._ftext    = re.compile('%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?' % self._fmon_str,
                           re.IGNORECASE)
        self._ftext2   = re.compile('(\d+)?\s+?%s\s*((\d+)(/\d+)?)?' % self._fmon_str,
                           re.IGNORECASE)
        self._ptext    = re.compile('%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?' % self._pmon_str,
                           re.IGNORECASE)
        self._ptext2   = re.compile('(\d+)?\s+?%s\s*((\d+)(/\d+)?)?' % self._pmon_str,
                           re.IGNORECASE)
        self._itext    = re.compile('%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?' % self._imon_str,
                           re.IGNORECASE)
        self._itext2   = re.compile('(\d+)?\s+?%s\s*((\d+)(/\d+)?)?' % self._imon_str,
                           re.IGNORECASE)
        self._numeric  = re.compile("((\d+)[/\.])?((\d+)[/\.])?(\d+)")
        self._iso      = re.compile("(\d+)-(\d+)-(\d+)")
        self._rfc      = re.compile("(%s,)?\s+(\d|\d\d)\s+%s\s+(\d+)\s+\d\d:\d\d(:\d\d)?\s+(\+|-)\d\d\d\d" 
                        % (self._rfc_day_str,self._rfc_mon_str))

    def _get_int(self,val):
        """
        Converts the string to an integer if the value is not None. If the
        value is None, a zero is returned
        """
        if val == None:
            return 0
        else:
            return int(val)

    def _parse_hebrew(self,text):
        return self._parse_calendar(text,self._jtext,self._jtext2,
                                    self.hebrew_to_int)

    def _parse_islamic(self,text):
        return self._parse_calendar(text,self._itext,self._itext2,
                                    self.islamic_to_int)

    def _parse_persian(self,text):
        return self._parse_calendar(text,self._ptext,self._ptext2,
                                    self.persian_to_int)

    def _parse_french(self,text):
        return self._parse_calendar(text,self._ftext,self._ftext2,
                                    self.french_to_int)

    def _parse_greg_julian(self,text):
        return self._parse_calendar(text,self._text,self._text2,
                                    self.month_to_int,gregorian_valid)
                             
    def _parse_calendar(self,text,regex1,regex2,mmap,check=None):
        match = regex1.match(text.lower())
        if match:
            groups = match.groups()
            if groups[0] == None:
                m = 0
            else:
                m = mmap[groups[0].lower()]

            if groups[2] == None:
                y = self._get_int(groups[1])
                d = 0
                s = None
            else:
                d = self._get_int(groups[1])
                y = int(groups[3])
                s = groups[4] != None
            value = (d,m,y,s)
            if check and not check((d,m,y)):
                value = Date.EMPTY
            return value

        match = regex2.match(text.lower())
        if match:
            groups = match.groups()
            if groups[1] == None:
                m = 0
            else:
                m = mmap[groups[1].lower()]

            d = self._get_int(groups[0])

            if groups[2] == None:
                y = 0
                s = None
            else:
                y = int(groups[3])
                s = groups[4] != None
            value = (d,m,y,s)
            if check and not check((d,m,y)):
                value = Date.EMPTY
            return value
        
        return Date.EMPTY
    
    def _parse_subdate(self,text,subparser=None):
        """
        Converts only the date portion of a date.
        """
        if subparser == None:
            subparser = self._parse_greg_julian
            check = gregorian_valid
        else:
            check = None
            
        value = subparser(text)
        if value != Date.EMPTY:
            return value
        
        match = self._iso.match(text)
        if match:
            groups = match.groups()
            y = self._get_int(groups[0])
            m = self._get_int(groups[1])
            d = self._get_int(groups[2])
            if gregorian_valid((d,m,y)):
                return (d,m,y,False)
            else:
                return Date.EMPTY

        match = self._rfc.match(text)
        if match:
            groups = match.groups()
            d = self._get_int(groups[2])
            m = self._rfc_mons_to_int[groups[3]]
            y = self._get_int(groups[4])
            if gregorian_valid((d,m,y)):
                return (d,m,y,False)
            else:
                return Date.EMPTY

        match = self._numeric.match(text)
        if match:
            groups = match.groups()
            if self.dmy:
                m = self._get_int(groups[3])
                d = self._get_int(groups[1])
            else:
                m = self._get_int(groups[1])
                d = self._get_int(groups[3])
            y = self._get_int(groups[4])
            value = (d,m,y,False)
            if check and not check((d,m,y)):
                value = Date.EMPTY
            return value
        
        return Date.EMPTY

    def match_calendar(self,text,cal):
        """
        Try parsing calendar.
        
        Return calendar index and the remainder of text.
        """
        match = self._cal.match(text)
        if match:
            grps = match.groups()
            cal = self.calendar_to_int[grps[1].lower()]
            text = grps[0]
        return (text,cal)

    def match_quality(self,text,qual):
        """
        Try matching quality.
        
        Return quality index and the remainder of text.
        """
        match = self._qual.match(text)
        if match:
            grps = match.groups()
            qual = self.quality_to_int[grps[0].lower()]
            text = grps[1]
        return (text,qual)

    def match_span(self,text,cal,qual,date):
        """
        Try matching span date.
        
        On success, set the date and return 1. On failure return 0.
        """
        match = self._span.match(text)
        if match:
            text_parser = self.parser[cal]
            start = self._parse_subdate(match.group('start'),text_parser)
            stop = self._parse_subdate(match.group('stop'),text_parser)
            date.set(qual,Date.MOD_SPAN,cal,start + stop)
            return 1
        return 0

    def match_range(self,text,cal,qual,date):
        """
        Try matching range date.
        
        On success, set the date and return 1. On failure return 0.
        """
        match = self._range.match(text)
        if match:
            text_parser = self.parser[cal]
            start = self._parse_subdate(match.group('start'),text_parser)
            stop = self._parse_subdate(match.group('stop'),text_parser)
            date.set(qual,Date.MOD_RANGE,cal,start + stop)
            return 1
        return 0

    def match_bce(self,text):
        """
        Try matching BCE qualifier.
        
        Return BCE (True/False) and the remainder of text.
        """
        match = self._bce_re.match(text)
        bc = False
        if match:
            text = match.groups()[0]
            bc = True
        return (text,bc)

    def match_modifier(self,text,cal,qual,bc,date):
        """
        Try matching date with modifier.
        
        On success, set the date and return 1. On failure return 0.
        """
        # modifiers before the date
        match = self._modifier.match(text)
        if match:
            grps = match.groups()
            start = self._parse_subdate(grps[1])
            mod = self.modifier_to_int.get(grps[0].lower(),Date.MOD_NONE)
            if bc:
                date.set(qual,mod,cal,self.invert_year(start))
            else:
                date.set(qual,mod,cal,start)
            return True
        # modifiers after the date
        if self.modifier_after_to_int:
            match = self._modifier_after.match(text)
            if match:
                grps = match.groups()
                start = self._parse_subdate(grps[0])
                mod = self.modifier_after_to_int.get(grps[1].lower(),Date.MOD_NONE)
                if bc:
                    date.set(qual,mod,cal,self.invert_year(start))
                else:
                    date.set(qual,mod,cal,start)
                return True
        match = self._abt2.match(text)
        if match:
            grps = match.groups()
            start = self._parse_subdate(grps[0])
            mod = Date.MOD_ABOUT
            if bc:
                date.set(qual,mod,cal,self.invert_year(start))
            else:
                date.set(qual,mod,cal,start)
            return True
        return False

    def set_date(self,date,text):
        """
        Parses the text and sets the date according to the parsing.
        """

        
        date.set_text_value(text)
        qual = Date.QUAL_NONE
        cal  = Date.CAL_GREGORIAN
        
        (text,cal) = self.match_calendar(text,cal)
        (text,qual) = self.match_quality(text,qual)
        if self.match_span(text,cal,qual,date):
            return
        if self.match_range(text,cal,qual,date):
            return

        (text,bc) = self.match_bce(text)
        if self.match_modifier(text,cal,qual,bc,date):
            return


        try:
            subdate = self._parse_subdate(text,self.parser[cal])
        except:
            date.set_as_text(text)
            return

        if bc:
            date.set(qual,Date.MOD_NONE,cal,self.invert_year(subdate))
        else:
            date.set(qual,Date.MOD_NONE,cal,subdate)

    def invert_year(self,subdate):
        return (subdate[0],subdate[1],-subdate[2],subdate[3])
    
    def parse(self,text):
        """
        Parses the text, returning a Date object.
        """
        new_date = Date.Date()
        try:
            self.set_date(new_date,text)
        except DateError:
            new_date.set_as_text(text)
        return new_date
