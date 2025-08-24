#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025 Doug Blank <doug.blank@gmail.com>
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
Tests for family tree traversal utilities.

This module tests both sequential and parallel implementations to ensure
they produce the same results.
"""

import unittest
import tempfile
import os
from typing import Set

from gramps.gen.db import DbTxn
from gramps.gen.dbstate import DbState
from gramps.cli.clidbman import CLIDbManager
from gramps.gen.db.utils import make_database
from gramps.gen.lib import Person, Family, ChildRef, Name, Surname
from gramps.gen.utils.family_tree_traversal import (
    FamilyTreeTraversal,
    get_person_ancestors,
    get_person_descendants,
    is_ancestor_of,
    get_family_ancestors,
)


class TestFamilyTreeTraversal(unittest.TestCase):
    """Test cases for family tree traversal utilities."""

    def setUp(self):
        """Set up test database and create a simple family tree."""
        # Create a temporary database
        self.temp_dir = tempfile.mkdtemp()

        # Initialize database using proper Gramps methods
        self.dbstate = DbState()
        self.dbman = CLIDbManager(self.dbstate)
        self.db_path, _name = self.dbman.create_new_db_cli(
            "Test Family Tree", dbid="sqlite"
        )
        self.db = make_database("sqlite")
        self.db.load(self.db_path, None)

        # Create test family tree
        self._create_test_family_tree()

    def tearDown(self):
        """Clean up test database."""
        if hasattr(self, "db"):
            self.db.close()
        if hasattr(self, "dbman"):
            self.dbman.remove_database("Test Family Tree")
        if hasattr(self, "temp_dir") and os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    def _create_test_family_tree(self):
        """Create a simple test family tree for testing."""
        with DbTxn("Create test family tree", self.db) as trans:
            # Create persons
            # Generation 0 (root)
            self.person_0 = Person()
            self.person_0.set_gramps_id("I0001")
            name_0 = Name()
            surname_0 = Surname()
            surname_0.set_surname("Root")
            name_0.add_surname(surname_0)
            name_0.set_primary_surname(0)
            self.person_0.set_primary_name(name_0)
            self.db.add_person(self.person_0, trans)

            # Generation 1 (children of person_0)
            self.person_1a = Person()
            self.person_1a.set_gramps_id("I0002")
            name_1a = Name()
            surname_1a = Surname()
            surname_1a.set_surname("Child1")
            name_1a.add_surname(surname_1a)
            name_1a.set_primary_surname(0)
            self.person_1a.set_primary_name(name_1a)
            self.db.add_person(self.person_1a, trans)

            self.person_1b = Person()
            self.person_1b.set_gramps_id("I0003")
            name_1b = Name()
            surname_1b = Surname()
            surname_1b.set_surname("Child2")
            name_1b.add_surname(surname_1b)
            name_1b.set_primary_surname(0)
            self.person_1b.set_primary_name(name_1b)
            self.db.add_person(self.person_1b, trans)

            # Generation 2 (children of person_1a)
            self.person_2a = Person()
            self.person_2a.set_gramps_id("I0004")
            name_2a = Name()
            surname_2a = Surname()
            surname_2a.set_surname("Grandchild1")
            name_2a.add_surname(surname_2a)
            name_2a.set_primary_surname(0)
            self.person_2a.set_primary_name(name_2a)
            self.db.add_person(self.person_2a, trans)

            self.person_2b = Person()
            self.person_2b.set_gramps_id("I0005")
            name_2b = Name()
            surname_2b = Surname()
            surname_2b.set_surname("Grandchild2")
            name_2b.add_surname(surname_2b)
            name_2b.set_primary_surname(0)
            self.person_2b.set_primary_name(name_2b)
            self.db.add_person(self.person_2b, trans)

            # Generation 3 (children of person_2a)
            self.person_3a = Person()
            self.person_3a.set_gramps_id("I0006")
            name_3a = Name()
            surname_3a = Surname()
            surname_3a.set_surname("GreatGrandchild1")
            name_3a.add_surname(surname_3a)
            name_3a.set_primary_surname(0)
            self.person_3a.set_primary_name(name_3a)
            self.db.add_person(self.person_3a, trans)

            # Create families
            # Family 1: person_0 + person_1a, person_1b
            self.family_1 = Family()
            self.family_1.set_gramps_id("F0001")
            self.family_1.set_father_handle(self.person_0.handle)
            child_ref_1a = ChildRef()
            child_ref_1a.ref = self.person_1a.handle
            self.family_1.add_child_ref(child_ref_1a)
            child_ref_1b = ChildRef()
            child_ref_1b.ref = self.person_1b.handle
            self.family_1.add_child_ref(child_ref_1b)
            self.db.add_family(self.family_1, trans)

            # Family 2: person_1a + person_2a, person_2b
            self.family_2 = Family()
            self.family_2.set_gramps_id("F0002")
            self.family_2.set_father_handle(self.person_1a.handle)
            child_ref_2a = ChildRef()
            child_ref_2a.ref = self.person_2a.handle
            self.family_2.add_child_ref(child_ref_2a)
            child_ref_2b = ChildRef()
            child_ref_2b.ref = self.person_2b.handle
            self.family_2.add_child_ref(child_ref_2b)
            self.db.add_family(self.family_2, trans)

            # Family 3: person_2a + person_3a
            self.family_3 = Family()
            self.family_3.set_gramps_id("F0003")
            self.family_3.set_father_handle(self.person_2a.handle)
            child_ref_3a = ChildRef()
            child_ref_3a.ref = self.person_3a.handle
            self.family_3.add_child_ref(child_ref_3a)
            self.db.add_family(self.family_3, trans)

            # Update person references
            self.person_0.add_family_handle(self.family_1.handle)
            self.person_1a.add_parent_family_handle(self.family_1.handle)
            self.person_1a.add_family_handle(self.family_2.handle)
            self.person_1b.add_parent_family_handle(self.family_1.handle)
            self.person_2a.add_parent_family_handle(self.family_2.handle)
            self.person_2a.add_family_handle(self.family_3.handle)
            self.person_2b.add_parent_family_handle(self.family_2.handle)
            self.person_3a.add_parent_family_handle(self.family_3.handle)

            # Commit changes
            self.db.commit_person(self.person_0, trans)
            self.db.commit_person(self.person_1a, trans)
            self.db.commit_person(self.person_1b, trans)
            self.db.commit_person(self.person_2a, trans)
            self.db.commit_person(self.person_2b, trans)
            self.db.commit_person(self.person_3a, trans)

    def _compare_results(
        self, sequential_result: Set[str], parallel_result: Set[str], test_name: str
    ):
        """Compare sequential and parallel results and assert they are equal."""
        self.assertEqual(
            sequential_result,
            parallel_result,
            f"{test_name}: Sequential and parallel results differ\n"
            f"Sequential: {sorted(sequential_result)}\n"
            f"Parallel: {sorted(parallel_result)}",
        )

    def test_get_person_ancestors_sequential_vs_parallel(self):
        """Test that sequential and parallel ancestor traversal produce the same results."""
        # Test with different root persons and depths
        test_cases = [
            (self.person_3a, None, False),  # All ancestors of great-grandchild
            (self.person_2a, None, False),  # All ancestors of grandchild
            (self.person_1a, None, False),  # All ancestors of child
            (self.person_0, None, False),  # All ancestors of root (should be empty)
            (self.person_3a, 1, False),  # Ancestors up to depth 1
            (self.person_3a, 2, False),  # Ancestors up to depth 2
            (self.person_2a, 1, False),  # Ancestors up to depth 1
            (self.person_3a, None, True),  # All ancestors including root
            (self.person_2a, None, True),  # All ancestors including root
        ]

        for root_person, max_depth, include_root in test_cases:
            # Sequential version
            sequential_traversal = FamilyTreeTraversal(
                use_parallel=False, max_threads=None
            )
            sequential_result = sequential_traversal.get_person_ancestors(
                self.db, [root_person], max_depth=max_depth, include_root=include_root
            )

            # Parallel version (now enabled with thread safety fixes)
            parallel_traversal = FamilyTreeTraversal(use_parallel=True, max_threads=2)
            parallel_result = parallel_traversal.get_person_ancestors(
                self.db, [root_person], max_depth=max_depth, include_root=include_root
            )

            test_name = f"Ancestors of {root_person.gramps_id} (depth={max_depth}, include_root={include_root})"
            self._compare_results(sequential_result, parallel_result, test_name)

    def test_get_person_descendants_sequential_vs_parallel(self):
        """Test that sequential and parallel descendant traversal produce the same results."""
        # Test with different root persons and depths
        test_cases = [
            (self.person_0, None, False),  # All descendants of root
            (self.person_1a, None, False),  # All descendants of child
            (self.person_2a, None, False),  # All descendants of grandchild
            (
                self.person_3a,
                None,
                False,
            ),  # All descendants of great-grandchild (should be empty)
            (self.person_0, 1, False),  # Descendants up to depth 1
            (self.person_0, 2, False),  # Descendants up to depth 2
            (self.person_1a, 1, False),  # Descendants up to depth 1
            (self.person_0, None, True),  # All descendants including root
            (self.person_1a, None, True),  # All descendants including root
        ]

        for root_person, max_depth, include_root in test_cases:
            # Sequential version
            sequential_traversal = FamilyTreeTraversal(
                use_parallel=False, max_threads=None
            )
            sequential_result = sequential_traversal.get_person_descendants(
                self.db, [root_person], max_depth=max_depth, include_root=include_root
            )

            # Parallel version (now enabled with thread safety fixes)
            parallel_traversal = FamilyTreeTraversal(use_parallel=True, max_threads=2)
            parallel_result = parallel_traversal.get_person_descendants(
                self.db, [root_person], max_depth=max_depth, include_root=include_root
            )

            test_name = f"Descendants of {root_person.gramps_id} (depth={max_depth}, include_root={include_root})"
            self._compare_results(sequential_result, parallel_result, test_name)

    def test_is_ancestor_of_sequential_vs_parallel(self):
        """Test that sequential and parallel ancestor checking produce the same results."""
        # Test various ancestor-descendant relationships
        test_cases = [
            (self.person_0, self.person_1a, None),  # Root is ancestor of child
            (self.person_0, self.person_2a, None),  # Root is ancestor of grandchild
            (
                self.person_0,
                self.person_3a,
                None,
            ),  # Root is ancestor of great-grandchild
            (self.person_1a, self.person_2a, None),  # Child is ancestor of grandchild
            (
                self.person_1a,
                self.person_3a,
                None,
            ),  # Child is ancestor of great-grandchild
            (
                self.person_2a,
                self.person_3a,
                None,
            ),  # Grandchild is ancestor of great-grandchild
            (self.person_1a, self.person_0, None),  # Child is NOT ancestor of root
            (self.person_2a, self.person_0, None),  # Grandchild is NOT ancestor of root
            (
                self.person_3a,
                self.person_0,
                None,
            ),  # Great-grandchild is NOT ancestor of root
            (self.person_0, self.person_0, None),  # Person is NOT ancestor of self
            (
                self.person_0,
                self.person_2a,
                1,
            ),  # Root is ancestor of grandchild within depth 1
            (
                self.person_0,
                self.person_3a,
                1,
            ),  # Root is NOT ancestor of great-grandchild within depth 1
        ]

        for potential_ancestor, potential_descendant, max_depth in test_cases:
            # Sequential version
            sequential_traversal = FamilyTreeTraversal(
                use_parallel=False, max_threads=None
            )
            sequential_result = sequential_traversal.is_ancestor_of(
                self.db, potential_ancestor, potential_descendant, max_depth=max_depth
            )

            # Parallel version (now enabled with thread safety fixes)
            parallel_traversal = FamilyTreeTraversal(use_parallel=True, max_threads=2)
            parallel_result = parallel_traversal.is_ancestor_of(
                self.db, potential_ancestor, potential_descendant, max_depth=max_depth
            )

            test_name = f"Is {potential_ancestor.gramps_id} ancestor of {potential_descendant.gramps_id} (depth={max_depth})"
            self.assertEqual(
                sequential_result,
                parallel_result,
                f"{test_name}: Sequential and parallel results differ\n"
                f"Sequential: {sequential_result}\n"
                f"Parallel: {parallel_result}",
            )

    def test_convenience_functions_sequential_vs_parallel(self):
        """Test that convenience functions work with both sequential and parallel processing."""
        # Test get_person_ancestors convenience function
        sequential_ancestors = get_person_ancestors(
            self.db, [self.person_3a], use_parallel=False, max_threads=None
        )
        parallel_ancestors = get_person_ancestors(
            self.db, [self.person_3a], use_parallel=True, max_threads=2
        )
        self._compare_results(
            sequential_ancestors,
            parallel_ancestors,
            "get_person_ancestors convenience function",
        )

        # Test get_person_descendants convenience function
        sequential_descendants = get_person_descendants(
            self.db, [self.person_0], use_parallel=False, max_threads=None
        )
        parallel_descendants = get_person_descendants(
            self.db, [self.person_0], use_parallel=True, max_threads=2
        )
        self._compare_results(
            sequential_descendants,
            parallel_descendants,
            "get_person_descendants convenience function",
        )

        # Test is_ancestor_of convenience function
        sequential_is_ancestor = is_ancestor_of(
            self.db, self.person_0, self.person_3a, use_parallel=False, max_threads=None
        )
        parallel_is_ancestor = is_ancestor_of(
            self.db, self.person_0, self.person_3a, use_parallel=True, max_threads=2
        )
        self.assertEqual(
            sequential_is_ancestor,
            parallel_is_ancestor,
            "is_ancestor_of convenience function: Sequential and parallel results differ",
        )

    def test_empty_inputs(self):
        """Test that empty inputs are handled correctly."""
        traversal = FamilyTreeTraversal(use_parallel=True, max_threads=2)

        # Test empty person list
        empty_ancestors = traversal.get_person_ancestors(self.db, [])
        self.assertEqual(empty_ancestors, set())

        empty_descendants = traversal.get_person_descendants(self.db, [])
        self.assertEqual(empty_descendants, set())

    def test_single_person_no_relations(self):
        """Test traversal with a person who has no family relations."""
        # Create a person with no family relations
        with DbTxn("Create isolated person", self.db) as trans:
            isolated_person = Person()
            isolated_person.set_gramps_id("I0007")
            name_isolated = Name()
            surname_isolated = Surname()
            surname_isolated.set_surname("Isolated")
            name_isolated.add_surname(surname_isolated)
            name_isolated.set_primary_surname(0)
            isolated_person.set_primary_name(name_isolated)
            self.db.add_person(isolated_person, trans)

        traversal = FamilyTreeTraversal(use_parallel=True, max_threads=2)

        # Test ancestors
        ancestors = traversal.get_person_ancestors(self.db, [isolated_person])
        self.assertEqual(ancestors, set())

        # Test descendants
        descendants = traversal.get_person_descendants(self.db, [isolated_person])
        self.assertEqual(descendants, set())

    def test_depth_limiting(self):
        """Test that depth limiting works correctly."""
        traversal = FamilyTreeTraversal(use_parallel=True, max_threads=2)

        # Test ancestor depth limiting
        ancestors_depth_1 = traversal.get_person_ancestors(
            self.db, [self.person_3a], max_depth=1
        )
        ancestors_depth_2 = traversal.get_person_ancestors(
            self.db, [self.person_3a], max_depth=2
        )
        ancestors_unlimited = traversal.get_person_ancestors(
            self.db, [self.person_3a], max_depth=None
        )

        # Depth 1 should be subset of depth 2, which should be subset of unlimited
        self.assertTrue(ancestors_depth_1.issubset(ancestors_depth_2))
        self.assertTrue(ancestors_depth_2.issubset(ancestors_unlimited))

        # Test descendant depth limiting
        descendants_depth_1 = traversal.get_person_descendants(
            self.db, [self.person_0], max_depth=1
        )
        descendants_depth_2 = traversal.get_person_descendants(
            self.db, [self.person_0], max_depth=2
        )
        descendants_unlimited = traversal.get_person_descendants(
            self.db, [self.person_0], max_depth=None
        )

        # Depth 1 should be subset of depth 2, which should be subset of unlimited
        self.assertTrue(descendants_depth_1.issubset(descendants_depth_2))
        self.assertTrue(descendants_depth_2.issubset(descendants_unlimited))

    def test_get_family_ancestors(self):
        """Test family ancestor traversal functionality."""
        # Test with parallel processing (now enabled with thread safety fixes)
        traversal_parallel = FamilyTreeTraversal(use_parallel=True, max_threads=2)

        # Test with sequential processing
        traversal_sequential = FamilyTreeTraversal(use_parallel=False, max_threads=None)

        # Test with the family containing person_3a (should find ancestors)
        family_3a = self.db.get_family_from_handle(
            self.person_3a.get_main_parents_family_handle()
        )

        # Get ancestor families using parallel processing
        ancestor_families_parallel = traversal_parallel.get_family_ancestors(
            self.db, [family_3a], max_depth=None, include_root=False
        )

        # Get ancestor families using sequential processing
        ancestor_families_sequential = traversal_sequential.get_family_ancestors(
            self.db, [family_3a], max_depth=None, include_root=False
        )

        # Both should produce the same results
        self.assertEqual(ancestor_families_parallel, ancestor_families_sequential)

        # Should find ancestor families (families where the parents of person_3a are children)
        self.assertIsInstance(ancestor_families_parallel, set)
        self.assertGreater(len(ancestor_families_parallel), 0)

        # Test with include_root=True
        ancestor_families_with_root_parallel = traversal_parallel.get_family_ancestors(
            self.db, [family_3a], max_depth=None, include_root=True
        )

        ancestor_families_with_root_sequential = (
            traversal_sequential.get_family_ancestors(
                self.db, [family_3a], max_depth=None, include_root=True
            )
        )

        # Both should produce the same results
        self.assertEqual(
            ancestor_families_with_root_parallel, ancestor_families_with_root_sequential
        )

        # Should include the root family
        self.assertIsInstance(ancestor_families_with_root_parallel, set)
        self.assertGreaterEqual(
            len(ancestor_families_with_root_parallel), len(ancestor_families_parallel)
        )

        # Test depth limiting
        ancestor_families_depth_1_parallel = traversal_parallel.get_family_ancestors(
            self.db, [family_3a], max_depth=1, include_root=False
        )

        ancestor_families_depth_1_sequential = (
            traversal_sequential.get_family_ancestors(
                self.db, [family_3a], max_depth=1, include_root=False
            )
        )

        # Both should produce the same results
        self.assertEqual(
            ancestor_families_depth_1_parallel, ancestor_families_depth_1_sequential
        )

        # Depth 1 should be subset of unlimited
        self.assertTrue(
            ancestor_families_depth_1_parallel.issubset(ancestor_families_parallel)
        )

        # Test convenience function
        convenience_ancestors = get_family_ancestors(
            self.db, [family_3a], use_parallel=True, max_threads=2
        )
        self.assertIsInstance(convenience_ancestors, set)

        # Test with empty input
        empty_ancestors_parallel = traversal_parallel.get_family_ancestors(self.db, [])
        empty_ancestors_sequential = traversal_sequential.get_family_ancestors(
            self.db, []
        )
        self.assertEqual(empty_ancestors_parallel, set())
        self.assertEqual(empty_ancestors_sequential, set())

    def test_database_parallel_support_detection(self):
        """Test that the system correctly detects database parallel support."""
        from gramps.gen.utils.family_tree_traversal import create_family_tree_traversal

        # Test with a database that supports parallel reads (our SQLite test database)
        if hasattr(self.db, "supports_parallel_reads"):
            supports_parallel = self.db.supports_parallel_reads()

            # Create traversal with database support detection
            traversal = create_family_tree_traversal(
                use_parallel=True, max_threads=2, db=self.db
            )

            # The traversal should respect the database's parallel support
            if supports_parallel:
                self.assertIsNotNone(traversal._parallel_processor)
            else:
                # If database doesn't support parallel reads, should fall back to sequential
                # The parallel processor should be None when database doesn't support it
                self.assertIsNone(traversal._parallel_processor)

        # Test convenience function with database detection
        ancestors = get_person_ancestors(
            self.db, [self.person_3a], use_parallel=True, max_threads=2
        )
        self.assertIsInstance(ancestors, set)

        # Should work regardless of parallel support
        descendants = get_person_descendants(
            self.db, [self.person_0], use_parallel=True, max_threads=2
        )
        self.assertIsInstance(descendants, set)


if __name__ == "__main__":
    unittest.main()
