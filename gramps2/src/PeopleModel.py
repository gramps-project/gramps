#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

import gobject
import gtk
import gtk.glade
import gnome
import gnome.ui

COLUMN_NAME      = 0
COLUMN_NAME_SORT = 7

from RelLib import *

class PeopleModel(gtk.GenericTreeModel):

    def __init__(self,db,filter=None):

        gtk.GenericTreeModel.__init__(self)
        self.set_property("leak_references",0)

        self.db = db
        self.filter = filter
        
        self.rebuild_data()
        self.connect('row-inserted',self.on_row_inserted)
        self.connect('row-deleted',self.on_row_deleted)
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_gender,
            self.column_birth_day,
            self.column_birth_place,
            self.column_death_day,
            self.column_death_place,
            self.sort_name,
            ]

    def rebuild_data(self):
        self.top_iter2path = {}
        self.top_path2iter = {}
        self.iter2path = {}
        self.path2iter = {}
        self.sname_sub = {}

        if not self.db.is_open():
            return

        for person_id in self.db.get_person_keys():
            
            person = self.db.find_person_from_id(person_id)
            if self.filter and not self.filter(person):
                continue
            
            surname = unicode(person.get_primary_name().get_surname())

            if self.sname_sub.has_key(surname):
                self.sname_sub[surname].append(person_id)
            else:
                self.sname_sub[surname] = [person_id]

        sval = 0
        name_list = self.db.get_surnames()
        for name in name_list:
            if self.sname_sub.has_key(name):
                self.top_iter2path[name] = (sval,)
                self.top_path2iter[sval] = name
                val = 0
                entries = self.sname_sub[name]
                entries.sort(self.byname)
                for person_id in entries:
                    tpl = (name,val)
                    self.iter2path[person_id] = tpl
                    self.path2iter[tpl] = person_id
                    val += 1
                sval += 1

    def byname(self,f,s):
        n1 = self.db.person_map.get(str(f))[2].get_sort_name()
        n2 = self.db.person_map.get(str(s))[2].get_sort_name()
        return cmp(n1,n2)

    def on_row_inserted(self,obj,path,iter):
        self.rebuild_data()

    def on_row_deleted(self,obj,path):
        self.rebuild_data()

    def on_get_flags(self):
	'''returns the GtkTreeModelFlags for this particular type of model'''
	return 1

    def on_get_n_columns(self):
        return 8

    def on_get_path(self, node):
	'''returns the tree path (a tuple of indices at the various
	levels) for a particular node.'''
        if self.top_iter2path.has_key(node):
            return self.top_iter2path[node]
        else:
            (surname,index) = self.iter2path[node]
            return (self.top_iter2path[surname][0],index)

    def on_get_column_type(self,index):
        return gobject.TYPE_STRING

    def on_get_iter(self, path):
        try:
            if len(path)==1:
                return self.top_path2iter[path[0]]
            else:
                surname = self.top_path2iter[path[0]]
                return self.path2iter[(surname,path[1])]
        except:
            return None

    def on_get_value(self,iter,col):
        if self.top_iter2path.has_key(iter):
            if col == 0:
                return iter
            elif col == COLUMN_NAME_SORT:
                return iter.upper()
            else:
                return u''            
        else:
            val = self.fmap[col](self.db.person_map[str(iter)])
            return val

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
        if self.top_iter2path.has_key(node):
            path = self.top_iter2path[node]
            return self.top_path2iter.get(path[0]+1)
        else:
            (surname,val) = self.iter2path[node]
            return self.path2iter.get((surname,val+1))

    def on_iter_children(self,node):
        """Return the first child of the node"""
        if node == None:
            return self.top_path2iter[0]
        return self.path2iter.get((node,0))

    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
        if node == None:
            return len(top_iter2path) > 0
        if self.sname_sub.has_key(node) and len(self.sname_sub[node]) > 0:
            return 1
        return 0

    def on_iter_n_children(self,node):
        if node == None:
            return len(self.top_iter2path)
        if self.top_iter2path.has_key(node):
            return len(self.sname_sub[node])
        return 0

    def on_iter_nth_child(self,node,n):
        path = self.top_iter2path.get(node)
        if path:
            return self.path2iter.get((node,n))
        else:
            return None

    def on_iter_parent(self, node):
	'''returns the parent of this node'''
        path = self.iter2path.get(node)
        if path:
            return path[0]
        return None

    def sort_name(self,data):
        return data[2].get_sort_name()

    def column_name(self,data):
        return data[2].get_name()

    def column_id(self,data):
        return data[0]

    def column_gender(self,data):
        return _GENDER[data[1]]

    def column_birth_day(self,data):
        if data[6]:
            return self.db.find_event_from_id(data[6]).get_date()
        else:
            return u""

    def column_death_day(self,data):
        if data[5]:
            return self.db.find_event_from_id(data[5]).get_date()
        else:
            return u""
        
    def column_birth_place(self,data):
        if data[6]:
            event = self.db.find_event_from_id(data[5])
            if event:
                place_id = event.get_place_id()
                if place_id:
                    return self.db.find_place_from_id(place_id).get_title()
        return u""

    def column_death_place(self,data):
        if data[5]:
            event = self.db.find_event_from_id(data[5])
            if event:
                place_id = event.get_place_id()
                if place_id:
                    return self.db.find_place_from_id(place_id).get_title()
        return u""

_GENDER = [ _('female'), _('male'), _('unknown') ]
