#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-2016 Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2016      Nick Hall
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Backend for sqlite database.
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import sqlite3
import logging
import re

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.db.dbconst import ARRAYSIZE
from gramps.gen.const import GRAMPS_LOCALE as glocale

sqlite3.paramstyle = 'qmark'

#-------------------------------------------------------------------------
#
# Sqlite class
#
#-------------------------------------------------------------------------
class Sqlite:
    """
    The Sqlite class is an interface between the DBAPI class which is the Gramps
    backend for the DBAPI interface and the sqlite3 python module.
    """
    @classmethod
    def get_summary(cls):
        """
        Return a dictionary of information about this database backend.
        """
        summary = {
            "DB-API version": "2.0",
            "Database SQL type": cls.__name__,
            "Database SQL module": "sqlite3",
            "Database SQL Python module version": sqlite3.version,
            "Database SQL module version": sqlite3.sqlite_version,
            "Database SQL module location": sqlite3.__file__,
        }
        return summary

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
        self.__connection.create_collation("glocale", glocale.strcoll)
        self.__connection.create_function("regexp", 2, regexp)

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
        self.execute("SELECT COUNT(*) "
                     "FROM sqlite_master "
                     "WHERE type='table' AND name='%s';" % table)
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


#-------------------------------------------------------------------------
#
# Cursor class
#
#-------------------------------------------------------------------------
class Cursor:
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
