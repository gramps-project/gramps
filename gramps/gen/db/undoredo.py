#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015 Douglas S. Blank <doug.blank@gmail.com>
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
#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
import time
from collections import deque

class DbUndo(metaclass=ABCMeta):
    """
    Base class for the Gramps undo/redo manager.  Needs to be subclassed
    for use with a real backend.
    """

    __slots__ = ('undodb', 'db', 'undo_history_timestamp', 'undoq', 'redoq')

    def __init__(self, db):
        """
        Class constructor. Set up main instance variables
        """
        self.db = db
        self.undoq = deque()
        self.redoq = deque()
        self.undo_history_timestamp = time.time()

    def clear(self):
        """
        Clear the undo/redo list (but not the backing storage)
        """
        self.undoq.clear()
        self.redoq.clear()
        self.undo_history_timestamp = time.time()

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

    @abstractmethod
    def open(self, value):
        """
        Open the backing storage.  Needs to be overridden in the derived
        class.
        """

    @abstractmethod
    def close(self):
        """
        Close the backing storage.  Needs to be overridden in the derived
        class.
        """

    @abstractmethod
    def append(self, value):
        """
        Add a new entry on the end.  Needs to be overridden in the derived
        class.
        """

    @abstractmethod
    def __getitem__(self, index):
        """
        Returns an entry by index number.  Needs to be overridden in the
        derived class.
        """

    @abstractmethod
    def __setitem__(self, index, value):
        """
        Set an entry to a value.  Needs to be overridden in the derived class.
        """

    @abstractmethod
    def __len__(self):
        """
        Returns the number of entries.  Needs to be overridden in the derived
        class.
        """

    @abstractmethod
    def _redo(self, update_history):
        """
        """

    @abstractmethod
    def _undo(self, update_history):
        """
        """

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
        return self._undo(update_history)

    def redo(self, update_history=True):
        """
        Redo a previously committed, then undone, transaction
        """
        if self.db.readonly or self.redo_count == 0:
            return False
        return self._redo(update_history)

    undo_count = property(lambda self:len(self.undoq))
    redo_count = property(lambda self:len(self.redoq))
