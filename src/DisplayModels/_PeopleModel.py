#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from __future__ import with_statement
from gettext import gettext as _
import time
import cgi
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
from gen.lib import Name, EventRef, EventType, EventRoleType, MarkerType
from BasicUtils import name_displayer
import DateHandler
import ToolTips
import GrampsLocale
import Config
from gen.utils.longop import LongOpStatus
from Filters import SearchFilter, ExactSearchFilter
from Lru import LRU

_CACHE_SIZE = 250
invalid_date_format = Config.get(Config.INVALID_DATE_FORMAT)

class NodeTreeMap(object):

    def __init__(self):

        self.sortnames = {}
        self.temp_top_path2iter = []

        self.iter2path = {}
        self.path2iter = {}
        self.sname_sub = {}

        self.temp_iter2path = {}
        self.temp_path2iter = {}
        self.temp_sname_sub = {}

    def clear_sort_names(self):
        self.sortnames = {}

    def clear_temp_data(self):
        del self.temp_iter2path
        del self.temp_path2iter
        del self.temp_sname_sub
        self.temp_iter2path = {}
        self.temp_path2iter = {}
        self.temp_sname_sub = {}

    def build_toplevel(self):
        self.temp_top_path2iter = sorted(self.temp_sname_sub, key=locale.strxfrm)
        for name in self.temp_top_path2iter:
            self.build_sub_entry(name)

    def get_group_names(self):
        return self.temp_top_path2iter

    def assign_sort_name(self, handle, sorted_name, group_name):
        self.sortnames[handle] = sorted_name
        if group_name in self.temp_sname_sub:
            self.temp_sname_sub[group_name] += [handle]
        else:
            self.temp_sname_sub[group_name] = [handle]

    def assign_data(self):
        self.top_path2iter = self.temp_top_path2iter
        self.iter2path = self.temp_iter2path
        self.path2iter = self.temp_path2iter
        self.sname_sub = self.temp_sname_sub
        self.top_iter2path = {}
        for i, item in enumerate(self.top_path2iter):
            self.top_iter2path[item] = i

    def get_path(self, node):
        if node in self.top_iter2path:
            return (self.top_iter2path[node], )
        else:
            (surname, index) = self.iter2path[node]
            return (self.top_iter2path[surname], index)

    def has_entry(self, handle):
        return handle in self.iter2path

    def get_iter(self, path):
        try:
            if len(path)==1: # Top Level
                return self.top_path2iter[path[0]]
            else: # Sublevel
                surname = self.top_path2iter[path[0]]
                return self.path2iter[(surname, path[1])]
        except:
            return None
        
    def has_top_node(self, node):
        return node in self.sname_sub

    def find_next_node(self, node):
        if node in self.top_iter2path:
            path = self.top_iter2path[node]
            if path+1 < len(self.top_path2iter):
                return self.top_path2iter[path+1]
            else:
                return None
        else:
            (surname, val) = self.iter2path[node]
            return self.path2iter.get((surname, val+1))

    def first_child(self, node):
        if node is None:
            return self.top_path2iter[0]
        else:
            return self.path2iter.get((node, 0))

    def has_child(self, node):
        if node is None:
            return len(self.sname_sub)
        if node in self.sname_sub and self.sname_sub[node]:
            return True
        return False

    def number_of_children(self, node):
        if node is None:
            return len(self.sname_sub)
        if node in self.sname_sub:
            return len(self.sname_sub[node])
        return 0

    def get_nth_child(self, node, n):
        if node is None:
            if n < len(self.top_path2iter):
                return self.top_path2iter[n]
            else:
                return None
        else:
            return self.path2iter.get((node, n))

    def get_parent_of(self, node):
        path = self.iter2path.get(node)
        if path:
            return path[0]
        return None

    def build_sub_entry(self, name):
        slist = sorted(( (self.sortnames[x], x) \
                  for x in self.temp_sname_sub[name] ), 
                  key=lambda x: locale.strxfrm(x[0]))

        for val, (junk, person_handle) in enumerate(slist):
            tpl = (name, val)
            self.temp_iter2path[person_handle] = tpl
            self.temp_path2iter[tpl] = person_handle

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
    COLUMN_INT_ID = 12

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
        self.in_build = False
        self.lru_data  = LRU(_CACHE_SIZE)
        self.lru_name  = LRU(_CACHE_SIZE)
        self.lru_bdate = LRU(_CACHE_SIZE)
        self.lru_ddate = LRU(_CACHE_SIZE)

        Config.client.notify_add("/apps/gramps/preferences/todo-color",
                                 self.update_todo)
        Config.client.notify_add("/apps/gramps/preferences/custom-marker-color",
                                 self.update_custom)
        Config.client.notify_add("/apps/gramps/preferences/complete-color",
                                 self.update_complete)

        self.complete_color = Config.get(Config.COMPLETE_COLOR)
        self.todo_color = Config.get(Config.TODO_COLOR)
        self.custom_color = Config.get(Config.CUSTOM_MARKER_COLOR)

        self.marker_color_column = 10
        self.tooltip_column = 11

        self.mapper = NodeTreeMap()

        self.total = 0
        self.displayed = 0

        if filter_info and filter_info != (1, (0, u'', False)):
            if filter_info[0] == PeopleModel.GENERIC:
                data_filter = filter_info[1]
                self._build_data = self._build_filter_sub
            elif filter_info[0] == PeopleModel.SEARCH:
                col, text, inv = filter_info[1][:3]
                func = lambda x: self.on_get_value(x, col) or u""

                if col == self._GENDER_COL:
                    data_filter = ExactSearchFilter(func, text, inv)
                else:
                    data_filter = SearchFilter(func, text, inv)

                self._build_data = self._build_search_sub
            else:
                data_filter = filter_info[1]
                self._build_data = self._build_search_sub
        else:
            self._build_data = self._build_search_sub
            data_filter = None
        self.current_filter = data_filter
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
        self.current_filter = data_filter
        
    def _build_search_sub(self,dfilter, skip):
        ngn = name_displayer.name_grouping_data
        nsn = name_displayer.raw_sorted_name

        self.mapper.clear_sort_names()

        self.total = 0
        self.displayed = 0
        with self.db.get_person_cursor() as cursor:
            for handle, d in cursor:
                self.total += 1
                if not (handle in skip or (dfilter and not dfilter.match(handle,self.db))):
                    name_data = d[PeopleModel._NAME_COL]
                    group_name = ngn(self.db, name_data)
                    sorted_name = nsn(name_data)
                    self.displayed += 1
                    self.mapper.assign_sort_name(handle, sorted_name, group_name)

    def _build_filter_sub(self,dfilter, skip):
        ngn = name_displayer.name_grouping_data
        nsn = name_displayer.raw_sorted_name
        handle_list = self.db.iter_person_handles()
        self.total = self.db.get_number_of_people()
            
        if dfilter:
            handle_list = dfilter.apply(self.db, handle_list)
            self.displayed = len(handle_list)
        else:
            self.displayed = self.db.get_number_of_people()

        self.mapper.clear_sort_names()
        status = LongOpStatus(msg="Loading People",
                              total_steps=self.displayed,
                              interval=self.displayed//10)
        self.db.emit('long-op-start', (status,))
        for handle in handle_list:
            status.heartbeat()
            d = self.db.get_raw_person_data(handle)
            if not handle in skip:
                name_data = d[PeopleModel._NAME_COL]
                group_name = ngn(self.db, name_data)
                sorted_name = nsn(name_data)

                self.mapper.assign_sort_name(handle, sorted_name, group_name)
        status.end()
        
    def calculate_data(self, dfilter=None, skip=[]):
        """
        Calculate the new path to node values for the model.
        """
        self.clear_cache()
        self.in_build  = True

        self.total = 0
        self.displayed = 0

        if dfilter:
            self.dfilter = dfilter
            
        self.mapper.clear_temp_data()

        if not self.db.is_open():
            return

        self._build_data(dfilter, skip)
        self.mapper.build_toplevel()

        self.in_build  = False

    def clear_cache(self):
        self.lru_name.clear()
        self.lru_data.clear()
        self.lru_bdate.clear()
        self.lru_ddate.clear()

    def build_sub_entry(self, name):
        self.mapper.build_sub_entry(name)

    def assign_data(self):
        self.mapper.assign_data()

    def on_get_flags(self):
        """returns the GtkTreeModelFlags for this particular type of model"""
        return gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        return len(PeopleModel.COLUMN_DEFS)

    def on_get_path(self,  node):
        """returns the tree path (a tuple of indices at the various
        levels) for a particular node."""
        return self.mapper.get_path(node)

    def is_visable(self, handle):
        return self.mapper.has_entry(handle)

    def on_get_column_type(self, index):
        return PeopleModel.COLUMN_DEFS[index][PeopleModel.COLUMN_DEF_TYPE]

    def on_get_iter(self, path):
        return self.mapper.get_iter(path)

    def on_get_value(self, node, col):
        # test for header or data row-type
        if self.mapper.has_top_node(node):
            # Header rows dont get the foreground color set
            if col == self.marker_color_column:
                return None
            # test for 'header' column being empty (most are)
            if not PeopleModel.COLUMN_DEFS[col][PeopleModel.COLUMN_DEF_HEADER]:
                return u''
            # return values for 'header' row, calling a function
            # according to column_defs table
            return (PeopleModel.COLUMN_DEFS[col]
                    [PeopleModel.COLUMN_DEF_HEADER](self, node)
                    )
        else:
            # return values for 'data' row, calling a function
            # according to column_defs table
            try:
                if node in self.lru_data:
                    data = self.lru_data[node]
                else:
                    data = self.db.get_raw_person_data(str(node))
                    if not self.in_build:
                        self.lru_data[node] = data
                return (PeopleModel.COLUMN_DEFS[col]
                        [PeopleModel.COLUMN_DEF_LIST](self, data, node)
                        )
            except:
                return None

    def on_iter_next(self,  node):
        """returns the next node at this level of the tree"""
        return self.mapper.find_next_node(node)

    def on_iter_children(self, node):
        """Return the first child of the node"""
        return self.mapper.first_child(node)

    def on_iter_has_child(self, node):
        """returns true if this node has children"""
        return self.mapper.has_child(node)

    def on_iter_n_children(self, node):
        return self.mapper.number_of_children(node)

    def on_iter_nth_child(self, node, n):
        return self.mapper.get_nth_child(node, n)

    def on_iter_parent(self, node):
        """returns the parent of this node"""
        return self.mapper.get_parent_of(node)

    def column_sort_name(self, data, node):
        n = Name()
        n.unserialize(data[PeopleModel._NAME_COL])
        return name_displayer.sort_string(n)

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
                if spouses_names:
                    spouses_names += ", "
                spouses_names += name_displayer.display(spouse)
        return spouses_names

    def column_name(self, data, node):
        if node in self.lru_name:
            name = self.lru_name[node]
        else:
            name = name_displayer.raw_sorted_name(data[PeopleModel._NAME_COL])
            if not self.in_build:
                self.lru_name[node] = name
        return name

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
        if node in self.lru_bdate:
            value = self.lru_bdate[node]
        else:
            value = self._get_birth_data(data, node)
            if not self.in_build:
                self.lru_bdate[node] = value
        return value

    def _get_birth_data(self, data, node):
        index = data[PeopleModel._BIRTH_COL]
        if index != -1:
            try:
                local = data[PeopleModel._EVENT_COL][index]
                b = EventRef()
                b.unserialize(local)
                birth = self.db.get_event_from_handle(b.ref)
                date_str = DateHandler.get_date(birth)
                if date_str != "":
                    retval = cgi.escape(date_str)
                if not DateHandler.get_date_valid(birth):
                    return invalid_date_format % retval
                else:
                    return retval
            except:
                return u''
        
        for event_ref in data[PeopleModel._EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()
            date_str = DateHandler.get_date(event)
            if (etype in [EventType.BAPTISM, EventType.CHRISTEN]
                and er.get_role() == EventRoleType.PRIMARY
                and date_str != ""):
                retval = u"<i>%s</i>" % cgi.escape(date_str)
                if not DateHandler.get_date_valid(event):
                    return invalid_date_format % retval
                else:
                    return retval
        
        return u""

    def column_death_day(self, data, node):
        if node in self.lru_ddate:
            value = self.lru_ddate[node]
        else:
            value = self._get_death_data(data, node)
            if not self.in_build:
                self.lru_ddate[node] = value
        return value

    def _get_death_data(self, data, node):
        index = data[PeopleModel._DEATH_COL]
        if index != -1:
            try:
                local = data[PeopleModel._EVENT_COL][index]
                ref = EventRef()
                ref.unserialize(local)
                event = self.db.get_event_from_handle(ref.ref)
                date_str = DateHandler.get_date(event)
                if date_str != "":
                    retval = cgi.escape(date_str)
                if not DateHandler.get_date_valid(event):
                    return invalid_date_format % retval
                else:
                    return retval
            except:
                return u''
        
        for event_ref in data[PeopleModel._EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()
            date_str = DateHandler.get_date(event)
            if (etype in [EventType.BURIAL, EventType.CREMATION, EventType.CAUSE_DEATH]
                and er.get_role() == EventRoleType.PRIMARY
                and date_str):
                retval = "<i>%s</i>" % cgi.escape(date_str)
                if not DateHandler.get_date_valid(event):
                    return invalid_date_format % retval
                else:
                    return retval
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
                        if place_title:
                            return cgi.escape(place_title)
            except:
                return u''
        
        for event_ref in data[PeopleModel._EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()
            if (etype in [EventType.BAPTISM, EventType.CHRISTEN] and
                er.get_role() == EventRoleType.PRIMARY):

                place_handle = event.get_place_handle()
                if place_handle:
                    place = self.db.get_place_from_handle(place_handle)
                    place_title = place.get_title()
                    if place_title:
                        return "<i>%s</i>" % cgi.escape(place_title)
        
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
                        if place_title:
                            return cgi.escape(place_title)
            except:
                return u''
        
        for event_ref in data[PeopleModel._EVENT_COL]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()
            if (etype in [EventType.BURIAL, EventType.CREMATION, EventType.CAUSE_DEATH]
                and er.get_role() == EventRoleType.PRIMARY):

                place_handle = event.get_place_handle()
                if place_handle:
                    place = self.db.get_place_from_handle(place_handle)
                    place_title = place.get_title()
                    if place_title != "":
                        return "<i>" + cgi.escape(place_title) + "</i>"
        return u""

    def column_marker_text(self, data, node):
        if PeopleModel._MARKER_COL < len(data):
            return str(data[PeopleModel._MARKER_COL])
        return ""

    def column_marker_color(self, data, node):
        try:
            if data[PeopleModel._MARKER_COL]:
                if data[PeopleModel._MARKER_COL][0] == MarkerType.COMPLETE:
                    return self.complete_color
                if data[PeopleModel._MARKER_COL][0] == MarkerType.TODO_TYPE:
                    return self.todo_color
                if data[PeopleModel._MARKER_COL][0] == MarkerType.CUSTOM:
                    return self.custom_color
        except IndexError:
            pass
        return None

    def column_tooltip(self, data, node):
        if const.USE_TIPS:
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
        (column_marker_text,    None,                      str),
        (column_marker_color,   None,                      str),
        # the order of the above columns must match PeopleView.column_names

        # these columns are hidden, and must always be last in the list
        (column_tooltip,        None,                      object),  
        (column_int_id,         None,                      str),
        ]
