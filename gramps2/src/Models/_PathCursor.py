
import cPickle
import logging
log = logging.getLogger(".")

class PathCursor(object):
    """
    Provides a wrapper around the cursor class that provides fast
    traversal using treeview paths.

    It keeps track of the current index that the cursor is pointing
    at by using a two stage index. The first element of the index is
    the sequence number of the record in the list of non_duplicate
    keys and the second element is the sequence number of the record
    within the duplicate keys to which it is a member.

    For example, with the following table indexed on Surname::

           Record Value      Index
           ============      =====
           
           Blogs, Jo         [0,0]
           Blogs, Jane       [0,1]
           Smith, Wilman     [1,0]
           Smith, John       [1,1]

    @ivar _index: The current index pointed to by the cursor.
    
    To speed up lookups the cursor is kept as close as possible to the
    likely next lookup and is moved using next_dup()/prev_dup() were ever
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
	self._index = [0,0]

    def next_nodup(self):
        """
        Move to the next non-duplcate record.
        """
	data = self._cursor.next_nodup()

        # If there was a next record that data will
        # not be None
        if data is not None:
            # Up date the index pointers so that
            # they point to the current record.
            self._index[0] += 1
            self._index[1] = 0
            
	return data

    def prev_nodup(self):
        """
        Move to the previous non-duplicate record.
        """
	data = self._cursor.prev_nodup()

        # If there was a next record that data will
        # not be None
        if data is not None:
            # Up date the index pointers so that
            # they point to the current record.
            self._index[0] -= 1
            self._index[1] = 0
            
	return data

    def next_dup(self):
        """
        Move to the next record with a duplicate key to the current record.
        """
	data = self._cursor.next_dup()

        # If there was a next record that data will
        # not be None
        if data is not None:
            # Update the secondary index.
            self._index[1] += 1            
            
	return data

    def has_children(self,path):
        """
        Check is the I{path} has any children.

        At the moment this method lies. There is no fast way to check
        if a given key has any duplicates and the TreeView insists on
        checking for every row. So this methods returns True if the
        path is 1 element long and False if it is more. This works
        for us because we show the first record in a set of duplicates
        as the first child. So all top level rows have at least one child.

        @param path: The path spec to check.
        @type path: A TreeView path.
        """
        
        if len(path) == 1:
            return True
        else:
            return False

    def get_n_children(self,path):
        """
        Return the number of children that the record at I{path} has.

        @param path: The path spec to check.
        @type path: A TreeView path.
        """

        # Only top level records can have children.
        if len(path) > 1:
            return 0

        # Fetch the primary record
        ret = self.lookup(path[0],use_cache=False)
        
        if ret is not None:
            # Now count the duplicates. We start at 1 because
            # we want to include the primary in the duplicates.
            count = 1
            ret = self.next_dup()
            while ret:
                ret = self.next_dup()
                count += 1
                self._index[1] += 1
                
            ret = count
        else:
            # If we failed to find the primary something is
            # wrong.
            ret = 0

        return ret
    
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
            ret = self._object_cache[index]['primary']

        # If the record is not in the cache or we are ignoring the
        # cache.
        else:
            
            # If the cursor points to a duplicate record
            # it will have a second index value of 0.            
            if self._index[1] != 0:
                # We need to move the cursor to the
                # first of a set of duplicates so that
                # we can then shift it to the required
                # index.
                self.next_nodup()

                
            # If the cursor points to the record we want
            # the first index will be equal to the
            # index required
            if index == self._index[0]:
                ret = self._cursor.current()

            # If the current cursor is behind the
            # requested index move it forward.
            elif index < self._index[0]:
                while index < self._index[0]:
                    ret = self.prev_nodup()
                    if ret is None:
                        log.warn("Failed to move back to index = %s" % (str(index)))
                        break

                # Because prev_nodup() leaves the cursor on
                # the last of a set of duplicates we need
                # to go up one further and then back down
                # again.
                ret = self.prev_nodup()
                if ret is None:
                    # We are at the start
                    self.top()
                    ret = self._cursor.current()
                else:
                    ret = self.next_nodup()

            # If the current cursor is in front of
            # requested index move it backward.
            else:
                while index > self._index[0]:
                    ret = self.next_nodup()
                    if ret is None:
                        log.warn("Failed to move forward to index = %s" % (str(index)))
                        break
                    
                ret = self._cursor.current()

            # when we have got the record save it in
            # the cache
            if ret is not None:
                ret = self._unpickle(ret)
                self._object_cache[index] = {'primary':ret}
            
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

        # If the path is for a primary record it will only
        # be 1 element long.
        if len(path) == 1:
            ret = self.lookup(path[0])

        # If it is for a secondary object we need to
        # traverse the duplicates.
        else:

            # First check to see if the record has already
            # been fetched.
            if self._object_cache.has_key(path[0]) and \
               self._object_cache[path[0]].has_key(path[1]):

                # return record from cache.
                ret = self._object_cache[path[0]][path[1]]
                
            else:
                # If we already in the duplicates for this
                # primary index then the first index will
                # be the same as the first element of the
                # path.
                if self._index[0] == path[0]:
                    # If the second elements match we are
                    # already looking at the correct record.
                    if self._index[1] == path[1]:
                        ret = self._cursor.current()

                    # If the cursor is in front we can
                    # move it back. Unfortunately there is no
                    # prev_dup() method so we have to
                    # reposition of the cursor at the start
                    # of the duplicates and step forward
                    else:
                        self.prev_nodup()
                        self.next_nodup()
                        ret = self.lookup(path[0],use_cache=False)

                        # If the request if not for the first duplicate
                        # we step forward the number of duplicates
                        # that have been requested.
                        count = 0
                        while count < path[1]:
                            ret = self.next_dup()
                            count += 1

                # If the primary elements do not match we
                # must move the cursor to the start of the
                # duplicates that are requested.
                else:
                    self.prev_nodup()
                    self.next_nodup()

                    ret = self.lookup(path[0],use_cache=False)

                    # If the request if not for the first duplicate
                    # we step forward the number of duplicates
                    # that have been requested.
                    count = 0
                    while count < path[1]:
                        ret = self.next_dup()
                        count += 1


                # Put the fetched record in the cache
                if ret is not None:
                    ret = self._unpickle(ret)
                    self._object_cache[path[0]][path[1]] = ret

        return ret

