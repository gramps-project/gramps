import os
import sqlite3
import logging
import re

sqlite3.paramstyle = 'qmark'

class Sqlite(object):
    @classmethod
    def get_summary(cls):
        """
        Return a diction of information about this database
        backend.
        """
        summary = {
            "DB-API version": "2.0",
            "Database SQL type": cls.__name__,
            "Database SQL module": "sqlite3",
            "Database SQL module version": sqlite3.version,
            "Database SQL module location": sqlite3.__file__,
        }
        return summary

    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(".sqlite")
        self.connection = sqlite3.connect(*args, **kwargs)
        self.cursor = self.connection.cursor()
        self.queries = {}
        self.connection.create_function("regexp", 2, regexp)

    def execute(self, *args, **kwargs):
        self.log.debug(args)
        self.cursor.execute(*args, **kwargs)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def begin(self):
        self.execute("BEGIN TRANSACTION;")

    def commit(self):
        self.log.debug("COMMIT;")
        self.connection.commit()

    def rollback(self):
        self.log.debug("ROLLBACK;")
        self.connection.rollback()

    def try_execute(self, sql):
        try:
            self.cursor.execute(sql)
        except Exception as exc:
            #print(str(exc))
            pass

    def close(self):
        self.log.debug("closing database...")
        self.connection.close()

def regexp(expr, value):
    return re.search(expr, value, re.MULTILINE) is not None
