#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2010       Nick Hall
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
This module provides the flat treemodel that is used for all flat treeviews.

For performance, Gramps does not use Gtk.TreeStore, as that would mean keeping
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

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
import logging
import bisect
from time import perf_counter

_LOG = logging.getLogger(".gui.basetreemodel")

# -------------------------------------------------------------------------
#
# GNOME/GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.filters import SearchFilter, ExactSearchFilter
from gramps.gen.const import GRAMPS_LOCALE as glocale
from .basemodel import BaseModel
from ...user import User
from gramps.gen.proxy.cache import CacheProxyDb

# -------------------------------------------------------------------------
#
# FlatNodeMap
#
# -------------------------------------------------------------------------

UEMPTY = ""


class FlatNodeMap:
    """
    A NodeMap for a flat treeview. In such a TreeView, the paths possible are
    0, 1, 2, ..., n-1, where n is the number of items to show. For the model
    it is needed to keep the Path to Iter mappings of the TreeView in memory

    The order of what is shown is based on the unique key: (sortkey, handle)
    Naming:
        * srtkey : key on which to sort
        * hndl   : handle of the object, makes it possible to retrieve the
                   object from the database. As handle is unique, it is used
                   in the iter for the TreeView
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

    ..Note: glocale.sort_key is applied to the underlying sort key,
            so as to have localized sort
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
        # We create a stamp to recognize invalid iterators. From the docs:
        # Set the stamp to be equal to your model's stamp, to mark the
        # iterator as valid. When your model's structure changes, you should
        # increment your model's stamp to mark all older iterators as invalid.
        # They will be recognised as invalid because they will then have an
        # incorrect stamp.
        self.stamp = 0

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self._index2hndl = None
        self._fullhndl = None
        self._hndl2index = None

    def set_path_map(self, index2hndllist, fullhndllist, identical=True, reverse=False):
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
                    a subset of all possible data.
        :type index2hndllist: a list of (sortkey, handle) tuples
        :param fullhndllist: the list of all possilbe ascending sorted
                    (sortkey, handle) values as they will appear in the flat
                     treeview if all data is shown.
        :type fullhndllist: a list of (sortkey, handl) tuples
        :param identical: identify if index2hndllist and fullhndllist are the
                        same list, so only one is kept in memory.
        :type identical: bool
        """
        self.stamp += 1
        self._index2hndl = index2hndllist
        self._hndl2index = {}
        self._identical = identical
        self._fullhndl = self._index2hndl if identical else fullhndllist
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
            # if hndl2index is build already, invert order, otherwise keep
            # requested order
            self._reverse = not self._reverse
        if self._reverse:
            self.__corr = (len(self._index2hndl) - 1, -1)
        else:
            self.__corr = (0, 1)
        if not self._hndl2index:
            self._hndl2index = dict(
                (key[1], index) for index, key in enumerate(self._index2hndl)
            )

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

    def get_path(self, iter):
        """
        Return the path from the passed iter.

        :param handle: the key of the object for which the path in the treeview
                        is needed
        :type handle: an object handle
        :Returns: the path, or None if handle does not link to a path
        """
        index = iter.user_data
        ##GTK3: user data may only be an integer, we store the index
        ##PROBLEM: pygobject 3.8 stores 0 as None, we need to correct
        ##        when using user_data for that!
        ##upstream bug: https://bugzilla.gnome.org/show_bug.cgi?id=698366
        if index is None:
            index = 0
        return Gtk.TreePath((self.real_path(index),))

    def get_path_from_handle(self, handle):
        """
        Return the path from the passed handle

        :param handle: the key of the object for which the path in the treeview
                        is needed
        :type handle: an object handle
        :Returns: the path, or None if handle does not link to a path
        """
        index = self._hndl2index.get(handle)
        if index is None:
            return None

        return Gtk.TreePath((self.real_path(index),))

    def get_sortkey(self, handle):
        """
        Return the sortkey used for the passed handle.

        :param handle: the key of the object for which the sortkey
                        is needed
        :type handle: an object handle
        :Returns: the sortkey, or None if handle is not present
        """
        index = self._hndl2index.get(handle)
        return None if index is None else self._index2hndl[index][0]

    def new_iter(self, handle):
        """
        Return a new iter containing the handle
        """
        iter = Gtk.TreeIter()
        iter.stamp = self.stamp
        ##GTK3: user data may only be an integer, we store the index
        ##PROBLEM: pygobject 3.8 stores 0 as None, we need to correct
        ##        when using user_data for that!
        ##upstream bug: https://bugzilla.gnome.org/show_bug.cgi?id=698366
        iter.user_data = self._hndl2index[handle]
        return iter

    def get_iter(self, path):
        """
        Return an iter from the path. The path is assumed to be an integer.
        This is accomplished by indexing into the index2hndl
        iters are always created afresh

        Will raise IndexError if the maps are not filled yet, or if it is empty.
        Caller should take care of this if it allows calling with invalid path

        :param path: path as it appears in the treeview
        :type path: integer
        """
        iter = self.new_iter(self._index2hndl[self.real_index(path)][1])
        return iter

    def get_handle(self, path):
        """
        Return the handle from the path. The path is assumed to be an integer.
        This is accomplished by indexing into the index2hndl

        Will raise IndexError if the maps are not filled yet, or if it is empty.
        Caller should take care of this if it allows calling with invalid path

        :param path: path as it appears in the treeview
        :type path: integer
        :return handle: unicode form of the handle
        """
        return self._index2hndl[self.real_index(path)][1]

    def iter_next(self, iter):
        """
        Increments the iter y finding the index associated with the iter,
        adding or substracting one.
        False is returned if no next handle

        :param iter: Gtk.TreeModel iterator
        :param type: Gtk.TreeIter
        """
        index = iter.user_data
        if index is None:
            ##GTK3: user data may only be an integer, we store the index
            ##PROBLEM: pygobject 3.8 stores 0 as None, we need to correct
            ##        when using user_data for that!
            ##upstream bug: https://bugzilla.gnome.org/show_bug.cgi?id=698366
            index = 0

        if self._reverse:
            index -= 1
            if index < 0:
                # -1 does not raise IndexError, as -1 is last element. Catch.
                return False
        else:
            index += 1
            if index >= len(self._index2hndl):
                return False
        iter.user_data = index
        return True

    def get_first_iter(self):
        """
        Return the first handle that must be shown (corresponding to path 0)

        Will raise IndexError if the maps are not filled yet, or if it is empty.
        Caller should take care of this if it allows calling with invalid path
        """
        return self.get_iter(0)

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
        :type srtkey_hndl: sortkey key already transformed by self.sort_func, object handle

        :Returns: path of the row inserted in the treeview
        :Returns type: Gtk.TreePath or None
        """
        if srtkey_hndl[1] in self._hndl2index:
            print(
                ("WARNING: Attempt to add row twice to the model (%s)" % srtkey_hndl[1])
            )
            return
        if not self._identical:
            bisect.insort_left(self._fullhndl, srtkey_hndl)
            if allkeyonly:
                # key is not part of the view
                return None
        insert_pos = bisect.bisect_left(self._index2hndl, srtkey_hndl)
        self._index2hndl.insert(insert_pos, srtkey_hndl)
        # make sure the index map is updated
        for srt_key, hndl in self._index2hndl[insert_pos + 1 :]:
            self._hndl2index[hndl] += 1
        self._hndl2index[srtkey_hndl[1]] = insert_pos
        # update self.__corr so it remains correct
        if self._reverse:
            self.__corr = (len(self._index2hndl) - 1, -1)
        return Gtk.TreePath((self.real_path(insert_pos),))

    def delete(self, handle):
        """
        Delete the row with the given (handle).
        This then rebuilds the hndl2index, subtracting one from each item
        greater than the deleted index.
        path of deleted row is returned
        If handle is not present, None is returned

        :param srtkey_hndl: the (sortkey, handle) tuple that must be inserted

        :Returns: path of the row deleted from the treeview
        :Returns type: Gtk.TreePath or None
        """
        # remove it from the full list first
        if not self._identical:
            for indx, hndle in enumerate(self._fullhndl):
                if hndle[1] == handle:
                    del self._fullhndl[indx]
                    break
        # now remove it from the index maps
        try:
            index = self._hndl2index[handle]
        except KeyError:
            # key not present in the treeview
            return None
        del self._index2hndl[index]
        del self._hndl2index[handle]
        # update self.__corr so it remains correct
        delpath = self.real_path(index)
        if self._reverse:
            self.__corr = (len(self._index2hndl) - 1, -1)
        # update the handle2path map so it remains correct
        for dummy_srt_key, hndl in self._index2hndl[index:]:
            self._hndl2index[hndl] -= 1
        return Gtk.TreePath((delpath,))


# -------------------------------------------------------------------------
#
# FlatBaseModel
#
# -------------------------------------------------------------------------
class FlatBaseModel(GObject.GObject, Gtk.TreeModel, BaseModel):
    """
    The base class for all flat treeview models.
    It keeps a FlatNodeMap, and obtains data from database as needed
    ..Note: glocale.sort_key is applied to the underlying sort key,
            so as to have localized sort
    """

    def __init__(
        self,
        db,
        uistate,
        scol=0,
        order=Gtk.SortType.ASCENDING,
        search=None,
        skip=set(),
        sort_map=None,
    ):
        cput = perf_counter()
        GObject.GObject.__init__(self)
        BaseModel.__init__(self)
        self.uistate = uistate
        self.user = User(parent=uistate.window, uistate=uistate)
        # inheriting classes must set self.map to obtain the data
        self.prev_handle = None
        self.prev_data = None

        # GTK3 We leak ref, yes??
        # self.set_property("leak_references", False)

        self.db = db
        # normally sort on first column, so scol=0
        if sort_map:
            # sort_map is the stored order of the columns and if they are
            # enabled or not. We need to store on scol of that map
            self.sort_map = [f for f in sort_map if f[0]]
            # we need the model col, that corresponds with scol
            col = self.sort_map[scol][1]
        else:
            col = scol
        # get the function that maps data to sort_keys
        self.sort_func = lambda x: glocale.sort_key(self.smap[col](x))
        self.sort_col = scol
        self.skip = skip
        self._in_build = False

        self.node_map = FlatNodeMap()
        self.set_search(search)

        self._reverse = order == Gtk.SortType.DESCENDING

        self.rebuild_data()
        _LOG.debug(
            self.__class__.__name__ + " __init__ " + str(perf_counter() - cput) + " sec"
        )

    def destroy(self):
        """
        Unset all elements that prevent garbage collection
        """
        BaseModel.destroy(self)
        self.db = None
        self.sort_func = None
        if self.node_map:
            self.node_map.destroy()
        self.node_map = None
        self.rebuild_data = None
        self.search = None

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
                # following is None if no data given in filter sidebar
                self.search = search[1]
                self.rebuild_data = self._rebuild_filter
            else:
                if search[1]:  # Search from topbar in columns
                    # we have search[1] = (index, text_unicode, inversion)
                    col = search[1][0]
                    text = search[1][1]
                    inv = search[1][2]
                    func = lambda x: self._get_value(x, col) or UEMPTY
                    if search[2]:
                        self.search = ExactSearchFilter(func, text, inv)
                    else:
                        self.search = SearchFilter(func, text, inv)
                else:
                    self.search = None
                self.rebuild_data = self._rebuild_search
        else:
            self.search = None
            self.rebuild_data = self._rebuild_search

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

    def color_column(self):
        """
        Return the color column.
        """
        return None

    def sort_keys(self):
        """
        Return the (sort_key, handle) list of all data that can maximally
        be shown.
        This list is sorted ascending, via localized string sort.
        """
        # use cursor as a context manager
        with self.gen_cursor() as cursor:
            # loop over database and store the sort field, and the handle
            srt_keys = [(self.sort_func(data), key) for key, data in cursor]
            srt_keys.sort()
            return srt_keys

    def _rebuild_search(self, ignore=None):
        """function called when view must be build, given a search text
        in the top search bar
        """
        self.clear_cache()
        self._in_build = True
        if (self.db is not None) and self.db.is_open():
            allkeys = self.node_map.full_srtkey_hndl_map()
            if not allkeys:
                allkeys = self.sort_keys()
            if self.search and self.search.text:
                dlist = [
                    h
                    for h in allkeys
                    if self.search.match(h[1], self.db)
                    and h[1] not in self.skip
                    and h[1] != ignore
                ]
                ident = False
            elif ignore is None and not self.skip:
                # nothing to remove from the keys present
                ident = True
                dlist = allkeys
            else:
                ident = False
                dlist = [h for h in allkeys if h[1] not in self.skip and h[1] != ignore]
            self.node_map.set_path_map(
                dlist, allkeys, identical=ident, reverse=self._reverse
            )
        else:
            self.node_map.clear_map()
        self._in_build = False

    def _rebuild_filter(self, ignore=None):
        """function called when view must be build, given filter options
        in the filter sidebar
        """
        self.clear_cache()
        self._in_build = True
        if (self.db is not None) and self.db.is_open():
            cdb = CacheProxyDb(self.db)
            allkeys = self.node_map.full_srtkey_hndl_map()
            if not allkeys:
                allkeys = self.sort_keys()
            if self.search:
                ident = False
                if ignore is None:
                    dlist = self.search.apply(cdb, allkeys, tupleind=1, user=self.user)
                else:
                    dlist = self.search.apply(
                        cdb, [k for k in allkeys if k[1] != ignore], tupleind=1
                    )
            elif ignore is None:
                ident = True
                dlist = allkeys
            else:
                ident = False
                dlist = [k for k in allkeys if k[1] != ignore]
            self.node_map.set_path_map(
                dlist, allkeys, identical=ident, reverse=self._reverse
            )
        else:
            self.node_map.clear_map()
        self._in_build = False

    def add_row_by_handle(self, handle):
        """
        Add a row. This is called after object with handle is created.
        Row is only added if search/filter data is such that it must be shown
        """
        assert isinstance(handle, str)
        if self.node_map.get_path_from_handle(handle) is not None:
            return  # row is already displayed
        data = self.map(handle)
        insert_val = (self.sort_func(data), handle)
        if not self.search or (self.search and self.search.match(handle, self.db)):
            # row needs to be added to the model
            insert_path = self.node_map.insert(insert_val)

            if insert_path is not None:
                node = self.do_get_iter(insert_path)[1]
                self.row_inserted(insert_path, node)
        else:
            self.node_map.insert(insert_val, allkeyonly=True)

    def delete_row_by_handle(self, handle):
        """
        Delete a row, called after the object with handle is deleted
        """
        delete_path = self.node_map.delete(handle)
        # delete_path is an integer from 0 to n-1
        if delete_path is not None:
            self.clear_cache(handle)
            self.row_deleted(delete_path)

    def update_row_by_handle(self, handle):
        """
        Update a row, called after the object with handle is changed
        """
        if self.node_map.get_path_from_handle(handle) is None:
            return  # row is not currently displayed
        self.clear_cache(handle)
        oldsortkey = self.node_map.get_sortkey(handle)
        newsortkey = self.sort_func(self.map(handle))
        if oldsortkey is None or oldsortkey != newsortkey:
            # or the changed object is not present in the view due to filtering
            # or the order of the object must change.
            self.delete_row_by_handle(handle)
            self.add_row_by_handle(handle)
        else:
            # the row is visible in the view, is changed, but the order is fixed
            path = self.node_map.get_path_from_handle(handle)
            node = self.do_get_iter(path)[1]
            self.row_changed(path, node)

    def get_iter_from_handle(self, handle):
        """
        Get the iter for a gramps handle.
        """
        if self.node_map.get_path_from_handle(handle) is None:
            return None
        return self.node_map.new_iter(handle)

    def get_handle_from_iter(self, iter):
        """
        Get the gramps handle for an iter.
        """
        index = iter.user_data
        if index is None:
            ##GTK3: user data may only be an integer, we store the index
            ##PROBLEM: pygobject 3.8 stores 0 as None, we need to correct
            ##        when using user_data for that!
            ##upstream bug: https://bugzilla.gnome.org/show_bug.cgi?id=698366
            index = 0
        path = self.node_map.real_path(index)
        return self.node_map.get_handle(path)

    # The following implement the public interface of Gtk.TreeModel

    def do_get_flags(self):
        """
        Returns the GtkTreeModelFlags for this particular type of model
        See Gtk.TreeModel
        """
        # print 'do_get_flags'
        return Gtk.TreeModelFlags.LIST_ONLY  # | Gtk.TreeModelFlags.ITERS_PERSIST

    def do_get_n_columns(self):
        """Internal method. Don't inherit"""
        return self.on_get_n_columns()

    def on_get_n_columns(self):
        """
        Return the number of columns. Must be implemented in the child objects
        See Gtk.TreeModel. Inherit as needed
        """
        # print 'do_get_n_col'
        raise NotImplementedError

    def do_get_path(self, iter):
        """
        Return the tree path (a tuple of indices at the various
        levels) for a particular iter. We use handles for unique key iters
        See Gtk.TreeModel
        """
        # print 'do_get_path', iter
        return self.node_map.get_path(iter)

    def do_get_column_type(self, index):
        """
        See Gtk.TreeModel
        """
        # print 'do_get_col_type'
        return str

    def do_get_iter_first(self):
        # print 'get iter first'
        raise NotImplementedError

    def do_get_iter(self, path):
        """
        See Gtk.TreeModel
        """
        # print 'do_get_iter', path
        for p in path:
            break
        try:
            return True, self.node_map.get_iter(p)
        except IndexError:
            return False, Gtk.TreeIter()

    def _get_value(self, handle, col):
        """
        Given handle and column, return unicode value in the column
        We need this to search in the column in the GUI
        """
        if handle != self.prev_handle:
            cached, data = self.get_cached_value(handle, col)
            if not cached:
                data = self.map(handle)
                self.set_cached_value(handle, col, data)
            if data is None:
                # object is no longer present
                return ""
            self.prev_data = data
            self.prev_handle = handle
        return self.fmap[col](self.prev_data)

    def do_get_value(self, iter, col):
        """
        See Gtk.TreeModel.
        col is the model column that is needed, not the visible column!
        """
        # print ('do_get_val', iter, iter.user_data, col)
        index = iter.user_data
        if index is None:
            ##GTK3: user data may only be an integer, we store the index
            ##PROBLEM: pygobject 3.8 stores 0 as None, we need to correct
            ##        when using user_data for that!
            ##upstream bug: https://bugzilla.gnome.org/show_bug.cgi?id=698366
            index = 0
        handle = self.node_map._index2hndl[index][1]
        val = self._get_value(handle, col)
        # print 'val is', val, type(val)

        return val

    def do_iter_previous(self, iter):
        # print 'do_iter_previous'
        raise NotImplementedError

    def do_iter_next(self, iter):
        """
        Sets iter to the next node at this level of the tree
        See Gtk.TreeModel
        """
        return self.node_map.iter_next(iter)

    def do_iter_children(self, iterparent):
        """
        Return the first child of the node
        See Gtk.TreeModel
        """
        # print 'do_iter_children'
        print("ERROR: iter children, should not be called in flat base!!")
        raise NotImplementedError
        if handle is None and len(self.node_map):
            return self.node_map.get_first_handle()
        return None

    def do_iter_has_child(self, iter):
        """
        Returns true if this node has children
        See Gtk.TreeModel
        """
        # print 'do_iter_has_child'
        print("ERROR: iter has_child", iter, "should not be called in flat base")
        return False
        if handle is None:
            return len(self.node_map) > 0
        return False

    def do_iter_n_children(self, iter):
        """
        See Gtk.TreeModel
        """
        # print 'do_iter_n_children'
        print("ERROR: iter_n_children", iter, "should not be called in flat base")
        return 0
        if handle is None:
            return len(self.node_map)
        return 0

    def do_iter_nth_child(self, iter, nth):
        """
        See Gtk.TreeModel
        """
        # print 'do_iter_nth_child', iter, nth
        if iter is None:
            return True, self.node_map.get_iter(nth)
        return False, None

    def do_iter_parent(self, iter):
        """
        Returns the parent of this node
        See Gtk.TreeModel
        """
        # print 'do_iter_parent'
        return False, None
