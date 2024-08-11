#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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
DbBookmarks Class
"""

from ..utils.callback import Callback


# -------------------------------------------------------------------------
#
# DbBookmarks class
#
# -------------------------------------------------------------------------
class DbBookmarks(Callback):
    """
    Simple class for tracking a list of bookmarked objects
    """

    __signals__ = {"bookmark-list-changed": None}

    def __init__(self, default=None):
        super().__init__()
        self.bookmarks = default or []

    def load(self, new_list):
        """
        Quietly load the bookmark list.
        """
        self.bookmarks = list(new_list)

    def set(self, new_list):
        """
        Set the bookmark list.
        """
        self.bookmarks = list(new_list)
        self.emit("bookmark-list-changed")

    def get(self):
        """
        Return the bookmark list.
        """
        return self.bookmarks

    def append(self, item):
        """
        Append an item to the end of the list.
        """
        self.bookmarks.append(item)
        self.emit("bookmark-list-changed")

    def append_list(self, blist):
        """
        Append a list of items to the end of the list.
        """
        self.bookmarks += blist
        self.emit("bookmark-list-changed")

    def remove(self, item):
        """
        Remove an item from the list.
        """
        self.bookmarks.remove(item)
        self.emit("bookmark-list-changed")

    def pop(self, index):
        """
        Pop an item from the list.
        """
        item = self.bookmarks.pop(index)
        self.emit("bookmark-list-changed")
        return item

    def insert(self, pos, item):
        """
        Insert a new item into the list.
        """
        self.bookmarks.insert(pos, item)
        self.emit("bookmark-list-changed")

    def close(self):
        """
        Close the list by deleting it.
        """
        del self.bookmarks
