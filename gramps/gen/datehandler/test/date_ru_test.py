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
Unit test for the Russian short-format date display.

In jralls's 2023-07-14 commit ``7f8455c867`` "Extract translation
classes from grampslocale.py", the ``Lexeme`` attribute used to
access inflected forms was renamed from ``.f`` to ``.forms``. That
commit updated every format-spec usage and almost every guard --
but missed the guard at ``_date_ru.py:165`` in
``DateDisplayRU.dd_dformat05``. The result is that ``hasattr(lexeme,
"f")`` always returns False (no ``Lexeme`` has ``.f`` after the
rename), so the no-Lexeme fallback always runs and the inflected
``.forms[Р]`` branch is dead code. Russian short-format dates
therefore skip inflection even when the Russian translations are
installed -- the *opposite* failure mode of bug 12283 (which is
about the *missing*-translation case).

The same idiom in the sibling ``dd_dformat04`` (line 142) was
correctly migrated, as were the format-spec accesses on lines 147
and 170. Only line 165 was forgotten.
"""

import unittest

from ...utils.grampslocale import GrampsLocale
from ...utils.grampstranslation import Lexeme
from .._date_ru import DateDisplayRU


class RussianDateDFormat05InflectionTest(unittest.TestCase):
    """
    Exercise ``DateDisplayRU.dd_dformat05`` with a ``Lexeme`` short
    month list (the translation-installed scenario) and verify the
    Russian-genitive (``Р``) form is selected, not the default str
    coercion.
    """

    @classmethod
    def setUpClass(cls):
        # The Russian translation catalog isn't required for this test
        # since we feed dd_dformat05 a synthetic Lexeme tuple directly.
        cls.dd = DateDisplayRU(blocale=GrampsLocale(lang="ru"))

    @staticmethod
    def _lexeme_months(genitive_prefix="GEN", nominative_prefix="NOM"):
        """Build a tuple of 13 entries (index 0 unused, 1..12 are
        Lexemes carrying a Russian-genitive (``Р``) form and a
        nominative fallback).

        The nominative form is intentionally placed *first* in the
        ordered dict, so that ``str(lexeme)`` (the bug path's
        fallback view, since Lexeme inherits from str and uses its
        first form as the str value) yields the nominative -- making
        the bug-path output distinguishable from the inflected-path
        output that uses the genitive ``.forms[Р]``. Without this
        ordering, both paths would render the same string and the
        test couldn't catch the regression.
        """
        return ("",) + tuple(
            Lexeme(
                [
                    ("И", f"{nominative_prefix}{m}"),
                    ("Р", f"{genitive_prefix}{m}"),
                ]
            )
            for m in range(1, 13)
        )

    def test_full_date_uses_genitive_form_when_lexemes_present(self):
        """
        Bug regression: with a Lexeme-bearing ``short_months`` and a
        day-non-zero date, ``dd_dformat05`` must emit the genitive
        (``Р``) form. Pre-fix the guard at ``_date_ru.py:165`` checked
        ``hasattr(..., "f")`` which never matches post-2023 Lexemes,
        so the function silently returned the nominative.
        """
        short_months = self._lexeme_months()
        # date_val = (day, month, year, slash)
        date_val = (9, 5, 1945, False)
        result = self.dd.dd_dformat05(date_val, inflect="", short_months=short_months)
        self.assertIn("GEN5", result)
        self.assertNotIn("NOM5", result)

    def test_genitive_form_across_all_months(self):
        """
        Same regression, exercised across every month. Asserts that
        the inflected branch is reached for each.
        """
        short_months = self._lexeme_months()
        for month in range(1, 13):
            with self.subTest(month=month):
                date_val = (9, month, 1945, False)
                result = self.dd.dd_dformat05(
                    date_val, inflect="", short_months=short_months
                )
                self.assertIn(f"GEN{month}", result)
                self.assertNotIn(f"NOM{month}", result)

    def test_full_date_with_non_lexeme_short_months_falls_back(self):
        """
        Regression guard: when ``short_months`` are plain ``str``
        (the no-translation-installed scenario), the function must
        still fall back to the uninflected form without raising.
        Mirrors the bug-12283 defensive-guard test on the Finnish
        side.
        """
        non_lexeme_months = (
            "",
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        )
        date_val = (9, 5, 1945, False)
        result = self.dd.dd_dformat05(
            date_val, inflect="", short_months=non_lexeme_months
        )
        # No assertion on exact text; just no exception and a
        # non-empty render. The exact str-fallback format is
        # "{day} {short_month} {year}" -> "9 May 1945".
        self.assertIn("9", result)
        self.assertIn("May", result)
        self.assertIn("1945", result)

    def test_dd_dformat04_long_form_unaffected(self):
        """
        Regression guard: the long-form guard at ``_date_ru.py:142``
        was already correctly updated to ``"forms"`` in the 2023
        rename. Confirm the long-form path still inflects properly.
        """
        long_months = self._lexeme_months(
            genitive_prefix="LGEN", nominative_prefix="LNOM"
        )
        date_val = (9, 5, 1945, False)
        result = self.dd.dd_dformat04(date_val, inflect="", long_months=long_months)
        self.assertIn("LGEN5", result)
        self.assertNotIn("LNOM5", result)


if __name__ == "__main__":
    unittest.main()
