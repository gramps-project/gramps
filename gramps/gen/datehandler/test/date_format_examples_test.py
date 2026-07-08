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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Tests for the date format example rendering used in the Preferences date
format drop-down (configure.py).
"""

import unittest

from gramps.gen.lib.date import Date
from gramps.gen.datehandler import get_date_formats
from gramps.gen.const import GRAMPS_LOCALE as glocale


class TestDateFormatExamples(unittest.TestCase):
    """Verify that a rendered example can be produced for every date format."""

    GRAMPS_BIRTHDAY = Date(2001, 4, 21)

    def _render_example(self, fmt_index: int) -> str:
        """Return the rendered example string for the given format index."""
        tmp_displayer = glocale.date_displayer.__class__(
            format=fmt_index, blocale=glocale
        )
        return tmp_displayer.display(self.GRAMPS_BIRTHDAY)

    def test_all_formats_produce_nonempty_string(self):
        """Every format index must render to a non-empty string."""
        formats = get_date_formats()
        for i, fmt_name in enumerate(formats):
            with self.subTest(format_index=i, format_name=fmt_name):
                example = self._render_example(i)
                self.assertTrue(
                    example,
                    f"Format {i} ({fmt_name!r}) rendered an empty string",
                )

    def test_all_formats_contain_2001(self):
        """Every rendered example must contain the year 2001."""
        formats = get_date_formats()
        for i, fmt_name in enumerate(formats):
            with self.subTest(format_index=i, format_name=fmt_name):
                example = self._render_example(i)
                self.assertIn(
                    "2001",
                    example,
                    f"Format {i} ({fmt_name!r}) example {example!r} missing year",
                )

    def test_format_count_is_positive(self):
        """There must be at least one date format available."""
        self.assertGreater(len(get_date_formats()), 0)


if __name__ == "__main__":
    unittest.main()
