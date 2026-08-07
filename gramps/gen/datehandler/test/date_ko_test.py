# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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

"""Tests for the Korean date handler (parser and displayer)."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib.date import Date
from gramps.gen.datehandler._date_ko import DateParserKO, DateDisplayKO


class TestDateParserKO(unittest.TestCase):
    """Tests for DateParserKO — Korean-language date input."""

    def setUp(self):
        """Create parser instance."""
        self.dp = DateParserKO()

    # --- Korean Lunar month names ---

    def test_jeongwol(self):
        """'정월' (month 1) parses correctly."""
        result = self.dp._parse_korean_lunar("정월 1 2024")
        self.assertEqual(result, (1, 1, 2024, False))

    def test_iwol(self):
        """'이월' (month 2) parses correctly."""
        result = self.dp._parse_korean_lunar("이월 15 2023")
        self.assertEqual(result, (15, 2, 2023, False))

    def test_sibirwol(self):
        """'십일월' (month 11) parses correctly."""
        result = self.dp._parse_korean_lunar("십일월 1 2022")
        self.assertEqual(result, (1, 11, 2022, False))

    def test_sibiwol(self):
        """'십이월' (month 12) parses correctly."""
        result = self.dp._parse_korean_lunar("십이월 29 2024")
        self.assertEqual(result, (29, 12, 2024, False))

    def test_numeric_wol(self):
        """'5월' (numeric shorthand) parses correctly."""
        result = self.dp._parse_korean_lunar("5월 10 2025")
        self.assertEqual(result, (10, 5, 2025, False))

    # --- Leap months ---

    def test_yun_sawol(self):
        """'윤사월' (leap month 4) parses to month 104."""
        result = self.dp._parse_korean_lunar("윤사월 1 2020")
        self.assertEqual(result, (1, 104, 2020, False))

    def test_yun_numeric(self):
        """'윤4월' (numeric leap month) parses to month 104."""
        result = self.dp._parse_korean_lunar("윤4월 1 2020")
        self.assertEqual(result, (1, 104, 2020, False))

    def test_yun_sibiwol(self):
        """'윤십이월' (leap month 12) parses to month 112."""
        result = self.dp._parse_korean_lunar("윤십이월 1 2033")
        self.assertEqual(result, (1, 112, 2033, False))

    # --- ISO numeric fallback ---

    def test_iso_numeric(self):
        """ISO numeric YYYY-MM-DD parses correctly."""
        result = self.dp._parse_korean_lunar("2024-1-1")
        self.assertEqual(result, (1, 1, 2024, False))

    def test_iso_year_only(self):
        """ISO year-only parses correctly."""
        result = self.dp._parse_korean_lunar("2024-0-0")
        self.assertEqual(result, (0, 0, 2024, False))

    def test_unrecognized_returns_empty(self):
        """Unrecognized text returns Date.EMPTY."""
        result = self.dp._parse_korean_lunar("not a date")
        self.assertEqual(result, Date.EMPTY)

    # --- calendar_to_int ---

    def test_eumnyeok_in_calendar_to_int(self):
        """'음력' maps to CAL_KOREAN_LUNAR."""
        self.assertEqual(self.dp.calendar_to_int["음력"], Date.CAL_KOREAN_LUNAR)

    def test_haneukmnyeok_in_calendar_to_int(self):
        """'한국음력' maps to CAL_KOREAN_LUNAR."""
        self.assertEqual(self.dp.calendar_to_int["한국음력"], Date.CAL_KOREAN_LUNAR)

    # --- modifier_to_int ---

    def test_modifier_ijeon(self):
        """'이전' is a postfix modifier mapping to MOD_BEFORE."""
        self.assertEqual(self.dp.modifier_after_to_int["이전"], Date.MOD_BEFORE)

    def test_modifier_ihu(self):
        """'이후' is a postfix modifier mapping to MOD_AFTER."""
        self.assertEqual(self.dp.modifier_after_to_int["이후"], Date.MOD_AFTER)

    def test_modifier_yak(self):
        """'약' maps to MOD_ABOUT."""
        self.assertEqual(self.dp.modifier_to_int["약"], Date.MOD_ABOUT)


class TestDateDisplayKO(unittest.TestCase):
    """Tests for DateDisplayKO — Korean date output."""

    def setUp(self):
        """Create displayer instance."""
        self.dd = DateDisplayKO()

    def _make_date(self, year, month, day):
        """Return a Korean Lunar Date."""
        d = Date()
        d.set(calendar=Date.CAL_KOREAN_LUNAR, value=(day, month, year, False))
        return d

    def test_iso_format(self):
        """Format 0 (ISO) returns ISO string."""
        self.dd.format = 0
        d = self._make_date(2024, 1, 1)
        result = self.dd._display_korean_lunar(d.get_dmy(get_slash=True))
        self.assertIn("2024", result)

    def test_numeric_format_year_only(self):
        """Format 1: year-only date shows 'YYYY년'."""
        self.dd.format = 1
        result = self.dd._display_korean_lunar((0, 0, 2024, False))
        self.assertEqual(result, "2024년")

    def test_numeric_format_year_month(self):
        """Format 1: year + month shows month name."""
        self.dd.format = 1
        result = self.dd._display_korean_lunar((0, 1, 2024, False))
        self.assertIn("정월", result)
        self.assertIn("2024", result)

    def test_numeric_format_full_date(self):
        """Format 1: full date includes year, month name, and day."""
        self.dd.format = 1
        result = self.dd._display_korean_lunar((15, 1, 2024, False))
        self.assertIn("정월", result)
        self.assertIn("2024", result)
        self.assertIn("15", result)

    def test_ganji_format(self):
        """Format 2: year is displayed as 간지 name."""
        self.dd.format = 2
        result = self.dd._display_korean_lunar((1, 1, 2024, False))
        self.assertIn("갑진", result)

    def test_leap_month_native_display(self):
        """Leap months are rendered natively with '윤' prefix in format 1."""
        self.dd.format = 1
        result = self.dd._display_korean_lunar((1, 104, 2020, False))
        self.assertIn("윤", result)
        self.assertIn("사월", result)
        self.assertIn("2020", result)

    def test_sibiwol_display(self):
        """Month 12 (십이월) is displayed correctly."""
        self.dd.format = 1
        result = self.dd._display_korean_lunar((1, 12, 2024, False))
        self.assertIn("십이월", result)

    def test_yuwol_display(self):
        """Month 6 (유월) is displayed correctly."""
        self.dd.format = 1
        result = self.dd._display_korean_lunar((1, 6, 2024, False))
        self.assertIn("유월", result)


class TestKoreanModifierParsing(unittest.TestCase):
    """Tests for Korean postfix temporal modifier parsing."""

    def setUp(self):
        """Set up parser and displayer."""
        self.dp = DateParserKO()
        self.dd = DateDisplayKO(format=1)

    def _parse(self, text):
        """Parse text and return a Date."""
        d = Date()
        self.dp.set_date(d, text)
        return d

    def test_before_postfix_with_space(self):
        """'2000년 이전' parses as MOD_BEFORE, year 2000."""
        d = self._parse("2000년 이전")
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 2000)

    def test_after_postfix_with_space(self):
        """'1949년 이후' parses as MOD_AFTER, year 1949."""
        d = self._parse("1949년 이후")
        self.assertEqual(d.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d.get_year(), 1949)

    def test_before_postfix_no_space(self):
        """'2000년이전' (no space) also parses as MOD_BEFORE."""
        d = self._parse("2000년이전")
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 2000)

    def test_about_prefix(self):
        """'약 2000년' parses as MOD_ABOUT, year 2000 (약 stays prefix)."""
        d = self._parse("약 2000년")
        self.assertEqual(d.get_modifier(), Date.MOD_ABOUT)
        self.assertEqual(d.get_year(), 2000)

    def test_english_before_fallback(self):
        """English 'before 2000' still parses as MOD_BEFORE."""
        d = self._parse("before 2000")
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 2000)

    def test_english_after_fallback(self):
        """English 'after 1949' still parses as MOD_AFTER."""
        d = self._parse("after 1949")
        self.assertEqual(d.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d.get_year(), 1949)

    def test_before_display_is_postfix(self):
        """Display of MOD_BEFORE places 이전 after the date."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_BEFORE, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        result = self.dd.display(d)
        self.assertIn("이전", result)
        self.assertTrue(result.endswith("이전"), msg=repr(result))
        self.assertFalse(result.startswith("이전"), msg=repr(result))

    def test_after_display_is_postfix(self):
        """Display of MOD_AFTER places 이후 after the date."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_AFTER, Date.CAL_GREGORIAN, (0, 0, 1949, False))
        result = self.dd.display(d)
        self.assertIn("이후", result)
        self.assertTrue(result.endswith("이후"), msg=repr(result))

    def test_about_display_is_prefix(self):
        """Display of MOD_ABOUT places 약 before the date."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN, (0, 0, 1850, False))
        result = self.dd.display(d)
        self.assertIn("약", result)
        self.assertTrue(result.startswith("약"), msg=repr(result))

    def test_before_roundtrip(self):
        """before-2000 round-trips through display and parse."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_BEFORE, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        text = self.dd.display(d)
        d2 = Date()
        self.dp.set_date(d2, text)
        self.assertEqual(d2.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d2.get_year(), 2000)

    def test_after_roundtrip(self):
        """after-1949 round-trips through display and parse."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_AFTER, Date.CAL_GREGORIAN, (0, 0, 1949, False))
        text = self.dd.display(d)
        d2 = Date()
        self.dp.set_date(d2, text)
        self.assertEqual(d2.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d2.get_year(), 1949)

    def test_about_roundtrip(self):
        """about-1850 round-trips through display and parse."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN, (0, 0, 1850, False))
        text = self.dd.display(d)
        d2 = Date()
        self.dp.set_date(d2, text)
        self.assertEqual(d2.get_modifier(), Date.MOD_ABOUT)
        self.assertEqual(d2.get_year(), 1850)


if __name__ == "__main__":
    unittest.main()
