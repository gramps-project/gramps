#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps developers
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
Regression test for :class:`CitationTreeModel` — bug 0007230.

Bug 7230 reported that in the Citation Tree View a source with **no
citations** did not appear in the tree at all: a freshly created,
citation-less source was invisible and hard to manage.

The tree model now uses a two-cursor ``has_secondary=True`` design.  The
*primary* cursor iterates **all** sources (``get_source_cursor`` /
``get_number_of_sources``) and :meth:`CitationTreeModel.add_row` adds each
one as a top-level node, while the *secondary* citation cursor only adds
citation children.  Under that design every source is a parent node whether
or not any citation references it.

This test drives the **production** model build against an in-memory
database holding one cited source and one citation-less source, and asserts
that *both* sources exist as top-level nodes — the citation-less one with no
children.  It is a guard against a regression to the pre-fix behaviour where
sources were only materialised as a side effect of iterating citations.

The model is built with ``uistate=None``: for a tiny database the loading
``ProgressMonitor`` never reaches its popup threshold, so no GTK dialog (and
no display) is required and the test runs headless.
"""

import unittest

import gi  # noqa: E402

gi.require_version("Gtk", "3.0")  # noqa: E402

from gramps.gen.db import DbTxn  # noqa: E402
from gramps.gen.db.utils import make_database  # noqa: E402
from gramps.gen.lib import Citation, Source  # noqa: E402

from ..citationtreemodel import CitationTreeModel  # noqa: E402


class CitationTreeModelEmptySourceTest(unittest.TestCase):
    """Bug 0007230 regression: every source is a top-level node."""

    def setUp(self):
        """Create an in-memory db with a cited and a citation-less source."""
        self.db = make_database("sqlite")
        self.db.load(":memory:")
        with DbTxn("setup", self.db) as trans:
            # A source that *is* referenced by a citation.
            cited = Source()
            cited.set_title("Cited Source")
            self.cited_handle = self.db.add_source(cited, trans)

            citation = Citation()
            citation.set_reference_handle(self.cited_handle)
            citation.set_page("p. 1")
            self.citation_handle = self.db.add_citation(citation, trans)

            # A brand-new source with no citations at all (the bug case).
            lonely = Source()
            lonely.set_title("Lonely Source")
            self.lonely_handle = self.db.add_source(lonely, trans)

    def tearDown(self):
        self.db.close()

    def _build_model(self):
        # search=(False, None, False) is the "no filter, no search" tuple the
        # view passes for an unfiltered tree; uistate=None is safe headless
        # (see module docstring).
        return CitationTreeModel(self.db, uistate=None, search=(False, None, False))

    def _top_level_handles(self, model):
        top = model.tree[None]
        return {model.nodemap.node(nodeid).handle for _, nodeid in top.children}

    def test_citationless_source_is_a_top_level_node(self):
        """A source with zero citations must still be a top-level node."""
        model = self._build_model()
        top_handles = self._top_level_handles(model)

        # The core assertion of bug 7230: the citation-less source appears.
        self.assertIn(
            self.lonely_handle,
            top_handles,
            "a source with no citations is missing from the Citation Tree View",
        )
        # It is present as a parent node with no children.
        self.assertEqual(model.tree[self.lonely_handle].children, [])

    def test_every_source_is_listed_independent_of_citations(self):
        """Both the cited and the citation-less source are top-level nodes."""
        model = self._build_model()
        top_handles = self._top_level_handles(model)

        self.assertIn(self.cited_handle, top_handles)
        self.assertIn(self.lonely_handle, top_handles)

        # The citation is a child of its source, not a top-level node.
        self.assertNotIn(self.citation_handle, top_handles)
        cited_children = {
            model.nodemap.node(nodeid).handle
            for _, nodeid in model.tree[self.cited_handle].children
        }
        self.assertEqual(cited_children, {self.citation_handle})


if __name__ == "__main__":
    unittest.main()
