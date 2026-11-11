#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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

"""Tests for the DNA references updated by a note, citation or media merge."""

import shutil
import tempfile
import unittest
from types import SimpleNamespace

from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import (
    Citation,
    DNAMatch,
    DNATest,
    Media,
    MediaRef,
    Note,
    SharedAncestor,
)
from gramps.gen.merge import MergeCitationQuery, MergeMediaQuery, MergeNoteQuery


# -------------------------------------------------------------------------
#
# MergeDNAReferencesTest
#
# -------------------------------------------------------------------------
class MergeDNAReferencesTest(unittest.TestCase):
    """A merge moves the removed object's DNA references to the kept object."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db = make_database("sqlite")
        self.db.load(self.tmpdir)

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.tmpdir)

    def _add(self, obj):
        """Add a primary object and return its handle."""
        with DbTxn("add", self.db) as trans:
            return self.db.method("add_%s", obj.__class__.__name__)(obj, trans)

    def _get(self, class_name, handle):
        """Return the primary object of the given class with the given handle."""
        return self.db.method("get_%s_from_handle", class_name)(handle)

    def _merge(self, query, class_name, phoenix_handle, titanic_handle):
        """Merge the titanic object into the phoenix object."""
        query(
            SimpleNamespace(db=self.db),
            self._get(class_name, phoenix_handle),
            self._get(class_name, titanic_handle),
        ).execute()

    def test_note_on_dnatest(self):
        """A DNA test note is moved to the kept note."""
        phoenix, titanic = self._add(Note("kept")), self._add(Note("removed"))
        test = DNATest()
        test.add_note(titanic)
        test_handle = self._add(test)

        self._merge(MergeNoteQuery, "Note", phoenix, titanic)

        self.assertEqual(self._get("DNATest", test_handle).get_note_list(), [phoenix])

    def test_note_on_shared_ancestor(self):
        """A shared ancestor note is moved to the kept note."""
        phoenix, titanic = self._add(Note("kept")), self._add(Note("removed"))
        ancestor = SharedAncestor()
        ancestor.add_note(titanic)
        dnamatch = DNAMatch()
        dnamatch.add_shared_ancestor(ancestor)
        match_handle = self._add(dnamatch)

        self._merge(MergeNoteQuery, "Note", phoenix, titanic)

        dnamatch = self._get("DNAMatch", match_handle)
        self.assertEqual(
            dnamatch.get_shared_ancestor_list()[0].get_note_list(), [phoenix]
        )

    def test_citation_on_dnamatch(self):
        """A DNA match citation is moved to the kept citation."""
        phoenix, titanic = self._add(Citation()), self._add(Citation())
        dnamatch = DNAMatch()
        dnamatch.add_citation(titanic)
        match_handle = self._add(dnamatch)

        self._merge(MergeCitationQuery, "Citation", phoenix, titanic)

        self.assertEqual(
            self._get("DNAMatch", match_handle).get_citation_list(), [phoenix]
        )

    def test_citation_on_dnatest(self):
        """A DNA test citation is moved to the kept citation."""
        phoenix, titanic = self._add(Citation()), self._add(Citation())
        test = DNATest()
        test.add_citation(titanic)
        test_handle = self._add(test)

        self._merge(MergeCitationQuery, "Citation", phoenix, titanic)

        self.assertEqual(
            self._get("DNATest", test_handle).get_citation_list(), [phoenix]
        )

    def test_media_on_dnatest(self):
        """A DNA test media reference is moved to the kept media object."""
        phoenix, titanic = self._add(Media()), self._add(Media())
        media_ref = MediaRef()
        media_ref.set_reference_handle(titanic)
        test = DNATest()
        test.add_media_reference(media_ref)
        test_handle = self._add(test)

        self._merge(MergeMediaQuery, "Media", phoenix, titanic)

        test = self._get("DNATest", test_handle)
        self.assertEqual(
            [ref.get_reference_handle() for ref in test.get_media_list()], [phoenix]
        )

    def test_media_on_dnamatch(self):
        """A DNA match media reference is moved to the kept media object."""
        phoenix, titanic = self._add(Media()), self._add(Media())
        media_ref = MediaRef()
        media_ref.set_reference_handle(titanic)
        dnamatch = DNAMatch()
        dnamatch.add_media_reference(media_ref)
        match_handle = self._add(dnamatch)

        self._merge(MergeMediaQuery, "Media", phoenix, titanic)

        dnamatch = self._get("DNAMatch", match_handle)
        self.assertEqual(
            [ref.get_reference_handle() for ref in dnamatch.get_media_list()],
            [phoenix],
        )


if __name__ == "__main__":
    unittest.main()
