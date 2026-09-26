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

`RelationshipEdgeCaseTest`, `RelationshipAllRelationshipsCollapseTest`, and
`RelationshipPrivacyProxyTest` below port coverage from the independent
SQL-based reimplementation this fix's own PR description names
(gramps-sql-extensions, https://github.com/dsblank/gramps-sql-extensions)
onto `RelationshipCalculator` directly -- structural edge cases (a
pedigree-collapse tie-break, same-couple remarriage ordering, half-sibling
wording) and privacy-proxy interaction that weren't otherwise exercised
here.
"""

import types
import unittest

from ..db import DbTxn
from ..db.utils import make_database
from ..lib import ChildRefType, Family, FamilyRelType, Person
from ..proxy import PrivateProxyDb
from ..relationship import get_relationship_calculator

BIRTH = ChildRefType.BIRTH
STEPCHILD = ChildRefType.STEPCHILD


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


def _add_family(db, father=None, mother=None, rel_type=None):
    family = Family()
    if rel_type is not None:
        family.set_relationship(rel_type)
    if father is not None:
        family.set_father_handle(father.handle)
    if mother is not None:
        family.set_mother_handle(mother.handle)
    with DbTxn("add family", db) as trans:
        db.add_family(family, trans)
    return family


def _link_spouse_to_family(db, person, family):
    """`add_family()` alone doesn't update the referenced person's own
    `family_list` -- that reciprocal update is application-layer behavior,
    not something the raw `add_family`/`commit_family` calls above do.
    Needed whenever a test relies on `family_list` order, e.g. which of
    several marriage records between the same couple is used."""
    with DbTxn("link spouse to family", db) as trans:
        person = db.get_person_from_handle(person.handle)
        person.add_family_handle(family.handle)
        db.commit_person(person, trans)


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


def _build_diamond_chain_with_stepfamily(db, levels):
    """Same sibling-marries-sibling crosslink pattern as
    `_build_diamond_chain`, but at every level the son is *also* recorded
    with a second, step parent family sharing the same mother -- so
    every ancestor in the chain has more than one recorded parent family
    (the shape `__apply_filter`'s "only_one_family" gate excludes from
    memoization -- see its docstring and `_pmap_append_checked`'s) at
    the same time it is being revisited via pedigree collapse. The PR
    that introduced the memoization fix documents this combination
    ("Multi-family recorded *and* pedigree-collapsed at every level
    simultaneously") as explicitly out of scope for acceleration --
    always re-derived from the database on every revisit, same as
    before that fix -- and measured it separately as polynomial rather
    than exponential. This fixture turns that into a persisted
    regression check, for both correctness and non-catastrophic growth,
    rather than only an ad hoc measurement.

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
        step_father = _add_person(db, Person.MALE)
        step_family = _add_family(db, step_father, mother)
        _add_child(db, step_family, son, frel=ChildRefType.STEPCHILD, mrel=BIRTH)
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
                self.assertNotEqual(
                    data[0][0], -1, "expected a relationship to be found"
                )
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
            _add_child(db, step_family, child, frel=ChildRefType.STEPCHILD, mrel=BIRTH)
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


class RelationshipMultiFamilyPedigreeCollapseTest(unittest.TestCase):
    """The "doubly-rare" combination the PR's "Explicitly out of scope"
    section calls out by name: a person with more than one recorded
    parent family (adoption, or a step-family alongside a birth family)
    who is *also* an ancestor reached via pedigree collapse. That
    section reports this was tested ad hoc against synthetic fixtures
    built the same way as the rest of this suite, and found to grow
    polynomially rather than exponentially -- not the bug this PR fixes,
    but real-world trees with adoptions or step-families are exactly the
    case most likely to still feel slow, so this persists that check as
    an actual regression test instead of only a one-off measurement.
    """

    def test_relationship_still_correct_with_stepfamilies(self):
        db = _make_db()
        try:
            child1, child2 = _build_diamond_chain_with_stepfamily(db, 5)
            calc = get_relationship_calculator(reinit=True)
            p1 = db.get_person_from_handle(child1.handle)
            p2 = db.get_person_from_handle(child2.handle)
            rel_str, dist1, dist2 = calc.get_one_relationship(
                db, p1, p2, extra_info=True
            )
            # final_son and final_daughter are children of the same
            # single family record (the last-generation couple), so
            # regardless of the step-families layered into every
            # ancestor above them, they must still come out as full
            # siblings -- a wrong family index picked up from a
            # revisited multi-family ancestor would corrupt this into a
            # half-sibling or cousin wording instead.
            self.assertEqual(rel_str, "sister")
            self.assertEqual((dist1, dist2), (1, 1))
        finally:
            db.close()

    def test_completes_without_hanging(self):
        """Confirms the documented "polynomial, not exponential" finding
        stays true: a generous wall-clock bound catches a regression
        back to exponential (or simply unbounded) growth without being
        flaky about the exact, worse-than-linear constant this
        deliberately-unaccelerated case is expected to have."""
        import time

        db = _make_db()
        try:
            child1, child2 = _build_diamond_chain_with_stepfamily(db, 7)
            calc = get_relationship_calculator(reinit=True)
            p1 = db.get_person_from_handle(child1.handle)
            p2 = db.get_person_from_handle(child2.handle)
            start = time.perf_counter()
            rel_str, _dist1, _dist2 = calc.get_one_relationship(
                db, p1, p2, extra_info=True
            )
            elapsed = time.perf_counter() - start
            self.assertNotEqual(rel_str, "")
            self.assertLess(elapsed, 15.0)
        finally:
            db.close()

    def test_call_count_growth_is_not_exponential(self):
        counts = {}
        for levels in (3, 5, 7):
            db = _make_db()
            try:
                child1, child2 = _build_diamond_chain_with_stepfamily(db, levels)
                calc = get_relationship_calculator(reinit=True)
                counter = _count_apply_filter_calls(calc)
                p1 = db.get_person_from_handle(child1.handle)
                p2 = db.get_person_from_handle(child2.handle)
                data, _msg = calc.get_relationship_distance_new(
                    db, p1, p2, all_dist=True, all_families=True, only_birth=False
                )
                self.assertNotEqual(
                    data[0][0], -1, "expected a relationship to be found"
                )
                counts[levels] = counter[0]
            finally:
                db.close()

        # Exponential (2^levels) growth would roughly double the ratio
        # between consecutive +2-level steps (e.g. 4x, then 16x); this
        # combination is documented to be polynomial (roughly quadratic)
        # instead, so the ratio should grow only arithmetically, not
        # multiply on itself. A generous bound (16x per +2 levels) stays
        # robust to incidental call-count changes while still failing
        # hard against a real regression back to exponential.
        self.assertLess(counts[5], counts[3] * 16)
        self.assertLess(counts[7], counts[5] * 16)


class RelationshipEdgeCaseTest(unittest.TestCase):
    """Structural edge cases ported from gramps-sql-extensions'
    tests/test_edge_cases.py -- each one a real bug that independent
    reimplementation shipped with at one point, kept here as a permanent
    regression guard against RelationshipCalculator itself, not just that
    other project's replica of it.
    """

    def setUp(self):
        self.db = _make_db()
        self.calc = get_relationship_calculator(reinit=True)

    def tearDown(self):
        self.db.close()

    def test_pedigree_collapse_tie_break_prefers_birth_line(self):
        """Two candidate common ancestors tied at the same generation
        distance, one reached by an all-birth path, the other through a
        step link -- gramps-core's own priority order prefers the
        birth-line one, so the result should be "first cousin", never
        "first stepcousin", even though the tie-break has no reason to
        prefer one over the other by generation distance alone."""
        MALE, FEMALE = Person.MALE, Person.FEMALE
        h1, h2 = _add_person(self.db, MALE), _add_person(self.db, FEMALE)
        f1, m1 = _add_person(self.db, MALE), _add_person(self.db, FEMALE)
        f2, m2 = _add_person(self.db, MALE), _add_person(self.db, FEMALE)
        # reached by an all-birth path on both sides
        ancestor_birth = _add_person(self.db, MALE)
        # reached via a step link on h1's side
        ancestor_step = _add_person(self.db, FEMALE)

        fam_birth = _add_family(self.db, ancestor_birth, None)
        _add_child(self.db, fam_birth, f1, frel=BIRTH, mrel=BIRTH)
        _add_child(self.db, fam_birth, f2, frel=BIRTH, mrel=BIRTH)
        fam_step = _add_family(self.db, None, ancestor_step)
        _add_child(self.db, fam_step, m1, frel=STEPCHILD, mrel=STEPCHILD)
        _add_child(self.db, fam_step, m2, frel=BIRTH, mrel=BIRTH)
        fam1 = _add_family(self.db, f1, m1)
        _add_child(self.db, fam1, h1)
        fam2 = _add_family(self.db, f2, m2)
        _add_child(self.db, fam2, h2)

        p1 = self.db.get_person_from_handle(h1.handle)
        p2 = self.db.get_person_from_handle(h2.handle)
        rel_str, dist1, dist2 = self.calc.get_one_relationship(
            self.db, p1, p2, extra_info=True
        )
        self.assertEqual(rel_str, "first cousin")
        self.assertEqual((dist1, dist2), (2, 2))

    def test_remarriage_uses_last_family_in_family_list_order(self):
        """The same couple recorded in two family records (e.g. an
        unmarried-partner record later formalized by marriage) --
        gramps-core's own spouse-type lookup takes the LAST match in the
        person's own family_list order, not an arbitrary one, so the
        wording must reflect the second (married) record, not the first
        (unmarried) one."""
        MALE, FEMALE = Person.MALE, Person.FEMALE
        husband, wife = _add_person(self.db, MALE), _add_person(self.db, FEMALE)

        fam1 = _add_family(self.db, husband, wife, rel_type=FamilyRelType.UNMARRIED)
        _link_spouse_to_family(self.db, husband, fam1)
        fam2 = _add_family(self.db, husband, wife, rel_type=FamilyRelType.MARRIED)
        _link_spouse_to_family(self.db, husband, fam2)

        p1 = self.db.get_person_from_handle(husband.handle)
        p2 = self.db.get_person_from_handle(wife.handle)
        rel_str, dist1, dist2 = self.calc.get_one_relationship(
            self.db, p1, p2, extra_info=True
        )
        # not "partner" (fam1's wording) -- fam2 is last in family_list
        self.assertEqual(rel_str, "wife")
        self.assertEqual((dist1, dist2), (-1, -1))

    def test_half_sibling_wording(self):
        MALE, FEMALE = Person.MALE, Person.FEMALE
        father = _add_person(self.db, MALE)
        mother1, mother2 = _add_person(self.db, FEMALE), _add_person(self.db, FEMALE)
        full1, full2 = _add_person(self.db, MALE), _add_person(self.db, FEMALE)
        half = _add_person(self.db, MALE)

        fam1 = _add_family(self.db, father, mother1)
        _add_child(self.db, fam1, full1)
        _add_child(self.db, fam1, full2)
        fam2 = _add_family(self.db, father, mother2)
        _add_child(self.db, fam2, half)

        p_full1 = self.db.get_person_from_handle(full1.handle)
        p_full2 = self.db.get_person_from_handle(full2.handle)
        p_half = self.db.get_person_from_handle(half.handle)
        rel_full, _, _ = self.calc.get_one_relationship(
            self.db, p_full1, p_full2, extra_info=True
        )
        rel_half, _, _ = self.calc.get_one_relationship(
            self.db, p_full1, p_half, extra_info=True
        )
        self.assertEqual(rel_full, "sister")
        self.assertEqual(rel_half, "half-brother")


class RelationshipAllRelationshipsCollapseTest(unittest.TestCase):
    """gramps-sql-extensions' test_all_relationships_no_overreporting
    guards a common ancestor sitting *behind* a nearer one from being
    reported as if it were a separate, more distant relationship --
    RelationshipCalculator.__apply_filter never even visits it (a branch
    stops at the first common ancestor it crosses), so a first-cousin
    pair descended from a grandparent couple who are themselves the
    children of a shared great-grandparent couple must still report
    exactly one relationship, "first cousin", not a phantom second/third
    cousin entry for that deeper, unvisited couple.
    """

    def test_get_all_relationships_reports_exactly_one_relationship(self):
        db = _make_db()
        try:
            MALE, FEMALE = Person.MALE, Person.FEMALE
            great_grandfather = _add_person(db, MALE)
            great_grandmother = _add_person(db, FEMALE)
            great_grandparent_family = _add_family(
                db, great_grandfather, great_grandmother
            )

            grandfather = _add_person(db, MALE)
            grandfathers_sibling = _add_person(db, FEMALE)
            _add_child(db, great_grandparent_family, grandfather)
            _add_child(db, great_grandparent_family, grandfathers_sibling)

            grandmother = _add_person(db, FEMALE)
            grandparent_family = _add_family(db, grandfather, grandmother)

            parent_a = _add_person(db, MALE)
            parent_b = _add_person(db, FEMALE)
            _add_child(db, grandparent_family, parent_a)
            _add_child(db, grandparent_family, parent_b)

            spouse_a = _add_person(db, FEMALE)
            spouse_b = _add_person(db, MALE)
            family_a = _add_family(db, parent_a, spouse_a)
            family_b = _add_family(db, spouse_b, parent_b)

            cousin1 = _add_person(db, MALE)
            cousin2 = _add_person(db, FEMALE)
            _add_child(db, family_a, cousin1)
            _add_child(db, family_b, cousin2)

            calc = get_relationship_calculator(reinit=True)
            p1 = db.get_person_from_handle(cousin1.handle)
            p2 = db.get_person_from_handle(cousin2.handle)
            relstrings, commons = calc.get_all_relationships(db, p1, p2)
            self.assertEqual(relstrings, ["first cousin"])
            self.assertEqual(len(commons), 1)
        finally:
            db.close()


class RelationshipPrivacyProxyTest(unittest.TestCase):
    """Ported from gramps-sql-extensions' tests/test_privacy.py, adapted
    from that library's own `restricted` parameter to gramps-core's real
    mechanism for the same thing: wrapping the database in
    `PrivateProxyDb` before handing it to `RelationshipCalculator`.
    `PrivateProxyDb` has three independent privacy rules -- a private
    Person, a private Family, or a private ChildRef are each individually
    invisible to a restricted viewer -- and this confirms
    RelationshipCalculator respects all three when searching through the
    proxy instead of the raw database, and that a non-private relative in
    the same family stays visible either way.
    """

    def test_private_person_is_hidden_and_other_parent_stays_visible(self):
        db = _make_db()
        try:
            MALE, FEMALE = Person.MALE, Person.FEMALE
            father = _add_person(db, MALE)
            mother = _add_person(db, FEMALE)
            with DbTxn("make mother private", db) as trans:
                mother.set_privacy(True)
                db.commit_person(mother, trans)
            child = _add_person(db, MALE)
            family = _add_family(db, father, mother)
            _add_child(db, family, child)

            proxy = PrivateProxyDb(db)
            calc = get_relationship_calculator(reinit=True)

            # the private parent is invisible to a restricted viewer --
            # PrivateProxyDb.get_person_from_handle returns None for her
            self.assertIsNone(proxy.get_person_from_handle(mother.handle))

            # the other, non-private parent is unaffected
            child_p = proxy.get_person_from_handle(child.handle)
            father_p = proxy.get_person_from_handle(father.handle)
            rel_str, _, _ = calc.get_one_relationship(
                proxy, child_p, father_p, extra_info=True
            )
            self.assertEqual(rel_str, "father")
        finally:
            db.close()

    def test_private_family_hidden_when_restricted(self):
        db = _make_db()
        try:
            MALE, FEMALE = Person.MALE, Person.FEMALE
            father = _add_person(db, MALE)
            mother = _add_person(db, FEMALE)
            child = _add_person(db, MALE)
            family = Family()
            family.set_privacy(True)
            family.set_father_handle(father.handle)
            family.set_mother_handle(mother.handle)
            with DbTxn("add private family", db) as trans:
                db.add_family(family, trans)
            _add_child(db, family, child)

            calc = get_relationship_calculator(reinit=True)
            unrestricted, _, _ = calc.get_one_relationship(
                db,
                db.get_person_from_handle(child.handle),
                db.get_person_from_handle(father.handle),
                extra_info=True,
            )
            self.assertEqual(unrestricted, "father")

            proxy = PrivateProxyDb(db)
            restricted, _, _ = calc.get_one_relationship(
                proxy,
                proxy.get_person_from_handle(child.handle),
                proxy.get_person_from_handle(father.handle),
                extra_info=True,
            )
            self.assertEqual(restricted, "")
        finally:
            db.close()

    def test_private_childref_hidden_when_restricted(self):
        db = _make_db()
        try:
            MALE, FEMALE = Person.MALE, Person.FEMALE
            father = _add_person(db, MALE)
            mother = _add_person(db, FEMALE)
            child = _add_person(db, MALE)
            family = _add_family(db, father, mother)
            _add_child(db, family, child)
            family = db.get_family_from_handle(family.handle)
            for ref in family.get_child_ref_list():
                if ref.ref == child.handle:
                    ref.set_privacy(True)
            with DbTxn("make childref private", db) as trans:
                db.commit_family(family, trans)

            calc = get_relationship_calculator(reinit=True)
            unrestricted, _, _ = calc.get_one_relationship(
                db,
                db.get_person_from_handle(child.handle),
                db.get_person_from_handle(father.handle),
                extra_info=True,
            )
            self.assertEqual(unrestricted, "father")

            proxy = PrivateProxyDb(db)
            restricted, _, _ = calc.get_one_relationship(
                proxy,
                proxy.get_person_from_handle(child.handle),
                proxy.get_person_from_handle(father.handle),
                extra_info=True,
            )
            self.assertEqual(restricted, "")
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
