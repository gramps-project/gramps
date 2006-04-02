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

# $Id: DisplayState.py 6085 2006-03-05 23:39:20Z dallingham $

import Errors
import gtk
from cStringIO import StringIO

#-------------------------------------------------------------------------
#
# Window manager
#
#-------------------------------------------------------------------------

_win_top = '<ui><menubar name="MenuBar"><menu action="WindowsMenu">'
_win_btm = '</menu></menubar></ui>'
DISABLED = -1

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

    def __init__(self,uimanager):
        # initialize empty tree and lookup dictionary
        self.uimanager = uimanager
        self.window_tree = []
        self.id2item = {}
        self.action_group = gtk.ActionGroup('WindowManger')
        self.active = DISABLED
        self.ui = _win_top + _win_btm
        
    def disable(self):
        """
        Removes the UI and action groups if the navigation is enabled
        """
        if self.active != DISABLED:
            self.uimanager.remove_ui(self.active)
            self.uimanager.remove_action_group(self.action_group)
            self.active = DISABLED

    def enable(self):
        """
        Enables the UI and action groups
        """
        self.uimanager.insert_action_group(self.action_group, 1)
        self.active = self.uimanager.add_ui_from_string(self.ui)

    def get_item_from_track(self,track):
        # Recursively find an item given track sequence
        item = self.window_tree
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
        item = self.get_item_from_track(track)
        self.recursive_action(item,self.close_item)
        # This only needs to be run once for the highest level point
        # to remove.
        self.remove_item(track)

    def recursive_action(self,item,func,*args):
        # This function recursively calls itself over the child items
        # starting with the given item.
        # Eventualy, every non-list item (leaf) will be reached
        # and the func(item,*args) will be called on that item.
        if type(item) == list:
            # If this item is a branch
            # close the children except for the first one
            for sub_item in item[1:]:
                self.recursive_action(sub_item,func,*args)
            # return the first child
            last_item = item[0]
        else:
            # This item is a leaf -- no children to close
            # return itself
            last_item = item
        func(last_item,*args)

    def close_item(self,item,*args):
        # Given an item, close its window and remove it's ID from the dict
        if item.window_id:
            del self.id2item[item.window_id]
        if item.window:
            item.window.destroy()

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
        # Adjust each item following the removed one
        # so that it's track is down by one on this level
        for ix in range(child_in_parent,len(parent_item)):
            item = parent_item[ix]
            self.recursive_action(item,self.move_item_down,len(track)-1)
        # Rebuild menu
        self.build_windows_menu()

    def move_item_down(self,item,*args):
        # Given an item and an index, adjust the item's track
        # by subtracting 1 from that index's level
        index = args[0]
        item.track[index] -= 1

    def add_item(self,track,item):
        # if the item is identifiable then we need to remember
        # its id so that in the future we recall this window
        # instead of spawning a new one
        if item.window_id:
            self.id2item[item.window_id] = item

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
                if item.window_id and self.id2item.get(item.window_id):
                    self.id2item[item.window_id].present()
        else:
            def f(obj):
                pass
        return f

    def generate_id(self,item):
        return str(item.window_id)

    def display_menu_list(self,data,action_data,mlist):
        i = mlist[0]
        idval = self.generate_id(i)
        data.write('<menu action="M:%s">' % idval)
        data.write('<menuitem action="%s"/>' % idval)

        action_data.append(("M:"+idval,None,i.submenu_label,None,None,None))
        action_data.append((idval,None,i.menu_label,None,None,
                            self.call_back_factory(i)))

        if len(mlist) > 1:
            for i in mlist[1:]:
                if type(i) == list:
                    self.display_menu_list(data,action_data,i)
                else:
                    idval = self.generate_id(i)
                    data.write('<menuitem action="%s"/>'
                               % self.generate_id(i))        
                    action_data.append((idval,None,i.menu_label,None,None,
                                        self.call_back_factory(i)))
        data.write('</menu>')
        
    def build_windows_menu(self):
        if self.active != DISABLED:
            self.uimanager.remove_ui(self.active)
            self.uimanager.remove_action_group(self.action_group)

        self.action_group = gtk.ActionGroup('WindowManger')
        action_data = []

        data = StringIO()
        data.write(_win_top)
        for i in self.window_tree:
            self.display_menu_list(data,action_data,i)
        data.write(_win_btm)
        self.ui = data.getvalue()
        data.close()
        self.action_group.add_actions(action_data)
        self.enable()

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

    def __init__(self,uistate,track,obj):
        """
        Create child windows and add itself to menu, if not there already.
        
        
        The usage from derived classes is envisioned as follows:
        
        
        import ManagedWindow
        class SomeWindowClass(ManagedWindow.ManagedWindow):
            def __init__(self,uistate,dbstate,track):
                window_id = self        # Or e.g. window_id = person.handle
                submenu_label = None    # This window cannot have children
                menu_label = 'Menu label for this window'
                ManagedWindow.ManagedWindow.__init__(self,
                                                    uistate,
                                                    track,
                                                    window_id,
                                                    submenu_label,
                                                    menu_label)
                # Proceed with the class.
                ...
                
        """
        window_key = self.build_window_key(obj)
        menu_label,submenu_label = self.build_menu_names(obj)
            
        if uistate.gwm.get_item_from_id(window_key):
            uistate.gwm.get_item_from_id(window_key).present()
            raise Errors.WindowActiveError('This window is already active')
        else:
            self.window_id = window_key
            self.submenu_label = submenu_label
            self.menu_label = menu_label
            self.uistate = uistate
            self.track = self.uistate.gwm.add_item(track,self)
            # Work out parent_window
            if len(self.track) > 1:
            # We don't belong to the lop level
                if self.track[-1] > 0:
                # If we are not the first in the group,
                # then first in that same group is our parent
                    parent_item_track = self.track[:-1]
                    parent_item_track.append(0)
                else:
                # If we're first in the group, then our parent
                # is the first in the group one level up
                    parent_item_track = self.track[:-2]
                    parent_item_track.append(0)

                # Based on the track, get item and then window object
                self.parent_window = self.uistate.gwm.get_item_from_track(
                    parent_item_track).window
            else:
                # On the top level: we use gramps top window
                self.parent_window = self.uistate.window

    def set_window(self, window):
        self.window = window

    def build_menu_names(self,obj):
        return ('Undefined Menu','Undefined Submenu')

    def build_window_key(self,obj):
        return id(self)

    def show(self):
        assert(self.window)
        self.window.set_transient_for(self.parent_window)
        self.window.show()

    def close(self,obj=None,obj2=None):
        """
        Close itself.

        Takes care of closing children and removing itself from menu.
        """
        self.uistate.gwm.close_track(self.track)

    def present(self):
        """
        Present window (unroll/unminimize/bring to top).
        """
        assert(self.window)
        self.window.present()
