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
import threading
import time

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


# -------------------------------------------------------------------------
#
# Connection Pool class
#
# -------------------------------------------------------------------------
class ConnectionPool:
    """
    A simple connection pool for SQLite connections.
    """

    def __init__(self, db_path, max_connections=5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = []
        self.in_use = set()
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def get_connection(self):
        """
        Get a connection from the pool.
        """
        with self.lock:
            # Return an available connection if any
            for conn in self.connections:
                if conn not in self.in_use:
                    self.in_use.add(conn)
                    return conn

            # Create a new connection if under limit
            if len(self.connections) < self.max_connections:
                conn = Connection(self.db_path)
                self.connections.append(conn)
                self.in_use.add(conn)
                return conn

            # Wait for a connection to become available
            while True:
                for conn in self.connections:
                    if conn not in self.in_use:
                        self.in_use.add(conn)
                        return conn
                # Wait for a connection to be returned to the pool
                self.condition.wait()

    def return_connection(self, connection):
        """
        Return a connection to the pool.
        """
        with self.lock:
            if connection in self.in_use:
                self.in_use.remove(connection)
                # Notify waiting threads that a connection is available
                self.condition.notify()

    def close_all(self):
        """
        Close all connections in the pool.
        """
        with self.lock:
            for conn in self.connections:
                conn.close()
            self.connections.clear()
            self.in_use.clear()


# -------------------------------------------------------------------------
#
# SQLite class
#
# -------------------------------------------------------------------------
class SQLite(DBAPI):
    """
    SQLite interface.
    """
    
    def optimize_database(self):
        """
        SQLite-specific database optimization including VACUUM.
        """
        # Call parent class optimization first
        super().optimize_database()
        
        # SQLite-specific optimizations
        try:
            self.dbapi.execute("VACUUM;")
            self.dbapi.commit()
        except Exception as e:
            # VACUUM might fail if there are active connections
            self.log.warning(f"Could not VACUUM database: {e}")

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
        if directory == ":memory:":
            path_to_db = ":memory:"
        else:
            path_to_db = os.path.join(directory, "sqlite.db")
        self.dbapi = Connection(path_to_db)


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

    def __init__(self, *args, **kwargs):
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
        self.__cursor = self.__connection.cursor()

        # Performance optimizations
        self.__connection.execute("PRAGMA journal_mode = WAL;")
        self.__connection.execute("PRAGMA synchronous = NORMAL;")
        self.__connection.execute("PRAGMA cache_size = -64000;")  # 64MB cache
        self.__connection.execute("PRAGMA temp_store = MEMORY;")
        self.__connection.execute("PRAGMA mmap_size = 268435456;")  # 256MB mmap
        # PRAGMA page_size only affects new databases. For existing databases, this has no effect.
        # See https://www.sqlite.org/pragma.html#pragma_page_size
        db_path = None
        if args and isinstance(args[0], str) and args[0] != ":memory:":
            db_path = args[0]
        if db_path and not os.path.exists(db_path):
            self.__connection.execute("PRAGMA page_size = 4096;")
        else:
            self.log.warning(
                "PRAGMA page_size has no effect on existing databases. "
                "To change the page size, you must VACUUM the database after setting the PRAGMA."
            )
        self.__connection.execute("PRAGMA auto_vacuum = INCREMENTAL;")
        self.__connection.execute("PRAGMA incremental_vacuum = 1000;")

        self.__connection.create_function("regexp", 2, regexp)
        self.__collations = []
        self.__tmap = str.maketrans("-.@=;", "_____")
        self.check_collation(glocale)

        # Prepare common statements for better performance
        self.__prepared_statements = {}
        self._prepare_common_statements()

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

    def _prepare_common_statements(self):
        """
        Prepare commonly used SQL statements for better performance.
        """
        # Person queries - store the SQL strings for later use
        self.__prepared_statements["get_person_by_handle"] = (
            "SELECT * FROM person WHERE handle = ?"
        )
        self.__prepared_statements["get_person_by_gramps_id"] = (
            "SELECT * FROM person WHERE gramps_id = ?"
        )
        self.__prepared_statements["get_persons_by_surname"] = (
            "SELECT * FROM person WHERE surname = ? ORDER BY given_name"
        )

        # Family queries
        self.__prepared_statements["get_family_by_handle"] = (
            "SELECT * FROM family WHERE handle = ?"
        )
        self.__prepared_statements["get_families_by_parent"] = (
            "SELECT * FROM family WHERE father_handle = ? OR mother_handle = ?"
        )

        # Reference queries
        self.__prepared_statements["get_references_by_handle"] = (
            "SELECT * FROM reference WHERE obj_handle = ?"
        )
        self.__prepared_statements["get_references_by_ref_handle"] = (
            "SELECT * FROM reference WHERE ref_handle = ?"
        )

    def execute_prepared(self, statement_name, params=None):
        """
        Execute a prepared statement.

        :param statement_name: Name of the prepared statement
        :param params: Parameters for the statement
        :returns: Cursor with results
        """
        if statement_name not in self.__prepared_statements:
            raise ValueError(f"Prepared statement '{statement_name}' not found")

        sql = self.__prepared_statements[statement_name]
        if params:
            return self.execute(sql, params)
        else:
            return self.execute(sql)

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
