#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2003  Donald N. Allingham
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
