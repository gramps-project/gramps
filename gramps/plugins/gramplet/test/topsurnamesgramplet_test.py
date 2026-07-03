#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Brian Caudill
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
Unittest for the Top Surnames gramplet surname tally.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest
from collections import defaultdict

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib import Name, Person, Surname
from gramps.gen.types import PersonHandle
from gramps.plugins.gramplet.topsurnamesgramplet import record_surnames


# -------------------------------------------------------------------------
#
# Test helpers
#
# -------------------------------------------------------------------------
class FakeDb:
    """
    Minimal database stand-in exposing only the name-group mapping that
    ``record_surnames`` consults.  An empty mapping leaves every surname
    grouped under itself (the no-grouping case the original tests exercise).
    """

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self._mapping = mapping or {}

    def get_name_group_mapping(self, surname: str) -> str:
        return self._mapping.get(surname, surname)


def make_name(surname_text: str) -> Name:
    """
    Build a Name carrying a single surname.
    """
    name = Name()
    surname = Surname()
    surname.set_surname(surname_text)
    name.add_surname(surname)
    return name


def make_person(handle: str, primary: str, alternates: tuple[str, ...] = ()) -> Person:
    """
    Build a Person with the given primary surname and alternate surnames.
    """
    person = Person()
    person.set_handle(handle)
    person.set_primary_name(make_name(primary))
    for alt in alternates:
        person.add_alternate_name(make_name(alt))
    return person


def tally(
    people: list[Person], db: object | None = None
) -> tuple[dict[str, int], dict[str, PersonHandle]]:
    """
    Run record_surnames over a list of people and return the tallies.
    """
    db = db if db is not None else FakeDb()
    surnames: dict[str, int] = defaultdict(int)
    representative_handle: dict[str, PersonHandle] = {}
    for person in people:
        record_surnames(db, person, surnames, representative_handle)
    return surnames, representative_handle


# -------------------------------------------------------------------------
#
# TopSurnamesTest
#
# -------------------------------------------------------------------------
class TopSurnamesTest(unittest.TestCase):
    """
    Test surname tallying and representative selection (bug #11101).
    """

    def test_counts_primary_and_alternate_names(self):
        """
        A person is counted under both their primary and alternate surnames.
        """
        people = [make_person("P1", "Webb", alternates=("Allen",))]
        surnames, _ = tally(people)
        self.assertEqual(surnames["Webb"], 1)
        self.assertEqual(surnames["Allen"], 1)

    def test_representative_has_matching_primary_surname(self):
        """
        Bug #11101: the representative for a surname must be a person whose
        primary surname matches it, even when an alternate-name carrier is
        processed last.

        "Allen" has "Webb" as an alternate name and is iterated after the real
        Webb, so the pre-fix code left her as Webb's representative.
        """
        webb = make_person("WEBB", "Webb")
        allen = make_person("ALLEN", "Allen", alternates=("Webb",))
        # Order matters: the alternate-name carrier comes last.
        _, representative_handle = tally([webb, allen])
        self.assertEqual(representative_handle["Webb"], "WEBB")
        self.assertEqual(representative_handle["Allen"], "ALLEN")

    def test_representative_correct_regardless_of_order(self):
        """
        The primary-name carrier wins even when processed after the alternate.
        """
        allen = make_person("ALLEN", "Allen", alternates=("Webb",))
        webb = make_person("WEBB", "Webb")
        _, representative_handle = tally([allen, webb])
        self.assertEqual(representative_handle["Webb"], "WEBB")

    def test_alternate_only_surname_falls_back_to_first_seen(self):
        """
        When no person carries a surname as their primary name, a deterministic
        fallback (the first person seen with it as an alternate) is used.

        Such surnames are inherently best-effort: the Same Surnames quick view
        derives the surname from the representative's primary name, so no
        representative can make the report match a surname nobody holds as a
        primary name.
        """
        smith = make_person("SMITH", "Smith", alternates=("Jones",))
        brown = make_person("BROWN", "Brown", alternates=("Jones",))
        _, representative_handle = tally([smith, brown])
        self.assertEqual(representative_handle["Jones"], "SMITH")

    def test_multiple_primary_carriers_keep_a_matching_representative(self):
        """
        With several primary-name carriers, the representative still has a
        matching primary surname.
        """
        people = [
            make_person("W1", "Webb"),
            make_person("ALLEN", "Allen", alternates=("Webb",)),
            make_person("W2", "Webb"),
        ]
        surnames, representative_handle = tally(people)
        self.assertIn(representative_handle["Webb"], ("W1", "W2"))
        self.assertEqual(surnames["Webb"], 3)


