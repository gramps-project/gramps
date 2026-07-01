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
Unittest for the shared "unique surnames" count (bug #6793).

The Top Surnames, Surname Cloud and Statistics gramplets each report a "unique
surnames" total.  They used to enumerate unique surnames by three different
rules, so the same tree produced three different totals.  They now share one
rule -- :func:`gramps.plugins.lib.libsurnames.record_surnames` -- which every
gramplet calls in its single people-pass to build a tally of distinct,
non-empty surname group names.  These tests drive that shared routine on a
fixture tree and assert the rule is one and the same across the three gramplets.
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
from gramps.gen.lib import Name, Person, Surname
from gramps.gen.types import PersonHandle

# The production rule under test.
from gramps.plugins.lib.libsurnames import record_surnames

# Each gramplet that reports "unique surnames" re-uses the shared rule; importing
# them proves the wiring is in place (and that the modules import import-light).
from gramps.plugins.gramplet.topsurnamesgramplet import (
    record_surnames as top_record_surnames,
)
from gramps.plugins.gramplet.surnamecloudgramplet import (
    record_surnames as cloud_record_surnames,
)
from gramps.plugins.gramplet.statsgramplet import (
    record_surnames as stats_record_surnames,
)


# -------------------------------------------------------------------------
#
# Test helpers
#
# -------------------------------------------------------------------------
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


def tally_unique(people: list[Person]) -> int:
    """
    Number of unique surnames via the shared rule used by all three gramplets:
    the ``len`` of the ``record_surnames`` tally over a people list.
    """
    surnames: dict[str, int] = defaultdict(int)
    representative_handle: dict[str, PersonHandle] = {}
    for person in people:
        record_surnames(person, surnames, representative_handle)
    return len(surnames)


# -------------------------------------------------------------------------
#
# Fixture
#
# -------------------------------------------------------------------------
# A tree exercising the cases that made the three gramplets diverge:
#   * a surname shared by several people (Webb)
#   * a person with an alternate (married) name (Souza -> Varela)
#   * a surname that only ever appears as an alternate name (Jones)
#   * a person with no surname at all (must NOT add to the count)
# Distinct non-empty group names: Webb, Allen, Souza, Varela, Smith, Brown, Jones
# -> 7 unique surnames (the empty no-surname is not counted).
FIXTURE = [
    make_person("P1", "Webb"),
    make_person("P2", "Webb", alternates=("Allen",)),
    make_person("P3", "Souza", alternates=("Varela",)),
    make_person("P4", "Smith", alternates=("Jones",)),
    make_person("P5", "Brown", alternates=("Jones",)),
    make_person("P6", ""),
]


# -------------------------------------------------------------------------
#
# SurnameCountTest
#
# -------------------------------------------------------------------------
class SurnameCountTest(unittest.TestCase):
    """
    The gramplets that report "unique surnames" must agree (bug #6793).
    """

    def setUp(self):
        self.people = FIXTURE
        # Distinct non-empty group names: Webb, Allen, Souza, Varela, Smith,
        # Brown, Jones -> 7.  The no-surname person (P6) is not counted.
        self.expected = 7

    def test_counts_distinct_nonempty_group_names(self):
        """
        The shared rule counts distinct surname group names across each person's
        primary and alternate names, excluding the empty (no-surname) one.
        """
        self.assertEqual(tally_unique(self.people), self.expected)

    def test_all_gramplets_share_one_rule(self):
        """
        Every gramplet that reports "unique surnames" builds its tally from the
        very same shared routine, so the three totals are identical for a tree.
        """
        self.assertIs(top_record_surnames, record_surnames)
        self.assertIs(cloud_record_surnames, record_surnames)
        self.assertIs(stats_record_surnames, record_surnames)

    def test_alternate_name_surnames_are_counted(self):
        """
        A surname that only ever appears as an alternate name (e.g. a married
        name) is still counted once -- the old Statistics rule, keyed on the
        primary-name index, missed these.
        """
        people = [make_person("A", "Souza", alternates=("Varela",))]
        # Souza + Varela = 2 distinct group names.
        self.assertEqual(tally_unique(people), 2)

    def test_empty_surname_is_not_counted(self):
        """
        A person with no surname contributes no unique surname -- the empty
        string is not a surname (bug #6793; previously the empty group name was
        tallied, inflating the count by one for any no-surname person).
        """
        self.assertEqual(tally_unique([make_person("N", "")]), 0)
        # A no-surname person alongside a real one does not add to the count.
        self.assertEqual(
            tally_unique([make_person("R", "Webb"), make_person("N", "")]), 1
        )


if __name__ == "__main__":
    unittest.main()
