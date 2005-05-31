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
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import gobject

def fill_combo(combo,data_list):
    store = gtk.ListStore(gobject.TYPE_STRING)

    for data in data_list:
        store.append(row=[data])
	    
    combo.set_model(store)
    combo.set_text_column(0)
    completion = gtk.EntryCompletion()
    completion.set_model(store)
    completion.set_minimum_key_length(1)
    completion.set_text_column(0)
    combo.child.set_completion(completion)

def fill_entry(entry,data_list):
    store = gtk.ListStore(gobject.TYPE_STRING)
    for data in data_list:
        store.append(row=[data])
        
    completion = gtk.EntryCompletion()
    completion.set_model(store)
    completion.set_minimum_key_length(1)
    completion.set_text_column(0)
    entry.set_completion(completion)
    
def fill_option_text(combobox,data):
    store = gtk.ListStore(str)
    for item in data:
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
        scs = StandardCustomSelector(mapping,custom_key,active_key)
        whatever_table.attach(scs,...)

    and later, when or before the dialog is closed, do:
        (i,s) = scs.get_values()

    to obtain the tuple of (int,str) corresponding to the user selection.

    No selection will return (custom_key,'') if the custom key is given,
    or (None,'') if it is not given.

    The active_key determines the default selection that will be displayed
    upon widget creation. If omitted, the entry will be empty. If present,
    then no selection on the user's part will return the
    (active_key,mapping[active_key]) tuple.
        
    """
    def __init__(self,mapping,custom_key=None,active_key=None):
        """
        Constructor for the StandardCustomSelector class.

        @param mapping: The mapping between integer and string constants.
        @type mapping:  dict
        @param custom_key: The key corresponding to the custom string entry
        @type custom_key:  int
        @param active_key: The key for the entry to make active upon creation
        @type active_key:  int
        """
        self.mapping = mapping
        self.custom_key = custom_key
        self.active_key = active_key
        self.active_index = 0
        # make model
        self.store = gtk.ListStore(gobject.TYPE_INT,gobject.TYPE_STRING)
        # fill it up using mapping
        self.fill()
        # create combo box entry
        self.selector = gtk.ComboBoxEntry(self.store,1)
        if self.active_key:
            self.selector.set_active(self.active_index)

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

    def by_value(self,f,s):
        """
        Method for sorting keys based on the values.
        """
        fv = self.mapping[f]
        sv = self.mapping[s]
        return cmp(fv,sv)

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
            return (i,s)
        entry = self.selector.child
        return (self.custom_key,entry.get_text())


#-------------------------------------------------------------------------
#
# Testing code below this point
#
#-------------------------------------------------------------------------
if __name__ == "__main__":
    def here(obj,event):
        print s.get_values()
        gtk.main_quit()


    s = StandardCustomSelector({0:'a',1:'b',2:'c'},0)
    w = gtk.Dialog()
    w.child.add(s.selector)
    w.connect('delete-event',here)
    w.show_all()
    gtk.main()
