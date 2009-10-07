#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2009       Nick Hall
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
This module provides the model that is used for all hierarchical treeviews.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from __future__ import with_statement
import time
import locale
import logging

_LOG = logging.getLogger(".gui.treebasemodel")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Config
from gen.utils.longop import LongOpStatus
from Filters import SearchFilter
# from Filters import ExactSearchFilter
from Lru import LRU

#-------------------------------------------------------------------------
#
# TreeNodeMap
#
#-------------------------------------------------------------------------
class TreeNodeMap(object):
    """
    A NodeMap for a hierarchical treeview.  The map defines the mapping
    between a unique node and a path. Paths are defined by a tuple.
    The first element is an integer specifying the position in the top
    level of the hierarchy.  The next element relates to the next level
    in the hierarchy.  The number of elements depends on the depth of the
    node within the hierarchy.

    The following data is stored:

    tree        A dictionary of unique nodes.  Each entry is a list
                containing the parent node and gramps handle.  The handle
                is set to None if no gramps object is associated with the
                node.
    children    A dictionary of parent nodes.  Each entry is a list of
                (child, sortkey) tuples.  The list is sorted during the
                build.  The top node of the hierarchy is None.
    path2node   A dictionary of paths.  Each entry is a node.
    node2path   A dictionary of nodes.  Each entry is a path.
    handle2node A dictionary of gramps handles.  Each entry is a node.

    Nodes are added using the add_node method.
    The path2node and node2path mapping is built using build_toplevel.
    A simple recursive algorithm is used.
    Branches of the tree can be re-built using build_sub_entry.
    """
    def __init__(self):
        """
        Initialise data structures
        """
        self.tree = {}
        self.children = {}
        self.path2node = {}
        self.node2path = {}

        self.handle2node = {}

        self.__reverse = False

    def clear(self):
        """
        Clear the entire map.
        """
        self.tree = {}
        self.children = {}
        self.path2node = {}
        self.node2path = {}

        self.handle2node = {}
       
    def clear_sub_entry(self, node):
        """
        Clear a single branch of the map.
        """
        if node is None:
            self.path2node = {}
            self.node2path = {}
        else:
            if node in self.children:
                for child in self.children[node]:
                    self.clear_node(child[0])

    def clear_node(self, node):
        if node in self.node2path:
            path = self.node2path[node]
            del self.path2node[path]
            del self.node2path[node]
            if node in self.children:
                for child in self.children[node]:
                    self.clear_node(child[0])
        
    def add_node(self, parent, child, sortkey, handle):
        """
        Add a node to the map.
        
        parent      The parent node for the child.  None for top level.
        child       A unique ID for the node.
        sortkey     A key by which to sort child nodes of each parent.
        handle      The gramps handle of the object corresponding to the
                    node.  None if the node does not have a handle.
        """
        if child in self.tree:
            if handle:
                self.tree[child][1] = handle
            node_added = False
        else:

            self.tree[child] = [parent, handle]
            if parent in self.children:
                self.children[parent] += [(child, sortkey)]
            else:
                self.children[parent] = [(child, sortkey)]                
            node_added = True

        if handle:
            self.handle2node[handle] = child

        return node_added
        
    def remove_node(self, node):
        if node in self.children:
            self.tree[node][1] = None
            node_removed = False
        else:
            parent = self.tree[node][0]
            del self.tree[node]
            new_list = []
            for child in self.children[parent]:
                if child[0] != node:
                    new_list.append(child)
            if len(new_list) == 0:
                del self.children[parent]
            else:
                self.children[parent] = new_list
            node_removed = True

        return node_removed

    def build_sub_entry(self, node, path, sort):
        """
        Build the path2node and node2path maps for the children of a
        given node and recursively builds the next level down.
        
        node        The parent node.
        path        The path of the parent node.
        """
        if sort:
            self.children[node].sort(key=lambda x: locale.strxfrm(x[1]))
        for i, child in enumerate(self.children[node]):
            if self.__reverse:
                new_path = path + [len(self.children[node]) - i - 1]
            else:
                new_path = path + [i]
            self.path2node[tuple(new_path)] = child[0]
            self.node2path[child[0]] = tuple(new_path)
            if child[0] in self.children:
                self.build_sub_entry(child[0], new_path, sort)

    def build_toplevel(self, sort=True):
        """
        Build the complete map from the top level.
        """
        if len(self.tree) == 0:
            return
        self.build_sub_entry(None, [], sort)

    def reverse_order(self):
        self.__reverse = not self.__reverse
        self.path2node = {}
        self.node2path = {}
        self.build_toplevel(sort=False)
        
    def get_handle(self, node):
        """
        Get the gramps handle for a node.  Return None if the node does
        not correspond to a gramps object.
        """
        if node in self.tree:
            return self.tree[node][1]
        else:
            return None
            
    def get_node(self, handle):
        """
        Get the node for a handle.
        """
        if handle in self.handle2node:
            return self.handle2node[handle]
        else:
            return None
            
    # The following methods support the public interface of the
    # GenericTreeModel.
    
    def get_path(self, node):
        """
        Get the path for a node.
        """
        # For trees without the active person a key error is thrown
        return self.node2path[node]        

    def get_iter(self, path):
        """
        Build the complete map from the top level.
        """
        if path in self.path2node:
            return self.path2node[path]
        else:
            # Empty tree
            return None

    def find_next_node(self, node):
        """
        Get the next node with the same parent as the given node.
        """
        path_list = list(self.node2path[node])
        path_list[len(path_list)-1] += 1
        path = tuple(path_list)
        if path in self.path2node:
            return self.path2node[path]
        else:
            return None

    def first_child(self, node):
        """
        Get the first child of the given node.
        """
        if node in self.children:
            if self.__reverse:
                size = len(self.children[node])
                return self.children[node][size - 1][0]
            else:
                return self.children[node][0][0]
        else:
            return None
        
    def has_child(self, node):
        """
        Find if the given node has any children.
        """
        if node in self.children:
            return True
        else:
            return False

    def number_of_children(self, node):
        """
        Get the number of children of the given node.
        """
        if node in self.children:
            return len(self.children[node])
        else:
            return 0

    def get_nth_child(self, node, index):
        """
        Get the nth child of the given node.
        """
        if node in self.children:
            if len(self.children[node]) > index:
                if self.__reverse:
                    size = len(self.children[node])
                    return self.children[node][size - index - 1][0]
                else:
                    return self.children[node][index][0]
            else:
                return None
        else:
            return None

    def get_parent_of(self, node):
        """
        Get the parent of the given node.
        """
        if node in self.tree:
            return self.tree[node][0]
        else:
            return None

