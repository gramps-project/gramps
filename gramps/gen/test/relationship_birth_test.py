#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Douglas S. Blank <doug.blank@gmail.com>
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
Unittest for RelationshipCalculator.get_one_relationship: a direct ancestor
or descendant reached by both a birth line and a non-birth line of the same
length is described by the birth line.

The tree::

    G (f)
     |-- M (f)  + F (m) -- P (m)   birth son of F and M
     `-- M2 (f) + F (m) -- P       stepson of M2 (this family comes first)
"""

import shutil
import tempfile
import unittest

from ..db import DbTxn
from ..db.utils import make_database
from ..lib import ChildRef, ChildRefType, Family, Person
from ..relationship import get_relationship_calculator


class DirectRelationBirthFirstTest(unittest.TestCase):
    """A birth line wins over an equally long non-birth line."""

    @classmethod
    def setUpClass(cls):
        cls.dirname = tempfile.mkdtemp(prefix="relationship_birth_")
        cls.db = make_database("sqlite")
        cls.db.load(cls.dirname)
        cls.people = {}
        with DbTxn("build test tree", cls.db) as txn:
            for name, gender in (
                ("G", Person.FEMALE),
                ("M", Person.FEMALE),
                ("M2", Person.FEMALE),
                ("F", Person.MALE),
                ("P", Person.MALE),
            ):
                person = Person()
                person.set_gender(gender)
                cls.people[name] = cls.db.add_person(person, txn)
            birth, step = ChildRefType.BIRTH, ChildRefType.STEPCHILD
            cls._family(txn, None, "G", [("M", birth), ("M2", birth)])
            cls._family(txn, "F", "M2", [("P", step)])
            cls._family(txn, "F", "M", [("P", birth)])
        cls.calc = get_relationship_calculator(reinit=True)

    @classmethod
    def _family(cls, txn, father, mother, children):
        family = Family()
        if father:
            family.set_father_handle(cls.people[father])
        family.set_mother_handle(cls.people[mother])
        for name, mother_relation in children:
            ref = ChildRef()
            ref.set_reference_handle(cls.people[name])
            ref.set_mother_relation(mother_relation)
            family.add_child_ref(ref)
        handle = cls.db.add_family(family, txn)
        for parent in (father, mother):
            if parent:
                person = cls.db.get_person_from_handle(cls.people[parent])
                person.add_family_handle(handle)
                cls.db.commit_person(person, txn)
        for name, _relation in children:
            person = cls.db.get_person_from_handle(cls.people[name])
            person.add_parent_family_handle(handle)
            cls.db.commit_person(person, txn)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        shutil.rmtree(cls.dirname, ignore_errors=True)

    def relationship(self, orig, other):
        """Return the relationship of other to orig, without wording."""
        _string, dist_orig, dist_other = self.calc.get_one_relationship(
            self.db,
            self.db.get_person_from_handle(self.people[orig]),
            self.db.get_person_from_handle(self.people[other]),
            extra_info=True,
        )
        return dist_orig, dist_other

    def wording(self, orig, other, gender_orig, gender_other, step):
        """The wording for the given distances, by birth or not."""
        dist_orig, dist_other = self.relationship(orig, other)
        path = "m" * max(dist_orig, dist_other)
        if step:
            path = path.upper()
        return self.calc.get_single_relationship_string(
            dist_orig,
            dist_other,
            gender_orig,
            gender_other,
            path if dist_orig else "",
            path if dist_other else "",
            only_birth=not step,
        )

    def test_ancestor_by_birth(self):
        """G is P's grandmother by birth, not his step-grandmother."""
        result = self.calc.get_one_relationship(
            self.db,
            self.db.get_person_from_handle(self.people["P"]),
            self.db.get_person_from_handle(self.people["G"]),
        )
        self.assertEqual(self.relationship("P", "G"), (2, 0))
        self.assertEqual(
            result, self.wording("P", "G", Person.MALE, Person.FEMALE, step=False)
        )
        self.assertNotEqual(
            result, self.wording("P", "G", Person.MALE, Person.FEMALE, step=True)
        )

    def test_descendant_by_birth(self):
        """P is G's grandson by birth, not her step-grandson."""
        result = self.calc.get_one_relationship(
            self.db,
            self.db.get_person_from_handle(self.people["G"]),
            self.db.get_person_from_handle(self.people["P"]),
        )
        self.assertEqual(self.relationship("G", "P"), (0, 2))
        self.assertEqual(
            result, self.wording("G", "P", Person.FEMALE, Person.MALE, step=False)
        )
        self.assertNotEqual(
            result, self.wording("G", "P", Person.FEMALE, Person.MALE, step=True)
        )


if __name__ == "__main__":
    unittest.main()
