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
Vietnamese-specific classes for parsing and displaying dates.
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
from ..lib.gcalendar import vietnamese_can_chi_year
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

# Vietnamese month names for the Vietnamese Lunar (Âm Lịch) calendar.
# Index 0 is a placeholder; indices 1-12 correspond to months 1-12.
_VIETNAMESE_LUNAR_MONTHS = (
    "",
    "Tháng Giêng",
    "Tháng Hai",
    "Tháng Ba",
    "Tháng Tư",
    "Tháng Năm",
    "Tháng Sáu",
    "Tháng Bảy",
    "Tháng Tám",
    "Tháng Chín",
    "Tháng Mười",
    "Tháng Mười Một",
    "Tháng Chạp",
)


# ------------------------------------------------------------
#
# DateParserVI
#
# ------------------------------------------------------------
class DateParserVI(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    modifier_to_int = {
        "trước": Date.MOD_BEFORE,
        "sau": Date.MOD_AFTER,
        "khoảng": Date.MOD_ABOUT,
        "từ": Date.MOD_FROM,
        "đến": Date.MOD_TO,
    }

    calendar_to_int = {
        "dương lịch": Date.CAL_GREGORIAN,
        "g": Date.CAL_GREGORIAN,
        "julius": Date.CAL_JULIAN,
        "j": Date.CAL_JULIAN,
        "hebrew": Date.CAL_HEBREW,
        "h": Date.CAL_HEBREW,
        "hồi giáo": Date.CAL_ISLAMIC,
        "i": Date.CAL_ISLAMIC,
        "pháp": Date.CAL_FRENCH,
        "f": Date.CAL_FRENCH,
        "ba tư": Date.CAL_PERSIAN,
        "p": Date.CAL_PERSIAN,
        "thụy điển": Date.CAL_SWEDISH,
        "s": Date.CAL_SWEDISH,
        "âm lịch": Date.CAL_VIETNAMESE_LUNAR,
        "am lich": Date.CAL_VIETNAMESE_LUNAR,
        "vl": Date.CAL_VIETNAMESE_LUNAR,
    }

    quality_to_int = {
        "ước tính": Date.QUAL_ESTIMATED,
        "tính toán": Date.QUAL_CALCULATED,
    }

    bce = ["before calendar", "negative year"] + DateParser.bce

    def init_strings(self):
        """
        Compile date-matching regular expressions, adding Vietnamese Lunar
        month names to the shared vietnamese_lunar_to_int prefix table.
        """
        DateParser.init_strings(self)

        DateParser.vietnamese_lunar_to_int.update(
            {
                "tháng giêng": 1,
                "tháng 1": 1,
                "tháng hai": 2,
                "tháng 2": 2,
                "tháng ba": 3,
                "tháng 3": 3,
                "tháng tư": 4,
                "tháng 4": 4,
                "tháng năm": 5,
                "tháng 5": 5,
                "tháng sáu": 6,
                "tháng 6": 6,
                "tháng bảy": 7,
                "tháng 7": 7,
                "tháng tám": 8,
                "tháng 8": 8,
                "tháng chín": 9,
                "tháng 9": 9,
                "tháng mười": 10,
                "tháng 10": 10,
                "tháng mười một": 11,
                "tháng 11": 11,
                "tháng chạp": 12,
                "tháng mười hai": 12,
                "tháng 12": 12,
                # Leap months (nhuận)
                "nhuận tháng giêng": 101,
                "nhuận tháng 1": 101,
                "nhuận tháng hai": 102,
                "nhuận tháng 2": 102,
                "nhuận tháng ba": 103,
                "nhuận tháng 3": 103,
                "nhuận tháng tư": 104,
                "nhuận tháng 4": 104,
                "nhuận tháng năm": 105,
                "nhuận tháng 5": 105,
                "nhuận tháng sáu": 106,
                "nhuận tháng 6": 106,
                "nhuận tháng bảy": 107,
                "nhuận tháng 7": 107,
                "nhuận tháng tám": 108,
                "nhuận tháng 8": 108,
                "nhuận tháng chín": 109,
                "nhuận tháng 9": 109,
                "nhuận tháng mười": 110,
                "nhuận tháng 10": 110,
                "nhuận tháng mười một": 111,
                "nhuận tháng 11": 111,
                "nhuận tháng chạp": 112,
                "nhuận tháng mười hai": 112,
                "nhuận tháng 12": 112,
            }
        )

        # Rebuild Vietnamese Lunar regexes with the full name table.
        self._vlmon_str = self.re_longest_first(
            list(self.vietnamese_lunar_to_int.keys())
        )
        self._vltext = re.compile(
            r"%s\.?(\s+\d+)?\s*,?\s+((\d+)(/\d+)?)?\s*$" % self._vlmon_str,
            re.IGNORECASE,
        )
        self._vltext2 = re.compile(
            r"(\d+)?\s+?%s\.?\s*((\d+)(/\d+)?)?\s*$" % self._vlmon_str,
            re.IGNORECASE,
        )

        _span_1 = ["từ"]
        _span_2 = ["đến"]
        _range_1 = ["giữa"]
        _range_2 = ["và"]
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
            r"((\d+)\s*năm\s*)?((\d+)\s*tháng\s*)?(\d+)?\s*ngày?\s*$",
            re.IGNORECASE,
        )


# ------------------------------------------------------------
#
# DateDisplayVI
#
# ------------------------------------------------------------
class DateDisplayVI(DateDisplay):
    """
    Vietnamese language date display class.
    """

    formats = (
        "YYYY-MM-DD (ISO)",
        "Số (ngày tháng năm)",
        "Năm Can Chi",
    )
    # this definition must agree with its "_display_calendar" method

    _bce_str = "%s TCN"

    display = DateDisplay.display_formatted

    def _display_vietnamese_lunar(self, date_val, **kwargs):
        """Display a Vietnamese Lunar date in ngày/tháng/năm format.

        Format 0: ISO numeric.  Format 1: numeric day + month name + year.
        Format 2: Can-Chi year name + month + day.
        """
        month = date_val[1]
        is_leap = month > 100
        actual = month - 100 if is_leap else month
        year = date_val[2]
        day = date_val[0]

        if self.format == 0 or is_leap:
            return self.display_iso(date_val)

        leap_prefix = "Nhuận " if is_leap else ""
        month_str = _VIETNAMESE_LUNAR_MONTHS[actual] if actual else ""

        if self.format == 2:
            year_str = "Năm %s" % vietnamese_can_chi_year(year)
        else:
            year_str = "Năm %s" % year

        if actual == 0 and day == 0:
            return year_str
        if day == 0:
            return "%s %s%s" % (year_str, leap_prefix, month_str)
        return "%s %s%s Ngày %s" % (year_str, leap_prefix, month_str, day)


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------

register_datehandler(
    ("vi", "vi_VN", "vietnamese", "Vietnamese", ("%d/%m/%Y",)),
    DateParserVI,
    DateDisplayVI,
)
