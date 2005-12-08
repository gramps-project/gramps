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

#-------------------------------------------------------------------------
#
# GNOME python modules
#
#-------------------------------------------------------------------------
import gobject
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import GrampsDbBase
import GrampsDBCallback
import GrampsKeys
import NameDisplay

#-------------------------------------------------------------------------
#
# History manager
#
#-------------------------------------------------------------------------
class History(GrampsDBCallback.GrampsDBCallback):

    __signals__ = {
        'changed'      : (list,),
        'menu-changed' : (list,),
        }

    def __init__(self):
        GrampsDBCallback.GrampsDBCallback.__init__(self)
        self.history = []
        self.mhistory = []
        self.index = -1
        self.lock = False

    def clear(self):
        self.history = []
        self.mistory = []
        self.index = -1
        self.lock = False

    def remove(self,person_handle,old_id=None):
        """Removes a person from the history list"""
        if old_id:
            del_id = old_id
        else:
            del_id = person_handle

        hc = self.history.count(del_id)
        for c in range(hc):
            self.history.remove(del_id)
            self.index -= 1
        
        mhc = self.mhistory.count(del_id)
        for c in range(mhc):
            self.mhistory.remove(del_id)
        self.emit('changed',(self.history,))
        self.emit('menu-changed',(self.mhistory,))

    def push(self,person_handle):
        self.prune()
        if len(self.history) == 0 or person_handle != self.history[-1]:
            self.history.append(person_handle)
            if person_handle not in self.mhistory:
                self.mhistory.append(person_handle)
            else:
                self.mhistory.remove(person_handle)
                self.mhistory.push(person_handle)
            self.index += 1
        self.emit('menu-changed',(self.mhistory,))
        self.emit('changed',(self.history,))

    def forward(self,step=1):
        self.index += step
        person_handle = self.history[self.index]
        if person_handle not in self.mhistory:
            self.mhistory.append(person_handle)
            self.emit('menu-changed',(self.mhistory,))
        return str(self.history[self.index])

    def back(self,step=1):
        self.index -= step
        person_handle = self.history[self.index]
        if person_handle not in self.mhistory:
            self.mhistory.append(person_handle)
            self.emit('menu-changed',(self.mhistory,))
        return str(self.history[self.index])

    def at_end(self):
        return self.index+1 == len(self.history)

    def at_front(self):
        return self.index <= 0

    def prune(self):
        if not self.at_end():
            self.history = self.history[0:self.index+1]

#-------------------------------------------------------------------------
#
# Window manager
#
#-------------------------------------------------------------------------
class GrampsWindowManager:

    def __init__(self):
        self.window_tree = []
        self.id2item = {}

    def get_item_from_node(self,node):
        item = self.window_tree
        for index in node:
            item = item[index]
        return item

    def get_window_from_id(self,window_id):
        return self.id2item.get(window_id,None)
    
    def close_node(self,node):
        import traceback
        traceback.print_stack()
        item = self.get_item_from_node(node)
        self.close_item_recursively(item)
        self.remove_node(node)

    def close_item_recursively(self,item):
        if type(item) == list:
            for sub_item in item[1:]:
                self.close_item_recursively(sub_item)
        else:
            if item.window_id:
                del self.id2item[item.window_id]
            item.window.destroy()
    
    def add_item(self,node,item):
        if item.window_id:
            self.id2item[item.window_id] = item

        parent_item = self.get_item_from_node(node)
        assert type(parent_item) == list or node == [], \
               "Gwm: add_item: Incorrect node."
        if item.submenu_label:
            # This is an item with potential children
            new_item = [item]
        else:
            # This is an item without children
            new_item = item
        parent_item.append(new_item)
        new_node = node + [len(parent_item) + 1]
        self.build_windows_menu()
        return new_node

    def remove_node(self,node):
        parent_node = node[:-1]
        child_in_parent = node[-1:][0]
        item = self.get_item_from_node(parent_node)
        item.pop(child_in_parent)
        self.build_windows_menu()

    def call_back_factory(self,item):
        if type(item) != list:
            def f(obj):
                if item.window_id and self.get_window_from_id(item.window_id):
                    self.get_window_from_id(item.window_id).present()
        else:
            def f(obj):
                pass
        return f

    def build_windows_menu(self):
        print self.window_tree
        print self.id2item
        pass

#-------------------------------------------------------------------------
#
# Gramps Managed Window class
#
#-------------------------------------------------------------------------
class ManagedWindow:
    """
    Managed window base class.
    
    This class provides all the goodies necessary for user-friendly window
    management in GRAMPS: registering the menu item under the Windows
    menu, keeping track of child windows, closing them on close/delete
    event, and presenting itself when selected or attempted to create again.
    """

    def __init__(self,uistate,node,window_key,submenu_label,menu_label):
        """
        Create child windows and add itself to menu, if not there already.


        The usage from derived classes is envisioned as follows:


        import DisplayState
        class SomeWindowClass(DisplayState.ManagedWindow):
            def __init__(self,uistate,dbstate,node):
                window_id = self        # Or e.g. window_id = person.handle
                submenu_label = None    # This window cannot have children
                menu_label = 'Menu label for this window'
                DisplayState.ManagedWindow.__init__(self,
                                                    uistate,
                                                    node,
                                                    window_id,
                                                    submenu_label,
                                                    menu_label)
                if self.already_exist:
                    return

                # Proceed with the class.
                ...

        """
        if uistate.gwm.get_window_from_id(window_key):
            uistate.gwm.get_window_from_id(window_key).present()
            self.already_exist = True
        else:
            self.already_exist = False
            self.window_id = window_key
            self.submenu_label = submenu_label
            self.menu_label = menu_label
            self.uistate = uistate
            self.node = self.uistate.gwm.add_item(node,self)

    def close(self):
        """
        Close itself.

        Takes care of closing children and removing itself from menu.
        """
        self.uistate.gwm.close_node(self.node)

    def present(self):
        """
        Present window (unroll/unminimize/bring to top).
        """
        self.window.present()

#-------------------------------------------------------------------------
#
# Gramps Display State class
#
#-------------------------------------------------------------------------
class DisplayState(GrampsDBCallback.GrampsDBCallback):

    __signals__ = {
        }

    def __init__(self,window,status,uimanager,dbstate):
        self.dbstate = dbstate
        self.uimanager = uimanager
        self.window = window
        GrampsDBCallback.GrampsDBCallback.__init__(self)
        self.status = status
        self.status_id = status.get_context_id('GRAMPS')
        self.phistory = History()
        self.gwm = GrampsWindowManager()

    def modify_statusbar(self,active=None):
        self.status.pop(self.status_id)
        if self.dbstate.active == None:
            self.status.push(self.status_id,"")
        else:
            if GrampsKeys.get_statusbar() <= 1:
                pname = NameDisplay.displayer.display(self.dbstate.active)
                name = "[%s] %s" % (self.dbstate.active.get_gramps_id(),pname)
            else:
                name = "" #self.display_relationship()
            self.status.push(self.status_id,name)

        while gtk.events_pending():
            gtk.main_iteration()

    def status_text(self,text):
        self.status.pop(self.status_id)
        self.status.push(self.status_id,text)
        while gtk.events_pending():
            gtk.main_iteration()
