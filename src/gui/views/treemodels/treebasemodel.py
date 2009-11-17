#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2009       Nick Hall
# Copyright (C) 2009       Benny Malengier
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
import config
from Utils import conv_unicode_tosrtkey_ongtk
from gen.utils.longop import LongOpStatus
from Lru import LRU
from bisect import bisect_right
from Filters import SearchFilter, ExactSearchFilter

#-------------------------------------------------------------------------
#
# TreeBaseModel
#
#-------------------------------------------------------------------------
class TreeBaseModel(gtk.GenericTreeModel):
    """
    The base class for all hierarchical treeview models.  The model defines the
    mapping between a unique node and a path. Paths are defined by a tuple.
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
                (sortkey, child) tuples.  The list is sorted during the
                build.  The top node of the hierarchy is None.
    handle2node A dictionary of gramps handles.  Each entry is a node.
    
    The model obtains data from database as needed and holds a cache of most
    recently used data.
    As iter for generictreemodel, node is used. This will be the handle for 
    database objects.
    
    Creation:
    db      :   the database
    tooltip_column :  column number of tooltip
    marker_column  :  column number of marker
    search         :  the search that must be shown
    skip           :  values not to show
    scol           :  column on which to sort
    order          :  order of the sort
    sort_map       :  mapping from columns seen on the GUI and the columns 
                      as defined here
    nrgroups       :  maximum number of grouping level, 0 = no group, 
                      1= one group, .... Some optimizations can be for only
                      one group. nrgroups=0 should never be used, as then a 
                      flatbasemodel should be used
    group_can_have_handle :
                      can groups have a handle. If False, this means groups 
                      are only used to group subnodes, not for holding data and
                      showing subnodes
    """

    # LRU cache size
    _CACHE_SIZE = 250
   
    def __init__(self, db, tooltip_column, marker_column=None,
                    search=None, skip=set(),
                    scol=0, order=gtk.SORT_ASCENDING, sort_map=None,
                    nrgroups = 1,
                    group_can_have_handle = False):
        cput = time.clock()
        gtk.GenericTreeModel.__init__(self)

        # Initialise data structures
        self.tree = {}
        self.children = {}
        self.children[None] = []
        self.handle2node = {}
        self.__reverse = (order == gtk.SORT_DESCENDING)
        self.nrgroups = nrgroups
        self.group_can_have_handle = group_can_have_handle

        self.set_property("leak_references", False)
        self.db = db
        #normally sort on first column, so scol=0
        if sort_map:
            #sort_map is the stored order of the columns and if they are
            #enabled or not. We need to store on scol of that map
            self.sort_map = [ f for f in sort_map if f[0]]
            #we need the model col, that corresponds with scol
            col = self.sort_map[scol][1]
            self.sort_func = self.smap[col]
            self.sort_col = col
        else:
            self.sort_func = self.smap[scol]
            self.sort_col = scol
    
        self._in_build = False
        
        self.lru_data  = LRU(TreeBaseModel._CACHE_SIZE)

        config.connect("preferences.todo-color",
                          self.__update_todo)
        config.connect("preferences.custom-marker-color",
                          self.__update_custom)
        config.connect("preferences.complete-color",
                          self.__update_complete)

        self.complete_color = config.get('preferences.complete-color')
        self.todo_color = config.get('preferences.todo-color')
        self.custom_color = config.get('preferences.custom-marker-color')

        self._tooltip_column = tooltip_column
        self._marker_column = marker_column

        self.__total = 0
        self.__displayed = 0

        self.set_search(search)
        self.rebuild_data(self.current_filter, skip)

        _LOG.debug(self.__class__.__name__ + ' __init__ ' +
                    str(time.clock() - cput) + ' sec')


    def __update_todo(self, *args):
        """
        Update the todo color when the preferences change.
        """
        self.todo_color = config.get('preferences.todo-color')
        
    def __update_custom(self, *args):
        """
        Update the custom color when the preferences change.
        """
        self.custom_color = config.get('preferences.custom-marker-color')

    def __update_complete(self, *args):
        """
        Update the complete color when the preferences change.
        """
        self.complete_color = config.get('preferences.complete-color')

    def displayed(self):
        """
        Return the number of rows displayed.
        """
        return self.__displayed
        
    def total(self):
        """
        Return the total number of rows without a filter or search condition.
        """
        return self.__total

    def tooltip_column(self):
        """
        Return the tooltip column.
        """
        return self._tooltip_column

    def marker_column(self):
        """
        Return the marker color column.
        """
        return self._marker_column

    def clear_cache(self):
        """
        Clear the LRU cache.
        """
        self.lru_data.clear()

    def clear(self):
        """
        Clear the data map.
        """
        self.tree = {}
        self.children = {}
        self.children[None] = []
        self.handle2node = {}
        self.__reverse = False

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
            if search[0] == 1: # Filter
                #following is None if no data given in filter sidebar
                self.search = search[1]
                self._build_data = self._rebuild_filter
            elif search[0] == 0: # Search
                if search[1]:
                    # we have search[1] = (index, text_unicode, inversion)
                    col, text, inv = search[1]
                    func = lambda x: self._get_value(x, col) or u""
                    if search[2]:
                        self.search = ExactSearchFilter(func, text, inv)
                    else:
                        self.search = SearchFilter(func, text, inv)
                else:
                    self.search = None
                self._build_data = self._rebuild_search
            else: # Fast filter
                self.search = search[1]
                self._build_data = self._rebuild_search
        else:
            self.search = None
            self._build_data = self._rebuild_search
            
        self.current_filter = self.search

    def rebuild_data(self, data_filter=None, skip=[]):
        """
        Rebuild the data map.
        """
        cput = time.clock()
        self.clear_cache()
        self._in_build = True

        if not self.db.is_open():
            return

        self.clear()
        self._build_data(self.current_filter, skip)
        self.sort_data()

        self._in_build = False

        self.current_filter = data_filter

        _LOG.debug(self.__class__.__name__ + ' rebuild_data ' +
                    str(time.clock() - cput) + ' sec')

    def _rebuild_search(self, dfilter, skip):
        """
        Rebuild the data map where a search condition is applied.
        """
        self.__total = 0
        self.__displayed = 0
        with self.gen_cursor() as cursor:
            for handle, data in cursor:
                self.__total += 1
                if not (handle in skip or (dfilter and not
                                        dfilter.match(handle, self.db))):
                    self.__displayed += 1
                    self.add_row(handle, data)

    def _rebuild_filter(self, dfilter, skip):
        """
        Rebuild the data map where a filter is applied.
        """        
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
        
    def add_node(self, parent, child, sortkey, handle, add_parent=True):
        """
        Add a node to the map.
        
        parent      The parent node for the child.  None for top level. If
                    this node does not exist, it will be added under the top
                    level if add_parent=True. For performance, if you have
                    added the parent, passing add_parent=False, will skip adding
                    missing parent
        child       A unique ID for the node.
        sortkey     A key by which to sort child nodes of each parent.
        handle      The gramps handle of the object corresponding to the
                    node.  None if the node does not have a handle.
        add_parent  Bool, if True, check if parent is present, if not add the 
                    parent as a top group with no handle
        """
        sortkey = conv_unicode_tosrtkey_ongtk(sortkey)
        if add_parent and not (parent in self.tree):
            #add parent to self.tree as a node with no handle, as the first
            #group level
            self.add_node(None, parent, parent, None, add_parent=False)
        if child in self.tree:
            #a node is added that is already present,
            self._add_dup_node(parent, child, sortkey, handle)
        else:
            self.tree[child] = (parent, handle)
            if parent in self.children:
                if self._in_build:
                    self.children[parent].append((sortkey, child))
                else:
                    index = bisect_right(self.children[parent], (sortkey, child))
                    self.children[parent].insert(index, (sortkey, child))
            else:
                self.children[parent] = [(sortkey, child)]

            if not self._in_build:
                # emit row_inserted signal
                path = self.on_get_path(child)
                node = self.get_iter(path)
                self.row_inserted(path, node)

        if handle:
            self.handle2node[handle] = child

    def _add_dup_node(self, parent, child, sortkey, handle):
        """
        How to handle adding a node a second time
        Default: if group nodes can have handles, it is allowed to add it 
            again, and this time setting the handle
        Otherwise, a node should never be added twice!
        """
        if not self.group_can_have_handle:
            raise ValueError, 'attempt to add twice a node to the model %s' % \
                                str(parent) + ' ' + str(child) + ' ' + sortkey
        present_val = self.tree[child]
        if handle and present_val[1] is None:
            self.tree[child][1] = handle
        elif handle is None:
            pass
        else:
            #handle given, and present handle is not None
            raise ValueError, 'attempt to add twice a node to the model'

    def sort_data(self):
        """
        Sort the data in the map according to the value of the sort key.
        """
        for node in self.children:
            self.children[node].sort()
            
    def remove_node(self, node):
        """
        Remove a node from the map.
        """
        if node in self.children:
            self.tree[node][1] = None
        else:
            path = self.on_get_path(node)
            parent = self.tree[node][0]
            del self.tree[node]
            new_list = []
            for child in self.children[parent]:
                if child[1] != node:
                    new_list.append(child)
            if len(new_list) == 0:
                del self.children[parent]
            else:
                self.children[parent] = new_list

            # emit row_deleted signal
            self.row_deleted(path)
        
    def reverse_order(self):
        """
        Reverse the order of the map.
        """
        cput = time.clock()
        self.__reverse = not self.__reverse
        self._reverse_level(None)
        _LOG.debug(self.__class__.__name__ + ' reverse_order ' +
                    str(time.clock() - cput) + ' sec')

    def _reverse_level(self, node):
        """
        Reverse the order of a single level in the map.
        """
        if node in self.children:
            rows = range(len(self.children[node]))
            rows.reverse()
            if node is None:
                path = iter = None
            else:
                path = self.on_get_path(node)
                iter = self.get_iter(path)
            self.rows_reordered(path, iter, rows)
            for child in self.children[node]:
                self._reverse_level(child[1])

    def add_row(self, handle, data):
        """
        Add a row to the model.  In general this will add more then one node.
        """
        raise NotImplementedError

    def add_row_by_handle(self, handle):
        """
        Add a row to the model.
        """
        cput = time.clock()
        data = self.map(handle)
        self.add_row(handle, data)

        _LOG.debug(self.__class__.__name__ + ' add_row_by_handle ' +
                    str(time.clock() - cput) + ' sec')

    def delete_row_by_handle(self, handle):
        """
        Delete a row from the model.
        """
        cput = time.clock()
        self.clear_cache()

        node = self.get_node(handle)
        parent = self.on_iter_parent(node)
        self.remove_node(node)
        
        while parent is not None:
            next_parent = self.on_iter_parent(parent)
            if parent not in self.children:
                self.remove_node(parent)
            parent = next_parent
            
        _LOG.debug(self.__class__.__name__ + ' delete_row_by_handle ' +
                    str(time.clock() - cput) + ' sec')

    def update_row_by_handle(self, handle):
        """
        Update a row in the model.
        """
        self.delete_row_by_handle(handle)
        self.add_row_by_handle(handle)
        
        # If the node hasn't moved, all we need is to call row_changed.
        #self.row_changed(path, node)
        
    def get_handle(self, node):
        """
        Get the gramps handle for a node.  Return None if the node does
        not correspond to a gramps object.
        """
        ret = self.tree.get(node)
        if ret:
            return ret[1]
        return ret
            
    def get_node(self, handle):
        """
        Get the node for a handle.
        """
        return self.handle2node.get(handle)

    # The following implement the public interface of gtk.GenericTreeModel

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

    def on_get_column_type(self, index):
        """
        See gtk.GenericTreeModel
        """
        if index == self._tooltip_column:
            return object
        return str

    def on_get_value(self, node, col):
        """
        See gtk.GenericTreeModel
        """
        handle = self.get_handle(node)
        if handle is None:
            # Header rows dont get the foreground color set
            if col == self._marker_column:
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
            
    def _get_value(self, handle, col):
        """
        Returns the contents of a given column of a gramps object
        """
        try:
            if handle in self.lru_data:
                data = self.lru_data[handle]
            else:
                data = self.map(handle)
                if not self._in_build:
                    self.lru_data[handle] = data
            return (self.fmap[col](data))
        except:
            return None

    def on_get_iter(self, path):
        """
        Returns a node from a given path.
        """
        if not self.tree:
            return None
        node = None
        pathlist = list(path)
        for index in pathlist:
            if self.__reverse:
                size = len(self.children[node])
                node = self.children[node][size - index - 1][1]
            else:
                node = self.children[node][index][1]
        return node
        
    def on_get_path(self, node):
        """
        Returns a path from a given node.
        """
        pathlist = []
        while node is not None:
            parent = self.tree[node][0]
            for index, value in enumerate(self.children[parent]):
                if value[1] == node:
                    break
            if self.__reverse:
                size = len(self.children[parent])
                pathlist.append(size - index - 1)
            else:
                pathlist.append(index)
            node = parent
        if pathlist is not None:
            pathlist.reverse()
            return tuple(pathlist)
        else:
            return None
            
    def on_iter_next(self, node):
        """
        Get the next node with the same parent as the given node.
        """
        parent = self.tree[node][0]
        for index, child in enumerate(self.children[parent]):
            if child[1] == node:
                break
                
        if self.__reverse:
            index -= 1
        else:
            index += 1

        if index >= 0 and index < len(self.children[parent]):
            return self.children[parent][index][1]
        else:
            return None

    def on_iter_children(self, node):
        """
        Get the first child of the given node.
        """
        if node in self.children:
            if self.__reverse:
                size = len(self.children[node])
                return self.children[node][size - 1][1]
            else:
                return self.children[node][0][1]
        else:
            return None
        
    def on_iter_has_child(self, node):
        """
        Find if the given node has any children.
        """
        if node in self.children:
            return True
        else:
            return False

    def on_iter_n_children(self, node):
        """
        Get the number of children of the given node.
        """
        if node in self.children:
            return len(self.children[node])
        else:
            return 0

    def on_iter_nth_child(self, node, index):
        """
        Get the nth child of the given node.
        """
        if node in self.children:
            if len(self.children[node]) > index:
                if self.__reverse:
                    size = len(self.children[node])
                    return self.children[node][size - index - 1][1]
                else:
                    return self.children[node][index][1]
            else:
                return None
        else:
            return None

    def on_iter_parent(self, node):
        """
        Get the parent of the given node.
        """
        if node in self.tree:
            return self.tree[node][0]
        else:
            return None
