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

#-------------------------------------------------------------------------
#
# class DbBookmarks
#
#-------------------------------------------------------------------------
class DbBookmarks:
    def __init__(self, default=[]):
        self.bookmarks = list(default) # want a copy (not an alias)

    def set(self, new_list):
        self.bookmarks = list(new_list)

    def get(self):
        return self.bookmarks

    def append(self, item):
        self.bookmarks.append(item)

    def append_list(self, blist):
        self.bookmarks += blist

    def remove(self, item):
        self.bookmarks.remove(item)

    def pop(self, item):
        return self.bookmarks.pop(item)

    def insert(self, pos, item):
        self.bookmarks.insert(pos, item)

    def close(self):
        del self.bookmarks
