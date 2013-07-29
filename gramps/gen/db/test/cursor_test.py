#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

# $Id$

import unittest
import os
import tempfile
import shutil
from bsddb import dbshelve, db

try:
    set()
except NameError:
    from sets import Set as set

class Data(object):

    def __init__(self, handle,surname, name):
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

        # clean up unused logs
        autoremove_flag = None
        autoremove_method = None
        for flag in ["DB_LOG_AUTO_REMOVE", "DB_LOG_AUTOREMOVE"]:
            if hasattr(db, flag):
                autoremove_flag = getattr(db, flag)
                break
        for method in ["log_set_config", "set_flags"]:
            if hasattr(self.env, method):
                autoremove_method = getattr(self.env, method)
                break
        if autoremove_method and autoremove_flag:
            autoremove_method(autoremove_flag, 1)

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
        self.person_map.put(data.handle, data, txn=the_txn)
        the_txn.commit()
        
        v = self.person_map.get(data.handle)

        self.assertEqual(v.handle, data.handle)

    def test_insert_with_curor_closed(self):
        """test_insert_with_curor_closed"""
        
        cursor_txn = self.env.txn_begin()
        
        cursor = self.surnames.cursor(txn=cursor_txn)
        cursor.first()
        cursor.next()
        cursor.close()
        cursor_txn.commit()
        
        data = Data(str(2), 'surname2', 'name2')
        the_txn = self.env.txn_begin()
        self.person_map.put(data.handle, data, txn=the_txn)
        the_txn.commit()
                
        v = self.person_map.get(data.handle)

        self.assertEqual(v.handle, data.handle)

    @unittest.skip("Insert expected to fail with open cursor")
    def test_insert_with_curor_open(self):
        """test_insert_with_curor_open"""
        
        cursor_txn = self.env.txn_begin()
        cursor = self.surnames.cursor(txn=cursor_txn)
        cursor.first()
        cursor.next()
        
        data = Data(str(2),'surname2', 'name2')
        the_txn = self.env.txn_begin()
        self.person_map.put(data.handle, data, txn=the_txn)
        the_txn.commit()
        
        cursor.close()
        cursor_txn.commit()
        
        v = self.person_map.get(data.handle)

        self.assertEqual(v.handle, data.handle)

    @unittest.skip("Insert expected to fail with open cursor")
    def test_insert_with_curor_open_and_db_open(self):
        """test_insert_with_curor_open_and_db_open"""

        (person2,surnames2) = self._open_tables()
        
        cursor_txn = self.env.txn_begin()
        cursor = surnames2.cursor(txn=cursor_txn)
        cursor.first()
        cursor.next()
        
        data = Data(str(2),'surname2', 'name2')
        the_txn = self.env.txn_begin()
        self.person_map.put(data.handle, data, txn=the_txn)
        the_txn.commit()
        
        cursor.close()
        cursor_txn.commit()
        
        v = self.person_map.get(data.handle)

        self.assertEqual(v.handle, data.handle)

        
def testSuite():
    suite = unittest.makeSuite(CursorTest, 'test')
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
