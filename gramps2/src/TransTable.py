#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Donald N. Allingham
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

from gettext import gettext as _

class TransTable:

    def __init__(self,map={}):
        self.map = {}
        self.rmap = {}

        if type(map) == type([]):
            for key in map:
                val = unicode(_(key))
                self.map[key] = val
                self.rmap[val] = unicode(key)
        else:
            for key in map.keys():
                val = unicode(map[key])
                self.map[key] = val
                self.rmap[val] = unicode(key)
            
    def add_pair(self,first,second):
        first = unicode(first)
        second = unicode(second)
        self.map[first] = second
        self.rmap[second] = first

    def find_value(self,key):
        return unicode(self.map.setdefault(key,_(key)))

    def find_key(self,value):
        value = unicode(value)
        return unicode(self.rmap.setdefault(value,value))

    def has_key(self,key):
        return self.map.has_key(key)

    def has_value(self,value):
        value = unicode(value)
        return self.rmap.has_key(value)

    def get_values(self):
        return self.map.values()

    
