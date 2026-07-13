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
from ..lib.gcalendar import chinese_sexagenary_year
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

# Compound quality+modifier strings: both display and parser use this table.
# Keys are the display prefix; values are (quality, modifier) integer pairs.
_COMPOUND_QUAL_MOD: dict[str, tuple[int, int]] = {
    "估计早于": (Date.QUAL_ESTIMATED, Date.MOD_BEFORE),
    "估计晚于": (Date.QUAL_ESTIMATED, Date.MOD_AFTER),
    "推算早于": (Date.QUAL_CALCULATED, Date.MOD_BEFORE),
    "推算晚于": (Date.QUAL_CALCULATED, Date.MOD_AFTER),
}


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
        "大约": Date.MOD_ABOUT,
        "从": Date.MOD_FROM,
        "到": Date.MOD_TO,
    }

    # 以前/以后 follow the date in Chinese: "2000年以前", "2000年以后"
    modifier_after_to_int = {
        "以前": Date.MOD_BEFORE,
        "以后": Date.MOD_AFTER,
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
        # New display forms; kept for round-trip parsing.
        "估计为": Date.QUAL_ESTIMATED,
        "推算为": Date.QUAL_CALCULATED,
    }

    bce = ["before calendar", "negative year"] + DateParser.bce

    def __init__(self, *args: object, **kwargs: object) -> None:
        """
        Initialize the parser and set pending-modifier state.

        _pending_modifier is set by match_quality when a compound
        quality+modifier prefix (e.g. "估计早于") is recognised, then
        consumed by match_modifier to apply the encoded modifier.
        """
        self._pending_modifier: int = Date.MOD_NONE
        super().__init__(*args, **kwargs)

    def init_strings(self) -> None:
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

        # Chinese postfix modifiers attach directly to the date with no space:
        # "2000年以前". Override the base regex which requires \s+.
        self._modifier_after = re.compile(
            r"(.*?)\s*(%s)\s*$" % self._mod_after_str, re.IGNORECASE
        )

        # Allow zero whitespace between a quality word and the date so that
        # display strings like "估计为1800年" parse without a separating space.
        self._qual = re.compile(r"(.* ?)%s\s*(.+)" % self._qual_str, re.IGNORECASE)

        # Allow zero whitespace between a prefix modifier and the date so that
        # display strings like "大约1850年" parse without a separating space.
        self._modifier = re.compile(r"%s\s*(.*)" % self._mod_str, re.IGNORECASE)

    def match_quality(self, text: str, qual: int) -> tuple[str, int]:
        """
        Try matching quality, including compound quality+modifier prefixes.

        Compound strings like "估计早于" encode both QUAL_ESTIMATED and
        MOD_BEFORE.  When one is found, the modifier is stashed in
        _pending_modifier for match_modifier to consume.
        """
        for compound, (q, m) in _COMPOUND_QUAL_MOD.items():
            if text.startswith(compound):
                self._pending_modifier = m
                return (text[len(compound) :], q)
        self._pending_modifier = Date.MOD_NONE
        return super().match_quality(text, qual)

    def match_modifier(
        self, text: str, cal: int, ny: int, qual: int, bc: bool, date: Date
    ) -> bool:
        """
        Try matching date with modifier, consuming any pending compound modifier.

        If match_quality stashed a modifier from a compound prefix, apply it
        directly to the remaining date text without another regex scan.
        """
        if self._pending_modifier != Date.MOD_NONE:
            mod = self._pending_modifier
            self._pending_modifier = Date.MOD_NONE
            start = self._parse_subdate(text, self.parser[cal], cal)
            if start == Date.EMPTY:
                date.set_modifier(Date.MOD_TEXTONLY)
                date.set_text_value(text)
            elif bc:
                date.set(qual, mod, cal, self.invert_year(start), newyear=ny)
            else:
                date.set(qual, mod, cal, start, newyear=ny)
            return True
        return super().match_modifier(text, cal, ny, qual, bc, date)


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
        "干支年格式",
    )
    # this definition must agree with its "_display_calendar" method

    _bce_str = "%s B.C.E."

    # Override pinyin month names with Chinese characters.
    chinese_lunar = _CHINESE_LUNAR_MONTHS_CN

    def __init__(self, *args: object, **kwargs: object) -> None:
        """
        Initialize and restore Simplified Chinese lunar month names.

        DateDisplay.__init__ overwrites chinese_lunar with the pinyin locale
        default, so we restore the Simplified Chinese character names here.
        """
        super().__init__(*args, **kwargs)
        self.chinese_lunar = _CHINESE_LUNAR_MONTHS_CN

    def _get_localized_year(self, year: str) -> str:
        """Return the year string with the Chinese year suffix 年."""
        return year + "年"

    def _display_calendar(
        self,
        date_val: tuple,
        long_months: tuple,
        short_months: tuple | None = None,
        inflect: str = "",
    ) -> str:
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

    def _display_chinese_lunar(self, date_val: tuple, **kwargs: object) -> str:
        """Display a Chinese Lunar date in 年/月/日 format.

        Format 0: ISO numeric.  Format 1: numeric year + month + day.
        Format 2: sexagenary (干支) year name + month + day.
        """
        month = date_val[1]
        is_leap = month > 100
        actual = month - 100 if is_leap else month
        year = date_val[2]
        day = date_val[0]

        if self.format == 0:
            return self.display_iso(date_val)

        leap_prefix = "闰" if is_leap else ""
        month_str = self.chinese_lunar[actual] if actual else ""

        if self.format == 2:
            year_str = chinese_sexagenary_year(year) + "年"
        else:
            year_str = "%s年" % year

        if actual == 0 and day == 0:
            return year_str
        if day == 0:
            return "%s%s%s" % (year_str, leap_prefix, month_str)
        return "%s%s%s%s日" % (year_str, leap_prefix, month_str, day)

    def display_formatted(self, date: Date) -> str:
        """
        Return a text string representing the date in Simplified Chinese.

        Assembles quality, modifier, and date text according to Chinese word
        order.  Compound quality+modifier cases (e.g. QUAL_ESTIMATED +
        MOD_BEFORE) produce a single fused prefix like "估计早于".
        """
        mod = date.get_modifier()
        cal = date.get_calendar()
        qual = date.get_quality()
        start = date.get_start_date()
        newyear = date.get_new_year()

        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        if start == Date.EMPTY:
            return ""
        if mod == Date.MOD_SPAN:
            return self.dd_span(date)
        if mod == Date.MOD_RANGE:
            return self.dd_range(date)

        text = self.display_cal[cal](start)
        scal = self.format_extras(cal, newyear)

        # Compound quality + directional modifier
        if qual == Date.QUAL_ESTIMATED and mod == Date.MOD_BEFORE:
            return "估计早于%s%s" % (text, scal)
        if qual == Date.QUAL_ESTIMATED and mod == Date.MOD_AFTER:
            return "估计晚于%s%s" % (text, scal)
        if qual == Date.QUAL_CALCULATED and mod == Date.MOD_BEFORE:
            return "推算早于%s%s" % (text, scal)
        if qual == Date.QUAL_CALCULATED and mod == Date.MOD_AFTER:
            return "推算晚于%s%s" % (text, scal)

        # Simple directional modifiers (postfix in Chinese)
        if mod == Date.MOD_BEFORE:
            return "%s以前%s" % (text, scal)
        if mod == Date.MOD_AFTER:
            return "%s以后%s" % (text, scal)

        # Other prefix modifiers (with optional quality prefix)
        if qual == Date.QUAL_ESTIMATED and mod == Date.MOD_ABOUT:
            return "估计为大约%s%s" % (text, scal)
        if qual == Date.QUAL_CALCULATED and mod == Date.MOD_ABOUT:
            return "推算为大约%s%s" % (text, scal)
        if qual == Date.QUAL_ESTIMATED and mod == Date.MOD_FROM:
            return "估计为从%s%s" % (text, scal)
        if qual == Date.QUAL_CALCULATED and mod == Date.MOD_FROM:
            return "推算为从%s%s" % (text, scal)
        if qual == Date.QUAL_ESTIMATED and mod == Date.MOD_TO:
            return "估计为到%s%s" % (text, scal)
        if qual == Date.QUAL_CALCULATED and mod == Date.MOD_TO:
            return "推算为到%s%s" % (text, scal)
        if mod == Date.MOD_ABOUT:
            return "大约%s%s" % (text, scal)
        if mod == Date.MOD_FROM:
            return "从%s%s" % (text, scal)
        if mod == Date.MOD_TO:
            return "到%s%s" % (text, scal)

        # Quality only, no modifier
        if qual == Date.QUAL_ESTIMATED:
            return "估计为%s%s" % (text, scal)
        if qual == Date.QUAL_CALCULATED:
            return "推算为%s%s" % (text, scal)

        return "%s%s" % (text, scal)

    display = display_formatted

    def dd_span(self, date: Date) -> str:
        """Return a span date as [质量前缀]自{start}至{stop}."""
        cal = date.get_calendar()
        qual = date.get_quality()
        scal = self.format_extras(cal, date.get_new_year())
        d1 = self.display_cal[cal](date.get_start_date())
        d2 = self.display_cal[cal](date.get_stop_date())
        if qual == Date.QUAL_ESTIMATED:
            return "估计为自%s至%s%s" % (d1, d2, scal)
        if qual == Date.QUAL_CALCULATED:
            return "推算为自%s至%s%s" % (d1, d2, scal)
        return "自%s至%s%s" % (d1, d2, scal)

    def dd_range(self, date: Date) -> str:
        """Return a range date as [质量前缀]介于{start}与{stop}之间."""
        cal = date.get_calendar()
        qual = date.get_quality()
        scal = self.format_extras(cal, date.get_new_year())
        d1 = self.display_cal[cal](date.get_start_date())
        d2 = self.display_cal[cal](date.get_stop_date())
        if qual == Date.QUAL_ESTIMATED:
            return "估计为介于%s与%s之间%s" % (d1, d2, scal)
        if qual == Date.QUAL_CALCULATED:
            return "推算为介于%s与%s之间%s" % (d1, d2, scal)
        return "介于%s与%s之间%s" % (d1, d2, scal)


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
