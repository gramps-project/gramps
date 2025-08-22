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
Tests for general parallel processing utilities.

This module tests the ParallelProcessor class and convenience functions
to ensure they work correctly for various use cases.
"""

import unittest
import time
from typing import List

from gramps.gen.utils.parallel import (
    ParallelProcessor,
    create_parallel_processor,
    process_in_parallel,
)


class TestParallelProcessor(unittest.TestCase):
    """Test cases for parallel processing utilities."""

    def test_empty_input(self):
        """Test that empty input is handled correctly."""
        processor = ParallelProcessor(max_threads=4)

        def dummy_processor(items: List[int]) -> List[str]:
            return [str(item) for item in items]

        result = processor.process_items([], dummy_processor)
        self.assertEqual(result, [])

    def test_single_item(self):
        """Test processing a single item."""
        processor = ParallelProcessor(max_threads=4)

        def square_processor(items: List[int]) -> List[int]:
            return [item * item for item in items]

        result = processor.process_items([5], square_processor)
        self.assertEqual(result, [25])

    def test_multiple_items_sequential_vs_parallel(self):
        """Test that sequential and parallel processing produce the same results."""
        items = list(range(100))

        def square_processor(items: List[int]) -> List[int]:
            return [item * item for item in items]

        # Sequential processing (single thread)
        sequential_processor = ParallelProcessor(max_threads=1)
        sequential_result = sequential_processor.process_items(items, square_processor)

        # Parallel processing (multiple threads)
        parallel_processor = ParallelProcessor(max_threads=4)
        parallel_result = parallel_processor.process_items(items, square_processor)

        # Results should be the same
        self.assertEqual(sequential_result, parallel_result)

        # Verify the results are correct
        expected = [i * i for i in items]
        self.assertEqual(sequential_result, expected)
        self.assertEqual(parallel_result, expected)

    def test_custom_chunk_size(self):
        """Test processing with custom chunk size."""
        items = list(range(20))

        def double_processor(items: List[int]) -> List[int]:
            return [item * 2 for item in items]

        # Use small chunk size to ensure multiple chunks
        processor = ParallelProcessor(max_threads=4, chunk_size=3)
        result = processor.process_items(items, double_processor)

        expected = [i * 2 for i in items]
        self.assertEqual(result, expected)

    def test_string_processing(self):
        """Test processing string items."""
        items = ["apple", "banana", "cherry", "date", "elderberry"]

        def uppercase_processor(items: List[str]) -> List[str]:
            return [item.upper() for item in items]

        processor = ParallelProcessor(max_threads=2)
        result = processor.process_items(items, uppercase_processor)

        expected = ["APPLE", "BANANA", "CHERRY", "DATE", "ELDERBERRY"]
        self.assertEqual(result, expected)

    def test_complex_processing(self):
        """Test processing with more complex operations."""
        items = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
            {"name": "Diana", "age": 28},
        ]

        def extract_names_processor(items: List[dict]) -> List[str]:
            return [item["name"] for item in items]

        processor = ParallelProcessor(max_threads=2)
        result = processor.process_items(items, extract_names_processor)

        expected = ["Alice", "Bob", "Charlie", "Diana"]
        self.assertEqual(result, expected)

    def test_error_handling(self):
        """Test that errors in processing are handled gracefully."""
        items = [1, 2, 3, 4, 5]

        def error_processor(items: List[int]) -> List[int]:
            # Raise an error for even numbers
            result = []
            for item in items:
                if item % 2 == 0:
                    raise ValueError(f"Error processing {item}")
                result.append(item * 2)
            return result

        processor = ParallelProcessor(max_threads=2)
        # Should not raise an exception, but should log the error
        result = processor.process_items(items, error_processor)

        # The result should contain only the odd numbers processed successfully
        # Since we're using 2 threads, some chunks may process successfully
        # We just verify that the result is a subset of the expected successful results
        expected_successful = [1 * 2, 3 * 2, 5 * 2]  # [2, 6, 10]
        self.assertTrue(all(r in expected_successful for r in result))
        self.assertTrue(len(result) <= len(expected_successful))

    def test_convenience_functions(self):
        """Test convenience functions."""
        items = list(range(10))

        def square_processor(items: List[int]) -> List[int]:
            return [item * item for item in items]

        # Test create_parallel_processor
        processor = create_parallel_processor(max_threads=3, chunk_size=2)
        result1 = processor.process_items(items, square_processor)

        # Test process_in_parallel
        result2 = process_in_parallel(
            items, square_processor, max_threads=3, chunk_size=2
        )

        expected = [i * i for i in items]
        self.assertEqual(result1, expected)
        self.assertEqual(result2, expected)

    def test_thread_count_limits(self):
        """Test that thread count limits are respected."""
        # Test minimum thread count
        processor = ParallelProcessor(max_threads=0)
        self.assertEqual(processor.max_threads, 1)

        processor = ParallelProcessor(max_threads=-5)
        self.assertEqual(processor.max_threads, 1)

        # Test normal thread count
        processor = ParallelProcessor(max_threads=8)
        self.assertEqual(processor.max_threads, 8)

    def test_large_dataset(self):
        """Test processing a larger dataset."""
        items = list(range(1000))

        def slow_processor(items: List[int]) -> List[int]:
            # Simulate some processing time
            time.sleep(0.001)
            return [item * 3 for item in items]

        # Sequential processing
        start_time = time.time()
        sequential_processor = ParallelProcessor(max_threads=1)
        sequential_result = sequential_processor.process_items(items, slow_processor)
        sequential_time = time.time() - start_time

        # Parallel processing
        start_time = time.time()
        parallel_processor = ParallelProcessor(max_threads=4)
        parallel_result = parallel_processor.process_items(items, slow_processor)
        parallel_time = time.time() - start_time

        # Results should be the same
        self.assertEqual(sequential_result, parallel_result)

        # Parallel should be faster (though this may not always be true due to overhead)
        # We'll just verify both complete successfully
        expected = [i * 3 for i in items]
        self.assertEqual(sequential_result, expected)
        self.assertEqual(parallel_result, expected)

    def test_mixed_data_types(self):
        """Test processing mixed data types."""
        items = [1, "hello", 3.14, True, None]

        def type_processor(items: List) -> List[str]:
            return [str(type(item).__name__) for item in items]

        processor = ParallelProcessor(max_threads=2)
        result = processor.process_items(items, type_processor)

        expected = ["int", "str", "float", "bool", "NoneType"]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
