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

"""Tests for Chinese date handlers — display format, modifier word order, and round-trips."""

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


# -------------------------------------------------------------------------
#
# Simplified Chinese (zh_CN) — display tests
#
# -------------------------------------------------------------------------
class TestDateDisplayZH_CN(unittest.TestCase):
    """Verify Simplified Chinese date display format."""

    def setUp(self):
        """Create displayer using format 1 (numeric, non-ISO)."""
        self.dd = DateDisplayZH_CN(format=1)

    def _date(self, qual, mod, year, month=0, day=0, cal=Date.CAL_GREGORIAN):
        """Return a Date with the given attributes."""
        d = Date()
        d.set(qual, mod, cal, (day, month, year, False))
        return d

    def test_year_only(self):
        """Year-only date displays as '1949年'."""
        d = self._date(Date.QUAL_NONE, Date.MOD_NONE, 1949)
        self.assertEqual(self.dd.display(d), "1949年")

    def test_before_year(self):
        """'before 2000' displays as '2000年以前'."""
        d = self._date(Date.QUAL_NONE, Date.MOD_BEFORE, 2000)
        self.assertEqual(self.dd.display(d), "2000年以前")

    def test_after_year(self):
        """'after 1949' displays as '1949年以后'."""
        d = self._date(Date.QUAL_NONE, Date.MOD_AFTER, 1949)
        self.assertEqual(self.dd.display(d), "1949年以后")

    def test_about_year(self):
        """'about 1850' displays as '大约1850年'."""
        d = self._date(Date.QUAL_NONE, Date.MOD_ABOUT, 1850)
        self.assertEqual(self.dd.display(d), "大约1850年")

    def test_estimated_year(self):
        """Estimated 1800 displays as '估计为1800年'."""
        d = self._date(Date.QUAL_ESTIMATED, Date.MOD_NONE, 1800)
        self.assertEqual(self.dd.display(d), "估计为1800年")

    def test_calculated_year_month(self):
        """Calculated 1776-06 displays as '推算为1776年6月'."""
        d = self._date(Date.QUAL_CALCULATED, Date.MOD_NONE, 1776, month=6)
        self.assertEqual(self.dd.display(d), "推算为1776年6月")

    def test_estimated_before(self):
        """Estimated before 1900 displays as '估计早于1900年'."""
        d = self._date(Date.QUAL_ESTIMATED, Date.MOD_BEFORE, 1900)
        self.assertEqual(self.dd.display(d), "估计早于1900年")

    def test_calculated_after(self):
        """Calculated after 1800 displays as '推算晚于1800年'."""
        d = self._date(Date.QUAL_CALCULATED, Date.MOD_AFTER, 1800)
        self.assertEqual(self.dd.display(d), "推算晚于1800年")

    def test_estimated_after(self):
        """Estimated after 1800 displays as '估计晚于1800年'."""
        d = self._date(Date.QUAL_ESTIMATED, Date.MOD_AFTER, 1800)
        self.assertEqual(self.dd.display(d), "估计晚于1800年")

    def test_calculated_before(self):
        """Calculated before 1900 displays as '推算早于1900年'."""
        d = self._date(Date.QUAL_CALCULATED, Date.MOD_BEFORE, 1900)
        self.assertEqual(self.dd.display(d), "推算早于1900年")

    def test_before_year_is_postfix(self):
        """'before 2000' has 以前 AFTER the year, not before."""
        d = self._date(Date.QUAL_NONE, Date.MOD_BEFORE, 2000)
        result = self.dd.display(d)
        self.assertIn("以前", result)
        self.assertTrue(result.endswith("以前"), msg=repr(result))
        self.assertFalse(result.startswith("以前"), msg=repr(result))

    def test_after_year_is_postfix(self):
        """'after 2000' has 以后 AFTER the year, not before."""
        d = self._date(Date.QUAL_NONE, Date.MOD_AFTER, 2000)
        result = self.dd.display(d)
        self.assertIn("以后", result)
        self.assertTrue(result.endswith("以后"), msg=repr(result))
        self.assertFalse(result.startswith("以后"), msg=repr(result))

    def test_about_year_is_prefix(self):
        """'about 2000' has 大约 BEFORE the year."""
        d = self._date(Date.QUAL_NONE, Date.MOD_ABOUT, 2000)
        result = self.dd.display(d)
        self.assertTrue(result.startswith("大约"), msg=repr(result))

    def test_span(self):
        """Span 1900–1910 displays as '自1900年至1910年'."""
        d = Date()
        d.set(
            Date.QUAL_NONE,
            Date.MOD_SPAN,
            Date.CAL_GREGORIAN,
            (0, 0, 1900, False) + (0, 0, 1910, False),
        )
        self.assertEqual(self.dd.display(d), "自1900年至1910年")

    def test_range(self):
        """Range 1900–1910 displays as '介于1900年与1910年之间'."""
        d = Date()
        d.set(
            Date.QUAL_NONE,
            Date.MOD_RANGE,
            Date.CAL_GREGORIAN,
            (0, 0, 1900, False) + (0, 0, 1910, False),
        )
        self.assertEqual(self.dd.display(d), "介于1900年与1910年之间")


