
import gtk
import time
import bsddb
import cPickle
import logging
log = logging.getLogger(".")

from _PathCursor import PathCursor
from _ListCursor import ListCursor

from _FastFilterModel import FastFilterModel
import RelLib


class PersonFilterModel(FastFilterModel):
    """Provides a fast model interface to the Person table.
    """
        
    def __init__(self,db,apply_filter):
        FastFilterModel.__init__(self,db,apply_filter)


    def _get_object_class(self,db):
        return RelLib.Person

    
    def _get_fetch_func(self,db):
        return db.get_person_from_handle
