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

"""Tests for Japanese date parsing and display (including Japanese Imperial 和暦)."""

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
from gramps.gen.datehandler._dateparser import DateParser
from gramps.gen.datehandler._datedisplay import DateDisplay
from gramps.gen.datehandler._date_ja import DateParserJA, DateDisplayJA


class TestJapaneseImperialParsing(unittest.TestCase):
    """Tests for DateParserJA era-name parsing."""

    def setUp(self):
        """Set up the JA parser."""
        self.dp = DateParserJA()

    def _parse_ji(self, text):
        """Return (day, month, greg_year) for a Japanese Imperial parse."""
        d = self.dp.parse(text)
        self.assertEqual(d.get_calendar(), Date.CAL_JAPANESE_IMPERIAL)
        return d.get_day(), d.get_month(), d.get_year()

    def test_showa_40_full(self):
        """昭和40年5月15日 → (day=15, month=5, year=1965)."""
        self.assertEqual(self._parse_ji("昭和40年5月15日"), (15, 5, 1965))

    def test_reiwa_6_year_only(self):
        """令和6年 (year-only) → (day=0, month=0, year=2024)."""
        self.assertEqual(self._parse_ji("令和6年"), (0, 0, 2024))

    def test_meiji_gen_first_year(self):
        """明治元年 (year 1 with 元) → year 1868."""
        day, month, year = self._parse_ji("明治元年")
        self.assertEqual(year, 1868)

    def test_meiji_year_month(self):
        """明治45年7月 → (day=0, month=7, year=1912)."""
        self.assertEqual(self._parse_ji("明治45年7月"), (0, 7, 1912))

    def test_ansei_5_pre_meiji(self):
        """安政5年8月19日 (pre-1873 lunisolar) → stored Gregorian year 1858."""
        day, month, year = self._parse_ji("安政5年8月19日")
        self.assertEqual(year, 1858)
        self.assertEqual(month, 8)
        self.assertEqual(day, 19)

    def test_keio_1(self):
        """慶応1年 → year 1865."""
        _, _, year = self._parse_ji("慶応1年")
        self.assertEqual(year, 1865)

    def test_heisei_1(self):
        """平成1年 → year 1989."""
        _, _, year = self._parse_ji("平成1年")
        self.assertEqual(year, 1989)

    def test_non_era_string_falls_through(self):
        """Non-era strings are not parsed as Japanese Imperial."""
        d = self.dp.parse("1999-12-31")
        self.assertNotEqual(d.get_calendar(), Date.CAL_JAPANESE_IMPERIAL)


class TestJapaneseImperialDisplay(unittest.TestCase):
    """Tests for DateDisplayJA Japanese Imperial rendering."""

    def _make_ji_date(self, year, month=0, day=0):
        """Build a CAL_JAPANESE_IMPERIAL Date with the given stored values."""
        d = Date()
        d.set(
            modifier=Date.MOD_NONE,
            calendar=Date.CAL_JAPANESE_IMPERIAL,
            value=(day, month, year, False),
        )
        return d

    def setUp(self):
        """Set up JA displayer in era format (format=4)."""
        self.dd = DateDisplayJA()
        self.dd.format = 4

    def test_showa_40_display(self):
        """Stored year=1965, month=5, day=15 → '昭和40年5月15日'."""
        d = self._make_ji_date(1965, 5, 15)
        result = self.dd._display_japanese_imperial(d.get_start_date())
        self.assertIn("昭和", result)
        self.assertIn("40", result)

    def test_meiji_year_1_displays_gen(self):
        """Meiji 1 displays as 元 (not '1') in year position."""
        d = self._make_ji_date(1868, 9, 8)
        result = self.dd._display_japanese_imperial(d.get_start_date())
        self.assertIn("明治", result)
        self.assertIn("元", result)

    def test_reiwa_year_only(self):
        """Year-only Reiwa 6 (2024) is displayed correctly."""
        d = self._make_ji_date(2024)
        result = self.dd._display_japanese_imperial(d.get_start_date())
        self.assertIn("令和", result)
        self.assertIn("6", result)

    def test_traditional_months_format5(self):
        """Format 5 uses traditional month names (e.g. 皐月 for month 5)."""
        self.dd.format = 5
        d = self._make_ji_date(1965, 5, 15)
        result = self.dd._display_japanese_imperial(d.get_start_date())
        self.assertIn("昭和", result)
        self.assertIn("皐月", result)

    def test_pre_meiji_display(self):
        """Pre-1873 date (安政5年8月19日) displays with correct era."""
        d = self._make_ji_date(1858, 8, 19)
        result = self.dd._display_japanese_imperial(d.get_start_date())
        self.assertIn("安政", result)
        self.assertIn("5", result)


