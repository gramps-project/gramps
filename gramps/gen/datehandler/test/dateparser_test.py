# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Vassilii Khachaturov
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
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Deeper testing of some DateParser internals.
"""

import unittest

from ...utils.grampslocale import GrampsLocale
from ...lib.date import Date


class DateParserTest(unittest.TestCase):
    def setUp(self):
        from .._dateparser import DateParser

        self.parser = DateParser()
        self.parser_RU = GrampsLocale(lang="ru").date_parser

    def assert_map_key_val(self, m, k, v):
        try:
            self.assertEqual(m[k], v)
        except KeyError:
            self.assertTrue(False, list(m.items()))

    def test_month_to_int_jan_is_1(self):
        self.assert_map_key_val(self.parser.month_to_int, "jan", 1)

    def test_prefix_table_for_RU_built(self):
        self.assertIn("ru_RU", self.parser._langs)

    def test_month_to_int_septem_RU_is_9(self):
        self.assert_map_key_val(self.parser.month_to_int, "сентяб", 9)

    def test_hebrew_to_int_av_is_12(self):
        self.assert_map_key_val(self.parser.hebrew_to_int, "av", 12)
        self.assert_map_key_val(self.parser.hebrew_to_int, "ав", 12)  # RU

    def test_french_to_int_thermidor_is_11(self):
        self.assert_map_key_val(self.parser.french_to_int, "thermidor", 11)
        self.assert_map_key_val(self.parser.french_to_int, "термидор", 11)  # RU

    def test_islamic_to_int_ramadan_is_9(self):
        self.assert_map_key_val(self.parser.islamic_to_int, "ramadan", 9)
        self.assert_map_key_val(self.parser.islamic_to_int, "рамадан", 9)  # RU

    def test_persian_to_int_tir_is_4(self):
        self.assert_map_key_val(self.parser.persian_to_int, "tir", 4)
        self.assert_map_key_val(self.parser.persian_to_int, "тир", 4)  # RU

    def test_calendar_to_int_gregorian(self):
        self.assert_map_key_val(
            self.parser.calendar_to_int, "gregorian", Date.CAL_GREGORIAN
        )
        self.assert_map_key_val(self.parser.calendar_to_int, "g", Date.CAL_GREGORIAN)
        self.assert_map_key_val(
            self.parser.calendar_to_int, "григорианский", Date.CAL_GREGORIAN
        )
        self.assert_map_key_val(self.parser.calendar_to_int, "г", Date.CAL_GREGORIAN)

    def test_calendar_to_int_julian(self):
        self.assert_map_key_val(self.parser.calendar_to_int, "julian", Date.CAL_JULIAN)
        self.assert_map_key_val(self.parser.calendar_to_int, "j", Date.CAL_JULIAN)
        self.assert_map_key_val(
            self.parser.calendar_to_int, "юлианский", Date.CAL_JULIAN
        )
        self.assert_map_key_val(self.parser.calendar_to_int, "ю", Date.CAL_JULIAN)

    def test_quarter_1(self):
        date = self.parser.parse("q1 1900")
        self.assertTrue(date.is_equal(self.parser.parse("Q1 1900")))
        self.assertEqual(date.get_ymd(), (1900, 1, 1))
        self.assertEqual(date.get_stop_ymd(), (1900, 3, 31))
        self.assertEqual(date.get_modifier(), Date.MOD_RANGE)

    def test_quarter_2(self):
        date = self.parser.parse("q2 1900")
        self.assertTrue(date.is_equal(self.parser.parse("Q2 1900")))
        self.assertEqual(date.get_ymd(), (1900, 4, 1))
        self.assertEqual(date.get_stop_ymd(), (1900, 6, 30))
        self.assertEqual(date.get_modifier(), Date.MOD_RANGE)

    def test_quarter_3(self):
        date = self.parser.parse("q3 1900")
        self.assertTrue(date.is_equal(self.parser.parse("Q3 1900")))
        self.assertEqual(date.get_ymd(), (1900, 7, 1))
        self.assertEqual(date.get_stop_ymd(), (1900, 9, 30))
        self.assertEqual(date.get_modifier(), Date.MOD_RANGE)

    def test_quarter_4(self):
        date = self.parser.parse("q4 1900")
        self.assertTrue(date.is_equal(self.parser.parse("Q4 1900")))
        self.assertEqual(date.get_ymd(), (1900, 10, 1))
        self.assertEqual(date.get_stop_ymd(), (1900, 12, 31))
        self.assertEqual(date.get_modifier(), Date.MOD_RANGE)

    def test_quarter_quality_calendar(self):
        date = self.parser.parse("calc q1 1900 (julian)")
        self.assertEqual(date.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(date.get_calendar(), Date.CAL_JULIAN)


class Test_generate_variants(unittest.TestCase):
    def setUp(self):
        from .. import _datestrings
        from .._dateparser import _generate_variants

        self.ds = ds = _datestrings.DateStrings(GrampsLocale(languages=("ru")))
        self.month_variants = list(
            _generate_variants(
                zip(ds.long_months, ds.short_months, ds.swedish_SV, ds.alt_long_months)
            )
        )

    def testVariantsSameLengthAsLongMonths(self):
        self.assertEqual(len(self.ds.long_months), len(self.month_variants))

    def testRussianHasDifferentVariantsForEachMonth(self):
        for i in range(1, 13):
            mvi = self.month_variants[i]
            self.assertTrue(len(mvi) > 1, msg=mvi)

    def testNoEmptyStringInVariants(self):
        for i in range(1, 13):
            mvi = self.month_variants[i]
            self.assertNotIn("", mvi)

    def testLongMonthsAppearInVariants(self):
        for i in range(1, 13):
            lmi = self.ds.long_months[i]
            mvi = self.month_variants[i]
            self.assertIn("{}".format(lmi), mvi)

    def testShortMonthsAppearInVariants(self):
        for i in range(1, 13):
            smi = self.ds.short_months[i]
            mvi = self.month_variants[i]
            self.assertIn("{}".format(smi), mvi)

    def testLongMonthVariantsUnique(self):
        for i in range(1, 13):
            mvi = self.month_variants[i]
            self.assertEqual(len(mvi), len(set(mvi)), msg=mvi)

    def testRuMayVariantsContainSvMaj(self):
        v = self.month_variants[5]
        self.assertIn("Maj", v)


class TestCompact8DateParsing(unittest.TestCase):
    """Tests for compact 8-digit date input (DDMMYYYY / MMDDYYYY / YYYYMMDD)."""

    def setUp(self):
        from .._dateparser import DateParser

        self.parser_mdy = DateParser()
        self.parser_mdy.dmy = False
        self.parser_mdy.ymd = False

        self.parser_dmy = DateParser()
        self.parser_dmy.dmy = True
        self.parser_dmy.ymd = False

        self.parser_ymd = DateParser()
        self.parser_ymd.dmy = False
        self.parser_ymd.ymd = True

    def test_mdy_compact(self):
        """MMDDYYYY: 01121720 -> month=01, day=12, year=1720."""
        date = self.parser_mdy.parse("01121720")
        self.assertEqual(date.get_ymd(), (1720, 1, 12))

    def test_dmy_compact(self):
        """DDMMYYYY: 01121720 -> day=01, month=12, year=1720."""
        date = self.parser_dmy.parse("01121720")
        self.assertEqual(date.get_ymd(), (1720, 12, 1))

    def test_ymd_yyyymmdd_via_isotimestamp(self):
        """YMD locale: 17201201 parsed as YYYYMMDD -> year=1720, month=12, day=01."""
        date = self.parser_ymd.parse("17201201")
        self.assertEqual(date.get_ymd(), (1720, 12, 1))

    def test_yyyymmdd_falls_through_compact_in_dmy(self):
        """In a DMY locale, YYYYMMDD (e.g. 17201201) has invalid month under DMY
        (month=20), so compact8 falls through to _isotimestamp which parses it
        correctly as year=1720, month=12, day=01."""
        date = self.parser_dmy.parse("17201201")
        self.assertEqual(date.get_ymd(), (1720, 12, 1))

    def test_yyyymmdd_falls_through_compact_in_mdy(self):
        """In an MDY locale, YYYYMMDD (e.g. 17201201) has invalid month under MDY
        (month=17), so compact8 falls through to _isotimestamp which parses it
        correctly as year=1720, month=12, day=01."""
        date = self.parser_mdy.parse("17201201")
        self.assertEqual(date.get_ymd(), (1720, 12, 1))

    def test_invalid_day_for_month_becomes_text(self):
        """31021720 (February 31) is invalid in any calendar; must not silently
        produce a wrong date — it should be stored as text."""
        date = self.parser_dmy.parse("31021720")
        self.assertEqual(date.get_modifier(), Date.MOD_TEXTONLY)

    def test_invalid_month_becomes_text(self):
        """99991720 has month=99 which is impossible; must become text."""
        date = self.parser_mdy.parse("99991720")
        self.assertEqual(date.get_modifier(), Date.MOD_TEXTONLY)

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is tolerated (strip() runs before parsing)."""
        date = self.parser_dmy.parse("  01121720  ")
        self.assertEqual(date.get_ymd(), (1720, 12, 1))


if __name__ == "__main__":
    unittest.main()
