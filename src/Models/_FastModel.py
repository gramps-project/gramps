
import gtk
import time
import logging
log = logging.getLogger(".")



class FastModel(gtk.GenericTreeModel):
    """A I{gtk.GenericTreeModel} that links to a BSDB cursor to provide
    fast access to large tables. This is a pure virtual class, it must be
    subclassed and the subclass must implement L{_get_table}, L{_get_cursor} and
    L{_get_object_class}.

    The primary trick is to use the path specification as the tree iter.
    This means that when the TreeView asks for the iter for path=[1,2]
    we just echo it straight back. The onlt hard part is making sure that
    on_iter_next can do something sensible. It needs to know how many
    non duplicate records are in the table and then it can just accept the
    iter from the TreeView and increment it until it reaches the total
    length.

    The record itself is only fetched when its value is requested from
    on_get_value() and when the number of childen need to calculated. The
    cursor looks after the number of children calculation but it does require
    walking the list of duplicate keys, usually this is quite short.
    
    @ivar _db: handle of the Gramps DB
    @ivar _table: main table to be displayed
    @ivar _cursor: cursor for accessing the table.
    @ivar _obj_class: the class of the object that is being pulled from
    the database. This should probably be one of the primary RelLib
    classes.
    @ivar _num_children_cache: dictionary to hold the number of
    children for each primary record so that we don't have to look
    it up every time.
    @ivar _length: the number of primary (non duplicate) records.
    """
    
    column_types = (object,)
    
    def __init__(self,db):
        gtk.GenericTreeModel.__init__(self)

	self._db = db
	self._table = self._get_table(db)
	self._cursor = self._get_cursor(db)
        self._object_class = self._get_object_class(db)
        self._length = self._get_length(db)
        
        self._num_children_cache = {}

    # Helper methods to enable treeviews to tell if the model is
    # a tree or a list.

    def is_tree(self):
        return not self.is_list()

    def is_list(self):
        return self.on_get_flags()&gtk.TREE_MODEL_LIST_ONLY

    # Methods that must be implemented by subclasses.
    
    def _get_table(self,db):
        raise NotImplementedError("subclass of FastModel must implement _get_table")

    def _get_cursor(self,db):
        raise NotImplementedError("subclass of FastModel must implement _get_cursor")

    def _get_object_class(self,db):
        raise NotImplementedError("subclass of FastModel must implement _get_cursor")

    def _get_length(self,db):
        raise NotImplementedError("subclass of FastModel must implement _get_length")

    # GenericTreeModel methods
    
    def on_get_flags(self):
        return gtk.TREE_MODEL_ITERS_PERSIST
    
    def on_get_n_columns(self):
        return len(self.__class__.column_types)

    def on_get_column_type(self, index):
        return self.column_types[index]

    def on_get_iter(self, path):
        return list(path)

    def on_get_path(self, rowref):
        return list(rowref)

    def on_get_value(self, rowref, column):
        """
        Fetch the real object from the database.
        """

        # We only have one column
        if column is 0:
            obj = self._object_class()

            # Use the rowref as the path, because the iter methods
            # simple return the path as the iter it is safe to use
            # it here.
            record = self._cursor.lookup_path(rowref)

            # This should never return none, but there is a subtle bug
            # somewhere that I can't find and sometimes it does.
            if record is not None:
                obj.unserialize(record[1])
            else:
                log.warn("Failed to fetch a record from the cursor rowref = %s" % (str(rowref)))
                
            return (obj,rowref)

    def on_iter_next(self, rowref):
        """
        Calculate the next iter at the same level in the tree.
        """

        # The length of the rowref (i.e. the number of elements in the path)
        # tells us the level in the tree.
        if len(rowref) == 1:

            # If we are at the top of the tree we just increment the
            # first element in the iter until we reach the total length.
            if rowref[0]+1 >= self._length:
                ret = None
            else:
                ret = [rowref[0]+1,]
                
        elif len(rowref) == 2:

            # If we are at the second level we first check to see if we
            # have the number of children of this row already in the cache
            if not self._num_children_cache.has_key(rowref[0]):

                # If not calculate the number of children and put it in the cache.
                self._num_children_cache[rowref[0]] = self._cursor.get_n_children([rowref[0],])

            num_children = self._num_children_cache[rowref[0]]

            # Now increment the second element of the iter path until we
            # reach the number of children.
            if rowref[1]+1 < num_children:
                ret = [rowref[0],rowref[1]+1]
            else:
                ret = None
        else:
            # We only support two levels.
            ret = None

        return ret


    def on_iter_children(self, rowref):
        """
        Return the first child of the given rowref.
        """
        if rowref:
            # If the rowref is not none then we must be
            # asking for the second level so the first
            # child is always 0.
            ret = [rowref[0],0]
        else:
            # If rowref is None the we are asking for the
            # top level and that is always [0]
            ret = [0,]
            
        return ret

    def on_iter_has_child(self, rowref):
        if rowref:
            ret = self._cursor.has_children(rowref)
        else:
            ret = range(0,self._length)
        return ret

    def on_iter_n_children(self, rowref):        
        if rowref:
            # If we are at the second level we first check to see if we
            # have the number of children of this row already in the cache
            if not self._num_children_cache.has_key(rowref[0]):

                # If not calculate the number of children and put it in the cache.
                self._num_children_cache[rowref[0]] = self._cursor.get_n_children([rowref[0],])

            ret = self._num_children_cache[rowref[0]]
        else:
            ret = self._length
        return ret

    def on_iter_nth_child(self, parent, n):
        if parent:
            ret = [parent[0],n]
        else:
            ret = [n,]
        return ret

    def on_iter_parent(self, child):
        if len(child) > 1:
            return [child[0]]
        return None
