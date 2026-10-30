# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  The Gramps project
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
Headless regression test for bug #13865.

On the Dashboard with a high "Number of Columns" (e.g. 20), adding a gramplet
placed it in an off-screen column with stray gaps.  The column for a drop / add
is computed by ``GrampletPane.drop_widget``
(``gramps.gui.widgets.grampletpane``) via
``gramps.gui.grampletlayout.column_index_for_x`` -- the production path routes
through that pure helper, so it is tested directly here without importing any
``gi`` / ``gramps.gui.widgets`` GUI module (which would need a display).
"""

import unittest

from ..grampletlayout import column_index_for_x


class TestColumnIndexForX(unittest.TestCase):
    """The added gramplet must land in a valid, on-screen column."""

    def test_bug_13865_high_column_count_stays_on_screen(self):
        """
        Reproduce the 13865 geometry: 20 homogeneous columns each wider than a
        twentieth of the viewport, so the content (6000px) overflows the
        visible viewport (800px) and scrolls.  Right-clicking below "Top
        Surnames" (column 0) drops at content-x 150.  The new gramplet must
        land in column 0, which is on screen -- not a far-right scrolled-off
        column.
        """
        viewport_width = 800
        col_width = 300  # homogeneous columns sized to the widest gramplet
        column_count = 20
        column_bounds = [(i * col_width, col_width) for i in range(column_count)]
        click_x = 150  # below Top Surnames, in column 0 (content coords)

        col = column_index_for_x(click_x, column_bounds)

        # Lands in the clicked (left-most) column ...
        self.assertEqual(col, 0)
        # ... and that column is on screen (its start is inside the viewport).
        start, _ = column_bounds[col]
        self.assertLess(
            start,
            viewport_width,
            "added gramplet was placed in an off-screen column (bug #13865)",
        )

    def test_old_viewport_division_would_go_off_screen(self):
        """
        Guard rail: the previous viewport-width division would, for the same
        click, choose a column scrolled off screen.  Documents *why* the
        helper maps against the real per-column allocation instead.
        """
        viewport_width = 800
        col_width = 300
        column_count = 20
        click_x = 150
        # The replaced formula: x < (viewport / n) * (i + 1).
        old_col = 0
        for i in range(column_count):
            if click_x < (viewport_width / column_count) * (i + 1):
                old_col = i
                break
        old_start = old_col * col_width
        self.assertGreaterEqual(
            old_start,
            viewport_width,
            "test premise broken: old formula should pick an off-screen column",
        )
        # The fixed helper does not.
        column_bounds = [(i * col_width, col_width) for i in range(column_count)]
        self.assertNotEqual(column_index_for_x(click_x, column_bounds), old_col)

    def test_index_always_in_range_for_any_count(self):
        """
        The invariant: for any configured column count and any drop position
        (including left of, inside, and right of the content) the index is in
        range -- never a nonexistent / off-screen column.
        """
        for column_count in range(1, 31):
            col_width = 120
            content_width = column_count * col_width
            column_bounds = [(i * col_width, col_width) for i in range(column_count)]
            for x in (
                -500,
                -1,
                0,
                1,
                content_width // 2,
                content_width,
                content_width + 5000,
            ):
                col = column_index_for_x(x, column_bounds)
                self.assertIn(
                    col,
                    range(column_count),
                    "x=%d, count=%d -> out-of-range column %d" % (x, column_count, col),
                )

    def test_click_inside_a_column_returns_that_column(self):
        """A click within column k's allocation maps to column k."""
        col_width = 100
        column_bounds = [(i * col_width, col_width) for i in range(10)]
        for k in range(10):
            mid_x = k * col_width + col_width // 2
            self.assertEqual(column_index_for_x(mid_x, column_bounds), k)

    def test_left_of_all_maps_to_first(self):
        column_bounds = [(i * 100, 100) for i in range(5)]
        self.assertEqual(column_index_for_x(-20, column_bounds), 0)

    def test_right_of_all_maps_to_last(self):
        column_bounds = [(i * 100, 100) for i in range(5)]
        self.assertEqual(column_index_for_x(999999, column_bounds), 4)

    def test_no_columns_is_defensive_zero(self):
        self.assertEqual(column_index_for_x(42, []), 0)


if __name__ == "__main__":
    unittest.main()
