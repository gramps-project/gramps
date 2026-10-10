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

"""Tests for the DNA references updated by a person merge."""

import shutil
import tempfile
import unittest

from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import DNAMatch, DNATest, Person, SharedAncestor
from gramps.gen.merge import MergePersonQuery


# -------------------------------------------------------------------------
#
# MergePersonDNATestTest
#
# -------------------------------------------------------------------------
class MergePersonDNATestTest(unittest.TestCase):
    """A person merge moves the removed person's DNA references to the kept person."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db = make_database("sqlite")
        self.db.load(self.tmpdir)
        with DbTxn("setup", self.db) as trans:
            self.phoenix_handle = self.db.add_person(Person(), trans)
            self.titanic_handle = self.db.add_person(Person(), trans)
            test = DNATest()
            test.set_person_handle(self.titanic_handle)
            self.test_handle = self.db.add_dnatest(test, trans)
            ancestor = SharedAncestor()
            ancestor.set_person_handle(self.titanic_handle)
            match = DNAMatch()
            match.add_shared_ancestor(ancestor)
            self.match_handle = self.db.add_dnamatch(match, trans)

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.tmpdir)

    def test_dnatest_moves_to_phoenix(self):
        """The DNA test of the removed person refers to the kept person."""
        phoenix = self.db.get_person_from_handle(self.phoenix_handle)
        titanic = self.db.get_person_from_handle(self.titanic_handle)
        MergePersonQuery(self.db, phoenix, titanic).execute()

        test = self.db.get_dnatest_from_handle(self.test_handle)
        self.assertEqual(test.get_person_handle(), self.phoenix_handle)
        self.assertEqual(
            list(self.db.find_backlink_handles(self.phoenix_handle, ["DNATest"])),
            [("DNATest", self.test_handle)],
        )

    def test_shared_ancestor_moves_to_phoenix(self):
        """A shared ancestor naming the removed person refers to the kept person."""
        phoenix = self.db.get_person_from_handle(self.phoenix_handle)
        titanic = self.db.get_person_from_handle(self.titanic_handle)
        MergePersonQuery(self.db, phoenix, titanic).execute()

        match = self.db.get_dnamatch_from_handle(self.match_handle)
        self.assertEqual(
            [sa.get_person_handle() for sa in match.get_shared_ancestor_list()],
            [self.phoenix_handle],
        )
        self.assertEqual(
            list(self.db.find_backlink_handles(self.phoenix_handle, ["DNAMatch"])),
            [("DNAMatch", self.match_handle)],
        )


if __name__ == "__main__":
    unittest.main()
