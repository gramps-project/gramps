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
import locale

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
import NameDisplay

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------

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

    def __init__(self,db,data_filter=None):
        gtk.GenericTreeModel.__init__(self)

        self.db = db
        self.visible = {}
        self.top_visible = {}
        self.rebuild_data(data_filter)
    
    def rebuild_data(self,data_filter=None):
        if data_filter:
            self.data_filter = data_filter
        temp_top_path2iter = []
        temp_iter2path = {}
        temp_path2iter = {}
        self.sname_sub = {}

        if not self.db.is_open():
            return

        if data_filter:
            handle_list = self.db.get_person_handles(sort_handles=False)
            keys = data_filter.apply(self.db,handle_list)
            del handle_list
        else:
            keys = self.db.get_person_handles(sort_handles=False)
            
        for person_handle in keys:
            person = self.db.get_person_from_handle(person_handle)
            grp_as = person.get_primary_name().get_group_as()
            sn = person.get_primary_name().get_surname()
            if grp_as:
                surname = grp_as
            else:
                surname = self.db.get_name_group_mapping(sn)

            if self.sname_sub.has_key(surname):
                self.sname_sub[surname].append(person_handle)
            else:
                self.sname_sub[surname] = [person_handle]
        
        temp_top_path2iter = self.sname_sub.keys()
        temp_top_path2iter.sort(locale.strcoll)
        for name in temp_top_path2iter:

            slist = []
            for handle in self.sname_sub[name]:
                n = self.db.person_map.get(handle)[_NAME_COL].get_sort_name()
                slist.append((n,handle))
            slist.sort(self.byname)
            entries = map(lambda x: x[1], slist)
            val = 0
            for person_handle in entries:
                tpl = (name,val)
                temp_iter2path[person_handle] = tpl
                temp_path2iter[tpl] = person_handle
                val += 1

        self.top_path2iter = temp_top_path2iter
        self.iter2path = temp_iter2path
        self.path2iter = temp_path2iter

    def byname(self,f,s):
        return locale.strcoll(f[0],s[0])

    def on_get_flags(self):
	'''returns the GtkTreeModelFlags for this particular type of model'''
	return gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        return len(COLUMN_DEFS)

    def on_get_path(self, node):
	'''returns the tree path (a tuple of indices at the various
	levels) for a particular node.'''
        try:
            return (self.top_path2iter.index(node),)
        except:
            (surname,index) = self.iter2path[node]
            return (self.top_path2iter.index(surname),index)

    def on_get_column_type(self,index):
         # return column data-type, from table
         return COLUMN_DEFS[index][COLUMN_DEF_TYPE]

    def on_get_iter(self, path):
        try:
            if len(path)==1: # Top Level
                return self.top_path2iter[path[0]]
            else: # Sublevel
                surname = self.top_path2iter[path[0]]
                return self.path2iter[(surname,path[1])]
        except:
            return None

    def on_get_value(self,node,col):
        # test for header or data row-type
        if self.sname_sub.has_key(node):
            # test for 'header' column being empty (most are)
            if not COLUMN_DEFS[col][COLUMN_DEF_HEADER]:
                return u''
            # return values for 'header' row, calling a function
            # according to column_defs table
            val = COLUMN_DEFS[col][COLUMN_DEF_HEADER](self,node)
            return val
        else:
            # return values for 'data' row, calling a function
            # according to column_defs table
            try:
                return COLUMN_DEFS[col][COLUMN_DEF_LIST](self,self.db.person_map[str(node)],node)
            except:
                return u'error'

    def reset_visible(self):
        pass

    def set_visible(self,node,val):
        pass

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
            return True
        return False

    def on_iter_n_children(self,node):
        if node == None:
            return len(self.sname_sub)
        try:
            return len(self.sname_sub[node])
        except:
            return 0

    def on_iter_nth_child(self,node,n):
        try:
            if node == None:
                return self.top_path2iter[n]
            try:
                return self.path2iter[(node,n)]
            except:
                return None
        except IndexError:
            return None

    def on_iter_parent(self, node):
	'''returns the parent of this node'''
        path = self.iter2path.get(node)
        if path:
            return path[0]
        return None

    def column_sort_name(self,data,node):
        return data[_NAME_COL].get_sort_name()

    def column_spouse(self,data,node):
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
                spouses_names += NameDisplay.displayer.display(spouse)
	return spouses_names

    def column_name(self,data,node):
        return NameDisplay.displayer.sorted_name(data[_NAME_COL])

    def column_id(self,data,node):
        return data[_ID_COL]

    def column_change(self,data,node):
        return time.asctime(time.localtime(data[_CHANGE_COL]))

    def column_gender(self,data,node):
        return _GENDER[data[_GENDER_COL]]

    def column_birth_day(self,data,node):
        if data[_BIRTH_COL]:
            return self.db.get_event_from_handle(data[_BIRTH_COL]).get_date()
        else:
            return u""

    def column_death_day(self,data,node):
        if data[_DEATH_COL]:
            return self.db.get_event_from_handle(data[_DEATH_COL]).get_date()
        else:
            return u""
        
    def column_birth_place(self,data,node):
        if data[_BIRTH_COL]:
            event = self.db.get_event_from_handle(data[_BIRTH_COL])
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

    def column_death_place(self,data,node):
        if data[_DEATH_COL]:
            event = self.db.get_event_from_handle(data[_DEATH_COL])
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

    def column_int_id(self,data,node):
        return node

    def column_header(self,node):
        return node

    def column_header_view(self,node):
        return True

_GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]

# table of column definitions
# (unless this is declared after the PeopleModel class, an error is thrown)
COLUMN_DEFS = [
    # data column (method)          header column (method)         column data type 
    (PeopleModel.column_name,       PeopleModel.column_header,     gobject.TYPE_STRING),
    (PeopleModel.column_id,         None,                          gobject.TYPE_STRING),
    (PeopleModel.column_gender,     None,                          gobject.TYPE_STRING),
    (PeopleModel.column_birth_day,  None,                          gobject.TYPE_STRING),
    (PeopleModel.column_birth_place,None,                          gobject.TYPE_STRING),
    (PeopleModel.column_death_day,  None,                          gobject.TYPE_STRING),
    (PeopleModel.column_death_place,None,                          gobject.TYPE_STRING),
    (PeopleModel.column_spouse,     None,                          gobject.TYPE_STRING),
    (PeopleModel.column_change,     None,                          gobject.TYPE_STRING),
    # the order of the above columns must match PeopleView.column_names

    # these columns are hidden, and must always be last in the list
    (PeopleModel.column_sort_name,  None,                          gobject.TYPE_STRING),
    (PeopleModel.column_int_id,     None,                          gobject.TYPE_STRING),
    ]

# dynamic calculation of column indices, for use by various Views
COLUMN_INT_ID = len(COLUMN_DEFS) - 1

# indices into main column definition table
COLUMN_DEF_LIST = 0
COLUMN_DEF_HEADER = 1
COLUMN_DEF_TYPE = 2
