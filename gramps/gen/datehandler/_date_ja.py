# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2014       Mathieu MD <mathieu.md@gmail.com>
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
Japanese-specific classes for parsing and displaying dates.
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
from ..lib.gcalendar import (
    JAPANESE_ERAS,
    gregorian_to_japanese_era,
    japanese_era_to_gregorian,
    japanese_imperial_sdn,
    gregorian_ymd,
)
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler

# Traditional Japanese lunisolar month names (和風月名), index 1–12.
_JA_TRADITIONAL_MONTHS = (
    "",
    "睦月",   # Mutsuki   (month 1)
    "如月",   # Kisaragi  (month 2)
    "弥生",   # Yayoi     (month 3)
    "卯月",   # Uzuki     (month 4)
    "皐月",   # Satsuki   (month 5)
    "水無月",  # Minazuki  (month 6)
    "文月",   # Fumizuki  (month 7)
    "葉月",   # Hazuki    (month 8)
    "長月",   # Nagatsuki (month 9)
    "神無月",  # Kannazuki (month 10)
    "霜月",   # Shimotsuki (month 11)
    "師走",   # Shiwasu   (month 12)
)

# Build a regex alternation of all era kanji names, longest-first to avoid
# prefix ambiguity (e.g. 天正 must be tried before 天).
_ERA_KANJI_LIST = [e[0] for e in JAPANESE_ERAS]
_ERA_ROMAJI_LIST = [e[1].lower() for e in JAPANESE_ERAS]
# Sort longest-first for the regex so longer era names match before shorter ones.
_ERA_KANJI_PATTERN = "|".join(
    sorted(set(_ERA_KANJI_LIST), key=len, reverse=True)
)
_ERA_ROMAJI_PATTERN = "|".join(
    sorted(set(_ERA_ROMAJI_LIST), key=len, reverse=True)
)

# Matches:  <era_kanji><year>年[<month>月[<day>日]]
# Also accepts "元" (= year 1) in place of a digit.
_ERA_NUMERIC_RE = re.compile(
    r"(?P<era>%s)\s*(?P<ey>元|\d+)年\s*(?:(?P<m>\d+)月\s*(?:(?P<d>\d+)日)?)?\s*$"
    % _ERA_KANJI_PATTERN,
    re.UNICODE,
)

# Same pattern but for ASCII romaji input (case-insensitive).
_ERA_ROMAJI_RE = re.compile(
    r"(?P<era>%s)\s*(?P<ey>\d+)\s*$" % _ERA_ROMAJI_PATTERN,
    re.IGNORECASE,
)


