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

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gobject
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
import DisplayTrace

_GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]

#-------------------------------------------------------------------------
#
# Localized constants
#
#-------------------------------------------------------------------------
_date_format = locale.nl_langinfo(locale.D_T_FMT)
_codeset = locale.nl_langinfo(locale.CODESET)

#-------------------------------------------------------------------------
#
# BaseModel
#
#-------------------------------------------------------------------------
class BaseModel(gtk.GenericTreeModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING,tooltip_column=None):
        gtk.GenericTreeModel.__init__(self)
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
            sarray.append((self.sort_func(data[1]),data[0]))
            data = cursor.next()
        cursor.close()
        sarray.sort()
        if self.reverse:
            sarray.reverse()
        return map(lambda x: x[1], sarray)

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
            self.indexlist = []
        
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
                             NameDisplay.displayer.display(child),
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
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return DateHandler.get_date(event)
        else:
            return u""

    def column_birth_sort(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return event.get_date_object().get_sort_value()
        else:
            return 0

    def column_death_day(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return DateHandler.get_date(event)
        else:
            return u""

    def column_death_sort(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return event.get_date_object().get_sort_value()
        else:
            return 0
        
    def column_birth_place(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

    def column_death_place(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
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

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING):
        self.map = db.source_map
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
        return unicode(time.strftime(_date_format,time.localtime(data[8])),
                            _codeset)
    def sort_change(self,data):
        return time.localtime(data[8])

    def column_tooltip(self,data):
        try:
            t = ToolTips.TipFromFunction(self.db, lambda: self.db.get_source_from_handle(data[0]))
        except:
            DisplayTrace.DisplayTrace()
        return t
        
#
#-------------------------------------------------------------------------
class PlaceModel(BaseModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING):
        self.gen_cursor = db.get_place_cursor
        self.map = db.place_map
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

    def column_postal_code(self,data):
        try:
            return data[5].get_postal_code()
        except:
            return u''

    def sort_change(self,data):
        return time.localtime(data[11])
    
    def column_change(self,data):
        return unicode(time.strftime(_date_format,time.localtime(data[11])),
                            _codeset)

    def column_tooltip(self,data):
        try:
            t = ToolTips.TipFromFunction(self.db, lambda: self.db.get_place_from_handle(data[0]))
        except:
            DisplayTrace.DisplayTrace()
        return t

#-------------------------------------------------------------------------
#
# MediaModel
#
#-------------------------------------------------------------------------
class MediaModel(BaseModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING):
        self.gen_cursor = db.get_media_cursor
        self.map = db.media_map
        
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
        return unicode(time.strftime(_date_format,time.localtime(data[8])),
                            _codeset)

    def column_tooltip(self,data):
        try:
            t = ToolTips.TipFromFunction(self.db, lambda: self.db.get_object_from_handle(data[0]))
        except:
            DisplayTrace.DisplayTrace()
        return t

#-------------------------------------------------------------------------
#
# EventModel
#
#-------------------------------------------------------------------------
class EventModel(BaseModel):

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING):
        self.gen_cursor = db.get_event_cursor
        self.map = db.event_map
        
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
        return unicode(data[4])

    def column_cause(self,data):
        return unicode(data[6])

    def column_place(self,data):
        if data[5]:
            return unicode(self.db.get_place_from_handle(data[5]).get_title())
        else:
            return u''

    def column_type(self,data):
        (code,val) = data[2]
        if code == RelLib.Event.CUSTOM:
            return unicode(val)
        else:
            val = Utils.personal_events.get(code)
            if not val:
                val = Utils.family_events.get(code,_("Unknown"))
            return val

    def column_id(self,data):
        return unicode(data[1])

    def column_date(self,data):
        if data[3]:
            return unicode(DateHandler.displayer.display(data[3]))
        return u''

    def column_handle(self,data):
        return unicode(data[0])

    def sort_change(self,data):
        return time.localtime(data[11])

    def column_change(self,data):
        return unicode(time.strftime(_date_format,time.localtime(data[11])),
                            _codeset)

    def column_tooltip(self,data):
        try:
            t = ToolTips.TipFromFunction(self.db, lambda: self.db.get_event_from_handle(data[0]))
        except:
            DisplayTrace.DisplayTrace()
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
        self.map = db.repository_map
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_type,
            self.column_home_url,
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
        rtype = data[2]
        if rtype[0] == RelLib.Event.CUSTOM or rtype[0] not in Utils.repository_types:
            name = rtype[1]
        else:
            name = Utils.repository_types[rtype[0]]
        return unicode(name)

    def column_name(self,data):
        return unicode(data[3])

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

    def column_postal_code(self,data):
        try:
            return data[4].get_postal_code()
        except:
            return u''

    def column_phone(self,data):
        try:
            return data[4].get_phone()
        except:
            return u''


    def column_email(self,data):
        return unicode(data[5])

    def column_search_url(self,data):
        return unicode(data[6])
    
    def column_home_url(self,data):
        return unicode(data[7])

    def column_tooltip(self,data):
        try:
            t = ToolTips.TipFromFunction(self.db, lambda: self.db.get_repository_from_handle(data[0]))
        except:
            DisplayTrace.DisplayTrace()
        return t