# -------------------------------------------------------------------------
#
# SurnameGroupingConsistencyTest (bug #6825)
#
# -------------------------------------------------------------------------
class SurnameGroupingConsistencyTest(unittest.TestCase):
    """
    Bug #6825: surname consumers must agree on the grouping.

    When two surnames are grouped together via the database-wide name-group
    mapping ("Group As -> Group All"), every surname consumer must treat
    them as one group.  Historically the Top Surnames gramplet and the Same
    Surnames quick view disagreed: both grouped by ``Name.get_group_name()``
    (which ignores the database-wide mapping) and the quick view's filter
    rule matched on the raw surname.
    """

    @classmethod
    def setUpClass(cls):
        # A real in-memory database is needed: the Same Surnames filter rule
        # applies against the live db, and the global name-group mapping
        # lives in the db, not on the Name objects.
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")
        cls.smith = make_person("H_SMITH", "Smith")
        cls.jones = make_person("H_JONES", "Jones")
        with DbTxn("setup", cls.db) as txn:
            cls.db.add_person(cls.smith, txn)
            cls.db.add_person(cls.jones, txn)
        # "Group As Smith -> Group All": a global mapping, no per-name
        # override on the Jones name.
        cls.db.set_name_group_mapping("Jones", "Smith")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_samesurnames_filter_honors_global_mapping(self):
        """
        The Same Surnames filter rule gathers a globally-grouped surname.

        Pre-fix this is RED: the rule matched the raw surname, so Jones
        (grouped under Smith only via the global mapping) was not gathered
        with Smith.
        """
        from gramps.plugins.quickview.samesurnames import SameSurname

        rule = SameSurname(["Smith"])
        self.assertTrue(rule.apply_to_one(self.db, self.smith))
        self.assertTrue(rule.apply_to_one(self.db, self.jones))

    def test_samesurnames_run_path_gathers_the_group(self):
        """
        Launching the quick view from either person returns the whole group.
        """
        from gramps.plugins.quickview.samesurnames import (
            _same_surname_handles,
        )

        expected = {"H_SMITH", "H_JONES"}
        self.assertEqual(set(_same_surname_handles(self.db, self.smith)), expected)
        self.assertEqual(set(_same_surname_handles(self.db, self.jones)), expected)

    def test_topsurnames_honors_global_mapping(self):
        """
        The Top Surnames tally groups the globally-mapped surname under
        Smith.
        """
        surnames, _ = tally([self.smith, self.jones], db=self.db)
        self.assertEqual(surnames.get("Smith"), 2)
        self.assertNotIn("Jones", surnames)

    def test_consumers_agree_on_the_grouping(self):
        """
        The two consumers group the same people together (the invariant).
        """
        from gramps.plugins.quickview.samesurnames import (
            _same_surname_handles,
        )

        same_surnames_group = set(_same_surname_handles(self.db, self.smith))

        surnames, representative_handle = tally([self.smith, self.jones], db=self.db)
        # The single group the gramplet reports, expanded to its members.
        top_group = set(
            _same_surname_handles(
                self.db,
                self.db.get_person_from_handle(representative_handle["Smith"]),
            )
        )

        self.assertEqual(same_surnames_group, top_group)
        self.assertEqual(same_surnames_group, {"H_SMITH", "H_JONES"})
        self.assertEqual(list(surnames), ["Smith"])


if __name__ == "__main__":
    unittest.main()
