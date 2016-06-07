#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  Gerald W. Britton
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
BSDDBTxn class: Wrapper for BSDDB transaction-oriented methods
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
import inspect
import os

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.db.dbconst import DBLOGNAME
_LOG = logging.getLogger(DBLOGNAME)

#-------------------------------------------------------------------------
#
# BSDDBTxn
#
#-------------------------------------------------------------------------

class BSDDBTxn:
    """
    Wrapper for BSDDB methods that set up and manage transactions.  Implements
    context management functionality allowing constructs like:

    with BSDDBTxn(env) as txn:
        DB.get(txn=txn)
        DB.put(txn=txn)
        DB.delete(txn=txn)

    and other transaction-oriented DB access methods, where "env" is a
    BSDDB DBEnv object and "DB" is a BSDDB database object.

    Transactions are automatically begun when the "with" statement is executed
    and automatically committed when control flows off the end of the "with"
    statement context, either implicitly by reaching the end of the indentation
    level or explicity if a "return" statement is encountered or an exception
    is raised.
    """

    __slots__ = ['env', 'db', 'txn', 'parent']

    def __init__(self, env, db=None):
        """
        Initialize transaction instance
        """
        # Conditional on __debug__ because all that frame stuff may be slow
        if __debug__:
            caller_frame = inspect.stack()[1]
            _LOG.debug("        BSDDBTxn %s instantiated. Called from file %s,"
                       " line %s, in %s" %
                       ((hex(id(self)),)+
                        (os.path.split(caller_frame[1])[1],)+
                        (tuple(caller_frame[i] for i in range(2, 4)))
                       )
                      )
        self.env = env
        self.db = db
        self.txn = None

    # Context manager methods

    def __enter__(self, parent=None, **kwargs):
        """
        Context manager entry method

        Begin the transaction
        """
        _LOG.debug("    BSDDBTxn %s entered" % hex(id(self)))
        self.txn = self.begin(parent, **kwargs)
        self.parent = parent
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit function

        Commit the transaction if no exception occurred
        """
        _LOG.debug("        BSDDBTxn %s exited" % hex(id(self)))
        if exc_type is not None:
            return False
        if self.txn:
            self.commit()
        return True

    # Methods implementing txn_ methods in DBEnv

    def begin(self, *args, **kwargs):
        """
        Create and begin a new transaction. A DBTxn object is returned
        """
        _LOG.debug("        BSDDBTxn %s begin" % hex(id(self)))
        _LOG.debug("        BSDDBTxn %s calls %s %s txn_begin" %
                   (hex(id(self)), self.env.__class__.__name__,
                    hex(id(self.env)))
                   )
        self.txn = self.env.txn_begin(*args, **kwargs)
        return self.txn

    def checkpoint(self, *args, **kwargs):
        """
        Flush the underlying memory pool, write a checkpoint record to the
        log and then flush the log
        """
        if self.env:
            self.env.txn_checkpoint(*args, **kwargs)

    def stat(self):
        """
        Return a dictionary of transaction statistics
        """
        if self.env:
            return self.env.txn_stat()

    def recover(self):
        """
        Returns a list of tuples (GID, TXN) of transactions prepared but
        still unresolved
        """
        if self.env:
            return self.env.txn_recover()

    # Methods implementing DBTxn methods

    def abort(self):
        """
        Abort the transaction
        """
        if self.txn:
            self.txn.abort()
            self.txn = None

    def commit(self, flags=0):
        """
        End the transaction, committing any changes to the databases
        """
        _LOG.debug("        BSDDBTxn %s commit" % hex(id(self)))
        if self.txn:
            self.txn.commit(flags)
            self.txn = None

    def id(self):
        """
        Return the unique transaction id associated with the specified
        transaction
        """
        if self.txn:
            return self.txn.id()

    def prepare(self, gid):
        """
        Initiate the beginning of a two-phase commit
        """
        if self.txn:
            self.txn.prepare(gid)

    def discard(self):
        """
        Release all the per-process resources associated with the specified
        transaction, neither committing nor aborting the transaction
        """
        if self.txn:
            self.txn.discard()
            self.txn = None

    # Methods implementing DB methods within the transaction context

    def get(self, key, default=None, txn=None, **kwargs):
        """
        Returns the data object associated with key
        """
        return self.db.get(key, default, txn or self.txn, **kwargs)

    def pget(self, key, default=None, txn=None, **kwargs):
        """
        Returns the primary key, given the secondary one, and associated data
        """
        return self.db.pget(key, default, txn or self.txn, **kwargs)

    def put(self, key, data, txn=None, **kwargs):
        """
        Stores the key/data pair in the database
        """
        return self.db.put(key, data, txn or self.txn, **kwargs)

    def delete(self, key, txn=None, **kwargs):
        """
        Removes a key/data pair from the database
        """
        self.db.delete(key, txn or self.txn, **kwargs)

# test code
if __name__ == "__main__":
    print("1")
    from bsddb3 import db, dbshelve
    print("2")
    x = db.DBEnv()
    print("3")
    x.open('/tmp', db.DB_CREATE | db.DB_PRIVATE |\
                         db.DB_INIT_MPOOL |\
                         db.DB_INIT_LOG | db.DB_INIT_TXN)
    print("4")
    d = dbshelve.DBShelf(x)
    print("5")
    #from tran import BSDDBTxn as T
    print("6")
    T = BSDDBTxn
    with T(x) as tx:
        print("stat", tx.stat())
        print("id", tx.id())
        tx.checkpoint()
