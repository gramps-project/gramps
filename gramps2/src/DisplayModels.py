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

import time

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gobject
import gtk

_GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]

#-------------------------------------------------------------------------
#
# BaseModel
#
#-------------------------------------------------------------------------
class BaseModel(gtk.GenericTreeModel):

    def __init__(self,db):
        gtk.GenericTreeModel.__init__(self)
        self.set_property("leak_references",False)
        self.db = db
        self.rebuild_data()

    def sort_keys(self):
        return []

    def rebuild_data(self):
        if self.db.is_open():
            self.datalist = self.sort_keys()
        else:
            self.datalist = []
        
    def on_row_inserted(self,obj,path,node):
        self.rebuild_data()

    def add_row_by_handle(self,handle):
        self.datalist = self.sort_keys()
        index = self.datalist.index(handle)
        node = self.get_iter(index)
        self.row_inserted(index,node)

    def delete_row_by_handle(self,handle):
        index = self.datalist.index(handle)
        del self.datalist[index]
        self.row_deleted(index)

    def update_row_by_handle(self,handle):
        index = self.datalist.index(handle)
        node = self.get_iter(index)
        self.row_changed(index,node)

    def on_get_flags(self):
	'''returns the GtkTreeModelFlags for this particular type of model'''
	return gtk.TREE_MODEL_LIST_ONLY | gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        return 1

    def on_get_path(self, node):
	'''returns the tree path (a tuple of indices at the various
	levels) for a particular node.'''
        return self.datalist.index(node[0])

    def on_get_column_type(self,index):
        return gobject.TYPE_STRING

    def on_get_iter(self, path):
        try:
            return self.datalist[path[0]]
        except IndexError:
            return None

    def on_get_value(self,node,col):
        try:
            return self.fmap[col](self.map[str(node)])
        except:
            return u''

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
        try:
            return self.datalist[self.datalist.index(node)+1]
        except IndexError:
            return None

    def on_iter_children(self,node):
        """Return the first child of the node"""
        if node == None:
            return self.datalist[0]
        return None

    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
        if node == None:
            return len(self.datalist) > 0
        return False

    def on_iter_n_children(self,node):
        if node == None:
            return len(self.datalist)
        return 0

    def on_iter_nth_child(self,node,n):
        if node == None:
            return self.datalist[n]
        return None

    def on_iter_parent(self, node):
	'''returns the parent of this node'''
        return None

#-------------------------------------------------------------------------
#
# ChildModel
#
#-------------------------------------------------------------------------
class ChildModel(gtk.ListStore):

    def __init__(self,child_list,db):
        gtk.ListStore.__init__(self,int,str,str,str,str,str,str,str,str,str,int,int)
        self.db = db
        index = 1
        for child_handle in child_list:
            child = db.get_person_from_handle(child_handle)
            self.append(row=[index,
                             child.get_gramps_id(),
                             child.get_primary_name().get_name(),
                             _GENDER[child.get_gender()],
                             self.column_birth_day(child),
                             self.column_death_day(child),
                             self.column_birth_place(child),
                             self.column_death_place(child),
                             child.get_handle(),
                             child.get_primary_name().get_sort_name(),
                             self.column_birth_sort(child),
                             self.column_death_sort(child),
                             ])
            index += 1

    def column_birth_day(self,data):
        event_handle = data.get_birth_handle()
        if event_handle:
            return self.db.get_event_from_handle(event_handle).get_date()
        else:
            return u""

    def column_birth_sort(self,data):
        event_handle = data.get_birth_handle()
        if event_handle:
            return self.db.get_event_from_handle(event_handle).get_date_object().get_sort_value()
        else:
            return 0

    def column_death_day(self,data):
        event_handle = data.get_death_handle()
        if event_handle:
            return self.db.get_event_from_handle(event_handle).get_date()
        else:
            return u""

    def column_death_sort(self,data):
        event_handle = data.get_death_handle()
        if event_handle:
            return self.db.get_event_from_handle(event_handle).get_date_object().get_sort_value()
        else:
            return 0
        
    def column_birth_place(self,data):
        event_handle = data.get_birth_handle()
        if event_handle:
            event = self.db.get_event_from_handle(event_handle)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

    def column_death_place(self,data):
        event_handle = data.get_death_handle()
        if event_handle:
            event = self.db.get_event_from_handle(event_handle)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

        
#-------------------------------------------------------------------------
#
# SourceModel
#
#-------------------------------------------------------------------------
class SourceModel(BaseModel):

    def __init__(self,db):
        self.sort_keys = db.get_source_handles
        self.map = db.source_map
        self.fmap = [
            self.column_title,
            self.column_id,
            self.column_author,
            self.column_abbrev,
            self.column_pubinfo,
            self.column_change,
            self.column_handle,
            ]
        BaseModel.__init__(self,db)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_title(self,data):
        return unicode(data[2])

    def column_handle(self,data):
        return unicode(data[0])

    def column_author(self,data):
        return unicode(data[3])

    def column_abbrev(self,data):
        return unicode(data[4])

    def column_id(self,data):
        return unicode(data[1])

    def column_pubinfo(self,data):
        return unicode(data[5])

    def column_change(self,data):
        return unicode(time.asctime(time.localtime(data[8])))

#-------------------------------------------------------------------------
#
# PlaceModel
#
#-------------------------------------------------------------------------
class PlaceModel(BaseModel):

    def __init__(self,db):
        self.sort_keys = db.get_place_handles
        self.map = db.place_map
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_parish,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.column_longitude,
            self.column_latitude,
            self.column_change,
            self.column_handle,
            ]
        BaseModel.__init__(self,db)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self,data):
        return unicode(data[0])

    def column_name(self,data):
        return unicode(data[2])

    def column_longitude(self,data):
        return unicode(data[3])

    def column_latitude(self,data):
        return unicode(data[4])

    def column_id(self,data):
        return unicode(data[1])

    def column_parish(self,data):
        try:
            return data[5].get_parish()
        except:
            return u''

    def column_city(self,data):
        try:
            return data[5].get_city()
        except:
            return u''
        
    def column_county(self,data):
        try:
            return data[5].get_county()
        except:
            return u''
    
    def column_state(self,data):
        try:
            return data[5].get_state()
        except:
            return u''

    def column_country(self,data):
        try:
            return data[5].get_country()
        except:
            return u''

    def column_change(self,data):
        return unicode(time.asctime(time.localtime(data[11])))

#-------------------------------------------------------------------------
#
# MediaModel
#
#-------------------------------------------------------------------------
class MediaModel(BaseModel):

    def __init__(self,db):
        self.sort_keys = db.get_media_object_handles
        self.map = db.media_map
        
        self.fmap = [
            self.column_description,
            self.column_id,
            self.column_mime,
            self.column_path,
            self.column_change,
            self.column_handle,
            ]
        BaseModel.__init__(self,db)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_description(self,data):
        return unicode(data[4])

    def column_path(self,data):
        return unicode(data[2])

    def column_mime(self,data):
        return unicode(data[3])

    def column_id(self,data):
        return unicode(data[1])

    def column_handle(self,data):
        return unicode(data[0])

    def column_change(self,data):
        return unicode(time.asctime(time.localtime(data[8])))

