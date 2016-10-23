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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import MySQLdb
import re

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.db.dbconst import ARRAYSIZE

MySQLdb.paramstyle = 'qmark' ## Doesn't work

class MySQL:
    @classmethod
    def get_summary(cls):
        """
        Return a diction of information about this database
        backend.
        """
        summary = {
            "DB-API version": "2.0",
            "Database SQL type": cls.__name__,
            "Database SQL module": "MySQLdb",
            "Database SQL module version": ".".join([str(v) for v in MySQLdb.version_info]),
            "Database SQL module location": MySQLdb.__file__,
        }
        return summary

    def __init__(self, *args, **kwargs):
        self.__connection = MySQLdb.connect(*args, **kwargs)
        self.__connection.autocommit(True)
        self.__cursor = self.__connection.cursor()

    def _hack_query(self, query):
        ## Workaround: no qmark support:
        query = query.replace("?", "%s")
        query = query.replace("INTEGER", "INT")
        query = query.replace("REAL", "DOUBLE")
        query = query.replace("change", "change_")
        query = query.replace("desc", "desc_")
        query = query.replace(" long ", " long_ ")
        ## LIMIT offset, count
        ## count can be -1, for all
        ## LIMIT -1
        ## LIMIT offset, -1
        query = query.replace("LIMIT -1",
                              "LIMIT 18446744073709551615") ##
        match = re.match(".* LIMIT (.*), (.*) ", query)
        if match and match.groups():
            offset, count = match.groups()
            if count == "-1":
                count = "18446744073709551615"
            query = re.sub("(.*) LIMIT (.*), (.*) ",
                           "\\1 LIMIT %s, %s " % (offset, count),
                           query)
        return query

    def execute(self, query, args=[]):
        query = self._hack_query(query)
        self.__cursor.execute(query, args)

    def fetchone(self):
        return self.__cursor.fetchone()

    def fetchall(self):
        return self.__cursor.fetchall()

    def commit(self):
        self.__cursor.execute("COMMIT;");

    def begin(self):
        self.__cursor.execute("BEGIN;");

    def rollback(self):
        self.__connection.rollback()

    def table_exists(self, table):
        self.__cursor.execute("SELECT COUNT(*) "
                              "FROM information_schema.tables "
                              "WHERE table_name='%s';" % table)
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
        return self.__cursor.fetchmany()
