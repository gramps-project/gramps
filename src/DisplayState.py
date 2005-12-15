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

_win_top = '<ui><menubar name="MenuBar"><menu name="WindowsMenu"><placeholder name="WinMenu">'
_win_btm = '</placeholder</menu></menubar></ui>'

class GrampsWindowManager:
    """
    Manage hierarchy of open GRAMPS windows.

    This class's purpose is to manage the hierarchy of open windows.
    The idea is to maintain the tree of branches and leaves.
    A leaf does not have children and corresponds to a single open window.
    A branch has children and corresponds to a group of windows.

    We will follow the convention of having first leaf in any given
    branch represent a parent window of the group, and the rest of the
    children leaves/branches represent windows spawned from the parent.

    The tree structure is maintained as a list of items.
    Items which are lists are branches.
    Items which are not lists are leaves.

    Lookup of an item is done via track sequence. The elements of
    the track sequence specify the lookup order: [2,3,1] means
    'take the second item of the tree, take its third child, and
    then the first child of that child'.

    Lookup can be also done by ID for windows that are identifiable.
    """

    def __init__(self):
        # initialize empty tree and lookup dictionary
        self.window_tree = []
        self.id2item = {}

    def get_item_from_track(self,track):
        # Recursively find an item given track sequence
        item = self.window_tree
        print "track", track
        for index in track:
            item = item[index]
        return item

    def get_item_from_id(self,item_id):
        # Find an item given its ID
        # Return None if the ID is not found
        return self.id2item.get(item_id,None)
    
    def close_track(self,track):
        # This is called when item needs to be closed
        # Closes all its children and then removes the item from the tree.
        print "1", track
        item = self.get_item_from_track(track)
        self.close_item(item)
        # This only needs to be run once for the highest level point
        # to remove.
        self.remove_item(track)

    def close_item(self,item):
        # This function calls children's close_item() method
        # to let the children go away cleanly.
        if type(item) == list:
            # If this item is a branch
            # close the children except for the first one
            for sub_item in item[1:]:
                self.close_item(sub_item)
            # return the first child
            last_item = item[0]
        else:
            # This item is a leaf -- no children to close
            # return itself
            last_item = item
        if last_item.window_id:
            del self.id2item[last_item.window_id]
        last_item.window.destroy()

    def remove_item(self,track):
        # We need the whole gymnastics below because our item
        # may actually be a list consisting of a single real
        # item and empty lists.
        
        # find the track corresponding to the parent item
        parent_track = track[:-1]
        # find index of our item in parent
        child_in_parent = track[-1:][0]
        # obtain parent item and remove our item from it
        parent_item = self.get_item_from_track(parent_track)
        parent_item.pop(child_in_parent)
        # Rebuild menu
        self.build_windows_menu()

    def add_item(self,track,item):
        # if the item is identifiable then we need to remember
        # its id so that in the future we recall this window
        # instead of spawning a new one
        if item.window_id:
            self.id2item[item.window_id] = item

        print "Adding: Track:", track

        # Make sure we have a track
        parent_item = self.get_item_from_track(track)
        assert type(parent_item) == list or track == [], \
               "Gwm: add_item: Incorrect track."

        # Prepare a new item, depending on whether it is branch or leaf
        if item.submenu_label:
            # This is an item with potential children -- branch
            new_item = [item]
        else:
            # This is an item without children -- leaf
            new_item = item

        # append new item to the parent
        parent_item.append(new_item)

        # rebuild the Windows menu based on the new tree
        self.build_windows_menu()

        # prepare new track corresponding to the added item and return it
        new_track = track + [len(parent_item)-1]
        return new_track

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

    def __init__(self,uistate,track,window_key,submenu_label,menu_label):
        """
        Create child windows and add itself to menu, if not there already.


        The usage from derived classes is envisioned as follows:


        import DisplayState
        class SomeWindowClass(DisplayState.ManagedWindow):
            def __init__(self,uistate,dbstate,track):
                window_id = self        # Or e.g. window_id = person.handle
                submenu_label = None    # This window cannot have children
                menu_label = 'Menu label for this window'
                DisplayState.ManagedWindow.__init__(self,
                                                    uistate,
                                                    track,
                                                    window_id,
                                                    submenu_label,
                                                    menu_label)
                if self.already_exist:
                    return

                # Proceed with the class.
                ...

        """
        if uistate.gwm.get_item_from_id(window_key):
            uistate.gwm.get_item_from_id(window_key).present()
            self.already_exist = True
        else:
            self.already_exist = False
            self.window_id = window_key
            self.submenu_label = submenu_label
            self.menu_label = menu_label
            self.uistate = uistate
            self.track = self.uistate.gwm.add_item(track,self)

    def close(self):
        """
        Close itself.

        Takes care of closing children and removing itself from menu.
        """
        self.uistate.gwm.close_track(self.track)

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
