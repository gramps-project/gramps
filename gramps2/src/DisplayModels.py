#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
# python modules
#
#-------------------------------------------------------------------------
import time
from gettext import gettext as _
import locale

import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import NameDisplay
import DateHandler
import RelLib
import Utils
import ToolTips
import GrampsLocale
import const

#-------------------------------------------------------------------------
#
# Localized constants
#
#-------------------------------------------------------------------------
_codeset = GrampsLocale.codeset

def sfunc(a,b):
    return locale.strcoll(a[0],b[0])

#-------------------------------------------------------------------------
#
# BaseModel
#
#-------------------------------------------------------------------------
class BaseModel(gtk.GenericTreeModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING,tooltip_column=None):
        gtk.GenericTreeModel.__init__(self)
        self.prev_handle = None
        self.prev_data = None
        self.set_property("leak_references",False)
        self.db = db
        self.sort_func = self.smap[scol]
        self.sort_col = scol
        self.reverse = (order == gtk.SORT_DESCENDING)
        self.tooltip_column = tooltip_column
        self.rebuild_data()

    def set_sort_column(self,col):
        self.sort_func = self.smap[col]

    def sort_keys(self):
        cursor = self.gen_cursor()
        sarray = []
        data = cursor.next()
        
        while data:
            sarray.append((locale.strxfrm(self.sort_func(data[1])),data[0]))
            data = cursor.next()
        cursor.close()

        sarray.sort()

        if self.reverse:
            sarray.reverse()

        return [ x[1] for x in sarray ]

    def rebuild_data(self):
        if self.db.is_open():
            self.datalist = self.sort_keys()
            i = 0
            self.indexlist = {}
            for key in self.datalist:
                self.indexlist[key] = i
                i += 1
        else:
            self.datalist = []
            self.indexlist = {}
        
    def add_row_by_handle(self,handle):
        self.datalist = self.sort_keys()
        i = 0
        self.indexlist = {}
        for key in self.datalist:
            self.indexlist[key] = i
            i += 1
        index = self.indexlist[handle]
        node = self.get_iter(index)
        self.row_inserted(index,node)

    def delete_row_by_handle(self,handle):
        index = self.indexlist[handle]
        self.indexlist = {}
        self.datalist = []
        i = 0
        for key in self.sort_keys():
            if key != handle:
                self.indexlist[key] = i
                self.datalist.append(key)
                i += 1
        self.row_deleted(index)

    def update_row_by_handle(self,handle):
        index = self.indexlist[handle]
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
        return self.indexlist[node]

    def on_get_column_type(self,index):
        if index == self.tooltip_column:
            return object
        return str

    def on_get_iter(self, path):
        try:
            return self.datalist[path[0]]
        except IndexError:
            return None

    def on_get_value(self,node,col):
        try:
            if node != self.prev_handle:
                self.prev_data = self.map(str(node))
                self.prev_handle = node
            return self.fmap[col](self.prev_data)
        except:
            return u''

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
        try:
            return self.datalist[self.indexlist[node]+1]
        except IndexError:
            return None

    def on_iter_children(self,node):
        """Return the first child of the node"""
        if node == None and self.datalist:
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
# SourceModel
#
#-------------------------------------------------------------------------
class SourceModel(BaseModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING):
        self.map = db.get_raw_source_data
        self.gen_cursor = db.get_source_cursor
        self.fmap = [
            self.column_title,
            self.column_id,
            self.column_author,
            self.column_abbrev,
            self.column_pubinfo,
            self.column_change,
            self.column_handle,
            self.column_tooltip
            ]
        self.smap = [
            self.column_title,
            self.column_id,
            self.column_author,
            self.column_abbrev,
            self.column_pubinfo,
            self.sort_change,
            ]
        BaseModel.__init__(self,db,scol,order,tooltip_column=7)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_title(self,data):
        return unicode(data[2])

    def column_handle(self,data):
        return unicode(data[0])

    def column_author(self,data):
        return unicode(data[3])

    def column_abbrev(self,data):
        return unicode(data[7])

    def column_id(self,data):
        return unicode(data[1])

    def column_pubinfo(self,data):
        return unicode(data[4])

    def column_change(self,data):
        return unicode(time.strftime('%x %X',time.localtime(data[8])),
                       GrampsLocale.codeset)
    
    def sort_change(self,data):
        return time.localtime(data[8])

    def column_tooltip(self,data):
        if const.use_tips:
            try:
                t = ToolTips.TipFromFunction(self.db, lambda:
                                             self.db.get_source_from_handle(data[0]))
            except:
                log.error("Failed to create tooltip.",exc_info=True)
                return t
        else:
            return u''
        
