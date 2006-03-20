#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
from TransUtils import sgettext as _
import time
import cgi
import sys
import traceback
import locale

import cPickle as pickle

try:
    set()
except:
    from sets import Set as set

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".")

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
import DateHandler
import ToolTips
import GrampsLocale

#-------------------------------------------------------------------------
#
# Localized constants
#
#-------------------------------------------------------------------------
_codeset = GrampsLocale.codeset

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
_EVENT_COL = 8
_FAMILY_COL= 9
_CHANGE_COL= 19
_MARKER_COL= 20

#-------------------------------------------------------------------------
#
# python 2.3 has a bug in the unicode sorting using locale.strcoll. Seems
# to have a buffer overrun. We can convince it to do the right thing by
# forcing the string to be nul terminated, sorting, then stripping off the
# nul.
#
#-------------------------------------------------------------------------

if sys.version_info[0:2] == (2,3):
    def locale_sort(mylist):
        mylist = map(lambda x: x + "\x00", mylist)
        mylist.sort(locale.strcoll)
        return map(lambda x: x[:-1], mylist)
else:
    def locale_sort(mylist):
        mylist.sort(locale.strcoll)
        return mylist

#-------------------------------------------------------------------------
#
# PeopleModel
#
#-------------------------------------------------------------------------
class PeopleModel(gtk.GenericTreeModel):

    def __init__(self,db,data_filter=None,invert_result=False,skip=[]):
        gtk.GenericTreeModel.__init__(self)

        self.db = db

        self.invert_result = invert_result
        self.sortnames = {}
        self.marker_color_column = 11
        self.tooltip_column = 12
        self.prev_handle = None
        self.prev_data = None
        self.temp_top_path2iter = []
        self.rebuild_data(data_filter,skip)

    def rebuild_data(self,data_filter=None,skip=[]):
        self.calculate_data(data_filter,skip)
        self.assign_data()
        
    def calculate_data(self,dfilter=None,skip=[]):
        if dfilter:
            self.dfilter = dfilter
        self.temp_iter2path = {}
        self.temp_path2iter = {}
        self.temp_sname_sub = {}

        if not self.db.is_open():
            return

        ngn = NameDisplay.displayer.name_grouping_name
        nsn = NameDisplay.displayer.raw_sorted_name

        self.sortnames = {}

        cursor = self.db.person_map.db.cursor()
        node = cursor.first()
        
        while node:
            handle,d = node
            d = pickle.loads(d)
            if not (handle in skip or (dfilter and not dfilter.match(handle))):
                name_data = d[_NAME_COL]
                self.sortnames[handle] = nsn(name_data)
                try:
                    self.temp_sname_sub[name_data[3]].append(handle)
                except:
                    self.temp_sname_sub[name_data[3]] = [handle]
            node = cursor.next()
        cursor.close()

        self.temp_top_path2iter = locale_sort(self.temp_sname_sub.keys())
        for name in self.temp_top_path2iter:
            self.build_sub_entry(name)

    def clear_cache(self):
        self.prev_handle = None
        
    def build_sub_entry(self,name):
        self.prev_handle = None
        slist = [ (locale.strxfrm(self.sortnames[x]),x) \
                  for x in self.temp_sname_sub[name] ]
        slist.sort()

        val = 0
        for (junk,person_handle) in slist:
            tpl = (name,val)
            self.temp_iter2path[person_handle] = tpl
            self.temp_path2iter[tpl] = person_handle
            val += 1

    def assign_data(self):
        self.top_path2iter = self.temp_top_path2iter
        self.iter2path = self.temp_iter2path
        self.path2iter = self.temp_path2iter
        self.sname_sub = self.temp_sname_sub

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

    def is_visable(self,handle):
        return self.iter2path.has_key(handle)

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
            # Header rows dont get the background color set
            if col==self.marker_color_column:
                return None
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
                if node != self.prev_handle:
                    self.prev_data = self.db.get_raw_person_data(str(node))
                    self.prev_handle = node
                return COLUMN_DEFS[col][COLUMN_DEF_LIST](self,self.prev_data,node)
            except:
                if col == _MARKER_COL:
                    return None
                else:
                    return u'error'

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
        n = Name()
        n.unserialize(data[_NAME_COL])
        return n.get_sort_name()

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
        n = Name()
        n.unserialize(data[_NAME_COL])
        return NameDisplay.displayer.sorted_name(n)

    def column_id(self,data,node):
        return data[_ID_COL]

    def column_change(self,data,node):
        return unicode(time.strftime('%x %X',time.localtime(data[_CHANGE_COL])),
                            _codeset)

    def column_gender(self,data,node):
        return _GENDER[data[_GENDER_COL]]

    def column_birth_day(self,data,node):
        if data[_BIRTH_COL]:
            b=EventRef()
            b.unserialize(data[_BIRTH_COL])
            birth = self.db.get_event_from_handle(b.ref)
            date_str = DateHandler.get_date(birth)
            if date_str != "":
                return cgi.escape(date_str)
        
        for event_ref in data[_EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()[0]
            date_str = DateHandler.get_date(event)
            if (etype in [Event.BAPTISM, Event.CHRISTEN]
                and date_str != ""):
                return "<i>" + cgi.escape(date_str) + "</i>"
        
        return u""

    def column_death_day(self,data,node):
        if data[_DEATH_COL]:
            dr = EventRef()
            dr.unserialize(data[_DEATH_COL])
            death = self.db.get_event_from_handle(dr.ref)
            date_str = DateHandler.get_date(death)
            if date_str != "":
                return cgi.escape(date_str)
        
        for event_ref in data[_EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()[0]
            date_str = DateHandler.get_date(event)
            if (etype in [Event.BURIAL, Event.CREMATION]
                and date_str != ""):
                return "<i>" + cgi.escape(date_str) + "</i>"
        
        return u""

    def column_cause_of_death(self,data,node):
        if data[_DEATH_COL]:
            dr = EventRef()
            dr.unserialize(data[_DEATH_COL])
            return self.db.get_event_from_handle(dr.ref).get_cause()
        else:
            return u""
        
    def column_birth_place(self,data,node):
        if data[_BIRTH_COL]:
            br = EventRef()
            br.unserialize(data[_BIRTH_COL])
            event = self.db.get_event_from_handle(br.ref)
            if event:
                  place_handle = event.get_place_handle()
                  if place_handle:
                    place_title = self.db.get_place_from_handle(place_handle).get_title()
                    if place_title != "":
                        return cgi.escape(place_title)
        
        for event_ref in data[_EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()[0]
            if etype in [Event.BAPTISM, Event.CHRISTEN]:
                place_handle = event.get_place_handle()
                if place_handle:
                    place_title = self.db.get_place_from_handle(place_handle).get_title()
                    if place_title != "":
                        return "<i>" + cgi.escape(place_title) + "</i>"
        
        return u""

    def column_death_place(self,data,node):
        if data[_DEATH_COL]:
            dr = EventRef()
            dr.unserialize(data[_DEATH_COL])
            event = self.db.get_event_from_handle(dr.ref)
            if event:
                  place_handle = event.get_place_handle()
                  if place_handle:
                    place_title = self.db.get_place_from_handle(place_handle).get_title()
                    if place_title != "":
                        return cgi.escape(place_title)
        
        for event_ref in data[_EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()[0]
            if etype in [Event.BURIAL, Event.CREMATION]:
                place_handle = event.get_place_handle()
                if place_handle:
                    place_title = self.db.get_place_from_handle(place_handle).get_title()
                    if place_title != "":
                        return "<i>" + cgi.escape(place_title) + "</i>"
        
        return u""

    def column_marker_text(self,data,node):
        try:
            if data[_MARKER_COL]:
                if data[_MARKER_COL][0] == PrimaryObject.MARKER_CUSTOM:
                    return data[_MARKER_COL][1]
                elif data[_MARKER_COL][0] in Utils.marker_types.keys():
                    return Utils.marker_types[data[_MARKER_COL][0]]
        except IndexError:
            return ""
        return ""

    def column_marker_color(self,data,node):
        try:
            if data[_MARKER_COL]:
                if data[_MARKER_COL][0] == PrimaryObject.MARKER_COMPLETE:
                    return u"#46a046"   # green
                if data[_MARKER_COL][0] == PrimaryObject.MARKER_TODO:
                    return u"#df421e"   # red
                if data[_MARKER_COL][0] == PrimaryObject.MARKER_CUSTOM:
                    return u"#eed680"  # blue
        except IndexError:
            pass
        return None

    def column_tooltip(self,data,node):
        if const.use_tips:
            return ToolTips.TipFromFunction(self.db, lambda: self.db.get_person_from_handle(data[0]))
        else:
            return u''
        

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
    (PeopleModel.column_name,       PeopleModel.column_header, str),
    (PeopleModel.column_id,         None,                      str),
    (PeopleModel.column_gender,     None,                      str),
    (PeopleModel.column_birth_day,  None,                      str),
    (PeopleModel.column_birth_place,None,                      str),
    (PeopleModel.column_death_day,  None,                      str),
    (PeopleModel.column_death_place,None,                      str),
    (PeopleModel.column_spouse,     None,                      str),
    (PeopleModel.column_change,     None,                      str),
    (PeopleModel.column_cause_of_death, None,                  str),
    (PeopleModel.column_marker_text, None,                  str),
    (PeopleModel.column_marker_color, None,                  str),
    # the order of the above columns must match PeopleView.column_names

    # these columns are hidden, and must always be last in the list
    (PeopleModel.column_tooltip,    None,                      object),    
#    (PeopleModel.column_sort_name,  None,                      str),
    (PeopleModel.column_int_id,     None,                      str),
    ]

# dynamic calculation of column indices, for use by various Views
COLUMN_INT_ID = 13

# indices into main column definition table
COLUMN_DEF_LIST = 0
COLUMN_DEF_HEADER = 1
COLUMN_DEF_TYPE = 2
