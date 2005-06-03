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
# Standard python modules
#
#-------------------------------------------------------------------------
import cPickle as pickle
from sets import Set

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from ListModel import ListModel, NOSORT, COMBO, TEXT, TOGGLE
from DdTargets import DdTargets

import const
import RelLib
import UrlEdit
import NameEdit
import NoteEdit
import AttrEdit
import EventEdit
import AddrEdit
import NameDisplay
import Utils

class ListBox:
    def __init__(self, parent, person, obj, label, button_list, titles):
        self.person = person
        self.label = label
        self.name = NameDisplay.displayer.display(self.person)
        self.db = parent.db
        self.parent = parent
        self.list_model = ListModel(
            obj, titles, self.select_row, self.update)
        self.blist = button_list
        self.node_map = {}
        self.tree = obj
        self.changed = False
        self.blist[0].connect('clicked',self.add)
        self.blist[1].connect('clicked',self.update)
        self.blist[2].connect('clicked',self.delete)
        self.tree.connect('key_press_event', self.keypress)
        self.change_list = Set()

    def keypress(self,obj,event):
        if event.keyval == 65379:
            print "insert"

    def get_changed_objects(self):
        return list(self.change_list)

    def add_object(self,item):
        self.data.append(item)
        self.change_list.add(item)
        
    def select_row(self,obj):
        store, node = obj.get_selected()
        enable = node != None
        for button in self.blist[1:]:
            button.set_sensitive(enable)

    def delete(self,obj):
        """Delete the selected event"""
        if Utils.delete_selected(obj,self.data):
            self.changed = True
            self.redraw()

    def update(self,obj):
        raise NotImplementedError

    def redraw(self):
        self.list_model.clear()
        self.node_map = {}
        for item in self.data:
            node = self.list_model.add(self.display_data(item),item)
            self.node_map[item] = node
        if self.data:
            self.list_model.select_row(0)
        self.set_label()

    def display_data(self,item):
        raise NotImplementedError

    def delete(self,obj):
        """Deletes the selected name from the name list"""
        store,node = self.list_model.get_selected()
        if node:
            self.list_model.remove(self.list_model.get_object(node))
            self.changed = True
            self.redraw()

    def edit_callback(self,data):
        self.changed = True
        self.change_list.add(data)
        if data not in self.data:
            self.data.append(data)
        self.redraw()
        try:
            self.list_model.select_iter(self.node_map[data])
        except:
            print "Edit callback failed"

    def set_label(self):
        if self.data:
            self.list_model.select_row(0)
            Utils.bold_label(self.label)
            self.blist[1].set_sensitive(True)
            self.blist[2].set_sensitive(True)
        else:
            Utils.unbold_label(self.label)
            self.blist[1].set_sensitive(False)
            self.blist[2].set_sensitive(False)

class ReorderListBox(ListBox):

    def __init__(self,parent,person,obj,label,button_list,evalues, dnd_type):

        ListBox.__init__(self,parent,person,obj,label,button_list,evalues)

        self.dnd_type = dnd_type

        obj.drag_dest_set(gtk.DEST_DEFAULT_ALL, [dnd_type.target()],
                          gtk.gdk.ACTION_COPY)
        obj.drag_source_set(gtk.gdk.BUTTON1_MASK, [dnd_type.target()],
                            gtk.gdk.ACTION_COPY)
        obj.connect('drag_data_get', self.drag_data_get)
        obj.connect('drag_data_received',self.drag_data_received)

    def drag_data_get(self,widget, context, sel_data, info, time):
        node = self.list_model.get_selected_objects()

        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(node[0]);
        data = str((self.dnd_type.drag_type, self.person.get_handle(),
                    pickled));
        sel_data.set(sel_data.target, bits_per, data)

    def unpickle(self, data):
        self.data.insert(pickle.loads(data))
    
    def drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.list_model.get_row_at(x,y)
        
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if mytype != self.dnd_type.drag_type:
                return
            elif person == self.person.get_handle():
                self.move_element(self.list_model.get_selected_row(),row)
            else:
                self.unpickle(data[2])
            self.changed = True
            self.redraw()

    def move_element(self,src,dest):
        if src != -1:
            obj = self.data[src]
            self.data.remove(obj)
            self.data.insert(dest,obj)

class AttrListBox(ReorderListBox):

    def __init__(self, parent, person, obj, label, button_list):

        attrlist = Utils.personal_attributes

        titles = [
            # Title          Sort Col, Size, Type
            (_('Attribute'), NOSORT,   200,  COMBO,  attrlist, self.set_type),
            (_('Value'),     NOSORT,   350,  TEXT,   None,     self.set_value),
            (_('Source'),    NOSORT,   50,   TOGGLE, None,     None),
            (_('Note'),      NOSORT,   50,   TOGGLE, None,     None),
            ]

        self.data = person.get_attribute_list()[:]
        ListBox.__init__(self, parent, person, obj, label,
                         button_list, titles)

    def set_type(self,index,value):
        self.data[index].set_type(value)

    def set_value(self,index,value):
        self.data[index].set_value(value)

    def add(self,obj):
        """Brings up the AttributeEditor for a new attribute"""
        AttrEdit.AttributeEditor(self.parent, None, self.name,
                                 Utils.personal_attributes,
                                 self.edit_callback,self.parent.window)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            attr = self.list_model.get_object(node)
            AttrEdit.AttributeEditor(self.parent, attr, self.name,
                                     Utils.personal_attributes,
                                     self.edit_callback,self.parent.window)

    def display_data(self,attr):
        has_note = attr.get_note()
        has_source = len(attr.get_source_references())> 0
        return [const.display_pattr(attr.get_type()), attr.get_value(),
                has_source, has_note]

