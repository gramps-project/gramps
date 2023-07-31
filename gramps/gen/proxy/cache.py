#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (c) 2016 Gramps Development Team
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
Proxy class for the Gramps databases. Caches lookups from handles.
"""

from ..utils.lru import LRU


class CacheProxyDb:
    """
    A Proxy for a database with cached lookups on handles.

    Does not invalid caches. Should be used only in read-only
    places, and not where caches are altered.
    """

    def __init__(self, database):
        """
        CacheProxy will cache items based on their handle.

        Assumes all handles (regardless of type) are unique.
        Database is called self.db for consistency with other
        proxies.
        """
        self.db = database
        # Memory allocation is power of 2 where slots has to fit.
        # LRU uses one extra slot in its work, so set max to 2^17-1
        # otherwise we are just wasting memory
        self.cache_handle = LRU(131071)

    def __del__(self):
        self.cache_handle.clear()

    def __getattr__(self, attr):
        """
        If an attribute isn't found here, use the self.db
        version.
        """
        return getattr(self.db, attr)

    def clear_cache(self, handle=None):
        """
        Clears all caches if handle is None, or
        specific entry.
        """
        if handle:
            del self.cache_handle[handle]
        else:
            self.cache_handle.clear()

    def get_person_from_handle(self, handle):
        """
        Gets item from cache if it exists. Converts
        handles to string, for uniformity.
        """
        if handle not in self.cache_handle:
            self.cache_handle[handle] = self.db.get_person_from_handle(handle)
        return self.cache_handle[handle]

    def get_event_from_handle(self, handle):
        """
        Gets item from cache if it exists. Converts
        handles to string, for uniformity.
        """
        if handle not in self.cache_handle:
            self.cache_handle[handle] = self.db.get_event_from_handle(handle)
        return self.cache_handle[handle]

    def get_family_from_handle(self, handle):
        """
        Gets item from cache if it exists. Converts
        handles to string, for uniformity.
        """
        if handle not in self.cache_handle:
            self.cache_handle[handle] = self.db.get_family_from_handle(handle)
        return self.cache_handle[handle]

    def get_repository_from_handle(self, handle):
        """
        Gets item from cache if it exists. Converts
        handles to string, for uniformity.
        """
        if handle not in self.cache_handle:
            self.cache_handle[handle] = self.db.get_repository_from_handle(handle)
        return self.cache_handle[handle]

    def get_place_from_handle(self, handle):
        """
        Gets item from cache if it exists. Converts
        handles to string, for uniformity.
        """
        if handle not in self.cache_handle:
            self.cache_handle[handle] = self.db.get_place_from_handle(handle)
        return self.cache_handle[handle]

    def get_citation_from_handle(self, handle):
        """
        Gets item from cache if it exists. Converts
        handles to string, for uniformity.
        """
        if handle not in self.cache_handle:
            self.cache_handle[handle] = self.db.get_citation_from_handle(handle)
        return self.cache_handle[handle]

    def get_source_from_handle(self, handle):
        """
        Gets item from cache if it exists. Converts
        handles to string, for uniformity.
        """
        if handle not in self.cache_handle:
            self.cache_handle[handle] = self.db.get_source_from_handle(handle)
        return self.cache_handle[handle]

    def get_note_from_handle(self, handle):
        """
        Gets item from cache if it exists. Converts
        handles to string, for uniformity.
        """
        if handle not in self.cache_handle:
            self.cache_handle[handle] = self.db.get_note_from_handle(handle)
        return self.cache_handle[handle]

    def get_media_from_handle(self, handle):
        """
        Gets item from cache if it exists. Converts
        handles to string, for uniformity.
        """
        if handle not in self.cache_handle:
            self.cache_handle[handle] = self.db.get_media_from_handle(handle)
        return self.cache_handle[handle]

    def get_tag_from_handle(self, handle):
        """
        Gets item from cache if it exists. Converts
        handles to string, for uniformity.
        """
        if handle not in self.cache_handle:
            self.cache_handle[handle] = self.db.get_tag_from_handle(handle)
        return self.cache_handle[handle]
