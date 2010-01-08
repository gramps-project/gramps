#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2009       Nick Hall
# Copyright (C) 2009       Benny Malengier
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
#from gettext import gettext as _
from TransUtils import gettext as _
import time
import cgi

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".")

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
from Lru import LRU
from gui.views.treemodels.treebasemodel import TreeBaseModel
import config

#-------------------------------------------------------------------------
#
# COLUMN constants
#
#-------------------------------------------------------------------------
COLUMN_ID     = 1
COLUMN_GENDER = 2
COLUMN_NAME   = 3
COLUMN_DEATH  = 5
COLUMN_BIRTH  = 6
COLUMN_EVENT  = 7
COLUMN_FAMILY = 8
COLUMN_CHANGE = 17
COLUMN_MARKER = 18

invalid_date_format = config.get('preferences.invalid-date-format')

#-------------------------------------------------------------------------
#
# PeopleModel
#
#-------------------------------------------------------------------------
class PeopleModel(TreeBaseModel):
    """
    Basic GenericTreeModel interface to handle the Tree interface for
    the PersonView
    """
    _GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]

    # The following is accessed from PersonView - CHECK
    COLUMN_INT_ID = 12  # dynamic calculation of column indices

    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):
        """
        Initialize the model building the initial data
        """
        self.lru_name  = LRU(TreeBaseModel._CACHE_SIZE)
        self.lru_bdate = LRU(TreeBaseModel._CACHE_SIZE)
        self.lru_ddate = LRU(TreeBaseModel._CACHE_SIZE)

        self.gen_cursor = db.get_person_cursor
        self.map = db.get_raw_person_data
        self.scol = scol

        #self.group_list = []

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
            self.column_marker_text,
            self.column_marker_color,
            self.column_tooltip,
            self.column_int_id,
            ]
        self.smap = [
            self.sort_name,
            self.column_id,
            self.column_gender,
            self.sort_birth_day,
            self.column_birth_place,
            self.sort_death_day,
            self.column_death_place,
            self.column_spouse,
            self.column_change,
            self.column_marker_text,
            self.column_marker_color,
            self.column_tooltip,
            self.column_int_id,
            ]
        self.hmap = [self.column_header] + [None]*len(self.smap)
        TreeBaseModel.__init__(self, db, search=search, skip=skip,
                                tooltip_column=11, marker_column=10,
                                scol=scol, order=order, sort_map=sort_map)
    def clear_cache(self):
        """ Clear the LRU cache """
        TreeBaseModel.clear_cache(self)
        self.lru_name.clear()
        self.lru_bdate.clear()
        self.lru_ddate.clear()
        
    def on_get_n_columns(self):
        """ Return the number of columns in the model """
        return len(self.fmap)+1

    def get_tree_levels(self):
        """
        Return the headings of the levels in the hierarchy.
        """
        return ['Group As', 'Name']

    def add_row(self, handle, data):
        """
        Add nodes to the node map for a single person.

        handle      The handle of the gramps object.
        data        The object data.
        """
        ngn = name_displayer.name_grouping_data
        nsn = name_displayer.raw_sorted_name
        
        name_data = data[COLUMN_NAME]
        group_name = ngn(self.db, name_data)
        sort_key = self.sort_func(data)

        #if group_name not in self.group_list:
            #self.group_list.append(group_name)
            #self.add_node(None, group_name, group_name, None)
            
        # add as node: parent, child, sortkey, handle; parent and child are 
        # nodes in the treebasemodel, and will be used as iters
        self.add_node(group_name, handle, sort_key, handle)
        
    def sort_name(self, data):
        n = Name()
        n.unserialize(data[COLUMN_NAME])
        return name_displayer.sort_string(n)

    def column_spouse(self, data):
        spouses_names = u""
        handle = data[0]
        for family_handle in data[COLUMN_FAMILY]:
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

    def column_name(self, data):
        handle = data[0]
        if handle in self.lru_name:
            name = self.lru_name[handle]
        else:
            name = name_displayer.raw_sorted_name(data[COLUMN_NAME])
            if not self._in_build:
                self.lru_name[handle] = name
        return name

    def column_id(self, data):
        return data[COLUMN_ID]
        
    def column_change(self, data):
        return unicode(
            time.strftime('%x %X',
                          time.localtime(data[COLUMN_CHANGE])),
            GrampsLocale.codeset)

    def column_gender(self, data):
        return PeopleModel._GENDER[data[COLUMN_GENDER]]

    def column_birth_day(self, data):
        handle = data[0]
        if handle in self.lru_bdate:
            value = self.lru_bdate[handle]
        else:
            value = self._get_birth_data(data, False)
            if not self._in_build:
                self.lru_bdate[handle] = value
        return value
        
    def sort_birth_day(self, data):
        handle = data[0]
        return self._get_birth_data(data, True)

    def _get_birth_data(self, data, sort_mode):
        index = data[COLUMN_BIRTH]
        if index != -1:
            try:
                local = data[COLUMN_EVENT][index]
                b = EventRef()
                b.unserialize(local)
                birth = self.db.get_event_from_handle(b.ref)
                if sort_mode:
                    retval = "%09d" % birth.get_date_object().get_sort_value()
                else:
                    date_str = DateHandler.get_date(birth)
                    if date_str != "":
                        retval = cgi.escape(date_str)
                if not DateHandler.get_date_valid(birth):
                    return invalid_date_format % retval
                else:
                    return retval
            except:
                return u''
        
        for event_ref in data[COLUMN_EVENT]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()
            date_str = DateHandler.get_date(event)
            if (etype in [EventType.BAPTISM, EventType.CHRISTEN]
                and er.get_role() == EventRoleType.PRIMARY
                and date_str != ""):
                if sort_mode:
                    retval = "%09d" % event.get_date_object().get_sort_value()
                else:
                    retval = u"<i>%s</i>" % cgi.escape(date_str)
                if not DateHandler.get_date_valid(event):
                    return invalid_date_format % retval
                else:
                    return retval
        
        return u""

    def column_death_day(self, data):
        handle = data[0]
        if handle in self.lru_ddate:
            value = self.lru_ddate[handle]
        else:
            value = self._get_death_data(data, False)
            if not self._in_build:
                self.lru_ddate[handle] = value
        return value
        
    def sort_death_day(self, data):
        handle = data[0]
        return self._get_death_data(data, True)

    def _get_death_data(self, data, sort_mode):
        index = data[COLUMN_DEATH]
        if index != -1:
            try:
                local = data[COLUMN_EVENT][index]
                ref = EventRef()
                ref.unserialize(local)
                event = self.db.get_event_from_handle(ref.ref)
                if sort_mode:
                    retval = "%09d" % event.get_date_object().get_sort_value()
                else:
                    date_str = DateHandler.get_date(event)
                    if date_str != "":
                        retval = cgi.escape(date_str)
                if not DateHandler.get_date_valid(event):
                    return invalid_date_format % retval
                else:
                    return retval
            except:
                return u''
        
        for event_ref in data[COLUMN_EVENT]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()
            date_str = DateHandler.get_date(event)
            if (etype in [EventType.BURIAL,
                          EventType.CREMATION,
                          EventType.CAUSE_DEATH]
                and er.get_role() == EventRoleType.PRIMARY
                and date_str):
                if sort_mode:
                    retval = "%09d" % event.get_date_object().get_sort_value()
                else:
                    retval = "<i>%s</i>" % cgi.escape(date_str)
                if not DateHandler.get_date_valid(event):
                    return invalid_date_format % retval
                else:
                    return retval
        return u""

    def column_birth_place(self, data):
        index = data[COLUMN_BIRTH]
        if index != -1:
            try:
                local = data[COLUMN_EVENT][index]
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
        
        for event_ref in data[COLUMN_EVENT]:
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

    def column_death_place(self, data):
        index = data[COLUMN_DEATH]
        if index != -1:
            try:
                local = data[COLUMN_EVENT][index]
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
        
        for event_ref in data[COLUMN_EVENT]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()
            if (etype in [EventType.BURIAL, EventType.CREMATION,
                          EventType.CAUSE_DEATH]
                and er.get_role() == EventRoleType.PRIMARY):

                place_handle = event.get_place_handle()
                if place_handle:
                    place = self.db.get_place_from_handle(place_handle)
                    place_title = place.get_title()
                    if place_title != "":
                        return "<i>" + cgi.escape(place_title) + "</i>"
        return u""

    def column_marker_text(self, data):
        if COLUMN_MARKER < len(data):
            return str(data[COLUMN_MARKER])
        return ""

    def column_marker_color(self, data):
        try:
            if data[COLUMN_MARKER]:
                if data[COLUMN_MARKER][0] == MarkerType.COMPLETE:
                    return self.complete_color
                if data[COLUMN_MARKER][0] == MarkerType.TODO_TYPE:
                    return self.todo_color
                if data[COLUMN_MARKER][0] == MarkerType.CUSTOM:
                    return self.custom_color
        except IndexError:
            pass
        return None

    def column_tooltip(self, data):
        if const.USE_TIPS:
            return ToolTips.TipFromFunction(
                self.db,
                lambda: self.db.get_person_from_handle(data[0])
                )
        else:
            return u''
        
    def column_int_id(self, data):
        return data[0]

    def column_header(self, node):
        return node

    def column_header_view(self, node):
        return True

