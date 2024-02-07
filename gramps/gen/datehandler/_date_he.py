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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
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
from ._dateparser import DateParser
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
        self._modifier = re.compile(r"%s\s*(.*)" % self._mod_str, re.IGNORECASE)
        self._text2 = re.compile(
            r"(\d+)?\s+?ב?%s\.?\s*((\d+)(/\d+)?)?\s*$" % self._mon_str, re.IGNORECASE
        )
        self._jtext2 = re.compile(
            r"(\d+)?\s+?ב?%s\s*((\d+)(/\d+)?)?\s*$" % self._jmon_str, re.IGNORECASE
        )
        self._ftext2 = re.compile(
            r"(\d+)?\s+?ב?%s\s*((\d+)(/\d+)?)?\s*$" % self._fmon_str, re.IGNORECASE
        )
        self._ptext2 = re.compile(
            r"(\d+)?\s+?ב?%s\s*((\d+)(/\d+)?)?\s*$" % self._pmon_str, re.IGNORECASE
        )
        self._itext2 = re.compile(
            r"(\d+)?\s+?ב?%s\s*((\d+)(/\d+)?)?\s*$" % self._imon_str, re.IGNORECASE
        )
        self._stext2 = re.compile(
            r"(\d+)?\s+?ב?%s\.?\s*((\d+)(/\d+)?)?\s*$" % self._smon_str, re.IGNORECASE
        )
        _span_1 = ["מ־", "מ"]
        _span_2 = ["עד"]
        _range_1 = ["בין"]
        _range_2 = ["ל־", "ל"]
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
