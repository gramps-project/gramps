import MySQLdb

MySQLdb.paramstyle = 'qmark' ## Doesn't work

class MySQL(object):
    def __init__(self, *args, **kwargs):
        self.connection = MySQLdb.connect(*args, **kwargs)

    def execute(self, query, args=[]):
        ## Workaround: no qmark support
        query = query.replace("?", "%s")
        self.cursor = self.connection.cursor()
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
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except Exception as exc:
            self.connection.rollback()
            #print(str(exc))

    def close(self):
        self.connection.close()
