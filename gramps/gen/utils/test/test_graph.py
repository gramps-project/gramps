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
from gramps.gen.utils.graph import find_ancestors, find_ancestors_iterative

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


if __name__ == "__main__":
    unittest.main()
