#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2005  Donald N. Allingham
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
import locale

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".AutoComp")

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

def fill_combo(combo,data_list):
    store = gtk.ListStore(str)

    for data in data_list:
        if data:
            store.append(row=[data])
	    
    combo.set_model(store)
    combo.set_text_column(0)
    completion = gtk.EntryCompletion()
    completion.set_model(store)
    completion.set_minimum_key_length(1)
    completion.set_text_column(0)
    combo.child.set_completion(completion)

def fill_entry(entry,data_list):
    store = gtk.ListStore(str)

    for data in data_list:
        if data:
            store.append(row=[data])
        
    completion = gtk.EntryCompletion()
    completion.set_model(store)
    completion.set_minimum_key_length(1)
    completion.set_text_column(0)
    entry.set_completion(completion)
    
def fill_option_text(combobox,data):
    store = gtk.ListStore(str)
    for item in data:
        if item:
            store.append(row=[item])
    combobox.set_model(store)
    combobox.set_active(0)

def get_option(combobox):
    store = combobox.get_model()
    return store.get_value(combobox.get_active_iter(),0)


#-------------------------------------------------------------------------
#
# StandardCustomSelector class
#
#-------------------------------------------------------------------------
class StandardCustomSelector:
    """
    This class provides an interface to selecting from the predefined
    options or entering custom string.

    The typical usage should be:
        type_sel = StandardCustomSelector(mapping,None,custom_key,active_key)
        whatever_table.attach(type_sel,...)
    or
        type_sel = StandardCustomSelector(mapping,cbe,custom_key,active_key)
    with the existing ComboBoxEntry cbe.

    To set up the combo box, specify the active key at creation time,
    or later (or with custom text) use:
       type_sel.set_values(i,s)

    and later, when or before the dialog is closed, do:
        (i,s) = type_sel.get_values()

    to obtain the tuple of (int,str) corresponding to the user selection.

    No selection will return (custom_key,'') if the custom key is given,
    or (None,'') if it is not given.

    The active_key determines the default selection that will be displayed
    upon widget creation. If omitted, the entry will be empty. If present,
    then no selection on the user's part will return the
    (active_key,mapping[active_key]) tuple.
        
    """
    def __init__(self,mapping,cbe=None,custom_key=None,active_key=None,
                 additional=None):
        """
        Constructor for the StandardCustomSelector class.

        @param cbe: Existing ComboBoxEntry widget to use.
        @type cbe: gtk.ComboBoxEntry
        @param mapping: The mapping between integer and string constants.
        @type mapping:  dict
        @param custom_key: The key corresponding to the custom string entry
        @type custom_key:  int
        @param active_key: The key for the entry to make active upon creation
        @type active_key:  int
        """

        # set variables
        self.mapping = mapping
        self.custom_key = custom_key
        self.active_key = active_key
        self.active_index = 0
        self.additional = additional
        # make model
        self.store = gtk.ListStore(int,str)

        # fill it up using mapping
        self.fill()

        # create combo box entry
        if cbe:
            self.selector = cbe
            self.selector.set_model(self.store)
            self.selector.set_text_column(1)
        else:
            self.selector = gtk.ComboBoxEntry(self.store,1)
        if self.active_key != None:
            self.selector.set_active(self.active_index)

        # make autocompletion work
        completion = gtk.EntryCompletion()
        completion.set_model(self.store)
        completion.set_minimum_key_length(1)
        completion.set_text_column(1)
        self.selector.child.set_completion(completion)

    def fill(self):
        keys = self.mapping.keys()
        keys.sort(self.by_value)
        index = 0
        for key in keys:
            if key != self.custom_key:
                self.store.append(row=[key,self.mapping[key]])
                if key == self.active_key:
                    self.active_index = index
                index = index + 1

        if self.additional:
            for event_type in self.additional:
                if type(event_type) == str or type(event_type) == unicode :
                    self.store.append(row=[self.custom_key, event_type])
                elif type(event_type) == tuple:
                    self.store.append(row=[event_type[0], event_type[1]])
                else:
                    self.store.append(row=[int(event_type), str(event_type[1])])
                if key == self.active_key:
                    self.active_index = index
                index = index + 1

    def by_value(self,f,s):
        """
        Method for sorting keys based on the values.
        """
        fv = self.mapping[f]
        sv = self.mapping[s]
        return locale.strcoll(fv,sv)

    def get_values(self):
        """
        Get selected values.

        @return: Returns (int,str) tuple corresponding to the selection.
        @rtype: tuple
        """
        ai = self.selector.get_active_iter()
        if ai:
            i = self.store.get_value(ai,0)
            s = self.store.get_value(ai,1)
            if s != self.mapping[i]:
                s = self.selector.child.get_text().strip()
        else:
            i = self.custom_key
            s = self.selector.child.get_text().strip()
        if s in self.mapping.values():
            for key in self.mapping.keys():
                if s == self.mapping[key]:
                    i = key
                    break
        else:
            i = self.custom_key
        return (i,s)

    def set_values(self,val):
        """
        Set values according to given tuple.

        @param val: (int,str) tuple with the values to set.
        @type val: tuple
        """
        i,s = val
        if i in self.mapping.keys() and i != self.custom_key:
            self.store.foreach(self.set_int_value,i)
        elif self.custom_key != None:
            self.selector.child.set_text(s)
        else:
            print "StandardCustomSelector.set(): Option not available:", val

    def set_int_value(self,model,path,iter,val):
        if model.get_value(iter,0) == val:
            self.selector.set_active_iter(iter)
            return True
        return False


#-------------------------------------------------------------------------
#
# Testing code below this point
#
#-------------------------------------------------------------------------
if __name__ == "__main__":
    def here(obj,event):
        print s.get_values()
        gtk.main_quit()

    s = StandardCustomSelector({0:'abc',1:'abd',2:'bbe'},None,0,1)
    s.set_values((2,'bbe'))
    w = gtk.Dialog()
    w.child.add(s.selector)
    w.connect('delete-event',here)
    w.show_all()
    gtk.main()