class EventListBox(ReorderListBox):
    
    titles = ['Event', 'Description','Date','Place','Source','Note']

    def __init__(self,parent,person,obj,label,button_list):

        self.data = []
        birth_ref = person.get_birth_ref()
        death_ref = person.get_death_ref()
        if birth_ref:
            self.data.append((birth_ref,
                             parent.db.get_event_from_handle(birth_ref.ref)))
        if death_ref:
            self.data.append((death_ref,
                             parent.db.get_event_from_handle(death_ref.ref)))
        for event_ref in person.get_event_ref_list():
            self.data.append((event_ref,
                              parent.db.get_event_from_handle(event_ref.ref)))

        eventnames = Utils.personal_events.values()

        evalues = [
            # Title            Sort Col Size, Type    Argument
            (_('Event'),       NOSORT,  100,  COMBO,  eventnames, self.set_name),
            (_('Description'), NOSORT,  140,  TEXT,   None,       self.set_description),
            (_('Date'),        NOSORT,  100,  TEXT,   None,       self.set_date),
            (_('Place'),       NOSORT,  100,  TEXT,   None,       self.set_place),
            (_('Source'),      NOSORT,  50,   TOGGLE, None,       None),
            (_('Note'),        NOSORT,  50,   TOGGLE, None,       None),
            ]
        
        ReorderListBox.__init__(self, parent, person, obj, label,
                                button_list, evalues, DdTargets.EVENT)

        self.name_map = {}
        self.val_map = Utils.personal_events
        self.custom = RelLib.Event.CUSTOM
        for key in self.val_map.keys():
            self.name_map[self.val_map[key]] = key

    def set_name(self,index,value):
        val = self.name_map.get(value,self.custom)
        if val == self.custom:
            self.data[index][1].set_type((val,value))
        else:
            self.data[index][1].set_type((val,self.val_map[val]))
        self.change_list.add(self.data[index])

    def set_description(self,index,value):
        self.data[index][1].set_description(value)
        self.change_list.add(self.data[index])

    def set_place(self,index,value):
        self.data[index][1].set_description(value)
        self.change_list.add(self.data[index])

    def set_date(self,index,value):
        self.data[index][1].set_date(value)
        self.change_list.add(self.data[index])

    def add(self,obj):
        """Brings up the EventEditor for a new event"""
        EventEdit.EventEditor(
            self.parent, self.name, Utils.personal_events,
            None, None, False,
            self.edit_callback, noedit=self.db.readonly)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if not node:
            return
        event = self.list_model.get_object(node)
        EventEdit.EventEditor(
            self.parent, self.name, Utils.personal_events,
            event[1], None, False,
            self.edit_callback, noedit=self.db.readonly)

    def display_data(self,event_tuple):
        (event_ref, event) = event_tuple
        pid = event.get_place_handle()
        if pid:
            pname = self.db.get_place_from_handle(pid).get_title()
        else:
            pname = u''
        has_note = event.get_note()
        has_source = len(event.get_source_references())> 0
        etype = event.get_type()
        if etype[0] == RelLib.Event.CUSTOM:
            name = etype[1]
        else:
            name = Utils.personal_events[etype[0]]
        return [name,
                event.get_description(), event.get_date(),
                pname, has_source, has_note]

    def unpickle(self, data):
        foo = pickle.loads(data);
        for src in foo.get_source_references():
            base_handle = src.get_base_handle()
            newbase = self.db.get_source_from_handle(base_handle)
            src.set_base_handle(newbase.get_handle())
        place = foo.get_place_handle()
        if place:
            foo.set_place_handle(place.get_handle())
        self.data.insert(row,foo.get_handle())

    def edit_callback(self,data):
        self.changed = True
        changed = False
        for val in self.data:
            if data.handle == val[1].handle:
                self.change_list.add(val)
                changed = True
        if not changed:
            ref = RelLib.EventRef()
            ref.ref = data.handle
            new_data = (ref,data)
            self.change_list.add(new_data)
            self.data.append(new_data)
        self.redraw()
        try:
            self.list_model.select_iter(self.node_map[new_data])
        except:
            print "Edit callback failed"

