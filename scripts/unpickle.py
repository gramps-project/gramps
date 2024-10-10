import os
os.environ["GRAMPS_RESOURCES"] = "/home/dsblank/gramps/gramps"

from gramps.gen.db.utils import open_database
import pickle
import json

db = open_database("Example")

###########################################################################
try:
    db.dbapi.execute("ALTER TABLE family ADD COLUMN unblob TEXT;")
    db.dbapi.commit()
except Exception:
    pass

db.dbapi.execute("SELECT handle from family;")
handles = [x[0] for x in db.dbapi.fetchall()]

for handle in handles:
    db.dbapi.execute("SELECT blob_data FROM family WHERE handle = ? limit 1;", [handle])
    row = db.dbapi.fetchone()
    unblob = json.dumps(pickle.loads(row[0]))
    db.dbapi.execute("UPDATE family SET unblob = ? where handle = ?;", [unblob, handle])
db.dbapi.commit()
###########################################################################
try:
    db.dbapi.execute("ALTER TABLE person ADD COLUMN unblob TEXT;")
except Exception:
    pass

db.dbapi.execute("SELECT handle from person;")
handles = [x[0] for x in db.dbapi.fetchall()]

for handle in handles:
    db.dbapi.execute("SELECT blob_data FROM person WHERE handle = ? limit 1;", [handle])
    row = db.dbapi.fetchone()
    unblob = json.dumps(pickle.loads(row[0]))
    db.dbapi.execute("UPDATE person SET unblob = ? where handle = ?;", [unblob, handle])
db.dbapi.commit()
db.close()
