import os
import sqlite3

sqlite3.paramstyle = 'qmark'

class Sqlite(object):
    def __init__(self, *args, **kwargs):
        self.connection = sqlite3.connect(*args, **kwargs)
        self.queries = {}

    def execute(self, *args, **kwargs):
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