#-------------------------------------------------------------------------
#
# PlaceModel
#
#-------------------------------------------------------------------------
class PlaceModel(BaseModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING):
        self.gen_cursor = db.get_place_cursor
        self.map = db.get_raw_place_data
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_parish,
            self.column_postal_code,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.column_longitude,
            self.column_latitude,
            self.column_change,
            self.column_handle,
            self.column_tooltip
            ]
        self.smap = [
            self.column_name,
            self.column_id,
            self.column_parish,
            self.column_postal_code,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.column_longitude,
            self.column_latitude,
            self.column_change,
            self.column_handle,
            ]
        BaseModel.__init__(self,db,scol,order,tooltip_column=12)

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
            return data[5][1]
        except:
            return u''

    def column_city(self,data):
        try:
            return data[5][0][0]
        except:
            return u''
        
    def column_county(self,data):
        try:
            return data[5][2]
        except:
            return u''
    
    def column_state(self,data):
        try:
            return data[5][0][1]
        except:
            return u''

    def column_country(self,data):
        try:
            return data[5][0][2]
        except:
            return u''

    def column_postal_code(self,data):
        try:
            return data[5][0][3]
        except:
            return u''

    def sort_change(self,data):
        return time.localtime(data[11])
    
    def column_change(self,data):
        return unicode(time.strftime('%x %X',time.localtime(data[11])),
                            _codeset)

    def column_tooltip(self,data):
        if const.use_tips:
            try:
                t = ToolTips.TipFromFunction(self.db, lambda:
                                             self.db.get_place_from_handle(data[0]))
            except:
                log.error("Failed to create tooltip.", exc_info=True)
            return t
        else:
            return u''

#-------------------------------------------------------------------------
#
# FamilyModel
#
#-------------------------------------------------------------------------
class FamilyModel(BaseModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING):
        self.gen_cursor = db.get_family_cursor
        self.map = db.get_raw_family_data
        self.fmap = [
            self.column_id,
            self.column_father,
            self.column_mother,
            self.column_type,
            self.column_change,
            self.column_handle,
            self.column_tooltip
            ]
        self.smap = [
            self.column_id,
            self.sort_father,
            self.sort_mother,
            self.column_type,
            self.sort_change,
            self.column_handle,
            self.column_tooltip
            ]
        BaseModel.__init__(self,db,scol,order,tooltip_column=6)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self,data):
        return unicode(data[0])

    def column_father(self,data):
        if data[2]:
            person = self.db.get_person_from_handle(data[2])
            return unicode(NameDisplay.displayer.sorted_name(person.primary_name))
        else:
            return u""

    def sort_father(self,data):
        if data[2]:
            person = self.db.get_person_from_handle(data[2])
            return NameDisplay.displayer.sort_string(person.primary_name)
        else:
            return u""

    def column_mother(self,data):
        if data[3]:
            person = self.db.get_person_from_handle(data[3])
            return unicode(NameDisplay.displayer.sorted_name(person.primary_name))
        else:
            return u""

    def sort_mother(self,data):
        if data[3]:
            person = self.db.get_person_from_handle(data[3])
            return NameDisplay.displayer.sort_string(person.primary_name)
        else:
            return u""

    def column_type(self,data):
        return str(RelLib.FamilyRelType(data[5]))

    def column_id(self,data):
        return unicode(data[1])

    def sort_change(self,data):
        return time.localtime(data[13])
    
    def column_change(self,data):
        return unicode(time.strftime('%x %X',time.localtime(data[13])),
                            _codeset)

    def column_tooltip(self,data):
        if const.use_tips:
            try:
                t = ToolTips.TipFromFunction(self.db, lambda:
                                             self.db.get_family_from_handle(data[0]))
            except:
                log.error("Failed to create tooltip.", exc_info=True)
            return t
        else:
            return u''


#-------------------------------------------------------------------------
#
# MediaModel
#
#-------------------------------------------------------------------------
class MediaModel(BaseModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING):
        self.gen_cursor = db.get_media_cursor
        self.map = db.get_raw_object_data
        
        self.fmap = [
            self.column_description,
            self.column_id,
            self.column_mime,
            self.column_path,
            self.column_change,
            self.column_date,
            self.column_handle,
            self.column_tooltip
            ]
        self.smap = [
            self.column_description,
            self.column_id,
            self.column_mime,
            self.column_path,
            self.sort_change,
            self.column_date,
            self.column_handle,
            ]
        BaseModel.__init__(self,db,scol,order,tooltip_column=7)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_description(self,data):
        try:
            return unicode(data[4])
        except:
            return unicode(data[4],'latin1')

    def column_path(self,data):
        try:
            return unicode(data[2])
        except:
            return unicode(data[2].encode('iso-8859-1'))

    def column_mime(self,data):
        if data[3]:
            return unicode(data[3])
        else:
            return _('Note')

    def column_id(self,data):
        return unicode(data[1])

    def column_date(self,data):
        if data[9]:
            return unicode(DateHandler.displayer.display(data[9]))
        return u''

    def column_handle(self,data):
        return unicode(data[0])

    def sort_change(self,data):
        return time.localtime(data[8])

    def column_change(self,data):
        return unicode(time.strftime('%x %X',time.localtime(data[8])),
                            _codeset)

    def column_tooltip(self,data):
        if const.use_tips:
            try:
                t = ToolTips.TipFromFunction(self.db, lambda:
                                             self.db.get_object_from_handle(data[0]))
            except:
                log.error("Failed to create tooltip.", exc_info=True)
            return t
        else:
            return u''

