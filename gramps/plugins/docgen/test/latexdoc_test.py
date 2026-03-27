#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  Gramps Development Team
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

"""Tests for latexdoc module utility functions."""

import unittest

from gramps.plugins.docgen.latexdoc import (
    TabCell,
    TabMem,
    TabRow,
    get_charform,
    get_numform,
    latexescape,
    latexescapeverbatim,
    map_font_size,
    str_incr,
)


class TestLatexEscape(unittest.TestCase):
    def test_ampersand(self):
        self.assertEqual(latexescape("a & b"), "a \\& b")

    def test_dollar(self):
        self.assertEqual(latexescape("$100"), "\\$100")

    def test_percent(self):
        self.assertEqual(latexescape("100%"), "100\\%")

    def test_hash(self):
        self.assertEqual(latexescape("#1"), "\\#1")

    def test_underscore(self):
        self.assertEqual(latexescape("a_b"), "a\\_b")

    def test_braces(self):
        self.assertEqual(latexescape("a{b}"), "a\\{b\\}")

    def test_multiple_specials(self):
        self.assertEqual(
            latexescape("cost: $10 & 100%"),
            "cost: \\$10 \\& 100\\%",
        )

    def test_arrow_substitution(self):
        self.assertEqual(latexescape("\u2192"), "$\\longrightarrow$")

    def test_plain_text_unchanged(self):
        self.assertEqual(latexescape("hello world"), "hello world")


class TestLatexEscapeVerbatim(unittest.TestCase):
    def test_space_escaped(self):
        self.assertEqual(latexescapeverbatim("a b"), "a\\ b")

    def test_newline_escaped(self):
        result = latexescapeverbatim("line1\nline2")
        self.assertIn("\\newline", result)
        self.assertIn("line1", result)
        self.assertIn("line2", result)

    def test_specials_also_escaped(self):
        result = latexescapeverbatim("a & b")
        self.assertIn("\\&", result)


class TestGetCharform(unittest.TestCase):
    def test_first_column(self):
        self.assertEqual(get_charform(0), "a")

    def test_last_column(self):
        self.assertEqual(get_charform(25), "z")

    def test_mid_column(self):
        self.assertEqual(get_charform(1), "b")
        self.assertEqual(get_charform(12), "m")

    def test_too_many_columns_raises(self):
        with self.assertRaises(ValueError):
            get_charform(26)


class TestGetNumform(unittest.TestCase):
    def test_first(self):
        self.assertEqual(get_numform("a"), 0)

    def test_last(self):
        self.assertEqual(get_numform("z"), 25)

    def test_roundtrip(self):
        for i in range(26):
            self.assertEqual(get_numform(get_charform(i)), i)


class TestStrIncr(unittest.TestCase):
    def test_basic_increment(self):
        gen = str_incr("aa")
        self.assertEqual(next(gen), "aa")
        self.assertEqual(next(gen), "ab")
        self.assertEqual(next(gen), "ac")

    def test_carry(self):
        gen = str_incr("ay")
        self.assertEqual(next(gen), "ay")
        self.assertEqual(next(gen), "az")
        self.assertEqual(next(gen), "ba")

    def test_double_carry(self):
        gen = str_incr("azz")
        self.assertEqual(next(gen), "azz")
        self.assertEqual(next(gen), "baa")

    def test_exhaustion_raises(self):
        gen = str_incr("z")
        next(gen)  # 'z'
        with self.assertRaises(ValueError):
            next(gen)

    def test_default_base(self):
        from gramps.plugins.docgen.latexdoc import MULTCOL_COUNT_BASE

        self.assertEqual(MULTCOL_COUNT_BASE, "aaa")
        gen = str_incr(MULTCOL_COUNT_BASE)
        self.assertEqual(next(gen), "aaa")
        self.assertEqual(next(gen), "aab")


class TestMapFontSize(unittest.TestCase):
    def test_small_size(self):
        self.assertEqual(map_font_size(8), "footnotesize")

    def test_large_size(self):
        self.assertEqual(map_font_size(24), "Huge")

    def test_tiny(self):
        self.assertEqual(map_font_size(4), "tiny")


class TestTabClasses(unittest.TestCase):
    def test_tabcell_attributes(self):
        cell = TabCell("a", 1, "{l}", "some content")
        self.assertEqual(cell.colchar, "a")
        self.assertEqual(cell.span, 1)
        self.assertEqual(cell.head, "{l}")
        self.assertEqual(cell.content, "some content")

    def test_tabrow_starts_empty(self):
        row = TabRow()
        self.assertEqual(row.cells, [])
        self.assertEqual(row.addit, "")

    def test_tabrow_add_cell(self):
        row = TabRow()
        cell = TabCell("a", 1, "{l}", "text")
        row.cells.append(cell)
        self.assertEqual(len(row.cells), 1)
        self.assertEqual(row.cells[0].content, "text")

    def test_tabmem_starts_empty(self):
        mem = TabMem("\\begin{longtable}{ll}")
        self.assertEqual(mem.head, "\\begin{longtable}{ll}")
        self.assertEqual(mem.rows, [])

    def test_tabmem_add_row(self):
        mem = TabMem("\\begin{longtable}{ll}")
        row = TabRow()
        mem.rows.append(row)
        self.assertEqual(len(mem.rows), 1)


if __name__ == "__main__":
    unittest.main()
