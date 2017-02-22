#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
Package providing filtering framework for Gramps.
"""

class SearchFilter:
    def __init__(self, func, text, invert):
        self.func = func
        self.text = text.upper()
        self.invert = invert

    def match(self, handle, db):
        return self.invert ^ (self.func(handle).upper().find(self.text) != -1)

class ExactSearchFilter(SearchFilter):
    def __init__(self, func, text, invert):
        SearchFilter.__init__(self, func, text, invert)

    def match(self, handle, db):
        return self.invert ^ (self.func(handle).upper() == self.text.strip())

