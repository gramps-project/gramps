#
# Gramps - a GTK+/GNOME based genealogy program
#
# This file is derived from the GPL program "PyPE"
#
# Copyright (C) 2003-2006  Josiah Carlson
# Copyright (C) 2009       Gary Burton
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
        """
        Set count to 0 or 1 to disable.
        """
        self.count = count
        self.data = {}
        self.first = None
        self.last = None

    def __contains__(self, obj):
        """
        Return True if the object is contained in the LRU
        """
        return obj in self.data

    def __getitem__(self, obj):
        """
        Return item associated with Obj
        """
        return self.data[obj].value[1]

    def __setitem__(self, obj, val):
        """
        Set the item in the LRU, removing an old entry if needed
        """
        if self.count <= 1:  # Disabled
            return
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
            if lnk.value[0] in self.data:
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
        while cur is not None:
            cur2 = cur.next
            yield cur.value[1]
            cur = cur2
        raise StopIteration

    def iteritems(self):
        """
        Return items in the LRU using a generator
        """
        cur = self.first
        while cur is not None:
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
        for data in self.items():
            yield data[1]

    def keys(self):
        """
        Return all keys
        """
        return [data[0] for data in self.items()]

    def values(self):
        """
        Return all values
        """
        return [data[1] for data in self.items()]

    def items(self):
        """
        Return all items
        """
        return [data[0] for data in self.items()]

    def clear(self):
        """
        Empties LRU
        """
        # Step through the doubly linked list, setting prev and next to None.
        # This ensures that each node is unreachable and therefore eligible for
        # garbage collection. "del" is also called for each node, but it is
        # unclear whether this actually has any effect, of just removes the
        # binding to nobj
        nobj = self.first
        # The references first and last are removed so that the nodes are not
        # reachable from these
        self.first = None
        self.last = None
        # The references from self.data are removed
        self.data.clear()
        while nobj is not None and nobj.next is not None:
            # each node except the last is processed
            nobj.next.prev = None
            nextobj = nobj.next
            nobj.next = None
            del nobj
            nobj = nextobj
        if nobj is not None:
            # The last node is processed
            del nobj
