#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import time

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import pango

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from RelLib import *
import accent

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
COLUMN_NAME      = 0
COLUMN_VIEW      = 9
COLUMN_BOLD      = COLUMN_VIEW + 1
COLUMN_INT_ID    = COLUMN_BOLD + 1

_INT_ID_COL= 0
_ID_COL    = 1
_GENDER_COL= 2
_NAME_COL  = 3
_DEATH_COL = 6
_BIRTH_COL = 7
_FAMILY_COL= 9
_CHANGE_COL= 21

#-------------------------------------------------------------------------
#
# PeopleModel
#
#-------------------------------------------------------------------------
class PeopleModel(gtk.GenericTreeModel):

    def __init__(self,db):
        gtk.GenericTreeModel.__init__(self)

        self.db = db
        self.visible = {}
        self.top_visible = {}
        
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_gender,
            self.column_birth_day,
            self.column_birth_place,
            self.column_death_day,
            self.column_death_place,
            self.column_spouse,
            self.column_change,
            self.sort_name,
            ]

        maps = self.db.get_people_view_maps()
        if maps[0] != None and len(maps[0]) != 0:
            self.top_path2iter = maps[1]
            self.iter2path = maps[2]
            self.path2iter = maps[3]
            self.sname_sub = maps[4]
        else:
            self.rebuild_data()

#        self.connect('row-deleted',self.on_row_deleted)
#        self.connect('row-inserted',self.on_row_inserted)
    
    def rebuild_data(self):
        self.top_path2iter = []
        self.iter2path = {}
        self.path2iter = {}
        self.sname_sub = {}
        self.visible = {}
        self.top_visible = {}

        if not self.db.is_open():
            return

        for person_handle in self.db.get_person_handles(sort_handles=False):

            person = self.db.get_person_from_handle(person_handle)
            surname = unicode(person.get_primary_name().get_surname())

            if self.sname_sub.has_key(surname):
                self.sname_sub[surname].append(person_handle)
            else:
                self.sname_sub[surname] = [person_handle]

        name_list = self.db.get_surname_list()
        for name in name_list:
            if self.sname_sub.has_key(name):
                self.top_path2iter.append(name)
                val = 0
                entries = self.sname_sub[name]
                entries.sort(self.byname)
                for person_handle in entries:
                    tpl = (name,val)
                    self.iter2path[person_handle] = tpl
                    self.path2iter[tpl] = person_handle
                    val += 1
        self.db.set_people_view_maps(self.get_maps())

    def get_maps(self):
        return (None,
                self.top_path2iter,
                self.iter2path,
                self.path2iter,
                self.sname_sub)

    def byname(self,f,s):
        n1 = self.db.person_map.get(str(f))[_NAME_COL].get_sort_name()
        n2 = self.db.person_map.get(str(s))[_NAME_COL].get_sort_name()
        return cmp(n1,n2)

    def on_get_flags(self):
	'''returns the GtkTreeModelFlags for this particular type of model'''
	return gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        return COLUMN_INT_ID + 1

    def on_get_path(self, node):
	'''returns the tree path (a tuple of indices at the various
	levels) for a particular node.'''
        try:
            return (self.top_path2iter.index(node),)
        except ValueError:
            (surname,index) = self.iter2path[node]
            return (self.top_path2iter.index(surname),index)

    def on_get_column_type(self,index):
        """The visibility column is a boolean, the weight column is an integer,
        everthing else is a string"""
        if index == COLUMN_VIEW:
            return gobject.TYPE_BOOLEAN
        elif index == COLUMN_BOLD:
            return gobject.TYPE_INT
        else:
            return gobject.TYPE_STRING

    def on_get_iter(self, path):
        try:
            if len(path)==1: # Top Level
                return self.top_path2iter[path[0]]
            else: # Sublevel
                surname = self.top_path2iter[path[0]]
                return self.path2iter[(surname,path[1])]
        except:
            return None

    def on_get_value(self,iter,col):
        if col == COLUMN_INT_ID:
            return iter
        elif col == COLUMN_BOLD:
            if self.sname_sub.has_key(iter):
                return pango.WEIGHT_BOLD
            else:
                return pango.WEIGHT_NORMAL
        elif col == COLUMN_VIEW:
            if self.sname_sub.has_key(iter):
                return self.top_visible.has_key(iter)
            return self.visible.has_key(iter)
        elif self.sname_sub.has_key(iter):
            if col == 0:
                return iter
            else:
                return u''            
        else:
            try:
                return self.fmap[col](self.db.person_map[str(iter)])
            except:
                return u''

    def reset_visible(self):
        self.visible = {}
        self.top_visible = {}

    def set_visible(self,iter,val):
        try:
            col = self.iter2path[iter]
            self.top_visible[col[0]] = val
            self.visible[iter] = val
        except:
            self.visible[iter] = val

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
        try:
            path = self.top_path2iter.index(node)
            if path+1 == len(self.top_path2iter):
                return None
            return self.top_path2iter[path+1]
        except:
            (surname,val) = self.iter2path[node]
            return self.path2iter.get((surname,val+1))

    def on_iter_children(self,node):
        """Return the first child of the node"""
        if node == None:
            return self.top_path2iter[0]
        else:
            return self.path2iter.get((node,0))

    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
        if node == None:
            return len(self.sname_sub)
        if self.sname_sub.has_key(node) and len(self.sname_sub[node]) > 0:
            return gtk.TRUE
        return gtk.FALSE

    def on_iter_n_children(self,node):
        if node == None:
            return len(self.sname_sub)
        try:
            return len(self.sname_sub[node])
        except:
            return 0

    def on_iter_nth_child(self,node,n):
        if node == None:
            return self.top_path2iter.get(n)
        try:
            path = self.top_path2iter.index(node)
            return self.path2iter[(node,n)]
        except:
            return None

    def on_iter_parent(self, node):
	'''returns the parent of this node'''
        path = self.iter2path.get(node)
        if path:
            return path[0]
        return None

    def sort_name(self,data):
        return data[_NAME_COL].get_sort_name()

    def column_spouse(self,data):
	spouses_names = u""
        handle = data[0]
        for family_handle in data[_FAMILY_COL]:
            family = self.db.get_family_from_handle(family_handle)
            for spouse_id in [family.get_father_handle(), family.get_mother_handle()]:
                if not spouse_id:
                    continue
                if spouse_id == handle:
                    continue
                spouse = self.db.get_person_from_handle(spouse_id)
                if len(spouses_names) > 0:
                    spouses_names += ", "
                spouses_names += spouse.get_primary_name().get_regular_name()
	return spouses_names

    def column_name(self,data):
        return data[_NAME_COL].get_name()

    def column_id(self,data):
        return data[_ID_COL]

    def column_change(self,data):
        return time.asctime(time.localtime(data[_CHANGE_COL]))

    def column_gender(self,data):
        return _GENDER[data[_GENDER_COL]]

    def column_birth_day(self,data):
        if data[_BIRTH_COL]:
            return self.db.get_event_from_handle(data[_BIRTH_COL]).get_date()
        else:
            return u""

    def column_death_day(self,data):
        if data[_DEATH_COL]:
            return self.db.get_event_from_handle(data[_DEATH_COL]).get_date()
        else:
            return u""
        
    def column_birth_place(self,data):
        if data[_BIRTH_COL]:
            event = self.db.get_event_from_handle(data[_BIRTH_COL])
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

    def column_death_place(self,data):
        if data[_DEATH_COL]:
            event = self.db.get_event_from_handle(data[_DEATH_COL])
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

