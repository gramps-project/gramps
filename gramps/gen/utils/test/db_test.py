#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank <doug.blank@gmail.com>
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
Unit tests for gramps/gen/utils/db.py
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..db import for_each_ancestor
from ...db.utils import import_as_dict
from ...const import TEST_DIR
from ...user import User

EXAMPLE = os.path.join(TEST_DIR, "example.gramps")


# -------------------------------------------------------------------------
#
# ForEachAncestorTest
#
# -------------------------------------------------------------------------
class ForEachAncestorTest(unittest.TestCase):
    """Tests for the for_each_ancestor utility function."""

    @classmethod
    def setUpClass(cls):
        """Import example database once for all tests."""
        cls.db = import_as_dict(EXAMPLE, User())

    def test_all_ancestors_collected(self):
        """
        for_each_ancestor visits the start person and all their ancestors.
        I0044 (handle GNUJQCL9MD64AM56OH) has 6 ancestors plus themselves.
        """
        person = self.db.get_person_from_gramps_id("I0044")
        collected = []

        def collect(data, handle):
            data.append(handle)
            return False

        result = for_each_ancestor(self.db, [person.handle], collect, collected)

        self.assertEqual(result, 0)
        self.assertEqual(
            set(collected),
            {
                "GNUJQCL9MD64AM56OH",
                "44WJQCLCQIPZUB0UH",
                "D3WJQCCGV58IP8PNHZ",
                "35WJQC1B7T7NPV8OLV",
                "46WJQCIOLQ0KOX2XCC",
                "H1DKQC4YGZ5A61FGS",
                "W2DKQCV4H3EZUJ35DX",
            },
        )

    def test_no_parents_visits_only_start(self):
        """
        A person with no parent families produces a visit to just themselves.
        I0000 (handle d5839c1237765987724) has no parents in the example db.
        """
        person = self.db.get_person_from_gramps_id("I0000")
        collected = []

        def collect(data, handle):
            data.append(handle)
            return False

        result = for_each_ancestor(self.db, [person.handle], collect, collected)

        self.assertEqual(result, 0)
        self.assertEqual(collected, ["d5839c1237765987724"])

    def test_early_exit_returns_one(self):
        """
        When func returns True the traversal stops and for_each_ancestor returns 1.
        """
        person = self.db.get_person_from_gramps_id("I0044")
        visited = []

        def stop_immediately(data, handle):
            data.append(handle)
            return True

        result = for_each_ancestor(self.db, [person.handle], stop_immediately, visited)

        self.assertEqual(result, 1)
        self.assertEqual(len(visited), 1)

    def test_early_exit_on_specific_ancestor(self):
        """
        Early exit on a known ancestor stops the traversal and returns 1.
        """
        person = self.db.get_person_from_gramps_id("I0044")
        target = "44WJQCLCQIPZUB0UH"
        found = []

        def find_target(data, handle):
            if handle == target:
                data.append(handle)
                return True
            return False

        result = for_each_ancestor(self.db, [person.handle], find_target, found)

        self.assertEqual(result, 1)
        self.assertEqual(found, [target])

    def test_complete_traversal_returns_zero(self):
        """
        When func never returns True, for_each_ancestor returns 0.
        """
        person = self.db.get_person_from_gramps_id("I0044")

        result = for_each_ancestor(self.db, [person.handle], lambda d, h: False, [])

        self.assertEqual(result, 0)

    def test_cycle_safety(self):
        """
        Each person handle is visited at most once even if supplied multiple
        times in the start list (simulates a reachable cycle).
        """
        person = self.db.get_person_from_gramps_id("I0044")
        visited = []

        def collect(data, handle):
            data.append(handle)
            return False

        # Supplying the same handle twice in start should not cause double-visits.
        for_each_ancestor(self.db, [person.handle, person.handle], collect, visited)

        self.assertEqual(len(visited), len(set(visited)))


if __name__ == "__main__":
    unittest.main()
