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

class DateDisplayTest(unittest.TestCase):
    def setUp(self):
        from .._datedisplay import DateDisplayEn
        self.display = DateDisplayEn()
        self.display_RU = GrampsLocale(lang='ru').date_displayer

    def assert_map_key_val(self, m, k, v):
        try:
            self.assertEqual(m[k], v)
        except KeyError:
            self.assertTrue(False, list(m.items()))

class DateDisplayCalendarTest(DateDisplayTest):
    def test_calendar_gregorian_is_empty(self):
        self.assert_map_key_val(self.display.calendar, Date.CAL_GREGORIAN, "")

    def test_calendar_julian_RU(self):
        self.assert_map_key_val(self.display_RU.calendar, Date.CAL_JULIAN, 'юлианский')

# This class tests common functionality in DateDisplay as applied to RU,
# and so it is coupled to translated strings and inflection names
# extracted by lexgettext from ru.po
class DateDisplayInflectionsTestRU(DateDisplayTest):
    def setUp(self):
        DateDisplayTest.setUp(self)
        self.dd = self.display = self.display_RU
        self.months = self.dd._ds.long_months
        # TODO hardwired magic numbers! Bad API smell.
        self.dd.set_format(4) # day month_name year
        self.may = self.months[5]

    def assertInflectionInDate(self, inflection, date, month=None):
        if month is None:
            month = date.get_month()
        month_lexeme = self.months[month]
        self.assertIn(month_lexeme.f[inflection],
                self.dd.display(date))

    def test_month_only_date_nominative_quality_none(self):
        d1945may = Date(1945, 5, 0)
        d1945may.set_quality(Date.QUAL_NONE)
        self.assertInflectionInDate('И', d1945may)

    def test_month_only_date_nominative_quality_estimated(self):
        d1945may = Date(1945, 5, 0)
        d1945may.set_quality(Date.QUAL_ESTIMATED)
        self.assertInflectionInDate('Т', d1945may)

    def test_month_only_date_nominative_quality_calculated(self):
        d1945may = Date(1945, 5, 0)
        d1945may.set_quality(Date.QUAL_CALCULATED)
        self.assertInflectionInDate('И', d1945may)

    def test_day_month_date_genitive(self):
        d1945may9 = Date(1945, 5, 9)
        self.assertInflectionInDate('Р', d1945may9)

    def test_day_month_date_genitiive_quality_estimated(self):
        d1945may9 = Date(1945, 5, 9)
        d1945may9.set_quality(Date.QUAL_ESTIMATED)
        self.assertInflectionInDate('Р', d1945may9)

    def test_before_month_only_date_genitive(self):
        d1945may = Date(1945, 5, 0)
        d1945may.set_modifier(Date.MOD_BEFORE)
        # TODO hardwired magic numbers! Bad API smell.
        for inflecting_format in (3,4):
            self.dd.set_format(inflecting_format)
# this depends on the fact that in Russian the short and long forms for May
# will be the same!
            self.assertIn("до мая", self.dd.display(d1945may))

    def test_after_month_only_date_genitive(self):
        d1945may = Date(1945, 5, 0)
        d1945may.set_modifier(Date.MOD_AFTER)
        # TODO hardwired magic numbers! Bad API smell.
        for inflecting_format in (3,4):
            self.dd.set_format(inflecting_format)
# this depends on the fact that in Russian the short and long forms for May
# will be the same!
            self.assertIn("после мая", self.dd.display(d1945may))

    def test_about_month_only_date_genitive(self):
        d1945may = Date(1945, 5, 0)
        d1945may.set_modifier(Date.MOD_ABOUT)
        # TODO hardwired magic numbers! Bad API smell.
        for inflecting_format in (3,4):
            self.dd.set_format(inflecting_format)
# this depends on the fact that in Russian the short and long forms for May
# will be the same!
            self.assertIn("около мая", self.dd.display(d1945may))

    def test_between_month_only_dates_ablative(self):
        b1945may_1946may = Date()
        b1945may_1946may.set(
                modifier=Date.MOD_RANGE,
                value=(0, 5, 1945, False, 0, 5, 1946, False))
        # TODO hardwired magic numbers! Bad API smell.
        for inflecting_format in (3,4):
            self.dd.set_format(inflecting_format)
# this depends on the fact that in Russian the short and long forms for May
# will be the same!
            self.assertIn("между маем", self.dd.display(b1945may_1946may))
            self.assertIn("и маем", self.dd.display(b1945may_1946may))

    def test_month_only_date_span_from_genitive_to_accusative(self):
        f1945may_t1946may = Date()
        f1945may_t1946may.set(
                modifier=Date.MOD_SPAN,
                value=(0, 5, 1945, False, 0, 5, 1946, False))
        # TODO hardwired magic numbers! Bad API smell.
        for inflecting_format in (3,4):
            self.dd.set_format(inflecting_format)
# this depends on the fact that in Russian the short and long forms for May
# will be the same!
            self.assertIn("с мая", self.dd.display(f1945may_t1946may))
            self.assertIn("по май", self.dd.display(f1945may_t1946may))

if __name__ == "__main__":
    unittest.main()
