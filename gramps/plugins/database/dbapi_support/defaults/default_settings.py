
## ----------------------------------------------
## Postgresql
## ----------------------------------------------

#from dbapi_support.postgresql import Postgresql
#dbapi = Postgresql(dbname='mydb', user='postgres',
#                   host='localhost', password='PASSWORD')

## ----------------------------------------------
## MySQL
## ----------------------------------------------

#from dbapi_support.mysql import MySQL
#dbapi = MySQL("localhost", "root", "PASSWORD", "mysqldb",
#              charset='utf8', use_unicode=True)

## ----------------------------------------------
## Sqlite
## ----------------------------------------------

from dbapi_support.sqlite import Sqlite
path_to_db = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'sqlite.db')
dbapi = Sqlite(path_to_db)
