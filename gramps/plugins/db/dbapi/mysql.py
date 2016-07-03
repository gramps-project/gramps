#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-2016 Douglas S. Blank <doug.blank@gmail.com>
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

import MySQLdb
import re

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
        self.connection = MySQLdb.connect(*args, **kwargs)
        self.connection.autocommit(True)
        self.cursor = self.connection.cursor()

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
        self.cursor.execute(query, args)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.cursor.execute("COMMIT;");

    def begin(self):
        self.cursor.execute("BEGIN;");

    def rollback(self):
        self.connection.rollback()

    def try_execute(self, sql):
        query = self._hack_query(sql)
        try:
            self.cursor.execute(sql)
        except Exception as exc:
            pass
            #print(str(exc))

    def close(self):
        self.connection.close()
