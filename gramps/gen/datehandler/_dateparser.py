# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2017       Paul Franklin
# Copyright (c) 2020       Steve Youngs
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Date parsing class. Serves as the base class for any localized
date parsing class. The default base class provides parsing for English.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import re
import calendar

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".DateParser")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..lib.date import Date, DateError, Today
from ..const import GRAMPS_LOCALE as glocale
from ..utils.grampslocale import GrampsLocale
from ._datestrings import DateStrings

# -------------------------------------------------------------------------
#
# Top-level module functions
#
# -------------------------------------------------------------------------
_max_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
_leap_days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def gregorian_valid(date_tuple):
    """Checks if date_tuple is a valid date in Gregorian Calendar"""
    day = date_tuple[0]
    month = date_tuple[1]
    valid = True
    try:
        if month > 12:
            valid = False
        elif calendar.isleap(date_tuple[2]):
            if day > _leap_days[month - 1]:
                valid = False
        elif day > _max_days[month - 1]:
            valid = False
    except:
        valid = False
    return valid


def julian_valid(date_tuple):
    """Checks if date_tuple is a valid date in Julian Calendar"""
    day = date_tuple[0]
    month = date_tuple[1]
    valid = True
    try:
        if month > 12:
            valid = False
        elif (date_tuple[2]) % 4 == 0:
            # julian always have leapyear every 4 year
            if day > _leap_days[month - 1]:
                valid = False
        elif day > _max_days[month - 1]:
            valid = False
    except:
        valid = False
    return valid


def swedish_valid(date_tuple):
    """Checks if date_tuple is a valid date in Swedish Calendar"""
    valid_J = julian_valid(date_tuple)
    date_tuple = (date_tuple[2], date_tuple[1], date_tuple[0])
    # Swedish calendar starts as Julian 1700-03-01 and ends 1712-03-01 as Julian
    if date_tuple >= (1700, 2, 29) and date_tuple < (1712, 3, 1):
        if date_tuple == (1712, 2, 30):  # extra day was inserted 1712, not valid Julian
            return True
        if valid_J:
            if date_tuple == (1700, 2, 29):  # leapday 1700 was skipped
                return False
            return True
        else:
            return False
    else:
        return False


def french_valid(date_tuple):
    """Checks if date_tuple is a valid date in French Calendar"""
    valid = True
    # year 1 starts on 22.9.1792
    if date_tuple[2] < 1:
        valid = False
    return valid


def _build_prefix_table(month_to_int, month_variants):
    """
    Populate a DateParser.month_to_int-like dict
    with all the prefixes found in month_variants.
    """

    month_variants = list(month_variants)  # drain the generator, if any
    month_to_int_new = {}

    # Populate with full names first, w/o prefixes
    log.debug("Mapping full names...")
    for i in range(0, len(month_variants)):
        for month in month_variants[i]:
            m = month.lower()
            log.debug("Mapping {} -> {}".format(m, i))
            month_to_int_new[m] = i
    month_to_int.update(month_to_int_new)

    log.debug("Mapping new prefixes...")
    months_sorted = list(month_to_int_new.keys())
    months_sorted.sort(key=len, reverse=True)
    for m in months_sorted:
        for prefixlen in reversed(range(1, len(m))):
            mp = m[:prefixlen]
            if mp.strip() != mp:
                continue
            if mp in month_to_int:
                break
            else:
                i = month_to_int[m]
                log.debug("Mapping {} -> {}".format(mp, i))
                month_to_int[mp] = i


def _generate_variants(months):
    """
    Generate all month variants for passing to _build_prefix_table
    :param months: an iterable ordered collection, 1st item is empty, the rest
                   1..N, for a calendar with N months overall, contain, each,
                   an iterable of alternative specifications.
                   Each such specification can be:
                     1) a Lexeme, supporting .variants() to return the list of
                        variants underneath
                     2) a literal string
                     3) a |-separated string of alternatives
                   Empty strings are discarded.
    :return: generator of lists per month with all variants listed once only
             the 1st item will be empty
    """

    for month_lexemes_and_alternatives in months:
        v = []
        for m in month_lexemes_and_alternatives:
            try:
                # Lexeme? ask it to compute the variants it knows
                mv = list(m.variants())
            except AttributeError:
                # plain string, not a lexeme with inflections...
                # Maybe a '|'-separated list of alternatives, maybe empty,
                # maybe a single string. Suppress empty strings!
                mv = (s for s in m.split("|") if s)
            v.extend(mv)
        yield (list(set(v)))


