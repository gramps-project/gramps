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
import json
import logging
import os
import re
import sqlite3

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db.dbconst import ARRAYSIZE
from gramps.gen.db.bizlogic import BusinessLogic
from gramps.plugins.db.dbapi.dbapi import DBAPI

_ = glocale.translation.gettext

sqlite3.paramstyle = "qmark"


# -------------------------------------------------------------------------
#
# SQLite class
#
# -------------------------------------------------------------------------
class SQLite(DBAPI, BusinessLogic):
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
                _("Database module version"): sqlite3.version,
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

    # -------------------------------------------------------
    # Fast sqlite-specific implementations, slow versions
    # in BusniessLogic. These are "underloads"
    # -------------------------------------------------------
    def get_father_mother_handles_from_family(self, handle=None, family=None):
        """ Get the father and mother handles given a family """
        if family:
            handle = family.handle
        self.dbapi.execute("SELECT JSON_EXTRACT(unblob, '$[2]', '$[3]') FROM family WHERE handle = ? limit 1;", [handle])
        row = self.dbapi.fetchone()
        if row:
            parent_list = json.loads(row[0])
            if parent_list:
                return parent_list[0], parent_list[1]
        return (None, None)

    def get_main_parents_family_handle_from_person(self, handle=None, person=None):
        """ Get the main parent's family handle given a person """
        if person:
            handle = person.handle
        self.dbapi.execute("SELECT JSON_EXTRACT(unblob, '$[9]') FROM person WHERE handle = ? limit 1;", [handle])
        row = self.dbapi.fetchone()
        parent_family_list = json.loads(row[0])
        if parent_family_list:
            return parent_family_list[0]

    def get_person_handle_from_gramps_id(self, gid):
        """
        Return the handle of the person having the given Gramps ID.
        """
        self.dbapi.execute("SELECT handle FROM person WHERE gramps_id = ? limit 1;", [gid])
        row = self.dbapi.fetchone()
        if row:
            return row[0]

    def get_father_mother_handles_from_primary_family_from_person(self, handle=None, person=None):
        """ Get the father and mother handle's from a person primary family """
        if person:
            handle = person.handle
        fam_handle = self.get_main_parents_family_handle_from_person(handle=handle)
        if fam_handle:
            f_handle, m_handle = self.get_father_mother_handles_from_family(handle=fam_handle)
            return (f_handle, m_handle)
        return (None, None)

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
