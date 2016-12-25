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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import psycopg2
import re
import os

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.db.dbconst import ARRAYSIZE

psycopg2.paramstyle = 'format'

class Postgresql:
    @classmethod
    def get_summary(cls):
        """
        Return a diction of information about this database
        backend.
        """
        summary = {
            "DB-API version": "2.0",
            "Database SQL type": cls.__name__,
            "Database SQL module": "psycopg2",
            "Database SQL module version": psycopg2.__version__,
            "Database SQL module location": psycopg2.__file__,
        }
        return summary

    def __init__(self, *args, **kwargs):
        self.__connection = psycopg2.connect(*args, **kwargs)
        self.__connection.autocommit = True
        self.__cursor = self.__connection.cursor()
        locale = os.environ.get('LANG', 'en_US.utf8')
        self.execute("DROP COLLTAION IF EXISTS glocale")
        self.execute("CREATE COLLATION glocale (LOCALE = '%s')" % locale)

    def _hack_query(self, query):
        query = query.replace("?", "%s")
        query = query.replace("REGEXP", "~")
        query = query.replace("desc", "desc_")
        ## LIMIT offset, count
        ## count can be -1, for all
        ## LIMIT -1
        ## LIMIT offset, -1
        query = query.replace("LIMIT -1",
                              "LIMIT all") ##
        match = re.match(".* LIMIT (.*), (.*) ", query)
        if match and match.groups():
            offset, count = match.groups()
            if count == "-1":
                count = "all"
            query = re.sub("(.*) LIMIT (.*), (.*) ",
                           "\\1 LIMIT %s OFFSET %s " % (count, offset),
                           query)
        return query

    def execute(self, *args, **kwargs):
        sql = self._hack_query(args[0])
        if len(args) > 1:
            args = args[1]
        else:
            args = None
        try:
            self.__cursor.execute(sql, args, **kwargs)
        except:
            self.__cursor.execute("rollback")
            raise

    def fetchone(self):
        try:
            return self.__cursor.fetchone()
        except:
            return None

    def fetchall(self):
        return self.__cursor.fetchall()

    def begin(self):
        self.__cursor.execute("BEGIN;")

    def commit(self):
        self.__cursor.execute("COMMIT;")

    def rollback(self):
        self.__connection.rollback()

    def table_exists(self, table):
        self.__cursor.execute("SELECT COUNT(*) "
                              "FROM information_schema.tables "
                              "WHERE table_name=?;", [table])
        return self.fetchone()[0] != 0

    def close(self):
        self.__connection.close()

    def cursor(self):
        return Cursor(self.__connection)


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
        try:
            return self.__cursor.fetchmany()
        except:
            return None
