import MySQLdb

MySQLdb.paramstyle = 'qmark' ## Doesn't work

class MySQL(object):
    def __init__(self, *args, **kwargs):
        self.connection = MySQLdb.connect(*args, **kwargs)
        self.cursor = self.connection.cursor()

    def execute(self, query, args=[]):
        ## Workaround: no qmark support
        query = query.replace("?", "%s")
        self.cursor.execute(query, args)

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
            self.cursor.execute(sql)
        except Exception as exc:
            pass
            #print(str(exc))

    def close(self):
        self.connection.close()