# -------------------------------------------------------------------------
#
# Simplified Chinese (zh_CN) — parser tests
#
# -------------------------------------------------------------------------
class TestDateParserZH_CN(unittest.TestCase):
    """Verify that all display forms parse back correctly."""

    def setUp(self):
        """Create parser instance."""
        self.dp = DateParserZH_CN()

    def _parse(self, text):
        """Parse text and return a Date."""
        d = Date()
        self.dp.set_date(d, text)
        return d

    def test_year_only_parses(self):
        """'1949年' parses as year 1949, no modifier."""
        d = self._parse("1949年")
        self.assertEqual(d.get_year(), 1949)
        self.assertEqual(d.get_modifier(), Date.MOD_NONE)

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

    def test_about_no_space_parses(self):
        """'大约1850年' (no space) parses as MOD_ABOUT, year 1850."""
        d = self._parse("大约1850年")
        self.assertEqual(d.get_modifier(), Date.MOD_ABOUT)
        self.assertEqual(d.get_year(), 1850)

    def test_about_with_space_still_parses(self):
        """'大约 2000年' (with space) still parses as MOD_ABOUT, year 2000."""
        d = self._parse("大约 2000年")
        self.assertEqual(d.get_modifier(), Date.MOD_ABOUT)
        self.assertEqual(d.get_year(), 2000)

    def test_estimated_parses(self):
        """'估计为1800年' parses as QUAL_ESTIMATED, year 1800."""
        d = self._parse("估计为1800年")
        self.assertEqual(d.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d.get_modifier(), Date.MOD_NONE)
        self.assertEqual(d.get_year(), 1800)

    def test_calculated_year_month_parses(self):
        """'推算为1776年6月' parses as QUAL_CALCULATED, year 1776, month 6."""
        d = self._parse("推算为1776年6月")
        self.assertEqual(d.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(d.get_modifier(), Date.MOD_NONE)
        self.assertEqual(d.get_year(), 1776)
        self.assertEqual(d.get_month(), 6)

    def test_estimated_before_parses(self):
        """'估计早于1900年' parses as QUAL_ESTIMATED + MOD_BEFORE, year 1900."""
        d = self._parse("估计早于1900年")
        self.assertEqual(d.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 1900)

    def test_calculated_after_parses(self):
        """'推算晚于1800年' parses as QUAL_CALCULATED + MOD_AFTER, year 1800."""
        d = self._parse("推算晚于1800年")
        self.assertEqual(d.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(d.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d.get_year(), 1800)

    def test_estimated_after_parses(self):
        """'估计晚于1800年' parses as QUAL_ESTIMATED + MOD_AFTER, year 1800."""
        d = self._parse("估计晚于1800年")
        self.assertEqual(d.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d.get_year(), 1800)

    def test_calculated_before_parses(self):
        """'推算早于1900年' parses as QUAL_CALCULATED + MOD_BEFORE, year 1900."""
        d = self._parse("推算早于1900年")
        self.assertEqual(d.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 1900)

    def test_old_estimated_still_parses(self):
        """'据估计 1800年' (old format) still parses as QUAL_ESTIMATED."""
        d = self._parse("据估计 1800年")
        self.assertEqual(d.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d.get_year(), 1800)

    def test_old_calculated_still_parses(self):
        """'据计算 1800年' (old format) still parses as QUAL_CALCULATED."""
        d = self._parse("据计算 1800年")
        self.assertEqual(d.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(d.get_year(), 1800)


# -------------------------------------------------------------------------
#
# Simplified Chinese (zh_CN) — round-trip tests
#
# -------------------------------------------------------------------------
class TestRoundTripZH_CN(unittest.TestCase):
    """Display then re-parse should recover the original date attributes."""

    def setUp(self):
        """Create parser and displayer pair."""
        self.dp = DateParserZH_CN()
        self.dd = DateDisplayZH_CN(format=1)

    def _make(self, qual, mod, year, month=0, day=0, cal=Date.CAL_GREGORIAN):
        """Build a Date with the given attributes."""
        d = Date()
        d.set(qual, mod, cal, (day, month, year, False))
        return d

    def _roundtrip(self, d):
        """Display then re-parse; return the re-parsed Date."""
        text = self.dd.display(d)
        d2 = Date()
        self.dp.set_date(d2, text)
        return d2

    def test_year_only_roundtrip(self):
        """Year-only date round-trips."""
        d = self._make(Date.QUAL_NONE, Date.MOD_NONE, 1949)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_year(), 1949)
        self.assertEqual(d2.get_modifier(), Date.MOD_NONE)

    def test_before_roundtrip(self):
        """Before-2000 round-trips."""
        d = self._make(Date.QUAL_NONE, Date.MOD_BEFORE, 2000)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d2.get_year(), 2000)

    def test_after_roundtrip(self):
        """After-1949 round-trips."""
        d = self._make(Date.QUAL_NONE, Date.MOD_AFTER, 1949)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d2.get_year(), 1949)

    def test_about_roundtrip(self):
        """About-1850 round-trips."""
        d = self._make(Date.QUAL_NONE, Date.MOD_ABOUT, 1850)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_ABOUT)
        self.assertEqual(d2.get_year(), 1850)

    def test_estimated_roundtrip(self):
        """Estimated-1800 round-trips."""
        d = self._make(Date.QUAL_ESTIMATED, Date.MOD_NONE, 1800)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d2.get_modifier(), Date.MOD_NONE)
        self.assertEqual(d2.get_year(), 1800)

    def test_calculated_year_month_roundtrip(self):
        """Calculated 1776-06 round-trips."""
        d = self._make(Date.QUAL_CALCULATED, Date.MOD_NONE, 1776, month=6)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(d2.get_year(), 1776)
        self.assertEqual(d2.get_month(), 6)

    def test_estimated_before_roundtrip(self):
        """Estimated before-1900 round-trips."""
        d = self._make(Date.QUAL_ESTIMATED, Date.MOD_BEFORE, 1900)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d2.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d2.get_year(), 1900)

    def test_calculated_after_roundtrip(self):
        """Calculated after-1800 round-trips."""
        d = self._make(Date.QUAL_CALCULATED, Date.MOD_AFTER, 1800)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(d2.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d2.get_year(), 1800)

    def test_span_roundtrip(self):
        """Span 1900–1910 round-trips."""
        d = Date()
        d.set(
            Date.QUAL_NONE,
            Date.MOD_SPAN,
            Date.CAL_GREGORIAN,
            (0, 0, 1900, False) + (0, 0, 1910, False),
        )
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_SPAN)
        self.assertEqual(d2.get_start_date()[:3], (0, 0, 1900))
        self.assertEqual(d2.get_stop_date()[:3], (0, 0, 1910))

    def test_range_roundtrip(self):
        """Range 1900–1910 round-trips."""
        d = Date()
        d.set(
            Date.QUAL_NONE,
            Date.MOD_RANGE,
            Date.CAL_GREGORIAN,
            (0, 0, 1900, False) + (0, 0, 1910, False),
        )
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_RANGE)
        self.assertEqual(d2.get_start_date()[:3], (0, 0, 1900))
        self.assertEqual(d2.get_stop_date()[:3], (0, 0, 1910))


