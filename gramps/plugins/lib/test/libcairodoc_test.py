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
Unittest for the Cairo docgen paragraph-split attribute re-indexing (bug 6250).

When ``GtkDocParagraph.divide`` splits a styled paragraph across a page break
it rebuilds the second part's ``Pango.AttrList`` by re-indexing the parsed
attribute runs onto the second part's plaintext byte offsets.  The old
workaround re-serialised the markup and counted escaped entities
(``&amp;``/``&lt;``/``&gt;``) as multiple plaintext bytes, so any paragraph
whose plaintext contained ``&``, ``<`` or ``>`` before the split desynced the
offsets and misplaced or dropped the style runs.

These tests drive the production re-index seam (``reindex_split_attrlist``,
the same function ``divide`` calls) on a ``Pango.AttrList`` obtained from
``Pango.parse_markup`` -- no display or cairo surface required.
"""

import unittest

import gi

gi.require_version("Pango", "1.0")
from gi.repository import Pango

from gramps.plugins.lib.libcairodocattr import reindex_split_attrlist


def _parse(markup):
    """Parse markup, returning (attrlist, plaintext-as-str)."""
    ok, attrlist, plaintext, _accel = Pango.parse_markup(markup, -1, "\000")
    assert ok
    return attrlist, plaintext


def _runs(attrlist):
    """Flatten an AttrList to a sorted set of (type, start, end) tuples."""
    found = set()
    iterator = attrlist.get_iterator()
    while True:
        for attr in iterator.get_attrs():
            found.add((int(attr.klass.type), attr.start_index, attr.end_index))
        if not iterator.next():
            break
    return found


class ReindexSplitAttrListTest(unittest.TestCase):
    """
    The split point ``index`` is a byte offset into the parsed *plaintext*,
    so re-indexing must be independent of how the markup serialised escaped
    characters.  ``"A &amp; B <b>BOLD</b> tail"`` parses to plaintext
    ``"A & B BOLD tail"`` (15 bytes) with a single weight run over the four
    bytes of ``BOLD`` (plaintext bytes 6..10).  The ``&`` sits at byte 2,
    before every split below -- exactly the case the old workaround got wrong.
    """

    MARKUP = "A &amp; B <b>BOLD</b> tail"

    def setUp(self):
        self.attrlist, self.plaintext = _parse(self.MARKUP)
        self.assertEqual(self.plaintext, "A & B BOLD tail")
        # sanity: the parsed run really is the bold over BOLD
        self.assertEqual(_runs(self.attrlist), {(int(Pango.AttrType.WEIGHT), 6, 10)})

    def test_split_at_run_start_rebases_to_zero(self):
        # Split exactly at the start of the bold run (byte offset of "BOLD").
        index = self.plaintext.encode("utf-8").index(b"BOLD")
        self.assertEqual(index, 6)
        result = reindex_split_attrlist(self.attrlist, index)
        # The bold survives, rebased onto the second part's bytes 0..4 ("BOLD").
        self.assertEqual(_runs(result), {(int(Pango.AttrType.WEIGHT), 0, 4)})

    def test_split_inside_run_clamps_start_to_zero(self):
        # Split inside the bold run (after "BO"); the straddling run clamps
        # its start to 0 and keeps its tail.
        index = 8
        result = reindex_split_attrlist(self.attrlist, index)
        self.assertEqual(_runs(result), {(int(Pango.AttrType.WEIGHT), 0, 2)})

    def test_split_after_run_shifts_start(self):
        # Split before the bold run (at the space after "B "); the run lies
        # wholly in the second part and both offsets shift by index.
        index = 5
        result = reindex_split_attrlist(self.attrlist, index)
        self.assertEqual(_runs(result), {(int(Pango.AttrType.WEIGHT), 1, 5)})

    def test_run_entirely_before_split_is_dropped(self):
        # Split past the end of the bold run; nothing survives into part two.
        index = 11
        result = reindex_split_attrlist(self.attrlist, index)
        self.assertEqual(_runs(result), set())


if __name__ == "__main__":
    unittest.main()