#-------------------------------------------------------------------------
#
# EventModel
#
#-------------------------------------------------------------------------
class EventModel(BaseModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING):
        self.gen_cursor = db.get_event_cursor
        self.map = db.get_raw_event_data
        
        self.fmap = [
            self.column_description,
            self.column_id,
            self.column_type,
            self.column_date,
            self.column_place,
            self.column_cause,
            self.column_change,
            self.column_handle,
            self.column_tooltip,
            ]
        self.smap = [
            self.column_description,
            self.column_id,
            self.column_type,
            self.column_date,
            self.column_place,
            self.column_cause,
            self.sort_change,
            self.column_handle,
            ]
        BaseModel.__init__(self,db,scol,order,tooltip_column=8)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_description(self,data):
        return data[4]

    def column_cause(self,data):
        return data[6]

    def column_place(self,data):
        if data[5]:
            return self.db.get_place_from_handle(data[5]).get_title()
        else:
            return u''

    def column_type(self,data):
        return str(RelLib.EventType(data[2]))

    def column_id(self,data):
        return unicode(data[1])

    def column_date(self,data):
        if data[3]:
            event = RelLib.Event()
            event.unserialize(data)
            return DateHandler.get_date(event)
        return u''

    def column_handle(self,data):
        return unicode(data[0])

    def sort_change(self,data):
        return time.localtime(data[11])

    def column_change(self,data):
        return unicode(time.strftime('%x %X',time.localtime(data[11])),
                            _codeset)

    def column_tooltip(self,data):
        try:
            t = ToolTips.TipFromFunction(self.db, lambda: self.db.get_event_from_handle(data[0]))
        except:
            log.error("Failed to create tooltip.", exc_info=True)
        return t


#-------------------------------------------------------------------------
#
# RepositoryModel
#
#-------------------------------------------------------------------------
class RepositoryModel(BaseModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING):
        self.gen_cursor = db.get_repository_cursor
        self.get_handles = db.get_repository_handles
        self.map = db.get_raw_repository_data
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_type,
            self.column_home_url,
            self.column_street,
            self.column_postal_code,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.column_email,
            self.column_search_url,            
            self.column_handle,
            self.column_tooltip
            ]
        
        self.smap = [
            self.column_name,
            self.column_id,
            self.column_type,
            self.column_home_url,
            self.column_street,
            self.column_postal_code,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.column_email,
            self.column_search_url,            
            self.column_handle,            
            ]
        
        BaseModel.__init__(self,db,scol,order,tooltip_column=12)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self,data):
        return unicode(data[0])

    def column_id(self,data):
        return unicode(data[1])

    def column_type(self,data):
        return Utils.format_repository_type(data[2])

    def column_name(self,data):
        return unicode(data[3])

    def column_city(self,data):
        try:
            return data[4].get_city()
        except:
            return u''

    def column_street(self,data):
        try:
            if data[5]:
                return data[5][0].get_street()
            else:
                return u''
        except:
            return u''
        
    def column_county(self,data):
        try:
            if data[5]:
                return data[5][0].get_county()
            else:
                return u''
        except:
            return u''
    
    def column_state(self,data):
        try:
            if data[5]:
                return data[5][0].get_state()
            else:
                return u''
        except:
            return u''

    def column_country(self,data):
        try:
            if data[5]:
                return data[5][0].get_country()
            else:
                return u''
        except:
            return u''

    def column_postal_code(self,data):
        try:
            if data[5]:
                return data[5][0].get_postal_code()
            else:
                return u''
        except:
            return u''

    def column_phone(self,data):
        try:
            if data[5]:
                return data[5][0].get_phone()
            else:
                return u''
        except:
            return u''

    def column_email(self,data):
        return unicode(data[5])

    def column_search_url(self,data):
        return unicode(data[6])
    
    def column_home_url(self,data):
        if data[6]:
            urllist = data[6]
            return unicode(urllist[0].path)
        else:
            return u""

    def column_tooltip(self,data):
        return ""
#         try:
#             t = ToolTips.TipFromFunction(self.db, lambda: self.db.get_repository_from_handle(data[0]))
#         except:
#             log.error("Failed to create tooltip.", exc_info=True)
#         return t

