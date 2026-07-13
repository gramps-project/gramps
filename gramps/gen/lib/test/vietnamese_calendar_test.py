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

"""Tests for the Vietnamese Lunar (Âm Lịch) calendar implementation."""

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
from gramps.gen.lib.gcalendar import (
    gregorian_sdn,
    gregorian_ymd,
    vietnamese_can_chi_year,
    vietnamese_lunar_sdn,
    vietnamese_lunar_ymd,
)
from gramps.gen.lib.date import Date
from gramps.gen.datehandler._dateparser import DateParser
from gramps.gen.datehandler._datedisplay import DateDisplay


class TestVietnameseLunarSDN(unittest.TestCase):
    """Round-trip and anchor tests for SDN conversions."""

    def test_new_year_2024(self):
        """Tết Nguyên Đán 2024 = Feb 10, 2024 Gregorian."""
        expected = gregorian_sdn(2024, 2, 10)
        self.assertEqual(vietnamese_lunar_sdn(2024, 1, 1), expected)

    def test_new_year_2025(self):
        """Tết Nguyên Đán 2025 = Jan 29, 2025 Gregorian."""
        expected = gregorian_sdn(2025, 1, 29)
        self.assertEqual(vietnamese_lunar_sdn(2025, 1, 1), expected)

    def test_new_year_2023(self):
        """Tết Nguyên Đán 2023 = Jan 22, 2023 Gregorian."""
        expected = gregorian_sdn(2023, 1, 22)
        self.assertEqual(vietnamese_lunar_sdn(2023, 1, 1), expected)

    def test_new_year_2022(self):
        """Tết Nguyên Đán 2022 = Feb 1, 2022 Gregorian."""
        expected = gregorian_sdn(2022, 2, 1)
        self.assertEqual(vietnamese_lunar_sdn(2022, 1, 1), expected)

    def test_round_trip_regular_months(self):
        """SDN → ymd → SDN round-trip for regular months."""
        for year in [2020, 2021, 2022, 2023, 2024, 2025]:
            for month in range(1, 13):
                for day in [1, 15]:
                    sdn = vietnamese_lunar_sdn(year, month, day)
                    if sdn != 0:
                        back = vietnamese_lunar_ymd(sdn)
                        self.assertEqual(
                            back,
                            (year, month, day),
                            f"Round-trip failed for {year}/{month}/{day}",
                        )

    def test_round_trip_leap_month(self):
        """Round-trip for a leap month (Nhuận tháng 4, year 2020)."""
        sdn = vietnamese_lunar_sdn(2020, 104, 1)
        self.assertNotEqual(sdn, 0)
        self.assertEqual(vietnamese_lunar_ymd(sdn), (2020, 104, 1))

    def test_leap_month_2020_date(self):
        """Nhuận tháng 4, ngày 1, 2020 = May 23, 2020 Gregorian."""
        expected = gregorian_sdn(2020, 5, 23)
        self.assertEqual(vietnamese_lunar_sdn(2020, 104, 1), expected)

    def test_leap_month_2023(self):
        """Nhuận tháng 2, ngày 1, 2023 starts on March 22, 2023."""
        expected = gregorian_sdn(2023, 3, 22)
        self.assertEqual(vietnamese_lunar_sdn(2023, 102, 1), expected)

    def test_out_of_range_low(self):
        """Year below table range returns 0."""
        self.assertEqual(vietnamese_lunar_sdn(399, 1, 1), 0)

    def test_out_of_range_high(self):
        """Year above table range returns 0."""
        self.assertEqual(vietnamese_lunar_sdn(10000, 1, 1), 0)

    def test_out_of_range_sdn_low(self):
        """SDN below table range returns (0, 0, 0)."""
        self.assertEqual(vietnamese_lunar_ymd(0), (0, 0, 0))

    def test_ymd_roundtrip_large_sdn(self):
        """SDN for far-future year round-trips correctly."""
        sdn = vietnamese_lunar_sdn(9999, 12, 29)
        self.assertNotEqual(sdn, 0)
        year, month, day = vietnamese_lunar_ymd(sdn)
        self.assertEqual(year, 9999)
        self.assertEqual(month, 12)
        self.assertEqual(day, 29)

    def test_identical_to_chinese(self):
        """Vietnamese and Chinese lunar calendars share the same dates.

        The only differences are the display names.
        """
        from gramps.gen.lib.gcalendar import chinese_lunar_sdn

        for year in [1921, 1967, 1985, 2022, 2023, 2024, 2025]:
            vn = vietnamese_lunar_sdn(year, 1, 1)
            cn = chinese_lunar_sdn(year, 1, 1)
            self.assertEqual(
                vn,
                cn,
                f"VN and CN dates should be identical for year {year}",
            )


