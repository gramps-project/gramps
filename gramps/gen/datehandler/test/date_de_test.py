# -*- coding: utf-8 -*-
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
Unit tests for the German date parser.

Bug 0013163: with the German UI, entering "bis 1760" ("until 1760") as a
date was silently converted to "0.8.1760" (August 1760).  "bis" was not in
the German modifier table, so the parser fell through to month-name matching
and matched the Old-German harvest-moon month name "bisemond" (= August).

"bis" is now an entry in ``DateParserDE.modifier_to_int`` mapping to
``Date.MOD_TO``, so "bis 1760" parses as a to/until date for the year 1760
with no month, never August.
"""

import unittest

from ...lib.date import Date
from .._date_de import DateParserDE


class DateParserDETest(unittest.TestCase):
    """Exercise ``DateParserDE.parse`` for the bug-13163 German "bis" case."""

    def setUp(self):
        self.parser = DateParserDE()

    def test_bis_year_is_mod_to_not_august(self):
        """
        Bug 13163 repro: "bis 1760" must parse as MOD_TO (to/until) of the
        year 1760, NOT as August (month 8) 1760.
        """
        date = self.parser.parse("bis 1760")
        self.assertEqual(date.get_modifier(), Date.MOD_TO)
        self.assertEqual(date.get_year(), 1760)
        # The reported "0.8.1760" August conversion: month must be 0 (no
        # month), never 8 (August / "bisemond").
        self.assertEqual(date.get_month(), 0)
        self.assertNotEqual(date.get_month(), 8)


if __name__ == "__main__":
    unittest.main()
