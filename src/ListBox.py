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
import locale

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
import DateHandler

class ListBox:
    """
    The ListBox manages the lists contained by the EditPerson or Marriage
    dialogs. It manages the add, update, and delete buttons, along with the
    handling of inline editing.

    The primary argument is either Person or Family object.
    """
    def __init__(self, state, uistate, track, 
                 primary, obj, label, button_list, titles):
        self.primary = primary
        if self.primary.__class__.__name__ == 'Person':
            self.name = NameDisplay.displayer.display(primary)
        elif self.primary.__class__.__name__ == 'Family':
            self.name = Utils.family_name(primary,state.db)
        else:
            self.name = ""
        self.label = label
        self.db = state.db
        self.state = state
        self.uistate = uistate
        self.track = track
        self.list_model = ListModel(
            obj, titles, self.select_row, self.update)
        self.blist = button_list
        self.node_map = {}
        self.tree = obj
        self.changed = False
        self.blist[0].connect('clicked',self.add)
        self.blist[1].connect('clicked',self.update)
        self.blist[2].connect('clicked',self.delete)
        if len(self.blist) > 3:
            self.blist[3].connect('clicked',self.select)
        self.tree.connect('key_press_event', self.keypress)
        self.change_list = Set()

    def build_maps(self,custom,string_map):
        name_map = {}
        val_map = string_map
        for key in val_map.keys():
            val = val_map[key]
            name_map[val] = key
        return (name_map,val_map)

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
        for button in self.blist[1:3]:
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
            self.data.remove(self.list_model.get_object(node))
            self.list_model.remove(node)
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

    def __init__(self,state,uistate,track,
                 primary,obj,label,button_list,evalues, dnd_type):

        ListBox.__init__(self,state,uistate,track,
                         primary,obj,label,button_list,evalues)

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
        data = str((self.dnd_type.drag_type, self.primary.get_handle(), pickled));
        sel_data.set(sel_data.target, bits_per, data)

    def unpickle(self, data):
        self.data.insert(pickle.loads(data))
    
    def drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.list_model.get_row_at(x,y)
        
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'primary = "%s"' % data[1]
            if mytype != self.dnd_type.drag_type:
                return
            elif primary == self.primary.get_handle():
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

    def __init__(self, state, uistate, track,
                 primary, obj, label, button_list):

        if primary.__class__.__name__ == 'Person':
            self.attr_dict = Utils.personal_attributes
        elif primary.__class__.__name__ == 'Family':
            self.attr_dict = Utils.family_attributes

        custom_str = self.attr_dict[RelLib.Attribute.CUSTOM]
        attrlist = filter(lambda x: x != custom_str,
                          self.attr_dict.values())
        attrlist.sort(locale.strcoll)

        titles = [
            # Title          Sort Col, Size, Type
            (_('Attribute'), NOSORT,   200,  COMBO,  attrlist, self.set_type),
            (_('Value'),     NOSORT,   350,  TEXT,   None,     self.set_value),
            (_('Source'),    NOSORT,   50,   TOGGLE, None,     None),
            (_('Note'),      NOSORT,   50,   TOGGLE, None,     None),
            ]

        self.data = primary.get_attribute_list()[:]
        ListBox.__init__(self, state, uistate, track,
                         primary, obj, label,
                         button_list, titles)

        self.attr_name_map,self.attr_val_map = self.build_maps(
            RelLib.Attribute.CUSTOM,self.attr_dict)

    def set_type(self,index,value):
        val = self.attr_name_map.get(value,RelLib.Attribute.CUSTOM)
        if val == RelLib.Attribute.CUSTOM:
            self.data[index].set_type((val,value))
        else:
            self.data[index].set_type((val,self.attr_val_map[val]))
        self.change_list.add(self.data[index])

    def set_value(self,index,value):
        self.data[index].set_value(value)

    def add(self,obj):
        """Brings up the AttributeEditor for a new attribute"""
        AttrEdit.AttributeEditor(self.state, self.uistate, self.track,
                                 None, self.name, self.attr_dict,
                                 self.edit_callback)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            attr = self.list_model.get_object(node)
            AttrEdit.AttributeEditor(self.state, self.uistate, self.track,
                                     attr, self.name, self.attr_dict,
                                     self.edit_callback)

    def display_data(self,attr):
        has_note = attr.get_note()
        has_source = len(attr.get_source_references())> 0

        etype = attr.get_type()
        if etype[0] == RelLib.Attribute.CUSTOM \
               or not self.attr_dict.has_key(etype[0]):
            name = etype[1]
        else:
            name = self.attr_dict[etype[0]]

        return [name, attr.get_value(), has_source, has_note]

