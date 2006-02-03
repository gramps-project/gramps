
import gtk
import time
import bsddb
import cPickle
import logging
log = logging.getLogger(".")

from _PathCursor import PathCursor
from _ListCursor import ListCursor

from _FastModel import FastModel
import RelLib


class PersonListModel(FastModel):
    """Provides a fast model interface to the Person table.
    """
        
    def __init__(self,db):
        FastModel.__init__(self,db)

    def _get_table(self,db):
        return db.surnames

    def _get_cursor(self,db):
        return ListCursor(db.surnames.cursor())

    def _get_object_class(self,db):
        return RelLib.Person

    def _get_length(self,db):
        return self._table.stat()['ndata']
    
    def on_get_flags(self):
        return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST
