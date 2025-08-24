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
Family tree traversal utilities for Gramps operations.

This module provides both sequential and parallel implementations for family tree
traversal operations, with automatic fallback to sequential processing when
parallel processing is not available or not beneficial.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
from collections import deque
from typing import Any, Callable, List, Optional, Set, Tuple, cast
import logging

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from ..lib import Person, Family
from ..types import PersonHandle, FamilyHandle
from .parallel import ParallelProcessor, process_in_parallel

_ = glocale.translation.gettext

# Set up logging
LOG = logging.getLogger(".family_tree_traversal")


class FamilyTreeTraversal:
    """
    Family tree traversal utilities with support for both sequential and parallel processing.

    This class provides methods for traversing family trees to find ancestors and descendants,
    with automatic fallback to sequential processing when parallel processing is not available.
    """

    def __init__(self, use_parallel: bool, max_threads: Optional[int] = None):
        """
        Initialize the family tree traversal utility.

        Args:
            use_parallel: Whether to attempt parallel processing
            max_threads: Maximum number of threads for parallel processing
        """
        if max_threads is None and use_parallel:
            raise ValueError("You must provide max_threads for parallel processing")

        self.max_threads = max_threads
        self.use_parallel = use_parallel
        self._parallel_processor = None

        # Initialize parallel processing if requested
        if use_parallel:
            self._parallel_processor = ParallelProcessor(max_threads=max_threads)

    def _check_parallel_support(self, db) -> bool:
        """
        Check if the database supports parallel processing.

        Args:
            db: Database instance

        Returns:
            True if parallel processing is supported
        """
        if not self.use_parallel or self._parallel_processor is None:
            return False

        # Check if the database supports parallel reads
        if hasattr(db, "supports_parallel_reads"):
            return db.supports_parallel_reads()

        # If the database doesn't have the method, assume it doesn't support parallel processing
        return False

    def get_person_ancestors(
        self,
        db,
        persons: List[Person],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get all ancestors of the given persons up to the specified depth.

        Args:
            db: Database instance
            persons: List of persons to find ancestors for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of ancestor handles
        """
        if not persons:
            return cast(Set[PersonHandle], set())

        # Check if parallel processing is available and database supports parallel reads
        if self._check_parallel_support(db):
            return self._get_person_ancestors_parallel(
                db, persons, max_depth, include_root
            )
        else:
            return self._get_person_ancestors_sequential(
                db, persons, max_depth, include_root
            )

    def get_person_ancestors_with_min_depth(
        self,
        db,
        persons: List[Person],
        min_depth: int,
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get all ancestors of the given persons at least min_depth generations away.

        Args:
            db: Database instance
            persons: List of persons to find ancestors for
            min_depth: Minimum depth to include in results
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of ancestor handles
        """
        if not persons:
            return cast(Set[PersonHandle], set())

        # Check if parallel processing is available and database supports parallel reads
        if self._check_parallel_support(db):
            return self._get_person_ancestors_with_min_depth_parallel(
                db, persons, min_depth, max_depth, include_root
            )
        else:
            return self._get_person_ancestors_with_min_depth_sequential(
                db, persons, min_depth, max_depth, include_root
            )

    def get_person_descendants(
        self,
        db,
        persons: List[Person],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get all descendants of the given persons up to the specified depth.

        Args:
            db: Database instance
            persons: List of persons to find descendants for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of descendant handles
        """
        if not persons:
            return cast(Set[PersonHandle], set())

        # Check if parallel processing is available and database supports parallel reads
        if self._check_parallel_support(db):
            return self._get_person_descendants_parallel(
                db, persons, max_depth, include_root
            )
        else:
            return self._get_person_descendants_sequential(
                db, persons, max_depth, include_root
            )

    def get_person_descendants_with_min_depth(
        self,
        db,
        persons: List[Person],
        min_depth: int,
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get all descendants of the given persons at least min_depth generations away.

        Args:
            db: Database instance
            persons: List of persons to find descendants for
            min_depth: Minimum depth to include in results
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of descendant handles
        """
        if not persons:
            return cast(Set[PersonHandle], set())

        # Check if parallel processing is available and database supports parallel reads
        if self._check_parallel_support(db):
            return self._get_person_descendants_with_min_depth_parallel(
                db, persons, min_depth, max_depth, include_root
            )
        else:
            return self._get_person_descendants_with_min_depth_sequential(
                db, persons, min_depth, max_depth, include_root
            )

    def is_ancestor_of(
        self,
        db,
        potential_ancestor: Person,
        potential_descendant: Person,
        max_depth: Optional[int] = None,
    ) -> bool:
        """
        Check if one person is an ancestor of another.

        Args:
            db: Database instance
            potential_ancestor: Person to check if they are an ancestor
            potential_descendant: Person to check if they are a descendant
            max_depth: Maximum depth to search (None for unlimited)

        Returns:
            True if potential_ancestor is an ancestor of potential_descendant
        """
        # Check if parallel processing is available and database supports parallel reads
        if self._check_parallel_support(db):
            return self._is_ancestor_of_parallel(
                db, potential_ancestor, potential_descendant, max_depth
            )
        else:
            return self._is_ancestor_of_sequential(
                db, potential_ancestor, potential_descendant, max_depth
            )

    def get_family_descendants(
        self,
        db,
        families: List[Family],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[FamilyHandle]:
        """
        Get all descendant families of the given families up to the specified depth.

        Args:
            db: Database instance
            families: List of families to find descendants for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root families in the result

        Returns:
            Set of descendant family handles
        """
        if not families:
            return cast(Set[FamilyHandle], set())

        # Check if parallel processing is available and database supports parallel reads
        if self._check_parallel_support(db):
            return self._get_family_descendants_parallel(
                db, families, max_depth, include_root
            )
        else:
            return self._get_family_descendants_sequential(
                db, families, max_depth, include_root
            )

    def get_family_ancestors(
        self,
        db,
        families: List[Family],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[FamilyHandle]:
        """
        Get all ancestor families of the given families up to the specified depth.

        Args:
            db: Database instance
            families: List of families to find ancestors for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root families in the result

        Returns:
            Set of ancestor family handles
        """
        if not families:
            return cast(Set[FamilyHandle], set())

        # Check if parallel processing is available and database supports parallel reads
        if self._check_parallel_support(db):
            return self._get_family_ancestors_parallel(
                db, families, max_depth, include_root
            )
        else:
            return self._get_family_ancestors_sequential(
                db, families, max_depth, include_root
            )

    def _get_family_children(self, db, family: Family) -> List[str]:
        """
        Get child handles for a family.

        Args:
            db: Database instance
            family: Family object

        Returns:
            List of child handles
        """
        if not family:
            return []

        child_handles = []
        for child_ref in family.child_ref_list:
            child_handles.append(child_ref.ref)

        return child_handles

    def _get_family_ancestors_sequential(
        self,
        db,
        families: List[Family],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[FamilyHandle]:
        """
        Get ancestor families using sequential processing.

        Args:
            db: Database instance
            families: List of families to find ancestors for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root families in the result

        Returns:
            Set of ancestor family handles
        """
        ancestor_families = set()
        visited_families = set()

        # Use BFS to traverse family ancestors
        work_queue: deque[Tuple[str, int]] = deque()
        for family in families:
            work_queue.append((family.handle, 0))  # (family_handle, depth)

        while work_queue:
            family_handle, depth = work_queue.popleft()

            if max_depth is not None and depth > max_depth:
                continue

            if not family_handle or family_handle in visited_families:
                continue

            visited_families.add(family_handle)

            # Add to results if not root (or if include_root is True and depth is 0)
            if depth > 0 or (include_root and depth == 0):
                ancestor_families.add(family_handle)

            # Get the family and find its parents
            family = db.get_family_from_handle(family_handle)
            if family:
                # For each parent in the family, get their main parents' family
                for parent_handle in [
                    family.get_father_handle(),
                    family.get_mother_handle(),
                ]:
                    if parent_handle:
                        parent = db.get_person_from_handle(parent_handle)
                        if parent:
                            # Get the parent's main parents' family (where they are a child)
                            parent_family_handle = (
                                parent.get_main_parents_family_handle()
                            )
                            if (
                                parent_family_handle
                                and parent_family_handle not in visited_families
                            ):
                                work_queue.append((parent_family_handle, depth + 1))

        return cast(Set[FamilyHandle], ancestor_families)

    def _get_family_ancestors_parallel(
        self,
        db,
        families: List[Family],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[FamilyHandle]:
        """
        Get ancestor families using parallel processing.

        Args:
            db: Database instance
            families: List of families to find ancestors for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root families in the result

        Returns:
            Set of ancestor family handles
        """
        if not families:
            return cast(Set[FamilyHandle], set())

        ancestor_families = set()
        visited_families = set()

        # Start with root families
        current_level = [(family.handle, 0) for family in families]  # (handle, depth)

        while current_level:
            # Process current level in parallel
            def process_family_level(
                family_batch: List[Tuple[str, int]], thread_db: Any
            ) -> Tuple[List[Tuple[str, int]], Set[str], Set[str]]:
                """Process a batch of families to find their parent families."""
                next_level = []
                local_visited = set()
                local_results = set()

                for family_handle, depth in family_batch:
                    if max_depth is not None and depth > max_depth:
                        continue

                    if not family_handle or family_handle in visited_families:
                        continue

                    local_visited.add(family_handle)

                    # Add to results if not root (or if include_root is True and depth is 0)
                    if depth > 0 or (include_root and depth == 0):
                        local_results.add(family_handle)

                    # Get the family and find its parents
                    family = thread_db.get_family_from_handle(family_handle)
                    if family:
                        # For each parent in the family, get their main parents' family
                        for parent_handle in [
                            family.get_father_handle(),
                            family.get_mother_handle(),
                        ]:
                            if parent_handle:
                                parent = thread_db.get_person_from_handle(parent_handle)
                                if parent:
                                    # Get the parent's main parents' family (where they are a child)
                                    parent_family_handle = (
                                        parent.get_main_parents_family_handle()
                                    )
                                    if (
                                        parent_family_handle
                                        and parent_family_handle not in visited_families
                                    ):
                                        next_level.append(
                                            (parent_family_handle, depth + 1)
                                        )

                return next_level, local_visited, local_results

            results = self._parallel_processor.process_items(
                current_level, process_family_level, db
            )
            # Flatten the results and update shared state
            current_level = []
            for next_level, local_visited, local_results in results:
                current_level.extend(next_level)
                visited_families.update(local_visited)
                ancestor_families.update(local_results)

        return cast(Set[FamilyHandle], ancestor_families)

    def _process_parent_families_parallel(
        self, db, parent_handles: List[str], visited_families: Set[str]
    ) -> List[str]:
        """
        Process parent handles to get their main parents' family handles using parallel processing.

        Args:
            db: Database instance
            parent_handles: List of parent handles to process
            visited_families: Set of already visited family handles

        Returns:
            List of parent family handles
        """
        # Get parents first
        parents = []
        for parent_handle in parent_handles:
            parent = db.get_person_from_handle(parent_handle)
            if parent:
                parents.append(parent)

        # Use parallel processing for extracting parent family handles
        def extract_parent_families(parent_batch: List[Person]) -> List[str]:
            """Extract parent family handles from a batch of parents."""
            parent_family_handles = []
            for parent in parent_batch:
                parent_family_handle = parent.get_main_parents_family_handle()
                if (
                    parent_family_handle
                    and parent_family_handle not in visited_families
                ):
                    parent_family_handles.append(parent_family_handle)
            return parent_family_handles

        return self._parallel_processor.process_items(parents, extract_parent_families)

    def _process_parent_families_sequential(
        self, db, parent_handles: List[str], visited_families: Set[str]
    ) -> List[str]:
        """
        Process parent handles to get their main parents' family handles using sequential processing.

        Args:
            db: Database instance
            parent_handles: List of parent handles to process
            visited_families: Set of already visited family handles

        Returns:
            List of parent family handles
        """
        parent_family_handles = []
        for parent_handle in parent_handles:
            parent = db.get_person_from_handle(parent_handle)
            if parent:
                parent_family_handle = parent.get_main_parents_family_handle()
                if (
                    parent_family_handle
                    and parent_family_handle not in visited_families
                ):
                    parent_family_handles.append(parent_family_handle)
        return parent_family_handles

    def _ancestor_traversal(
        self,
        db,
        root_items: List[Any],
        get_parents_func: Callable[[Any], List[str]],
        get_item_func: Callable[[str], Optional[Any]],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[str]:
        """
        Perform ancestor traversal starting from multiple root items.

        Args:
            db: Database instance
            root_items: List of root items to start traversal from
            get_parents_func: Function to get parents of an item
            get_item_func: Function to get item by handle
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root items in the result

        Returns:
            Set of ancestor handles
        """
        if not root_items:
            return set()

        ancestor_handles: Set[str] = set()
        visited: Set[str] = set()

        # Extract handles from root items
        root_handles = []
        for item in root_items:
            item_handle = getattr(item, "handle", None)
            if item_handle:
                root_handles.append(item_handle)

        if not root_handles:
            return set()

        # BFS traversal
        work_queue: deque[Tuple[str, int]] = deque()
        for handle in root_handles:
            work_queue.append((handle, 0))  # (handle, depth)

        while work_queue:
            handle, depth = work_queue.popleft()

            if max_depth is not None and depth > max_depth:
                continue

            if not handle or handle in visited:
                continue

            visited.add(handle)

            # Include in results based on depth and include_root flag during traversal
            if depth > 0 or (include_root and depth == 0):
                ancestor_handles.add(handle)

            # Get the item and its parents
            item = get_item_func(handle)
            if item:
                parent_handles = get_parents_func(item)
                if parent_handles:
                    for parent_handle in parent_handles:
                        if parent_handle not in visited:
                            work_queue.append((parent_handle, depth + 1))

        return ancestor_handles

    def _ancestor_traversal_with_min_depth(
        self,
        db,
        root_items: List[Any],
        get_parents_func: Callable[[Any], List[str]],
        get_item_func: Callable[[str], Optional[Any]],
        min_depth: int,
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[str]:
        """
        Perform ancestor traversal starting from multiple root items, filtering by minimum depth.

        Args:
            db: Database instance
            root_items: List of root items to start traversal from
            get_parents_func: Function to get parents of an item
            get_item_func: Function to get item by handle
            min_depth: Minimum depth to include in results
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root items in the result

        Returns:
            Set of ancestor handles
        """
        if not root_items:
            return set()

        ancestor_handles: Set[str] = set()
        visited: Set[str] = set()

        # Extract handles from root items
        root_handles = []
        for item in root_items:
            item_handle = getattr(item, "handle", None)
            if item_handle:
                root_handles.append(item_handle)

        if not root_handles:
            return set()

        # BFS traversal
        work_queue: deque[Tuple[str, int]] = deque()
        for handle in root_handles:
            work_queue.append((handle, 0))  # (handle, depth)

        while work_queue:
            handle, depth = work_queue.popleft()

            if max_depth is not None and depth > max_depth:
                continue

            if not handle or handle in visited:
                continue

            visited.add(handle)

            # Include in results based on depth and include_root flag during traversal
            if depth >= min_depth or (include_root and depth == 0):
                ancestor_handles.add(handle)

            # Get the item and its parents
            item = get_item_func(handle)
            if item:
                parent_handles = get_parents_func(item)
                if parent_handles:
                    for parent_handle in parent_handles:
                        if parent_handle not in visited:
                            work_queue.append((parent_handle, depth + 1))

        return ancestor_handles

    def _descendant_traversal(
        self,
        db,
        root_items: List[Any],
        get_children_func: Callable[[Any], List[str]],
        get_item_func: Callable[[str], Optional[Any]],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[str]:
        """
        Perform descendant traversal starting from multiple root items.

        Args:
            db: Database instance
            root_items: List of root items to start traversal from
            get_children_func: Function to get children of an item
            get_item_func: Function to get item by handle
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root items in the result

        Returns:
            Set of descendant handles
        """
        if not root_items:
            return set()

        descendant_handles: Set[str] = set()
        visited: Set[str] = set()

        # Extract handles from root items
        root_handles = []
        for item in root_items:
            item_handle = getattr(item, "handle", None)
            if item_handle:
                root_handles.append(item_handle)

        if not root_handles:
            return set()

        # BFS traversal
        work_queue: deque[Tuple[str, int]] = deque()
        for handle in root_handles:
            work_queue.append((handle, 0))  # (handle, depth)

        while work_queue:
            handle, depth = work_queue.popleft()

            if max_depth is not None and depth > max_depth:
                continue

            if not handle or handle in visited:
                continue

            visited.add(handle)

            # Include in results based on depth and include_root flag during traversal
            if depth > 0 or (include_root and depth == 0):
                descendant_handles.add(handle)

            # Get the item and its children
            item = get_item_func(handle)
            if item:
                child_handles = get_children_func(item)
                if child_handles:
                    for child_handle in child_handles:
                        if child_handle not in visited:
                            work_queue.append((child_handle, depth + 1))

        return descendant_handles

    def _descendant_traversal_with_min_depth(
        self,
        db,
        root_items: List[Any],
        get_children_func: Callable[[Any], List[str]],
        get_item_func: Callable[[str], Optional[Any]],
        min_depth: int,
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[str]:
        """
        Perform descendant traversal starting from multiple root items, filtering by minimum depth.

        Args:
            db: Database instance
            root_items: List of root items to start traversal from
            get_children_func: Function to get children of an item
            get_item_func: Function to get item by handle
            min_depth: Minimum depth to include in results
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root items in the result

        Returns:
            Set of descendant handles
        """
        if not root_items:
            return set()

        descendant_handles: Set[str] = set()
        visited: Set[str] = set()

        # Extract handles from root items
        root_handles = []
        for item in root_items:
            item_handle = getattr(item, "handle", None)
            if item_handle:
                root_handles.append(item_handle)

        if not root_handles:
            return set()

        # BFS traversal
        work_queue: deque[Tuple[str, int]] = deque()
        for handle in root_handles:
            work_queue.append((handle, 0))  # (handle, depth)

        while work_queue:
            handle, depth = work_queue.popleft()

            if max_depth is not None and depth > max_depth:
                continue

            if not handle or handle in visited:
                continue

            visited.add(handle)

            # Include in results based on depth and include_root flag during traversal
            if depth >= min_depth or (include_root and depth == 0):
                descendant_handles.add(handle)

            # Get the item and its children
            item = get_item_func(handle)
            if item:
                child_handles = get_children_func(item)
                if child_handles:
                    for child_handle in child_handles:
                        if child_handle not in visited:
                            work_queue.append((child_handle, depth + 1))

        return descendant_handles

    def _get_person_ancestors_with_min_depth_sequential(
        self,
        db,
        persons: List[Person],
        min_depth: int,
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get ancestors with minimum depth using sequential processing.

        Args:
            db: Database instance
            persons: List of persons to find ancestors for
            min_depth: Minimum depth to include in results
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of ancestor handles
        """

        def get_parents_func(person: Person) -> List[str]:
            return self._get_person_parents(db, person)

        def get_item_func(handle: str) -> Optional[Person]:
            return db.get_person_from_handle(handle)

        return cast(
            Set[PersonHandle],
            self._ancestor_traversal_with_min_depth(
                db=db,
                root_items=persons,
                get_parents_func=get_parents_func,
                get_item_func=get_item_func,
                min_depth=min_depth,
                max_depth=max_depth,
                include_root=include_root,
            ),
        )

    def _get_person_ancestors_with_min_depth_parallel(
        self,
        db,
        persons: List[Person],
        min_depth: int,
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get ancestors with minimum depth using parallel processing.

        Args:
            db: Database instance
            persons: List of persons to find ancestors for
            min_depth: Minimum depth to include in results
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of ancestor handles
        """
        if not persons:
            return cast(Set[PersonHandle], set())

        ancestor_handles = set()
        visited = set()

        # Start with root persons
        current_level = [(person.handle, 0) for person in persons]  # (handle, depth)

        while current_level:
            # Process current level in parallel
            def process_person_level(
                person_batch: List[Tuple[str, int]], thread_db: Any
            ) -> Tuple[List[Tuple[str, int]], Set[str], Set[str]]:
                """Process a batch of persons to find their ancestors."""
                next_level = []
                local_visited = set()
                local_results = set()

                for person_handle, depth in person_batch:
                    if max_depth is not None and depth > max_depth:
                        continue

                    if not person_handle or person_handle in visited:
                        continue

                    local_visited.add(person_handle)

                    # Include in results based on depth and include_root flag
                    if depth >= min_depth or (include_root and depth == 0):
                        local_results.add(person_handle)

                    # Get the person and their parents using thread-safe database
                    # thread_db is already a thread-safe database wrapper
                    # Get raw person data using thread-safe database
                    raw_person_data = thread_db.get_raw_person_data(person_handle)
                    if raw_person_data:
                        # Extract parent family list from raw data
                        parent_family_list = raw_person_data.get(
                            "parent_family_list", []
                        )
                        for family_handle in parent_family_list:
                            # Get raw family data
                            raw_family_data = thread_db.get_raw_family_data(
                                family_handle
                            )
                            if raw_family_data:
                                # Extract parent handles from raw data
                                father_handle = raw_family_data.get("father_handle")
                                mother_handle = raw_family_data.get("mother_handle")
                                for parent_handle in [
                                    father_handle,
                                    mother_handle,
                                ]:
                                    if parent_handle and parent_handle not in visited:
                                        next_level.append((parent_handle, depth + 1))

                return next_level, local_visited, local_results

            results = self._parallel_processor.process_items(
                current_level, process_person_level, db
            )
            # Flatten the results and update shared state
            current_level = []
            for next_level, local_visited, local_results in results:
                current_level.extend(next_level)
                visited.update(local_visited)
                ancestor_handles.update(local_results)

        return cast(Set[PersonHandle], ancestor_handles)

    def _get_person_descendants_with_min_depth_sequential(
        self,
        db,
        persons: List[Person],
        min_depth: int,
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get descendants with minimum depth using sequential processing.

        Args:
            db: Database instance
            persons: List of persons to find descendants for
            min_depth: Minimum depth to include in results
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of descendant handles
        """

        def get_children_func(person: Person) -> List[str]:
            return self._get_person_children(db, person)

        def get_item_func(handle: str) -> Optional[Person]:
            return db.get_person_from_handle(handle)

        return cast(
            Set[PersonHandle],
            self._descendant_traversal_with_min_depth(
                db=db,
                root_items=persons,
                get_children_func=get_children_func,
                get_item_func=get_item_func,
                min_depth=min_depth,
                max_depth=max_depth,
                include_root=include_root,
            ),
        )

    def _get_person_descendants_with_min_depth_parallel(
        self,
        db,
        persons: List[Person],
        min_depth: int,
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get descendants with minimum depth using parallel processing.

        Args:
            db: Database instance
            persons: List of persons to find descendants for
            min_depth: Minimum depth to include in results
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of descendant handles
        """
        if not persons:
            return cast(Set[PersonHandle], set())

        descendant_handles = set()
        visited = set()

        # Start with root persons
        current_level = [(person.handle, 0) for person in persons]  # (handle, depth)

        while current_level:
            # Process current level in parallel
            def process_person_level(
                person_batch: List[Tuple[str, int]], thread_db: Any
            ) -> Tuple[List[Tuple[str, int]], Set[str], Set[str]]:
                """Process a batch of persons to find their descendants."""
                print(
                    f"DEBUG: process_person_level called with {len(person_batch)} persons"
                )
                next_level = []
                local_visited = set()
                local_results = set()

                for person_handle, depth in person_batch:
                    if max_depth is not None and depth > max_depth:
                        continue

                    if not person_handle or person_handle in visited:
                        continue

                    local_visited.add(person_handle)

                    # Include in results based on depth and include_root flag
                    if depth > 0 or (include_root and depth == 0):
                        local_results.add(person_handle)

                    # Get the person and their children using thread-safe database
                    try:
                        print(f"DEBUG: Processing person {person_handle} in parallel")
                        # thread_db is already a thread-safe database wrapper
                        if thread_db and hasattr(thread_db, "get_raw_person_data"):
                            print(f"DEBUG: thread_db supports get_raw_person_data")
                            # Get raw person data using thread-safe database
                            raw_person_data = thread_db.get_raw_person_data(
                                person_handle
                            )
                            if raw_person_data:
                                print(f"DEBUG: Got raw person data for {person_handle}")
                                # Extract family list from raw data
                                family_list = raw_person_data.get("family_list", [])
                                print(
                                    f"DEBUG: Person {person_handle} has {len(family_list)} families: {family_list}"
                                )
                                for family_handle in family_list:
                                    # Get raw family data
                                    raw_family_data = thread_db.get_raw_family_data(
                                        family_handle
                                    )
                                    if raw_family_data:
                                        # Extract child references from raw data
                                        child_ref_list = raw_family_data.get(
                                            "child_ref_list", []
                                        )
                                        print(
                                            f"DEBUG: Family {family_handle} has {len(child_ref_list)} children: {child_ref_list}"
                                        )
                                        for child_ref in child_ref_list:
                                            child_handle = child_ref.get("ref")
                                            if (
                                                child_handle
                                                and child_handle not in visited
                                            ):
                                                next_level.append(
                                                    (child_handle, depth + 1)
                                                )
                                                print(
                                                    f"DEBUG: Added child {child_handle} to next_level at depth {depth + 1}"
                                                )
                                            else:
                                                print(
                                                    f"DEBUG: Skipping child {child_handle} - already visited or invalid"
                                                )
                                    else:
                                        print(
                                            f"DEBUG: Could not get raw family data for {family_handle}"
                                        )
                            else:
                                print(
                                    f"DEBUG: Could not get raw person data for {person_handle}"
                                )
                        else:
                            # Fallback: don't process this person in parallel to avoid thread safety issues
                            print(
                                f"DEBUG: thread_db does not support get_raw_person_data"
                            )
                            pass
                    except Exception as e:
                        print(
                            f"DEBUG: Error processing person {person_handle} in parallel: {e}"
                        )
                        LOG.error(
                            f"Error processing person {person_handle} in parallel: {e}"
                        )
                        # Fallback: don't process this person in parallel to avoid thread safety issues
                        pass

                return next_level, local_visited, local_results

            results = self._parallel_processor.process_items(
                current_level, process_person_level, db
            )
            # Flatten the results and update shared state
            current_level = []
            for next_level, local_visited, local_results in results:
                current_level.extend(next_level)
                visited.update(local_visited)
                descendant_handles.update(local_results)

        return cast(Set[PersonHandle], descendant_handles)

    def _get_person_parents(self, db, person: Person) -> List[str]:
        """
        Get parent handles for a person by traversing their families.

        Args:
            db: Database instance
            person: Person object

        Returns:
            List of parent handles
        """
        parent_handles = []

        # Get families where this person is a child
        for family_handle in person.parent_family_list:
            family = db.get_family_from_handle(family_handle)
            if family:
                # Add father and mother handles
                if family.father_handle:
                    parent_handles.append(family.father_handle)
                if family.mother_handle:
                    parent_handles.append(family.mother_handle)

        return parent_handles

    def _get_person_children(self, db, person: Person) -> List[str]:
        """
        Get child handles for a person by traversing their families.

        Args:
            db: Database instance
            person: Person object

        Returns:
            List of child handles
        """
        if not person:
            return []

        # Get family handles for this person
        family_handles = list(person.family_list)

        # Get child handles from all families
        if family_handles:
            # Check if parallel processing is available and database supports parallel reads
            if self._check_parallel_support(db):
                return self._process_person_families_parallel(db, family_handles)
            else:
                return self._process_person_families_sequential(db, family_handles)

        return []

    def _process_person_families_sequential(
        self, db, family_handles: List[str]
    ) -> List[str]:
        """
        Process person families to get child handles using sequential processing.

        Args:
            db: Database instance
            family_handles: List of family handles to process

        Returns:
            List of child handles
        """
        child_handles = []
        for family_handle in family_handles:
            family = db.get_family_from_handle(family_handle)
            if family:
                for child_ref in family.child_ref_list:
                    child_handles.append(child_ref.ref)
        return child_handles

    def _process_person_families_parallel(
        self, db, family_handles: List[str]
    ) -> List[str]:
        """
        Process person families to get child handles using parallel processing.

        Args:
            db: Database instance
            family_handles: List of family handles to process

        Returns:
            List of child handles
        """
        # Get families first
        families = []
        for family_handle in family_handles:
            family = db.get_family_from_handle(family_handle)
            if family:
                families.append(family)

        # Use parallel processing for extracting child handles from families
        def extract_children(family_batch: List[Family]) -> List[str]:
            """Extract child handles from a batch of families."""
            child_handles = []
            for family in family_batch:
                for child_ref in family.child_ref_list:
                    child_handles.append(child_ref.ref)
            return child_handles

        if self._check_parallel_support(db):
            return self._parallel_processor.process_items(families, extract_children)
        else:
            # Fallback to sequential processing if parallel processor is not available
            return self._process_person_families_sequential(db, family_handles)

    def _get_person_ancestors_sequential(
        self,
        db,
        persons: List[Person],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get ancestors using sequential processing.

        Args:
            db: Database instance
            persons: List of persons to find ancestors for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of ancestor handles
        """

        def get_parents_func(person: Person) -> List[str]:
            return self._get_person_parents(db, person)

        def get_item_func(handle: str) -> Optional[Person]:
            return db.get_person_from_handle(handle)

        return cast(
            Set[PersonHandle],
            self._ancestor_traversal(
                db=db,
                root_items=persons,
                get_parents_func=get_parents_func,
                get_item_func=get_item_func,
                max_depth=max_depth,
                include_root=include_root,
            ),
        )

    def _get_person_ancestors_parallel(
        self,
        db,
        persons: List[Person],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get ancestors using parallel processing.

        Args:
            db: Database instance
            persons: List of persons to find ancestors for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of ancestor handles
        """
        if not persons:
            return cast(Set[PersonHandle], set())

        ancestor_handles = set()
        visited = set()

        # Start with root persons
        current_level = [(person.handle, 0) for person in persons]  # (handle, depth)

        while current_level:
            # Process current level in parallel
            def process_person_level(
                person_batch: List[Tuple[str, int]], thread_db: Any
            ) -> Tuple[List[Tuple[str, int]], Set[str], Set[str]]:
                """Process a batch of persons to find their ancestors."""
                next_level = []
                local_visited = set()
                local_results = set()

                for person_handle, depth in person_batch:
                    if max_depth is not None and depth > max_depth:
                        continue

                    if not person_handle or person_handle in visited:
                        continue

                    local_visited.add(person_handle)

                    # Include in results based on depth and include_root flag
                    if depth > 0 or (include_root and depth == 0):
                        local_results.add(person_handle)

                    # Get the person and their parents using thread-safe database
                    # thread_db is already a thread-safe database wrapper
                    # Get raw person data using thread-safe database
                    raw_person_data = thread_db.get_raw_person_data(person_handle)
                    if raw_person_data:
                        # Extract parent family list from raw data
                        parent_family_list = raw_person_data.get(
                            "parent_family_list", []
                        )
                        for family_handle in parent_family_list:
                            # Get raw family data
                            raw_family_data = thread_db.get_raw_family_data(
                                family_handle
                            )
                            if raw_family_data:
                                # Extract parent handles from raw data
                                father_handle = raw_family_data.get("father_handle")
                                mother_handle = raw_family_data.get("mother_handle")
                                for parent_handle in [
                                    father_handle,
                                    mother_handle,
                                ]:
                                    if parent_handle and parent_handle not in visited:
                                        next_level.append((parent_handle, depth + 1))

                return next_level, local_visited, local_results

            if self._check_parallel_support(db):
                results = self._parallel_processor.process_items(
                    current_level, process_person_level, db
                )
                # Flatten the results and update shared state
                current_level = []
                for next_level, local_visited, local_results in results:
                    current_level.extend(next_level)
                    visited.update(local_visited)
                    ancestor_handles.update(local_results)
            else:
                # Fallback to sequential processing
                next_level, local_visited, local_results = process_person_level(
                    current_level, db
                )
                current_level = next_level
                visited.update(local_visited)
                ancestor_handles.update(local_results)

        return cast(Set[PersonHandle], ancestor_handles)

    def _get_person_descendants_sequential(
        self,
        db,
        persons: List[Person],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get descendants using sequential processing.

        Args:
            db: Database instance
            persons: List of persons to find descendants for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of descendant handles
        """

        def get_children_func(person: Person) -> List[str]:
            return self._get_person_children(db, person)

        def get_item_func(handle: str) -> Optional[Person]:
            return db.get_person_from_handle(handle)

        return cast(
            Set[PersonHandle],
            self._descendant_traversal(
                db=db,
                root_items=persons,
                get_children_func=get_children_func,
                get_item_func=get_item_func,
                max_depth=max_depth,
                include_root=include_root,
            ),
        )

    def _get_person_descendants_parallel(
        self,
        db,
        persons: List[Person],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[PersonHandle]:
        """
        Get descendants using parallel processing.

        Args:
            db: Database instance
            persons: List of persons to find descendants for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of descendant handles
        """
        if not persons:
            return cast(Set[PersonHandle], set())

        descendant_handles = set()
        visited = set()

        # Start with root persons
        current_level = [(person.handle, 0) for person in persons]  # (handle, depth)

        while current_level:
            # Process current level in parallel
            def process_person_level(
                person_batch: List[Tuple[str, int]], thread_db: Any
            ) -> Tuple[List[Tuple[str, int]], Set[str], Set[str]]:
                """Process a batch of persons to find their descendants."""
                import threading

                current_thread = threading.current_thread()
                print(
                    f"DEBUG: process_person_level called with {len(person_batch)} persons, thread_db type: {type(thread_db)}, in thread: {current_thread.name}"
                )
                next_level = []
                local_visited = set()
                local_results = set()

                for person_handle, depth in person_batch:
                    if max_depth is not None and depth > max_depth:
                        continue

                    if not person_handle or person_handle in visited:
                        continue

                    local_visited.add(person_handle)

                    # Include in results based on depth and include_root flag
                    if depth > 0 or (include_root and depth == 0):
                        local_results.add(person_handle)

                        # Get the person and their children using thread-safe database
                    try:
                        # thread_db is already a thread-safe database wrapper
                        if thread_db and hasattr(thread_db, "get_raw_person_data"):
                            # Get raw person data using thread-safe database
                            raw_person_data = thread_db.get_raw_person_data(
                                person_handle
                            )
                            if raw_person_data:
                                # Extract family list from raw data
                                family_list = raw_person_data.get("family_list", [])
                                for family_handle in family_list:
                                    # Get raw family data
                                    raw_family_data = thread_db.get_raw_family_data(
                                        family_handle
                                    )
                                    if raw_family_data:
                                        # Extract child references from raw data
                                        child_ref_list = raw_family_data.get(
                                            "child_ref_list", []
                                        )
                                        for child_ref in child_ref_list:
                                            child_handle = child_ref.get("ref")
                                            if (
                                                child_handle
                                                and child_handle not in local_visited
                                            ):
                                                next_level.append(
                                                    (child_handle, depth + 1)
                                                )
                        else:
                            # Fallback: don't process this person in parallel to avoid thread safety issues
                            pass
                    except Exception as e:
                        LOG.error(
                            f"Error processing person {person_handle} in parallel: {e}"
                        )
                        # If there's an error, we have to skip this person
                        pass

                return next_level, local_visited, local_results

            results = self._parallel_processor.process_items(
                current_level, process_person_level, db
            )
            # Flatten the results and update shared state
            current_level = []
            for next_level, local_visited, local_results in results:
                current_level.extend(next_level)
                visited.update(local_visited)
                descendant_handles.update(local_results)

        return cast(Set[PersonHandle], descendant_handles)

    def _is_ancestor_of_sequential(
        self,
        db,
        potential_ancestor: Person,
        potential_descendant: Person,
        max_depth: Optional[int] = None,
    ) -> bool:
        """
        Check if one person is an ancestor of another using sequential processing.

        Args:
            db: Database instance
            potential_ancestor: Person to check if they are an ancestor
            potential_descendant: Person to check if they are a descendant
            max_depth: Maximum depth to search (None for unlimited)

        Returns:
            True if potential_ancestor is an ancestor of potential_descendant
        """
        # Get all ancestors of the potential descendant
        ancestors = self.get_person_ancestors(
            db=db,
            persons=[potential_descendant],
            max_depth=max_depth,
        )

        # Check if the potential ancestor is in the ancestor set
        return potential_ancestor.handle in ancestors

    def _is_ancestor_of_parallel(
        self,
        db,
        potential_ancestor: Person,
        potential_descendant: Person,
        max_depth: Optional[int] = None,
    ) -> bool:
        """
        Check if one person is an ancestor of another using parallel processing.

        Args:
            db: Database instance
            potential_ancestor: Person to check if they are an ancestor
            potential_descendant: Person to check if they are a descendant
            max_depth: Maximum depth to search (None for unlimited)

        Returns:
            True if potential_ancestor is an ancestor of potential_descendant
        """
        # Get all ancestors of the potential descendant
        ancestors = self.get_person_ancestors(
            db=db,
            persons=[potential_descendant],
            max_depth=max_depth,
        )

        # Check if the potential ancestor is in the ancestor set
        return potential_ancestor.handle in ancestors

    def _get_family_descendants_sequential(
        self,
        db,
        families: List[Family],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[FamilyHandle]:
        """
        Get descendant families using sequential processing.

        Args:
            db: Database instance
            families: List of families to find descendants for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root families in the result

        Returns:
            Set of descendant family handles
        """
        descendant_families = set()
        visited_families = set()

        # Use BFS to traverse family descendants
        work_queue: deque[Tuple[str, int]] = deque()
        for family in families:
            work_queue.append((family.handle, 0))  # (family_handle, depth)

        while work_queue:
            family_handle, depth = work_queue.popleft()

            if max_depth is not None and depth > max_depth:
                continue

            if not family_handle or family_handle in visited_families:
                continue

            visited_families.add(family_handle)

            # Add to results if not root (or if include_root is True and depth is 0)
            if depth > 0 or (include_root and depth == 0):
                descendant_families.add(family_handle)

            # Get the family and find its children
            family = db.get_family_from_handle(family_handle)
            if family:
                # Get all children in this family
                for child_ref in family.child_ref_list:
                    child_handle = child_ref.ref
                    if child_handle:
                        child = db.get_person_from_handle(child_handle)
                        if child:
                            # Find families where this child is a parent
                            for child_family_handle in child.family_list:
                                if child_family_handle not in visited_families:
                                    work_queue.append((child_family_handle, depth + 1))

        return cast(Set[FamilyHandle], descendant_families)

    def _get_family_descendants_parallel(
        self,
        db,
        families: List[Family],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[FamilyHandle]:
        """
        Get descendant families using parallel processing.

        Args:
            db: Database instance
            families: List of families to find descendants for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root families in the result

        Returns:
            Set of descendant family handles
        """
        if not families:
            return cast(Set[FamilyHandle], set())

        descendant_families = set()
        visited_families = set()

        # Start with root families
        current_level = [(family.handle, 0) for family in families]  # (handle, depth)

        while current_level:
            # Process current level in parallel
            def process_family_level(
                family_batch: List[Tuple[str, int]], thread_db: Any
            ) -> Tuple[List[Tuple[str, int]], Set[str], Set[str]]:
                """Process a batch of families to find their descendant families."""
                next_level = []
                local_visited = set()
                local_results = set()

                for family_handle, depth in family_batch:
                    if max_depth is not None and depth > max_depth:
                        continue

                    if not family_handle or family_handle in visited_families:
                        continue

                    local_visited.add(family_handle)

                    # Add to results if not root (or if include_root is True and depth is 0)
                    if depth > 0 or (include_root and depth == 0):
                        local_results.add(family_handle)

                    # Get the family and find its children
                    family = thread_db.get_family_from_handle(family_handle)
                    if family:
                        # Get all children in this family
                        for child_ref in family.child_ref_list:
                            child_handle = child_ref.ref
                            if child_handle:
                                child = thread_db.get_person_from_handle(child_handle)
                                if child:
                                    # Find families where this child is a parent
                                    for child_family_handle in child.family_list:
                                        if child_family_handle not in visited_families:
                                            next_level.append(
                                                (child_family_handle, depth + 1)
                                            )

                return next_level, local_visited, local_results

            results = self._parallel_processor.process_items(
                current_level, process_family_level, db
            )
            # Flatten the results and update shared state
            current_level = []
            for next_level, local_visited, local_results in results:
                current_level.extend(next_level)
                visited_families.update(local_visited)
                descendant_families.update(local_results)

        return cast(Set[FamilyHandle], descendant_families)


# Convenience functions
def create_family_tree_traversal(
    use_parallel: bool,
    max_threads: int,
    db=None,
) -> FamilyTreeTraversal:
    """
    Create a FamilyTreeTraversal instance with sensible defaults.

    Args:
        use_parallel: Whether to attempt parallel processing
        max_threads: Maximum number of threads for parallel processing
        db: Database instance (optional, used for parallel support detection)

    Returns:
        Configured FamilyTreeTraversal instance
    """
    # Check if database supports parallel reads
    if db and hasattr(db, "supports_parallel_reads"):
        if not db.supports_parallel_reads():
            use_parallel = False

    return FamilyTreeTraversal(
        use_parallel=use_parallel,
        max_threads=max_threads,
    )


def get_person_ancestors(
    db,
    persons: List[Person],
    use_parallel: bool,
    max_threads: int,
    max_depth: Optional[int] = None,
    include_root: bool = False,
) -> Set[PersonHandle]:
    """
    Convenience function to get all ancestors of the given persons.

    Args:
        db: Database instance
        persons: List of persons to find ancestors for
        max_depth: Maximum depth to traverse (None for unlimited)
        include_root: Whether to include root persons in the result
        use_parallel: Whether to attempt parallel processing
        max_threads: Maximum number of threads for parallel processing

    Returns:
        Set of ancestor handles
    """
    traversal = FamilyTreeTraversal(
        use_parallel=use_parallel,
        max_threads=max_threads,
    )
    return traversal.get_person_ancestors(
        db=db,
        persons=persons,
        max_depth=max_depth,
        include_root=include_root,
    )


def get_person_ancestors_with_min_depth(
    db,
    persons: List[Person],
    min_depth: int,
    use_parallel: bool,
    max_threads: int,
    max_depth: Optional[int] = None,
    include_root: bool = False,
) -> Set[PersonHandle]:
    """
    Convenience function to get all ancestors of the given persons at least min_depth generations away.

    Args:
        db: Database instance
        persons: List of persons to find ancestors for
        min_depth: Minimum depth to include in results
        max_depth: Maximum depth to traverse (None for unlimited)
        include_root: Whether to include root persons in the result
        use_parallel: Whether to attempt parallel processing
        max_threads: Maximum number of threads for parallel processing

    Returns:
        Set of ancestor handles
    """
    traversal = FamilyTreeTraversal(
        use_parallel=use_parallel,
        max_threads=max_threads,
    )
    return traversal.get_person_ancestors_with_min_depth(
        db=db,
        persons=persons,
        min_depth=min_depth,
        max_depth=max_depth,
        include_root=include_root,
    )


def get_person_descendants(
    db,
    persons: List[Person],
    use_parallel: bool,
    max_threads: int,
    max_depth: Optional[int] = None,
    include_root: bool = False,
) -> Set[PersonHandle]:
    """
    Convenience function to get all descendants of the given persons.

    Args:
        db: Database instance
        persons: List of persons to find descendants for
        max_depth: Maximum depth to traverse (None for unlimited)
        include_root: Whether to include root persons in the result
        use_parallel: Whether to attempt parallel processing
        max_threads: Maximum number of threads for parallel processing

    Returns:
        Set of descendant handles
    """
    traversal = FamilyTreeTraversal(
        use_parallel=use_parallel,
        max_threads=max_threads,
    )
    return traversal.get_person_descendants(
        db=db,
        persons=persons,
        max_depth=max_depth,
        include_root=include_root,
    )


def get_person_descendants_with_min_depth(
    db,
    persons: List[Person],
    min_depth: int,
    use_parallel: bool,
    max_threads: int,
    max_depth: Optional[int] = None,
    include_root: bool = False,
) -> Set[PersonHandle]:
    """
    Convenience function to get all descendants of the given persons at least min_depth generations away.

    Args:
        db: Database instance
        persons: List of persons to find descendants for
        min_depth: Minimum depth to include in results
        max_depth: Maximum depth to traverse (None for unlimited)
        include_root: Whether to include root persons in the result
        use_parallel: Whether to attempt parallel processing
        max_threads: Maximum number of threads for parallel processing

    Returns:
        Set of descendant handles
    """
    traversal = FamilyTreeTraversal(
        use_parallel=use_parallel,
        max_threads=max_threads,
    )
    return traversal.get_person_descendants_with_min_depth(
        db=db,
        persons=persons,
        min_depth=min_depth,
        max_depth=max_depth,
        include_root=include_root,
    )


def is_ancestor_of(
    db,
    potential_ancestor: Person,
    potential_descendant: Person,
    use_parallel: bool,
    max_threads: int,
    max_depth: Optional[int] = None,
) -> bool:
    """
    Convenience function to check if one person is an ancestor of another.

    Args:
        db: Database instance
        potential_ancestor: Person to check if they are an ancestor
        potential_descendant: Person to check if they are a descendant
        max_depth: Maximum depth to search (None for unlimited)
        use_parallel: Whether to attempt parallel processing
        max_threads: Maximum number of threads for parallel processing

    Returns:
        True if potential_ancestor is an ancestor of potential_descendant
    """
    traversal = FamilyTreeTraversal(
        use_parallel=use_parallel,
        max_threads=max_threads,
    )
    return traversal.is_ancestor_of(
        db=db,
        potential_ancestor=potential_ancestor,
        potential_descendant=potential_descendant,
        max_depth=max_depth,
    )


def get_family_ancestors(
    db,
    families: List[Family],
    use_parallel: bool,
    max_threads: int,
    max_depth: Optional[int] = None,
    include_root: bool = False,
) -> Set[FamilyHandle]:
    """
    Convenience function to get all ancestor families of the given families.

    Args:
        db: Database instance
        families: List of families to find ancestors for
        max_depth: Maximum depth to traverse (None for unlimited)
        include_root: Whether to include root families in the result
        use_parallel: Whether to attempt parallel processing
        max_threads: Maximum number of threads for parallel processing

    Returns:
        Set of ancestor family handles
    """
    traversal = FamilyTreeTraversal(
        use_parallel=use_parallel,
        max_threads=max_threads,
    )
    return traversal.get_family_ancestors(
        db=db,
        families=families,
        max_depth=max_depth,
        include_root=include_root,
    )


def get_family_descendants(
    db,
    families: List[Family],
    use_parallel: bool,
    max_threads: int,
    max_depth: Optional[int] = None,
    include_root: bool = False,
) -> Set[FamilyHandle]:
    """
    Convenience function to get all descendant families of the given families.

    Args:
        db: Database instance
        families: List of families to find descendants for
        max_depth: Maximum depth to traverse (None for unlimited)
        include_root: Whether to include root families in the result
        use_parallel: Whether to attempt parallel processing
        max_threads: Maximum number of threads for parallel processing

    Returns:
        Set of descendant family handles
    """
    traversal = FamilyTreeTraversal(
        use_parallel=use_parallel,
        max_threads=max_threads,
    )
    return traversal.get_family_descendants(
        db=db,
        families=families,
        max_depth=max_depth,
        include_root=include_root,
    )
