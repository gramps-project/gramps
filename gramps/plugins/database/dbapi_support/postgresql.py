import pg8000

pg8000.paramstyle = 'qmark'

class Postgresql(object):
    def __init__(self, *args, **kwargs):
        self.connection = pg8000.connect(*args, **kwargs)

    def execute(self, *args, **kwargs):
        self.cursor = self.connection.cursor()
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
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except Exception as exc:
            self.connection.rollback()
            #print(str(exc))

    def close(self):
        self.connection.close()
