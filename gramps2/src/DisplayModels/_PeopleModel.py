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

"""
TreeModel for the GRAMPS Person tree.
"""

__author__ = "Donald N. Allingham"
__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import time
import cgi
import sys
import locale

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
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
from RelLib import *
import NameDisplay
import DateHandler
import ToolTips
import GrampsLocale
import Config
from Filters import SearchFilter

#-------------------------------------------------------------------------
#
# python 2.3 has a bug in the unicode sorting using locale.strcoll. Seems
# to have a buffer overrun. We can convince it to do the right thing by
# forcing the string to be nul terminated, sorting, then stripping off the
# nul.
#
#-------------------------------------------------------------------------

if sys.version_info[0:2] == (2, 3):
    def locale_sort(mylist):
        """
        Sort version to get around a python2.3 bug with unicode strings
        """
        mylist = [ value + "\x00" for value in mylist ]
        mylist.sort(locale.strcoll)
        return [ value[:-1] for value in mylist ]
else:
    def locale_sort(mylist):
        """
        Normal sort routine
        """
        mylist.sort(locale.strcoll)
        return mylist

#-------------------------------------------------------------------------
#
# PeopleModel
#
#-------------------------------------------------------------------------
class PeopleModel(gtk.GenericTreeModel):
    """
    Basic GenericTreeModel interface to handle the Tree interface for
    the PersonView
    """

    # Model types
    GENERIC = 0
    SEARCH = 1
    FAST = 2

    # Column numbers
    _ID_COL     = 1
    _GENDER_COL = 2
    _NAME_COL   = 3
    _DEATH_COL  = 5
    _BIRTH_COL  = 6
    _EVENT_COL  = 7
    _FAMILY_COL = 8
    _CHANGE_COL = 17
    _MARKER_COL = 18


    _GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]

    # dynamic calculation of column indices, for use by various Views
    COLUMN_INT_ID = 13

    # indices into main column definition table
    COLUMN_DEF_LIST = 0
    COLUMN_DEF_HEADER = 1
    COLUMN_DEF_TYPE = 2

    def __init__(self, db, filter_info=None, skip=[]):
        """
        Initialize the model building the initial data
        """
        gtk.GenericTreeModel.__init__(self)

        self.db = db

        Config.client.notify_add("/apps/gramps/preferences/todo-color",
                                 self.update_todo)
        Config.client.notify_add("/apps/gramps/preferences/custom-marker-color",
                                 self.update_custom)
        Config.client.notify_add("/apps/gramps/preferences/complete-color",
                                 self.update_complete)

        self.complete_color = Config.get(Config.COMPLETE_COLOR)
        self.todo_color = Config.get(Config.TODO_COLOR)
        self.custom_color = Config.get(Config.CUSTOM_MARKER_COLOR)

        self.sortnames = {}
        self.marker_color_column = 11
        self.tooltip_column = 12
        self.prev_handle = None
        self.prev_data = None
        self.temp_top_path2iter = []
        self.iter2path = {}
        self.path2iter = {}
        self.sname_sub = {}
        if filter_info:
            if filter_info[0] == PeopleModel.GENERIC:
                data_filter = filter_info[1]
                self._build_data = self._build_filter_sub
            elif filter_info[0] == PeopleModel.SEARCH:
                col = filter_info[1][0]
                text = filter_info[1][1]
                inv = filter_info[1][2]
                func = lambda x: self.on_get_value(x, col) or u""
                data_filter = SearchFilter(func, text, inv)
                self._build_data = self._build_search_sub
            else:
                data_filter = filter_info[1]
                self._build_data = self._build_search_sub
        else:
            self._build_data = self._build_search_sub
            data_filter = None
        self.rebuild_data(data_filter, skip)

    def update_todo(self,client,cnxn_id,entry,data):
        self.todo_color = Config.get(Config.TODO_COLOR)
        
    def update_custom(self,client,cnxn_id,entry,data):
        self.custom_color = Config.get(Config.CUSTOM_MARKER_COLOR)

    def update_complete(self,client,cnxn_id,entry,data):
        self.complete_color = Config.get(Config.COMPLETE_COLOR)

    def rebuild_data(self, data_filter=None, skip=[]):
        """
        Convience function that calculates the new data and assigns it.
        """
        self.calculate_data(data_filter, skip)
        self.assign_data()
        
    def _build_search_sub(self,dfilter, skip):
        self.sortnames = {}

        ngn = NameDisplay.displayer.name_grouping_data
        nsn = NameDisplay.displayer.raw_sorted_name

        cursor = self.db.get_person_cursor()
        node = cursor.first()

        while node:
            handle, d = node
            if not (handle in skip or (dfilter and not dfilter.match(handle))):
                name_data = d[PeopleModel._NAME_COL]
                sn = ngn(self.db, name_data)
                self.sortnames[handle] = nsn(name_data)
                try:
                    self.temp_sname_sub[sn].append(handle)
                except:
                    self.temp_sname_sub[sn] = [handle]
            node = cursor.next()
        cursor.close()

    def _build_filter_sub(self,dfilter, skip):
        self.sortnames = {}

        ngn = NameDisplay.displayer.name_grouping_data
        nsn = NameDisplay.displayer.raw_sorted_name

        if dfilter:
            handle_list = dfilter.apply(self.db, self.db.get_person_handles())
        else:
            handle_list = self.db.get_person_handles()

        for handle in handle_list:
            d = self.db.get_raw_person_data(handle)
            if not (handle in skip or (dfilter and not dfilter.match(handle))):
                name_data = d[PeopleModel._NAME_COL]
                sn = ngn(self.db, name_data)
                self.sortnames[handle] = nsn(name_data)
                try:
                    self.temp_sname_sub[sn].append(handle)
                except:
                    self.temp_sname_sub[sn] = [handle]
        
    def calculate_data(self, dfilter=None, skip=[]):
        """
        Calculates the new path to node values for the model.
        """

        if dfilter:
            self.dfilter = dfilter
        self.temp_iter2path = {}
        self.temp_path2iter = {}
        self.temp_sname_sub = {}

        if not self.db.is_open():
            return

        self._build_data(dfilter, skip)

        self.temp_top_path2iter = locale_sort(self.temp_sname_sub.keys())
        for name in self.temp_top_path2iter:
            self.build_sub_entry(name)

    def clear_cache(self):
        self.prev_handle = None
        
    def build_sub_entry(self, name):
        self.prev_handle = None
        slist = [ (locale.strxfrm(self.sortnames[x]), x) \
                  for x in self.temp_sname_sub[name] ]
        slist.sort()

        val = 0
        for (junk, person_handle) in slist:
            tpl = (name, val)
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
        return len(PeopleModel.COLUMN_DEFS)

    def on_get_path(self,  node):
        '''returns the tree path (a tuple of indices at the various
        levels) for a particular node.'''
        try:
            return (self.top_path2iter.index(node), )
        except:
            (surname, index) = self.iter2path[node]
            return (self.top_path2iter.index(surname), index)

    def is_visable(self, handle):
        return self.iter2path.has_key(handle)

    def on_get_column_type(self, index):
        return PeopleModel.COLUMN_DEFS[index][PeopleModel.COLUMN_DEF_TYPE]

    def on_get_iter(self, path):
        try:
            if len(path)==1: # Top Level
                return self.top_path2iter[path[0]]
            else: # Sublevel
                surname = self.top_path2iter[path[0]]
                return self.path2iter[(surname, path[1])]
        except:
            return None

    def on_get_value(self, node, col):
        # test for header or data row-type
        if self.sname_sub.has_key(node):
            # Header rows dont get the foreground color set
            if col == self.marker_color_column:
                return None
            # test for 'header' column being empty (most are)
            if not PeopleModel.COLUMN_DEFS[col][PeopleModel.COLUMN_DEF_HEADER]:
                return u''
            # return values for 'header' row, calling a function
            # according to column_defs table
            val = PeopleModel.COLUMN_DEFS[col][PeopleModel.COLUMN_DEF_HEADER](self, node)
            return val
        else:
            # return values for 'data' row, calling a function
            # according to column_defs table
            try:
                if node != self.prev_handle:
                    self.prev_data = self.db.get_raw_person_data(str(node))
                    self.prev_handle = node
                return PeopleModel.COLUMN_DEFS[col][PeopleModel.COLUMN_DEF_LIST](self,
                                                         self.prev_data, node)
            except:
                return None

    def on_iter_next(self,  node):
        '''returns the next node at this level of the tree'''
        try:
            path = self.top_path2iter.index(node)
            if path+1 == len(self.top_path2iter):
                return None
            return self.top_path2iter[path+1]
        except:
            (surname, val) = self.iter2path[node]
            return self.path2iter.get((surname, val+1))

    def on_iter_children(self, node):
        """Return the first child of the node"""
        if node == None:
            return self.top_path2iter[0]
        else:
            return self.path2iter.get((node, 0))

    def on_iter_has_child(self, node):
        '''returns true if this node has children'''
        if node == None:
            return len(self.sname_sub)
        if self.sname_sub.has_key(node) and len(self.sname_sub[node]) > 0:
            return True
        return False

    def on_iter_n_children(self, node):
        if node == None:
            return len(self.sname_sub)
        try:
            return len(self.sname_sub[node])
        except:
            return 0

    def on_iter_nth_child(self, node, n):
        try:
            if node == None:
                return self.top_path2iter[n]
            try:
                return self.path2iter[(node, n)]
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

    def column_sort_name(self, data, node):
        n = Name()
        n.unserialize(data[PeopleModel._NAME_COL])
        return NameDisplay.displayer.sort_string(n)

    def column_spouse(self, data, node):
        spouses_names = u""
        handle = data[0]
        for family_handle in data[PeopleModel._FAMILY_COL]:
            family = self.db.get_family_from_handle(family_handle)
            for spouse_id in [family.get_father_handle(),
                              family.get_mother_handle()]:
                if not spouse_id:
                    continue
                if spouse_id == handle:
                    continue
                spouse = self.db.get_person_from_handle(spouse_id)
                if len(spouses_names) > 0:
                    spouses_names += ", "
                spouses_names += NameDisplay.displayer.display(spouse)
        return spouses_names

    def column_name(self, data, node):
        n = Name()
        n.unserialize(data[PeopleModel._NAME_COL])
        return NameDisplay.displayer.sorted_name(n)

    def column_id(self, data, node):
        return data[PeopleModel._ID_COL]

    def column_change(self, data, node):
        return unicode(
            time.strftime('%x %X',
                          time.localtime(data[PeopleModel._CHANGE_COL])),
            GrampsLocale.codeset)

    def column_gender(self, data, node):
        return PeopleModel._GENDER[data[PeopleModel._GENDER_COL]]

    def column_birth_day(self, data, node):
        index = data[PeopleModel._BIRTH_COL]
        if index != -1:
            try:
                local = data[PeopleModel._EVENT_COL][index]
                b = EventRef()
                b.unserialize(local)
                birth = self.db.get_event_from_handle(b.ref)
                date_str = DateHandler.get_date(birth)
                if date_str != "":
                    return cgi.escape(date_str)
            except:
                return u''
        
        for event_ref in data[PeopleModel._EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()[0]
            date_str = DateHandler.get_date(event)
            if (etype in [EventType.BAPTISM, EventType.CHRISTEN]
                and date_str != ""):
                return "<i>" + cgi.escape(date_str) + "</i>"
        
        return u""

    def column_death_day(self, data, node):
        index = data[PeopleModel._DEATH_COL]
        if index != -1:
            try:
                local = data[PeopleModel._EVENT_COL][index]
                ref = EventRef()
                ref.unserialize(local)
                event = self.db.get_event_from_handle(ref.ref)
                date_str = DateHandler.get_date(event)
                if date_str != "":
                    return cgi.escape(date_str)
            except:
                return u''
        
        for event_ref in data[PeopleModel._EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()[0]
            date_str = DateHandler.get_date(event)
            if (etype in [EventType.BURIAL, EventType.CREMATION]
                and date_str != ""):
                return "<i>" + cgi.escape(date_str) + "</i>"
        
        return u""

    def column_cause_of_death(self, data, node):
        index = data[PeopleModel._DEATH_COL]
        if index != -1:
            try:
                local = data[PeopleModel._EVENT_COL][index]
                dr = EventRef()
                dr.unserialize(local)
                return self.db.get_event_from_handle(dr.ref).get_cause()
            except:
                return u''
        else:
            return u""
        
    def column_birth_place(self, data, node):
        index = data[PeopleModel._BIRTH_COL]
        if index != -1:
            try:
                local = data[PeopleModel._EVENT_COL][index]
                br = EventRef()
                br.unserialize(local)
                event = self.db.get_event_from_handle(br.ref)
                if event:
                    place_handle = event.get_place_handle()
                    if place_handle:
                        place = self.db.get_place_from_handle(place_handle)
                        place_title = place.get_title()
                        if place_title != "":
                            return cgi.escape(place_title)
            except:
                return u''
        
        for event_ref in data[PeopleModel._EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()[0]
            if etype in [EventType.BAPTISM, EventType.CHRISTEN]:
                place_handle = event.get_place_handle()
                if place_handle:
                    place = self.db.get_place_from_handle(place_handle)
                    place_title = place.get_title()
                    if place_title != "":
                        return "<i>" + cgi.escape(place_title) + "</i>"
        
        return u""

    def column_death_place(self, data, node):
        index = data[PeopleModel._DEATH_COL]
        if index != -1:
            try:
                local = data[PeopleModel._EVENT_COL][index]
                dr = EventRef()
                dr.unserialize(local)
                event = self.db.get_event_from_handle(dr.ref)
                if event:
                    place_handle = event.get_place_handle()
                    if place_handle:
                        place = self.db.get_place_from_handle(place_handle)
                        place_title = place.get_title()
                        if place_title != "":
                            return cgi.escape(place_title)
            except:
                return u''
        
        for event_ref in data[PeopleModel._EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()[0]
            if etype in [EventType.BURIAL, EventType.CREMATION]:
                place_handle = event.get_place_handle()
                if place_handle:
                    place = self.db.get_place_from_handle(place_handle)
                    place_title = place.get_title()
                    if place_title != "":
                        return "<i>" + cgi.escape(place_title) + "</i>"
        
        return u""

    def column_marker_text(self, data, node):
        try:
            if data[PeopleModel._MARKER_COL]:
                return str(data[PeopleModel._MARKER_COL])
        except IndexError:
            return ""
        return ""

    def column_marker_color(self, data, node):
        try:
            if data[PeopleModel._MARKER_COL]:
                if data[PeopleModel._MARKER_COL][0] == MarkerType.COMPLETE:
                    return self.complete_color
                if data[PeopleModel._MARKER_COL][0] == MarkerType.TODO:
                    return self.todo_color
                if data[PeopleModel._MARKER_COL][0] == MarkerType.CUSTOM:
                    return self.custom_color
        except IndexError:
            pass
        return None

    def column_tooltip(self, data, node):
        if const.use_tips:
            return ToolTips.TipFromFunction(
                self.db,
                lambda: self.db.get_person_from_handle(data[0])
                )
        else:
            return u''
        

    def column_int_id(self, data, node):
        return node

    def column_header(self, node):
        return node

    def column_header_view(self, node):
        return True

    # table of column definitions
    # (unless this is declared after the PeopleModel class, an error is thrown)

    COLUMN_DEFS = [
        (column_name,           column_header, str),
        (column_id,             None,                      str),
        (column_gender,         None,                      str),
        (column_birth_day,      None,                      str),
        (column_birth_place,    None,                      str),
        (column_death_day,      None,                      str),
        (column_death_place,    None,                      str),
        (column_spouse,         None,                      str),
        (column_change,         None,                      str),
        (column_cause_of_death, None,                      str),
        (column_marker_text,    None,                      str),
        (column_marker_color,   None,                      str),
        # the order of the above columns must match PeopleView.column_names

        # these columns are hidden, and must always be last in the list
        (column_tooltip,        None,                      object),  
        (column_int_id,         None,                      str),
        ]