# -------------------------------------------------------------------------
#
# Traditional Chinese (zh_TW) — display tests
#
# -------------------------------------------------------------------------
class TestDateDisplayZH_TW(unittest.TestCase):
    """Verify Traditional Chinese date display format."""

    def setUp(self):
        """Create displayer using format 1 (numeric, non-ISO)."""
        self.dd = DateDisplayZH_TW(format=1)

    def _date(self, qual, mod, year, month=0, day=0, cal=Date.CAL_GREGORIAN):
        """Return a Date with the given attributes."""
        d = Date()
        d.set(qual, mod, cal, (day, month, year, False))
        return d

    def test_year_only(self):
        """Year-only date displays as '1949年'."""
        d = self._date(Date.QUAL_NONE, Date.MOD_NONE, 1949)
        self.assertEqual(self.dd.display(d), "1949年")

    def test_before_year(self):
        """'before 2000' displays as '2000年以前'."""
        d = self._date(Date.QUAL_NONE, Date.MOD_BEFORE, 2000)
        self.assertEqual(self.dd.display(d), "2000年以前")

    def test_after_year(self):
        """'after 1949' displays as '1949年以後'."""
        d = self._date(Date.QUAL_NONE, Date.MOD_AFTER, 1949)
        self.assertEqual(self.dd.display(d), "1949年以後")

    def test_about_year(self):
        """'about 1850' displays as '大約1850年'."""
        d = self._date(Date.QUAL_NONE, Date.MOD_ABOUT, 1850)
        self.assertEqual(self.dd.display(d), "大約1850年")

    def test_estimated_year(self):
        """Estimated 1800 displays as '估計為1800年'."""
        d = self._date(Date.QUAL_ESTIMATED, Date.MOD_NONE, 1800)
        self.assertEqual(self.dd.display(d), "估計為1800年")

    def test_calculated_year_month(self):
        """Calculated 1776-06 displays as '推算為西元1776年6月'."""
        d = self._date(Date.QUAL_CALCULATED, Date.MOD_NONE, 1776, month=6)
        self.assertEqual(self.dd.display(d), "推算為西元1776年6月")

    def test_estimated_before(self):
        """Estimated before 1900 displays as '估計早於1900年'."""
        d = self._date(Date.QUAL_ESTIMATED, Date.MOD_BEFORE, 1900)
        self.assertEqual(self.dd.display(d), "估計早於1900年")

    def test_calculated_after(self):
        """Calculated after 1800 displays as '推算晚於1800年'."""
        d = self._date(Date.QUAL_CALCULATED, Date.MOD_AFTER, 1800)
        self.assertEqual(self.dd.display(d), "推算晚於1800年")

    def test_before_year_is_postfix(self):
        """'before 2000' has 以前 AFTER the year, not before."""
        d = self._date(Date.QUAL_NONE, Date.MOD_BEFORE, 2000)
        result = self.dd.display(d)
        self.assertTrue(result.endswith("以前"), msg=repr(result))
        self.assertFalse(result.startswith("以前"), msg=repr(result))

    def test_after_year_is_postfix(self):
        """'after 2000' has 以後 AFTER the year, not before."""
        d = self._date(Date.QUAL_NONE, Date.MOD_AFTER, 2000)
        result = self.dd.display(d)
        self.assertTrue(result.endswith("以後"), msg=repr(result))
        self.assertFalse(result.startswith("以後"), msg=repr(result))

    def test_about_year_is_prefix(self):
        """'about 2000' has 大約 BEFORE the year."""
        d = self._date(Date.QUAL_NONE, Date.MOD_ABOUT, 2000)
        result = self.dd.display(d)
        self.assertTrue(result.startswith("大約"), msg=repr(result))

    def test_span(self):
        """Span 1900–1910 displays as '自1900年至1910年'."""
        d = Date()
        d.set(
            Date.QUAL_NONE,
            Date.MOD_SPAN,
            Date.CAL_GREGORIAN,
            (0, 0, 1900, False) + (0, 0, 1910, False),
        )
        self.assertEqual(self.dd.display(d), "自1900年至1910年")

    def test_range(self):
        """Range 1900–1910 displays as '介於1900年與1910年之間'."""
        d = Date()
        d.set(
            Date.QUAL_NONE,
            Date.MOD_RANGE,
            Date.CAL_GREGORIAN,
            (0, 0, 1900, False) + (0, 0, 1910, False),
        )
        self.assertEqual(self.dd.display(d), "介於1900年與1910年之間")


