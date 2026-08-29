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
Unittest for the ODF docgen table-column-style naming (bug 6549).

The ODF generator names each table-column style ``<table-style>.<suffix>``.
The historical suffix ``chr(ord("A") + col)`` only yields a valid, unique
token for the first 26 columns: past column 25 it emits non-letter
characters and past column 62 it runs beyond ``chr(127)``, producing
malformed/invalid column-style names.  A second, related defect capped the
column-style *definition* loop at 50 columns while the *reference* loop
emitted one reference per column, so for a wide table (e.g. the census
report's 78-column US-1840 table) every column past 49 referenced a style
name that was never defined.

These tests drive the production ``ODFDoc`` emission path -- the same
``init`` (column-style definitions) and ``start_table`` (column-style
references) methods a real report uses -- for a 78-column table, then assert
on the generated content that every referenced column-style name is valid,
was actually defined, and is unique per column.
"""

import os
import re
import tempfile
import unittest

from gramps.gen.plug.docgen import (
    PaperSize,
    PaperStyle,
    PAPER_PORTRAIT,
    StyleSheet,
    TableStyle,
)
from gramps.plugins.docgen.odfdoc import ODFDoc

# More than 63 columns: the threshold past which the old chr() scheme ran
# beyond chr(127), and well past the old 50-column definition cap.
NCOLS = 78
TABLE_STYLE = "GRAPHTABLE"

# A column-style suffix must be a valid identifier token: only ASCII
# letters (the ODF validator rejects control/punctuation characters in a
# style name).
_VALID_SUFFIX = re.compile(r"^[A-Za-z]+$")

# style:name="GRAPHTABLE.<suffix>" on a table-column family style (a
# column-style DEFINITION emitted by ODFDoc.init).
_DEFINED = re.compile(
    r'<style:style style:name="'
    + re.escape(TABLE_STYLE)
    + r'\.([^"]+)" style:family="table-column"'
)
# table:style-name="GRAPHTABLE.<suffix>" on a table-column (a column-style
# REFERENCE emitted by ODFDoc.start_table).
_REFERENCED = re.compile(
    r'<table:table-column table:style-name="' + re.escape(TABLE_STYLE) + r'\.([^"]+)"'
)


def _wide_table_content():
    """Build an ODFDoc whose only table style declares NCOLS columns and run
    the production emission methods, returning the generated content XML
    (column-style definitions from ``init`` followed by the table's column
    references from ``start_table``)."""
    table = TableStyle()
    table.set_width(100)
    table.set_columns(NCOLS)
    for col in range(NCOLS):
        table.set_column_width(col, 100.0 / NCOLS)

    sheet = StyleSheet()
    sheet.add_table_style(TABLE_STYLE, table)

    paper = PaperStyle(PaperSize("Letter", 27.94, 21.59), PAPER_PORTRAIT)
    doc = ODFDoc(sheet, paper)

    with tempfile.TemporaryDirectory() as tmp:
        doc.open(os.path.join(tmp, "wide"))
        doc.init()  # emits the column-style DEFINITIONS
        doc.start_table("the_table", TABLE_STYLE)  # emits the REFERENCES
        return doc.cntnt.getvalue()


class ODFWideTableTest(unittest.TestCase):
    """Drive the production ODFDoc path for a >63-column table (bug 6549)."""

    def setUp(self):
        self.content = _wide_table_content()
        self.defined = set(_DEFINED.findall(self.content))
        self.referenced = _REFERENCED.findall(self.content)

    def test_emits_one_reference_per_column(self):
        self.assertEqual(len(self.referenced), NCOLS)

    def test_every_referenced_name_is_valid(self):
        # Past column 25 the old chr() scheme emitted non-letter characters
        # (and past column 62, characters beyond chr(127)).
        for name in self.referenced:
            with self.subTest(name=name):
                self.assertRegex(name, _VALID_SUFFIX)

    def test_every_referenced_name_was_defined(self):
        # The definition loop and the reference loop must agree for every
        # column -- the old min(get_columns(), 50) cap left every column past
        # 49 referencing a style name that was never defined.
        missing = [n for n in self.referenced if n not in self.defined]
        self.assertEqual(
            missing,
            [],
            "column references with no matching definition: %r" % (missing,),
        )

    def test_referenced_names_are_unique(self):
        self.assertEqual(len(set(self.referenced)), NCOLS)


if __name__ == "__main__":
    unittest.main()
