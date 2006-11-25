from bsddb import dbshelve, db
import os
import sys

sys.path.append('../src')
import const

env_name = os.path.expanduser(const.bsddbenv_dir)
if not os.path.isdir(env_name):
       os.mkdir(env_name)

env = db.DBEnv()
env.set_cachesize(0,0x2000000)
env.set_lk_max_locks(25000)
env.set_lk_max_objects(25000)
env.set_flags(db.DB_LOG_AUTOREMOVE,1)
env_flags = db.DB_CREATE|db.DB_RECOVER|db.DB_PRIVATE|\
            db.DB_INIT_MPOOL|db.DB_INIT_LOCK|\
            db.DB_INIT_LOG|db.DB_INIT_TXN|db.DB_THREAD
try:
    env.open(env_name,env_flags)
except db.DBRunRecoveryError, e:
    print "Exception: "
    print e
    env.remove(env_name)
    env.open(env_name,env_flags)
