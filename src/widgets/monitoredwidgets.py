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

__all__ = ["MonitoredCheckbox", "MonitoredEntry", "MonitoredSpinButton",
           "MonitoredText", "MonitoredType", "MonitoredDataType",
           "MonitoredMenu", "MonitoredStrMenu", "MonitoredDate",
           "MonitoredComboSelectedEntry"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.monitoredwidgets")
import locale

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import AutoComp
import DateEdit

#-------------------------------------------------------------------------
#
# MonitoredCheckbox class
#
#-------------------------------------------------------------------------
class MonitoredCheckbox:

    def __init__(self, obj, button, set_val, get_val, on_toggle=None, readonly = False):
        self.button = button
        self.button.connect('toggled', self._on_toggle)
        self.on_toggle = on_toggle
        self.obj = obj
        self.set_val = set_val
        self.get_val = get_val
        self.button.set_active(get_val())
        self.button.set_sensitive(not readonly)

    def _on_toggle(self, obj):
        self.set_val(obj.get_active())
        if self.on_toggle:
            self.on_toggle(self.get_val())
        
#-------------------------------------------------------------------------
#
# MonitoredEntry class
#
#-------------------------------------------------------------------------
class MonitoredEntry:

    def __init__(self, obj, set_val, get_val, read_only=False, 
                 autolist=None, changed=None):
        self.obj = obj
        self.set_val = set_val
        self.get_val = get_val
        self.changed = changed

        if get_val():
            self.obj.set_text(get_val())
        self.obj.connect('changed', self._on_change)
        self.obj.set_editable(not read_only)

        if autolist:
            AutoComp.fill_entry(obj, autolist)

    def reinit(self, set_val, get_val):
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def set_text(self, text):
        self.obj.set_text(text)
        
    def connect(self, signal, callback, *data):
        self.obj.connect(signal, callback, *data)

    def _on_change(self, obj):
        self.set_val(unicode(obj.get_text()))
        if self.changed:
            self.changed(obj)

    def force_value(self, value):
        self.obj.set_text(value)

    def get_value(self, value):
        return unicode(self.obj.get_text())

    def enable(self, value):
        self.obj.set_sensitive(value)
        self.obj.set_editable(value)

    def grab_focus(self):
        self.obj.grab_focus()

    def update(self):
        if self.get_val() is not None:
            self.obj.set_text(self.get_val())

#-------------------------------------------------------------------------
#
# MonitoredSpinButton class
#
#-------------------------------------------------------------------------
class MonitoredSpinButton:
    """
    Class for signal handling of spinbuttons.
    (Code is a modified copy of MonitoredEntry)
    """

    def __init__(self, obj, set_val, get_val, read_only=False,
                 autolist=None, changed=None):
        """
        @param obj: widget to be monitored
        @type obj: gtk.SpinButton
        @param set_val: callback to be called when obj is changed
        @param get_val: callback to be called to retrieve value for obj
        @param read_only: If SpinButton is read only.
        """
        
        self.obj = obj
        self.set_val = set_val
        self.get_val = get_val
        self.changed = changed

        if get_val():
            self.obj.set_value(get_val())
        self.obj.connect('value-changed', self._on_change)
        self.obj.set_editable(not read_only)

        if autolist:
            AutoComp.fill_entry(obj,autolist)

    def reinit(self, set_val, get_val):
        """
        Reinitialize class with the specified callback functions.

        @param set_val: callback to be called when SpinButton is changed
        @param get_val: callback to be called to retrieve value for SpinButton
        """
        
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def set_value(self, value):
        """
        Set the value of the monitored widget to the specified value.

        @param value: Value to be set.
        """
        
        self.obj.set_value(value)
        
    def connect(self, signal, callback):
        """
        Connect the signal of monitored widget to the specified callback.

        @param signal: Signal prototype for which a connection should be set up.
        @param callback: Callback function to be called when signal is emitted.
        """
        
        self.obj.connect(signal, callback)

    def _on_change(self, obj):
        """
        Event handler to be called when the monitored widget is changed.

        @param obj: Widget that has been changed.
        @type obj: gtk.SpinButton
        """
        
        self.set_val(obj.get_value())
        if self.changed:
            self.changed(obj)

    def force_value(self, value):
        """
        Set the value of the monitored widget to the specified value.

        @param value: Value to be set.
        """
        
        self.obj.set_value(value)

    def get_value(self):
        """
        Get the current value of the monitored widget.

        @returns: Current value of monitored widget.
        """

        return self.obj.get_value()

    def enable(self, value):
        """
        Change the property editable and sensitive of the monitored widget to value.

        @param value: If widget should be editable or deactivated.
        @type value: bool
        """
        
        self.obj.set_sensitive(value)
        self.obj.set_editable(value)

    def grab_focus(self):
        """
        Assign the keyboard focus to the monitored widget.
        """
        
        self.obj.grab_focus()

    def update(self):
        """
        Updates value of monitored SpinButton with the value returned by the get_val callback.
        """
        
        if self.get_val():
            self.obj.set_value(self.get_val())

#-------------------------------------------------------------------------
#
# MonitoredText class
#
#-------------------------------------------------------------------------
class MonitoredText:

    def __init__(self, obj, set_val, get_val, read_only=False):
        self.buf = obj.get_buffer()
        self.set_val = set_val
        self.get_val = get_val

        if get_val():
            self.buf.set_text(get_val())
        self.buf.connect('changed', self.on_change)
        obj.set_editable(not read_only)

    def on_change(self, obj):
        s, e = self.buf.get_bounds()
        self.set_val(unicode(self.buf.get_text(s, e, False)))

#-------------------------------------------------------------------------
#
# MonitoredType class
#
#-------------------------------------------------------------------------
class MonitoredType:

    def __init__(self, obj, set_val, get_val, mapping, custom, readonly=False, 
                 custom_values=None):
        self.set_val = set_val
        self.get_val = get_val

        self.obj = obj

        val = get_val()
        if val:
            default = val[0]
        else:
            default = None

        self.sel = AutoComp.StandardCustomSelector(
            mapping, obj, custom, default, additional=custom_values)

        self.set_val(self.sel.get_values())
        self.obj.set_sensitive(not readonly)
        self.obj.connect('changed', self.on_change)

    def reinit(self, set_val, get_val):
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def update(self):
        if self.get_val():
            self.sel.set_values(self.get_val())

    def on_change(self, obj):
        self.set_val(self.sel.get_values())

#-------------------------------------------------------------------------
#
# MonitoredDataType class
#
#-------------------------------------------------------------------------
class MonitoredDataType:
    

    def __init__(self, obj, set_val, get_val, readonly=False, 
                 custom_values=None, ignore_values=None):
        """
        Constructor for the MonitoredDataType class.

        @param obj: Existing ComboBoxEntry widget to use.
        @type obj: gtk.ComboBoxEntry
        @param set_val: The function that sets value of the type in the object
        @type set_val:  method
        @param get_val: The function that gets value of the type in the object.
            This returns a GrampsType, of which get_map returns all possible types
        @type get_val:  method
        @param custom_values: Extra values to show in the combobox. These can be
            text of custom type, tuple with type info or GrampsType class
        @type : list of str, tuple or GrampsType
        @ignore_values: list of values not to show in the combobox. If the result
            of get_val is in these, it is not ignored
        @type : list of int 
        """
        self.set_val = set_val
        self.get_val = get_val

        self.obj = obj

        val = get_val()

        if val:
            default = int(val)
        else:
            default = None
            
        map = get_val().get_map().copy()
        if ignore_values :
            for key in map.keys():
                try :
                    i = ignore_values.index(key)
                except ValueError:
                    i = None
                if (i is not None) and (not ignore_values[i] == default) :
                    del map[key]

        self.sel = AutoComp.StandardCustomSelector(
            map, 
            obj, 
            get_val().get_custom(), 
            default, 
            additional=custom_values)

        self.sel.set_values((int(get_val()), str(get_val())))
        self.obj.set_sensitive(not readonly)
        self.obj.connect('changed', self.on_change)

    def reinit(self, set_val, get_val):
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def fix_value(self, value):
        if value[0] == self.get_val().get_custom():
            return value
        else:
            return (value[0], '')

    def update(self):
        val = self.get_val()
        if isinstance(val, tuple):
            self.sel.set_values(val)
        else:
            self.sel.set_values((int(val), str(val)))

    def on_change(self, obj):
        value = self.fix_value(self.sel.get_values())
        self.set_val(value)

#-------------------------------------------------------------------------
#
# MonitoredMenu class
#
#-------------------------------------------------------------------------
class MonitoredMenu:

    def __init__(self, obj, set_val, get_val, mapping, 
                 readonly=False, changed=None):
        self.set_val = set_val
        self.get_val = get_val

        self.changed = changed
        self.obj = obj

        self.change_menu(mapping)
        self.obj.connect('changed', self.on_change)
        self.obj.set_sensitive(not readonly)

    def force(self, value):
        self.obj.set_active(value)

    def change_menu(self, mapping):
        self.data = {}
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        index = 0
        for t, v in mapping:
            self.model.append(row=[t, v])
            self.data[v] = index
            index += 1
        self.obj.set_model(self.model)
        self.obj.set_active(self.data.get(self.get_val(), 0))

    def on_change(self, obj):
        self.set_val(self.model.get_value(obj.get_active_iter(), 1))
        if self.changed:
            self.changed()

#-------------------------------------------------------------------------
#
# MonitoredStrMenu class
#
#-------------------------------------------------------------------------
class MonitoredStrMenu:

    def __init__(self, obj, set_val, get_val, mapping, readonly=False):
        self.set_val = set_val
        self.get_val = get_val

        self.obj = obj
        self.model = gtk.ListStore(gobject.TYPE_STRING)
        
        if len(mapping) > 20:
            self.obj.set_wrap_width(3)

        self.model.append(row=[''])
        index = 0
        self.data = ['']

        default = get_val()
        active = 0
        
        for t, v in mapping:
            self.model.append(row=[v])
            self.data.append(t)
            index += 1
            if t == default:
                active = index
            
        self.obj.set_model(self.model)
        self.obj.set_active(active)
        self.obj.connect('changed', self.on_change)
        self.obj.set_sensitive(not readonly)

    def on_change(self, obj):
        self.set_val(self.data[obj.get_active()])

#-------------------------------------------------------------------------
#
# MonitoredDate class
#
#-------------------------------------------------------------------------
class MonitoredDate:

    def __init__(self, field, button, value, uistate, track, readonly=False):
        self.date = value
        self.date_check = DateEdit.DateEdit(
            self.date, field, button, uistate, track)
        field.set_editable(not readonly)
        button.set_sensitive(not readonly)

#-------------------------------------------------------------------------
#
# MonitoredComboSelectedEntry class
#
#-------------------------------------------------------------------------
class MonitoredComboSelectedEntry:
    """
    A MonitoredEntry driven by a Combobox to select what the entry field
    works upon
    """
    def __init__(self, objcombo, objentry, textlist, set_val_list, 
                 get_val_list, default=0, read_only=False):
        """
        Create a MonitoredComboSelectedEntry
        Objcombo and objentry should be the gtk widgets to use
        textlist is the values that must be used in the combobox
        Every value needs an entry in set/get_val_list with the data retrieval
         and storage method of the data entered in the entry box
        Read_only should be true if no changes may be done
        default is the entry in the combobox that must be preselected
        """
        self.objcombo = objcombo
        self.objentry = objentry
        self.set_val_list = set_val_list
        self.get_val_list = get_val_list
        
        #fill the combobox, set on a specific entry
        self.mapping = dict([[i,x] for (i,x) in zip(range(len(textlist)),
                                                    textlist)])

        self.active_key = default
        self.active_index = 0
        
        self.__fill()
        self.objcombo.clear()
        self.objcombo.set_model(self.store)
        cell = gtk.CellRendererText()
        self.objcombo.pack_start(cell, True)
        self.objcombo.add_attribute(cell, 'text', 1)
        self.objcombo.set_active(self.active_index)
        self.objcombo.connect('changed', self.on_combochange)
        
        #fill the entrybox with required data
        self.entry_reinit()
        self.objentry.connect('changed', self._on_change_entry)
        
        #set correct editable
        self.enable(not read_only)

    def __fill(self):
        """
        Fill combo with data
        """
        self.store = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING)
        keys = self.mapping.keys()
        keys.sort(self.__by_value)
        index = 0
        for key in keys:
            self.store.append(row=[key, self.mapping[key]])
            if key == self.active_key:
                self.active_index = index
            index = index + 1

    def __by_value(self, first, second):
        """
        Method for sorting keys based on the values.
        """
        fvalue = self.mapping[first]
        svalue = self.mapping[second]
        return locale.strcoll(fvalue, svalue)

    def on_combochange(self, obj):
        """
        callback for change on the combo, change active iter, update 
        associated entrybox
        """
        self.active_key = self.store.get_value(self.objcombo.get_active_iter(),
                                               0)
        self.entry_reinit()
    
    def reinit(self, set_val_list, get_val_list):
        """
        The interface is attached to another object, so the methods need to be
        reset.
        """
        self.set_val_list = set_val_list
        self.get_val_list = get_val_list
        self.update()

    def entry_reinit(self):
        """
        Make the entry field show the value corresponding to the active key
        """
        self.objentry.set_text(self.get_val_list[self.active_key]())
        self.set_val = self.set_val_list[self.active_key]
        self.get_val = self.get_val_list[self.active_key]

    def _on_change_entry(self, obj):
        """
        Callback when the entry field changes
        """
        self.set_val_list[self.active_key](self.get_value_entry())

    def get_value_entry(self):
        return unicode(self.objentry.get_text())

    def enable(self, value):
        self.objentry.set_sensitive(value)
        self.objentry.set_editable(value)

    def update(self):
        """
        Method called when object changed without interface change
        Eg: name editor save brings you back to person editor that must update
        """
        self.entry_reinit()
