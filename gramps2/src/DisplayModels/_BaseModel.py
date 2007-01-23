#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# $Id$

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import locale
try:
    set()
except:
    from sets import Set as set
    
#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters import SearchFilter

#-------------------------------------------------------------------------
#
# BaseModel
#
#-------------------------------------------------------------------------
class BaseModel(gtk.GenericTreeModel):

    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING,
                 tooltip_column=None, search=None, skip=set(),
                 sort_map=None):
        gtk.GenericTreeModel.__init__(self)
        self.prev_handle = None
        self.prev_data = None
        self.set_property("leak_references",False)
        self.db = db
        if sort_map:
	    self.sort_map = [ f for f in sort_map if f[0]]
            col = self.sort_map[scol][1]
            self.sort_func = self.smap[col]
        else:
            self.sort_func = self.smap[scol]
        self.sort_col = scol
        self.skip = skip

        if search:
            if search[0]:
                self.search = search[1]
                self.rebuild_data = self._rebuild_filter
            else:
                if search[1]:
                    col = search[1][0]
                    text = search[1][1]
                    inv = search[1][2]
                    func = lambda x: self.on_get_value(x, col) or u""
                    self.search = SearchFilter(func, text, inv)
                else:
                    self.search = None
                self.rebuild_data = self._rebuild_search
        else:
            self.search = None
            self.rebuild_data = self._rebuild_search
            
        self.reverse = (order == gtk.SORT_DESCENDING)
        self.tooltip_column = tooltip_column
        self.rebuild_data()

    def set_sort_column(self,col):
        self.sort_func = self.smap[col]

    def sort_keys(self):
        cursor = self.gen_cursor()
        sarray = []
        data = cursor.next()

        while data:
            key = locale.strxfrm(self.sort_func(data[1]))
            sarray.append((key,data[0]))
            data = cursor.next()
        cursor.close()

        sarray.sort(reverse=self.reverse)

        return [ x[1] for x in sarray ]

    def _rebuild_search(self,ignore=None):
        if self.db.is_open():
            if self.search and self.search.text:
                self.datalist = [h for h in self.sort_keys()\
                                 if self.search.match(h) and \
				 h not in self.skip and h != ignore]
            else:
                self.datalist = [h for h in self.sort_keys() \
				 if h not in self.skip and h != ignore]
            i = 0
            self.indexlist = {}
            for key in self.datalist:
		self.indexlist[key] = i
		i += 1
        else:
            self.datalist = []
            self.indexlist = {}

    def _rebuild_filter(self, ignore=None):
        if self.db.is_open():
            if self.search:
                self.datalist = self.search.apply(self.db, 
						  [ k for k in self.sort_keys()\
						    if k != ignore])
            else:
                self.datalist = [ k for k in self.sort_keys() \
				  if k != ignore ]

            i = 0
            self.indexlist = {}
            for key in self.datalist:
                if key not in self.skip:
                    self.indexlist[key] = i
                    i += 1
        else:
            self.datalist = []
            self.indexlist = {}
        
#    def add_row_by_handle(self,handle):
#        self.build_tree()

    def delete_row_by_handle(self,handle):
        index = self.indexlist[handle]

	del self.datalist[index]
	del self.indexlist[handle]

	for key in self.indexlist:
	    if self.indexlist[key] > index:
		self.indexlist[key] -= 1
	#self.rebuild_data(ignore=handle)
        self.row_deleted(index)

    def update_row_by_handle(self,handle):
        index = self.indexlist[handle]
        node = self.get_iter(index)
        self.row_changed(index,node)

    def on_get_flags(self):
	'''returns the GtkTreeModelFlags for this particular type of model'''
	return gtk.TREE_MODEL_LIST_ONLY | gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        return 1

    def on_get_path(self, node):
	'''returns the tree path (a tuple of indices at the various
	levels) for a particular node.'''
        return self.indexlist[node]

    def on_get_column_type(self,index):
        if index == self.tooltip_column:
            return object
        return str

    def on_get_iter(self, path):
        try:
            return self.datalist[path[0]]
        except IndexError:
            return None

    def on_get_value(self,node,col):
        try:
            if node != self.prev_handle:
                self.prev_data = self.map(str(node))
                self.prev_handle = node
            return self.fmap[col](self.prev_data)
        except:
            return u''

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
        try:
            return self.datalist[self.indexlist[node]+1]
        except IndexError:
            return None

    def on_iter_children(self,node):
        """Return the first child of the node"""
        if node == None and self.datalist:
            return self.datalist[0]
        return None

    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
        if node == None:
            return len(self.datalist) > 0
        return False

    def on_iter_n_children(self,node):
        if node == None:
            return len(self.datalist)
        return 0

    def on_iter_nth_child(self,node,n):
        if node == None:
            return self.datalist[n]
        return None

    def on_iter_parent(self, node):
	'''returns the parent of this node'''
        return None
