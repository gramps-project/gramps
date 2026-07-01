#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026
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
Unit test for the relationship calculator's handling of adopted vs. step
links (issue 10554).

An adoptee is treated, genealogically and legally, as born into the family;
the database already records the relation explicitly with
``ChildRefType.ADOPTED``.  Yet the calculator used to collapse every non-birth
link to "step", so an adopted child was reported as a *stepchild* / *stepbrother*.
These tests build an in-memory tree with a birth child, an adopted child and a
genuine stepchild and assert that:

* an adopted child is NOT labelled "step" (and reads as "adopted ..."), while
* a genuine stepchild still IS labelled "step".

The tests exercise the production path -- ``get_one_relationship`` -- which is
what the Narrative Web report and every other relationship consumer route
through; ``relationship.py`` is import-light (no GUI / gi), so this runs under
the headless test runner.
"""

import unittest

from ..db import DbTxn
from ..db.utils import make_database
from ..lib import ChildRef, ChildRefType, Family, Person
from ..relationship import RelationshipCalculator


def _make_db():
    """Create and return a fresh in-memory SQLite database."""
    db = make_database("sqlite")
    db.load(":memory:")
    return db


class AdoptedVsStepTest(unittest.TestCase):
    """
    A father/mother couple with three sons sharing the same parents but
    different child-reference types: birth, adopted and stepchild.
    """

    @classmethod
    def setUpClass(cls):
        cls.db = _make_db()
        cls.calc = RelationshipCalculator()

        with DbTxn("build tree", cls.db) as trans:
            # the parents
            cls.father = cls._add_person(trans, "I0001", Person.MALE)
            cls.mother = cls._add_person(trans, "I0002", Person.FEMALE)
            # the three children
            cls.birth = cls._add_person(trans, "I0003", Person.MALE)
            cls.adopted = cls._add_person(trans, "I0004", Person.MALE)
            cls.step = cls._add_person(trans, "I0005", Person.MALE)

            fam = Family()
            fam.set_handle("F0001")
            fam.set_gramps_id("F0001")
            fam.set_father_handle(cls.father.handle)
            fam.set_mother_handle(cls.mother.handle)
            for child, reltype in (
                (cls.birth, ChildRefType.BIRTH),
                (cls.adopted, ChildRefType.ADOPTED),
                (cls.step, ChildRefType.STEPCHILD),
            ):
                ref = ChildRef()
                ref.set_reference_handle(child.handle)
                ref.set_mother_relation(ChildRefType(reltype))
                ref.set_father_relation(ChildRefType(reltype))
                fam.add_child_ref(ref)
                child.add_parent_family_handle(fam.handle)
            cls.father.add_family_handle(fam.handle)
            cls.mother.add_family_handle(fam.handle)

            cls.db.add_family(fam, trans)
            for person in (cls.father, cls.mother, cls.birth, cls.adopted, cls.step):
                cls.db.commit_person(person, trans)

    @classmethod
    def _add_person(cls, trans, gramps_id, gender):
        person = Person()
        person.set_handle(gramps_id)
        person.set_gramps_id(gramps_id)
        person.set_gender(gender)
        cls.db.add_person(person, trans)
        return person

    def _rel(self, orig, other):
        return self.calc.get_one_relationship(self.db, orig, other)

    # --- parent -> child --------------------------------------------------

    def test_birth_child_has_no_qualifier(self):
        rel = self._rel(self.father, self.birth)
        self.assertNotIn("step", rel)
        self.assertNotIn("adopted", rel)

    def test_stepchild_is_step(self):
        rel = self._rel(self.father, self.step)
        self.assertIn("step", rel)

    def test_adopted_child_is_not_step(self):
        rel = self._rel(self.father, self.adopted)
        self.assertNotIn("step", rel)

    def test_adopted_child_reads_adopted(self):
        rel = self._rel(self.father, self.adopted)
        self.assertIn("adopted", rel)

    # --- child -> adoptive parent (reciprocal) ----------------------------

    def test_adoptive_parent_is_not_step(self):
        rel = self._rel(self.adopted, self.father)
        self.assertNotIn("step", rel)
        self.assertIn("adopted", rel)

    # --- siblings ---------------------------------------------------------

    def test_step_sibling_is_step(self):
        rel = self._rel(self.birth, self.step)
        self.assertIn("step", rel)

    def test_adopted_sibling_is_not_step(self):
        rel = self._rel(self.birth, self.adopted)
        self.assertNotIn("step", rel)


if __name__ == "__main__":
    unittest.main()
