#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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

"""
Exports the DbTxn class for managing Gramps transactions and the undo
database.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from __future__ import with_statement
import cPickle as pickle
from bsddb import dbshelve, db
import logging

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.db.dbconst import *
from gen.db import BSDDBTxn
import Errors

_LOG = logging.getLogger(DBLOGNAME)

#-------------------------------------------------------------------------
#
# Gramps transaction class
#
#-------------------------------------------------------------------------
class DbTxn(dict):
    """
    Define a group of database commits that define a single logical operation.
    This class should not be used directly, but subclassed to reference a real
    database
    """

    __slots__ = ('msg', 'commitdb', 'db', 'first',
                 'last', 'timestamp', 'db_maps')

    def get_db_txn(self, value):
        """
        Return a transaction object from the database
        """
        raise NotImplementedError

    def __enter__(self):
        """
        Context manager entry method
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit method
        """
        if exc_type is None:
            self.commit()
        return exc_type is None
    
    def __init__(self, msg, commitdb, grampsdb):
        """
        Create a new transaction. 
        
        A Transaction instance should not be created directly, but by the 
        DbBase class or classes derived from DbBase. The commitdb 
        parameter is a list-like interface that stores the commit data. This 
        could be a simple list, or a RECNO-style database object.  The grampsdb
        parameter is a reference to the DbWrite object to which this
        transaction will be applied.

        The data structure used to handle the transactions is a Python
        dictionary where:
        
        key = (object type, transaction type) where:
            object type = the numeric type of an object. These are
                          defined as PERSON_KEY = 0, FAMILY_KEY = 1, etc.
                          as imported from dbconst.
            transaction type = a numeric representation of the type of
                          transaction: TXNADD = 0, TXNUPD = 1, TXNDEL = 2
        
        data = Python list where:
            list element = (handle, data) where:
                handle = handle (database key) of the object in the transaction
                data   = pickled representation of the object        
        """

        super(DbTxn, self).__init__({})

        self.msg = msg
        self.commitdb = commitdb
        self.db = grampsdb
        self.first = None
        self.last = None
        self.timestamp = 0

        # Dictionary to enable table-driven logic in the class
        self.db_maps = {
                    PERSON_KEY:     (self.db.person_map, 'person'),
                    FAMILY_KEY:     (self.db.family_map, 'family'),
                    EVENT_KEY:      (self.db.event_map,  'event'),
                    SOURCE_KEY:     (self.db.source_map, 'source'),
                    PLACE_KEY:      (self.db.place_map,  'place'),
                    MEDIA_KEY:      (self.db.media_map,  'media'),
                    REPOSITORY_KEY: (self.db.repository_map, 'repository'),
                    #REFERENCE_KEY: (self.db.reference_map, 'reference'),
                    NOTE_KEY:       (self.db.note_map,   'note'),
                  }

    def get_description(self):
        """
        Return the text string that describes the logical operation performed 
        by the Transaction.
        """
        return self.msg

    def set_description(self, msg):
        """
        Set the text string that describes the logical operation performed by 
        the Transaction.
        """
        self.msg = msg

    def add(self, obj_type, trans_type, handle, old_data, new_data):
        """
        Add a commit operation to the Transaction. 
        
        The obj_type is a constant that indicates what type of PrimaryObject 
        is being added. The handle is the object's database handle, and the 
        data is the tuple returned by the object's serialize method.
        """
        self.last = self.commitdb.append(
            pickle.dumps((obj_type, trans_type, handle, old_data, new_data), 1))
        if self.last is None:
            self.last = len(self.commitdb) -1
        if self.first is None:
            self.first = self.last
        if (obj_type, trans_type) in self:
            self[(obj_type, trans_type)] += [(handle, new_data)]
        else:
            self[(obj_type, trans_type)] = [(handle, new_data)]

    def get_recnos(self, reverse=False):
        """
        Return a list of record numbers associated with the transaction.
        
        While the list is an arbitrary index of integers, it can be used
        to indicate record numbers for a database.
        """
        if not reverse:
            return xrange(self.first, self.last+1)
        else:
            return xrange(self.last, self.first-1, -1)

    def get_record(self, recno):
        """
        Return a tuple representing the PrimaryObject type, database handle
        for the PrimaryObject, and a tuple representing the data created by
        the object's serialize method.
        """
        return pickle.loads(self.commitdb[recno])

    def __len__(self):
        """
        Return the number of commits associated with the Transaction.
        """
        if self.first is None or self.last is None:
            return 0
        return self.last - self.first + 1

    def commit(self, msg=None):
        """
        Commit the transaction to the assocated commit database.
        """
        if msg is not None:
            self.msg = msg

        if not len(self) or self.db.readonly:
            return        

        # Begin new database transaction
        txn = self.get_db_txn(self.db.env)
        self.db.txn = txn.begin()

        # Commit all add transactions to the database
        db_map = lambda key: self.db_maps[key][0]
        for (obj_type, trans_type), data in self.iteritems():
            if trans_type == TXNADD and obj_type in self.db_maps:
                for handle, new_data in data:
                    assert handle == str(handle)
                    db_map(obj_type).put(handle, new_data, txn=txn.txn)

        # Commit all update transactions to the database
        for (obj_type, trans_type), data in self.iteritems():
            if trans_type == TXNUPD and obj_type in self.db_maps:
                for handle, new_data in data:
                    assert handle == str(handle)
                    db_map(obj_type).put(handle, new_data, txn=txn.txn)

        # Before we commit delete transactions, emit signals as required

        # Loop through the data maps, emitting signals as required
        emit = self.__emit
        for obj_type, (m_, obj_name) in self.db_maps.iteritems():
            # Do an emit for each object and transaction type as required
            emit(obj_type, TXNADD, obj_name, '-add')
            emit(obj_type, TXNUPD, obj_name, '-update')
            emit(obj_type, TXNDEL, obj_name, '-delete')

        # Commit all delete transactions to the database
        for (obj_type, trans_type), data in self.iteritems():
            if trans_type == TXNDEL and obj_type in self.db_maps:
                for handle, n_ in data:
                    assert handle == str(handle)
                    db_map(obj_type).delete(handle, txn=txn.txn)

        # Add new reference keys as required
        db_map = self.db.reference_map
        if (REFERENCE_KEY, TXNADD) in self:
            for handle, new_data in self[(REFERENCE_KEY, TXNADD)]:
                assert handle == str(handle)
                db_map.put(handle, new_data, txn=txn.txn)

        # Delete old reference keys as required
        if (REFERENCE_KEY, TXNDEL) in self:
            for handle, none_ in self[(REFERENCE_KEY, TXNDEL)]:
                assert handle == str(handle)
                db_map.delete(handle, txn=txn.txn)

        # Commit database transaction
        txn.commit()
        self.db.txn = None
        self.clear()
        return

    # Define helper function to do the actual emits
    def __emit(self,obj_type, trans_type, obj, suffix):
        if (obj_type, trans_type) in self:
            handles = [handle for handle, data in
                            self[(obj_type, trans_type)]]
            if handles:
                self.db.emit(obj + suffix, (handles, ))

# Test functions

def testtxn():
    """
    Test suite
    """    
    class M(dict):
        """Fake database map with just two methods"""
        def put(self, key, data, txn=None):
            super(M, self).__setitem__(key, data)
        def delete(self, key, txn=None):
            super(M, self).__delitem__(key)

    class D:
        """Fake gramps database"""
        def __init__(self):
            self.person_map = M()
            self.family_map = M()
            self.source_map = M()
            self.event_map  = M()
            self.media_map  = M()
            self.place_map  = M()
            self.note_map   = M()
            self.repository_map = M()
            self.reference_map  = M()
            self.readonly = False
            self.env = None
        def emit(self, obj, value):
            pass

    class C(list):
        """ Fake commit database"""
        pass

    class G(DbTxn):
        """Derived transacton class"""
        def get_db_txn(self, env):
            return T()

    class T():
        """Fake DBMS transaction class"""
        def __init__(self):
            self.txn = None
        def begin(self):
            return self
        def commit(self):
            pass

    commitdb = C()
    grampsdb = D()
    trans = G("Test Transaction", commitdb, grampsdb)
    trans.add(0, TXNADD, '1', None, "data1")
    trans.add(0, TXNADD, '2', None, "data2")
    trans.add(0, TXNUPD, '2', None, "data3")
    trans.add(0, TXNDEL, '1', None, None)

    print trans
    print trans.get_description()
    print trans.set_description("new text")
    print trans.get_description()
    for i in trans.get_recnos():
        print trans.get_record(i)
    print list(trans.get_recnos())
    print list(trans.get_recnos(reverse=True))
    trans.commit("test")
    print grampsdb.person_map

if __name__ == '__main__':
    testtxn()
