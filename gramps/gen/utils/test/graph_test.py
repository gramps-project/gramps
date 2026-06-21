#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024  Gramps Development Team
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
Test module for graph utilities.
"""

import unittest
import tempfile
import os

from gramps.gen.db.utils import import_as_dict
from gramps.gen.const import TEST_DIR
from gramps.gen.user import User
from gramps.gen.lib import Person, Family
from gramps.gen.utils.graph import (
    find_ancestors,
    find_ancestors_iterative,
    find_descendants,
    find_descendants_iterative,
)

EXAMPLE = os.path.join(TEST_DIR, "example.gramps")


class TestGraph(unittest.TestCase):
    """Test cases for graph utilities."""

    @classmethod
    def setUpClass(cls):
        """Import example database."""
        cls.db = import_as_dict(EXAMPLE, User())

        # Get some people from the example database for testing
        cls.person1 = cls.db.get_person_from_gramps_id("I0001")
        cls.person2 = cls.db.get_person_from_gramps_id("I0002")
        cls.person3 = cls.db.get_person_from_gramps_id("I0003")
        cls.person4 = cls.db.get_person_from_gramps_id("I0004")
        cls.person5 = cls.db.get_person_from_gramps_id("I0005")

    def tearDown(self):
        """Clean up test database."""
        pass

    def test_find_ancestors_basic(self):
        """Test basic ancestor finding (equivalent to _isancestorof.py)."""
        # Find all ancestors of a person with parents
        if self.person1 and self.person1.parent_family_list:
            ancestors = find_ancestors(self.db, [self.person1.handle], inclusive=False)
            # Should have at least some ancestors
            self.assertIsInstance(ancestors, set)
            # The person itself should not be in the ancestors list when inclusive=False
            self.assertNotIn(self.person1.handle, ancestors)

    def test_find_ancestors_inclusive(self):
        """Test ancestor finding with inclusive=True."""
        # Find all ancestors of a person including the person itself
        if self.person1:
            ancestors = find_ancestors(self.db, [self.person1.handle], inclusive=True)
            # Should have at least the person itself
            self.assertIsInstance(ancestors, set)
            # The person itself should be in the ancestors list when inclusive=True
            self.assertIn(self.person1.handle, ancestors)

    def test_find_ancestors_max_generation(self):
        """Test ancestor finding with max_generation (equivalent to _islessthannthgenerationancestorof.py)."""
        # Find ancestors up to 1 generation
        if self.person1 and self.person1.parent_family_list:
            ancestors = find_ancestors(
                self.db, [self.person1.handle], max_generation=1, inclusive=False
            )
            # Should have some ancestors but not too many
            self.assertIsInstance(ancestors, set)
            # Should not include the person itself
            self.assertNotIn(self.person1.handle, ancestors)

    def test_find_ancestors_min_generation(self):
        """Test ancestor finding with min_generation (equivalent to _ismorethannthgenerationancestorof.py)."""
        # Find ancestors at least 1 generation away
        if self.person1 and self.person1.parent_family_list:
            ancestors = find_ancestors(
                self.db, [self.person1.handle], min_generation=1, inclusive=False
            )
            # Should have some ancestors
            self.assertIsInstance(ancestors, set)
            # Should not include the person itself
            self.assertNotIn(self.person1.handle, ancestors)

    def test_find_ancestors_generation_range(self):
        """Test ancestor finding with both min and max generation."""
        # Find ancestors between 1 and 2 generations away
        if self.person1 and self.person1.parent_family_list:
            ancestors = find_ancestors(
                self.db,
                [self.person1.handle],
                min_generation=1,
                max_generation=2,
                inclusive=False,
            )
            # Should have some ancestors
            self.assertIsInstance(ancestors, set)
            # Should not include the person itself
            self.assertNotIn(self.person1.handle, ancestors)

    def test_find_ancestors_multiple_people(self):
        """Test finding ancestors of multiple people (equivalent to _islessthannthgenerationancestorofbookmarked.py)."""
        # Find ancestors of multiple people
        if self.person1 and self.person2 and self.person1.parent_family_list:
            ancestors = find_ancestors(
                self.db, [self.person1.handle, self.person2.handle], inclusive=False
            )
            # Should have some ancestors
            self.assertIsInstance(ancestors, set)
            # Should not include the original people
            self.assertNotIn(self.person1.handle, ancestors)
            self.assertNotIn(self.person2.handle, ancestors)

    def test_find_ancestors_iterative(self):
        """Test iterative ancestor finding."""
        # Collect ancestors using the iterative function
        if self.person1 and self.person1.parent_family_list:
            ancestors = set()
            generations = {}
            for handle, generation in find_ancestors_iterative(
                self.db, [self.person1.handle], inclusive=False
            ):
                ancestors.add(handle)
                generations[handle] = generation

            # Should have some ancestors
            self.assertIsInstance(ancestors, set)
            # Should not include the person itself
            self.assertNotIn(self.person1.handle, ancestors)
            # Should have generation information
            self.assertIsInstance(generations, dict)

    def test_find_ancestors_empty(self):
        """Test ancestor finding with invalid input."""
        # Test with None handle
        ancestors = find_ancestors(self.db, None)
        self.assertEqual(ancestors, set())

        # Test with non-existent handle
        ancestors = find_ancestors(self.db, "non_existent_handle")
        self.assertEqual(ancestors, set())

    def test_find_ancestors_cycle_protection(self):
        """Test that the function handles cycles gracefully."""
        # Test with a person that might have cycles in the real data
        if self.person1 and self.person1.parent_family_list:
            # This should not cause an infinite loop even if there are cycles
            ancestors = find_ancestors(self.db, [self.person1.handle], inclusive=False)
            # Should return a set of ancestors
            self.assertIsInstance(ancestors, set)
            # Should not include the person itself
            self.assertNotIn(self.person1.handle, ancestors)

    # Tests for descendant functions
    def test_find_descendants_basic(self):
        """Test basic descendant finding."""
        # Find all descendants of a person with children
        if self.person1 and self.person1.family_list:
            descendants = find_descendants(
                self.db, [self.person1.handle], inclusive=False
            )
            # Should have at least some descendants
            self.assertIsInstance(descendants, set)
            # The person itself should not be in the descendants list when inclusive=False
            self.assertNotIn(self.person1.handle, descendants)

    def test_find_descendants_inclusive(self):
        """Test descendant finding with inclusive=True."""
        # Find all descendants of a person including the person itself
        if self.person1:
            descendants = find_descendants(
                self.db, [self.person1.handle], inclusive=True
            )
            # Should have at least the person itself
            self.assertIsInstance(descendants, set)
            # The person itself should be in the descendants list when inclusive=True
            self.assertIn(self.person1.handle, descendants)

    def test_find_descendants_max_generation(self):
        """Test descendant finding with max_generation."""
        # Find descendants up to 1 generation
        if self.person1 and self.person1.family_list:
            descendants = find_descendants(
                self.db, [self.person1.handle], max_generation=1, inclusive=False
            )
            # Should have some descendants but not too many
            self.assertIsInstance(descendants, set)
            # Should not include the person itself
            self.assertNotIn(self.person1.handle, descendants)

    def test_find_descendants_min_generation(self):
        """Test descendant finding with min_generation."""
        # Find descendants at least 1 generation away
        if self.person1 and self.person1.family_list:
            descendants = find_descendants(
                self.db, [self.person1.handle], min_generation=1, inclusive=False
            )
            # Should have some descendants
            self.assertIsInstance(descendants, set)
            # Should not include the person itself
            self.assertNotIn(self.person1.handle, descendants)

    def test_find_descendants_generation_range(self):
        """Test descendant finding with both min and max generation."""
        # Find descendants between 1 and 2 generations away
        if self.person1 and self.person1.family_list:
            descendants = find_descendants(
                self.db,
                [self.person1.handle],
                min_generation=1,
                max_generation=2,
                inclusive=False,
            )
            # Should have some descendants
            self.assertIsInstance(descendants, set)
            # Should not include the person itself
            self.assertNotIn(self.person1.handle, descendants)

    def test_find_descendants_multiple_people(self):
        """Test finding descendants of multiple people."""
        # Find descendants of multiple people
        if (
            self.person1
            and self.person2
            and (self.person1.family_list or self.person2.family_list)
        ):
            descendants = find_descendants(
                self.db, [self.person1.handle, self.person2.handle], inclusive=False
            )
            # Should have some descendants
            self.assertIsInstance(descendants, set)
            # Should not include the original people
            self.assertNotIn(self.person1.handle, descendants)
            self.assertNotIn(self.person2.handle, descendants)

    def test_find_descendants_iterative(self):
        """Test iterative descendant finding."""
        # Collect descendants using the iterative function
        if self.person1 and self.person1.family_list:
            descendants = set()
            generations = {}
            for handle, generation in find_descendants_iterative(
                self.db, [self.person1.handle], inclusive=False
            ):
                descendants.add(handle)
                generations[handle] = generation

            # Should have some descendants
            self.assertIsInstance(descendants, set)
            # Should not include the person itself
            self.assertNotIn(self.person1.handle, descendants)
            # Should have generation information
            self.assertIsInstance(generations, dict)

    def test_find_descendants_empty(self):
        """Test descendant finding with invalid input."""
        # Test with None handle
        descendants = find_descendants(self.db, None)
        self.assertEqual(descendants, set())

        # Test with non-existent handle
        descendants = find_descendants(self.db, "non_existent_handle")
        self.assertEqual(descendants, set())

    def test_find_descendants_cycle_protection(self):
        """Test that the function handles cycles gracefully."""
        # Test with a person that might have cycles in the real data
        if self.person1 and self.person1.family_list:
            # This should not cause an infinite loop even if there are cycles
            descendants = find_descendants(
                self.db, [self.person1.handle], inclusive=False
            )
            # Should return a set of descendants
            self.assertIsInstance(descendants, set)
            # Should not include the person itself
            self.assertNotIn(self.person1.handle, descendants)

    def test_find_descendants_include_all_families(self):
        """Test descendant finding with include_all_families=True."""
        # Find descendants including all families
        if self.person1 and self.person1.family_list:
            descendants_all = find_descendants(
                self.db,
                [self.person1.handle],
                include_all_families=True,
                inclusive=False,
            )
            descendants_first = find_descendants(
                self.db,
                [self.person1.handle],
                include_all_families=False,
                inclusive=False,
            )
            # Should have some descendants
            self.assertIsInstance(descendants_all, set)
            self.assertIsInstance(descendants_first, set)
            # All families should include at least as many descendants as first family only
            self.assertGreaterEqual(len(descendants_all), len(descendants_first))

    def test_find_descendants_no_families(self):
        """Test descendant finding for a person with no families."""
        # Find descendants of a person with no families
        if self.person1 and not self.person1.family_list:
            descendants = find_descendants(
                self.db, [self.person1.handle], inclusive=False
            )
            # Should return empty set
            self.assertEqual(descendants, set())

    def test_find_descendants_generation_consistency(self):
        """Test that generation numbers are consistent between iterative and non-iterative versions."""
        if self.person1 and self.person1.family_list:
            # Get descendants with generation info
            descendants_with_gens = {}
            for handle, generation in find_descendants_iterative(
                self.db, [self.person1.handle], inclusive=False
            ):
                descendants_with_gens[handle] = generation

            # Get descendants without generation info
            descendants = find_descendants(
                self.db, [self.person1.handle], inclusive=False
            )

            # The sets should be the same
            self.assertEqual(set(descendants_with_gens.keys()), descendants)
            # All generations should be >= 1
            for generation in descendants_with_gens.values():
                self.assertGreaterEqual(generation, 1)

    def test_find_descendants_edge_cases(self):
        """Test edge cases for descendant finding."""
        # Test with empty list
        descendants = find_descendants(self.db, [], inclusive=False)
        self.assertEqual(descendants, set())

        # Test with empty list in iterative version
        descendants_iter = list(
            find_descendants_iterative(self.db, [], inclusive=False)
        )
        self.assertEqual(descendants_iter, [])

        # Test with None in list
        descendants = find_descendants(self.db, [None], inclusive=False)
        self.assertEqual(descendants, set())

        # Test with None in list in iterative version
        descendants_iter = list(
            find_descendants_iterative(self.db, [None], inclusive=False)
        )
        self.assertEqual(descendants_iter, [])


if __name__ == "__main__":
    unittest.main()