class TestBaseDisplayJapaneseImperial(unittest.TestCase):
    """Tests for the base DateDisplay fallback rendering.

    The base DateDisplay uses format=0 (ISO) by default, so Japanese Imperial
    dates are rendered as YYYY-MM-DD (Japanese Imperial).  Era-name rendering
    is provided by DateDisplayJA (the JA locale handler).
    """

    def test_base_display_modern_date_iso(self):
        """Base DateDisplay at format=0 renders Japanese Imperial as ISO + label."""
        d = Date()
        d.set(
            modifier=Date.MOD_NONE,
            calendar=Date.CAL_JAPANESE_IMPERIAL,
            value=(15, 5, 1965, False),
        )
        dd = DateDisplay()
        result = dd.display(d)
        self.assertIn("1965", result)
        self.assertIn("Japanese Imperial", result)

    def test_base_display_era_format(self):
        """Base DateDisplay with format=1 renders era + numbers."""
        d = Date()
        d.set(
            modifier=Date.MOD_NONE,
            calendar=Date.CAL_JAPANESE_IMPERIAL,
            value=(15, 5, 1965, False),
        )
        dd = DateDisplay()
        dd.format = 1  # any non-ISO format triggers era rendering
        result = dd._display_japanese_imperial(d.get_start_date())
        self.assertIn("昭和", result)

    def test_base_display_year_only(self):
        """A year-only Japanese Imperial date displays without crashing."""
        d = Date()
        d.set(
            modifier=Date.MOD_NONE,
            calendar=Date.CAL_JAPANESE_IMPERIAL,
            value=(0, 0, 1965, False),
        )
        dd = DateDisplay()
        dd.format = 1
        result = dd._display_japanese_imperial(d.get_start_date())
        self.assertIsInstance(result, str)
        self.assertIn("昭和", result)


class TestJapaneseImperialParseDisplayRoundtrip(unittest.TestCase):
    """Parse → display → parse round-trips."""

    def setUp(self):
        """Set up JA parser and displayer."""
        self.dp = DateParserJA()
        self.dd = DateDisplayJA()
        self.dd.format = 4

    def test_roundtrip_showa(self):
        """昭和40年5月15日 round-trips through parse → display → parse."""
        original = "昭和40年5月15日"
        d1 = self.dp.parse(original)
        displayed = self.dd.display(d1)
        d2 = self.dp.parse(displayed)
        self.assertEqual(d1.get_year(), d2.get_year())
        self.assertEqual(d1.get_month(), d2.get_month())
        self.assertEqual(d1.get_day(), d2.get_day())
        self.assertEqual(d1.get_calendar(), d2.get_calendar())

    def test_roundtrip_reiwa_year_only(self):
        """令和6年 round-trips."""
        d1 = self.dp.parse("令和6年")
        displayed = self.dd.display(d1)
        d2 = self.dp.parse(displayed)
        self.assertEqual(d1.get_year(), d2.get_year())
        self.assertEqual(d1.get_calendar(), d2.get_calendar())


if __name__ == "__main__":
    unittest.main()
