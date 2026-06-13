# -*- coding: utf-8 -*-
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

"""Tests for Chinese date handlers — modifier word order (postfix before/after)."""

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
from gramps.gen.datehandler._date_zh_CN import DateParserZH_CN, DateDisplayZH_CN
from gramps.gen.datehandler._date_zh_TW import DateParserZH_TW, DateDisplayZH_TW


def _make_date(modifier, year, month=0, day=0):
    """Return a Date with the given modifier and Gregorian date."""
    d = Date()
    d.set(modifier, Date.MOD_NONE, Date.CAL_GREGORIAN, (day, month, year, False))
    d.set_modifier(modifier)
    return d


# -------------------------------------------------------------------------
#
# Simplified Chinese (zh_CN) — display tests
#
# -------------------------------------------------------------------------
class TestDateDisplayZH_CN(unittest.TestCase):
    """Verify that 以前/以后 appear AFTER the date in Simplified Chinese."""

    def setUp(self):
        """Create displayer using format 1 (numeric, non-ISO)."""
        self.dd = DateDisplayZH_CN(format=1)

    def test_before_year_is_postfix(self):
        """'before 2000' displays as '2000年以前', not '以前2000年'."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_BEFORE, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        result = self.dd.display(d)
        self.assertIn("以前", result)
        self.assertTrue(
            result.endswith("以前"),
            msg=f"Expected '以前' at end, got: {result!r}",
        )
        self.assertFalse(
            result.startswith("以前"),
            msg=f"'以前' should not be at the start, got: {result!r}",
        )

    def test_after_year_is_postfix(self):
        """'after 2000' displays as '2000年以后', not '以后2000年'."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_AFTER, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        result = self.dd.display(d)
        self.assertIn("以后", result)
        self.assertTrue(
            result.endswith("以后"),
            msg=f"Expected '以后' at end, got: {result!r}",
        )
        self.assertFalse(
            result.startswith("以后"),
            msg=f"'以后' should not be at the start, got: {result!r}",
        )

    def test_about_year_is_prefix(self):
        """'about 2000' displays with '大约' before the year."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        result = self.dd.display(d)
        self.assertIn("大约", result)
        self.assertTrue(
            result.startswith("大约"),
            msg=f"Expected '大约' at start, got: {result!r}",
        )

    def test_before_display_exact(self):
        """'before 2000' ends with 以前 in numeric format (year-only = '2000 以前')."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_BEFORE, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        result = self.dd.display(d)
        self.assertTrue(result.endswith("以前"), msg=repr(result))

    def test_after_display_exact(self):
        """'after 1949' ends with 以后 in numeric format (year-only = '1949 以后')."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_AFTER, Date.CAL_GREGORIAN, (0, 0, 1949, False))
        result = self.dd.display(d)
        self.assertTrue(result.endswith("以后"), msg=repr(result))


# -------------------------------------------------------------------------
#
# Simplified Chinese (zh_CN) — parser tests
#
# -------------------------------------------------------------------------
class TestDateParserZH_CN(unittest.TestCase):
    """Verify that postfix 以前/以后 parse correctly in Simplified Chinese."""

    def setUp(self):
        """Create parser instance."""
        self.dp = DateParserZH_CN()

    def _parse(self, text):
        """Parse text and return a Date."""
        d = Date()
        self.dp.set_date(d, text)
        return d

    def test_before_postfix_parses(self):
        """'2000年以前' parses as MOD_BEFORE, year 2000."""
        d = self._parse("2000年以前")
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 2000)

    def test_after_postfix_parses(self):
        """'1949年以后' parses as MOD_AFTER, year 1949."""
        d = self._parse("1949年以后")
        self.assertEqual(d.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d.get_year(), 1949)

    def test_before_with_month_parses(self):
        """'2000年3月以前' parses as MOD_BEFORE, year 2000, month 3."""
        d = self._parse("2000年3月以前")
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 2000)
        self.assertEqual(d.get_month(), 3)

    def test_about_prefix_parses(self):
        """'大约 2000年' parses as MOD_ABOUT, year 2000 (space required by prefix regex)."""
        d = self._parse("大约 2000年")
        self.assertEqual(d.get_modifier(), Date.MOD_ABOUT)
        self.assertEqual(d.get_year(), 2000)


# -------------------------------------------------------------------------
#
# Simplified Chinese (zh_CN) — round-trip tests
#
# -------------------------------------------------------------------------
class TestRoundTripZH_CN(unittest.TestCase):
    """Display then re-parse should recover the original modifier and year."""

    def setUp(self):
        """Create parser and displayer pair."""
        self.dp = DateParserZH_CN()
        self.dd = DateDisplayZH_CN(format=1)

    def _roundtrip(self, d):
        """Display then re-parse; return the re-parsed Date."""
        text = self.dd.display(d)
        d2 = Date()
        self.dp.set_date(d2, text)
        return d2

    def test_before_roundtrip(self):
        """Before-2000 round-trips through display and parse."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_BEFORE, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d2.get_year(), 2000)

    def test_after_roundtrip(self):
        """After-1949 round-trips through display and parse."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_AFTER, Date.CAL_GREGORIAN, (0, 0, 1949, False))
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d2.get_year(), 1949)


# -------------------------------------------------------------------------
#
# Traditional Chinese (zh_TW) — display tests
#
# -------------------------------------------------------------------------
class TestDateDisplayZH_TW(unittest.TestCase):
    """Verify that 以前/以後 appear AFTER the date in Traditional Chinese."""

    def setUp(self):
        """Create displayer using format 1 (numeric, non-ISO)."""
        self.dd = DateDisplayZH_TW(format=1)

    def test_before_year_is_postfix(self):
        """'before 2000' displays as '2000年以前', not '以前2000年'."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_BEFORE, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        result = self.dd.display(d)
        self.assertIn("以前", result)
        self.assertTrue(
            result.endswith("以前"),
            msg=f"Expected '以前' at end, got: {result!r}",
        )

    def test_after_year_is_postfix(self):
        """'after 2000' displays as '2000年以後', not '以後2000年'."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_AFTER, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        result = self.dd.display(d)
        self.assertIn("以後", result)
        self.assertTrue(
            result.endswith("以後"),
            msg=f"Expected '以後' at end, got: {result!r}",
        )

    def test_about_year_is_prefix(self):
        """'about 2000' displays with '大約' before the year."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_ABOUT, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        result = self.dd.display(d)
        self.assertIn("大約", result)
        self.assertTrue(
            result.startswith("大約"),
            msg=f"Expected '大約' at start, got: {result!r}",
        )

    def test_before_display_exact(self):
        """'before 2000' ends with 以前 in numeric format (year-only = '2000 以前')."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_BEFORE, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        result = self.dd.display(d)
        self.assertTrue(result.endswith("以前"), msg=repr(result))

    def test_after_display_exact(self):
        """'after 1949' ends with 以後 in numeric format (year-only = '1949 以後')."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_AFTER, Date.CAL_GREGORIAN, (0, 0, 1949, False))
        result = self.dd.display(d)
        self.assertTrue(result.endswith("以後"), msg=repr(result))


