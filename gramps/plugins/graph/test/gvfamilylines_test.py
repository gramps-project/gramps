#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps Development Team
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
Unit test for the Family Lines Graph people/family selection.

Bug 0010415 (originally 0010400): with "follow parents" on and "Try to
remove extra people and families" on, the ``remove_uninteresting_parents``
pruning dropped *direct-line ancestors* of the person of interest whenever
their surname spelling differed across generations -- it kept an ancestor
only via a surname-equality test, with no lineage-based criterion.  A
top-of-tree direct ancestor whose surname spelling drifts (e.g. great-
grandfather "Smyth" for a "Smith" descendant) was therefore removed.

The test drives the production selection unit
(:class:`gramps.plugins.graph.gvfamilylines.FamilyLinesSelection`, the same
``find_parents`` + ``remove_uninteresting_parents`` code the report runs in
``begin_report``) on a real in-memory database, and asserts that no direct-
line ancestor is pruned regardless of surname spelling.
"""

import os
import tempfile
import unittest

from gramps.gen.db.utils import import_as_dict
from gramps.gen.user import User
from gramps.plugins.graph.gvfamilylines import FamilyLinesSelection

# A four-generation direct line for I0000.  The paternal surname drifts in
# spelling every generation (Smith -> Smithe -> Smyth) and each generation
# has a married-in spouse with an unrelated surname.  Every one of these
# people is a direct-line ancestor of I0000:
#
#   I0000 Smith (F, person of interest)
#     father  I0001 Smith   mother I0002 Brown            (F0000)
#       I0001's father I0003 Smithe   mother I0004 Green   (F0001)
#         I0003's father I0005 Smyth  mother I0006 White   (F0002)
#
# Pre-fix, the top-of-tree ancestors with a surname that differs from the
# person of interest -- I0005 "Smyth" (the drifted direct paternal line) and
# I0006 "White" -- are pruned as "extra".  Both must be retained.
_FIXTURE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE database PUBLIC "-//Gramps//DTD Gramps XML 1.7.2//EN"
"http://gramps-project.org/xml/1.7.2/grampsxml.dtd">
<database xmlns="http://gramps-project.org/xml/1.7.2/">
  <header><created date="2026-06-27" version="5.2"/><researcher></researcher></header>
  <people>
    <person handle="_p0" id="I0000"><gender>F</gender>
      <name type="Birth Name"><first>Anna</first><surname>Smith</surname></name>
      <childof hlink="_f0"/></person>
    <person handle="_p1" id="I0001"><gender>M</gender>
      <name type="Birth Name"><first>John</first><surname>Smith</surname></name>
      <childof hlink="_f1"/><parentin hlink="_f0"/></person>
    <person handle="_p2" id="I0002"><gender>F</gender>
      <name type="Birth Name"><first>Mary</first><surname>Brown</surname></name>
      <parentin hlink="_f0"/></person>
    <person handle="_p3" id="I0003"><gender>M</gender>
      <name type="Birth Name"><first>James</first><surname>Smithe</surname></name>
      <childof hlink="_f2"/><parentin hlink="_f1"/></person>
    <person handle="_p4" id="I0004"><gender>F</gender>
      <name type="Birth Name"><first>Eliza</first><surname>Green</surname></name>
      <parentin hlink="_f1"/></person>
    <person handle="_p5" id="I0005"><gender>M</gender>
      <name type="Birth Name"><first>Robert</first><surname>Smyth</surname></name>
      <parentin hlink="_f2"/></person>
    <person handle="_p6" id="I0006"><gender>F</gender>
      <name type="Birth Name"><first>Jane</first><surname>White</surname></name>
      <parentin hlink="_f2"/></person>
  </people>
  <families>
    <family handle="_f0" id="F0000"><rel type="Married"/>
      <father hlink="_p1"/><mother hlink="_p2"/><childref hlink="_p0"/></family>
    <family handle="_f1" id="F0001"><rel type="Married"/>
      <father hlink="_p3"/><mother hlink="_p4"/><childref hlink="_p1"/></family>
    <family handle="_f2" id="F0002"><rel type="Married"/>
      <father hlink="_p5"/><mother hlink="_p6"/><childref hlink="_p3"/></family>
  </families>
</database>
"""


class FamilyLinesDirectAncestorTest(unittest.TestCase):
    """Bug 10415: the remove-extra pruning must never drop a direct ancestor."""

    @classmethod
    def setUpClass(cls):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".gramps", delete=False, encoding="utf8"
        ) as handle:
            handle.write(_FIXTURE_XML)
            cls._path = handle.name
        # Preserve the gramps IDs from the fixture so the test can look people
        # up by ID.
        cls.db = import_as_dict(
            cls._path, User(), person_prefix="I%04d", family_prefix="F%04d"
        )

    @classmethod
    def tearDownClass(cls):
        if cls.db is not None:
            cls.db.close()
        try:
            os.unlink(cls._path)
        except OSError:
            pass

    def _handle(self, gramps_id):
        person = self.db.get_person_from_gramps_id(gramps_id)
        self.assertIsNotNone(person, "fixture person %s missing" % gramps_id)
        return person.get_handle()

    def _select(self):
        """Run the production follow-parents + remove-extra selection."""
        interest = {self._handle("I0000")}
        selection = FamilyLinesSelection(
            self.db,
            interest,
            followpar=True,
            followchild=False,
            removeextra=True,
            limitparents=False,
            maxparents=0,
            limitchildren=False,
            maxchildren=0,
            surnamecolors={},
        )
        # Drive the exact routine begin_report() uses for the parent side.
        selection.find_parents()
        selection.remove_uninteresting_parents()
        return selection

    def test_drifting_surname_direct_ancestor_retained(self):
        """The reporter's case: a direct ancestor whose surname spelling
        differs from the descendant must not be pruned as "extra"."""
        selection = self._select()
        people = selection._people
        # I0005 "Smyth" is the great-grandfather on the direct paternal line;
        # his surname spelling drifted from the "Smith" person of interest.
        self.assertIn(
            self._handle("I0005"),
            people,
            "direct-line ancestor I0005 (Smyth) was pruned despite being "
            "a direct ancestor of the person of interest",
        )
        # I0006 "White" is the great-grandmother (married into the line) --
        # also a direct-line ancestor and equally must be kept.
        self.assertIn(
            self._handle("I0006"),
            people,
            "direct-line ancestor I0006 (White) was pruned",
        )

    def test_no_direct_ancestor_is_removed(self):
        """Every person on the direct line survives the pruning, and the
        report reports zero people removed."""
        selection = self._select()
        people = selection._people
        for gid in ("I0000", "I0001", "I0002", "I0003", "I0004", "I0005", "I0006"):
            self.assertIn(
                self._handle(gid),
                people,
                "direct-line ancestor %s was pruned" % gid,
            )
        self.assertEqual(
            selection.deleted_people,
            0,
            "no direct-line ancestor should be counted as removed",
        )


if __name__ == "__main__":
    unittest.main()
