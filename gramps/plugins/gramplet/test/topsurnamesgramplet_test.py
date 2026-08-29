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
from gramps.gen.lib import Name, Person, Surname
from gramps.gen.types import PersonHandle
from gramps.plugins.gramplet.topsurnamesgramplet import record_surnames


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


def tally(people: list[Person]) -> tuple[dict[str, int], dict[str, PersonHandle]]:
    """
    Run record_surnames over a list of people and return the tallies.
    """
    surnames: dict[str, int] = defaultdict(int)
    representative_handle: dict[str, PersonHandle] = {}
    for person in people:
        record_surnames(person, surnames, representative_handle)
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

    def test_reported_repro_6826_clicked_surname_resolves_to_primary_carrier(self):
        """
        Bug #6826 (reported repro): a person P1 with primary surname "A" and
        alternate surname "B", plus a person P2 whose primary surname is "B".

        The Same Surnames quick view re-derives the clicked surname from the
        representative's *primary* name, so the representative for "B" must be
        P2 (whose primary name is "B") and never P1 (whose primary name is "A").
        Otherwise double-clicking "B" opens "People sharing the surname 'A'".

        Pre-fix the representative was overwritten unconditionally, so whichever
        of the two was iterated last won "B" -- making the result depend on
        database order.  Assert the primary-name carrier wins for *both* orders.
        """
        for order in (("P2", "P1"), ("P1", "P2")):
            people_by_handle = {
                "P1": make_person("P1", "A", alternates=("B",)),
                "P2": make_person("P2", "B"),
            }
            people = [people_by_handle[handle] for handle in order]
            surnames, representative_handle = tally(people)
            # Clicking "B" must open the report for surname B (P2's primary).
            self.assertEqual(
                representative_handle["B"],
                "P2",
                msg=f"iteration order {order}: 'B' must resolve to the "
                "primary-B carrier P2, not the alternate-name carrier P1",
            )
            # "A" is held by P1 as a primary name.
            self.assertEqual(representative_handle["A"], "P1")
            # "B" is counted for both: P1's alternate and P2's primary.
            self.assertEqual(surnames["B"], 2)
            self.assertEqual(surnames["A"], 1)


if __name__ == "__main__":
    unittest.main()
