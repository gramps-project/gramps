#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-2016 Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2016-2017 Nick Hall
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
Backend for SQLite database.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging
import os
import re
import sqlite3
import json
import threading
from typing import Optional

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db.dbconst import ARRAYSIZE
from gramps.plugins.db.dbapi.dbapi import DBAPI

_ = glocale.translation.gettext
sqlite3.paramstyle = "qmark"
DEFAULT_DATABASE_CONFIG = {
    "pragma": {
        "journal_mode": "WAL",
        "synchronous": "NORMAL",
        "cache_size": "-131072",
        "temp_store": "MEMORY",
        "page_size": "16384",
        "mmap_size": "-1",
        "foreign_keys": "ON",
        "auto_vacuum": "NONE",
        "journal_size_limit": "67108864",
    }
}


# -------------------------------------------------------------------------
#
# ThreadSafeConnectionManager class
#
# -------------------------------------------------------------------------
class ThreadSafeConnectionManager:
    """
    Thread-safe connection manager for SQLite databases.

    This class provides thread-local database connections that can be used
    for concurrent read operations in SQLite WAL mode.
    """

    def __init__(self, db_path: str, database_config: Optional[dict] = None):
        """
        Initialize the connection manager.

        Args:
            db_path: Path to the SQLite database file
            database_config: Database configuration dictionary
        """
        self.db_path = db_path
        self.database_config = database_config or {}
        self._thread_local = threading.local()
        self._lock = threading.Lock()

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a thread-local database connection.

        Returns:
            SQLite connection for the current thread
        """
        if not hasattr(self._thread_local, "connection"):
            # Create new connection for this thread
            connection = sqlite3.connect(self.db_path)

            # Apply database configuration
            if self.database_config.get("pragma"):
                for key, value in self.database_config["pragma"].items():
                    connection.execute(f"PRAGMA {key} = {value};")

            # Store connection in thread-local storage
            self._thread_local.connection = connection

        return self._thread_local.connection

    def close_all_connections(self):
        """Close all thread-local connections."""
        if hasattr(self._thread_local, "connection"):
            try:
                self._thread_local.connection.close()
                delattr(self._thread_local, "connection")
            except:
                pass


# -------------------------------------------------------------------------
#
# SQLite class
#
# -------------------------------------------------------------------------
class SQLite(DBAPI):
    """
    SQLite interface.
    """

    def get_summary(self):
        """
        Return a dictionary of information about this database backend.
        """
        summary = super().get_summary()
        summary.update(
            {
                _("Database version"): sqlite3.sqlite_version,
                _("Database module location"): sqlite3.__file__,
            }
        )
        return summary

    def _initialize(self, directory, username, password):
        self.database_config = self._get_database_config(directory)
        if directory == ":memory:":
            path_to_db = ":memory:"
        else:
            path_to_db = os.path.join(directory, "sqlite.db")

        # Create the main connection for the primary thread
        self.dbapi = Connection(path_to_db, database_config=self.database_config)

        # Create thread-safe connection manager for parallel operations
        if directory != ":memory:":
            self.thread_connection_manager = ThreadSafeConnectionManager(
                path_to_db, self.database_config
            )
        else:
            self.thread_connection_manager = None

    def _get_database_config(self, directory):
        """
        Get the default database config dictionary.
        """
        if directory == ":memory:":
            return DEFAULT_DATABASE_CONFIG
        else:
            database_json_path = os.path.join(directory, "config.json")
            if os.path.exists(database_json_path):
                with open(database_json_path) as fp:
                    return json.load(fp)
            else:
                with open(database_json_path, "w") as fp:
                    json.dump(DEFAULT_DATABASE_CONFIG, fp)
                return DEFAULT_DATABASE_CONFIG

    def get_thread_connection(self):
        """
        Get a thread-local database connection for parallel operations.

        Returns:
            Thread-local SQLite connection or None if not available
        """
        if self.thread_connection_manager:
            return self.thread_connection_manager.get_connection()
        return None

    def close_thread_connections(self):
        """Close all thread-local connections."""
        if self.thread_connection_manager:
            self.thread_connection_manager.close_all_connections()

    def supports_parallel_reads(self):
        """
        Check if this database backend supports parallel read operations.

        Returns:
            True if parallel reads are supported
        """
        return self.thread_connection_manager is not None

    def create_connection_wrapper(self, original_connection, thread_connection):
        """
        Create a thread-safe connection wrapper for this database backend.

        Args:
            original_connection: The original database connection
            thread_connection: Thread-local connection to use

        Returns:
            Thread-safe connection wrapper
        """
        return SQLiteConnectionWrapper(original_connection, thread_connection)

    def _close(self):
        """Close the database and all thread connections."""
        # Close thread connections first
        self.close_thread_connections()
        # Close the main connection
        super()._close()


# -------------------------------------------------------------------------
#
# Connection class
#
# -------------------------------------------------------------------------
class Connection:
    """
    The Sqlite class is an interface between the DBAPI class which is the Gramps
    backend for the DBAPI interface and the sqlite3 python module.
    """

    def __init__(self, *args, database_config=None, **kwargs):
        """
        Create a new Sqlite instance.

        This connects to a sqlite3 database and creates a cursor instance.

        :param args: arguments to be passed to the sqlite3 connect class at
                     creation.
        :type args: list
        :param kwargs: arguments to be passed to the sqlite3 connect class at
                       creation.
        :type kwargs: list
        """
        self.log = logging.getLogger(".sqlite")
        self.__connection = sqlite3.connect(*args, **kwargs)

        if database_config is not None and database_config.get("pragma"):
            for key, value in database_config["pragma"].items():
                self.__connection.execute(f"PRAGMA {key} = {value};")
            self.__connection.execute("VACUUM;")
            self.__connection.execute("PRAGMA optimize;")

        self.__cursor = self.__connection.cursor()
        self.__connection.create_function("regexp", 2, regexp)
        self.__collations = []
        self.__tmap = str.maketrans("-.@=;", "_____")
        self.check_collation(glocale)

    def check_collation(self, locale):
        """
        Checks that a collation exists and if not creates it.

        :param locale: Locale to be checked.
        :param type: A GrampsLocale object.
        """
        # PySQlite3 permits only ascii alphanumerics and underscores in
        # collation names so first translate any old-style Unicode locale
        # delimiters to underscores.
        collation = locale.get_collation().translate(self.__tmap)
        if collation not in self.__collations:
            self.__connection.create_collation(collation, locale.strcoll)
            self.__collations.append(collation)
        return collation

    def execute(self, *args, **kwargs):
        """
        Executes an SQL statement.

        :param args: arguments to be passed to the sqlite3 execute statement
        :type args: list
        :param kwargs: arguments to be passed to the sqlite3 execute statement
        :type kwargs: list
        """
        self.log.debug(args)
        self.__cursor.execute(*args, **kwargs)

    def fetchone(self):
        """
        Fetches the next row of a query result set, returning a single sequence,
        or None when no more data is available.
        """
        return self.__cursor.fetchone()

    def fetchall(self):
        """
        Fetches the next set of rows of a query result, returning a list. An
        empty list is returned when no more rows are available.
        """
        return self.__cursor.fetchall()

    def begin(self):
        """
        Start a transaction manually. This transactions usually persist until
        the next COMMIT or ROLLBACK command.
        """
        self.log.debug("BEGIN TRANSACTION;")
        self.execute("BEGIN TRANSACTION;")

    def commit(self):
        """
        Commit the current transaction.
        """
        self.log.debug("COMMIT;")
        self.__connection.commit()

    def rollback(self):
        """
        Roll back any changes to the database since the last call to commit().
        """
        self.log.debug("ROLLBACK;")
        self.__connection.rollback()

    def table_exists(self, table):
        """
        Test whether the specified SQL database table exists.

        :param table: table name to check.
        :type table: str
        :returns: True if the table exists, false otherwise.
        :rtype: bool
        """
        self.execute(
            "SELECT COUNT(*) "
            "FROM sqlite_master "
            f"WHERE type='table' AND name='{table}';"
        )
        return self.fetchone()[0] != 0

    def column_exists(self, table, column):
        """
        Test whether the specified SQL column exists in the specified table.

        :param table: table name to check.
        :type table: str
        :param column: column name to check.
        :type column: str
        :returns: True if the column exists, False otherwise.
        :rtype: bool
        """
        self.execute(
            "SELECT COUNT(*) "
            f"FROM pragma_table_info('{table}') "
            f"WHERE name = '{column}'"
        )
        return self.fetchone()[0] != 0

    def drop_column(self, table_name, column_name):
        # DROP COLUMN is available with Sqlite v 3.35.0, released 2021-03-12
        db_ver = sqlite3.sqlite_version.split(".")
        if int(db_ver[0]) == 3 and int(db_ver[1]) >= 35:
            self.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name};")

    def close(self):
        """
        Close the current database.
        """
        self.log.debug("closing database...")
        self.__connection.close()

    def cursor(self):
        """
        Return a new cursor.
        """
        return Cursor(self.__connection)


# -------------------------------------------------------------------------
#
# SQLite-specific thread-safe wrappers
#
# -------------------------------------------------------------------------
class SQLiteConnectionWrapper:
    """
    A wrapper for SQLite database connections that can be used with thread-local connections.

    This class mimics the interface of the original database connection but uses
    thread-local connections when available, providing transparent thread-safe
    database access without changing any database access methods.
    """

    def __init__(self, original_connection, thread_connection):
        """
        Initialize the wrapper.

        Args:
            original_connection: The original database connection (Connection object)
            thread_connection: Thread-local SQLite connection to use instead
        """
        self.original_connection = original_connection
        self.thread_connection = thread_connection
        # Create a cursor from the thread-local connection for execute/fetch operations
        self._thread_cursor = thread_connection.cursor()

    def execute(self, *args, **kwargs):
        """Execute SQL using thread-local connection."""
        return self._thread_cursor.execute(*args, **kwargs)

    def fetchone(self):
        """Fetch one row using thread-local connection."""
        return self._thread_cursor.fetchone()

    def fetchall(self):
        """Fetch all rows using thread-local connection."""
        return self._thread_cursor.fetchall()

    def fetchmany(self, size=None):
        """Fetch many rows using thread-local connection."""
        if size is None:
            return self._thread_cursor.fetchmany()
        else:
            return self._thread_cursor.fetchmany(size)

    def cursor(self):
        """Return a cursor using thread-local connection."""
        return SQLiteCursorWrapper(
            self.original_connection.cursor(), self.thread_connection
        )

    def __getattr__(self, name):
        """Delegate any other attributes to the original connection."""
        return getattr(self.original_connection, name)


class SQLiteCursorWrapper:
    """
    A wrapper for SQLite database cursors that uses thread-local connections.
    """

    def __init__(self, original_cursor, thread_connection):
        """
        Initialize the cursor wrapper.

        Args:
            original_cursor: The original cursor
            thread_connection: Thread-local connection to use
        """
        self.original_cursor = original_cursor
        self.thread_connection = thread_connection
        self._thread_cursor = None

    def __enter__(self):
        """Create thread-local cursor for context manager."""
        self._thread_cursor = self.thread_connection.cursor()
        return self

    def __exit__(self, *args, **kwargs):
        """Close thread-local cursor."""
        if self._thread_cursor:
            self._thread_cursor.close()
            self._thread_cursor = None

    def execute(self, *args, **kwargs):
        """Execute SQL using thread-local cursor."""
        if self._thread_cursor:
            return self._thread_cursor.execute(*args, **kwargs)
        else:
            # Create a temporary cursor if not in context manager
            cursor = self.thread_connection.cursor()
            try:
                return cursor.execute(*args, **kwargs)
            finally:
                cursor.close()

    def fetchone(self):
        """Fetch one row using thread-local cursor."""
        if self._thread_cursor:
            return self._thread_cursor.fetchone()
        else:
            return None

    def fetchall(self):
        """Fetch all rows using thread-local cursor."""
        if self._thread_cursor:
            return self._thread_cursor.fetchall()
        else:
            return []

    def fetchmany(self, size=None):
        """Fetch many rows using thread-local cursor."""
        if self._thread_cursor:
            if size is None:
                return self._thread_cursor.fetchmany()
            else:
                return self._thread_cursor.fetchmany(size)
        else:
            return []

    def __getattr__(self, name):
        """Delegate any other attributes to the original cursor."""
        return getattr(self.original_cursor, name)


# -------------------------------------------------------------------------
#
# Cursor class
#
# -------------------------------------------------------------------------
class Cursor:
    """
    Exposes access to a SQLite cursor as an iterator
    """

    def __init__(self, connection):
        self.__connection = connection

    def __enter__(self):
        self.__cursor = self.__connection.cursor()
        self.__cursor.arraysize = ARRAYSIZE
        return self

    def __exit__(self, *args, **kwargs):
        self.__cursor.close()

    def execute(self, *args, **kwargs):
        """
        Executes an SQL statement.

        :param args: arguments to be passed to the sqlite3 execute statement
        :type args: list
        :param kwargs: arguments to be passed to the sqlite3 execute statement
        :type kwargs: list
        """
        self.__cursor.execute(*args, **kwargs)

    def fetchmany(self):
        """
        Fetches the next set of rows of a query result, returning a list. An
        empty list is returned when no more rows are available.
        """
        return self.__cursor.fetchmany()


def regexp(expr, value):
    """
    A user defined function that can be called from within an SQL statement.

    This function has two parameters.

    :param expr: pattern to look for.
    :type expr: str
    :param value: the string to search.
    :type value: list
    :returns: True if the expr exists within the value, false otherwise.
    :rtype: bool
    """
    return re.search(expr, value, re.MULTILINE) is not None
