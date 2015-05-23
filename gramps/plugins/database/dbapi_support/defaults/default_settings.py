import os
import sqlite3

path_to_db = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'sqlite.db')  
dbapi = sqlite3.connect(path_to_db)
dbapi.row_factory = sqlite3.Row # allows access by name