# -------------------------------------------------------------------------
#
# Traditional Chinese (zh_TW) — parser tests
#
# -------------------------------------------------------------------------
class TestDateParserZH_TW(unittest.TestCase):
    """Verify that postfix 以前/以後 parse correctly in Traditional Chinese."""

    def setUp(self):
        """Create parser instance."""
        self.dp = DateParserZH_TW()

    def _parse(self, text):
        """Parse text and return a Date."""
        d = Date()
        self.dp.set_date(d, text)
        return d

    def test_before_postfix_parses(self):
        """'2000年以前' parses as MOD_BEFORE, year 2000."""
        d = self._parse("2000年以前")
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 2000)

    def test_after_postfix_parses(self):
        """'1949年以後' parses as MOD_AFTER, year 1949."""
        d = self._parse("1949年以後")
        self.assertEqual(d.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d.get_year(), 1949)

    def test_english_before_still_parses(self):
        """English fallback 'before 2000' still parses as MOD_BEFORE."""
        d = self._parse("before 2000")
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 2000)

    def test_english_after_still_parses(self):
        """English fallback 'after 2000' still parses as MOD_AFTER."""
        d = self._parse("after 2000")
        self.assertEqual(d.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d.get_year(), 2000)


# -------------------------------------------------------------------------
#
# Traditional Chinese (zh_TW) — round-trip tests
#
# -------------------------------------------------------------------------
class TestRoundTripZH_TW(unittest.TestCase):
    """Display then re-parse should recover the original modifier and year."""

    def setUp(self):
        """Create parser and displayer pair."""
        self.dp = DateParserZH_TW()
        self.dd = DateDisplayZH_TW(format=1)

    def _roundtrip(self, d):
        """Display then re-parse; return the re-parsed Date."""
        text = self.dd.display(d)
        d2 = Date()
        self.dp.set_date(d2, text)
        return d2

    def test_before_roundtrip(self):
        """Before-2000 round-trips through display and parse."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_BEFORE, Date.CAL_GREGORIAN, (0, 0, 2000, False))
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d2.get_year(), 2000)

    def test_after_roundtrip(self):
        """After-1949 round-trips through display and parse."""
        d = Date()
        d.set(Date.QUAL_NONE, Date.MOD_AFTER, Date.CAL_GREGORIAN, (0, 0, 1949, False))
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d2.get_year(), 1949)


if __name__ == "__main__":
    unittest.main()
