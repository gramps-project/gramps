#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  David Straub
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Unit tests for the person ordering of the Relationship Graph report.
"""

# ------------------------
# Python modules
# ------------------------
import unittest
from types import SimpleNamespace
from typing import cast

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import ChildRef, Family, Person
from gramps.gen.types import PersonHandle
from gramps.plugins.graph.gvrelgraph import RelGraphReport


# ------------------------------------------------------------
#
# SortPersonsTest
#
# ------------------------------------------------------------
class SortPersonsTest(unittest.TestCase):
    """
    Test ``RelGraphReport.sort_persons``.
    """

    def setUp(self) -> None:
        """
        Create an empty in-memory database.
        """
        self.db = make_database("sqlite")
        self.db.load(":memory:")

    def tearDown(self) -> None:
        """
        Close the database.
        """
        self.db.close()

    def _add_person(self) -> PersonHandle:
        """
        Add a person to the database.

        :returns: The handle of the new person.
        :rtype: PersonHandle
        """
        with DbTxn("Add person", self.db) as trans:
            return self.db.add_person(Person(), trans)

    def _add_family(self, father: PersonHandle, child: PersonHandle) -> None:
        """
        Add a family with the given father and child.

        :param father: The handle of the father.
        :type father: PersonHandle
        :param child: The handle of the child.
        :type child: PersonHandle
        """
        with DbTxn("Add family", self.db) as trans:
            family = Family()
            family.set_father_handle(father)
            child_ref = ChildRef()
            child_ref.set_reference_handle(child)
            family.add_child_ref(child_ref)
            fam_handle = self.db.add_family(family, trans)
            for handle, add in (
                (father, Person.add_family_handle),
                (child, Person.add_parent_family_handle),
            ):
                person = self.db.get_person_from_handle(handle)
                add(person, fam_handle)
                self.db.commit_person(person, trans)

    def _sort(self) -> list[PersonHandle]:
        """
        Sort all persons of the database like the report does.

        :returns: The sorted person handles.
        :rtype: list[PersonHandle]
        """
        handles = list(self.db.iter_person_handles())
        report = SimpleNamespace(
            database=self.db,
            persons=set(handles),
            _is_waiting_for=RelGraphReport._is_waiting_for,
        )
        return RelGraphReport.sort_persons(cast(RelGraphReport, report), handles)

    def test_tree(self) -> None:
        """
        Parents are sorted before their children.
        """
        grandfather = self._add_person()
        father = self._add_person()
        child = self._add_person()
        self._add_family(father, child)
        self._add_family(grandfather, father)
        self.assertEqual(self._sort(), [grandfather, father, child])

    def test_own_ancestor(self) -> None:
        """
        Two persons who are each other's parent are both sorted.
        """
        person_a = self._add_person()
        person_b = self._add_person()
        self._add_family(person_a, person_b)
        self._add_family(person_b, person_a)
        self.assertCountEqual(self._sort(), [person_a, person_b])

    def test_own_ancestor_below_root(self) -> None:
        """
        A loop reachable from a person without parents is sorted.
        """
        root = self._add_person()
        person_a = self._add_person()
        person_b = self._add_person()
        self._add_family(root, person_a)
        self._add_family(person_a, person_b)
        self._add_family(person_b, person_a)
        result = self._sort()
        self.assertCountEqual(result, [root, person_a, person_b])
        self.assertEqual(result[0], root)


if __name__ == "__main__":
    unittest.main()