#-------------------------------------------------------------------------
#
# TreeBaseModel
#
#-------------------------------------------------------------------------
class TreeBaseModel(gtk.GenericTreeModel):
    """
    The base class for all hierarchical treeview models. 
    It keeps a TreeNodeMap, and obtains data from database as needed.
    """

    # LRU cache size
    _CACHE_SIZE = 250
   
    # Search/Filter modes
    GENERIC = 0
    SEARCH = 1
    FAST = 2

    def __init__(self, db, tooltip_column, marker_column=None,
                    search=None, skip=set(),
                    scol=0, order=gtk.SORT_ASCENDING, sort_map=None):
        cput = time.clock()
        gtk.GenericTreeModel.__init__(self)

        self.db = db
        #normally sort on first column, so scol=0
        if sort_map:
            #sort_map is the stored order of the columns and if they are
            #enabled or not. We need to store on scol of that map
            self.sort_map = [ f for f in sort_map if f[0]]
            #we need the model col, that corresponds with scol
            col = self.sort_map[scol][1]
            self.sort_func = self.smap[col]
        else:
            self.sort_func = self.smap[scol]
        self.sort_col = scol
    
        self.in_build = False
        
        self.lru_data  = LRU(TreeBaseModel._CACHE_SIZE)

        Config.client.notify_add("/apps/gramps/preferences/todo-color",
                                 self.__update_todo)
        Config.client.notify_add("/apps/gramps/preferences/custom-marker-color",
                                 self.__update_custom)
        Config.client.notify_add("/apps/gramps/preferences/complete-color",
                                 self.__update_complete)

        self.complete_color = Config.get(Config.COMPLETE_COLOR)
        self.todo_color = Config.get(Config.TODO_COLOR)
        self.custom_color = Config.get(Config.CUSTOM_MARKER_COLOR)

        self.mapper = TreeNodeMap()
        self.set_search(search)
            
        self.tooltip_column = tooltip_column
        self.marker_color_column = marker_column

        self.__total = 0
        self.__displayed = 0

        self.rebuild_data(self.current_filter, skip)

        _LOG.debug(self.__class__.__name__ + ' __init__ ' +
                    str(time.clock() - cput) + ' sec')


    def __update_todo(self, *args):
        self.todo_color = Config.get(Config.TODO_COLOR)
        
    def __update_custom(self, *args):
        self.custom_color = Config.get(Config.CUSTOM_MARKER_COLOR)

    def __update_complete(self, *args):
        self.complete_color = Config.get(Config.COMPLETE_COLOR)

    def displayed(self):
        return self.__displayed
        
    def total(self):
        return self.__total

    def set_search(self, search):
        """
        Change the search function that filters the data in the model. 
        When this method is called, make sure:
        # you call self.rebuild_data() to recalculate what should be seen 
          in the model
        # you reattach the model to the treeview so that the treeview updates
          with the new entries
        """
        if search:
            if search[0]:
                #following is None if no data given in filter sidebar
                self.search = search[1]
                self._build_data = self._build_filter_sub
            else:
                if search[1]:
                    # we have search[1] = (index, text_unicode, inversion)
                    col = search[1][0]
                    text = search[1][1]
                    inv = search[1][2]
                    func = lambda x: self._get_value(x, col) or u""
                    self.search = SearchFilter(func, text, inv)
                else:
                    self.search = None
                self._build_data = self._build_search_sub
        else:
            self.search = None
            self._build_data = self._build_search_sub
            
        self.current_filter = self.search

    def rebuild_data(self, data_filter=None, skip=[]):
        """
        Rebuild the data map.
        """
        self.clear_cache()
        self.in_build  = True

        self.mapper.clear()

        if not self.db.is_open():
            return

        #self._build_data(data_filter, skip)
        self._build_data(self.current_filter, skip)
        self.mapper.build_toplevel()

        self.in_build  = False

        self.current_filter = data_filter

    def _build_search_sub(self, dfilter, skip):
        self.__total = 0
        self.__displayed = 0
        with self.gen_cursor() as cursor:
            for handle, data in cursor:
                self.__total += 1
                if not (handle in skip or (dfilter and not
                                        dfilter.match(handle, self.db))):
                    self.__displayed += 1
                    self.add_row(handle, data)

    def _build_filter_sub(self, dfilter, skip):
        
        with self.gen_cursor() as cursor:
            handle_list = [key for key, data in cursor]
        self.__total = len(handle_list)

        if dfilter:
            handle_list = dfilter.apply(self.db, handle_list)
            self.__displayed = len(handle_list)
        else:
            self.__displayed = self.db.get_number_of_people()

        status = LongOpStatus(msg="Loading People",
                              total_steps=self.__displayed,
                              interval=self.__displayed//10)
        self.db.emit('long-op-start', (status,))
        for handle in handle_list:
            status.heartbeat()
            data = self.map(handle)
            if not handle in skip:
                self.add_row(handle, data)
        status.end()
        
    def reverse_order(self):
        self.mapper.reverse_order()

    def clear_cache(self):
        self.lru_data.clear()

    def build_sub_entry(self, node):
        self.mapper.clear_sub_entry(node)
        if node is None:
            self.mapper.build_toplevel(sort=True)
        else:
            path = self.on_get_path(node)
            self.mapper.build_sub_entry(node, list(path), sort=True)

    def add_row(self, handle, data):
        pass

    def add_row_by_handle(self, handle):
        """
        Add a row to the model.
        """
        data = self.map(handle)
        top_node = self.add_row(handle, data)
        parent_node = self.on_iter_parent(top_node)
        
        self.build_sub_entry(parent_node)

        path = self.on_get_path(top_node)
        node = self.get_iter(path)
        # only one row_inserted and row_has_child_toggled is needed?
        self.row_inserted(path, node)
        self.row_has_child_toggled(path, node)

    def delete_row_by_handle(self, handle):
        """
        Delete a row from the model.
        """
        self.clear_cache()
        node = self.get_node(handle)
        parent = self.on_iter_parent(node)
        while node and self.mapper.remove_node(node):
            path = self.on_get_path(node)
            node = parent
            parent = self.on_iter_parent(parent)
            
        self.build_sub_entry(node)
        
        self.row_deleted(path)

    def update_row_by_handle(self, handle):
        """
        Update a row in the model.
        """
        self.delete_row_by_handle(handle)
        self.add_row_by_handle(handle)
        
        # If the node hasn't moved all we need is to call row_changed.
        #self.row_changed(path, node)
        
    def get_node(self, handle):
        return self.mapper.get_node(handle)
        
    def get_handle(self, node):
        return self.mapper.get_handle(node)

    def _get_value(self, handle, col):
        """
        Returns the contents of a given column of a gramps object
        """
        try:
            if handle in self.lru_data:
                data = self.lru_data[handle]
            else:
                data = self.map(handle)
                if not self.in_build:
                    self.lru_data[handle] = data
            return (self.fmap[col](data, handle))
        except:
            return None

    # The following define the public interface of gtk.GenericTreeModel

    def on_get_flags(self):
        """
        See gtk.GenericTreeModel
        """
        return gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        """
        Return the number of columns. Must be implemented in the child objects
        See gtk.GenericTreeModel
        """
        raise NotImplementedError

    def on_get_path(self, node):
        """
        See gtk.GenericTreeModel
        """
        return self.mapper.get_path(node)

    def on_get_column_type(self, index):
        """
        See gtk.GenericTreeModel
        """
        if index == self.tooltip_column:
            return object
        return str

    def on_get_iter(self, path):
        """
        See gtk.GenericTreeModel
        """
        return self.mapper.get_iter(path)

    def on_get_value(self, node, col):
        """
        See gtk.GenericTreeModel
        """
        handle = self.mapper.get_handle(node)
        if handle is None:
            # Header rows dont get the foreground color set
            if col == self.marker_color_column:
                return None

            # Look for header fuction for column and call it
            if self.hmap[col] is not None:
                return self.hmap[col](node)

            # If no header fuction return an empty string
            return u''

        else:
            # return values for 'data' row, calling a function
            # according to column_defs table
            return self._get_value(handle, col)

    def on_iter_next(self,  node):
        """
        See gtk.GenericTreeModel
        """
        return self.mapper.find_next_node(node)

    def on_iter_children(self, node):
        """
        See gtk.GenericTreeModel
        """
        return self.mapper.first_child(node)

    def on_iter_has_child(self, node):
        """
        See gtk.GenericTreeModel
        """
        return self.mapper.has_child(node)

    def on_iter_n_children(self, node):
        """
        See gtk.GenericTreeModel
        """
        return self.mapper.number_of_children(node)

    def on_iter_nth_child(self, node, index):
        """
        See gtk.GenericTreeModel
        """
        return self.mapper.get_nth_child(node, index)

    def on_iter_parent(self, node):
        """
        See gtk.GenericTreeModel
        """
        return self.mapper.get_parent_of(node)
