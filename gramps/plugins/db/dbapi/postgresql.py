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

import psycopg2
import re

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
        self.connection = psycopg2.connect(*args, **kwargs)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

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
            self.cursor.execute(sql, args, **kwargs)
        except:
            self.cursor.execute("rollback")
            raise

    def fetchone(self):
        try:
            return self.cursor.fetchone()
        except:
            return None

    def fetchall(self):
        return self.cursor.fetchall()

    def begin(self):
        self.cursor.execute("BEGIN;")

    def commit(self):
        self.cursor.execute("COMMIT;")

    def rollback(self):
        self.connection.rollback()

    def try_execute(self, sql):
        sql = self._hack_query(sql)
        sql = sql.replace("BLOB", "bytea")
        try:
            self.cursor.execute(sql)
        except Exception as exc:
            self.cursor.execute("rollback")
            #print("ERROR:", sql)
            #print(str(exc))

    def close(self):
        self.connection.close()
