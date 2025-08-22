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
Parallel processing utilities for Gramps operations.

This module provides reusable parallel processing infrastructure for operations
that can benefit from concurrent execution, such as family tree traversal,
data processing, and filtering operations.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import threading
from typing import Any, Callable, List, Optional, TypeVar, Generic, Set, Tuple
from collections.abc import Iterable
from collections import deque
import logging
import queue

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from ..lib import Person, Family
from ..types import PersonHandle


_ = glocale.translation.gettext

# Set up logging
LOG = logging.getLogger(".parallel")

# Type variables for generic typing
T = TypeVar("T")
R = TypeVar("R")


class ParallelProcessor(Generic[T, R]):
    """
    A configurable parallel processor for batch operations.

    This class provides a thread-safe way to process collections of items
    in parallel, with configurable thread counts.
    """

    def __init__(
        self,
        max_threads: int = 4,
        chunk_size: Optional[int] = None,
    ):
        """
        Initialize the parallel processor.

        Args:
            max_threads: Maximum number of threads to use (default: 4)
            chunk_size: Size of chunks to process per thread (default: auto-calculate)
        """
        self.max_threads = max(1, max_threads)
        self.chunk_size = chunk_size
        self._lock = threading.Lock()

    def process_items(
        self,
        items: List[T],
        processor_func: Callable[[List[T]], List[R]],
    ) -> List[R]:
        """
        Process a list of items using parallel processing.

        Args:
            items: List of items to process
            processor_func: Function to process a chunk of items
                          Should have signature: func(chunk: List[T]) -> List[R]

        Returns:
            List of results
        """
        # Calculate optimal chunk size
        if self.chunk_size is None:
            chunk_size = max(1, len(items) // self.max_threads)
        else:
            chunk_size = self.chunk_size

        # Split items into chunks
        chunks: List[List[T]] = [
            items[i : i + chunk_size] for i in range(0, len(items), chunk_size)
        ]

        LOG.debug(
            f"Using parallel processing: {len(items)} items in {len(chunks)} chunks"
        )

        # Process chunks in parallel
        threads: List[threading.Thread] = []
        results_queue: queue.Queue[List[R]] = queue.Queue()

        def worker(chunk: List[T]):
            """Worker function for processing chunks."""
            try:
                chunk_results = processor_func(chunk)
                results_queue.put(chunk_results)
            except Exception as e:
                LOG.error(f"Error in parallel processing: {e}")
                results_queue.put([])

        for chunk in chunks:
            thread = threading.Thread(target=worker, args=(chunk,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Combine results
        all_results: List[R] = []
        while not results_queue.empty():
            chunk_results = results_queue.get()
            all_results.extend(chunk_results)

        return all_results


class FamilyTreeProcessor:
    """
    Specialized parallel processor for family tree operations.

    This class provides optimized parallel processing for common family tree
    operations like descendant traversal, with thread safety.
    """

    def __init__(
        self,
        max_threads: int = 4,
    ):
        """
        Initialize the family tree processor.

        Args:
            max_threads: Maximum number of threads to use
        """
        self.processor: ParallelProcessor = ParallelProcessor(max_threads=max_threads)
        self._lock = threading.Lock()

    def process_person_families(
        self,
        db,
        family_handles: List[str],
    ) -> List[str]:
        """
        Process person families to get child handles with optimized batching.
        Uses parallel database access when supported, otherwise sequential.

        Args:
            db: Database instance
            family_handles: List of family handles to process

        Returns:
            List of child handles
        """
        if not family_handles:
            return []

        # Create database wrapper for thread-local connections
        db_wrapper = db.create_thread_safe_wrapper()
        if db_wrapper is None:
            # Fall back to sequential processing if no thread-safe wrapper available
            families = []
            for family_handle in family_handles:
                family = db.get_family_from_handle(family_handle)
                if family:
                    families.append(family)

            # Parallel processing for extracting child handles from families
            def extract_children(family_batch: List[Family]) -> List[str]:
                """Extract child handles from a batch of families."""
                child_handles = []
                for family in family_batch:
                    for child_ref in family.child_ref_list:
                        child_handles.append(child_ref.ref)
                return child_handles

            # Use parallel processing for the data extraction
            return self.processor.process_items(families, extract_children)

        # Check if database supports parallel reads
        if db_wrapper.supports_parallel_reads():
            # Use parallel processing with connection swapping
            def parallel_family_processor(chunk: List[str]) -> List[str]:
                """Process a chunk of family handles using thread-local connections."""
                child_handles = []

                # Use context manager to swap connection for this thread
                with db_wrapper as thread_safe_db:
                    for family_handle in chunk:
                        # Now all database methods use thread-local connection automatically!
                        raw_family = thread_safe_db.get_raw_family_data(family_handle)
                        if raw_family and "child_ref_list" in raw_family:
                            for child_ref in raw_family["child_ref_list"]:
                                if "ref" in child_ref:
                                    child_handles.append(child_ref["ref"])

                return child_handles

            return self.processor.process_items(
                family_handles, parallel_family_processor
            )
        else:
            # Fall back to sequential processing with batching
            families = []
            for family_handle in family_handles:
                family = db.get_family_from_handle(family_handle)
                if family:
                    families.append(family)

            # Parallel processing for extracting child handles from families
            def extract_children(family_batch: List[Family]) -> List[str]:
                """Extract child handles from a batch of families."""
                child_handles = []
                for family in family_batch:
                    for child_ref in family.child_ref_list:
                        child_handles.append(child_ref.ref)
                return child_handles

            # Use parallel processing for the data extraction
            return self.processor.process_items(families, extract_children)

    def process_child_families(self, db, child_handles: List[str]) -> List[str]:
        """
        Process children to get their family handles with optimized batching.
        Uses parallel database access when supported, otherwise sequential.

        Args:
            db: Database instance
            child_handles: List of child handles to process

        Returns:
            List of family handles
        """
        if not child_handles:
            return []

        # Create database wrapper for thread-local connections
        db_wrapper = db.create_thread_safe_wrapper()
        if db_wrapper is None:
            # Fall back to sequential processing if no thread-safe wrapper available
            persons = []
            for child_handle in child_handles:
                person = db.get_person_from_handle(child_handle)
                if person:
                    persons.append(person)

            # Parallel processing for extracting family handles from persons
            def extract_families(person_batch: List[Person]) -> List[str]:
                """Extract family handles from a batch of persons."""
                family_handles = []
                for person in person_batch:
                    for family_handle in person.family_list:
                        family_handles.append(family_handle)
                return family_handles

            # Use parallel processing for the data extraction
            return self.processor.process_items(persons, extract_families)

        # Check if database supports parallel reads
        if db_wrapper.supports_parallel_reads():
            # Use parallel processing with connection swapping
            def parallel_person_processor(chunk: List[str]) -> List[str]:
                """Process a chunk of person handles using thread-local connections."""
                family_handles = []

                # Use context manager to swap connection for this thread
                with db_wrapper as thread_safe_db:
                    for person_handle in chunk:
                        # Now all database methods use thread-local connection automatically!
                        raw_person = thread_safe_db.get_raw_person_data(person_handle)
                        if raw_person and "family_list" in raw_person:
                            for family_handle in raw_person["family_list"]:
                                family_handles.append(family_handle)

                return family_handles

            return self.processor.process_items(
                child_handles, parallel_person_processor
            )
        else:
            # Fall back to sequential processing with batching
            persons = []
            for child_handle in child_handles:
                person = db.get_person_from_handle(child_handle)
                if person:
                    persons.append(person)

            # Parallel processing for extracting family handles from persons
            def extract_families(person_batch: List[Person]) -> List[str]:
                """Extract family handles from a batch of persons."""
                family_handles = []
                for person in person_batch:
                    for family_handle in person.family_list:
                        family_handles.append(family_handle)
                return family_handles

            # Use parallel processing for the data extraction
            return self.processor.process_items(persons, extract_families)

    def parallel_descendant_traversal(
        self,
        db,
        root_items: List[Any],
        get_children_func: Callable[[Any], List[str]],
        get_item_func: Callable[[str], Optional[Any]],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[str]:
        """
        Perform optimized descendant traversal starting from multiple root items.
        Uses sequential database access with parallel processing for data manipulation.

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

        # Simple BFS traversal without complex batching
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

            # Add to results if not root (or if include_root is True and depth is 0)
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

    def parallel_ancestor_traversal(
        self,
        db,
        root_items: List[Any],
        get_parents_func: Callable[[Any], List[str]],
        get_item_func: Callable[[str], Optional[Any]],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[str]:
        """
        Perform optimized ancestor traversal starting from multiple root items.
        Uses sequential database access with parallel processing for data manipulation.

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

        # Simple BFS traversal without complex batching
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

            # Add to results if not root (or if include_root is True and depth is 0)
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

    def get_person_parents(self, db, person: Person) -> List[str]:
        """
        Get parent handles for a person by traversing their families.
        Uses optimized database access.

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

    def get_person_ancestors(
        self,
        db,
        persons: List[Person],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[str]:
        """
        Get all ancestors of the given persons up to the specified depth.
        This is a convenience method that combines ancestor traversal with person-specific logic.

        Args:
            db: Database instance
            persons: List of persons to find ancestors for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of ancestor handles
        """

        def get_parents_func(person: Person) -> List[str]:
            return self.get_person_parents(db, person)

        def get_item_func(handle: str) -> Optional[Person]:
            return db.get_person_from_handle(handle)

        return self.parallel_ancestor_traversal(
            db=db,
            root_items=persons,
            get_parents_func=get_parents_func,
            get_item_func=get_item_func,
            max_depth=max_depth,
            include_root=include_root,
        )

    def get_person_descendants(
        self,
        db,
        persons: List[Person],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[str]:
        """
        Get all descendants of the given persons up to the specified depth.
        This is a convenience method that combines descendant traversal with person-specific logic.

        Args:
            db: Database instance
            persons: List of persons to find descendants for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root persons in the result

        Returns:
            Set of descendant handles
        """

        def get_children_func(person: Person) -> List[str]:
            return self.get_person_children(db, person)

        def get_item_func(handle: str) -> Optional[Person]:
            return db.get_person_from_handle(handle)

        return self.parallel_descendant_traversal(
            db=db,
            root_items=persons,
            get_children_func=get_children_func,
            get_item_func=get_item_func,
            max_depth=max_depth,
            include_root=include_root,
        )

    def get_family_descendants(
        self,
        db,
        families: List[Family],
        max_depth: Optional[int] = None,
        include_root: bool = False,
    ) -> Set[str]:
        """
        Get all descendant families of the given families up to the specified depth.
        This is a convenience method that combines descendant traversal with family-specific logic.

        Args:
            db: Database instance
            families: List of families to find descendants for
            max_depth: Maximum depth to traverse (None for unlimited)
            include_root: Whether to include root families in the result

        Returns:
            Set of descendant family handles
        """

        def get_children_func(family: Family) -> List[str]:
            return self.get_family_children(db, family)

        def get_item_func(handle: str) -> Optional[Family]:
            return db.get_family_from_handle(handle)

        return self.parallel_descendant_traversal(
            db=db,
            root_items=families,
            get_children_func=get_children_func,
            get_item_func=get_item_func,
            max_depth=max_depth,
            include_root=include_root,
        )

    def get_family_children(self, db, family: Family) -> List[str]:
        """
        Get child family handles for a family by traversing their children's families.
        Uses optimized database access.

        Args:
            db: Database instance
            family: Family object

        Returns:
            List of child family handles
        """
        if not family:
            return []

        # Get child handles from this family
        child_handles = [child_ref.ref for child_ref in family.child_ref_list]

        # Get family handles for all children in parallel
        if child_handles:
            return self.process_child_families(db, child_handles)

        return []

    def get_person_children(self, db, person: Person) -> List[str]:
        """
        Get child handles for a person by traversing their families.
        Uses optimized database access.

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

        # Get child handles from all families in parallel
        if family_handles:
            return self.process_person_families(db, family_handles)

        return []

    def is_ancestor_of(
        self,
        db,
        potential_ancestor: Person,
        potential_descendant: Person,
        max_depth: Optional[int] = None,
    ) -> bool:
        """
        Check if one person is an ancestor of another.
        Uses optimized ancestor traversal to determine the relationship.

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


# Convenience functions for common use cases
def create_family_tree_processor(
    max_threads: int = 4,
) -> FamilyTreeProcessor:
    """
    Create a FamilyTreeProcessor with sensible defaults.

    Args:
        max_threads: Maximum number of worker threads for parallel processing

    Returns:
        Configured FamilyTreeProcessor instance
    """
    return FamilyTreeProcessor(
        max_threads=max_threads,
    )


def process_in_parallel(
    items: List[T],
    processor_func: Callable[[List[T]], List[R]],
    max_threads: int = 4,
) -> List[R]:
    """
    Convenience function to process items in parallel.

    Args:
        items: Items to process
        processor_func: Processing function
        max_threads: Maximum threads to use

    Returns:
        List of results
    """
    processor: ParallelProcessor = ParallelProcessor(max_threads)
    return processor.process_items(items, processor_func)


def is_ancestor_of(
    db,
    potential_ancestor: Person,
    potential_descendant: Person,
    max_depth: Optional[int] = None,
    max_threads: int = 4,
) -> bool:
    """
    Convenience function to check if one person is an ancestor of another.
    Creates a FamilyTreeProcessor and uses its is_ancestor_of method.

    Args:
        db: Database instance
        potential_ancestor: Person to check if they are an ancestor
        potential_descendant: Person to check if they are a descendant
        max_depth: Maximum depth to search (None for unlimited)
        max_threads: Maximum number of threads to use for processing

    Returns:
        True if potential_ancestor is an ancestor of potential_descendant
    """
    processor = create_family_tree_processor(max_threads=max_threads)
    return processor.is_ancestor_of(
        db=db,
        potential_ancestor=potential_ancestor,
        potential_descendant=potential_descendant,
        max_depth=max_depth,
    )


def get_person_ancestors(
    db,
    persons: List[Person],
    max_depth: Optional[int] = None,
    max_threads: int = 4,
    include_root: bool = False,
) -> Set[str]:
    """
    Convenience function to get all ancestors of the given persons.
    Creates a FamilyTreeProcessor and uses its get_person_ancestors method.

    Args:
        db: Database instance
        persons: List of persons to find ancestors for
        max_depth: Maximum depth to traverse (None for unlimited)
        max_threads: Maximum number of threads to use for processing
        include_root: Whether to include root persons in the result

    Returns:
        Set of ancestor handles
    """
    processor = create_family_tree_processor(max_threads=max_threads)
    return processor.get_person_ancestors(
        db=db,
        persons=persons,
        max_depth=max_depth,
        include_root=include_root,
    )


def get_person_descendants(
    db,
    persons: List[Person],
    max_depth: Optional[int] = None,
    max_threads: int = 4,
    include_root: bool = False,
) -> Set[str]:
    """
    Convenience function to get all descendants of the given persons.
    Creates a FamilyTreeProcessor and uses its get_person_descendants method.

    Args:
        db: Database instance
        persons: List of persons to find descendants for
        max_depth: Maximum depth to traverse (None for unlimited)
        max_threads: Maximum number of threads to use for processing
        include_root: Whether to include root persons in the result

    Returns:
        Set of descendant handles
    """
    processor = create_family_tree_processor(max_threads=max_threads)
    return processor.get_person_descendants(
        db=db,
        persons=persons,
        max_depth=max_depth,
        include_root=include_root,
    )


def get_family_descendants(
    db,
    families: List[Family],
    max_depth: Optional[int] = None,
    max_threads: int = 4,
    include_root: bool = False,
) -> Set[str]:
    """
    Convenience function to get all descendants of the given families.
    Creates a FamilyTreeProcessor and uses its get_family_descendants method.

    Args:
        db: Database instance
        families: List of families to find descendants for
        max_depth: Maximum depth to traverse (None for unlimited)
        max_threads: Maximum number of threads to use for processing
        include_root: Whether to include root families in the result

    Returns:
        Set of descendant family handles
    """
    processor = create_family_tree_processor(max_threads=max_threads)
    return processor.get_family_descendants(
        db=db,
        families=families,
        max_depth=max_depth,
        include_root=include_root,
    )
