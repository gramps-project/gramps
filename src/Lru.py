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

class Node:
    def __init__(self, prev, me):
        self.prev = prev
        self.me = me
        self.next = None

class LRU: #Implementation of a length-limited O(1) LRU cache
    def __init__(self, count):
        self.count = max(count, 2)
        self.d = {}
        self.first = None
        self.last = None

    def __contains__(self, obj):
        return obj in self.d

    def __getitem__(self, obj):
        return self.d[obj].me[1]

    def __setitem__(self, obj, val):
        if obj in self.d:
            del self[obj]
        nobj = Node(self.last, (obj, val))
        if self.first is None:
            self.first = nobj
        if self.last:
            self.last.next = nobj
        self.last = nobj
        self.d[obj] = nobj
        if len(self.d) > self.count:
            if self.first == self.last:
                self.first = None
                self.last = None
                return
            a = self.first
            a.next.prev = None
            self.first = a.next
            a.next = None
            del self.d[a.me[0]]
            del a

    def __delitem__(self, obj):
        nobj = self.d[obj]
        if nobj.prev:
            nobj.prev.next = nobj.next
        else:
            self.first = nobj.next
        if nobj.next:
            nobj.next.prev = nobj.prev
        else:
            self.last = nobj.prev
        del self.d[obj]

    def __iter__(self):
        cur = self.first
        while cur != None:
            cur2 = cur.next
            yield cur.me[1]
            cur = cur2
        raise StopIteration

    def iteritems(self):
        cur = self.first
        while cur != None:
            cur2 = cur.next
            yield cur.me
            cur = cur2
        raise StopIteration

    def iterkeys(self):
        return iter(self.d)

    def itervalues(self):
        for i,j in self.iteritems():
            yield j

    def keys(self):
        return [i for i,j in self.iteritems()]

    def values(self):
        return [j for i,j in self.iteritems()]

    def items(self):
        return [i for i in self.iteritems()]
