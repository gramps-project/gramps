# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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
Validate localized date parser and displayer.

Based on the Check Localized Date Displayer and Parser tool.
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import unittest

import sys
if '-v' in sys.argv or '--verbose' in sys.argv:
    import logging
    logging.getLogger('').addHandler(logging.StreamHandler())
    log = logging.getLogger(".Date")
    log.setLevel(logging.DEBUG)

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ...lib import Date, DateError
from .. import parser as _dp
from .. import displayer as _dd

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class DateHandlerTest(unittest.TestCase):
    def base_case(self, test_date):
        datestr = _dd.display(test_date)
        new_date = _dp.parse(datestr)

        self.assertTrue(test_date.is_equal(new_date),
                "{} -> {}\n{} -> {}".format(
                    test_date, new_date,
                    test_date.__dict__, new_date.__dict__))

    def test_simple(self):

        dates = []
        for calendar in (Date.CAL_GREGORIAN, Date.CAL_JULIAN):
            for newyear in (Date.NEWYEAR_JAN1, Date.NEWYEAR_MAR25, (5,5)):
                for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED,
                                Date.QUAL_CALCULATED):
                    for modifier in (Date.MOD_NONE, Date.MOD_BEFORE,
                                     Date.MOD_AFTER, Date.MOD_ABOUT):
                        for slash1 in (False,True):
                            for month in range(1, 13):
                                for day in (5, 27):
                                    d = Date()
                                    d.set(quality, modifier, calendar,
                                          (day, month, 1789, slash1),
                                          "Text comment",
                                          newyear)
                                    dates.append(d)

        for test_date in dates:
            self.base_case(test_date)

    def test_span(self):

        dates = []
        calendar = Date.CAL_GREGORIAN
        for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED,
                        Date.QUAL_CALCULATED):
            for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
                for slash1 in (False, True):
                    for slash2 in (False, True):
                        for month in range(1, 13):
                            for day in (5, 27):
                                d = Date()
                                d.set(quality, modifier, calendar,
                                      (day, month, 1789, slash1,
                                       day, month, 1876, slash2),
                                      "Text comment")
                                dates.append(d)
                                d = Date()
                                d.set(quality, modifier, calendar,
                                      (day, month, 1789, slash1,
                                       day, 13-month, 1876, slash2),
                                      "Text comment")
                                dates.append(d)
                                d = Date()
                                d.set(quality, modifier, calendar,
                                      (day, month, 1789, slash1,
                                       32-day, month, 1876, slash2),
                                      "Text comment")
                                dates.append(d)
                                d = Date()
                                d.set(quality, modifier, calendar,
                                      (day, month, 1789, slash1,
                                       32-day, 13-month, 1876, slash2),
                                      "Text comment")
                                dates.append(d)

        for test_date in dates:
            self.base_case(test_date)

    def test_textual(self):
        calendar = Date.CAL_GREGORIAN
        modifier = Date.MOD_TEXTONLY
        for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED,
                        Date.QUAL_CALCULATED):
            test_date = Date()
            test_date.set(quality, modifier, calendar, Date.EMPTY,
                          "This is a textual date")
            self.base_case(test_date)

    def test_too_few_arguments(self):
        dateval = (4, 7, 1789, False)
        for l in range(1, len(dateval)):
            d = Date()
            with self.assertRaises(DateError):
                d.set(Date.QUAL_NONE, Date.MOD_NONE, Date.CAL_GREGORIAN,
                      dateval[:l], "Text comment")

    def test_too_few_span_arguments(self):
        dateval = (4, 7, 1789, False, 5, 8, 1876, False)
        for l in range(1, len(dateval)):
            d = Date()
            with self.assertRaises(DateError):
                d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                      dateval[:l], "Text comment")

    def test_invalid_day(self):
        d = Date()
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE, Date.MOD_NONE, Date.CAL_GREGORIAN,
                  (44, 7, 1789,False), "Text comment")

    def test_invalid_month(self):
        d = Date()
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE,Date.MOD_NONE, Date.CAL_GREGORIAN,
                  (4, 77, 1789, False), "Text comment")

    def test_invalid_month_with_ny(self):
        d = Date()
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE,Date.MOD_NONE, Date.CAL_GREGORIAN,
                  (4, 77, 1789, False), "Text comment", newyear=2)

    def test_invalid_span_day(self):
        d = Date()
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                  (4, 7, 1789, False, 55, 8, 1876, False), "Text comment")

    def test_invalid_span_month(self):
        d = Date()
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                  (4, 7, 1789, False, 5, 88, 1876, False), "Text comment")

if __name__ == "__main__":
    unittest.main()