class EventListBox(ReorderListBox):
    
    titles = ['Event', 'Description','Date','Place','Source','Note']

    def __init__(self,state,uistate,track,primary,obj,label,button_list):

        self.data = []
        self.primary = primary
        self.state = state
        self.uistate = uistate
        if self.primary.__class__.__name__ == 'Person':
            birth_ref = primary.get_birth_ref()
            death_ref = primary.get_death_ref()
            if birth_ref:
                self.data.append(
                    (birth_ref,state.db.get_event_from_handle(birth_ref.ref)))
                if death_ref:
                    self.data.append(
                        (death_ref,
                         state.db.get_event_from_handle(death_ref.ref))
                        )
            self.ev_dict = Utils.personal_events
            self.role_dict = Utils.event_roles
        elif self.primary.__class__.__name__ == 'Family':
            self.ev_dict = Utils.family_events
            self.role_dict = Utils.family_event_roles

        for event_ref in primary.get_event_ref_list():
            self.data.append((event_ref,
                              state.db.get_event_from_handle(event_ref.ref)))

        ev_custom_str = self.ev_dict[RelLib.Event.CUSTOM]
        eventnames = filter(lambda x: x != ev_custom_str,
                            self.ev_dict.values())
        eventnames.sort(locale.strcoll)

        role_custom_str = self.role_dict[RelLib.EventRef.CUSTOM]
        rolenames = filter(lambda x: x != role_custom_str,
                           self.role_dict.values())

        self.place_dict = {} 
        for handle in self.state.db.get_place_handles():
            title = self.state.db.get_place_from_handle(handle).get_title()
            self.place_dict[title] = handle
        placenames = self.place_dict.keys()
        placenames.sort(locale.strcoll)
        
        evalues = [
            # Title            Sort Col Size, Type    Argument
            (_('Event'),       NOSORT, 100, COMBO,  eventnames,self.set_type),
            (_('Description'), NOSORT, 140, TEXT,   None,self.set_description),
            (_('Date'),        NOSORT, 100, TEXT,   None,      self.set_date),
            (_('Place'),       NOSORT, 100, TEXT,   None,      self.set_place),
            (_('Role'),        NOSORT, 100, COMBO,  rolenames, self.set_role),
            (_('Source'),      NOSORT, 50,  TOGGLE, None,      None),
            (_('Note'),        NOSORT, 50,  TOGGLE, None,      None),
            ]
        
        ReorderListBox.__init__(self, state, uistate, track,
                                primary, obj, label,
                                button_list, evalues, DdTargets.EVENT)

        self.ev_name_map,self.ev_val_map = self.build_maps(
            RelLib.Event.CUSTOM,self.ev_dict)
        self.ref_name_map,self.ref_val_map = self.build_maps(
            RelLib.EventRef.CUSTOM,self.role_dict)

    def set_type(self,index,value):
        val = self.ev_name_map.get(value,RelLib.Event.CUSTOM)
        if val == RelLib.Event.CUSTOM:
            self.data[index][1].set_type((val,value))
        else:
            self.data[index][1].set_type((val,self.ev_val_map[val]))
        self.change_list.add(self.data[index])

    def set_role(self,index,value):
        val = self.ref_name_map.get(value,RelLib.EventRef.CUSTOM)
        if val == RelLib.EventRef.CUSTOM:
            self.data[index][0].set_role((val,value))
        else:
            self.data[index][0].set_role((val,self.ref_val_map[val]))
        self.change_list.add(self.data[index])

    def set_description(self,index,value):
        self.data[index][1].set_description(value)
        self.change_list.add(self.data[index])

    def set_place(self,index,value):
        if not value.strip():
            return
        handle = self.place_dict.get(value,None)
        if handle:
            place = self.state.db.get_place_from_handle(handle)
        else:
            place = RelLib.Place()
            place.set_title(value)
            trans = self.state.db.transaction_begin()
            self.state.db.add_place(place,trans)
            self.state.db.transaction_commit(trans,_("Add Place"))
            handle = place.get_handle()
        
        self.data[index][1].set_place_handle(handle)
        self.change_list.add(self.data[index])

    def set_date(self,index,value):
        DateHandler.set_date(self.data[index][1],value)
        self.change_list.add(self.data[index])

    def add(self,obj):
        """Brings up the EventEditor for a new event"""
        EventEdit.EventRefEditor(self.state,self.uistate,self.track,
                                 None,None,self.primary,self.edit_callback)

    def select(self,obj):
        """
        Creates eventref for an existing event.
        """
        # select existing event
        import SelectEvent
        sel_event = SelectEvent.SelectEvent(self.state.db,_('Select Event'))
        event = sel_event.run()
        if event:
            EventEdit.EventRefEditor(self.state,self.uistate,self.track,
                                     event,None,self.primary,
                                     self.edit_callback)
    
    def update(self,obj):
        store,node = self.list_model.get_selected()
        if not node:
            return
        event_ref,event = self.list_model.get_object(node)
        EventEdit.EventRefEditor(self.state,self.uistate,self.track,
                                 event,event_ref,self.primary,
                                 self.edit_callback)   

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
        if etype[0] == RelLib.Event.CUSTOM \
               or not self.ev_dict.has_key(etype[0]):
            name = etype[1]
        else:
            name = self.ev_dict[etype[0]]
        ref_role = event_ref.get_role()
        if ref_role[0] == RelLib.EventRef.CUSTOM \
               or not self.role_dict.has_key(ref_role[0]):
            role = ref_role[1]
        else:
            role = self.role_dict[ref_role[0]]
        return [name, event.get_description(), DateHandler.get_date(event),
                pname, role, has_source, has_note]

