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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Exports the DbTxn class for managing Gramps transactions and the undo
database.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import pickle
import logging
from collections import defaultdict
import time
import inspect
import os

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .dbconst import DBLOGNAME

_LOG = logging.getLogger(DBLOGNAME)


# -------------------------------------------------------------------------
#
# Gramps transaction class
#
# -------------------------------------------------------------------------
class DbTxn(defaultdict):
    """
    Define a group of database commits that define a single logical operation.
    """

    __slots__ = (
        "msg",
        "commitdb",
        "db",
        "batch",
        "first",
        "last",
        "timestamp",
        "__dict__",
    )

    def __enter__(self):
        """
        Context manager entry method
        """
        _LOG.debug("    DbTxn %s entered" % hex(id(self)))
        self.start_time = time.time()
        self.db.transaction_begin(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit method
        """
        if exc_type is None:
            self.db.transaction_commit(self)
        else:
            self.db.transaction_abort(self)

        elapsed_time = time.time() - self.start_time
        if __debug__ and _LOG.isEnabledFor(logging.DEBUG):
            frame = inspect.currentframe()
            c_frame = frame.f_back
            c_code = c_frame.f_code
            _LOG.debug(
                "    **** DbTxn %s exited. Called from file %s, "
                "line %s, in %s **** %.2f seconds",
                hex(id(self)),
                c_code.co_filename,
                c_frame.f_lineno,
                c_code.co_name,
                elapsed_time,
            )

        return False

    def __init__(self, msg, grampsdb, batch=False, **kwargs):
        """
        Create a new transaction.

        The grampsdb should have transaction_begin/commit/abort methods, and
        a get_undodb method to store undo actions.

        A Transaction instance can be created directly, but it is advised to
        use a context to do this. Like this the user must not worry about
        calling the transaction_xx methods on the database.

        The grampsdb parameter is a reference to the DbWrite object to which
        this transaction will be applied.
        grampsdb.get_undodb() should return a list-like interface that
        stores the commit data. This could be a simple list, or a RECNO-style
        database object.

        The data structure used to handle the transactions (see the add method)
        is a Python dictionary where:

        key = (object type, transaction type) where:
            object type = the numeric type of an object. These are
                          defined as PERSON_KEY = 0, FAMILY_KEY = 1, etc.
                          as imported from dbconst.
            transaction type = a numeric representation of the type of
                          transaction: TXNADD = 0, TXNUPD = 1, TXNDEL = 2

        data = Python list where:
            list element = (handle, data) where:
                handle = handle (database key) of the object in the transaction
                data = pickled representation of the object
        """

        # Conditional on __debug__ because all that frame stuff may be slow
        if __debug__ and _LOG.isEnabledFor(logging.DEBUG):
            caller_frame = inspect.stack()[1]
            # If the call comes from gramps.gen.db.generic.DbGenericTxn.__init__
            # then it is just a dummy redirect, so we need to go back another
            # frame to get any real information. The test does not accurately
            # check this, but seems to be good enough for the current diagnostic
            # purposes.
            if (
                os.path.split(caller_frame[1])[1] == "generic.py"
                and caller_frame[3] == "__init__"
            ):
                caller_frame = inspect.stack()[2]
            _LOG.debug(
                "%sDbTxn %s instantiated for '%s'. Called from file %s, "
                "line %s, in %s"
                % (
                    ("Batch " if batch else "",)
                    + (hex(id(self)),)
                    + (msg,)
                    + (os.path.split(caller_frame[1])[1],)
                    + (tuple(caller_frame[i] for i in range(2, 4)))
                )
            )
        defaultdict.__init__(self, list, {})

        self.msg = msg
        self.commitdb = grampsdb.get_undodb()
        self.db = grampsdb
        self.batch = batch
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.first = None
        self.last = None
        self.timestamp = 0

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
            pickle.dumps((obj_type, trans_type, handle, old_data, new_data), 1)
        )
        if self.last is None:
            self.last = len(self.commitdb) - 1
        if self.first is None:
            self.first = self.last
        _LOG.debug("added to trans: %d %d %s" % (obj_type, trans_type, handle))
        self[(obj_type, trans_type)] += [(handle, new_data)]
        return

    def get_recnos(self, reverse=False):
        """
        Return a list of record numbers associated with the transaction.

        While the list is an arbitrary index of integers, it can be used
        to indicate record numbers for a database.
        """

        if self.first is None or self.last is None:
            return []
        if not reverse:
            return range(self.first, self.last + 1)
        else:
            return range(self.last, self.first - 1, -1)

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
