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
Tests for RelationshipCalculator.__apply_filter's visited-once-per-call
memoization fix (replacing the previous exponential-under-pedigree-
collapse recursion) and the related common-ancestor-path cap in
get_relationship_distance_new.

These build small, purpose-shaped databases via Gramps' own object model
(matching the pattern in gramps.gen.utils.test.alive_test) rather than
relying on the bundled example.gramps, since each test needs a specific
structural shape (a sibling-marries-sibling collapse chain, a person with
more than one recorded parent family, a genuine cycle) that a general
demo dataset doesn't reliably exercise.
"""

import types
import unittest

from ..db import DbTxn
from ..db.utils import make_database
from ..lib import ChildRefType, Family, Person
from ..relationship import get_relationship_calculator

BIRTH = ChildRefType.BIRTH


def _make_db():
    db = make_database("sqlite")
    db.load(":memory:")
    return db


def _add_person(db, gender=Person.MALE):
    person = Person()
    person.set_gender(gender)
    with DbTxn("add person", db) as trans:
        db.add_person(person, trans)
    return person


def _add_family(db, father=None, mother=None):
    family = Family()
    if father is not None:
        family.set_father_handle(father.handle)
    if mother is not None:
        family.set_mother_handle(mother.handle)
    with DbTxn("add family", db) as trans:
        db.add_family(family, trans)
    return family


def _add_child(db, family, child, frel=BIRTH, mrel=BIRTH):
    with DbTxn("add child", db) as trans:
        db.add_child_to_family(
            family, child, mrel=ChildRefType(mrel), frel=ChildRefType(frel), trans=trans
        )


def _build_diamond_chain(db, levels):
    """Level 0 is a founder couple. At each level, the couple has two
    children (a son and a daughter) who become the couple at the next
    level -- so at every level, both parents are siblings, each reached
    via a *different* parent when searching upward from below. That is
    exactly the crosslink pattern that made the pre-fix `__apply_filter`
    exponential: the shared level-N ancestor pair gets reached twice
    (once via the son's branch, once via the daughter's), and without
    memoization, both revisits re-walk everything above them -- which
    itself has the same doubling at every earlier level too.

    Returns the two children of the final level's couple.
    """
    father = _add_person(db, Person.MALE)
    mother = _add_person(db, Person.FEMALE)
    family = _add_family(db, father, mother)
    for _ in range(levels):
        son = _add_person(db, Person.MALE)
        daughter = _add_person(db, Person.FEMALE)
        _add_child(db, family, son)
        _add_child(db, family, daughter)
        family = _add_family(db, son, daughter)
    final_son = _add_person(db, Person.MALE)
    final_daughter = _add_person(db, Person.FEMALE)
    _add_child(db, family, final_son)
    _add_child(db, family, final_daughter)
    return final_son, final_daughter


def _count_apply_filter_calls(calc):
    """Wrap calc's own (already-fixed) __apply_filter to count calls,
    returning the mutable counter list. A linear (not exponential) call
    count as `levels` grows is the actual regression this guards."""
    counter = [0]
    orig = calc._RelationshipCalculator__apply_filter.__func__

    def counting(self, *args, **kwargs):
        counter[0] += 1
        return orig(self, *args, **kwargs)

    calc._RelationshipCalculator__apply_filter = types.MethodType(counting, calc)
    return counter


class RelationshipBasicTest(unittest.TestCase):
    """Sanity checks: ordinary relationships still come out right."""

    def setUp(self):
        self.db = _make_db()
        self.calc = get_relationship_calculator(reinit=True)

    def tearDown(self):
        self.db.close()

    def test_first_cousins(self):
        grandfather = _add_person(self.db, Person.MALE)
        grandmother = _add_person(self.db, Person.FEMALE)
        grandparent_family = _add_family(self.db, grandfather, grandmother)

        parent_a = _add_person(self.db, Person.MALE)
        parent_b = _add_person(self.db, Person.FEMALE)
        _add_child(self.db, grandparent_family, parent_a)
        _add_child(self.db, grandparent_family, parent_b)

        spouse_a = _add_person(self.db, Person.FEMALE)
        spouse_b = _add_person(self.db, Person.MALE)
        family_a = _add_family(self.db, parent_a, spouse_a)
        family_b = _add_family(self.db, spouse_b, parent_b)

        cousin1 = _add_person(self.db, Person.MALE)
        cousin2 = _add_person(self.db, Person.FEMALE)
        _add_child(self.db, family_a, cousin1)
        _add_child(self.db, family_b, cousin2)

        p1 = self.db.get_person_from_handle(cousin1.handle)
        p2 = self.db.get_person_from_handle(cousin2.handle)
        rel_str, dist1, dist2 = self.calc.get_one_relationship(
            self.db, p1, p2, extra_info=True
        )
        self.assertEqual(rel_str, "first cousin")
        self.assertEqual((dist1, dist2), (2, 2))


class RelationshipPedigreeCollapsePerformanceTest(unittest.TestCase):
    """The actual regression: a search that revisits the same ancestor
    many times (pedigree collapse) must cost close to linear work in the
    number of generations, not exponential. Before this fix,
    __apply_filter re-derived a revisited ancestor's entire upward
    closure from the database again on every revisit, and since this
    chain's crosslink pattern repeats at every level, that made the call
    count double per level -- 2^N for N levels. Asserting on the call
    count (not wall-clock time) keeps this deterministic on slow CI
    hardware; the wall-clock bound is a generous backstop for a genuine
    hang, not the primary check.
    """

    def test_call_count_is_linear_not_exponential(self):
        counts = {}
        for levels in (4, 8, 12):
            db = _make_db()
            try:
                child1, child2 = _build_diamond_chain(db, levels)
                calc = get_relationship_calculator(reinit=True)
                counter = _count_apply_filter_calls(calc)
                p1 = db.get_person_from_handle(child1.handle)
                p2 = db.get_person_from_handle(child2.handle)
                data, _msg = calc.get_relationship_distance_new(
                    db, p1, p2, all_dist=True, all_families=True, only_birth=False
                )
                self.assertNotEqual(data[0][0], -1, "expected a relationship to be found")
                counts[levels] = counter[0]
            finally:
                db.close()

        # Exponential (2^levels) would give roughly 16x more calls for
        # each +4 levels; linear-ish memoized growth gives a small,
        # bounded multiple. Generous bound (4x per +4 levels) to stay
        # robust to incidental call-count changes elsewhere, while still
        # failing hard against a real regression back to exponential.
        self.assertLess(counts[8], counts[4] * 4)
        self.assertLess(counts[12], counts[8] * 4)

    def test_completes_quickly_at_real_depth(self):
        """12 levels of unbroken pedigree collapse, safely within the
        default max_depth=15, used to hang or take an exponential amount
        of time before this fix. A generous wall-clock bound (well over
        what this should ever take) catches an actual hang without being
        flaky on slow CI machines."""
        import time

        db = _make_db()
        try:
            child1, child2 = _build_diamond_chain(db, 12)
            calc = get_relationship_calculator(reinit=True)
            p1 = db.get_person_from_handle(child1.handle)
            p2 = db.get_person_from_handle(child2.handle)
            start = time.perf_counter()
            rel_str, _dist1, _dist2 = calc.get_one_relationship(
                db, p1, p2, extra_info=True
            )
            elapsed = time.perf_counter() - start
            self.assertNotEqual(rel_str, "")
            self.assertLess(elapsed, 10.0)
        finally:
            db.close()


class RelationshipMaxCommonResultsTest(unittest.TestCase):
    """`set_max_common_results` bounds how many distinct non-dominated
    common-ancestor paths get_relationship_distance_new(all_dist=True)
    will compute, nearest-first -- see its docstring. A heavily
    collapsed tree can have combinatorially many such paths to report
    (observed: 122,880 for one pair on a real 100,000-person tree), so
    this cap is load-bearing for the performance fix, not just a
    convenience."""

    def test_cap_truncates_result_count(self):
        db = _make_db()
        try:
            child1, child2 = _build_diamond_chain(db, 10)
            p1 = db.get_person_from_handle(child1.handle)
            p2 = db.get_person_from_handle(child2.handle)

            calc = get_relationship_calculator(reinit=True)
            calc.set_max_common_results(5)
            data, _msg = calc.get_relationship_distance_new(
                db, p1, p2, all_dist=True, all_families=True, only_birth=False
            )
            self.assertEqual(len(data), 5)

            calc_uncapped = get_relationship_calculator(reinit=True)
            calc_uncapped.set_max_common_results(None)
            data_uncapped, _msg = calc_uncapped.get_relationship_distance_new(
                db, p1, p2, all_dist=True, all_families=True, only_birth=False
            )
            self.assertGreater(len(data_uncapped), 1000)
        finally:
            db.close()

    def test_default_cap_is_set(self):
        calc = get_relationship_calculator(reinit=True)
        self.assertIsNotNone(calc.get_max_common_results())
        self.assertGreater(calc.get_max_common_results(), 0)


class RelationshipMultipleParentFamiliesTest(unittest.TestCase):
    """A person with more than one recorded parent family (e.g. a
    step-parent alongside a birth parent) is deliberately excluded from
    the memoization fix -- see `_pmap_append_checked`'s docstring and
    `__apply_filter`'s "only_one_family" comment -- and instead re-derived
    from the database on every revisit, same as before this fix. This
    just confirms that fallback path still works correctly, since
    get_one_relationship()/get_all_relationships() always pass
    all_families=True."""

    def test_all_families_true_with_two_parent_families(self):
        db = _make_db()
        try:
            bio_father = _add_person(db, Person.MALE)
            mother = _add_person(db, Person.FEMALE)
            bio_family = _add_family(db, bio_father, mother)

            step_father = _add_person(db, Person.MALE)
            step_family = _add_family(db, step_father, mother)

            child = _add_person(db, Person.MALE)
            _add_child(db, bio_family, child, frel=BIRTH, mrel=BIRTH)
            _add_child(
                db, step_family, child, frel=ChildRefType.STEPCHILD, mrel=BIRTH
            )
            self.assertEqual(len(child.get_parent_family_handle_list()), 2)

            sibling = _add_person(db, Person.FEMALE)
            _add_child(db, bio_family, sibling)

            calc = get_relationship_calculator(reinit=True)
            p1 = db.get_person_from_handle(child.handle)
            p2 = db.get_person_from_handle(sibling.handle)
            rel_str, dist1, dist2 = calc.get_one_relationship(
                db, p1, p2, extra_info=True
            )
            self.assertEqual(rel_str, "sister")
            self.assertEqual((dist1, dist2), (1, 1))
        finally:
            db.close()


class RelationshipLoopDetectionTest(unittest.TestCase):
    """Genuine cyclic data (a data-integrity error, not a normal tree)
    must still be detected -- see `_pmap_append_checked`'s bounded
    replacement for the original's O(n^2)-per-append inline check."""

    def test_cycle_is_detected(self):
        db = _make_db()
        try:
            person_a = _add_person(db, Person.MALE)
            person_b = _add_person(db, Person.MALE)
            family_ab = _add_family(db, person_a, None)
            _add_child(db, family_ab, person_b)
            family_ba = _add_family(db, person_b, None)
            _add_child(db, family_ba, person_a)  # closes the cycle

            calc = get_relationship_calculator(reinit=True)
            p1 = db.get_person_from_handle(person_a.handle)
            p2 = db.get_person_from_handle(person_b.handle)
            calc.get_one_relationship(db, p1, p2, extra_info=True)
            self.assertTrue(calc._RelationshipCalculator__loop_detected)
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