class TestVietnameseCanChi(unittest.TestCase):
    """Tests for the Can-Chi (sexagenary) year name."""

    def test_2024_giap_thin(self):
        """2024 = Giáp Thìn (year of the Dragon)."""
        self.assertEqual(vietnamese_can_chi_year(2024), "Giáp Thìn")

    def test_1984_giap_ty(self):
        """1984 = Giáp Tý (year of the Rat)."""
        self.assertEqual(vietnamese_can_chi_year(1984), "Giáp Tý")

    def test_2025_at_ty(self):
        """2025 = Ất Tỵ (year of the Snake)."""
        self.assertEqual(vietnamese_can_chi_year(2025), "Ất Tỵ")

    def test_cycle_length(self):
        """Sexagenary cycle repeats every 60 years."""
        self.assertEqual(
            vietnamese_can_chi_year(2024), vietnamese_can_chi_year(2024 - 60)
        )


class TestVietnameseDateHandler(unittest.TestCase):
    """Tests for date display and parsing."""

    def setUp(self):
        """Set up displayer and parser."""
        self.dd = DateDisplay()
        self.dp = DateParser()

    def test_display_iso_format(self):
        """ISO format (format=0) shows YYYY-MM-DD (Vietnamese Lunar)."""
        d = Date()
        d.set(calendar=Date.CAL_VIETNAMESE_LUNAR, value=(1, 1, 2024, False))
        result = self.dd.display(d)
        self.assertIn("2024", result)
        self.assertIn("Vietnamese Lunar", result)

    def test_display_non_iso_format(self):
        """Non-ISO format delegates to _display_calendar (not display_iso)."""
        d = Date()
        d.set(calendar=Date.CAL_VIETNAMESE_LUNAR, value=(1, 1, 2024, False))
        # With format != 0, _display_vietnamese_lunar calls _display_calendar
        old_format = self.dd.format
        self.dd.format = 1
        result = self.dd._display_vietnamese_lunar(d.get_dmy(get_slash=True))
        self.dd.format = old_format
        # Should produce a string without "ISO" — just verify it doesn't raise
        self.assertIsInstance(result, str)

    def test_display_leap_month_iso(self):
        """Leap months always use ISO encoding in display."""
        d = Date()
        d.set(calendar=Date.CAL_VIETNAMESE_LUNAR, value=(1, 104, 2020, False))
        result = self.dd.display(d)
        self.assertIn("104", result)

    def test_parse_iso_numeric(self):
        """ISO numeric YYYY-MM-DD parses correctly."""
        result = self.dp._parse_vietnamese_lunar("2024-1-1")
        self.assertEqual(result, (1, 1, 2024, False))

    def test_parse_month_name(self):
        """Vietnamese month name parses correctly."""
        result = self.dp._parse_vietnamese_lunar("Tháng Giêng 1 2024")
        self.assertEqual(result, (1, 1, 2024, False))

    def test_parse_empty(self):
        """Unrecognized text returns Date.EMPTY."""
        result = self.dp._parse_vietnamese_lunar("not a date")
        self.assertEqual(result, Date.EMPTY)

    def test_cal_constant(self):
        """CAL_VIETNAMESE_LUNAR constant is 8."""
        self.assertEqual(Date.CAL_VIETNAMESE_LUNAR, 8)

    def test_calendars_range(self):
        """CALENDARS range includes Vietnamese Lunar."""
        self.assertIn(Date.CAL_VIETNAMESE_LUNAR, Date.CALENDARS)

    def test_calendar_name(self):
        """Calendar name at index 8 is 'Vietnamese Lunar'."""
        self.assertEqual(Date.calendar_names[8], "Vietnamese Lunar")


if __name__ == "__main__":
    unittest.main()