class NameListBox(ReorderListBox):
    
    def __init__(self,parent,person,obj,label,button_list):

        surnames = parent.db.get_surname_list()
        types = Utils.name_types.values()

        titles = [
            # Title            Sort Col Size, Type
            (_('Family Name'), NOSORT,  150,  COMBO,  surnames, self.set_name),
            (_('Prefix'),      NOSORT,  50,   TEXT,   None,     self.set_prefix),
            (_('Given Name'),  NOSORT,  200,  TEXT,   None,     self.set_given),
            (_('Suffix'),      NOSORT,  50,   TEXT,   None,     self.set_suffix),
            (_('Type'),        NOSORT,  150,  COMBO,  types,    self.set_type),
            (_('Source'),      NOSORT,  50,   TOGGLE, None,     None),
            (_('Note'),        NOSORT,  50,   TOGGLE, None,     None),
            ]

        self.data = person.get_alternate_names()[:]
        ReorderListBox.__init__(self, parent, person, obj, label,
                                button_list, titles, DdTargets.NAME)

    def set_name(self,index,value):
        self.data[index].set_surname(value)

    def set_prefix(self,index,value):
        self.data[index].set_surname_prefix(value)

    def set_given(self,index,value):
        self.data[index].set_first_name(value)

    def set_suffix(self,index,value):
        self.data[index].set_suffix(value)

    def set_type(self,index,value):
        self.data[index].set_type(value[1])

    def add(self,obj):
        NameEdit.NameEditor(self.parent, None, self.edit_callback,
                            self.parent.window)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            NameEdit.NameEditor(self.parent, self.list_model.get_object(node),
                                self.edit_callback, self.window)

    def display_data(self,name):
        has_note = name.get_note()
        has_source = len(name.get_source_references())> 0
        return [name.get_surname(),name.get_surname_prefix(),
                name.get_first_name(), name.get_suffix(),
                name.get_type()[1],has_source,has_note]

    def unpickle(self, data):
        foo = pickle.loads(data);
        for src in foo.get_source_references():
            base_handle = src.get_base_handle()
            newbase = self.db.get_source_from_handle(base_handle)
            src.set_base_handle(newbase.get_handle())
        self.data.insert(row,foo)

class AddressListBox(ReorderListBox):
    
    def __init__(self,parent,person,obj,label,button_list):

        titles = [
            # Title              Sort Col Size, Type
            (_('Date'),          NOSORT,  175,  TEXT,   None, self.set_date),
            (_('Address'),       NOSORT,  150,  TEXT,   None, self.set_addr),
            (_('City'),          NOSORT,  100,  TEXT,   None, self.set_city),
            (_('State/Province'),NOSORT,  75,   TEXT,   None, self.set_state),
            (_('Country'),       NOSORT,  100,  TEXT,   None, self.set_country),
            (_('Source'),        NOSORT,  50,   TOGGLE, None, None),
            (_('Note'),          NOSORT,  50,   TOGGLE, None, None),
            ]

        self.data = person.get_address_list()[:]
        ReorderListBox.__init__(self, parent, person, obj, label,
                                button_list, titles, DdTargets.ADDRESS)

    def set_date(self,index,value):
        self.data[index].set_date(value)

    def set_addr(self,index,value):
        self.data[index].set_street(value)

    def set_city(self,index,value):
        self.data[index].set_city(value)

    def set_state(self,index,value):
        self.data[index].set_state(value)

    def set_country(self,index,value):
        self.data[index].set_country(value)

    def add(self,obj):
        AddrEdit.AddressEditor(self.parent, None, self.edit_callback,
                               self.parent.window)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            item = self.list_model.get_object(node)
            AddrEdit.AddressEditor(self.parent, item,
                                   self.edit_callback, self.parent.window)

    def display_data(self,item):
        has_note = item.get_note()
        has_source = len(item.get_source_references())> 0
        return [item.get_date(),item.get_street(),
                item.get_city(), item.get_state(),
                item.get_country(), has_source,has_note]

    def unpickle(self,data):
        foo = pickle.loads(data);
        for src in foo.get_source_references():
            base_handle = src.get_base_handle()
            newbase = self.db.get_source_from_handle(base_handle)
            src.set_base_handle(newbase.get_handle())
        self.data.insert(row,foo)

class UrlListBox(ReorderListBox):
    
    def __init__(self,parent,person,obj,label,button_list):

        titles = [
            # Title            Sort Col  Size, Type
            (_('Path'),        NOSORT,   250,  TEXT, None, self.set_path),
            (_('Description'), NOSORT,   100,  TEXT, None, self.set_description),
            ]

        self.data = person.get_url_list()[:]
        ReorderListBox.__init__(self, parent, person, obj, label,
                                button_list, titles, DdTargets.URL)

    def set_path(self,index,value):
        self.data[index].set_path(value)

    def set_description(self,index,value):
        self.data[index].set_description(value)

    def add(self,obj):
        UrlEdit.UrlEditor(self.parent, self.name, None,
                          self.edit_callback, self.parent.window)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            UrlEdit.UrlEditor(self.parent, self.name,
                              self.list_model.get_object(node),
                              self.edit_callback, self.window)

    def display_data(self,url):
        return [url.get_path(), url.get_description()]