#     def add_person(self,person):
#         pid = person.get_handle()
#         need = 0
#         surname = person.get_primary_name().get_surname()
#         if self.sname_sub.has_key(surname):
#             self.sname_sub[surname].append(pid)
#         else:
#             self.sname_sub[surname] = [pid]

#             inscol = 0
#             sval = 0
#             name_list = self.db.get_surname_list()
#             for name in name_list:
#                 if self.sname_sub.has_key(name):
#                     self.top_path2iter[sval] = name
#                 if name == surname:
#                     inscol = (sval,)
#                     need = 1
#                 sval += 1

#         column = 0
#         val = 0
#         entries = self.sname_sub[surname]
#         entries.sort(self.byname)
#         for person_handle in entries:
#             tpl = (surname,val)
#             self.iter2path[person_handle] = tpl
#             self.path2iter[tpl] = person_handle
#             if person_handle == pid:
#                 column = val
#             val += 1

#         col = self.top_path2iter.index(surname)
#         mypath = (col[0],column)
#         if need:
#             self.row_inserted(inscol,self.get_iter(inscol))
#         self.row_inserted(mypath,self.get_iter(mypath))

#     def on_row_inserted(self,model,path,iter):
#         pass

#     def on_row_deleted(self,model,path):
#         surname = self.top_path2iter[path[0]]
#         pid = self.path2iter[(surname,path[1])]

#         for idval in self.sname_sub[surname]:
#             key = self.iter2path[idval]
#             del self.iter2path[idval]
#             del self.path2iter[key]
#         self.sname_sub[surname].remove(pid)

#         val = 0
#         entries = self.sname_sub[surname]
#         entries.sort(self.byname)
#         for person_handle in entries:
#             tpl = (surname,val)
#             self.iter2path[person_handle] = tpl
#             self.path2iter[tpl] = person_handle
#             val += 1
#         return 0

_GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]
