#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-2016, 2025 Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2016-2017       Nick Hall
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
    "pragmas": {
        "journal_mode": "WAL",
        "synchronous": "NORMAL",
        "cache_size": "-131072",
        "temp_store": "MEMORY",
        "page_size": "16384",
        "mmap_size": "-1",
        "foreign_keys": "ON",
        "auto_vacuum": "NONE",
        "journal_size_limit": "67108864",
    },
    "parallel": {
        "max_threads": 4,
    },
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

    def __init__(self, db_path: str, database_config: dict = None):
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
            if self.database_config.get("pragmas"):
                for key, value in self.database_config["pragmas"].items():
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
        self._database_config = self._get_database_config(directory)
        self._thread_connection_manager = None

        if directory == ":memory:":
            path_to_db = ":memory:"
        else:
            path_to_db = os.path.join(directory, "sqlite.db")
            self._thread_connection_manager = ThreadSafeConnectionManager(
                path_to_db, self._database_config
            )

        # Create the main connection for the primary thread
        self.dbapi = Connection(path_to_db, pragmas=self.get_database_config("pragmas"))

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

    def get_database_config(self, section=None, key=None):
        """
        Get database configuration value.

        Args:
            section: Configuration section (e.g., "pragmas", "parallel")
            key: Configuration key within section

        Returns:
            Configuration value or entire config dict if section/key not specified
        """
        if section is None:
            return self._database_config
        elif key is None:
            return self._database_config.get(section, {})
        else:
            return self._database_config.get(section, {}).get(key)

    def supports_parallel_reads(self):
        """
        Check if this database backend supports parallel read operations.

        Returns:
            True if parallel reads are supported
        """
        # Check if WAL mode is enabled AND we have thread connection manager
        # (in-memory databases can't use parallel processing)
        return (
            self.get_database_config("pragmas", "journal_mode") == "WAL"
            and self._thread_connection_manager is not None
        )

    def create_thread_safe_wrapper(self):
        """
        Create a thread-safe wrapper for this database.

        This method creates a wrapper that can be used as a context manager
        to temporarily swap the database connection with a thread-local one.

        Returns:
            Thread-safe database wrapper or None if not supported
        """
        from gramps.gen.utils.parallel import ThreadLocalDatabaseWrapper

        if self.supports_parallel_reads():
            # Get the thread connection manager from the database
            if self._thread_connection_manager:
                return ThreadLocalDatabaseWrapper(self, self._thread_connection_manager)
        return None

    def create_thread_safe_database_instance(self, thread_connection_manager):
        """
        Create a new database instance that uses a thread-local connection.

        This method creates a new SQLite database instance that uses the
        provided thread-local connection manager for database operations.

        Args:
            thread_connection_manager: Thread-local connection manager

        Returns:
            New database instance with thread-local connection or None if not supported
        """
        # Check if the database supports parallel reads
        if not self.supports_parallel_reads():
            # If this database doesn't support parallel reads, return None
            # This will cause the parallel processor to fall back to sequential processing
            return None

        # Import here to avoid circular imports
        from gramps.gen.utils.parallel import ThreadLocalConnectionWrapper

        # Create a thread-local dbapi wrapper
        thread_local_dbapi = ThreadLocalConnectionWrapper(
            thread_connection_manager, self.dbapi
        )

        # Create a new database instance
        from gramps.gen.db.utils import make_database

        thread_db = make_database("sqlite")
        thread_db.dbapi = thread_local_dbapi
        thread_db.serializer = self.serializer

        # Copy the thread-safe infrastructure from the original database
        thread_db._thread_connection_manager = thread_connection_manager
        thread_db._database_config = getattr(self, "_database_config", {})

        return thread_db

    def _close(self):
        """Close the database and all thread connections."""
        # Close thread connections first
        if self._thread_connection_manager:
            self._thread_connection_manager.close_all_connections()
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

    def __init__(self, *args, pragmas=None, **kwargs):
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

        if pragmas is not None:
            for key, value in pragmas.items():
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
# SQLiteConnectionWrapper class
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
        # Maintain a cursor for the current operation
        self._current_cursor = None

    def execute(self, *args, **kwargs):
        """Execute SQL using thread-local connection."""
        # Close any existing cursor
        if self._current_cursor:
            self._current_cursor.close()
        # Create new cursor in current thread
        self._current_cursor = self.thread_connection.cursor()
        return self._current_cursor.execute(*args, **kwargs)

    def fetchone(self):
        """Fetch one row using thread-local connection."""
        if self._current_cursor:
            return self._current_cursor.fetchone()
        return None

    def fetchall(self):
        """Fetch all rows using thread-local connection."""
        if self._current_cursor:
            return self._current_cursor.fetchall()
        return []

    def fetchmany(self, size=None):
        """Fetch many rows using thread-local connection."""
        if self._current_cursor:
            return self._current_cursor.fetchmany(size)
        return []

    def __getattr__(self, name):
        """Delegate any other attributes to the thread connection."""
        # For database operations that don't involve cursors, use the thread connection
        if name in [
            "close",
            "commit",
            "rollback",
            "create_function",
            "create_collation",
        ]:
            return getattr(self.thread_connection, name)
        # For cursor operations, create a new cursor in the current thread
        elif name in ["cursor"]:
            return lambda: self.thread_connection.cursor()
        # For everything else, use the thread connection
        else:
            return getattr(self.thread_connection, name)


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
