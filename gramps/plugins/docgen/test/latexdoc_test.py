#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Eduard Ralph
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
Unittest for the LaTeX docgen multicolumn counter (bug 13418).
"""

import unittest

from gramps.plugins.docgen.latexdoc import str_incr, MULTCOL_COUNT_BASE


# ------------------------------------------------------------
#
# StrIncrTest
#
# ------------------------------------------------------------
class StrIncrTest(unittest.TestCase):
    """
    ``str_incr`` generates the column identifiers used when a LaTeX
    table has spanning (multicolumn) cells. Before the fix the
    increment loop iterated the list's *elements* rather than its
    indices, so the second value raised
    ``TypeError: list indices must be integers or slices, not str``.
    That second ``next()`` is reached whenever a table has two or more
    multicolumns, e.g. a styled note containing subscript/strikeout
    (bug 13418).
    """

    def test_yields_successive_ids_without_typeerror(self):
        counter = str_incr(MULTCOL_COUNT_BASE)
        values = [next(counter) for _ in range(28)]
        self.assertEqual(values[0], "aaa")
        self.assertEqual(values[1], "aab")
        self.assertEqual(values[25], "aaz")
        self.assertEqual(values[26], "aba")  # carry into the next column
        self.assertEqual(values[27], "abb")

    def test_carry_with_short_base(self):
        counter = str_incr("az")
        self.assertEqual(next(counter), "az")
        self.assertEqual(next(counter), "ba")  # full carry


if __name__ == "__main__":
    unittest.main()
