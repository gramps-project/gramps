import psycopg2

psycopg2.paramstyle = 'format'

class Postgresql(object):
    @classmethod
    def get_summary(cls):
        """
        Return a diction of information about this database
        backend.
        """
        summary = {
            "DB-API version": "2.0",
            "Database SQL type": cls.__name__,
            "Database SQL module": "psycopg2",
            "Database SQL module version": psycopg2.__version__,
            "Database SQL module location": psycopg2.__file__,
        }
        return summary

    def __init__(self, *args, **kwargs):
        self.connection = psycopg2.connect(*args, **kwargs)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def execute(self, *args, **kwargs):
        sql = args[0]
        sql = sql.replace("?", "%s")
        sql = sql.replace("REGEXP", "~")
        sql = sql.replace("desc", "desc_")
        if len(args) > 1:
            args = args[1]
        else:
            args = None
        try:
            self.cursor.execute(sql, args, **kwargs)
        except:
            self.cursor.execute("rollback")
            raise

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def begin(self):
        self.cursor.execute("BEGIN;")

    def commit(self):
        self.cursor.execute("COMMIT;")

    def rollback(self):
        self.connection.rollback()

    def try_execute(self, sql):
        sql = sql.replace("?", "%s")
        sql = sql.replace("BLOB", "bytea")
        sql = sql.replace("desc", "desc_")
        try:
            self.cursor.execute(sql)
        except Exception as exc:
            self.cursor.execute("rollback")
            #print("ERROR:", sql)
            #print(str(exc))

    def close(self):
        self.connection.close()
