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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
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
        self.parser_RU = GrampsLocale(lang='ru').date_parser

    def assert_map_key_val(self, m, k, v):
        try:
            self.assertEqual(m[k], v)
        except KeyError:
            self.assertTrue(False, list(m.items()))

    def test_month_to_int_jan_is_1(self):
        self.assert_map_key_val(self.parser.month_to_int, 'jan', 1)

    def test_prefix_table_for_RU_built(self):
        self.assertIn('ru_RU', self.parser._langs)

    def test_month_to_int_septem_RU_is_9(self):
        self.assert_map_key_val(self.parser.month_to_int, 'сентяб', 9)

    def test_hebrew_to_int_av_is_12(self):
        self.assert_map_key_val(self.parser.hebrew_to_int, 'av', 12)
        self.assert_map_key_val(self.parser.hebrew_to_int, 'ав', 12) # RU

    def test_french_to_int_thermidor_is_11(self):
        self.assert_map_key_val(self.parser.french_to_int, 'thermidor', 11)
        self.assert_map_key_val(self.parser.french_to_int, 'термидор', 11) # RU

    def test_islamic_to_int_ramadan_is_9(self):
        self.assert_map_key_val(self.parser.islamic_to_int, 'ramadan', 9)
        self.assert_map_key_val(self.parser.islamic_to_int, 'рамадан', 9) # RU

    def test_persian_to_int_tir_is_4(self):
        self.assert_map_key_val(self.parser.persian_to_int, 'tir', 4)
        self.assert_map_key_val(self.parser.persian_to_int, 'тир', 4) # RU

    def test_calendar_to_int_gregorian(self):
        self.assert_map_key_val(self.parser.calendar_to_int, 'gregorian', Date.CAL_GREGORIAN)
        self.assert_map_key_val(self.parser.calendar_to_int, 'g', Date.CAL_GREGORIAN)
        self.assert_map_key_val(self.parser.calendar_to_int, 'григорианский', Date.CAL_GREGORIAN)
        self.assert_map_key_val(self.parser.calendar_to_int, 'г', Date.CAL_GREGORIAN)

    def test_calendar_to_int_julian(self):
        self.assert_map_key_val(self.parser.calendar_to_int, 'julian', Date.CAL_JULIAN)
        self.assert_map_key_val(self.parser.calendar_to_int, 'j', Date.CAL_JULIAN)
        self.assert_map_key_val(self.parser.calendar_to_int, 'юлианский', Date.CAL_JULIAN)
        self.assert_map_key_val(self.parser.calendar_to_int, 'ю', Date.CAL_JULIAN)

class Test_generate_variants(unittest.TestCase):
    def setUp(self):
        from .. import _datestrings
        from .._dateparser import _generate_variants
        self.ds = ds = _datestrings.DateStrings(GrampsLocale(languages=('ru')))
        self.month_variants = list(_generate_variants(
                    zip(ds.long_months, ds.short_months,
                        ds.swedish_SV, ds.alt_long_months)))

    def testVariantsSameLengthAsLongMonths(self):
        self.assertEqual(len(self.ds.long_months),
                len(self.month_variants))

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

if __name__ == "__main__":
    unittest.main()
