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
Backend for PostgreSQL database.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import psycopg2
import os
import re

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.plugins.db.dbapi.dbapi import DBAPI
from gramps.gen.utils.configmanager import ConfigManager
from gramps.gen.config import config
from gramps.gen.db.dbconst import ARRAYSIZE
from gramps.gen.db.exceptions import DbConnectionError
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

psycopg2.paramstyle = 'format'

#-------------------------------------------------------------------------
#
# PostgreSQL class
#
#-------------------------------------------------------------------------
class PostgreSQL(DBAPI):

    def get_summary(self):
        """
        Return a diction of information about this database
        backend.
        """
        summary = super().get_summary()
        summary.update({
            _("Database version"): psycopg2.__version__,
            _("Database module location"): psycopg2.__file__,
        })
        return summary

    def _initialize(self, directory):
        config_file = os.path.join(directory, 'settings.ini')
        config_mgr = ConfigManager(config_file)
        config_mgr.register('database.dbname', '')
        config_mgr.register('database.host', '')
        config_mgr.register('database.user', '')
        config_mgr.register('database.password', '')
        config_mgr.register('database.port', '')

        if not os.path.exists(config_file):
            name_file = os.path.join(directory, 'name.txt')
            with open(name_file, 'r', encoding='utf8') as file:
                dbname = file.readline().strip()
            config_mgr.set('database.dbname', dbname)
            config_mgr.set('database.host', config.get('database.host'))
            config_mgr.set('database.user', config.get('database.user'))
            config_mgr.set('database.password', config.get('database.password'))
            config_mgr.set('database.port', config.get('database.port'))
            config_mgr.save()

        config_mgr.load()

        dbkwargs = {}
        for key in config_mgr.get_section_settings('database'):
            dbkwargs[key] = config_mgr.get('database.' + key)

        try:
            self.dbapi = Connection(**dbkwargs)
        except psycopg2.OperationalError as msg:
            raise DbConnectionError(str(msg), config_file)


#-------------------------------------------------------------------------
#
# Connection class
#
#-------------------------------------------------------------------------
class Connection:

    def __init__(self, *args, **kwargs):
        self.__connection = psycopg2.connect(*args, **kwargs)
        self.__connection.autocommit = True
        self.__cursor = self.__connection.cursor()
        self.check_collation(glocale)

    def check_collation(self, locale):
        """
        Checks that a collation exists and if not creates it.

        :param locale: Locale to be checked.
        :param type: A GrampsLocale object.
        """
        # Duplicating system collations works, but to delete them the schema
        # must be specified, so get the current schema
        self.execute('SELECT current_schema()')
        current_schema, = self.fetchone()
        collation = locale.get_collation()
        self.execute('DROP COLLATION IF EXISTS "%s"."%s"'
                     % (current_schema, collation))
        self.execute('CREATE COLLATION "%s"'
                     "(LOCALE = '%s')" % (collation, locale.collation))

    def _hack_query(self, query):
        query = query.replace("?", "%s")
        query = query.replace("REGEXP", "~")
        query = query.replace("desc", "desc_")
        query = query.replace("BLOB", "bytea")
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
                              "WHERE table_name=%s;", [table])
        return self.fetchone()[0] != 0

    def close(self):
        self.__connection.close()

    def cursor(self):
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
        try:
            return self.__cursor.fetchmany()
        except:
            return None
