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

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
import sqlite3
from ..const import GRAMPS_LOCALE as glocale
from gramps.plugins.db.dbapi.sqlite import SQLiteConnectionWrapper


class ThreadLocalConnectionWrapper:
    """
    A simple wrapper for thread-local SQLite connections.

    This wrapper provides the basic interface needed for database operations
    using a thread-local connection.
    """

    def __init__(self, thread_connection_manager, original_connection=None):
        """
        Initialize the wrapper.

        Args:
            thread_connection_manager: ThreadSafeConnectionManager to get thread-local connections
            original_connection: Original connection for fallback (optional)
        """
        self.thread_connection_manager = thread_connection_manager
        self._original_connection = original_connection
        self._current_cursor = None

    @property
    def thread_connection(self):
        """Get the thread-local connection for the current thread."""
        return self.thread_connection_manager.get_connection()

    def execute(self, *args, **kwargs):
        """Execute SQL using thread-local connection."""
        try:
            # Create new cursor in current thread (don't reuse cursors across threads)
            import threading

            current_thread = threading.current_thread()
            print(
                f"DEBUG: ThreadLocalConnectionWrapper.execute called in thread: {current_thread.name}"
            )
            print(
                f"DEBUG: Getting thread connection from manager: {self.thread_connection_manager}"
            )
            thread_conn = self.thread_connection
            print(f"DEBUG: Got thread connection: {thread_conn}")
            self._current_cursor = thread_conn.cursor()
            print(f"DEBUG: Created cursor: {self._current_cursor}")
            return self._current_cursor.execute(*args, **kwargs)
        except sqlite3.ProgrammingError as e:
            if (
                "SQLite objects created in a thread can only be used in that same thread"
                in str(e)
            ):
                # If we're in the wrong thread, try to get a new connection for this thread
                import threading

                current_thread = threading.current_thread()
                print(f"DEBUG: SQLite thread error in thread: {current_thread.name}")
                if current_thread.name == "MainThread" and self._original_connection:
                    # In main thread, we should use the original connection
                    # This is a fallback for teardown scenarios
                    print(f"DEBUG: Using original connection fallback")
                    return self._original_connection.execute(*args, **kwargs)
                else:
                    # In worker thread, try to get a new thread-local connection
                    from gramps.plugins.db.dbapi.sqlite import (
                        ThreadSafeConnectionManager,
                    )

                    # This is a complex case - we might need to create a new connection
                    print(f"DEBUG: Re-raising error in worker thread")
                    raise e
            else:
                raise e

    def fetchone(self):
        """Fetch one row using thread-local connection."""
        try:
            if self._current_cursor:
                return self._current_cursor.fetchone()
            return None
        except sqlite3.ProgrammingError as e:
            if (
                "SQLite objects created in a thread can only be used in that same thread"
                in str(e)
            ):
                # If we're in the main thread and getting a thread error, try using the original connection
                import threading

                if (
                    threading.current_thread().name == "MainThread"
                    and self._original_connection
                ):
                    return self._original_connection.fetchone()
            raise

    def fetchall(self):
        """Fetch all rows using thread-local connection."""
        try:
            if self._current_cursor:
                return self._current_cursor.fetchall()
            return []
        except sqlite3.ProgrammingError as e:
            if (
                "SQLite objects created in a thread can only be used in that same thread"
                in str(e)
            ):
                # If we're in the main thread and getting a thread error, try using the original connection
                import threading

                if (
                    threading.current_thread().name == "MainThread"
                    and self._original_connection
                ):
                    return self._original_connection.fetchall()
            raise

    def fetchmany(self, size=None):
        """Fetch many rows using thread-local connection."""
        try:
            if self._current_cursor:
                return self._current_cursor.fetchmany(size)
            return []
        except sqlite3.ProgrammingError as e:
            if (
                "SQLite objects created in a thread can only be used in that same thread"
                in str(e)
            ):
                # If we're in the main thread and getting a thread error, try using the original connection
                import threading

                if (
                    threading.current_thread().name == "MainThread"
                    and self._original_connection
                ):
                    return self._original_connection.fetchmany(size)
            raise

    def begin(self):
        """Start a transaction manually."""
        self.execute("BEGIN TRANSACTION;")

    def commit(self):
        """Commit the current transaction."""
        try:
            self.thread_connection.commit()
        except sqlite3.ProgrammingError as e:
            if (
                "SQLite objects created in a thread can only be used in that same thread"
                in str(e)
            ):
                # If we're in the main thread and getting a thread error, try using the original connection
                import threading

                if (
                    threading.current_thread().name == "MainThread"
                    and self._original_connection
                ):
                    self._original_connection.commit()
                else:
                    raise
            else:
                raise

    def rollback(self):
        """Roll back any changes to the database since the last call to commit()."""
        try:
            self.thread_connection.rollback()
        except sqlite3.ProgrammingError as e:
            if (
                "SQLite objects created in a thread can only be used in that same thread"
                in str(e)
            ):
                # If we're in the main thread and getting a thread error, try using the original connection
                import threading

                if (
                    threading.current_thread().name == "MainThread"
                    and self._original_connection
                ):
                    self._original_connection.rollback()
                else:
                    raise
            else:
                raise

    def table_exists(self, table):
        """Test whether the specified SQL database table exists."""
        self.execute(
            "SELECT COUNT(*) "
            "FROM sqlite_master "
            f"WHERE type='table' AND name='{table}';"
        )
        return self.fetchone()[0] != 0

    def column_exists(self, table, column):
        """Test whether the specified SQL column exists in the specified table."""
        self.execute(
            "SELECT COUNT(*) "
            f"FROM pragma_table_info('{table}') "
            f"WHERE name = '{column}'"
        )
        return self.fetchone()[0] != 0

    def close(self):
        """Close the current database."""
        # Don't close cursors or connections - let the thread manager handle it
        pass

    def cursor(self):
        """Return a new cursor."""
        return self.thread_connection.cursor()

    def __getattr__(self, name):
        """Delegate any other attributes to the thread connection."""
        return getattr(self.thread_connection, name)


