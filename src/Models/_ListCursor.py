
import cPickle
import logging
log = logging.getLogger(".")

class ListCursor(object):
    """
    Provides a wrapper around the cursor class that provides fast
    traversal using treeview paths for models that are LISTONLY, i.e.
    they have no tree structure.

    It keeps track of the current index that the cursor is pointing
    at.
    
    @ivar _index: The current index pointed to by the cursor.
    
    To speed up lookups the cursor is kept as close as possible to the
    likely next lookup and is moved using next()/prev() were ever
    possible.

    @ivar _object_cache: A cache of previously fetched records. These are
    indexed by the values of the L{_index}.
    """
    
    def __init__(self,cursor):
        """
        @param cursor: The cursor used to fetch the records.
        @type cursor: An object supporting the cursor methods of a U{BSDB
        cursor<http://pybsddb.sourceforge.net/bsddb3.html>}.
        It must have a BTREE index type and DB_DUP to support duplicate
        records. It should probably also have DB_DUPSORT if you want to
        have sorted records.
        """
	self._cursor = cursor
        self._object_cache = {}

        self.top()


    def top(self):
	self._cursor.first()
	self._index = 0

    def next(self):
        """
        Move to the next record.
        """
	data = self._cursor.next()

        # If there was a next record that data will
        # not be None
        if data is not None:
            # Up date the index pointers so that
            # they point to the current record.
            self._index+= 1
            
	return data

    def prev(self):
        """
        Move to the previous record.
        """
	data = self._cursor.prev()

        # If there was a next record that data will
        # not be None
        if data is not None:
            # Up date the index pointers so that
            # they point to the current record.
            self._index -= 1
            
	return data


    def has_children(self,path):
        """
        This cursor is only for simple lists so no records have
        children.
        
        @param path: The path spec to check.
        @type path: A TreeView path.
        """
        
        return False

    def get_n_children(self,path):
        """
        Return the number of children that the record at I{path} has.

        @param path: The path spec to check.
        @type path: A TreeView path.
        """

        return 0
    
    def lookup(self,index,use_cache=True):
        """
        Lookup a primary record.

        @param index: The index of the primary record. This is its
        possition in the sequence of non_duplicate keys.
        @type index: int
        @para use_case: If B{True} the record will be looked up in the
        object cache and will be returned from there. This will not
        update the possition of the cursor. If B{False} the record will
        fetched from the cursor even if it is in the object cache and
        cursor will be left possitioned on the record.
        """

        # See if the record is in the cache.
        if self._object_cache.has_key(index) and use_cache is True:
            ret = self._object_cache[index]

        # If the record is not in the cache or we are ignoring the
        # cache.
        else:
            
            # If the cursor points to the record we want
            # the first index will be equal to the
            # index required
            if index == self._index:
                ret = self._cursor.current()

            # If the current cursor is behind the
            # requested index move it forward.
            elif index < self._index:
                while index < self._index:
                    ret = self.prev()
                    if ret is None:
                        log.warn("Failed to move back to index = %s" % (str(index)))
                        break

                ret = self._cursor.current()

            # If the current cursor is in front of
            # requested index move it backward.
            else:
                while index > self._index:
                    ret = self.next()
                    if ret is None:
                        log.warn("Failed to move forward to index = %s" % (str(index)))
                        break
                    
                ret = self._cursor.current()

            # when we have got the record save it in
            # the cache
            if ret is not None:
                ret = self._unpickle(ret)
                self._object_cache[index] = ret
            
	return ret

    def _unpickle(self,rec):
        """
        It appears that reading an object from a cursor does not
        automatically unpickle it. So this method provides
        a convenient way to unpickle the object.
        """
        if rec and type(rec[1]) == type(""):
            tmp = [rec[0],None]
            tmp[1] = cPickle.loads(rec[1])
            rec = tmp
        return rec

    def lookup_path(self,path):
        """
        Lookup a record from a patch specification.

        @param path: The path spec to check.
        @type path: A TreeView path.

        """
        return self.lookup(path[0])