# -------------------------------------------------------------------------
#
# Traditional Chinese (zh_TW) — parser tests
#
# -------------------------------------------------------------------------
class TestDateParserZH_TW(unittest.TestCase):
    """Verify that all display forms parse back correctly in Traditional Chinese."""

    def setUp(self):
        """Create parser instance."""
        self.dp = DateParserZH_TW()

    def _parse(self, text):
        """Parse text and return a Date."""
        d = Date()
        self.dp.set_date(d, text)
        return d

    def test_year_only_parses(self):
        """'1949年' parses as year 1949, no modifier."""
        d = self._parse("1949年")
        self.assertEqual(d.get_year(), 1949)
        self.assertEqual(d.get_modifier(), Date.MOD_NONE)

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

    def test_about_no_space_parses(self):
        """'大約1850年' (no space) parses as MOD_ABOUT, year 1850."""
        d = self._parse("大約1850年")
        self.assertEqual(d.get_modifier(), Date.MOD_ABOUT)
        self.assertEqual(d.get_year(), 1850)

    def test_estimated_parses(self):
        """'估計為1800年' parses as QUAL_ESTIMATED, year 1800."""
        d = self._parse("估計為1800年")
        self.assertEqual(d.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d.get_modifier(), Date.MOD_NONE)
        self.assertEqual(d.get_year(), 1800)

    def test_calculated_year_month_parses(self):
        """'推算為西元1776年6月' parses as QUAL_CALCULATED, year 1776, month 6."""
        d = self._parse("推算為西元1776年6月")
        self.assertEqual(d.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(d.get_modifier(), Date.MOD_NONE)
        self.assertEqual(d.get_year(), 1776)
        self.assertEqual(d.get_month(), 6)

    def test_estimated_before_parses(self):
        """'估計早於1900年' parses as QUAL_ESTIMATED + MOD_BEFORE, year 1900."""
        d = self._parse("估計早於1900年")
        self.assertEqual(d.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 1900)

    def test_calculated_after_parses(self):
        """'推算晚於1800年' parses as QUAL_CALCULATED + MOD_AFTER, year 1800."""
        d = self._parse("推算晚於1800年")
        self.assertEqual(d.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(d.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d.get_year(), 1800)

    def test_xiyuan_year_month_parses(self):
        """'西元2000年3月' (dhformat output) parses as year 2000, month 3."""
        d = self._parse("西元2000年3月")
        self.assertEqual(d.get_year(), 2000)
        self.assertEqual(d.get_month(), 3)

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

    def test_old_estimated_still_parses(self):
        """'據估計 1800年' (old format) still parses as QUAL_ESTIMATED."""
        d = self._parse("據估計 1800年")
        self.assertEqual(d.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d.get_year(), 1800)


# -------------------------------------------------------------------------
#
# Traditional Chinese (zh_TW) — round-trip tests
#
# -------------------------------------------------------------------------
class TestRoundTripZH_TW(unittest.TestCase):
    """Display then re-parse should recover the original date attributes."""

    def setUp(self):
        """Create parser and displayer pair."""
        self.dp = DateParserZH_TW()
        self.dd = DateDisplayZH_TW(format=1)

    def _make(self, qual, mod, year, month=0, day=0, cal=Date.CAL_GREGORIAN):
        """Build a Date with the given attributes."""
        d = Date()
        d.set(qual, mod, cal, (day, month, year, False))
        return d

    def _roundtrip(self, d):
        """Display then re-parse; return the re-parsed Date."""
        text = self.dd.display(d)
        d2 = Date()
        self.dp.set_date(d2, text)
        return d2

    def test_year_only_roundtrip(self):
        """Year-only date round-trips."""
        d = self._make(Date.QUAL_NONE, Date.MOD_NONE, 1949)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_year(), 1949)
        self.assertEqual(d2.get_modifier(), Date.MOD_NONE)

    def test_before_roundtrip(self):
        """Before-2000 round-trips through display and parse."""
        d = self._make(Date.QUAL_NONE, Date.MOD_BEFORE, 2000)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d2.get_year(), 2000)

    def test_after_roundtrip(self):
        """After-1949 round-trips through display and parse."""
        d = self._make(Date.QUAL_NONE, Date.MOD_AFTER, 1949)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d2.get_year(), 1949)

    def test_about_roundtrip(self):
        """About-1850 round-trips."""
        d = self._make(Date.QUAL_NONE, Date.MOD_ABOUT, 1850)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_ABOUT)
        self.assertEqual(d2.get_year(), 1850)

    def test_estimated_roundtrip(self):
        """Estimated-1800 round-trips."""
        d = self._make(Date.QUAL_ESTIMATED, Date.MOD_NONE, 1800)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d2.get_modifier(), Date.MOD_NONE)
        self.assertEqual(d2.get_year(), 1800)

    def test_calculated_year_month_roundtrip(self):
        """Calculated 1776-06 round-trips."""
        d = self._make(Date.QUAL_CALCULATED, Date.MOD_NONE, 1776, month=6)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(d2.get_year(), 1776)
        self.assertEqual(d2.get_month(), 6)

    def test_estimated_before_roundtrip(self):
        """Estimated before-1900 round-trips."""
        d = self._make(Date.QUAL_ESTIMATED, Date.MOD_BEFORE, 1900)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_quality(), Date.QUAL_ESTIMATED)
        self.assertEqual(d2.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d2.get_year(), 1900)

    def test_calculated_after_roundtrip(self):
        """Calculated after-1800 round-trips."""
        d = self._make(Date.QUAL_CALCULATED, Date.MOD_AFTER, 1800)
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_quality(), Date.QUAL_CALCULATED)
        self.assertEqual(d2.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d2.get_year(), 1800)

    def test_span_roundtrip(self):
        """Span 1900–1910 round-trips."""
        d = Date()
        d.set(
            Date.QUAL_NONE,
            Date.MOD_SPAN,
            Date.CAL_GREGORIAN,
            (0, 0, 1900, False) + (0, 0, 1910, False),
        )
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_SPAN)
        self.assertEqual(d2.get_start_date()[:3], (0, 0, 1900))
        self.assertEqual(d2.get_stop_date()[:3], (0, 0, 1910))

    def test_range_roundtrip(self):
        """Range 1900–1910 round-trips."""
        d = Date()
        d.set(
            Date.QUAL_NONE,
            Date.MOD_RANGE,
            Date.CAL_GREGORIAN,
            (0, 0, 1900, False) + (0, 0, 1910, False),
        )
        d2 = self._roundtrip(d)
        self.assertEqual(d2.get_modifier(), Date.MOD_RANGE)
        self.assertEqual(d2.get_start_date()[:3], (0, 0, 1900))
        self.assertEqual(d2.get_stop_date()[:3], (0, 0, 1910))


if __name__ == "__main__":
    unittest.main()
