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
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .lru import LRU

class BaseModel(object):

    # LRU cache size
    _CACHE_SIZE = 10000 # 250

    def __init__(self):
        self.lru_data  = LRU(BaseModel._CACHE_SIZE)
        self.lru_path = LRU(BaseModel._CACHE_SIZE)

    def destroy(self):
        """
        """
        self.lru_data = None
        self.lru_path = None

    def clear_cache(self, handle=None):
        """
        Clear the LRU cache.
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
        """
        if handle in self.lru_data and col in self.lru_data[handle]:
            return (True, self.lru_data[handle][col])
        return (False, None)

    def set_cached_value(self, handle, col, data):
        """
        """
        if not self._in_build:
            if handle not in self.lru_data:
                self.lru_data[handle] = {}
            self.lru_data[handle][col] = data
    
    ## Cached Path's for TreeView:
    def get_cached_path(self, handle):
        """
        """
        if handle in self.lru_path:
            return (True, self.lru_path[handle])
        return (False, None)

    def set_cached_path(self, handle, path):
        """
        """
        if not self._in_build:
            self.lru_path[handle] = path
