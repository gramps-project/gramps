#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Exports the DbUndo class for managing Gramps transactions
undos and redos.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import time, os
import pickle
from collections import deque

try:
    from bsddb3 import db
except:
    # FIXME: make this more abstract to deal with other backends
    class db:
        DBRunRecoveryError = 0
        DBAccessError = 0
        DBPageNotFoundError = 0
        DBInvalidArgError = 0

from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.db.dbconst import *
from . import BSDDBTxn
from gramps.gen.errors import DbError

#-------------------------------------------------------------------------
#
# Local Constants
#
#-------------------------------------------------------------------------
DBERRS      = (db.DBRunRecoveryError, db.DBAccessError,
               db.DBPageNotFoundError, db.DBInvalidArgError)

_SIGBASE = ('person', 'family', 'source', 'event', 'media',
            'place', 'repository', 'reference', 'note', 'tag', 'citation')

#-------------------------------------------------------------------------
#
# DbUndo class
#
#-------------------------------------------------------------------------
class DbUndo:
    """
    Base class for the Gramps undo/redo manager.  Needs to be subclassed
    for use with a real backend.
    """

    __slots__ = ('undodb', 'db', 'mapbase', 'undo_history_timestamp',
                 'txn', 'undoq', 'redoq')

    def __init__(self, grampsdb):
        """
        Class constructor. Set up main instance variables
        """
        self.db = grampsdb
        self.undoq = deque()
        self.redoq = deque()
        self.undo_history_timestamp = time.time()
        self.txn = None
        # N.B. the databases have to be in the same order as the numbers in
        # xxx_KEY in gen/db/dbconst.py
        self.mapbase = (
                        self.db.person_map,
                        self.db.family_map,
                        self.db.source_map,
                        self.db.event_map,
                        self.db.media_map,
                        self.db.place_map,
                        self.db.repository_map,
                        self.db.reference_map,
                        self.db.note_map,
                        self.db.tag_map,
                        self.db.citation_map,
                        )

    def clear(self):
        """
        Clear the undo/redo list (but not the backing storage)
        """
        self.undoq.clear()
        self.redoq.clear()
        self.undo_history_timestamp = time.time()
        self.txn = None

    def __enter__(self, value):
        """
        Context manager method to establish the context
        """
        self.open(value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager method to finish the context
        """
        if exc_type is None:
            self.close()
        return exc_type is None

    def open(self, value):
        """
        Open the backing storage.  Needs to be overridden in the derived
        class.
        """
        raise NotImplementedError

    def close(self):
        """
        Close the backing storage.  Needs to be overridden in the derived
        class.
        """
        raise NotImplementedError

    def append(self, value):
        """
        Add a new entry on the end.  Needs to be overridden in the derived
        class.
        """
        raise NotImplementedError

    def __getitem__(self, index):
        """
        Returns an entry by index number.  Needs to be overridden in the
        derived class.
        """
        raise NotImplementedError

    def __setitem__(self, index, value):
        """
        Set an entry to a value.  Needs to be overridden in the derived class.
        """
        raise NotImplementedError

    def __len__(self):
        """
        Returns the number of entries.  Needs to be overridden in the derived
        class.
        """
        raise NotImplementedError

    def commit(self, txn, msg):
        """
        Commit the transaction to the undo/redo database.  "txn" should be
        an instance of Gramps transaction class
        """
        txn.set_description(msg)
        txn.timestamp = time.time()
        self.undoq.append(txn)

    def undo(self, update_history=True):
        """
        Undo a previously committed transaction
        """
        if self.db.readonly or self.undo_count == 0:
            return False
        return self.__undo(update_history)

    def redo(self, update_history=True):
        """
        Redo a previously committed, then undone, transaction
        """
        if self.db.readonly or self.redo_count == 0:
            return False
        return self.__redo(update_history)

    def undoredo(func):
        """
        Decorator function to wrap undo and redo operations within a bsddb
        transaction.  It also catches bsddb errors and raises an exception
        as appropriate
        """
        def try_(self, *args, **kwargs):
            try:
                with BSDDBTxn(self.db.env) as txn:
                    self.txn = self.db.txn = txn.txn
                    status = func(self, *args, **kwargs)
                    if not status:
                        txn.abort()
                    self.db.txn = None
                    return status

            except DBERRS as msg:
                self.db._log_error()
                raise DbError(msg)

        return try_

    @undoredo
    def __undo(self, update_history=True):
        """
        Access the last committed transaction, and revert the data to the
        state before the transaction was committed.
        """
        txn = self.undoq.pop()
        self.redoq.append(txn)
        transaction = txn
        db = self.db
        subitems = transaction.get_recnos(reverse=True)

        # Process all records in the transaction
        for record_id in subitems:
            (key, trans_type, handle, old_data, new_data) = \
                    pickle.loads(self.undodb[record_id])

            if key == REFERENCE_KEY:
                self.undo_reference(old_data, handle, self.mapbase[key])
            else:
                self.undo_data(old_data, handle, self.mapbase[key],
                                db.emit, _SIGBASE[key])
        # Notify listeners
        if db.undo_callback:
            if self.undo_count > 0:
                db.undo_callback(_("_Undo %s")
                                   % self.undoq[-1].get_description())
            else:
                db.undo_callback(None)

        if db.redo_callback:
            db.redo_callback(_("_Redo %s")
                                   % transaction.get_description())

        if update_history and db.undo_history_callback:
            db.undo_history_callback()
        return True

    @undoredo
    def __redo(self, db=None, update_history=True):
        """
        Access the last undone transaction, and revert the data to the state
        before the transaction was undone.
        """
        txn = self.redoq.pop()
        self.undoq.append(txn)
        transaction = txn
        db = self.db
        subitems = transaction.get_recnos()

        # Process all records in the transaction
        for record_id in subitems:
            (key, trans_type, handle, old_data, new_data) = \
                pickle.loads(self.undodb[record_id])

            if key == REFERENCE_KEY:
                self.undo_reference(new_data, handle, self.mapbase[key])
            else:
                self.undo_data(new_data, handle, self.mapbase[key],
                                    db.emit, _SIGBASE[key])
        # Notify listeners
        if db.undo_callback:
            db.undo_callback(_("_Undo %s")
                                   % transaction.get_description())

        if db.redo_callback:
            if self.redo_count > 1:
                new_transaction = self.redoq[-2]
                db.redo_callback(_("_Redo %s")
                                   % new_transaction.get_description())
            else:
                db.redo_callback(None)

        if update_history and db.undo_history_callback:
            db.undo_history_callback()
        return True

    def undo_reference(self, data, handle, db_map):
        """
        Helper method to undo a reference map entry
        """
        try:
            if data is None:
                db_map.delete(handle, txn=self.txn)
            else:
                db_map.put(handle, data, txn=self.txn)

        except DBERRS as msg:
            self.db._log_error()
            raise DbError(msg)

    def undo_data(self, data, handle, db_map, emit, signal_root):
        """
        Helper method to undo/redo the changes made
        """
        try:
            if data is None:
                emit(signal_root + '-delete', ([handle.decode('utf-8')],))
                db_map.delete(handle, txn=self.txn)
            else:
                ex_data = db_map.get(handle, txn=self.txn)
                if ex_data:
                    signal = signal_root + '-update'
                else:
                    signal = signal_root + '-add'
                db_map.put(handle, data, txn=self.txn)
                emit(signal, ([handle.decode('utf-8')],))

        except DBERRS as msg:
            self.db._log_error()
            raise DbError(msg)

    undo_count = property(lambda self:len(self.undoq))
    redo_count = property(lambda self:len(self.redoq))

class DbUndoList(DbUndo):
    """
    Implementation of the Gramps undo database using a Python list
    """
    def __init__(self, grampsdb):
        """
        Class constructor
        """
        super(DbUndoList, self).__init__(grampsdb)
        self.undodb = []

    def open(self):
        """
        A list does not need to be opened
        """
        pass

    def close(self):
        """
        Close the list by resetting it to empty
        """
        self.undodb = []
        self.clear()

    def append(self, value):
        """
        Add an entry on the end of the list
        """
        self.undodb.append(value)
        return len(self.undodb)-1

    def __getitem__(self, index):
        """
        Return an item at the specified index
        """
        return self.undodb[index]

    def __setitem__(self, index, value):
        """
        Set an item at the speficied index to the given value
        """
        self.undodb[index] = value

    def __iter__(self):
        """
        Iterator
        """
        for item in self.undodb:
            yield item

    def __len__(self):
        """
        Return number of entries in the list
        """
        return len(self.undodb)

class DbUndoBSDDB(DbUndo):
    """
    Class constructor for Gramps undo/redo database using a bsddb recno
    database as the backing store.
    """

    def __init__(self, grampsdb, path):
        """
        Class constructor
        """
        super(DbUndoBSDDB, self).__init__(grampsdb)
        self.undodb = db.DB()
        self.path = path

    def open(self):
        """
        Open the undo/redo database
        """
        path = self.path
        self.undodb.open(path, db.DB_RECNO, db.DB_CREATE)

    def close(self):
        """
        Close the undo/redo database
        """
        self.undodb.close()
        self.undodb = None
        self.mapbase = None
        self.db = None

        try:
            os.remove(self.path)
        except OSError:
            pass
        self.clear()

    def append(self, value):
        """
        Add an entry on the end of the database
        """
        return self.undodb.append(value)

    def __len__(self):
        """
        Returns the number of entries in the database
        """
        x = self.undodb.stat()['nkeys']
        y = len(self.undodb)
        assert x == y
        return x

    def __getitem__(self, index):
        """
        Returns the entry stored at the specified index
        """
        return self.undodb.get(index)

    def __setitem__(self, index, value):
        """
        Sets the entry stored at the specified index to the value given.
        """
        self.undodb.put(index, value)

    def __iter__(self):
        """
        Iterator
        """
        cursor = self.undodb.cursor()
        data = cursor.first()
        while data:
            yield data
            data = next(cursor)

def testundo():
    class T:
        def __init__(self):
            self.msg = ''
            self.timetstamp = 0
        def set_description(self, msg):
            self.msg = msg

    class D:
        def __init__(self):
            self.person_map = {}
            self.family_map = {}
            self.source_map = {}
            self.event_map  = {}
            self.media_map  = {}
            self.place_map  = {}
            self.note_map   = {}
            self.tag_map   = {}
            self.repository_map = {}
            self.reference_map  = {}

    print("list tests")
    undo = DbUndoList(D())
    print(undo.append('foo'))
    print(undo.append('bar'))
    print(undo[0])
    undo[0] = 'foobar'
    print(undo[0])
    print("len", len(undo))
    print("iter")
    for data in undo:
        print(data)
    print()
    print("bsddb tests")
    undo = DbUndoBSDDB(D(), '/tmp/testundo')
    undo.open()
    print(undo.append('foo'))
    print(undo.append('fo2'))
    print(undo.append('fo3'))
    print(undo[1])
    undo[1] = 'bar'
    print(undo[1])
    for data in undo:
        print(data)
    print("len", len(undo))

    print("test commit")
    undo.commit(T(), msg="test commit")
    undo.close()

if __name__ == '__main__':
    testundo()
