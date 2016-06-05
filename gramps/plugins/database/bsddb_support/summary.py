#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016 Douglas S. Blank <doug.blank@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

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
        with open(bdbversion_file) as vers_file:
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
