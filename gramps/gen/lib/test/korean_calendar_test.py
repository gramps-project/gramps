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

"""Tests for the Korean Lunar (음력) calendar implementation."""

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
    korean_ganji_year,
    korean_lunar_sdn,
    korean_lunar_ymd,
)
from gramps.gen.lib.date import Date
from gramps.gen.datehandler._dateparser import DateParser
from gramps.gen.datehandler._datedisplay import DateDisplay


class TestKoreanLunarSDN(unittest.TestCase):
    """Round-trip and anchor tests for SDN conversions."""

    def test_seollal_2024(self):
        """Seollal (Korean New Year) 2024 = Feb 10, 2024 Gregorian."""
        expected = gregorian_sdn(2024, 2, 10)
        self.assertEqual(korean_lunar_sdn(2024, 1, 1), expected)

    def test_seollal_2025(self):
        """Seollal 2025 = Jan 29, 2025 Gregorian."""
        expected = gregorian_sdn(2025, 1, 29)
        self.assertEqual(korean_lunar_sdn(2025, 1, 1), expected)

    def test_seollal_2023(self):
        """Seollal 2023 = Jan 22, 2023 Gregorian."""
        expected = gregorian_sdn(2023, 1, 22)
        self.assertEqual(korean_lunar_sdn(2023, 1, 1), expected)

    def test_seollal_2022(self):
        """Seollal 2022 = Feb 1, 2022 Gregorian."""
        expected = gregorian_sdn(2022, 2, 1)
        self.assertEqual(korean_lunar_sdn(2022, 1, 1), expected)

    def test_round_trip_regular_months(self):
        """SDN → ymd → SDN round-trip for regular months."""
        for year in [2020, 2021, 2022, 2023, 2024, 2025]:
            for month in range(1, 13):
                for day in [1, 15]:
                    sdn = korean_lunar_sdn(year, month, day)
                    if sdn != 0:
                        back = korean_lunar_ymd(sdn)
                        self.assertEqual(
                            back,
                            (year, month, day),
                            f"Round-trip failed for {year}/{month}/{day}",
                        )

    def test_round_trip_leap_month(self):
        """Round-trip for a leap month (윤4월, year 2020)."""
        sdn = korean_lunar_sdn(2020, 104, 1)
        self.assertNotEqual(sdn, 0)
        self.assertEqual(korean_lunar_ymd(sdn), (2020, 104, 1))

    def test_leap_month_2020_date(self):
        """윤4월 1일 2020 = May 23, 2020 Gregorian."""
        expected = gregorian_sdn(2020, 5, 23)
        self.assertEqual(korean_lunar_sdn(2020, 104, 1), expected)

    def test_out_of_range_low(self):
        """Year below table range returns 0."""
        self.assertEqual(korean_lunar_sdn(399, 1, 1), 0)

    def test_out_of_range_high(self):
        """Year above table range returns 0."""
        self.assertEqual(korean_lunar_sdn(10000, 1, 1), 0)

    def test_out_of_range_sdn_low(self):
        """SDN below table range returns (0, 0, 0)."""
        self.assertEqual(korean_lunar_ymd(0), (0, 0, 0))

    def test_identical_to_chinese(self):
        """Korean and Chinese lunar calendars share the same dates."""
        from gramps.gen.lib.gcalendar import chinese_lunar_sdn

        for year in [1921, 1967, 1985, 2022, 2023, 2024, 2025]:
            kr = korean_lunar_sdn(year, 1, 1)
            cn = chinese_lunar_sdn(year, 1, 1)
            self.assertEqual(
                kr,
                cn,
                f"KR and CN dates should be identical for year {year}",
            )


class TestKoreanGanjiYear(unittest.TestCase):
    """Tests for the 간지 (干支) sexagenary year name."""

    def test_2024_gapjin(self):
        """2024 = 갑진 (Year of the Dragon)."""
        self.assertEqual(korean_ganji_year(2024), "갑진")

    def test_1984_gapja(self):
        """1984 = 갑자 (Year of the Rat)."""
        self.assertEqual(korean_ganji_year(1984), "갑자")

    def test_2025_eulsa(self):
        """2025 = 을사 (Year of the Snake)."""
        self.assertEqual(korean_ganji_year(2025), "을사")

    def test_cycle_length(self):
        """Sexagenary cycle repeats every 60 years."""
        self.assertEqual(korean_ganji_year(2024), korean_ganji_year(2024 - 60))

    def test_all_stems_covered(self):
        """All 10 heavenly stems appear in a 10-year run."""
        stems = {korean_ganji_year(2024 + i)[0] for i in range(10)}
        self.assertEqual(len(stems), 10)

    def test_all_branches_covered(self):
        """All 12 earthly branches appear in a 12-year run."""
        branches = {korean_ganji_year(2024 + i)[1] for i in range(12)}
        self.assertEqual(len(branches), 12)


class TestKoreanLunarDateHandler(unittest.TestCase):
    """Tests for date display and parsing."""

    def setUp(self):
        """Set up displayer and parser."""
        self.dd = DateDisplay()
        self.dp = DateParser()

    def test_display_iso_format(self):
        """ISO format (format=0) shows YYYY-MM-DD (Korean Lunar)."""
        d = Date()
        d.set(calendar=Date.CAL_KOREAN_LUNAR, value=(1, 1, 2024, False))
        result = self.dd.display(d)
        self.assertIn("2024", result)
        self.assertIn("Korean Lunar", result)

    def test_display_leap_month_iso(self):
        """Base DateDisplay uses ISO encoding for Korean Lunar leap months."""
        d = Date()
        d.set(calendar=Date.CAL_KOREAN_LUNAR, value=(1, 104, 2020, False))
        result = self.dd.display(d)
        self.assertIn("104", result)

    def test_parse_iso_numeric(self):
        """ISO numeric YYYY-MM-DD parses correctly."""
        result = self.dp._parse_korean_lunar("2024-1-1")
        self.assertEqual(result, (1, 1, 2024, False))

    def test_parse_iso_year_only(self):
        """ISO year-only parses correctly."""
        result = self.dp._parse_korean_lunar("2024-0-0")
        self.assertEqual(result, (0, 0, 2024, False))

    def test_parse_empty(self):
        """Unrecognized text returns Date.EMPTY."""
        result = self.dp._parse_korean_lunar("not a date")
        self.assertEqual(result, Date.EMPTY)

    def test_cal_constant(self):
        """CAL_KOREAN_LUNAR constant is 8."""
        self.assertEqual(Date.CAL_KOREAN_LUNAR, 8)

    def test_calendars_range(self):
        """CALENDARS range includes Korean Lunar."""
        self.assertIn(Date.CAL_KOREAN_LUNAR, Date.CALENDARS)

    def test_calendar_name(self):
        """Calendar name at index 8 is 'Korean Lunar'."""
        self.assertEqual(Date.calendar_names[8], "Korean Lunar")


if __name__ == "__main__":
    unittest.main()
