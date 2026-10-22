#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  Gramps Development Team
# Copyright (C) 2026  Eduard Ralph
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""Tests for latexdoc module utility functions."""

import types
import unittest

from gramps.plugins.docgen.latexdoc import (
    NORMAL_END,
    TabCell,
    TabMem,
    TabRow,
    get_charform,
    get_numform,
    latexescape,
    latexescapeverbatim,
    map_font_size,
    pict_with_caption,
    pict_width_of,
    str_incr,
)


# ------------------------------------------------------------
#
# TestLatexEscape
#
# ------------------------------------------------------------
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


# ------------------------------------------------------------
#
# TestLatexEscapeVerbatim
#
# ------------------------------------------------------------
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


# ------------------------------------------------------------
#
# TestGetCharform
#
# ------------------------------------------------------------
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


# ------------------------------------------------------------
#
# TestGetNumform
#
# ------------------------------------------------------------
class TestGetNumform(unittest.TestCase):
    def test_first(self):
        self.assertEqual(get_numform("a"), 0)

    def test_last(self):
        self.assertEqual(get_numform("z"), 25)

    def test_roundtrip(self):
        for i in range(26):
            self.assertEqual(get_numform(get_charform(i)), i)


# ------------------------------------------------------------
#
# TestStrIncr
#
# ------------------------------------------------------------
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

    def test_yields_successive_ids_without_typeerror(self):
        # Regression for bug 13418: the second next() raised TypeError
        # when the increment loop iterated elements instead of indices.
        from gramps.plugins.docgen.latexdoc import MULTCOL_COUNT_BASE

        counter = str_incr(MULTCOL_COUNT_BASE)
        values = [next(counter) for _ in range(28)]
        self.assertEqual(values[0], "aaa")
        self.assertEqual(values[1], "aab")
        self.assertEqual(values[25], "aaz")
        self.assertEqual(values[26], "aba")  # carry into the next column
        self.assertEqual(values[27], "abb")


# ------------------------------------------------------------
#
# TestPictWithCaption
#
# ------------------------------------------------------------
class TestPictWithCaption(unittest.TestCase):
    def test_no_trailing_text(self):
        pict = "\\grmkpicture{a.jpg}{4.0}{4.0}{}"
        self.assertEqual(pict_with_caption(pict), pict)

    def test_trailing_text_becomes_label(self):
        pict = "\\grmkpicture{a.jpg}{4.0}{4.0}{}\\hfill\\footnotesize (Age: 50)"
        self.assertEqual(
            pict_with_caption(pict),
            "\\grmkpicture{a.jpg}{4.0}{4.0}{\\footnotesize (Age: 50)}",
        )

    def test_trailing_text_appended_to_label(self):
        pict = "\\grmkpicture{a.jpg}{4.0}{4.0}{a}(Age: 50)"
        self.assertEqual(
            pict_with_caption(pict), "\\grmkpicture{a.jpg}{4.0}{4.0}{a (Age: 50)}"
        )

    def test_trailing_text_with_braces(self):
        pict = "\\grmkpicture{a.jpg}{4.0}{4.0}{}x\\textsuperscript{3c}"
        self.assertEqual(
            pict_with_caption(pict),
            "\\grmkpicture{a.jpg}{4.0}{4.0}{x\\textsuperscript{3c}}",
        )

    def test_not_a_picture(self):
        self.assertEqual(pict_with_caption("text"), "text")

    def test_trailing_comment_dropped(self):
        """A trailing "%" must not end up in the label."""
        self.assertEqual(
            pict_with_caption("\\grmkpicture{a.jpg}{4.0}{4.0}{}%"),
            "\\grmkpicture{a.jpg}{4.0}{4.0}{}",
        )

    def test_further_caption_lines(self):
        self.assertEqual(
            pict_with_caption(
                "\\grmkpicture{a.jpg}{4.0}{4.0}{}(Age: 50)", ["(Height: 2m)", " "]
            ),
            "\\grmkpicture{a.jpg}{4.0}{4.0}{(Age: 50)\\newline (Height: 2m)}",
        )

    def test_only_further_caption_lines(self):
        self.assertEqual(
            pict_with_caption("\\grmkpicture{a.jpg}{4.0}{4.0}{}", ["(Height: 2m)"]),
            "\\grmkpicture{a.jpg}{4.0}{4.0}{(Height: 2m)}",
        )


# ------------------------------------------------------------
#
# TestPictWidthOf
#
# ------------------------------------------------------------
class TestPictWidthOf(unittest.TestCase):
    def test_width(self):
        self.assertEqual(pict_width_of("\\grmkpicture{a.jpg}{4.5}{3.0}{x}"), 4.5)

    def test_not_a_picture(self):
        self.assertEqual(pict_width_of("text"), 0)

    def test_bad_width(self):
        self.assertEqual(pict_width_of("\\grmkpicture{a.jpg}{x}{3.0}{}"), 0)


# ------------------------------------------------------------
#
# TestMapFontSize
#
# ------------------------------------------------------------
class TestMapFontSize(unittest.TestCase):
    def test_small_size(self):
        self.assertEqual(map_font_size(8), "footnotesize")

    def test_large_size(self):
        self.assertEqual(map_font_size(24), "Huge")

    def test_tiny(self):
        self.assertEqual(map_font_size(4), "tiny")


# ------------------------------------------------------------
#
# TestTabClasses
#
# ------------------------------------------------------------
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


# ------------------------------------------------------------
#
# TestMkCompleteRow
#
# ------------------------------------------------------------
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
