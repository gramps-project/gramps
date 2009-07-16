#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009  Benny Malengier
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

"""
This module provides the flat treemodel that is used for all flat treeviews.

For performance, GRAMPS does not use gtk.TreeStore, as that would mean keeping
the entire database table of an object in memory. 
Instead, it suffices to keep in memory the sortkey and the matching handle, 
as well as a map of sortkey,handle to treeview path, and vice versa. 

For a flat view, the index of sortkey,handle will be the path, so it suffices
to keep in memory a map that given a sortkey,handle returns the path.
As we need to be able to insert/delete/update objects, and for that the handle
is all we know initially, and as sortkey,handle is uniquely determined by 
handle, instead of keeping a map of sortkey,handle to path, we keep a map of
handle to path

As a user selects another column to sort, the sortkey must be rebuild, and the
map remade. 

The class FlatNodeMap keeps a sortkeyhandle list with (sortkey, handle) entries,
and a handle2path dictionary. As the Map is flat, the index in sortkeyhandle
corresponds to the path.

The class FlatBaseModel, is the base class for all flat treeview models. 
It keeps a FlatNodeMap, and obtains data from database as needed
"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------

from __future__ import with_statement
import locale
import logging
import bisect
import time

_LOG = logging.getLogger(".gui.basetreemodel")
    
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
from Utils import conv_unicode_tosrtkey_ongtk

#-------------------------------------------------------------------------
#
# FlatNodeMap
#
#-------------------------------------------------------------------------
class FlatNodeMap(object):
    """
    A NodeMap for a flat treeview. In such a TreeView, the paths possible are
    0, 1, 2, ..., n-1, where n is the number of items to show. For the model
    it is needed to keep the Path to Iter mappings of the TreeView in memory
    
    The order of what is shown is based on the unique key: (sortkey, handle)
    Naming:
        * srtkey : key on which to sort
        * hndl   : handle of the object, makes it possible to retrieve the 
                   object from the database. As handle is unique, it is used
                   as the iter for the TreeView
        * index  : the index in the internal lists. When a view is in reverse, 
                    this is not kept physically, but instead via an offset
        * path   : integer path in the TreeView. This will be index if view is
                    ascending, but will begin at back of list if view shows
                    the entries in reverse.
        * index2hndl : list of (srtkey, hndl) tuples. The index gives the 
                        (srtkey, hndl) it belongs to. 
                       This normally is only a part of all possible data 
        * hndl2index : dictionary of *hndl: index* values
        
    The implementation provides a list of (srtkey, hndl) of which the index is
    the path, and a dictionary mapping hndl to index.
    To obtain index given a path, method real_index() is available
    
    ..Note: If a string sortkey is used, apply locale.strxfrm on it , so as 
            to have localized sort
    """

    def __init__(self):
        """
        Create a new instance.
        """
        self._index2hndl = []
        self._fullhndl = self._index2hndl
        self._identical = True
        self._hndl2index = {}
        self._reverse = False
        self.__corr = (0, 1)

    def set_path_map(self, index2hndllist, fullhndllist, identical=True,
                     reverse=False):
        """
        This is the core method to set up the FlatNodeMap
        Input is a list of (srtkey, handle), of which the index is the path
        Calling this method sets the index2hndllist, and creates the hndl2index
        map. 
        fullhndllist is the entire list of (srtkey, handle) that is possible, 
        normally index2hndllist is only part of this list as determined by
        filtering. To avoid memory, if both lists are the same, pass only one
        list twice and set identical to True.
        Reverse sets up how the path is determined from the index. If True the
        first index is the last path
        
        :param index2hndllist: the ascending sorted (sortkey, handle) values 
                    as they will appear in the flat treeview. This often is 
                    a subset of all possible data
        :type index2hndllist: a list of (sortkey, handle) tuples
        :param fullhndllist: the list of all possilbe ascending sorted 
                    (sortkey, handle) values as they will appear in the flat 
                     treeview if all data is shown.
        :type fullhndllist: a list of (sortkey, handle) tuples
        :param identical: identify if index2hndllist and fullhndllist are the
                        same list, so only one is kept in memory.
        :type identical: bool
        """
        self._index2hndl = index2hndllist
        self._hndl2index = {}
        self._identical = identical
        if identical:
            self._fullhndl = self._index2hndl
        else:
            self._fullhndl = fullhndllist
        self._reverse = reverse
        self.reverse_order()
    
    def full_srtkey_hndl_map(self):
        """
        The list of all possible (sortkey, handle) tuples. 
        This is stored in FlatNodeMap so that it would not be needed to 
        reiterate over the database to obtain all posibilities.
        """
        return self._fullhndl

    def reverse_order(self):
        """
        This method keeps the index2hndl map, but sets it up the index in 
        reverse order. If the hndl2index map does not exist yet, it is created
        in the acending order as given in index2hndl
        The result is always a hndl2index map wich is correct, so or ascending
        order, or reverse order.
        """
        if self._hndl2index:
            #if hndl2index is build already, invert order, otherwise keep 
            # requested order
            self._reverse = not self._reverse
        if self._reverse:
            self.__corr = (len(self._index2hndl) - 1, -1)
        else:
            self.__corr = (0, 1)
        if not self._hndl2index: 
            for index, key in enumerate(self._index2hndl):
                #the handle is key[1]
                self._hndl2index[key[1]] = index
    
    def real_path(self, index):
        """
        Given the index in the maps, return the real path. 
        If reverse = False, then index is path, otherwise however, the 
        path must be calculated so that the last index is the first path
        """
        return self.__corr[0] + self.__corr[1] * index
    
    def real_index(self, path):
        """
        Given the path in the view, return the real index.
        If reverse = False, then path is index, otherwise however, the 
        index must be calculated so that the last index is the first path
        """
        return self.__corr[0] + self.__corr[1] * path

    def clear_map(self):
        """
        Clears out the index2hndl and the hndl2index
        """
        self._index2hndl = []
        self._hndl2index = {}
        self._fullhndl = self._index2hndl
        self._identical = True

    def get_path(self, handle):
        """
        Return the path from the passed handle.
        
        :param handle: the key of the object for which the path in the treeview
                        is needed
        :param type: an object handle
        :Returns: the path, or None if handle does not link to a path
        """
        index = self._hndl2index.get(handle)
        if index is None:
            return None
        else:
            return self.real_path(index)

    def get_handle(self, path):
        """
        Return the handle from the path. The path is assumed to be an integer.
        This is accomplished by indexing into the index2hndl
        
        Will raise IndexError if the maps are not filled yet, or if it is empty.
        Caller should take care of this if it allows calling with invalid path
        
        :param path: path as it appears in the treeview
        :type path: integer
        """
        return self._index2hndl[self.real_index(path)][1]

    def find_next_handle(self, handle):
        """
        Finds the next handle based off the passed handle. This is accomplished
        by finding the index associated with the handle, adding or substracting
        one to find the next index, then finding the handle associated with 
        that.
        
        :param handle: the key of the object for which the next handle shown
                        in the treeview is needed
        :param type: an object handle
        """
        index = self._hndl2index.get(handle)
        if self._reverse : 
            index -= 1
            if index < 0:
                # -1 does not raise IndexError, as -1 is last element. Catch.
                return None
        else:
            index += 1

        try:
            return self._index2hndl[index][1]
        except IndexError:
            return None
    
    def get_first_handle(self):
        """
        Return the first handle that must be shown (corresponding to path 0)
        
        Will raise IndexError if the maps are not filled yet, or if it is empty.
        Caller should take care of this if it allows calling with invalid path
        """
        return self._index2hndl[self.real_index(0)][1]

    def __len__(self):
        """
        Return the number of entries in the map.
        """
        return len(self._index2hndl)
    
    def max_rows(self):
        """
        Return maximum number of entries that might be present in the 
        map
        """
        return len(self._fullhndl)
    
    def insert(self, srtkey_hndl, allkeyonly=False):
        """
        Insert a node. Given is a tuple (sortkey, handle), and this is added
        in the correct place, while the hndl2index map is updated.
        Returns the path of the inserted row
        
        :param srtkey_hndl: the (sortkey, handle) tuple that must be inserted
        
        :Returns: path of the row inserted in the treeview
        :Returns type: integer or None
        """
        if not self._identical:
            bisect.insort_left(self._fullhndl, srtkey_hndl)
            if allkeyonly:
                #key is not part of the view
                return None
        insert_pos = bisect.bisect_left(self._index2hndl, srtkey_hndl)
        self._index2hndl.insert(insert_pos, srtkey_hndl)
        #make sure the index map is updated
        for hndl, index in self._hndl2index.iteritems():
            if index >= insert_pos:
                self._hndl2index[hndl] += 1
        self._hndl2index[srtkey_hndl[1]] = insert_pos
        #update self.__corr so it remains correct
        if self._reverse:
            self.__corr = (len(self._index2hndl) - 1, -1)
        return self.real_path(insert_pos)
    
    def delete(self, srtkey_hndl):
        """
        Delete the row with the given (sortkey, handle).
        This then rebuilds the hndl2index, subtracting one from each item
        greater than the deleted index.
        path of deleted row is returned
        If handle is not present, None is returned
        
        :param srtkey_hndl: the (sortkey, handle) tuple that must be inserted
        
        :Returns: path of the row deleted from the treeview
        :Returns type: integer or None
        """
        #remove it from the full list first
        if not self._identical:
            del_pos = bisect.bisect_left(self._fullhndl, srtkey_hndl)
            #check that indeed this is correct:
            if not self._fullhndl[del_pos][1] == srtkey_hndl[1]:
                raise KeyError, 'Handle %s not in list of all handles' %  \
                                                srtkey_hndl[1]
            del self._fullhndl[del_pos]
        #now remove it from the index maps
        handle = srtkey_hndl[1]
        try:
            index = self._hndl2index[handle]
        except KeyError:
            # key not present in the treeview
            return None
        del self._index2hndl[index]
        del self._hndl2index[handle]
        #update self.__corr so it remains correct
        delpath = self.real_path(index)
        if self._reverse:
            self.__corr = (len(self._index2hndl) - 1, -1)
        #update the handle2path map so it remains correct
        for key, val in self._hndl2index.iteritems():
            if val > index:
                self._hndl2index[key] -= 1
        return delpath

#-------------------------------------------------------------------------
#
# FlatBaseModel
#
#-------------------------------------------------------------------------
class FlatBaseModel(gtk.GenericTreeModel):
    """
    The base class for all flat treeview models. 
    It keeps a FlatNodeMap, and obtains data from database as needed
    """

    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING,
                 tooltip_column=None, search=None, skip=set(),
                 sort_map=None):
        cput = time.clock()
        gtk.GenericTreeModel.__init__(self)
        self.prev_handle = None
        self.prev_data = None
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
        else:
            self.sort_func = self.smap[scol]
        self.sort_col = scol
        self.skip = skip

        self.node_map = FlatNodeMap()
        self.set_search(search)
            
        self._reverse = (order == gtk.SORT_DESCENDING)
        self.tooltip_column = tooltip_column

        Config.client.notify_add("/apps/gramps/preferences/todo-color",
                                 self.__update_todo)
        Config.client.notify_add("/apps/gramps/preferences/custom-marker-color",
                                 self.__update_custom)
        Config.client.notify_add("/apps/gramps/preferences/complete-color",
                                 self.__update_complete)

        self.complete_color = Config.get(Config.COMPLETE_COLOR)
        self.todo_color = Config.get(Config.TODO_COLOR)
        self.custom_color = Config.get(Config.CUSTOM_MARKER_COLOR)
        self.rebuild_data()
        _LOG.debug(self.__class__.__name__ + ' __init__ ' +
                    str(time.clock() - cput) + ' sec')

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
                self.rebuild_data = self._rebuild_filter
            else:
                if search[1]:
                    # we have search[1] = (index, text_unicode, inversion)
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

    def __update_todo(self, client, cnxn_id, entry, data):
        """
        Callback if preferences todo color changes
        """
        self.todo_color = Config.get(Config.TODO_COLOR)
        
    def __update_custom(self, client, cnxn_id, entry, data):
        """
        Callback if preferences todo color changes
        """
        self.custom_color = Config.get(Config.CUSTOM_MARKER_COLOR)

    def __update_complete(self, client, cnxn_id, entry, data):
        """
        Callback if preferences todo color changes
        """
        self.complete_color = Config.get(Config.COMPLETE_COLOR)

    def total(self):
        """
        Total number of items that maximally can be shown
        """
        return self.node_map.max_rows()

    def displayed(self):
        """
        Number of items that are currently displayed
        """
        return len(self.node_map)

    def reverse_order(self):
        """
        reverse the sort order of the sort column
        """
        self._reverse = not self._reverse
        self.node_map.reverse_order()

    def sort_keys(self):
        """
        Return the (sort_key, handle) list of all data that can maximally 
        be shown. 
        This list is sorted ascending, via localized string sort. strxfrm 
        is used, which is apparently broken in Win ?? --> they should fix 
        base lib, we need strxfrm
        """
        # use cursor as a context manager
        with self.gen_cursor() as cursor:   
            #loop over database and store the sort field, and the handle
            return sorted( (conv_unicode_tosrtkey_ongtk(self.sort_func(data)),  
                            key) for key, data in cursor )

    def _rebuild_search(self, ignore=None):
        """ function called when view must be build, given a search text
            in the top search bar
        """
        if self.db.is_open():
            allkeys = self.node_map.full_srtkey_hndl_map()
            if not allkeys:
                allkeys = self.sort_keys()
            if self.search and self.search.text:
                dlist = [h for h  in allkeys \
                             if self.search.match(h[1], self.db) and \
                             h[1] not in self.skip and h[1] != ignore]
                ident = False
            elif ignore is None and not self.skip:
                #nothing to remove from the keys present
                ident = True
                dlist = allkeys
            else:
                ident = False
                dlist = [h for h in allkeys \
                             if h[1] not in self.skip and h[1] != ignore]
            self.node_map.set_path_map(dlist, allkeys, identical=ident, 
                                       reverse=self._reverse)
        else:
            self.node_map.clear_map()

    def _rebuild_filter(self, ignore=None):
        """ function called when view must be build, given filter options
            in the filter sidebar
        """
        if self.db.is_open():
            allkeys = self.node_map.full_srtkey_hndl_map()
            if not allkeys:
                allkeys = self.sort_keys()
            if self.search:
                ident = False
                if ignore is None:
                    dlist = self.search.apply(self.db, allkeys, tupleind=1)
                else:
                    dlist = self.search.apply(self.db, 
                                [ k for k in allkeys if k[1] != ignore],
                                tupleind=1)
            elif ignore is None :
                ident = True
                dlist = allkeys
            else:
                ident = False
                dlist = [ k for k in allkeys if k[1] != ignore ]
            self.node_map.set_path_map(dlist, allkeys, identical=ident, 
                                       reverse=self._reverse)
        else:
            self.node_map.clear_map()
        
    def add_row_by_handle(self, handle):
        """
        Add a row. This is called after object with handle is created.
        Row is only added if search/filter data is such that it must be shown
        """
        data = self.map(handle)
        insert_val = (locale.strxfrm(self.sort_func(data)), handle)
        if not self.search or \
                (self.search and self.search.match(handle, self.db)):
            #row needs to be added to the model
            insert_path = self.node_map.insert(insert_val)

            if insert_path is not None:
                node = self.get_iter(insert_path)
                self.row_inserted(insert_path, node)
        else:
            self.node_map.insert(insert_val, allkeyonly=True)

    def delete_row_by_handle(self, handle):
        """
        Delete a row, called after the object with handle is deleted
        """
        data = self.map(handle)
        delete_val = (locale.strxfrm(self.sort_func(data)), handle)
        delete_path = self.node_map.delete(delete_val)
        #delete_path is an integer from 0 to n-1
        if delete_path is not None: 
            self.row_deleted(delete_path)

    def update_row_by_handle(self, handle):
        """
        Update a row, called after the object with handle is changed
        """
        ## TODO: if sort key changes, this is not updated correctly ....
        path = self.node_map.get_path(handle)
        if path is not None:
            node = self.get_iter(path)
            self.row_changed(path, node)

    def on_get_flags(self):
        """
        Returns the GtkTreeModelFlags for this particular type of model
        See gtk.TreeModel
        """
        return gtk.TREE_MODEL_LIST_ONLY | gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        """
        Return the number of columns. Must be implemented in the child objects
        See gtk.TreeModel
        """
        raise NotImplementedError

    def on_get_path(self, handle):
        """
        Return the tree path (a tuple of indices at the various
        levels) for a particular iter. We use handles for unique key iters
        See gtk.TreeModel
        """
        return self.node_map.get_path(handle)

    def on_get_column_type(self, index):
        """
        See gtk.TreeModel
        """
        if index == self.tooltip_column:
            return object
        return str

    def on_get_iter(self, path):
        """
        See gtk.TreeModel
        """
        try:
            return self.node_map.get_handle(path[0])
        except IndexError:
            return None

    def on_get_value(self, handle, col):
        """
        See gtk.TreeModel. 
        col is the model column that is needed, not the visible column!
        """
        try:
            if handle != self.prev_handle:
                self.prev_data = self.map(str(handle))
                self.prev_handle = handle
            return self.fmap[col](self.prev_data)
        except:
            return u''

    def on_iter_next(self, handle):
        """
        Returns the next node at this level of the tree
        See gtk.TreeModel
        """
        return self.node_map.find_next_handle(handle)

    def on_iter_children(self, handle):
        """
        Return the first child of the node
        See gtk.TreeModel
        """
        if handle is None and len(self.node_map):
            return self.node_map.get_first_handle()
        return None

    def on_iter_has_child(self, handle):
        """
        Returns true if this node has children
        See gtk.TreeModel
        """
        if handle is None:
            return len(self.node_map) > 0
        return False

    def on_iter_n_children(self, handle):
        """
        See gtk.TreeModel
        """
        if handle is None:
            return len(self.node_map)
        return 0

    def on_iter_nth_child(self, handle, nth):
        """
        See gtk.TreeModel
        """
        if handle is None:
            return self.node_map.get_handle(nth)
        return None

    def on_iter_parent(self, handle):
        """
        Returns the parent of this node
        See gtk.TreeModel
        """
        return None
