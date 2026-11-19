#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps Development Team
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
# along with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""Unittest for diff_dates / diff_items in gen/merge/diff.py"""

import unittest

from gramps.gen.lib import Date, Event
from gramps.gen.lib.json_utils import object_to_dict
from gramps.gen.merge.diff import diff_dates, diff_items


def _date(year=0, month=0, day=0):
    date = Date()
    if year:
        date.set_yr_mon_day(year, month, day)
    return date


def _text_date(text):
    date = Date()
    date.set(modifier=Date.MOD_TEXTONLY, text=text)
    return date


def _dict(obj):
    return object_to_dict(obj)


class DiffDatesTest(unittest.TestCase):
    def test_equal_dates(self):
        self.assertFalse(
            diff_dates(_dict(_date(1697, 5, 14)), _dict(_date(1697, 5, 14)))
        )

    def test_different_day(self):
        self.assertTrue(
            diff_dates(_dict(_date(1697, 5, 14)), _dict(_date(1697, 5, 17)))
        )

    def test_year_added_to_empty_date(self):
        self.assertTrue(diff_dates(_dict(_date(1813)), _dict(_date())))

    def test_same_value_different_text(self):
        date1 = _date(1697, 5, 14)
        date2 = _date(1697, 5, 14)
        date2.text = "14 May 1697"
        self.assertFalse(diff_dates(_dict(date1), _dict(date2)))

    def test_text_only_dates(self):
        self.assertFalse(
            diff_dates(_dict(_text_date("spring")), _dict(_text_date("spring")))
        )
        self.assertTrue(
            diff_dates(_dict(_text_date("spring")), _dict(_text_date("summer")))
        )

    def test_event_with_changed_date_is_different(self):
        event1 = Event()
        event1.set_date_object(_date(1697, 5, 14))
        event2 = Event()
        event2.set_date_object(_date(1697, 5, 17))
        self.assertTrue(diff_items("Event", _dict(event1), _dict(event2)))


if __name__ == "__main__":
    unittest.main()
