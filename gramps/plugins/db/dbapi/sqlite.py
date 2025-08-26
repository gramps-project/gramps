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
import json
import os
import re
import sqlite3
from typing import Dict, Any, Optional, List

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

# TODO: put into a place that user can edit
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
}
ALLOWED_PRAGMAS = {
    "journal_mode": {"DELETE", "TRUNCATE", "PERSIST", "MEMORY", "WAL", "OFF"},
    "synchronous": {"OFF", "NORMAL", "FULL", "EXTRA", "0", "1", "2", "3"},
    "cache_size": re.compile(r"^-?\d+$"),
    "temp_store": {"DEFAULT", "FILE", "MEMORY", "0", "1", "2"},
    "page_size": re.compile(r"^\d+$"),
    "mmap_size": re.compile(r"^-?\d+$"),
    "foreign_keys": {"ON", "OFF", "1", "0"},
    "auto_vacuum": {"NONE", "FULL", "INCREMENTAL", "0", "1", "2"},
    "journal_size_limit": re.compile(r"^\d+$"),
}


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
        self._database_config = self._init_database_config(directory)
        if directory == ":memory:":
            path_to_db = ":memory:"
        else:
            path_to_db = os.path.join(directory, "sqlite.db")
        self.dbapi = Connection(path_to_db, pragmas=self.get_database_config("pragmas"))

    def _init_database_config(self, directory):
        """
        Load the database configuration from a config file in the given directory.
        If the config file does not exist, create it with default values.
        Returns the loaded configuration or the default configuration if not present.
        """
        if directory == ":memory:":
            return DEFAULT_DATABASE_CONFIG
        else:
            database_json_path = os.path.join(directory, "config.json")
            if os.path.exists(database_json_path):
                with open(database_json_path) as fp:
                    try:
                        return json.load(fp)
                    except (json.JSONDecodeError, ValueError) as e:
                        logging.error(
                            "Failed to load database config from '%s': %s. Falling back to default config.",
                            database_json_path,
                            e,
                        )
                        return DEFAULT_DATABASE_CONFIG
            else:
                try:
                    with open(database_json_path, "w") as fp:
                        json.dump(DEFAULT_DATABASE_CONFIG, fp)
                except OSError as e:
                    logging.error(
                        f"Failed to write default database config to {database_json_path}: {e}."
                    )
                return DEFAULT_DATABASE_CONFIG


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

    def __init__(self, *args, pragmas: Optional[Dict[str, str]] = None, **kwargs):
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
                if self._is_valid_pragma(key, value):
                    self.__connection.execute(f"PRAGMA {key} = {value};")
                else:
                    self.log.warning(
                        f"Skipped unsafe or invalid PRAGMA: {key} = {value}"
                    )
            self.__connection.execute("VACUUM;")
            self.__connection.execute("PRAGMA optimize;")

        self.__cursor = self.__connection.cursor()
        self.__connection.create_function("regexp", 2, regexp)
        self.__collations: List[str] = []
        self.__tmap = str.maketrans("-.@=;", "_____")
        self.check_collation(glocale)

    def _is_valid_pragma(self, key: str, value: str) -> bool:
        """
        Check to see if the key and value are valid.
        """
        if key not in ALLOWED_PRAGMAS:
            return False

        allowed = ALLOWED_PRAGMAS[key]
        if isinstance(allowed, set):
            return str(value).upper() in allowed
        elif isinstance(allowed, re.Pattern):
            return allowed.match(str(value)) is not None
        return False

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