class NameListBox(ReorderListBox):
    
    def __init__(self, state, uistate, track, person, obj, label, button_list):

        surnames = state.db.get_surname_list()

        custom_str = Utils.name_types[RelLib.Name.CUSTOM]
        types = filter(lambda x: x != custom_str, Utils.name_types.values())
        types.sort(locale.strcoll)

        titles = [
            # Title            Sort Col Size, Type
            (_('Family Name'), NOSORT,  180,  COMBO,  surnames, self.set_name),
            (_('Prefix'),      NOSORT,  50,   TEXT,   None,     self.set_prefix),
            (_('Given Name'),  NOSORT,  200,  TEXT,   None,     self.set_given),
            (_('Suffix'),      NOSORT,  50,   TEXT,   None,     self.set_suffix),
            (_('Type'),        NOSORT,  150,  COMBO,  types,    self.set_type),
            (_('Source'),      NOSORT,  50,   TOGGLE, None,     None),
            (_('Note'),        NOSORT,  50,   TOGGLE, None,     None),
            ]

        self.data = person.get_alternate_names()[:]
        ReorderListBox.__init__(self, state, uistate, track,
                                person, obj, label,
                                button_list, titles, DdTargets.NAME)

        self.name_name_map,self.name_val_map = self.build_maps(
            RelLib.Name.CUSTOM,Utils.name_types)

    def set_type(self,index,value):
        val = self.name_name_map.get(value,RelLib.Name.CUSTOM)
        if val == RelLib.Name.CUSTOM:
            self.data[index].set_type((val,value))
        else:
            self.data[index].set_type((val,self.name_val_map[val]))
        self.change_list.add(self.data[index])

    def set_name(self,index,value):
        self.data[index].set_surname(value)

    def set_prefix(self,index,value):
        self.data[index].set_surname_prefix(value)

    def set_given(self,index,value):
        self.data[index].set_first_name(value)

    def set_suffix(self,index,value):
        self.data[index].set_suffix(value)

    def add(self,obj):
        NameEdit.NameEditor(self.state, self.uistate, self.track,
                            None, self.edit_callback)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            NameEdit.NameEditor(self.state, self.uistate, self.track,
                                self.list_model.get_object(node),
                                self.edit_callback)

    def display_data(self,name):
        has_note = name.get_note()
        has_source = len(name.get_source_references())> 0
        the_type = name.get_type()
        if the_type[0] == RelLib.Name.CUSTOM or \
                not Utils.name_types.has_key(the_type[0]):
            type_name = the_type[1]
        else:
            type_name = Utils.name_types[the_type[0]]
        return [name.get_surname(),name.get_surname_prefix(),
                name.get_first_name(), name.get_suffix(),
                type_name,has_source,has_note]

    def unpickle(self, data):
        foo = pickle.loads(data);
        for src in foo.get_source_references():
            base_handle = src.get_base_handle()
            newbase = self.db.get_source_from_handle(base_handle)
            src.set_base_handle(newbase.get_handle())
        self.data.insert(row,foo)

class AddressListBox(ReorderListBox):
    
    def __init__(self,state,uistate,track,person,obj,label,button_list):

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
        ReorderListBox.__init__(self, state, uistate, track,
                                person, obj, label,
                                button_list, titles, DdTargets.ADDRESS)

    def set_date(self,index,value):
        DateHandler.set_date(self.data[index],value)

    def set_addr(self,index,value):
        self.data[index].set_street(value)

    def set_city(self,index,value):
        self.data[index].set_city(value)

    def set_state(self,index,value):
        self.data[index].set_state(value)

    def set_country(self,index,value):
        self.data[index].set_country(value)

    def add(self,obj):
        AddrEdit.AddressEditor(self.state, self.uistate, self.track, None,
                               self.edit_callback)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            item = self.list_model.get_object(node)
            AddrEdit.AddressEditor(self.state, self.uistate, self.track, item,
                                   self.edit_callback)

    def display_data(self,item):
        has_note = item.get_note()
        has_source = len(item.get_source_references())> 0
        return [DateHandler.get_date(item),item.get_street(),
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
    
    def __init__(self,state,uistate,track,person,obj,label,button_list):

        titles = [
            # Title            Sort Col  Size, Type
            (_('Path'),        NOSORT,   250,  TEXT, None, self.set_path),
            (_('Description'), NOSORT,   100,  TEXT, None, self.set_description),
            ]
        self.data = person.get_url_list()[:]
        ReorderListBox.__init__(self, state, uistate, track,
                                person, obj, label,
                                button_list, titles, DdTargets.URL)

    def set_path(self,index,value):
        self.data[index].set_path(value)

    def set_description(self,index,value):
        self.data[index].set_description(value)

    def add(self,obj):
        UrlEdit.UrlEditor(self.state, self.uistate, self.track,
                          self.name, None, self.edit_callback)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            UrlEdit.UrlEditor(self.state, self.uistate, self.track,
                              self.name,
                              self.list_model.get_object(node),
                              self.edit_callback)

    def display_data(self,url):
        return [url.get_path(), url.get_description()]
