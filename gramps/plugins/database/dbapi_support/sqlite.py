import os
import sqlite3
import logging

sqlite3.paramstyle = 'qmark'

class Sqlite(object):
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(".sqlite")
        self.connection = sqlite3.connect(*args, **kwargs)
        self.cursor = self.connection.cursor()
        self.queries = {}

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
