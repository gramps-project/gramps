
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


class PersonTreeModel(FastModel):
    """Provides a fast model interface to the Person table.
    """
        
    def __init__(self,db):
        FastModel.__init__(self,db)

    def _get_table(self,db):
        return db.surnames

    def _get_cursor(self,db):
        return PathCursor(db.surnames.cursor())

    def _get_object_class(self,db):
        return RelLib.Person

    def _get_length(self,db):
        return self._table.stat()['nkeys'] 
