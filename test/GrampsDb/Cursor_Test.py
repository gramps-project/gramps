import unittest
import logging
import os
import tempfile
import shutil
import time
import traceback
import sys
from bsddb import dbshelve, db

sys.path.append('../../src')

try:
    set()
except NameError:
    from sets import Set as set

import const
import RelLib

logger = logging.getLogger('Gramps.GrampsDbBase_Test')

from GrampsDbTestBase import GrampsDbBaseTest
import GrampsDb

class Data(object):

    def __init__(self,handle,surname,name):
        self.handle = handle
        self.surname = surname
        self.name = name

##     def __repr__(self):
##         return repr((self.handle,self.surname,self.name))
    
class CursorTest(unittest.TestCase):
    """Test the cursor handling."""

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self.full_name = os.path.join(self._tmpdir,'test.grdb')
        self.env = db.DBEnv()
        self.env.set_cachesize(0,0x2000000)
        self.env.set_lk_max_locks(25000)
        self.env.set_lk_max_objects(25000)
        self.env.set_flags(db.DB_LOG_AUTOREMOVE,1)  # clean up unused logs
        # The DB_PRIVATE flag must go if we ever move to multi-user setup
        env_flags = db.DB_CREATE|db.DB_RECOVER|db.DB_PRIVATE|\
                    db.DB_INIT_MPOOL|db.DB_INIT_LOCK|\
                    db.DB_INIT_LOG|db.DB_INIT_TXN

        env_name = "%s/env" % (self._tmpdir,)
        if not os.path.isdir(env_name):
            os.mkdir(env_name)
        self.env.open(env_name,env_flags)
        (self.person_map,self.surnames) = self._open_tables()
        
    def _open_tables(self):
        dbmap = dbshelve.DBShelf(self.env)
        dbmap.db.set_pagesize(16384)
        dbmap.open(self.full_name, 'person', db.DB_HASH,
                       db.DB_CREATE|db.DB_AUTO_COMMIT, 0666)
        person_map     = dbmap

        table_flags = db.DB_CREATE|db.DB_AUTO_COMMIT

        surnames = db.DB(self.env)
        surnames.set_flags(db.DB_DUP|db.DB_DUPSORT)
        surnames.open(self.full_name, "surnames", db.DB_BTREE,
                               flags=table_flags)
        
        def find_surname(key,data):
            return data.surname
        
        person_map.associate(surnames, find_surname, table_flags)

        return (person_map,surnames)
    
    def tearDown(self):
        shutil.rmtree(self._tmpdir)
        
    def test_simple_insert(self):
        """test insert and retrieve works."""

        data = Data(str(1),'surname1','name1')
        the_txn = self.env.txn_begin()
        self.person_map.put(data.handle,data,txn=the_txn)
        the_txn.commit()
        
        v = self.person_map.get(data.handle)

        assert v.handle == data.handle

    def test_insert_with_curor_closed(self):
        """test_insert_with_curor_closed"""
        
        cursor_txn = self.env.txn_begin()
        
        cursor = self.surnames.cursor(txn=cursor_txn)
        cursor.first()
        cursor.next()
        cursor.close()
        cursor_txn.commit()
        
        data = Data(str(2),'surname2','name2')
        the_txn = self.env.txn_begin()
        self.person_map.put(data.handle,data,txn=the_txn)
        the_txn.commit()
                
        v = self.person_map.get(data.handle)

        assert v.handle == data.handle

    def test_insert_with_curor_open(self):
        """test_insert_with_curor_open"""
        
        cursor_txn = self.env.txn_begin()
        cursor = self.surnames.cursor(txn=cursor_txn)
        cursor.first()
        cursor.next()
        
        data = Data(str(2),'surname2','name2')
        the_txn = self.env.txn_begin()
        self.person_map.put(data.handle,data,txn=the_txn)
        the_txn.commit()
        
        cursor.close()
        cursor_txn.commit()
        
        v = self.person_map.get(data.handle)

        assert v.handle == data.handle

    def xtest_insert_with_curor_open_and_db_open(self):
        """test_insert_with_curor_open_and_db_open"""

        (person2,surnames2) = self._open_tables()
        
        cursor_txn = self.env.txn_begin()
        cursor = surnames2.cursor(txn=cursor_txn)
        cursor.first()
        cursor.next()
        
        data = Data(str(2),'surname2','name2')
        the_txn = self.env.txn_begin()
        self.person_map.put(data.handle,data,txn=the_txn)
        the_txn.commit()
        
        cursor.close()
        cursor_txn.commit()
        
        v = self.person_map.get(data.handle)

        assert v.handle == data.handle

        
def testSuite():
    suite = unittest.makeSuite(CursorTest,'test')
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
