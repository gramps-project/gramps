import MySQLdb

MySQLdb.paramstyle = 'qmark' ## Doesn't work

class MySQL(object):
    @classmethod
    def get_summary(cls):
        """
        Return a diction of information about this database
        backend.
        """
        summary = {
            "DB-API version": "2.0",
            "Database SQL type": cls.__name__,
            "Database SQL module": "MySQLdb",
            "Database SQL module version": ".".join([str(v) for v in MySQLdb.version_info]),
            "Database SQL module location": MySQLdb.__file__,
        }
        return summary

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
