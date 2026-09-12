# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2023       Avi Markovitz
# Copyright (C) 2023       Nick Hall
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/\>.
#

"""
Hebrew-specific classes for parsing and displaying dates.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import re

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..lib.date import Date
from ._dateparser import (
    DateParser,
    gregorian_valid,
    julian_valid,
    swedish_valid,
    french_valid,
)
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

# -------------------------------------------------------------------------
#
# Hebrew parser
#
# -------------------------------------------------------------------------


class DateParserHE(DateParser):
    calendar_to_int = {
        "גרגוריאני": Date.CAL_GREGORIAN,
        "אזרחי": Date.CAL_GREGORIAN,
        "יוליאני": Date.CAL_JULIAN,
        "י": Date.CAL_JULIAN,
        "עברי": Date.CAL_HEBREW,
        "ע": Date.CAL_HEBREW,
        "מוסלמי": Date.CAL_ISLAMIC,
        "מ": Date.CAL_ISLAMIC,
        "המהפכה הצרפתית": Date.CAL_FRENCH,
        "צ": Date.CAL_FRENCH,
        "פרסי": Date.CAL_PERSIAN,
        "פ": Date.CAL_PERSIAN,
        "שוודי": Date.CAL_SWEDISH,
        "ש": Date.CAL_SWEDISH,
    }

    # Where there are substrings, put the longest string first. e.g. "ב־" before "ב".
    modifier_to_int = {
        "ב־": Date.MOD_NONE,
        "ב": Date.MOD_NONE,
        "לפני": Date.MOD_BEFORE,
        "לפני ה־": Date.MOD_BEFORE,
        "לפ.": Date.MOD_BEFORE,
        "אחרי": Date.MOD_AFTER,
        "אחרי ה־": Date.MOD_AFTER,
        "אח.": Date.MOD_AFTER,
        "בסביבות־": Date.MOD_ABOUT,
        "בסביבות": Date.MOD_ABOUT,
        "בערך ב־": Date.MOD_ABOUT,
        "בערך ב": Date.MOD_ABOUT,
        "באזור ה־": Date.MOD_ABOUT,
        "באזור ה": Date.MOD_ABOUT,
        "קרוב ל־": Date.MOD_ABOUT,
        "קרוב ל": Date.MOD_ABOUT,
        "בקרוב": Date.MOD_ABOUT,
        "במקורב": Date.MOD_ABOUT,
        "מיום": Date.MOD_FROM,
        "מה־": Date.MOD_FROM,
        "מ־": Date.MOD_FROM,
        "מ": Date.MOD_FROM,
        "עד ל־": Date.MOD_TO,
        "עד ל": Date.MOD_TO,
        "עד": Date.MOD_TO,
        "עד יום": Date.MOD_TO,
        "עד ה־": Date.MOD_TO,
        "ועד יום": Date.MOD_TO,
    }

    quality_to_int = {
        "מוערך": Date.QUAL_ESTIMATED,
        "משוער": Date.QUAL_ESTIMATED,
        "מחושב": Date.QUAL_CALCULATED,
    }

    bce = [
        "לפני הספירה",
        "לפני עידן זה",
        'לפנה"\\ס',
        "לפני ספירת הנוצרים",
        "לספירתם",
    ] + DateParser.bce

    def init_strings(self):
        DateParser.init_strings(self)

        # Negative lookahead (?![א-ת]) prevents the single-letter
        # modifiers "מ"/"ב" (no maqaf) from matching as a false prefix
        # inside ordinary Hebrew words that happen to start with the
        # same letter -- most notably the Gregorian month names "מאי"
        # (May) and "מרץ" (March). Without this guard, "מאי 1944" was
        # wrongly split into modifier "מ" + leftover text "אי 1944",
        # which is not a valid date and so parsing failed entirely.
        # Genuine modifier usage ("מ 1893", "מ-1893", "מ־1893", "מיום
        # 1944", etc.) is unaffected, since in all of those the letter
        # is followed by a non-Hebrew-letter character (space, digit,
        # or maqaf), not by another Hebrew letter.
        self._modifier = re.compile(
            r"%s(?![א-ת])\s*(.*)" % self._mod_str, re.IGNORECASE
        )

        # Optional geresh (Hebrew ׳ or ASCII ') right after an
        # abbreviated month name, e.g. "יונ'" or "יונ׳" for June.
        self._text = re.compile(
            r"%s['׳]?\.?(\s+\d+)?\s*,?\s+((\d+)(/\d+)?)?\s*$" % self._mon_str,
            re.IGNORECASE,
        )
        self._text2 = re.compile(
            r"(\d+)?\s+?ב?%s['׳]?\.?\s*((\d+)(/\d+)?)?\s*$" % self._mon_str,
            re.IGNORECASE,
        )
        self._jtext2 = re.compile(
            r"(\d+)?\s+?ב?%s['׳]?\s*((\d+)(/\d+)?)?\s*$" % self._jmon_str,
            re.IGNORECASE,
        )
        self._ftext2 = re.compile(
            r"(\d+)?\s+?ב?%s['׳]?\s*((\d+)(/\d+)?)?\s*$" % self._fmon_str,
            re.IGNORECASE,
        )
        self._ptext2 = re.compile(
            r"(\d+)?\s+?ב?%s['׳]?\s*((\d+)(/\d+)?)?\s*$" % self._pmon_str,
            re.IGNORECASE,
        )
        self._itext2 = re.compile(
            r"(\d+)?\s+?ב?%s['׳]?\s*((\d+)(/\d+)?)?\s*$" % self._imon_str,
            re.IGNORECASE,
        )
        self._stext2 = re.compile(
            r"(\d+)?\s+?ב?%s['׳]?\.?\s*((\d+)(/\d+)?)?\s*$" % self._smon_str,
            re.IGNORECASE,
        )

        # Flexible 3-field numeric date, with any separator among
        # . - / (used in _parse_subdate below to support both
        # yyyy-dd-mm and mm-dd-yyyy, alongside the regular
        # dd-mm-yyyy / yyyy-mm-dd forms).
        self._numeric_flexible = re.compile(
            r"^\s*(\d+)\s*[./\-]\s*(\d+)\s*[./\-]\s*(\d+)\s*$"
        )

        # A bare two-year span, e.g. "1893-1894" or "1893–1894" (en
        # dash), without needing the words "from...to" (used in
        # match_span below).
        self._bare_year_span = re.compile(r"^\s*(\d{3,4})\s*[-–]\s*(\d{3,4})\s*$")

        # "מ" (from) and "ל" (to) are also supported with a regular
        # hyphen (מ-1893) and with the Hebrew maqaf (מ־1893), not only
        # with no separator at all.
        _span_1 = ["מ־", "מ-", "מ"]
        _span_2 = ["עד"]
        _range_1 = ["בין"]
        _range_2 = ["ל־", "ל-", "ל"]
        self._span = re.compile(
            r"(%s)\s*(?P<start>.+)\s+(%s)\s+(?P<stop>.+)"
            % ("|".join(_span_1), "|".join(_span_2)),
            re.IGNORECASE,
        )
        self._range = re.compile(
            r"(%s)\s+(?P<start>.+)\s+(%s)\s*(?P<stop>.+)"
            % ("|".join(_range_1), "|".join(_range_2)),
            re.IGNORECASE,
        )

    def _parse_subdate(self, text, subparser=None, cal=None):
        """
        Same as DateParser._parse_subdate, plus support for a flexible
        3-field numeric date with any separator (./-), including
        yyyy-dd-mm and mm-dd-yyyy: day vs. month is decided by
        magnitude (over 12 = day); only when both fields are
        ambiguous (both <= 12) does it fall back to the existing
        default (day-month for the year-last form, month-day for the
        year-first/ISO form). All other behaviour (slash-year, partial
        date, RFC-2822, "$T"/"today") is unchanged from the original
        DateParser.
        """
        if subparser is None:
            subparser = self._parse_gregorian
        check = {
            self._parse_gregorian: gregorian_valid,
            self._parse_julian: julian_valid,
            self._parse_swedish: swedish_valid,
            self._parse_french: french_valid,
        }.get(subparser)

        # 1) Forms with a month name (Hebrew/Gregorian/French/...)
        value = subparser(text)
        if value != Date.EMPTY:
            return value

        # 2) Flexible numeric date
        match = self._numeric_flexible.match(text)
        if match:
            a, b, c = (int(g) for g in match.groups())
            long_idx = [i for i, g in enumerate((a, b, c)) if len(str(g)) >= 3]
            if len(long_idx) == 1:
                idx = long_idx[0]
                year = x = z = month_first = None
                if idx == 0:
                    year, x, z, month_first = a, b, c, True  # yyyy-X-Z
                elif idx == 2:
                    year, x, z, month_first = c, a, b, False  # X-Z-yyyy

                if year is not None:
                    day = month = None
                    if x > 12 and z <= 12:
                        day, month = x, z
                    elif z > 12 and x <= 12:
                        day, month = z, x
                    elif x <= 12 and z <= 12:  # ambiguous: existing default
                        if month_first:
                            month, day = x, z
                        else:
                            day, month = x, z

                    if day is not None:
                        value = (day, month, year, False)
                        if check is None or check((day, month, year)):
                            return value
                        return Date.EMPTY

        # 3) Everything else unchanged: regular ISO, slash-year,
        #    DB stamp, RFC-2822, "$T"/"today"
        return DateParser._parse_subdate(self, text, subparser, cal)

    def match_span(self, text, cal, ny, qual, date):
        """
        Same as DateParser.match_span, plus support for a bare
        two-year span without the words "from...to", e.g. "1893-1894"
        or "1893–1894" (en dash) -- parsed exactly like "מ־1893 עד
        1894".
        """
        bare = self._bare_year_span.match(text)
        if bare:
            year1, year2 = int(bare.group(1)), int(bare.group(2))
            if year2 >= year1:
                date.set(
                    qual,
                    Date.MOD_SPAN,
                    cal,
                    (0, 0, year1, False, 0, 0, year2, False),
                    newyear=ny,
                )
                return 1
            # Larger year before smaller year (e.g. "1894-1893") -- not
            # guessed at, falls back to normal behaviour (will fail,
            # exactly as today)
        return DateParser.match_span(self, text, cal, ny, qual, date)


# -------------------------------------------------------------------------
#
# Hebrew display
#
# -------------------------------------------------------------------------
class DateDisplayHE(DateDisplay):
    """
    Hebrew language date display class.
    """

    _bce_str = "%s לספירה"

    long_months = (
        "",
        "ינואר",
        "פברואר",
        "מרץ",
        "אפריל",
        "מאי",
        "יוני",
        "יולי",
        "אוגוסט",
        "ספטמבר",
        "אוקטובר",
        "נובמבר",
        "דצמבר",
    )

    short_months = (
        "",
        "ינו",
        "פבר",
        "מרץ",
        "אפר",
        "מאי",
        "יונ",
        "יול",
        "אוג",
        "ספט",
        "אוק",
        "נוב",
        "דצמ",
    )

    hebrew = (
        "",
        "תשרי",
        "חשוון",
        "כסלו",
        "תבט",
        "שבט",
        "אדר",
        "אדר א'",
        "ניסן",
        "אייר",
        "סיוון",
        "תמוז",
        "אב",
        "אלול",
    )

    formats = (
        "DD-MM-AAAA (ISO)",
        "סיפרתי",
        "חודש יום, שנה",
        "חודש יום, שנה",
        "יום חודש, שנה",
        "יום חודש, שנה",
    )
    # this must agree with DateDisplayEn's "formats" definition
    # (since no locale-specific _display_gregorian exists, here)

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
            return ""
        elif mod == Date.MOD_SPAN:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s%s" % (qual_str, add_prefix(d1, "מ"), "עד", d2, scal)
        elif mod == Date.MOD_RANGE:
            d1 = self.display_cal[cal](start)
            d2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s%s" % (qual_str, "בין", d1, add_prefix(d2, "ל"), scal)
        elif mod == Date.MOD_NONE:
            text = self.display_cal[cal](start)
            scal = self.format_extras(cal, newyear)
            if start[0] == 0 or qual != Date.QUAL_NONE:
                text = add_prefix(text, "ב")
            return "%s%s%s" % (qual_str, text, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            term = self._mod_str[mod]
            if term.endswith(" "):
                modifier = term + text
            else:
                modifier = add_prefix(text, term)
            return "%s%s%s" % (qual_str, modifier, scal)


def add_prefix(text, prefix):
    """
    Return a prefixed string with a maqaf added for non-Hebrew text.
    """
    if text[0] < "א" or text[0] > "ת":
        return prefix + "־" + text
    else:
        return prefix + text


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------
register_datehandler(
    ("he_IL", "he", "Hebrew", "Ivrit", "עברית", ("%d-%m-%Y",)),
    DateParserHE,
    DateDisplayHE,
)