# ------------------------------------------------------------
#
# DateParserJA
#
# ------------------------------------------------------------
class DateParserJA(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    # modifiers after the date
    modifier_after_to_int = {
        "以前": Date.MOD_BEFORE,
        "以降": Date.MOD_AFTER,
        "頃": Date.MOD_ABOUT,
        "ごろ": Date.MOD_ABOUT,
        "from": Date.MOD_FROM,
        "to": Date.MOD_TO,
    }

    month_to_int = DateParser.month_to_int

    quality_to_int = {
        "およそ": Date.QUAL_ESTIMATED,
        "ごろ": Date.QUAL_ESTIMATED,
        "位": Date.QUAL_ESTIMATED,
        "の見積り": Date.QUAL_ESTIMATED,
        "計算上": Date.QUAL_CALCULATED,
    }

    bce = ["紀元前", "BC"] + DateParser.bce

    def init_strings(self):
        """
        Compile regular expressions for Japanese date parsing, including
        era-name (元号) patterns for Japanese Imperial (和暦) dates.
        """
        DateParser.init_strings(self)

        DateParser.calendar_to_int.update(
            {
                "グレゴリオ暦": Date.CAL_GREGORIAN,
                "g": Date.CAL_GREGORIAN,
                "ユリウス暦": Date.CAL_JULIAN,
                "j": Date.CAL_JULIAN,
                "ユダヤ暦": Date.CAL_HEBREW,
                "h": Date.CAL_HEBREW,
                "ヒジュラ暦": Date.CAL_ISLAMIC,
                "i": Date.CAL_ISLAMIC,
                "フランス革命暦": Date.CAL_FRENCH,
                "共和暦": Date.CAL_FRENCH,
                "f": Date.CAL_FRENCH,
                "イラン暦": Date.CAL_PERSIAN,
                "p": Date.CAL_PERSIAN,
                "スウェーデン暦": Date.CAL_SWEDISH,
                "s": Date.CAL_SWEDISH,
                "和暦": Date.CAL_JAPANESE_IMPERIAL,
                "元号": Date.CAL_JAPANESE_IMPERIAL,
                "ji": Date.CAL_JAPANESE_IMPERIAL,
            }
        )

        DateParser.month_to_int.update(
            {
                "一月": 1,
                "ichigatsu": 1,
                "睦月": 1,
                "mutsuki": 1,
                "二月": 2,
                "nigatsu": 2,
                "如月": 2,
                "kisaragi": 2,
                "衣更着": 2,
                "kinusaragi": 2,
                "三月": 3,
                "sangatsu": 3,
                "弥生": 3,
                "yayoi": 3,
                "四月": 4,
                "shigatsu": 4,
                "卯月": 4,
                "uzuki": 4,
                "五月": 5,
                "gogatsu": 5,
                "皐月": 5,
                "satsuki": 5,
                "早苗月": 5,
                "sanaetsuki": 5,
                "六月": 6,
                "rokugatsu": 6,
                "水無月": 6,
                "minazuki": 6,
                "七月": 7,
                "shichigatsu": 7,
                "文月": 7,
                "fumizuki": 7,
                "八月": 8,
                "hachigatsu": 8,
                "葉月": 8,
                "hazuki": 8,
                "九月": 9,
                "kugatsu": 9,
                "長月": 9,
                "nagatsuki": 9,
                "十月": 10,
                "jugatsu": 10,
                "jūgatsu": 10,
                "juugatsu": 10,
                "神無月": 10,
                "kannazuki": 10,
                "kaminazuki": 10,
                "神有月": 10,
                "神在月": 10,
                "kamiarizuki": 10,
                "十一月": 11,
                "juichigatsu": 11,
                "jūichigatsu": 11,
                "juuichigatsu": 11,
                "霜月": 11,
                "shimotsuki": 11,
                "十二月": 12,
                "junigatsu": 12,
                "jūnigatsu": 12,
                "juunigatsu": 12,
                "師走": 12,
                "shiwasu": 12,
            }
        )

        _span_1 = ["から", "~", "〜"]
        _span_2 = ["まで"]
        _range_1 = ["から", "と", "~", "〜"]
        _range_2 = ["までの間", "の間"]
        self._span = re.compile(
            r"(?P<start>.+)(%s)(?P<stop>.+)(%s)"
            % ("|".join(_span_1), "|".join(_span_2)),
            re.IGNORECASE,
        )
        self._range = re.compile(
            r"(?P<start>.+)(%s)(?P<stop>.+)(%s)"
            % ("|".join(_range_1), "|".join(_range_2)),
            re.IGNORECASE,
        )
        self._numeric = re.compile(r"((\d+)年\s*)?((\d+)月\s*)?(\d+)?日?\s*$")
        self._cal = re.compile(r"(.*?)\s*\(%s\)\s*(.*)" % self._cal_str, re.IGNORECASE)
        self._qual = re.compile(r"(.*?)\s*%s\s*(.*)" % self._qual_str, re.IGNORECASE)

    def _parse_japanese_imperial_era(self, text: str) -> tuple | None:
        """
        Parse an era-format Japanese Imperial date string.

        Accepts kanji era names (昭和40年5月15日) with optional 元 for year 1.
        Returns (day, month, gregorian_year, False) on success, None on failure.
        """
        m = _ERA_NUMERIC_RE.match(text.strip())
        if not m:
            return None
        era_kanji = m.group("era")
        ey_str = m.group("ey")
        year_in_era = 1 if ey_str == "元" else int(ey_str)
        greg_year = japanese_era_to_gregorian(era_kanji, year_in_era)
        if greg_year is None:
            return None
        month = int(m.group("m")) if m.group("m") else 0
        day = int(m.group("d")) if m.group("d") else 0
        return (day, month, greg_year, False)

    def parse(self, text: str) -> Date:
        """
        Parse a date string, trying era-name patterns before falling back
        to the base parser.  The calendar-name suffix added by display()
        (e.g. " (Japanese Imperial)") is stripped before the era regex is
        tried so that round-trips through display() → parse() work.
        """
        stripped = text.strip()
        # Strip trailing "(Japanese Imperial)" label if present.
        clean, _cal = self.match_calendar(stripped, Date.CAL_GREGORIAN)
        result = self._parse_japanese_imperial_era(clean.strip())
        if result is not None:
            d = Date()
            d.set(
                modifier=Date.MOD_NONE,
                calendar=Date.CAL_JAPANESE_IMPERIAL,
                value=result,
                text=text,
            )
            return d
        return DateParser.parse(self, text)


# ------------------------------------------------------------
#
# DateDisplayJA
#
# ------------------------------------------------------------
class DateDisplayJA(DateDisplay):
    """
    Japanese language date display class.
    """

    def formats_changed(self):
        """Allow overriding so a subclass can modify."""

        example = self.dhformat
        example = example.replace("%d", "31")
        example = example.replace("%m", "12")
        example = example.replace("%Y", "1999")

        # This definition must agree with its "_display_gregorian" method.
        self.formats = (
            "YYYY-MM-DD (ISO)",                        # 0
            "システムデフォールト (" + example + ")",  # 1
            "1999年12月31日",                          # 2
            "1999年十二月31日",                        # 3
            "昭和40年5月15日",                         # 4  Japanese Imperial era
            "昭和40年皐月15日",                        # 5  era + traditional month
        )

    def _display_gregorian(self, date_val, **kwargs):
        """
        Display a Gregorian calendar date in Japanese formats.
        """
        year = self._slash_year(date_val[2], date_val[3])
        if self.format == 0:
            return self.display_iso(date_val)

        elif self.format == 1:
            if date_val[2] < 0 or date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self.dhformat.replace("%m", str(date_val[1]))
                    if date_val[0] == 0:
                        i_day = value.find("%d")
                        value = value.replace(value[i_day : i_day + 3], "")
                    value = value.replace("%d", str(date_val[0]))
                    value = value.replace("%Y", str(date_val[2]))

        elif self.format == 2:
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s年" % year
                else:
                    value = "%s年%s" % (year, self.short_months[date_val[1]])
            else:
                value = "%s年%s%s日" % (
                    year,
                    self.short_months[date_val[1]],
                    date_val[0],
                )

        elif self.format == 3:
            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = "%s年" % year
                else:
                    value = "%s年%s" % (year, self.long_months[date_val[1]])
            else:
                value = "%s年%s%s日" % (
                    year,
                    self.long_months[date_val[1]],
                    date_val[0],
                )

        else:
            return self.display_iso(date_val)

        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    def _display_japanese_imperial(self, date_val, **kwargs):
        """
        Display a Japanese Imperial (和暦) date in era-name format.

        Formats 0–3 fall back to the Gregorian display (ISO or numeric).
        Formats 4 and 5 render the era name + year-within-era + month + day.
        Format 4 uses numeric months; format 5 uses traditional month names
        (和風月名) for pre-1873 lunisolar dates.
        """
        day, month, year = date_val[0], date_val[1], date_val[2]

        if self.format in (0, 1, 2, 3):
            # Derive Gregorian date via SDN for the numeric display.
            # For year/month-only dates use January 1 as the proxy.
            if day == 0 or month == 0:
                g_year, g_month, g_day = year, 1, 1
            else:
                sdn = japanese_imperial_sdn(year, month, day)
                if not sdn:
                    return self.display_iso(date_val)
                g_year, g_month, g_day = gregorian_ymd(sdn)
            return self._display_gregorian(
                (g_day, g_month, g_year, date_val[3]), **kwargs
            )

        # Formats 4 and 5: era rendering.
        if day == 0 or month == 0:
            if year >= 1873:
                era_info = gregorian_to_japanese_era(year, 1, 1)
            else:
                from ..lib.gcalendar import chinese_lunar_sdn

                proxy_sdn = chinese_lunar_sdn(year, 6, 1)
                if not proxy_sdn:
                    return self.display_iso(date_val)
                pg_year, pg_month, pg_day = gregorian_ymd(proxy_sdn)
                era_info = gregorian_to_japanese_era(pg_year, pg_month, pg_day)
        else:
            sdn = japanese_imperial_sdn(year, month, day)
            if not sdn:
                return self.display_iso(date_val)
            g_year, g_month, g_day = gregorian_ymd(sdn)
            era_info = gregorian_to_japanese_era(g_year, g_month, g_day)
        if era_info is None:
            return self.display_iso(date_val)
        era_kanji, year_in_era = era_info
        return self._format_japanese_imperial(era_kanji, year_in_era, month, day)

    def _format_japanese_imperial(
        self, era: str, year_in_era: int, month: int, day: int
    ) -> str:
        """
        Render a Japanese Imperial date in kanji format.

        Format 5 uses traditional lunisolar month names (和風月名) for the
        month; format 4 (and all other formats) uses numeric months.
        """
        era_year = "元" if year_in_era == 1 else str(year_in_era)

        if day == 0 and month == 0:
            return "%s%s年" % (era, era_year)

        if self.format == 5 and 1 <= month <= 12:
            month_str = _JA_TRADITIONAL_MONTHS[month]
        else:
            month_str = "%d月" % month

        if day == 0:
            return "%s%s年%s" % (era, era_year, month_str)
        return "%s%s年%s%d日" % (era, era_year, month_str, day)

    display = DateDisplay.display_formatted


# -------------------------------------------------------------------------
#
# Register classes
#
# -------------------------------------------------------------------------

register_datehandler(
    ("ja_JP", "ja", "japanese", "Japanese", ("%Y年%m月%d日",)),
    DateParserJA,
    DateDisplayJA,
)
