import os
import sqlite3
import logging

sqlite3.paramstyle = 'qmark'

class Sqlite(object):
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(".sqlite")
        self.connection = sqlite3.connect(*args, **kwargs)
        self.queries = {}

    def execute(self, *args, **kwargs):
        self.log.debug(args)
        self.cursor = self.connection.execute(*args, **kwargs)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def try_execute(self, sql):
        try:
            self.connection.execute(sql)
        except Exception as exc:
            #print(str(exc))
            pass

    def close(self):
        self.connection.close()
