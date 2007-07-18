# This file is derived from the GPL program "PyPE"
#
# Copyright (C) 2003-2006  Josiah Carlson
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Least recently used algorithm
"""

class Node:
    """
    Node to be stored in the LRU structure
    """
    def __init__(self, prev, value):
        self.prev = prev
        self.value = value
        self.next = None

class LRU: 
    """
    Implementation of a length-limited O(1) LRU cache
    """
    def __init__(self, count):
        self.count = max(count, 2)
        self.data = {}
        self.first = None
        self.last = None

    def __contains__(self, obj):
        """
        Returns True if the object is contained in the LRU
        """
        return obj in self.data

    def __getitem__(self, obj):
        """
        Returns item assocated with Obj
        """
        return self.data[obj].value[1]

    def __setitem__(self, obj, val):
        """
        Sets the item in the LRU, removing an old entry if needed
        """
        if obj in self.data:
            del self[obj]
        nobj = Node(self.last, (obj, val))
        if self.first is None:
            self.first = nobj
        if self.last:
            self.last.next = nobj
        self.last = nobj
        self.data[obj] = nobj
        if len(self.data) > self.count:
            if self.first == self.last:
                self.first = None
                self.last = None
                return
            lnk = self.first
            lnk.next.prev = None
            self.first = lnk.next
            lnk.next = None
            del self.data[lnk.value[0]]
            del lnk

    def __delitem__(self, obj):
        """
        Delete the object from the LRU
        """
        nobj = self.data[obj]
        if nobj.prev:
            nobj.prev.next = nobj.next
        else:
            self.first = nobj.next
        if nobj.next:
            nobj.next.prev = nobj.prev
        else:
            self.last = nobj.prev
        del self.data[obj]

    def __iter__(self):
        """
        Iterate over the LRU
        """
        cur = self.first
        while cur != None:
            cur2 = cur.next
            yield cur.value[1]
            cur = cur2
        raise StopIteration

    def iteritems(self):
        """
        Return items in the LRU using a generator
        """
        cur = self.first
        while cur != None:
            cur2 = cur.next
            yield cur.value
            cur = cur2
        raise StopIteration

    def iterkeys(self):
        """
        Return keys in the LRU using a generator
        """
        return iter(self.data)

    def itervalues(self):
        """
        Return items and keys in the LRU using a generator
        """
        for data in self.iteritems():
            yield data[1]

    def keys(self):
        """
        Return all keys
        """
        return [data[0] for data in self.iteritems()]

    def values(self):
        """
        Return all values
        """
        return [data[1] for data in self.iteritems()]

    def items(self):
        """
        Return all items
        """
        return [data[0] for data in self.iteritems()]
