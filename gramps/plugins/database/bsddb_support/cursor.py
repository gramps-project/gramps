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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# gen/db/cursor.py

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from pickle import dumps, loads

try:
    from bsddb3 import db
except:
    # FIXME: make this more abstract to deal with other backends
    class db:
        DB_RMW = 0
        DB_FIRST = 0
        DB_LAST = 0
        DB_CURRENT = 0
        DB_PREV = 0
        DB_NEXT = 0

#-------------------------------------------------------------------------
#
# BsddbBaseCursor class
#
#-------------------------------------------------------------------------

class BsddbBaseCursor:
    """
    Provide a basic iterator that allows the user to cycle through
    the elements in a particular map.

    A cursor should never be directly instantiated. Instead, in should be
    created by the database class.

    A cursor should only be used for a single pass through the
    database. If multiple passes are needed, multiple cursors
    should be used.
    """

    def __init__(self, txn=None, update=False, commit=False):
        """
        Instantiate the object. Note, this method should be overridden in
        derived classes that properly set self.cursor and self.source
        """
        self.cursor = self.source = None
        self.txn = txn
        self._update = update
        self.commit = commit

    def __getattr__(self, name):
        """
        Return a method from the underlying cursor object, if it exists
        """
        return getattr(self.cursor, name)

    def __enter__(self):
        """
        Context manager enter method
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit method
        """
        self.close()
        if self.txn and self.commit:
            self.txn.commit()
        return exc_type is None

    def __iter__(self):
        """
        Iterator
        """

        data = self.first()
        _n = self.next      # Saved attribute lookup in the loop
        while data:
            yield data
            data = _n()

    def _get(_flags=0):
        """ Closure that returns a cursor get function """

        def get(self, flags=0, **kwargs):
            """
            Issue DBCursor get call (with DB_RMW flag if update requested)
            Return results to caller
            """
            data = self.cursor.get(
                        _flags | flags | (db.DB_RMW if self._update else 0),
                        **kwargs)

            try:
                return (data[0], loads(data[1])) if data else None
            except UnicodeDecodeError:
                #we need to assume we opened data in python3 saved in python2
                return (data[0], loads(data[1], encoding='utf-8')) if data else None

        return get

    # Use closure to define access methods

    current = _get(db.DB_CURRENT)
    first   = _get(db.DB_FIRST)
    ##python2 iterator
    next    = _get(db.DB_NEXT)
    ##python3 iterator
    __next__ = _get(db.DB_NEXT)
    last    = _get(db.DB_LAST)
    prev    = _get(db.DB_PREV)

    def update(self, key, data, flags=0, **kwargs):
        """
        Write the current key, data pair to the database.
        """
        self.cursor.put(key, dumps(data), flags=flags | db.DB_CURRENT,
                        **kwargs)