# -------------------------------------------------------------------------
#
# DateParser class
#
# -------------------------------------------------------------------------
class DateParser:
    """
    Convert a text string into a :class:`.Date` object. If the date cannot be
    converted, the text string is assigned.
    """

    _dhformat_parse = re.compile(r".*%(\S).*%(\S).*%(\S).*")

    # RFC-2822 only uses capitalized English abbreviated names, no locales.
    _rfc_days = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
    _rfc_mons_to_int = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    # seeded with __init_prefix_tables
    swedish_to_int = month_to_int = {}
    """
    Map Gregorian month names and their prefixes, wherever unambiguous,
    to the relevant integer index (1..12).
    """

    # modifiers before the date
    # (overridden if a locale-specific date parser exists)
    modifier_to_int = {
        "before": Date.MOD_BEFORE,
        "bef": Date.MOD_BEFORE,
        "bef.": Date.MOD_BEFORE,
        "after": Date.MOD_AFTER,
        "aft": Date.MOD_AFTER,
        "aft.": Date.MOD_AFTER,
        "about": Date.MOD_ABOUT,
        "abt.": Date.MOD_ABOUT,
        "abt": Date.MOD_ABOUT,
        "circa": Date.MOD_ABOUT,
        "c.": Date.MOD_ABOUT,
        "around": Date.MOD_ABOUT,
        "from": Date.MOD_FROM,
        "to": Date.MOD_TO,
    }
    # in some languages some of above listed modifiers are after the date,
    # in that case the subclass should put them into this dictionary instead
    modifier_after_to_int = {}

    hebrew_to_int = {
        "tishri": 1,
        "heshvan": 2,
        "kislev": 3,
        "tevet": 4,
        "shevat": 5,
        "adari": 6,
        "adarii": 7,
        "nisan": 8,
        "iyyar": 9,
        "sivan": 10,
        "tammuz": 11,
        "av": 12,
        "elul": 13,
        # alternative spelling
        "cheshvan": 2,
        "adar sheni": 7,
        "iyar": 9,
        # GEDCOM months
        "tsh": 1,
        "csh": 5,
        "ksl": 3,
        "tvt": 4,
        "shv": 5,
        "adr": 6,
        "ads": 7,
        "nsn": 8,
        "iyr": 9,
        "svn": 10,
        "tmz": 11,
        "aav": 12,
        "ell": 13,
    }

    french_to_int = {
        # the long ones are seeded with __init_prefix_tables
        # GEDCOM months
        "vend": 1,
        "brum": 2,
        "frim": 3,
        "nivo": 4,
        "pluv": 5,
        "vent": 6,
        "germ": 7,
        "flor": 8,
        "prai": 9,
        "mess": 10,
        "ther": 11,
        "fruc": 12,
        "comp": 13,
    }

    islamic_to_int = {
        # some are already seeded with __init_prefix_tables,
        # but it is a pain to separate them out from the variants...
        "muharram": 1,
        "muharram ul haram": 1,
        "safar": 2,
        "rabi`al-awwal": 3,
        "rabi'l": 3,
        "rabi`ul-akhir": 4,
        "rabi`ath-thani": 4,
        "rabi` ath-thani": 4,
        "rabi`al-thaany": 4,
        "rabi` al-thaany": 4,
        "rabi' ii": 4,
        "jumada l-ula": 5,
        "jumaada-ul-awwal": 5,
        "jumaada i": 5,
        "jumada t-tania": 6,
        "jumaada-ul-akhir": 6,
        "jumaada al-thaany": 6,
        "jumaada ii": 5,
        "rajab": 7,
        "sha`ban": 8,
        "sha`aban": 8,
        "ramadan": 9,
        "ramadhan": 9,
        "shawwal": 10,
        "dhu l-qa`da": 11,
        "dhu qadah": 11,
        "thw al-qi`dah": 11,
        "dhu l-hijja": 12,
        "dhu hijja": 12,
        "thw al-hijjah": 12,
    }

    # seeded with __init_prefix_tables
    persian_to_int = {}

    bce = ["B.C.E.", "B.C.E", "BCE", "B.C.", "B.C", "BC"]
    # (overridden if a locale-specific date parser exists)

    # seeded with __init_prefix_tables
    calendar_to_int = {}
    # (probably overridden if a locale-specific date parser exists)

    newyear_to_int = {
        "jan1": Date.NEWYEAR_JAN1,
        "mar1": Date.NEWYEAR_MAR1,
        "mar25": Date.NEWYEAR_MAR25,
        "sep1": Date.NEWYEAR_SEP1,
    }

    quality_to_int = {
        "estimated": Date.QUAL_ESTIMATED,
        "est.": Date.QUAL_ESTIMATED,
        "est": Date.QUAL_ESTIMATED,
        "calc.": Date.QUAL_CALCULATED,
        "calc": Date.QUAL_CALCULATED,
        "calculated": Date.QUAL_CALCULATED,
    }
    # (overridden if a locale-specific date parser exists)

    today = [
        "$T",
    ]
    # Override with a list of *synonyms* for "today" in your language.
    # Note: the word "today" itself will already be pulled in from your translation DB,
    # see init_strings, so there is no need to override this if you have no aliases
    # for "today".
    # We also secretly support "$T" like in some reports.

    _langs = set()

    def __init_prefix_tables(self):
        ds = self._ds = DateStrings(self._locale)
        lang = self._locale.lang
        if lang in DateParser._langs:
            log.debug("Prefix tables for {} already built".format(lang))
            return
        else:
            DateParser._langs.add(lang)
        log.debug("Begin building parser prefix tables for {}".format(lang))
        _build_prefix_table(
            DateParser.month_to_int,
            _generate_variants(
                zip(ds.long_months, ds.short_months, ds.swedish_SV, ds.alt_long_months)
            ),
        )
        _build_prefix_table(
            DateParser.hebrew_to_int, _generate_variants(zip(ds.hebrew))
        )
        _build_prefix_table(
            DateParser.french_to_int, _generate_variants(zip(ds.french))
        )
        _build_prefix_table(
            DateParser.islamic_to_int, _generate_variants(zip(ds.islamic))
        )
        _build_prefix_table(
            DateParser.persian_to_int, _generate_variants(zip(ds.persian))
        )
        _build_prefix_table(
            DateParser.calendar_to_int, _generate_variants(zip(ds.calendar))
        )

    def __init__(self, plocale=None):
        """
        :param plocale: allow correct date format to be loaded and parsed
        :type plocale: a :class:`.GrampsLocale` instance
        """
        from ._datehandler import locale_tformat  # circular import if above

        if plocale:
            self._locale = plocale
        elif not hasattr(self, "_locale"):
            self._locale = glocale
        if self._locale.calendar in locale_tformat:
            self.dhformat = locale_tformat[self._locale.calendar]  # date format
        else:
            self.dhformat = locale_tformat["en_GB"]  # something is required
        self.dhformat_changed()  # Allow overriding so a subclass can modify it
        self.init_strings()
        self.parser = {
            Date.CAL_GREGORIAN: self._parse_gregorian,
            Date.CAL_JULIAN: self._parse_julian,
            Date.CAL_FRENCH: self._parse_french,
            Date.CAL_PERSIAN: self._parse_persian,
            Date.CAL_HEBREW: self._parse_hebrew,
            Date.CAL_ISLAMIC: self._parse_islamic,
            Date.CAL_SWEDISH: self._parse_swedish,
        }

        match = self._dhformat_parse.match(self.dhformat.lower())
        if match:
            self._ddmy = match.groups() == ("a", "e", "b", "y")  # Icelandic
            self.dmy = (
                match.groups() == ("d", "m", "y")
                or match.groups() == ("e", "m", "y")
                or match.groups() == ("d", "b", "y")  # Bulgarian
                or match.groups() == ("a", "e", "b", "y")
            )
            self.ymd = match.groups() == ("y", "m", "d") or match.groups() == (
                "y",
                "b",
                "d",
            )
            # note ('m','d','y') is valid -- in which case both will be False
        else:
            self.dmy = True
            self.ymd = False
            self._ddmy = False

    def dhformat_changed(self):
        """Allow overriding so a subclass can modify it"""
        pass

    def re_longest_first(self, keys):
        """
        returns a string for a RE group which contains the given keys
        sorted so that longest keys match first.  Any '.' characters
        are quoted.
        """
        keys.sort(key=len, reverse=True)
        return "(" + "|".join([re.escape(key) for key in keys]) + ")"

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.

        Most of the re's in most languages can stay as is. span and range
        most likely will need to change. Whatever change is done, this method
        may be called first as DateParser.init_strings(self) so that the
        invariant expresions don't need to be repeatedly coded. All differences
        can be coded after DateParser.init_strings(self) call, that way they
        override stuff from this method.

        .. seealso:: :class:`.DateParserRU` as an example.
        """
        _ = self._locale.translation.gettext
        self.__init_prefix_tables()

        self._rfc_mon_str = "(" + "|".join(list(self._rfc_mons_to_int.keys())) + ")"
        self._rfc_day_str = "(" + "|".join(self._rfc_days) + ")"

        self._bce_str = self.re_longest_first(self.bce)
        self._qual_str = self.re_longest_first(list(self.quality_to_int.keys()))
        self._mod_str = self.re_longest_first(list(self.modifier_to_int.keys()))
        self._mod_after_str = self.re_longest_first(
            list(self.modifier_after_to_int.keys())
        )

        self._mon_str = self.re_longest_first(list(self.month_to_int.keys()))
        self._jmon_str = self.re_longest_first(list(self.hebrew_to_int.keys()))
        self._fmon_str = self.re_longest_first(list(self.french_to_int.keys()))
        self._pmon_str = self.re_longest_first(list(self.persian_to_int.keys()))
        self._imon_str = self.re_longest_first(list(self.islamic_to_int.keys()))
        self._smon_str = self.re_longest_first(list(self.swedish_to_int.keys()))
        self._cal_str = self.re_longest_first(list(self.calendar_to_int.keys()))
        self._ny_str = self.re_longest_first(list(self.newyear_to_int.keys()))

        self._today_str = self.re_longest_first(
            self.today
            + [
                _("today"),
            ]
        )

        # bce, calendar type and quality may be either at the end or at
        # the beginning of the given date string, therefore they will
        # be parsed from the middle and will be in match.group(2).
        self._bce_re = re.compile(r"(.*)\s+%s( ?.*)" % self._bce_str)

        self._cal = re.compile(r"(.*)\s+\(%s\)( ?.*)" % self._cal_str, re.IGNORECASE)
        self._calny = re.compile(
            r"(.*)\s+\(%s,\s*%s\)( ?.*)" % (self._cal_str, self._ny_str), re.IGNORECASE
        )
        self._calny_iso = re.compile(
            r"(.*)\s+\(%s,\s*(\d{1,2}-\d{1,2})\)( ?.*)" % self._cal_str, re.IGNORECASE
        )

        self._ny = re.compile(r"(.*)\s+\(%s\)( ?.*)" % self._ny_str, re.IGNORECASE)
        self._ny_iso = re.compile(r"(.*)\s+\((\d{1,2}-\d{1,2})\)( ?.*)")

        self._qual = re.compile(r"(.* ?)%s\s+(.+)" % self._qual_str, re.IGNORECASE)

        self._span = re.compile(
            r"(from)\s+(?P<start>.+)\s+to\s+(?P<stop>.+)", re.IGNORECASE
        )
        self._range = re.compile(
            r"(bet|bet.|between)\s+(?P<start>.+)\s+and\s+(?P<stop>.+)", re.IGNORECASE
        )
        self._quarter = re.compile(
            r"[qQ](?P<quarter>[1-4])\s+(?P<year>.+)", re.IGNORECASE
        )
        self._modifier = re.compile(r"%s\s+(.*)" % self._mod_str, re.IGNORECASE)
        self._modifier_after = re.compile(
            r"(.*)\s+%s" % self._mod_after_str, re.IGNORECASE
        )
        self._abt2 = re.compile("<(.*)>", re.IGNORECASE)
        self._text = re.compile(
            r"%s\.?(\s+\d+)?\s*,?\s+((\d+)(/\d+)?)?\s*$" % self._mon_str, re.IGNORECASE
        )
        # this next RE has the (possibly-slashed) year at the string's end
        self._text2 = re.compile(
            r"(\d+)?\s+?%s\.?\s*((\d+)(/\d+)?)?\s*$" % self._mon_str, re.IGNORECASE
        )
        self._jtext = re.compile(
            r"%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$" % self._jmon_str, re.IGNORECASE
        )
        self._jtext2 = re.compile(
            r"(\d+)?\s+?%s\s*((\d+)(/\d+)?)?\s*$" % self._jmon_str, re.IGNORECASE
        )
        self._ftext = re.compile(
            r"%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$" % self._fmon_str, re.IGNORECASE
        )
        self._ftext2 = re.compile(
            r"(\d+)?\s+?%s\s*((\d+)(/\d+)?)?\s*$" % self._fmon_str, re.IGNORECASE
        )
        self._ptext = re.compile(
            r"%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$" % self._pmon_str, re.IGNORECASE
        )
        self._ptext2 = re.compile(
            r"(\d+)?\s+?%s\s*((\d+)(/\d+)?)?\s*$" % self._pmon_str, re.IGNORECASE
        )
        self._itext = re.compile(
            r"%s\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$" % self._imon_str, re.IGNORECASE
        )
        self._itext2 = re.compile(
            r"(\d+)?\s+?%s\s*((\d+)(/\d+)?)?\s*$" % self._imon_str, re.IGNORECASE
        )
        self._stext = re.compile(
            r"%s\.?\s+(\d+)?\s*,?\s*((\d+)(/\d+)?)?\s*$" % self._smon_str, re.IGNORECASE
        )
        self._stext2 = re.compile(
            r"(\d+)?\s+?%s\.?\s*((\d+)(/\d+)?)?\s*$" % self._smon_str, re.IGNORECASE
        )
        self._numeric = re.compile(r"((\d+)[/\.]\s*)?((\d+)[/\.]\s*)?(\d+)\s*$")
        self._iso = re.compile(r"(\d+)(/(\d+))?-(\d+)(-(\d+))?\s*$")
        self._isotimestamp = re.compile(
            r"^\s*?(\d{4})([01]\d)([0123]\d)(?:(?:[012]\d[0-5]\d[0-5]\d)|"
            r"(?:\s+[012]\d:[0-5]\d(?::[0-5]\d)?))?\s*?$"
        )
        self._rfc = re.compile(
            r"(%s,)?\s+(\d|\d\d)\s+%s\s+(\d+)\s+\d\d:\d\d(:\d\d)?\s+"
            r"(\+|-)\d\d\d\d" % (self._rfc_day_str, self._rfc_mon_str)
        )
        self._today = re.compile(r"^\s*%s\s*$" % self._today_str, re.IGNORECASE)

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
        return self._parse_calendar(text, self._jtext, self._jtext2, self.hebrew_to_int)

    def _parse_islamic(self, text):
        return self._parse_calendar(
            text, self._itext, self._itext2, self.islamic_to_int
        )

    def _parse_persian(self, text):
        return self._parse_calendar(
            text, self._ptext, self._ptext2, self.persian_to_int
        )

    def _parse_french(self, text):
        return self._parse_calendar(
            text, self._ftext, self._ftext2, self.french_to_int, french_valid
        )

    def _parse_gregorian(self, text):
        return self._parse_calendar(
            text, self._text, self._text2, self.month_to_int, gregorian_valid
        )

    def _parse_julian(self, text):
        return self._parse_calendar(
            text, self._text, self._text2, self.month_to_int, julian_valid
        )

    def _parse_swedish(self, text):
        return self._parse_calendar(
            text, self._stext, self._stext2, self.swedish_to_int, swedish_valid
        )

    def _parse_calendar(self, text, regex1, regex2, mmap, check=None):
        match = regex1.match(text.lower())
        if match:  # user typed in 'month-name day year' or 'month-name year'
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
                if groups[4] is not None:
                    y = int(groups[3]) + 1  # fullyear + 1
                    s = True  # slash year
                else:  # regular year
                    y = int(groups[3])
                    s = False
            value = (d, m, y, s)
            if s and julian_valid(value):  # slash year
                pass
            elif check and not check((d, m, y)):
                value = Date.EMPTY
            return value

        match = regex2.match(text.lower())
        if match:  # user typed in day month-name year or year month-name day
            groups = match.groups()
            if self.ymd:
                if groups[3] is None:
                    m = 0
                else:
                    m = mmap[groups[3].lower()]
                d = self._get_int(groups[4])
                if groups[0] is None:
                    y = None
                    s = False
                else:
                    if groups[2] is not None:
                        y = int(groups[1]) + 1  # fullyear + 1
                        s = True  # slash year
                    else:  # regular year
                        y = int(groups[1])
                        s = False
            else:
                if groups[1] is None:
                    m = 0
                else:
                    m = mmap[groups[1].lower()]
                d = self._get_int(groups[0])
                if groups[2] is None:
                    y = None
                    s = False
                else:
                    if groups[4] is not None:
                        y = int(groups[3]) + 1  # fullyear + 1
                        s = True  # slash year
                    else:  # regular year
                        y = int(groups[3])
                        s = False
            value = (d, m, y, s)
            if check and not check((d, m, y)):
                value = Date.EMPTY
            return value

        return Date.EMPTY

    def _parse_subdate(self, text, subparser=None, cal=None):
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

        match = self._iso.match(text)
        if match:
            groups = match.groups()
            y = self._get_int(groups[0])
            m = self._get_int(groups[3])
            d = self._get_int(groups[5])
            if groups[2] and julian_valid((d, m, y + 1)):
                return (d, m, y + 1, True)  # slash year
            if check is None or check((d, m, y)):
                return (d, m, y, False)
            return Date.EMPTY

        # Database datetime format, used in ex. MSSQL
        # YYYYMMDD HH:MM:SS or YYYYMMDD or YYYYMMDDHHMMSS
        match = self._isotimestamp.match(text)
        if match:
            groups = match.groups()
            y = self._get_int(groups[0])
            m = self._get_int(groups[1])
            d = self._get_int(groups[2])
            value = (d, m, y, False)
            if not check((d, m, y)):
                value = Date.EMPTY
            return value

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
            if groups == (None, None, None, None, None):
                return Date.EMPTY
            if self._ddmy:  # Icelandic
                groups = groups[1:]  # ignore the day of the week at the start
            if self.ymd:
                # '1789' and ymd: incomplete date
                if groups[1] is None:
                    y = self._get_int(groups[4])
                    m = 0
                    d = 0
                elif groups[3] is None:
                    y = self._get_int(groups[1])
                    m = self._get_int(groups[4])
                    d = 0
                else:
                    y = self._get_int(groups[1])
                    m = self._get_int(groups[3])
                    d = self._get_int(groups[4])
                if m > 12:  # maybe a slash year, not a month (1722/3 is March)
                    if y % 100 == 99:
                        modyear = (y + 1) % 1000
                    elif y % 10 == 9:
                        modyear = (y + 1) % 100
                    else:
                        modyear = (y + 1) % 10
                    if m == modyear:
                        return (0, 0, y + 1, True)  # slash year
            else:
                y = self._get_int(groups[4])
                if self.dmy:
                    if groups[3] is None:
                        m = self._get_int(groups[1])
                        d = 0
                    else:
                        m = self._get_int(groups[3])
                        d = self._get_int(groups[1])
                else:
                    m = self._get_int(groups[1])
                    d = self._get_int(groups[3])
                if m > 12:  # maybe a slash year, not a month
                    if m % 100 == 99:
                        modyear = (m + 1) % 1000
                    elif m % 10 == 9:
                        modyear = (m + 1) % 100
                    else:
                        modyear = (m + 1) % 10
                    if y == modyear:
                        return (0, 0, m + 1, True)  # slash year
            value = (d, m, y, False)
            if check and not check((d, m, y)):
                value = Date.EMPTY
            return value

        match = self._today.match(text)
        if match:
            today = Today()
            if cal:
                today = today.to_calendar(cal)
            return today.get_dmy(get_slash=True)

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
        else:
            match = self._calny_iso.match(text)
            if match:
                cal = self.calendar_to_int[match.group(2).lower()]
                newyear = tuple(map(int, match.group(3).split("-")))
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
        else:
            match = self._ny_iso.match(text)
            if match:
                newyear = tuple(map(int, match.group(2).split("-")))
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
            (text1, bc1) = self.match_bce(match.group("start"))
            start = self._parse_subdate(text1, text_parser, cal)
            if start == Date.EMPTY and text1 != "":
                return 0
            if bc1:
                start = self.invert_year(start)

            (text2, bc2) = self.match_bce(match.group("stop"))
            stop = self._parse_subdate(text2, text_parser, cal)
            if stop == Date.EMPTY and text2 != "":
                return 0
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
            (text1, bc1) = self.match_bce(match.group("start"))
            start = self._parse_subdate(text1, text_parser, cal)
            if start == Date.EMPTY and text1 != "":
                return 0
            if bc1:
                start = self.invert_year(start)

            (text2, bc2) = self.match_bce(match.group("stop"))
            stop = self._parse_subdate(text2, text_parser, cal)
            if stop == Date.EMPTY and text2 != "":
                return 0
            if bc2:
                stop = self.invert_year(stop)

            date.set(qual, Date.MOD_RANGE, cal, start + stop, newyear=ny)
            return 1
        return 0

    def match_quarter(self, text, cal, ny, qual, date):
        """
        Try matching calendar quarter date.

        On success, set the date and return 1. On failure return 0.
        """
        match = self._quarter.match(text)
        if match:
            quarter = self._get_int(match.group("quarter"))

            text_parser = self.parser[cal]
            (text, bc) = self.match_bce(match.group("year"))
            start = self._parse_subdate(text, text_parser, cal)
            if (
                (start == Date.EMPTY and text != "")
                or (start[0] != 0)
                or (start[1] != 0)
            ):  # reject dates where the day or month have been set
                return 0
            if bc:
                start = self.invert_year(start)

            stop_month = quarter * 3
            stop_day = _max_days[
                stop_month - 1
            ]  # no need to worry about leap years since no quarter ends in February

            date.set(
                qual,
                Date.MOD_RANGE,
                cal,
                (1, stop_month - 2, start[2], start[3])
                + (stop_day, stop_month, start[2], start[3]),
                newyear=ny,
            )
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
                print("ERROR MATCH:", match.groups())
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
            start = self._parse_subdate(grps[1], self.parser[cal], cal)
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
                start = self._parse_subdate(grps[0], self.parser[cal], cal)
                mod = self.modifier_after_to_int.get(grps[1].lower(), Date.MOD_NONE)
                if start == Date.EMPTY:
                    date.set_modifier(Date.MOD_TEXTONLY)
                    date.set_text_value(text)
                elif bc:
                    date.set(qual, mod, cal, self.invert_year(start), newyear=ny)
                else:
                    date.set(qual, mod, cal, start, newyear=ny)
                return True
        match = self._abt2.match(text)
        if match:
            grps = match.groups()
            start = self._parse_subdate(grps[0], cal=cal)
            mod = Date.MOD_ABOUT
            if start == Date.EMPTY:
                date.set_modifier(Date.MOD_TEXTONLY)
                date.set_text_value(text)
            elif bc:
                date.set(qual, mod, cal, self.invert_year(start), newyear=ny)
            else:
                date.set(qual, mod, cal, start, newyear=ny)
            return True
        return False

    def set_date(self, date, text):
        """
        Parses the text and sets the date according to the parsing.
        """
        text = text.strip()  # otherwise spaces can make it a bad date
        date.set_text_value(text)
        qual = Date.QUAL_NONE
        cal = Date.CAL_GREGORIAN
        newyear = Date.NEWYEAR_JAN1

        (text, cal, newyear) = self.match_calendar_newyear(text, cal, newyear)
        (text, newyear) = self.match_newyear(text, newyear)
        (text, cal) = self.match_calendar(text, cal)
        (text, qual) = self.match_quality(text, qual)

        if self.match_span(text, cal, newyear, qual, date):
            return
        if self.match_range(text, cal, newyear, qual, date):
            return
        if self.match_quarter(text, cal, newyear, qual, date):
            return

        (text, bc) = self.match_bce(text)
        if self.match_modifier(text, cal, newyear, qual, bc, date):
            return

        try:
            subdate = self._parse_subdate(text, self.parser[cal], cal)
            if subdate == Date.EMPTY and text != "":
                date.set_as_text(text)
                return
        except:
            date.set_as_text(text)
            return

        if bc:
            date.set(
                qual, Date.MOD_NONE, cal, self.invert_year(subdate), newyear=newyear
            )
        else:
            date.set(qual, Date.MOD_NONE, cal, subdate, newyear=newyear)

    def invert_year(self, subdate):
        return (subdate[0], subdate[1], -subdate[2], subdate[3])

    def parse(self, text):
        """
        Parses the text, returning a :class:`.Date` object.
        """
        new_date = Date()
        try:
            self.set_date(new_date, text)
        except DateError:
            new_date.set_as_text(text)
        return new_date
