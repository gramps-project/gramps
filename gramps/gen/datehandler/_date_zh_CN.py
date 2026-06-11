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
Simplified-Chinese-specific classes for parsing and displaying dates.
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

# Simplified Chinese month names for the Chinese Lunar calendar.
# Index 0 is a placeholder; indices 1-12 correspond to months 1-12.
_CHINESE_LUNAR_MONTHS_CN = (
    "",
    "正月",
    "二月",
    "三月",
    "四月",
    "五月",
    "六月",
    "七月",
    "八月",
    "九月",
    "十月",
    "十一月",
    "十二月",
)


# -------------------------------------------------------------------------
#
# Simplified-Chinese parser
#
# -------------------------------------------------------------------------
class DateParserZH_CN(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    # modifiers before the date
    modifier_to_int = {
        "以前": Date.MOD_BEFORE,
        "以后": Date.MOD_AFTER,
        "大约": Date.MOD_ABOUT,
        "从": Date.MOD_FROM,
        "到": Date.MOD_TO,
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

    calendar_to_int = {
        "阳历": Date.CAL_GREGORIAN,
        "g": Date.CAL_GREGORIAN,
        "儒略历": Date.CAL_JULIAN,
        "j": Date.CAL_JULIAN,
        "希伯来历": Date.CAL_HEBREW,
        "h": Date.CAL_HEBREW,
        "伊斯兰历": Date.CAL_ISLAMIC,
        "i": Date.CAL_ISLAMIC,
        "法国共和历": Date.CAL_FRENCH,
        "f": Date.CAL_FRENCH,
        "伊郎历": Date.CAL_PERSIAN,
        "p": Date.CAL_PERSIAN,
        "瑞典历": Date.CAL_SWEDISH,
        "s": Date.CAL_SWEDISH,
        "农历": Date.CAL_CHINESE_LUNAR,
        "阴历": Date.CAL_CHINESE_LUNAR,
        "旧历": Date.CAL_CHINESE_LUNAR,
        "cl": Date.CAL_CHINESE_LUNAR,
    }

    quality_to_int = {
        "据估计": Date.QUAL_ESTIMATED,
        "据计算": Date.QUAL_CALCULATED,
    }

    bce = ["before calendar", "negative year"] + DateParser.bce

    def init_strings(self):
        """
        Compile date-matching regular expressions, adding Chinese Lunar
        month names to the shared chinese_lunar_to_int prefix table.
        """
        DateParser.init_strings(self)

        # Add Simplified Chinese character month names for parsing.
        DateParser.chinese_lunar_to_int.update(
            {
                "正月": 1,
                "一月": 1,
                "二月": 2,
                "三月": 3,
                "四月": 4,
                "五月": 5,
                "六月": 6,
                "七月": 7,
                "八月": 8,
                "九月": 9,
                "十月": 10,
                "十一月": 11,
                "十二月": 12,
                # Leap months (Simplified: 闰)
                "闰正月": 101,
                "闰一月": 101,
                "闰二月": 102,
                "闰三月": 103,
                "闰四月": 104,
                "闰五月": 105,
                "闰六月": 106,
                "闰七月": 107,
                "闰八月": 108,
                "闰九月": 109,
                "闰十月": 110,
                "闰十一月": 111,
                "闰十二月": 112,
            }
        )

        # Rebuild Chinese Lunar regexes now that character names are added.
        self._clmon_str = self.re_longest_first(list(self.chinese_lunar_to_int.keys()))
        self._cltext = re.compile(
            r"%s\.?(\s+\d+)?\s*,?\s+((\d+)(/\d+)?)?\s*$" % self._clmon_str,
            re.IGNORECASE,
        )
        self._cltext2 = re.compile(
            r"(\d+)?\s+?%s\.?\s*((\d+)(/\d+)?)?\s*$" % self._clmon_str,
            re.IGNORECASE,
        )

        _span_1 = ["自"]
        _span_2 = ["至"]
        _range_1 = ["介于"]
        _range_2 = ["与"]
        _range_3 = ["之间"]
        self._span = re.compile(
            r"(%s)\s*(?P<start>.+)\s*(%s)\s*(?P<stop>.+)"
            % ("|".join(_span_1), "|".join(_span_2)),
            re.IGNORECASE,
        )
        self._range = re.compile(
            r"(%s)\s*(?P<start>.+)\s*(%s)\s*(?P<stop>.+)\s*(%s)"
            % ("|".join(_range_1), "|".join(_range_2), "|".join(_range_3)),
            re.IGNORECASE,
        )
        self._numeric = re.compile(r"((\d+)年\s*)?((\d+)月\s*)?(\d+)?日?\s*$")


# -------------------------------------------------------------------------
#
# Simplified-Chinese display
#
# -------------------------------------------------------------------------
class DateDisplayZH_CN(DateDisplay):
    """
    Simplified-Chinese language date display class.
    """

    formats = (
        "年年年年-月月-日日 (ISO)",
        "数字格式",
    )
    # this definition must agree with its "_display_calendar" method

    _bce_str = "%s B.C.E."

    # Override pinyin month names with Chinese characters.
    chinese_lunar = _CHINESE_LUNAR_MONTHS_CN

    display = DateDisplay.display_formatted

    def _display_calendar(self, date_val, long_months, short_months=None, inflect=""):
        """Display a date using Chinese numeric format or ISO."""
        if short_months is None:
            short_months = long_months

        if self.format == 0:
            return self.display_iso(date_val)
        else:
            value = self.dd_dformat01(date_val)
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    def _display_chinese_lunar(self, date_val, **kwargs):
        """Display a Chinese Lunar date in native 年/月/日 format."""
        month = date_val[1]
        is_leap = month > 100
        actual = month - 100 if is_leap else month
        year = date_val[2]
        day = date_val[0]

        if actual == 0 and day == 0:
            return "%s年" % year

        leap_prefix = "闰" if is_leap else ""
        month_str = self.chinese_lunar[actual] if actual else ""

        if day == 0:
            return "%s年%s%s" % (year, leap_prefix, month_str)
        return "%s年%s%s%s日" % (year, leap_prefix, month_str, day)


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------

register_datehandler(
    ("zh_CN", "zh_SG", "zh", "chinese", "Chinese", ("%Y年%m月%d日",)),
    DateParserZH_CN,
    DateDisplayZH_CN,
)