_ = glocale.translation.gettext

# Set up logging
LOG = logging.getLogger(".parallel")

# Type variables for generic typing
T = TypeVar("T")
R = TypeVar("R")


class ThreadLocalDatabaseWrapper:
    """
    A wrapper for database objects that provides thread-local database connections.

    This wrapper intercepts database method calls and ensures they use the
    thread-local connection when available, providing transparent thread-safe
    database access.
    """

    def __init__(self, database, thread_connection_manager):
        """
        Initialize the wrapper.

        Args:
            database: The original database object
            thread_connection_manager: ThreadSafeConnectionManager instance
        """
        self._database = database
        self._thread_connection_manager = thread_connection_manager
        self._original_dbapi = database.dbapi

    def __enter__(self):
        """Enter the context manager, swapping the database connection."""
        if self._thread_connection_manager:
            # Get thread-local connection and create wrapper
            thread_connection = self._thread_connection_manager.get_connection()
            if thread_connection:
                # Create a wrapper that intercepts method calls
                return DatabaseMethodWrapper(
                    self._database, self._thread_connection_manager
                )
        # Fall back to original database if no thread connection
        return self._database

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager, restoring the original connection."""
        # No cleanup needed - the thread connection manager handles this
        pass


class DatabaseMethodWrapper:
    """
    A wrapper that intercepts database method calls and uses thread-local connections.
    """

    def __init__(self, database, thread_connection_manager):
        """
        Initialize the wrapper.

        Args:
            database: The original database object
            thread_connection_manager: ThreadSafeConnectionManager for getting thread-local connections
        """
        self._database = database
        self._thread_connection_manager = thread_connection_manager
        self._original_dbapi = database.dbapi

    def __getattr__(self, name):
        """
        Intercept attribute access and handle database methods specially.
        """
        import threading

        current_thread = threading.current_thread()
        print(
            f"DEBUG: DatabaseMethodWrapper.__getattr__ called for '{name}' in thread: {current_thread.name}"
        )

        # Special handling for dbapi attribute - always use thread-local in worker threads
        if name == "dbapi":
            if current_thread.name != "MainThread":
                # In worker threads, return a thread-local connection wrapper
                print(
                    f"DEBUG: Returning ThreadLocalConnectionWrapper for dbapi in worker thread"
                )
                return ThreadLocalConnectionWrapper(
                    self._thread_connection_manager, self._original_dbapi
                )
            else:
                # In main thread, return the original dbapi
                print(f"DEBUG: Returning original dbapi in main thread")
                return self._original_dbapi

        # Get the attribute from the original database
        attr = getattr(self._database, name)
        print(f"DEBUG: Got attribute '{name}' from database: {type(attr)}")

        # If it's a method that might use the database, wrap it
        if callable(attr) and hasattr(attr, "__name__"):
            # Check if this method might use the database
            if any(
                keyword in attr.__name__.lower()
                for keyword in ["raw", "data", "get", "find", "iter"]
            ):
                print(f"DEBUG: Wrapping method '{name}' for thread-safe access")
                return self._wrap_method(attr)

        return attr

    def _wrap_method(self, method):
        """
        Wrap a method to use the thread-local connection.
        """

        def wrapped_method(*args, **kwargs):
            import threading

            current_thread = threading.current_thread()
            print(
                f"DEBUG: _wrap_method executing '{method.__name__}' in thread: {current_thread.name}"
            )

            if current_thread.name != "MainThread":
                # In worker threads, temporarily swap the dbapi to use thread-local connection
                original_dbapi = self._database.dbapi
                thread_local_dbapi = ThreadLocalConnectionWrapper(
                    self._thread_connection_manager, original_dbapi
                )
                print(f"DEBUG: Temporarily swapping dbapi for method {method.__name__}")

                try:
                    # Swap the dbapi attribute
                    self._database.dbapi = thread_local_dbapi
                    # Call the original method with the thread-local connection
                    result = method(*args, **kwargs)
                    print(f"DEBUG: Method {method.__name__} completed successfully")
                    return result
                finally:
                    # Always restore the original dbapi
                    self._database.dbapi = original_dbapi
                    print(
                        f"DEBUG: Restored original dbapi after method {method.__name__}"
                    )
            else:
                # In main thread, just call the original method
                print(
                    f"DEBUG: Calling method {method.__name__} directly in main thread"
                )
                return method(*args, **kwargs)

        return wrapped_method

    def get_database_config(self):
        """Delegate to the original database."""
        return self._database.get_database_config()


class ParallelProcessor(Generic[T, R]):
    """
    A configurable parallel processor for batch operations.

    This class provides a thread-safe way to process collections of items
    in parallel, with configurable thread counts.
    """

    def __init__(
        self,
        max_threads: int,
        chunk_size: Optional[int] = None,
    ):
        """
        Initialize the parallel processor.

        Args:
            max_threads: Maximum number of threads to use
            chunk_size: Size of chunks to process per thread (default: auto-calculate)
        """
        self.max_threads = max(1, max_threads)
        self.chunk_size = chunk_size
        self._lock = threading.Lock()

    def process_items(
        self,
        items: List[T],
        processor_func: Callable[[List[T], Any], List[R]],
        db: Optional[Any] = None,
    ) -> List[R]:
        """
        Process a list of items using parallel processing.

        Args:
            items: List of items to process
            processor_func: Function to process a chunk of items
                          Should have signature: func(chunk: List[T], db: Any) -> List[R]
            db: Database instance (optional, for thread-safe access)

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
        results: List[List[R]] = [[] for _ in chunks]  # Pre-allocate results list

        def worker(chunk: List[T], chunk_index: int):
            """Worker function for processing chunks."""
            try:
                LOG.debug(
                    f"Worker {chunk_index} processing chunk of {len(chunk)} items"
                )
                # Create database wrapper for thread-safe access if database is provided
                LOG.debug(
                    f"Worker {chunk_index} checking database: db={db is not None}, hasattr={hasattr(db, 'create_thread_safe_wrapper') if db else False}"
                )
                if db and hasattr(db, "create_thread_safe_wrapper"):
                    LOG.debug(
                        f"Worker {chunk_index} attempting to create thread-safe database wrapper"
                    )
                    database_wrapper = db.create_thread_safe_wrapper()
                    LOG.debug(
                        f"Worker {chunk_index} database wrapper creation result: {database_wrapper is not None}"
                    )
                    if database_wrapper:
                        LOG.debug(
                            f"Worker {chunk_index} using thread-safe database wrapper"
                        )
                        with database_wrapper as thread_safe_db:
                            # Pass the thread-safe database to the processor function
                            chunk_results = processor_func(chunk, thread_safe_db)
                            LOG.debug(
                                f"Worker {chunk_index} got results with thread-safe db: {chunk_results}"
                            )
                    else:
                        LOG.debug(
                            f"Worker {chunk_index} database wrapper creation failed, using original database"
                        )
                        chunk_results = processor_func(chunk, db)
                        LOG.debug(
                            f"Worker {chunk_index} got results with original db: {chunk_results}"
                        )
                else:
                    LOG.debug(f"Worker {chunk_index} using original database")
                    chunk_results = processor_func(chunk, db)
                    LOG.debug(f"Worker {chunk_index} got results: {chunk_results}")

                results[chunk_index] = [chunk_results]
                LOG.debug(f"Worker {chunk_index} completed successfully")
            except Exception as e:
                LOG.error(f"Error in parallel processing: {e}")
                import traceback

                traceback.print_exc()
                results[chunk_index] = []

        for i, chunk in enumerate(chunks):
            thread = threading.Thread(target=worker, args=(chunk, i))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Combine results in order
        all_results: List[R] = []
        for chunk_results in results:
            all_results.extend(chunk_results)

        return all_results


# Convenience functions for common use cases
def create_parallel_processor(
    max_threads: int,
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
    max_threads: int,
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
