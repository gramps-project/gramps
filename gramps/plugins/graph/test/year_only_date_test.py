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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Unit test for the ``_year_only_date`` helper used by the Family Lines
Graph and Relationship Graph reports.

Bug 0004658: when the "Limit dates to years only" report option is on,
modifier (before/after/about), quality (estimated/calculated) and the
second-stop of compound dates must be preserved; the old code built a
fresh ``Date(date.get_year())`` and dropped all of those.
"""

import unittest

from gramps.gen.lib import Date
from gramps.plugins.graph.gvfamilylines import _year_only_date as fl_year_only
from gramps.plugins.graph.gvrelgraph import _year_only_date as rg_year_only


def _make_simple(modifier, quality=Date.QUAL_NONE, day=15, month=6, year=1923):
    """Build a non-compound Date with the given modifier and quality."""
    date = Date()
    date.set(
        quality,
        modifier,
        Date.CAL_GREGORIAN,
        (day, month, year, False),
        "",
    )
    return date


def _make_compound(modifier, year1=1923, year2=1925):
    """Build a compound (range/span) Date with two distinct year stops."""
    date = Date()
    date.set(
        Date.QUAL_NONE,
        modifier,
        Date.CAL_GREGORIAN,
        (15, 6, year1, False, 20, 9, year2, False),
        "",
    )
    return date


class YearOnlyDateTest(unittest.TestCase):
    """Bug 4658: years-only mode must preserve modifier/quality/stop year."""

    # ------------------------------------------------------------------
    # Modifier preservation -- the symptom the bug names.
    # ------------------------------------------------------------------

    def test_before_preserves_modifier(self):
        """Reporter's case: 'before 1923' must stay 'before 1923'."""
        src = _make_simple(Date.MOD_BEFORE)
        for fn in (fl_year_only, rg_year_only):
            res = fn(src)
            self.assertEqual(res.get_modifier(), Date.MOD_BEFORE)
            self.assertEqual(res.get_year(), 1923)

    def test_after_preserves_modifier(self):
        src = _make_simple(Date.MOD_AFTER)
        for fn in (fl_year_only, rg_year_only):
            res = fn(src)
            self.assertEqual(res.get_modifier(), Date.MOD_AFTER)
            self.assertEqual(res.get_year(), 1923)

    def test_about_preserves_modifier(self):
        src = _make_simple(Date.MOD_ABOUT)
        for fn in (fl_year_only, rg_year_only):
            res = fn(src)
            self.assertEqual(res.get_modifier(), Date.MOD_ABOUT)
            self.assertEqual(res.get_year(), 1923)

    # ------------------------------------------------------------------
    # Quality preservation -- estimated/calculated must survive too.
    # ------------------------------------------------------------------

    def test_estimated_quality_preserved(self):
        src = _make_simple(Date.MOD_NONE, quality=Date.QUAL_ESTIMATED)
        for fn in (fl_year_only, rg_year_only):
            self.assertEqual(fn(src).get_quality(), Date.QUAL_ESTIMATED)

    def test_calculated_quality_preserved(self):
        src = _make_simple(Date.MOD_NONE, quality=Date.QUAL_CALCULATED)
        for fn in (fl_year_only, rg_year_only):
            self.assertEqual(fn(src).get_quality(), Date.QUAL_CALCULATED)

    # ------------------------------------------------------------------
    # Year-only truncation -- month and day must be zeroed.
    # ------------------------------------------------------------------

    def test_month_day_zeroed(self):
        src = _make_simple(Date.MOD_NONE, day=15, month=6, year=1923)
        for fn in (fl_year_only, rg_year_only):
            res = fn(src)
            self.assertEqual(res.get_year(), 1923)
            self.assertEqual(res.get_month(), 0)
            self.assertEqual(res.get_day(), 0)

    # ------------------------------------------------------------------
    # Compound dates -- the old code threw away the second stop entirely.
    # ------------------------------------------------------------------

    def test_range_keeps_both_years(self):
        src = _make_compound(Date.MOD_RANGE, 1923, 1925)
        for fn in (fl_year_only, rg_year_only):
            res = fn(src)
            self.assertEqual(res.get_modifier(), Date.MOD_RANGE)
            self.assertEqual(res.get_year(), 1923)
            self.assertEqual(res.get_stop_year(), 1925)

    def test_span_keeps_both_years(self):
        src = _make_compound(Date.MOD_SPAN, 1923, 1925)
        for fn in (fl_year_only, rg_year_only):
            res = fn(src)
            self.assertEqual(res.get_modifier(), Date.MOD_SPAN)
            self.assertEqual(res.get_year(), 1923)
            self.assertEqual(res.get_stop_year(), 1925)

    # ------------------------------------------------------------------
    # Regression guard: behaviour for the unmodified common case must
    # match the previous output (year-only, no modifier).
    # ------------------------------------------------------------------

    def test_plain_date_collapses_to_year(self):
        src = _make_simple(Date.MOD_NONE, day=15, month=6, year=1923)
        for fn in (fl_year_only, rg_year_only):
            res = fn(src)
            self.assertEqual(res.get_modifier(), Date.MOD_NONE)
            self.assertEqual(res.get_quality(), Date.QUAL_NONE)
            self.assertEqual(res.get_year(), 1923)
            self.assertEqual(res.get_month(), 0)
            self.assertEqual(res.get_day(), 0)

    # ------------------------------------------------------------------
    # The helper is intentionally duplicated in both plugins (no shared
    # private module in gramps/plugins/graph/). Guard against the copies
    # drifting.
    # ------------------------------------------------------------------

    def test_helpers_agree(self):
        cases = [
            _make_simple(Date.MOD_NONE),
            _make_simple(Date.MOD_BEFORE),
            _make_simple(Date.MOD_AFTER),
            _make_simple(Date.MOD_ABOUT),
            _make_simple(Date.MOD_NONE, quality=Date.QUAL_ESTIMATED),
            _make_simple(Date.MOD_NONE, quality=Date.QUAL_CALCULATED),
            _make_compound(Date.MOD_RANGE, 1900, 1910),
            _make_compound(Date.MOD_SPAN, 1900, 1910),
        ]
        for src in cases:
            self.assertEqual(
                fl_year_only(src).serialize(),
                rg_year_only(src).serialize(),
                msg=f"helpers disagree for {src.serialize()}",
            )


if __name__ == "__main__":
    unittest.main()
