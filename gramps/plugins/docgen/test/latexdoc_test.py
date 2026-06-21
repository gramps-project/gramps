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
Unittests for the LaTeX docgen: the multicolumn counter (bug 13418) and
the picture-in-table width emission (bug 11166).
"""

import os
import tempfile
import unittest
from unittest import mock

from gramps.gen.plug.docgen import (
    PaperSize,
    PaperStyle,
    PAPER_PORTRAIT,
    ParagraphStyle,
    StyleSheet,
    TableCellStyle,
    TableStyle,
)
from gramps.plugins.docgen import latexdoc
from gramps.plugins.docgen.latexdoc import LaTeXDoc, str_incr, MULTCOL_COUNT_BASE


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


# ------------------------------------------------------------
#
# LaTeXPictureInTableTest
#
# ------------------------------------------------------------
class LaTeXPictureInTableTest(unittest.TestCase):
    """
    A table that contains a picture cell (e.g. the Complete Individual
    Report with "Add Pictures" enabled) drives
    :meth:`LaTeXDoc.calc_latex_widths`, which emits the
    ``\\setlength{\\grpictsize}`` command. Before the fix it joined the
    numeric ``self.pict_width`` straight into that LaTeX string, so the
    report crashed with::

        TypeError: sequence item 1: expected str instance, float found

    The two sibling emission sites (``repack_row`` and the cell emit)
    already stringify the width with ``repr``; this exercises the third
    one through the real doc API so it stays consistent (bug 11166).

    ``add_media`` only produces a clean ``\\grmkpicture`` picture cell
    (the one that reaches the crash site) when Pillow is available — the
    condition on the affected user's machine. The image extra is not part
    of the unit-test environment, so ``HAVE_PIL`` is forced on to
    reproduce it; a ``.jpg`` source means the production code never
    actually calls into Pillow (it skips conversion for an already-jpg
    input), so no real Pillow install is needed.
    """

    def _make_doc(self, path):
        """Build a LaTeXDoc with the minimal styles its API needs."""
        styles = StyleSheet()
        styles.add_paragraph_style("Default", ParagraphStyle())

        table = TableStyle()
        table.set_width(100)
        table.set_columns(1)
        table.set_column_widths([100])
        styles.add_table_style("PictureTable", table)

        styles.add_cell_style("PictureCell", TableCellStyle())

        paper = PaperStyle(PaperSize("Letter", 27.94, 21.59), PAPER_PORTRAIT)
        doc = LaTeXDoc(styles, paper)
        doc.open(path)
        return doc

    def test_picture_cell_emits_without_typeerror(self):
        """end_table()->calc_latex_widths() must stringify the picture width."""
        with tempfile.TemporaryDirectory() as tmp:
            doc = self._make_doc(os.path.join(tmp, "report"))
            doc.start_table("table", "PictureTable")
            doc.start_row()
            doc.start_cell("PictureCell")
            # Emulate the affected environment (Pillow present). The .jpg input
            # makes add_media skip conversion, so Pillow is never actually
            # invoked — but the cell becomes a clean \grmkpicture cell and
            # self.pict_width is set to the (float) width, exactly as in the
            # Complete Individual Report with "Add Pictures" enabled.
            with mock.patch.object(latexdoc, "HAVE_PIL", True):
                doc.add_media(os.path.join(tmp, "image.jpg"), "single", 5.0, 4.0)
            doc.end_cell()
            doc.end_row()
            # Sanity: the cell really is the picture cell that reaches the crash
            # site, and the width is the bare float that triggered it.
            cell = doc.tabmem.rows[0].cells[0]
            self.assertTrue(cell.content.startswith("\\grmkpicture"))
            self.assertIsInstance(doc.pict_width, float)
            try:
                # Before the fix this raises:
                #   TypeError: sequence item 1: expected str instance, float found
                doc.end_table()
            except TypeError as err:
                self.fail("LaTeX picture-in-table emission raised TypeError: %s" % err)
            doc.close()


if __name__ == "__main__":
    unittest.main()
