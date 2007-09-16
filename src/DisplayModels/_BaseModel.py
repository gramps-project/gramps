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
import Config

#-------------------------------------------------------------------------
#
# NodeMap
#
#-------------------------------------------------------------------------
class NodeMap:
    """
    Provides the Path to Iter mappings for a TreeView model. The implementation
    provides a list of nodes and a dictionary of handles. The datalist provides
    the path (index) to iter (handle) mapping, while the the indexmap provides
    the handle to index mappings
    """

    def __init__(self):
        """
        Create a new instance, clearing the datalist and indexmap
        """
        self.data_list = []
        self.index_map = {}

    def set_path_map(self, dlist):
        """
        Takes a list of handles and builds the index map from it.
        """
        self.data_list = dlist
        i = 0
        self.index_map = {}
        for key in self.data_list:
            self.index_map[key] = i
            i +=1

    def clear_map(self):
        """
        Clears out the data_list and the index_map
        """
        self.data_list = []
        self.index_map = {}

    def get_path(self, handle):
        """
        Returns the path from the passed handle. This is accomplished by
        indexing into the index_map to get the index (path)
        """
        return self.index_map.get(handle)

    def get_handle(self, path):
        """
        Returns the handle from the path. The path is assumed to be an integer.
        This is accomplished by indexing into the data_list
        """
        return self.data_list[path]

    def delete_by_index(self, index):
        """
        Deletes the item at the specified path, then rebuilds the index_map,
        subtracting one from each item greater than the deleted index.
        """
        handle = self.data_list[index]
        del self.data_list[index]
        del self.index_map[handle]

        for key in self.index_map:
            if self.index_map[key] > index:
                self.index_map[key] -= 1

    def find_next_handle(self, handle):
        """
        Finds the next handle based off the passed handle. This is accomplished
        by finding the index of associated with the handle, adding one to find
        the next index, then finding the handle associated with the next index.
        """
        try:
            return self.data_list[self.index_map.get(handle)+1]
        except IndexError:
            return None
        
    def __len__(self):
        """
        Returns the number of entries in the map.
        """
        return len(self.data_list)

    def get_first_handle(self):
        """
        Returns the first handle in the map.
        """
        return self.data_list[0]

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

        self.total = 0
        self.displayed = 0

        self.node_map = NodeMap()

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

        Config.client.notify_add("/apps/gramps/preferences/todo-color",
                                 self.update_todo)
        Config.client.notify_add("/apps/gramps/preferences/custom-marker-color",
                                 self.update_custom)
        Config.client.notify_add("/apps/gramps/preferences/complete-color",
                                 self.update_complete)

        self.complete_color = Config.get(Config.COMPLETE_COLOR)
        self.todo_color = Config.get(Config.TODO_COLOR)
        self.custom_color = Config.get(Config.CUSTOM_MARKER_COLOR)
        self.rebuild_data()

    def update_todo(self,client,cnxn_id,entry,data):
        self.todo_color = Config.get(Config.TODO_COLOR)
        
    def update_custom(self,client,cnxn_id,entry,data):
        self.custom_color = Config.get(Config.CUSTOM_MARKER_COLOR)

    def update_complete(self,client,cnxn_id,entry,data):
        self.complete_color = Config.get(Config.COMPLETE_COLOR)

    def set_sort_column(self,col):
        self.sort_func = self.smap[col]

    def sort_keys(self):
        cursor = self.gen_cursor()
        self.sort_data = []
        data = cursor.next()

        self.total = 0
        while data:
            key = locale.strxfrm(self.sort_func(data[1]))
            self.sort_data.append((key,data[0]))
            self.total += 1
            data = cursor.next()
        cursor.close()

        self.sort_data.sort(reverse=self.reverse)

        return [ x[1] for x in self.sort_data ]

    def _rebuild_search(self,ignore=None):
        """ function called when view must be build, given a search text
            in the top search bar
            Remark: this method is overridden in NoteModel !
        """
        self.total = 0
        if self.db.is_open():
            if self.search and self.search.text:
                dlist = [h for h in self.sort_keys()\
                             if self.search.match(h) and \
                             h not in self.skip and h != ignore]
            else:
                dlist = [h for h in self.sort_keys() \
                             if h not in self.skip and h != ignore]
            self.displayed = len(dlist)
            self.node_map.set_path_map(dlist)
        else:
            self.displayed = 0
            self.node_map.clear_map()

    def _rebuild_filter(self, ignore=None):
        """ function called when view must be build, given filter options
            in the filter sidebar
            Remark: this method is overridden in NoteModel !
        """
        self.total = 0
        if self.db.is_open():
            if self.search:
                dlist = self.search.apply(self.db, 
                [ k for k in self.sort_keys()\
                      if k != ignore])
            else:
                dlist = [ k for k in self.sort_keys() \
                              if k != ignore ]

            self.displayed = len(dlist)
            self.node_map.set_path_map(dlist)
        else:
            self.displayed = 0
            self.node_map.clear_map()
        
    def add_row_by_handle(self,handle):
	if not self.search or (self.search and self.search.match(handle)):

	    data = self.map(handle)
            key = locale.strxfrm(self.sort_func(data))
            self.sort_data.append((key,handle))
	    self.sort_data.sort(reverse=self.reverse)
	    self.node_map.set_path_map([ x[1] for x in self.sort_data ])

	    index = self.node_map.get_path(handle)
	    if index != None:
		node = self.get_iter(index)
		self.row_inserted(index, node)

    def delete_row_by_handle(self,handle):
        index = self.node_map.get_path(handle)

        # remove from sort array
        i = 0
        for (key, node) in self.sort_data:
            if handle == node:
                del self.sort_data[i]
                break
            i += 1

        self.node_map.delete_by_index(index)
        self.row_deleted(index)

    def update_row_by_handle(self,handle):
        index = self.node_map.get_path(handle)
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
        return self.node_map.get_path(node)

    def on_get_column_type(self,index):
        if index == self.tooltip_column:
            return object
        return str

    def on_get_iter(self, path):
        try:
            return self.node_map.get_handle(path[0])
        except:
            return None

    def on_get_value(self, node, col):
        try:
            if node != self.prev_handle:
                self.prev_data = self.map(str(node))
                self.prev_handle = node
            return self.fmap[col](self.prev_data)
        except:
            return u''

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
        return self.node_map.find_next_handle(node)

    def on_iter_children(self,node):
        """Return the first child of the node"""
        if node == None and len(self.node_map):
            return self.node_map.get_first_handle()
        return None

    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
        if node == None:
            return len(self.node_map) > 0
        return False

    def on_iter_n_children(self,node):
        if node == None:
            return len(self.node_map)
        return 0

    def on_iter_nth_child(self,node,n):
        if node == None:
            return self.node_map.get_handle(n)
        return None

    def on_iter_parent(self, node):
	'''returns the parent of this node'''
        return None
