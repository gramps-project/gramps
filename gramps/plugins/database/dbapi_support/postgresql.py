import pg8000

pg8000.paramstyle = 'qmark'

class Postgresql(object):
    def __init__(self, *args, **kwargs):
        self.connection = pg8000.connect(*args, **kwargs)
        self.cursor = self.connection.cursor()

    def execute(self, *args, **kwargs):
        self.cursor.execute(*args, **kwargs)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def try_execute(self, sql):
        sql = sql.replace("BLOB", "bytea")
        try:
            self.cursor.execute(sql)
        except Exception as exc:
            pass
            #print(str(exc))

    def close(self):
        self.connection.close()
