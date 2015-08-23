## Removed from clidbman.py
## specific to bsddb

from bsddb3 import dbshelve, db
import os

from gramps.gen.db import META, PERSON_TBL
from  gramps.gen.db.dbconst import BDBVERSFN

def get_dbdir_summary(dirpath, name):
    """
    Returns (people_count, bsddb_version, schema_version) of
    current DB.
    Returns ("Unknown", "Unknown", "Unknown") if invalid DB or other error.
    """

    bdbversion_file = os.path.join(dirpath, BDBVERSFN)
    if os.path.isfile(bdbversion_file):
        vers_file = open(bdbversion_file)
        bsddb_version = vers_file.readline().strip()
    else:
        return "Unknown", "Unknown", "Unknown"

    current_bsddb_version = str(db.version())
    if bsddb_version != current_bsddb_version:
        return "Unknown", bsddb_version, "Unknown"

    env = db.DBEnv()
    flags = db.DB_CREATE | db.DB_PRIVATE |\
        db.DB_INIT_MPOOL |\
        db.DB_INIT_LOG | db.DB_INIT_TXN
    try:
        env.open(dirpath, flags)
    except Exception as msg:
        LOG.warning("Error opening db environment for '%s': %s" %
                    (name, str(msg)))
        try:
            env.close()
        except Exception as msg:
            LOG.warning("Error closing db environment for '%s': %s" %
                    (name, str(msg)))
        return "Unknown", bsddb_version, "Unknown"
    dbmap1 = dbshelve.DBShelf(env)
    fname = os.path.join(dirpath, META + ".db")
    try:
        dbmap1.open(fname, META, db.DB_HASH, db.DB_RDONLY)
    except:
        env.close()
        return "Unknown", bsddb_version, "Unknown"
    schema_version = dbmap1.get(b'version', default=None)
    dbmap1.close()
    dbmap2 = dbshelve.DBShelf(env)
    fname = os.path.join(dirpath, PERSON_TBL + ".db")
    try:
        dbmap2.open(fname, PERSON_TBL, db.DB_HASH, db.DB_RDONLY)
    except:
        env.close()
        return "Unknown", bsddb_version, schema_version
    count = len(dbmap2)
    dbmap2.close()
    env.close()
    return (count, bsddb_version, schema_version)
