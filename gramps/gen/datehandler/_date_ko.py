# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2014-2015  Paul Franklin
# Copyright (C) 2026       Doug Blank
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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Korean-specific classes for parsing and displaying dates.
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
from ..lib.gcalendar import korean_ganji_year
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

# Korean month names for the Korean Lunar (음력) calendar.
# Index 0 is a placeholder; indices 1-12 correspond to months 1-12.
_KOREAN_LUNAR_MONTHS = (
    "",
    "정월",
    "이월",
    "삼월",
    "사월",
    "오월",
    "유월",
    "칠월",
    "팔월",
    "구월",
    "시월",
    "십일월",
    "십이월",
)


# ------------------------------------------------------------
#
# DateParserKO
#
# ------------------------------------------------------------
class DateParserKO(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    modifier_to_int = {
        "이전": Date.MOD_BEFORE,
        "이후": Date.MOD_AFTER,
        "약": Date.MOD_ABOUT,
        "부터": Date.MOD_FROM,
        "까지": Date.MOD_TO,
    }

    calendar_to_int = {
        "양력": Date.CAL_GREGORIAN,
        "g": Date.CAL_GREGORIAN,
        "율리우스": Date.CAL_JULIAN,
        "j": Date.CAL_JULIAN,
        "히브리": Date.CAL_HEBREW,
        "h": Date.CAL_HEBREW,
        "이슬람": Date.CAL_ISLAMIC,
        "i": Date.CAL_ISLAMIC,
        "프랑스": Date.CAL_FRENCH,
        "f": Date.CAL_FRENCH,
        "페르시아": Date.CAL_PERSIAN,
        "p": Date.CAL_PERSIAN,
        "스웨덴": Date.CAL_SWEDISH,
        "s": Date.CAL_SWEDISH,
        "음력": Date.CAL_KOREAN_LUNAR,
        "한국음력": Date.CAL_KOREAN_LUNAR,
        "kl": Date.CAL_KOREAN_LUNAR,
    }

    quality_to_int = {
        "추정": Date.QUAL_ESTIMATED,
        "계산": Date.QUAL_CALCULATED,
    }

    bce = ["before calendar", "negative year"] + DateParser.bce

    def init_strings(self):
        """
        Compile date-matching regular expressions, adding Korean Lunar
        month names to the shared korean_lunar_to_int prefix table.
        """
        DateParser.init_strings(self)

        DateParser.korean_lunar_to_int.update(
            {
                "정월": 1,
                "1월": 1,
                "이월": 2,
                "2월": 2,
                "삼월": 3,
                "3월": 3,
                "사월": 4,
                "4월": 4,
                "오월": 5,
                "5월": 5,
                "유월": 6,
                "6월": 6,
                "칠월": 7,
                "7월": 7,
                "팔월": 8,
                "8월": 8,
                "구월": 9,
                "9월": 9,
                "시월": 10,
                "10월": 10,
                "십일월": 11,
                "11월": 11,
                "십이월": 12,
                "12월": 12,
                # Leap months (윤)
                "윤정월": 101,
                "윤1월": 101,
                "윤이월": 102,
                "윤2월": 102,
                "윤삼월": 103,
                "윤3월": 103,
                "윤사월": 104,
                "윤4월": 104,
                "윤오월": 105,
                "윤5월": 105,
                "윤유월": 106,
                "윤6월": 106,
                "윤칠월": 107,
                "윤7월": 107,
                "윤팔월": 108,
                "윤8월": 108,
                "윤구월": 109,
                "윤9월": 109,
                "윤시월": 110,
                "윤10월": 110,
                "윤십일월": 111,
                "윤11월": 111,
                "윤십이월": 112,
                "윤12월": 112,
            }
        )

        # Rebuild Korean Lunar regexes with the full name table.
        self._klmon_str = self.re_longest_first(
            list(self.korean_lunar_to_int.keys())
        )
        self._kltext = re.compile(
            r"%s\.?(\s+\d+)?\s*,?\s+((\d+)(/\d+)?)?\s*$" % self._klmon_str,
            re.IGNORECASE,
        )
        self._kltext2 = re.compile(
            r"(\d+)?\s+?%s\.?\s*((\d+)(/\d+)?)?\s*$" % self._klmon_str,
            re.IGNORECASE,
        )

        _span_1 = ["부터"]
        _span_2 = ["까지"]
        _range_1 = ["사이"]
        _range_2 = ["와", "과"]
        _range_3 = []
        self._span = re.compile(
            r"(%s)\s*(?P<start>.+)\s*(%s)\s*(?P<stop>.+)"
            % ("|".join(_span_1), "|".join(_span_2)),
            re.IGNORECASE,
        )
        if _range_3:
            self._range = re.compile(
                r"(%s)\s*(?P<start>.+)\s*(%s)\s*(?P<stop>.+)\s*(%s)"
                % ("|".join(_range_1), "|".join(_range_2), "|".join(_range_3)),
                re.IGNORECASE,
            )
        else:
            self._range = re.compile(
                r"(%s)\s*(?P<start>.+)\s*(%s)\s*(?P<stop>.+)"
                % ("|".join(_range_1), "|".join(_range_2)),
                re.IGNORECASE,
            )

        self._numeric = re.compile(
            r"((\d+)\s*년\s*)?((\d+)\s*월\s*)?(\d+)?\s*일?\s*$",
            re.IGNORECASE,
        )


# ------------------------------------------------------------
#
# DateDisplayKO
#
# ------------------------------------------------------------
class DateDisplayKO(DateDisplay):
    """
    Korean language date display class.
    """

    formats = (
        "YYYY-MM-DD (ISO)",
        "숫자 (일 월 년)",
        "간지 년",
    )
    # this definition must agree with its "_display_calendar" method

    _bce_str = "%s B.C.E."

    # Override romanized month names with Korean Hangul.
    korean_lunar = _KOREAN_LUNAR_MONTHS

    display = DateDisplay.display_formatted

    def _display_korean_lunar(self, date_val, **kwargs):
        """Display a Korean Lunar date in 년/월/일 format.

        Format 0: ISO numeric.  Format 1: numeric year + month name + day.
        Format 2: 간지 (干支) year name + month + day.
        """
        month = date_val[1]
        is_leap = month > 100
        actual = month - 100 if is_leap else month
        year = date_val[2]
        day = date_val[0]

        if self.format == 0:
            return self.display_iso(date_val)

        leap_prefix = "윤" if is_leap else ""
        month_str = _KOREAN_LUNAR_MONTHS[actual] if actual else ""

        if self.format == 2:
            year_str = "%s년" % korean_ganji_year(year)
        else:
            year_str = "%s년" % year

        if actual == 0 and day == 0:
            return year_str
        if day == 0:
            return "%s %s%s" % (year_str, leap_prefix, month_str)
        return "%s %s%s %s일" % (year_str, leap_prefix, month_str, day)


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------

register_datehandler(
    ("ko", "ko_KR", "korean", "Korean", ("%Y년%m월%d일",)),
    DateParserKO,
    DateDisplayKO,
)
