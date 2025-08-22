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
General-purpose parallel processing utilities for Gramps operations.

This module provides reusable parallel processing infrastructure for operations
that can benefit from concurrent execution, such as data processing and filtering operations.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import threading
from typing import Any, Callable, List, Optional, TypeVar, Generic
import logging
import queue

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale

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
        if not items:
            return []

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


# Convenience functions for common use cases
def create_parallel_processor(
    max_threads: int = 4,
    chunk_size: Optional[int] = None,
) -> ParallelProcessor:
    """
    Create a ParallelProcessor with sensible defaults.

    Args:
        max_threads: Maximum number of worker threads for parallel processing
        chunk_size: Size of chunks to process per thread

    Returns:
        Configured ParallelProcessor instance
    """
    return ParallelProcessor(
        max_threads=max_threads,
        chunk_size=chunk_size,
    )


def process_in_parallel(
    items: List[T],
    processor_func: Callable[[List[T]], List[R]],
    max_threads: int = 4,
    chunk_size: Optional[int] = None,
) -> List[R]:
    """
    Convenience function to process items in parallel.

    Args:
        items: Items to process
        processor_func: Processing function
        max_threads: Maximum threads to use
        chunk_size: Size of chunks to process per thread

    Returns:
        List of results
    """
    processor: ParallelProcessor = ParallelProcessor(
        max_threads=max_threads, chunk_size=chunk_size
    )
    return processor.process_items(items, processor_func)
