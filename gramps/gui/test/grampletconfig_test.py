#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Gramps project
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
Tests for gramplet view configuration helpers.
"""

import unittest

from gramps.gui.grampletconfig import MAX_GRAMPLET_COLUMNS, clamp_column_count


class GrampletConfigTest(unittest.TestCase):
    """
    Test gramplet configuration value normalization.
    """

    def test_clamp_column_count_keeps_supported_values(self):
        self.assertEqual(clamp_column_count(1), 1)
        self.assertEqual(clamp_column_count(2), 2)
        self.assertEqual(clamp_column_count(MAX_GRAMPLET_COLUMNS), MAX_GRAMPLET_COLUMNS)

    def test_clamp_column_count_raises_low_values_to_one(self):
        self.assertEqual(clamp_column_count(0), 1)
        self.assertEqual(clamp_column_count(-5), 1)

    def test_clamp_column_count_limits_large_values(self):
        self.assertEqual(clamp_column_count(1000), MAX_GRAMPLET_COLUMNS)

    def test_clamp_column_count_accepts_config_file_strings(self):
        self.assertEqual(clamp_column_count("1000"), MAX_GRAMPLET_COLUMNS)


if __name__ == "__main__":
    unittest.main()
