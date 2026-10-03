#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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

"""Unittests for the DNA segment display tab sort columns."""

# ------------------------
# Python modules
# ------------------------
import unittest

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.lib import DNASegment
from gramps.gui.editors.displaytabs.dnasegmentembedlist import (
    DNASegmentModel,
    DNASegmentEmbedList,
)


def _segment(chromosome="", start=0, end=0, shared_cm=0.0, snp_count=0):
    """Return a DNASegment carrying the given values."""
    seg = DNASegment()
    seg.set_chromosome(chromosome)
    seg.set_start_bp(start)
    seg.set_end_bp(end)
    seg.set_shared_cm(shared_cm)
    seg.set_snp_count(snp_count)
    return seg


def _sorted_display(model, display_col, sort_col):
    """Return the display values ordered by their sort column."""
    rows = [(row[sort_col], row[display_col]) for row in model]
    return [display for _, display in sorted(rows)]


class TestDNASegmentSortColumns(unittest.TestCase):
    """The tab sorts numeric fields by value, not by their text form."""

    def test_chromosome_orders_numerically(self):
        segments = [_segment(chromosome=c) for c in ("10", "2", "22", "1", "9")]
        model = DNASegmentModel(segments, None)
        self.assertEqual(
            _sorted_display(model, 0, DNASegmentModel.COL_SORT_CHROMOSOME),
            ["1", "2", "9", "10", "22"],
        )

    def test_chromosome_puts_x_y_and_mt_after_the_numbers(self):
        segments = [_segment(chromosome=c) for c in ("MT", "X", "1", "Y", "22")]
        model = DNASegmentModel(segments, None)
        self.assertEqual(
            _sorted_display(model, 0, DNASegmentModel.COL_SORT_CHROMOSOME),
            ["1", "22", "X", "Y", "MT"],
        )

    def test_start_orders_numerically(self):
        segments = [_segment(start=s) for s in (9000000, 100000000, 752721)]
        model = DNASegmentModel(segments, None)
        self.assertEqual(
            _sorted_display(model, 1, DNASegmentModel.COL_SORT_START),
            ["752721", "9000000", "100000000"],
        )

    def test_end_orders_numerically(self):
        segments = [_segment(end=e) for e in (20156313, 3512800, 107580985)]
        model = DNASegmentModel(segments, None)
        self.assertEqual(
            _sorted_display(model, 2, DNASegmentModel.COL_SORT_END),
            ["3512800", "20156313", "107580985"],
        )

    def test_shared_cm_orders_numerically(self):
        segments = [_segment(shared_cm=cm) for cm in (8.9, 15.2, 100.5, 7.0)]
        model = DNASegmentModel(segments, None)
        self.assertEqual(
            _sorted_display(model, 3, DNASegmentModel.COL_SORT_SHARED_CM),
            ["7.0", "8.9", "15.2", "100.5"],
        )

    def test_snp_count_orders_numerically(self):
        segments = [_segment(snp_count=n) for n in (421, 2185, 90)]
        model = DNASegmentModel(segments, None)
        self.assertEqual(
            _sorted_display(model, 4, DNASegmentModel.COL_SORT_SNP_COUNT),
            ["90", "421", "2185"],
        )

    def test_empty_values_sort_before_populated_ones(self):
        segments = [_segment(start=100), _segment(), _segment(start=5)]
        model = DNASegmentModel(segments, None)
        self.assertEqual(
            _sorted_display(model, 1, DNASegmentModel.COL_SORT_START),
            ["", "5", "100"],
        )

    def test_handle_column_still_holds_the_segment(self):
        seg = _segment(chromosome="7")
        model = DNASegmentModel([seg], None)
        self.assertIs(model[0][DNASegmentEmbedList._HANDLE_COL], seg)

    def test_columns_sort_on_their_sort_column(self):
        expected = {
            0: DNASegmentModel.COL_SORT_CHROMOSOME,
            1: DNASegmentModel.COL_SORT_START,
            2: DNASegmentModel.COL_SORT_END,
            3: DNASegmentModel.COL_SORT_SHARED_CM,
            4: DNASegmentModel.COL_SORT_SNP_COUNT,
        }
        for display_col, sort_col in expected.items():
            with self.subTest(column=display_col):
                self.assertEqual(
                    DNASegmentEmbedList._column_names[display_col][1], sort_col
                )


if __name__ == "__main__":
    unittest.main()
