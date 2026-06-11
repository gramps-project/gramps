#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024  Doug Blank
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

"""Tests for the Chinese Lunar Calendar SDN conversion functions."""

import unittest

from ..gcalendar import (
    chinese_lunar_sdn,
    chinese_lunar_ymd,
    gregorian_sdn,
    gregorian_ymd,
)


class TestChineseLunarConversion(unittest.TestCase):
    """Round-trip and known-date tests for Chinese Lunar <-> SDN."""

    # Known correspondences: (lunar_year, lunar_month, lunar_day, greg_year, greg_month, greg_day)
    # Sources: published Chinese calendar tables and lunardate library.
    KNOWN_DATES = [
        # Chinese New Year dates (always lunar 1/1)
        (1900, 1, 1, 1900, 1, 31),
        (1949, 1, 1, 1949, 1, 29),
        (1976, 1, 1, 1976, 1, 31),
        (2000, 1, 1, 2000, 2, 5),
        (2023, 1, 1, 2023, 1, 22),
        (2024, 1, 1, 2024, 2, 10),
        (2025, 1, 1, 2025, 1, 29),
        # Mid-year dates
        (2008, 8, 8, 2008, 9, 7),  # 8th day, 8th lunar month 2008
        (1976, 9, 1, 1976, 10, 23),  # 1st day of 9th lunar month 1976
    ]

    # Leap month tests: verify encoding 101-112 for leap months.
    LEAP_DATES = [
        # (lunar_year, leap_month_encoded, lunar_day, greg_year, greg_month, greg_day)
        # 1976 leap 8th month (闰八月): day 8 = 1976-10-01
        (1976, 108, 8, 1976, 10, 1),
        # 2023 leap 2nd month (闰二月): starts 2023-03-22
        (2023, 102, 1, 2023, 3, 22),
        (2023, 102, 15, 2023, 4, 5),
    ]

    def test_known_dates_sdn(self):
        """Chinese Lunar -> SDN matches expected Gregorian date."""
        for ly, lm, ld, gy, gm, gd in self.KNOWN_DATES:
            with self.subTest(lunar=(ly, lm, ld)):
                expected_sdn = gregorian_sdn(gy, gm, gd)
                got_sdn = chinese_lunar_sdn(ly, lm, ld)
                self.assertEqual(
                    got_sdn,
                    expected_sdn,
                    f"lunar {ly}/{lm}/{ld} -> SDN {got_sdn}, "
                    f"expected {expected_sdn} (Gregorian {gy}-{gm:02d}-{gd:02d})",
                )

    def test_known_dates_ymd(self):
        """SDN -> Chinese Lunar matches expected lunar date."""
        for ly, lm, ld, gy, gm, gd in self.KNOWN_DATES:
            with self.subTest(gregorian=(gy, gm, gd)):
                sdn = gregorian_sdn(gy, gm, gd)
                got = chinese_lunar_ymd(sdn)
                self.assertEqual(
                    got,
                    (ly, lm, ld),
                    f"SDN for {gy}-{gm:02d}-{gd:02d} -> lunar {got}, "
                    f"expected ({ly}, {lm}, {ld})",
                )

    def test_leap_month_sdn(self):
        """Leap month dates convert to the correct SDN."""
        for ly, lm, ld, gy, gm, gd in self.LEAP_DATES:
            with self.subTest(lunar=(ly, lm, ld)):
                expected_sdn = gregorian_sdn(gy, gm, gd)
                got_sdn = chinese_lunar_sdn(ly, lm, ld)
                self.assertEqual(
                    got_sdn,
                    expected_sdn,
                    f"leap lunar {ly}/{lm}/{ld} -> SDN {got_sdn}, "
                    f"expected {expected_sdn} (Gregorian {gy}-{gm:02d}-{gd:02d})",
                )

    def test_leap_month_ymd(self):
        """SDN within a leap month decodes with the leap flag."""
        for ly, lm, ld, gy, gm, gd in self.LEAP_DATES:
            with self.subTest(gregorian=(gy, gm, gd)):
                sdn = gregorian_sdn(gy, gm, gd)
                got = chinese_lunar_ymd(sdn)
                self.assertEqual(
                    got,
                    (ly, lm, ld),
                    f"SDN for {gy}-{gm:02d}-{gd:02d} -> {got}, "
                    f"expected ({ly}, {lm}, {ld})",
                )

    def test_round_trip_sdn_to_ymd(self):
        """Every day in a sample range survives SDN -> ymd -> SDN round-trip."""
        start_sdn = gregorian_sdn(2020, 1, 1)
        end_sdn = gregorian_sdn(2026, 1, 1)
        for sdn in range(start_sdn, end_sdn):
            ymd = chinese_lunar_ymd(sdn)
            self.assertNotEqual(ymd, (0, 0, 0), f"SDN {sdn} returned (0,0,0)")
            recovered = chinese_lunar_sdn(*ymd)
            self.assertEqual(
                recovered,
                sdn,
                f"Round-trip failed for SDN {sdn}: ymd={ymd}, recovered SDN={recovered}",
            )

    def test_round_trip_ymd_to_sdn(self):
        """Lunar ymd -> SDN -> ymd round-trip for a sample of dates."""
        # Walk through year 2023 (has a leap 2nd month) day by day.
        year = 2023
        sdn = chinese_lunar_sdn(year, 1, 1)
        end = chinese_lunar_sdn(year + 1, 1, 1)
        while sdn < end:
            ymd = chinese_lunar_ymd(sdn)
            self.assertEqual(ymd[0], year)
            recovered = chinese_lunar_sdn(*ymd)
            self.assertEqual(recovered, sdn, f"Round-trip at SDN {sdn}: {ymd}")
            sdn += 1

    def test_out_of_range_returns_zero(self):
        """Dates outside 1900-2099 return 0 / (0,0,0)."""
        self.assertEqual(chinese_lunar_sdn(1899, 1, 1), 0)
        self.assertEqual(chinese_lunar_sdn(2100, 1, 1), 0)
        too_early = gregorian_sdn(1899, 1, 1)
        too_late = gregorian_sdn(2101, 1, 1)
        self.assertEqual(chinese_lunar_ymd(too_early), (0, 0, 0))
        self.assertEqual(chinese_lunar_ymd(too_late), (0, 0, 0))

    def test_new_year_is_month1_day1(self):
        """Chinese New Year always maps to month 1, day 1."""
        new_year_gregorian = [
            (2021, 2, 12),
            (2022, 2, 1),
            (2023, 1, 22),
            (2024, 2, 10),
            (2025, 1, 29),
        ]
        for gy, gm, gd in new_year_gregorian:
            with self.subTest(gregorian=(gy, gm, gd)):
                sdn = gregorian_sdn(gy, gm, gd)
                year, month, day = chinese_lunar_ymd(sdn)
                self.assertEqual(month, 1, f"{gy}-{gm:02d}-{gd:02d} month={month}")
                self.assertEqual(day, 1, f"{gy}-{gm:02d}-{gd:02d} day={day}")


if __name__ == "__main__":
    unittest.main()
