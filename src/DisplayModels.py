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

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gobject
import gtk

#-------------------------------------------------------------------------
#
# BaseModel
#
#-------------------------------------------------------------------------
class BaseModel(gtk.GenericTreeModel):

    def __init__(self,db):

        gtk.GenericTreeModel.__init__(self)
        self.set_property("leak_references",0)

        self.db = db
        self.rebuild_data()
        self.connect('row-inserted',self.on_row_inserted)
        self.connect('row-deleted',self.on_row_deleted)

    def rebuild_data(self):
        self.iter2path = {}
        self.path2iter = {}

        if not self.db.is_open():
            return
        
        val = 0
        for place_id in self.sort_keys():
            self.iter2path[place_id] = (val,)
            self.path2iter[(val,)] = place_id
            val += 1
        
    def on_row_inserted(self,obj,path,iter):
        self.rebuild_data()

    def on_row_deleted(self,obj,path):
        self.rebuild_data()

    def on_get_flags(self):
	'''returns the GtkTreeModelFlags for this particular type of model'''
	return gtk.TREE_MODEL_LIST_ONLY

    def on_get_n_columns(self):
        return 10

    def on_get_path(self, node):
	'''returns the tree path (a tuple of indices at the various
	levels) for a particular node.'''
        return self.iter2path[node]

    def on_get_column_type(self,index):
        return gobject.TYPE_STRING

    def on_get_iter(self, path):
        return self.path2iter.get(path)

    def on_get_value(self,iter,col):
        return self.fmap[col](self.map[str(iter)])

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
        path = self.iter2path.get(node)
        return self.path2iter.get((path[0]+1,))

    def on_iter_children(self,node):
        """Return the first child of the node"""
        if node == None:
            return self.path2iter[(0,)]
        return None

    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
        if node == None:
            return len(self.iter2path) > 0
        return 0

    def on_iter_n_children(self,node):
        if node == None:
            return len(self.iter2path)
        return 0

    def on_iter_nth_child(self,node,n):
        path = self.iter2path.get(node)
        if path:
            return self.path2iter.get((node,n))
        else:
            return None

    def on_iter_parent(self, node):
	'''returns the parent of this node'''
        return None

#-------------------------------------------------------------------------
#
# SourceModel
#
#-------------------------------------------------------------------------
class SourceModel(BaseModel):

    def __init__(self,db):
        self.sort_keys = db.sort_source_keys
        self.map = db.source_map
        self.fmap = [
            self.column_title,
            self.column_id,
            self.column_author,
            self.column_abbrev,
            self.column_pubinfo,
            ]
        BaseModel.__init__(self,db)

    def column_title(self,data):
        return unicode(data[1])

    def column_author(self,data):
        return unicode(data[2])

    def column_abbrev(self,data):
        return unicode(data[3])

    def column_id(self,data):
        return unicode(data[0])

    def column_pubinfo(self,data):
        return unicode(data[4])

#-------------------------------------------------------------------------
#
# PlaceModel
#
#-------------------------------------------------------------------------
class PlaceModel(BaseModel):

    def __init__(self,db):
        self.sort_keys = db.sort_place_keys
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
            ]
        BaseModel.__init__(self,db)

    def column_name(self,data):
        return unicode(data[1])

    def column_longitude(self,data):
        return unicode(data[2])

    def column_latitude(self,data):
        return unicode(data[3])

    def column_id(self,data):
        return unicode(data[0])

    def column_parish(self,data):
        try:
            return data[4].get_parish()
        except:
            return u''

    def column_city(self,data):
        try:
            return data[4].get_city()
        except:
            return u''
        
    def column_county(self,data):
        try:
            return data[4].get_county()
        except:
            return u''
    
    def column_state(self,data):
        try:
            return data[4].get_state()
        except:
            return u''

    def column_country(self,data):
        try:
            return data[4].get_country()
        except:
            return u''

#-------------------------------------------------------------------------
#
# MediaModel
#
#-------------------------------------------------------------------------
class MediaModel(BaseModel):

    def __init__(self,db):
        self.sort_keys = db.sort_media_keys
        self.map = db.media_map
        
        self.fmap = [
            self.column_description,
            self.column_id,
            self.column_mime,
            self.column_path,
            ]
        BaseModel.__init__(self,db)

    def column_description(self,data):
        return unicode(data[3])

    def column_path(self,data):
        return unicode(data[1])

    def column_mime(self,data):
        return unicode(data[2])

    def column_id(self,data):
        return unicode(data[0])
