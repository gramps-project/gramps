import time
from collections import deque

class DbUndo(object):
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
        pass

    def __redo(self, update_history=True):
        """
        Access the last undone transaction, and revert the data to the state 
        before the transaction was undone.
        """
        pass

    def __undo(self, db=None, update_history=True):
        """
        Access the last committed transaction, and revert the data to the 
        state before the transaction was committed.
        """
        pass

    undo_count = property(lambda self:len(self.undoq))
    redo_count = property(lambda self:len(self.redoq))
