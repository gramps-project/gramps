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

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.utils.lru import LRU
from gramps.gen.config import config

class BaseModel:

    # LRU cache size
    _CACHE_SIZE = config.get('interface.treemodel-cache-size')

    def __init__(self):
        self.lru_data = LRU(BaseModel._CACHE_SIZE)
        self.lru_path = LRU(BaseModel._CACHE_SIZE)

    def destroy(self):
        """
        Destroy the items in memory.
        """
        self.lru_data = None
        self.lru_path = None

    def clear_cache(self, handle=None):
        """
        Clear the LRU cache. Always clear lru_path, because paths may have
        changed.
        """
        if handle:
            if handle in self.lru_data:
                del self.lru_data[handle]
        else:
            self.lru_data.clear()
        # Invalidates all paths
        self.lru_path.clear()

    def get_cached_value(self, handle, col):
        """
        Get the value of a "col". col may be a number (position in a model)
        or a name (special value used by view).
        """
        if handle in self.lru_data and col in self.lru_data[handle]:
            #print("hit", handle, col)
            return (True, self.lru_data[handle][col])
        #print("MISS", handle, col)
        return (False, None)

    def set_cached_value(self, handle, col, data):
        """
        Set the data associated with handle + col.
        """
        if not self._in_build:
            if self.lru_data.count > 0:
                if handle not in self.lru_data:
                    self.lru_data[handle] = {}
                self.lru_data[handle][col] = data

    ## Cached Path's for TreeView:
    def get_cached_path(self, handle):
        """
        Saves the Gtk iter path.
        """
        if handle in self.lru_path:
            return (True, self.lru_path[handle])
        return (False, None)

    def set_cached_path(self, handle, path):
        """
        Set the Gtk iter path value.
        """
        if not self._in_build:
            self.lru_path[handle] = path

    def clear_path_cache(self):
        """
        Clear path cache for all.
        """
        self.lru_path.clear()
