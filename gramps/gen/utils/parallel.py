#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024 Gramps Development Team
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
from typing import Any, Callable, List, Optional, TypeVar, Generic
from collections.abc import Iterable
import logging

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .lru import LRU

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
    in parallel, with configurable thread counts and automatic fallback
    to sequential processing for small workloads.
    """

    def __init__(
        self,
        max_threads: int = 4,
        min_items_for_parallel: int = 4,
        chunk_size: Optional[int] = None,
    ):
        """
        Initialize the parallel processor.

        Args:
            max_threads: Maximum number of threads to use (default: 4)
            min_items_for_parallel: Minimum items needed to use parallel processing (default: 4)
            chunk_size: Size of chunks to process per thread (default: auto-calculate)
        """
        self.max_threads = max(1, max_threads)
        self.min_items_for_parallel = max(1, min_items_for_parallel)
        self.chunk_size = chunk_size
        self._lock = threading.Lock()

    def process_items(
        self,
        items: List[T],
        processor_func: Callable[[List[T], List[R]], None],
        results_list: List[R],
    ) -> None:
        """
        Process a list of items using parallel or sequential processing.

        Args:
            items: List of items to process
            processor_func: Function to process a chunk of items
                          Should have signature: func(chunk: List[T], results: List[R]) -> None
            results_list: List to collect results (will be modified in-place)
        """
        if len(items) < self.min_items_for_parallel:
            # Use sequential processing for small workloads
            LOG.debug(f"Using sequential processing for {len(items)} items")
            processor_func(items, results_list)
            return

        # Calculate optimal chunk size
        if self.chunk_size is None:
            chunk_size = max(1, len(items) // self.max_threads)
        else:
            chunk_size = self.chunk_size

        # Split items into chunks
        chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

        if len(chunks) == 1:
            # Only one chunk, use sequential processing
            LOG.debug(
                f"Using sequential processing for single chunk of {len(items)} items"
            )
            processor_func(items, results_list)
            return

        LOG.debug(
            f"Using parallel processing: {len(items)} items in {len(chunks)} chunks"
        )

        # Process chunks in parallel
        threads = []
        thread_results = []

        for chunk in chunks:
            chunk_results = []
            thread = threading.Thread(
                target=processor_func, args=(chunk, chunk_results)
            )
            threads.append(thread)
            thread_results.append(chunk_results)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Combine results thread-safely
        with self._lock:
            for chunk_results in thread_results:
                results_list.extend(chunk_results)


class FamilyTreeProcessor:
    """
    Specialized parallel processor for family tree operations.

    This class provides optimized parallel processing for common family tree
    operations like descendant traversal, with built-in caching and thread safety.
    """

    def __init__(
        self,
        max_threads: int = 4,
        min_families_for_parallel: int = 5,
        enable_caching: bool = True,
        cache_size: int = 1000,
    ):
        """
        Initialize the family tree processor.

        Args:
            max_threads: Maximum number of threads to use
            min_families_for_parallel: Minimum families needed for parallel processing
            enable_caching: Whether to enable LRU caching
            cache_size: Size of LRU caches (if enabled)
        """
        self.processor = ParallelProcessor(
            max_threads=max_threads, min_items_for_parallel=min_families_for_parallel
        )
        self.enable_caching = enable_caching
        self.cache_size = cache_size
        self._lock = threading.Lock()

        # Initialize caches if enabled
        if self.enable_caching:
            self._person_cache = LRU(cache_size)
            self._family_cache = LRU(cache_size)
        else:
            self._person_cache = None
            self._family_cache = None

    def get_person_cached(self, db, handle: str):
        """
        Get person from cache or database with thread-safe caching.

        Args:
            db: Database instance
            handle: Person handle

        Returns:
            Person object or None
        """
        if not self.enable_caching:
            return db.get_person_from_handle(handle)

        with self._lock:
            if handle not in self._person_cache:
                person = db.get_person_from_handle(handle)
                if person:
                    self._person_cache[handle] = person
                return person
            return self._person_cache[handle]

    def get_family_cached(self, db, handle: str):
        """
        Get family from cache or database with thread-safe caching.

        Args:
            db: Database instance
            handle: Family handle

        Returns:
            Family object or None
        """
        if not self.enable_caching:
            return db.get_family_from_handle(handle)

        with self._lock:
            if handle not in self._family_cache:
                family = db.get_family_from_handle(handle)
                if family:
                    self._family_cache[handle] = family
                return family
            return self._family_cache[handle]

    def clear_caches(self):
        """Clear all caches."""
        if self.enable_caching:
            with self._lock:
                self._person_cache.clear()
                self._family_cache.clear()

    def process_person_families(
        self,
        db,
        family_handles: List[str],
        processor_func: Callable[[str, List[str]], None],
        results: List[str],
    ) -> None:
        """
        Process person families in parallel.

        Args:
            db: Database instance
            family_handles: List of family handles to process
            processor_func: Function to process each family handle
                          Should have signature: func(family_handle: str, child_handles: List[str]) -> None
            results: List to collect child handles
        """

        def chunk_processor(chunk: List[str], chunk_results: List[str]):
            """Process a chunk of family handles."""
            for family_handle in chunk:
                family = self.get_family_cached(db, family_handle)
                if family:
                    for child_ref in family.child_ref_list:
                        chunk_results.append(child_ref.ref)

        self.processor.process_items(family_handles, chunk_processor, results)

    def process_child_families(
        self, db, child_handles: List[str], results: List[str]
    ) -> None:
        """
        Process children to get their family handles in parallel.

        Args:
            db: Database instance
            child_handles: List of child handles to process
            results: List to collect family handles
        """

        def chunk_processor(chunk: List[str], chunk_results: List[str]):
            """Process a chunk of child handles."""
            for child_handle in chunk:
                child = self.get_person_cached(db, child_handle)
                if child:
                    for family_handle in child.family_list:
                        chunk_results.append(family_handle)

        self.processor.process_items(child_handles, chunk_processor, results)


# Convenience functions for common use cases
def create_family_tree_processor(**kwargs) -> FamilyTreeProcessor:
    """
    Create a FamilyTreeProcessor with sensible defaults.

    Args:
        **kwargs: Arguments to pass to FamilyTreeProcessor constructor

    Returns:
        Configured FamilyTreeProcessor instance
    """
    return FamilyTreeProcessor(**kwargs)


def process_in_parallel(
    items: List[T],
    processor_func: Callable[[List[T], List[R]], None],
    max_threads: int = 4,
    min_items_for_parallel: int = 4,
) -> List[R]:
    """
    Convenience function to process items in parallel.

    Args:
        items: Items to process
        processor_func: Processing function
        max_threads: Maximum threads to use
        min_items_for_parallel: Minimum items for parallel processing

    Returns:
        List of results
    """
    processor = ParallelProcessor(max_threads, min_items_for_parallel)
    results = []
    processor.process_items(items, processor_func, results)
    return results
