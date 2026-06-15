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

import types
import unittest

from gramps.plugins.docgen.latexdoc import (
    HI_SPACE,
    HI_STRUT,
    LO_SPACE,
    LO_STRUT,
    NORMAL_END,
    TabCell,
    TabMem,
    TabRow,
    VerticalFineTuning,
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


class TestVerticalFineTuningDecorate(unittest.TestCase):
    def setUp(self):
        self.vft = VerticalFineTuning()

    def test_hi_strut_float_becomes_grupstrut(self):
        self.assertEqual(self.vft.decorate(HI_STRUT, "1.0"), "\\grupstrut{1.0ex}")

    def test_lo_strut_float_becomes_grdownstrut(self):
        self.assertEqual(self.vft.decorate(LO_STRUT, "0.5"), "\\grdownstrut{0.5ex}")

    def test_hi_space_float_becomes_ex_measure(self):
        self.assertEqual(self.vft.decorate(HI_SPACE, "2.0"), "2.0ex")

    def test_lo_space_float_becomes_ex_measure(self):
        self.assertEqual(self.vft.decorate(LO_SPACE, "3.0"), "3.0ex")

    def test_non_float_passes_through(self):
        self.assertEqual(self.vft.decorate(HI_SPACE, "-\\parskip"), "-\\parskip")

    def test_negative_float_passes_through_for_space(self):
        # negative floats match FLOAT_PAT
        self.assertEqual(self.vft.decorate(LO_SPACE, "-1.0"), "-1.0ex")


class TestVerticalFineTuningGetVAdjust(unittest.TestCase):
    def setUp(self):
        self.vft = VerticalFineTuning()

    def test_known_tail_style_returns_strut(self):
        # "DR-First-Entry" → tail "First-Entry" → HI_STRUT value "1.0" → grupstrut
        result = self.vft.get_v_adjust(HI_STRUT, "DR-First-Entry")
        self.assertEqual(result, "\\grupstrut{1.0ex}")

    def test_known_cmpl_style_returns_measure(self):
        # "EOL" is a cmpl_vals key for HI_SPACE → "1.0" → "1.0ex"
        result = self.vft.get_v_adjust(HI_SPACE, "EOL")
        self.assertEqual(result, "1.0ex")

    def test_unknown_style_returns_vacant(self):
        result = self.vft.get_v_adjust(HI_STRUT, "Unknown-Style")
        self.assertEqual(result, "")  # vacant[HI_STRUT] == ""

    def test_unknown_style_hi_space_returns_vacant(self):
        result = self.vft.get_v_adjust(HI_SPACE, "Unknown-Style")
        self.assertEqual(result, "0ex")  # vacant[HI_SPACE] == "0ex"

    def test_lo_strut_known_style(self):
        result = self.vft.get_v_adjust(LO_STRUT, "DR-ParentName")
        self.assertEqual(result, "\\grdownstrut{0.5ex}")


class TestMkCompleteRow(unittest.TestCase):
    """Test LaTeXDoc.mk_complete_row via a minimal stub object."""

    def _make_stub(self, counter_vals=None):
        stub = types.SimpleNamespace()
        stub.multcol_alph_counter = iter(counter_vals or [])
        return stub

    def _make_row(self, cells, tail=NORMAL_END, addit=""):
        row = TabRow()
        row.cells = cells
        row.tail = tail
        row.addit = addit
        return row

    def test_single_cell_row(self):
        from gramps.plugins.docgen.latexdoc import LaTeXDoc

        stub = self._make_stub()
        row = self._make_row([TabCell("a", 1, "{l}", "Hello")])
        result = LaTeXDoc.mk_complete_row(stub, row, None)
        self.assertIn("\\grcolpart", result)
        self.assertIn("{l}", result)
        self.assertIn("Hello", result)
        self.assertIn("\\grtempwidtha", result)
        self.assertTrue(result.endswith(NORMAL_END))

    def test_two_cell_row_joined_with_ampersand(self):
        from gramps.plugins.docgen.latexdoc import LaTeXDoc

        stub = self._make_stub()
        cells = [TabCell("a", 1, "{l}", "Col1"), TabCell("b", 1, "{l}", "Col2")]
        row = self._make_row(cells)
        result = LaTeXDoc.mk_complete_row(stub, row, None)
        self.assertIn("Col1", result)
        self.assertIn("Col2", result)
        self.assertIn(" & ", result)

    def test_phantom_cell_skipped(self):
        from gramps.plugins.docgen.latexdoc import LaTeXDoc

        stub = self._make_stub()
        cells = [TabCell("a", 0, "", ""), TabCell("b", 1, "{l}", "Real")]
        row = self._make_row(cells)
        result = LaTeXDoc.mk_complete_row(stub, row, None)
        # phantom cell (span==0) should be omitted — no ' & ' separator
        self.assertNotIn(" & ", result)
        self.assertIn("Real", result)

    def test_last_parameter_slices_cells(self):
        from gramps.plugins.docgen.latexdoc import LaTeXDoc

        stub = self._make_stub()
        cells = [TabCell("a", 1, "{l}", "A"), TabCell("b", 1, "{l}", "B")]
        row = self._make_row(cells)
        result = LaTeXDoc.mk_complete_row(stub, row, -1)
        self.assertIn("A", result)
        self.assertNotIn("B", result)


if __name__ == "__main__":
    unittest.main()
