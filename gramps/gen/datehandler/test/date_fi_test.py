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
Unit tests for the Finnish date display.

Bug 0012283: when the Finnish translation message catalog is not
installed (typical on Windows AIO where the user picked English
only), Gramps still loads the Finnish date handler, but the
``long_months`` list it gets from the localised DateStrings is a
list of plain ``str`` (English fallback) rather than a list of
``Lexeme``. The day-zero / no-inflect branch of
``DateDisplayFI.dd_dformat04`` then tried to format
``"{long_month.forms[IN]}"``, which raises
``AttributeError: 'str' object has no attribute 'forms'`` (or
``'f'`` on 5.1.x where the Lexeme attribute was named ``f``). All
the other branches of the same function already had the canonical
``hasattr(..., "forms")`` guard; only this one was missing.
"""

import unittest

from ...utils.grampslocale import GrampsLocale
from .._date_fi import DateDisplayFI


class FinnishDateNoLexemeTest(unittest.TestCase):
    """
    Exercise ``DateDisplayFI.dd_dformat04`` with a plain-``str``
    ``long_months`` list, mimicking the no-translation-installed
    environment that triggered bug 12283.
    """

    @classmethod
    def setUpClass(cls):
        # A Finnish DateDisplayFI works without the Finnish .mo
        # being installed -- it just falls back to English message
        # strings, which is exactly the bug scenario.
        cls.dd = DateDisplayFI(blocale=GrampsLocale(lang="fi"))

    # Non-Lexeme month list: index 0 unused, indices 1..12 are
    # plain English month names (what gettext returns when the
    # Finnish catalog is missing).
    NON_LEXEME_MONTHS = (
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )

    def test_month_only_no_inflect_does_not_raise(self):
        """
        Bug 12283 repro: day-zero date + ``inflect=""`` +
        non-Lexeme ``long_months`` used to raise ``AttributeError``.
        Must now return a plain "Month Year" string instead.
        """
        # date_val = (day, month, year, slash)
        date_val = (0, 5, 1945, False)
        result = self.dd.dd_dformat04(
            date_val, inflect="", long_months=self.NON_LEXEME_MONTHS
        )
        self.assertEqual(result, "May 1945")

    def test_month_only_no_inflect_no_exception_across_months(self):
        """
        Same guard, all 12 months. Asserts the defensive fallback
        never raises and always yields "<month> <year>".
        """
        for month in range(1, 13):
            with self.subTest(month=month):
                date_val = (0, month, 1900, False)
                result = self.dd.dd_dformat04(
                    date_val, inflect="", long_months=self.NON_LEXEME_MONTHS
                )
                self.assertEqual(result, f"{self.NON_LEXEME_MONTHS[month]} 1900")

    def test_year_only_unchanged(self):
        """
        Regression guard: a date with day=0 *and* month=0 still
        returns just the year, the same as before the fix.
        """
        date_val = (0, 0, 1945, False)
        result = self.dd.dd_dformat04(
            date_val, inflect="", long_months=self.NON_LEXEME_MONTHS
        )
        self.assertEqual(result, "1945")

    def test_full_date_unchanged(self):
        """
        Regression guard: the ``date_val[0] != 0`` branch already
        had a ``hasattr(..., "forms")`` guard before this PR. With
        non-Lexeme ``long_months`` it falls through to
        ``dd_dformat01`` (numeric). Make sure the bug fix didn't
        disturb that path.
        """
        date_val = (9, 5, 1945, False)
        result = self.dd.dd_dformat04(
            date_val, inflect="", long_months=self.NON_LEXEME_MONTHS
        )
        # dd_dformat01 returns numeric "DD.MM.YYYY" form for Finnish.
        # We don't assert the exact format string (that's a separate
        # concern); we just assert no exception and a non-empty result.
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
