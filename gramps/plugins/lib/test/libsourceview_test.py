#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026       Gramps developers
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
Unit tests for the delete logic shared by SourceView and CitationTreeView.

Regression test for bug 13876: deleting a selected citation row in the
Citation Tree view mode left the citation in the database, because the shared
delete helper always called ``remove_source`` regardless of the selected
object's type.  These tests drive the production ``LibSourceView`` methods
directly (the module is GUI-free) so they run headlessly.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import unittest
from types import SimpleNamespace

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import Citation, Source
from gramps.plugins.lib.libsourceview import LibSourceView


# -------------------------------------------------------------------------
#
# A minimal, GUI-free carrier of the production delete methods
#
# -------------------------------------------------------------------------
class _Probe(LibSourceView):
    """
    Carries the real ``LibSourceView`` methods without the Gtk ``ListView``
    machinery.  ``selected_handles`` and ``remove_selected_objects`` are the
    only collaborators ``remove`` needs; the latter is captured rather than
    run so no confirmation dialog is shown.
    """

    def __init__(self, db, selected):
        self.dbstate = SimpleNamespace(db=db)
        self.uistate = SimpleNamespace(pulse_progressbar=lambda *args: None)
        self._selected = selected
        self.captured = None

    def selected_handles(self):
        return list(self._selected)

    def remove_selected_objects(self, ht_list=None):
        self.captured = ht_list


# -------------------------------------------------------------------------
#
# Test class
#
# -------------------------------------------------------------------------
class LibSourceViewDeleteTest(unittest.TestCase):
    """
    Exercise the source/citation delete path used by the Citation Tree view.
    """

    def setUp(self):
        self.db = make_database("sqlite")
        self.db.load(":memory:")
        with DbTxn("Add source and citation", self.db) as trans:
            source = Source()
            source.set_title("World of the Wierd")
            self.source_handle = self.db.add_source(source, trans)
            citation = Citation()
            citation.set_page("p. 1")
            citation.set_reference_handle(self.source_handle)
            self.citation_handle = self.db.add_citation(citation, trans)

    def tearDown(self):
        self.db.close()

    def test_remove_resolves_selected_citation_to_citation(self):
        """
        A selected citation row is resolved to a ("Citation", handle) pair,
        not mistaken for a source.
        """
        probe = _Probe(self.db, [self.citation_handle])
        probe.remove()
        self.assertEqual(probe.captured, [("Citation", self.citation_handle)])

    def test_delete_citation_removes_it_from_db(self):
        """
        Deleting a selected citation removes that citation from the database
        (bug 13876) while leaving its source intact.
        """
        self.assertTrue(self.db.has_citation_handle(self.citation_handle))
        with DbTxn("Delete citation", self.db) as trans:
            probe = _Probe(self.db, [self.citation_handle])
            probe.remove_object_from_handle(
                "Citation", self.citation_handle, trans, in_use_prompt=False
            )
        self.assertFalse(
            self.db.has_citation_handle(self.citation_handle),
            "citation should be gone from the database after delete",
        )
        self.assertTrue(
            self.db.has_source_handle(self.source_handle),
            "the citation's source must remain",
        )

    def test_delete_source_removes_source_and_its_citation(self):
        """
        Deleting a source still removes the source and its child citations
        (the path that already worked must keep working).
        """
        with DbTxn("Delete source", self.db) as trans:
            probe = _Probe(self.db, [self.source_handle])
            probe.remove_object_from_handle(
                "Source", self.source_handle, trans, in_use_prompt=False
            )
        self.assertFalse(self.db.has_source_handle(self.source_handle))
        self.assertFalse(self.db.has_citation_handle(self.citation_handle))


if __name__ == "__main__":
    unittest.main()
