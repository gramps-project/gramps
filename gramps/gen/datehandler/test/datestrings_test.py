# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013  Vassilii Khachaturov
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

import unittest

from .. import _datestrings
from ...lib.date import Date


class DateStringsTest(unittest.TestCase):
    def setUp(self):
        from ...utils.grampslocale import GrampsLocale

        self.ds = _datestrings.DateStrings(GrampsLocale())  # whatever the default...
        self.ds_EN = _datestrings.DateStrings(GrampsLocale(languages="en"))
        self.ds_RU = _datestrings.DateStrings(GrampsLocale(languages="ru"))

    def testTwelfthMonthIsDecember(self):
        self.assertEqual(self.ds_EN.long_months[12], "December")
        self.assertEqual(self.ds_EN.short_months[12], "Dec")

    # May is 3-letter in Russian, and so abbreviated form
    # will be different for inflections!
    def testRussianHasDifferentInflectionsForShortMay(self):
        v5 = list(self.ds_RU.short_months[5].variants())
        self.assertTrue(len(v5) > 1, msg=v5)

    def testEnAdarI_in_AdarII(self):
        adar1 = self.ds_EN.hebrew[6]
        adar2 = self.ds_EN.hebrew[7]
        self.assertIn(str(adar1), str(adar2))

    def testEnLastFrenchIsExtra(self):
        self.assertEqual(str(self.ds_EN.french[-1]), "Extra")

    def testEnPersianKhordadMordad(self):
        khordad = self.ds_EN.persian[3].lower()
        mordad = self.ds_EN.persian[5].lower()
        self.assertEqual(khordad, "khordad")
        self.assertEqual(mordad, "mordad")

    def testEnIslamicRamadan9(self):
        self.assertEqual(str(self.ds_EN.islamic[9]), "Ramadan")

    def testFirstStringEmpty(self):
        self.assertEqual(self.ds.long_months[0], "")
        self.assertEqual(self.ds.short_months[0], "")
        self.assertEqual(self.ds.alt_long_months[0], "")
        self.assertEqual(self.ds.long_days[0], "")

    def testCalendarIndex(self):
        self.assertEqual(self.ds_EN.calendar[Date.CAL_GREGORIAN], "Gregorian")
        self.assertEqual(self.ds_EN.calendar[Date.CAL_JULIAN], "Julian")
        self.assertEqual(self.ds_EN.calendar[Date.CAL_HEBREW], "Hebrew")
        self.assertEqual(self.ds_EN.calendar[Date.CAL_FRENCH], "French Republican")
        self.assertEqual(self.ds_EN.calendar[Date.CAL_PERSIAN], "Persian")
        self.assertEqual(self.ds_EN.calendar[Date.CAL_ISLAMIC], "Islamic")
        self.assertEqual(self.ds_EN.calendar[Date.CAL_SWEDISH], "Swedish")

    def testDayNamesLenIs8(self):
        self.assertEqual(len(self.ds.long_days), 8)


if __name__ == "__main__":
    unittest.main()
