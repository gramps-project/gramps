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

_top = '<ui><menubar name="MenuBar"><menu action="GoMenu"><placeholder name="CommonHistory">'
_btm = '</placeholder></menu></menubar></ui>'

import gtk
import sys
import NameDisplay

DISABLED = -1

class BaseNavigation:
    """
    Base history navigation class. Builds the action group and ui for the
    uimanager. Changes to the associated history objects are tracked. When
    the history changes, the UI XML string and the action groups are updated.

    Import variables:

    self.title - name used for Action group name and Actions
    self.ui - XML string used to build menu items for UIManager
    self.action_group - associate action group for selecting items
    self.active - merge ID for the action group. DISABLED if not active
    self.items - history handles associated with the menu
    self.func - array of functions to take action based off of.
    
    """
    def __init__(self,uistate,history,title):
        self.title = title
        self.ui = _top+_btm
        history.connect('menu-changed', self.update_menu)
        self.action_group = gtk.ActionGroup(self.title)
        self.active = DISABLED
        self.uistate = uistate
        self.items = []
        
    def disable(self):
        """
        Removes the UI and action groups if the navigation is enabled
        """
        if self.active != DISABLED:
            self.uistate.uimanager.remove_ui(self.active)
            self.uistate.uimanager.remove_action_group(self.action_group)
            self.active = DISABLED

    def enable(self):
        """
        Enables the UI and action groups
        """
        if self.active == DISABLED:
            self.uistate.uimanager.insert_action_group(self.action_group, 1)
            self.active = self.uistate.uimanager.add_ui_from_string(self.ui)

    def build_item_name(self,handle):
        """
        Builds a string from the passed handle. Must be overridden by the
        derrived class.
        """
        return "ERROR"

    def update_menu(self,items):
        """
        Builds the UI and action group. 
        """
        self.items = items

        self.disable()

        data = map(lambda x: '<menuitem action="%s%02d"/>' % (self.title,x), range(0,len(items)))
        self.ui = _top + "".join(data) + _btm

        self.action_group = gtk.ActionGroup(self.title)

        data = []
        index = 0
        for item in items:
            name = self.build_item_name(item)
            f = self.func[index]
            data.append(('%s%02d'%(self.title,index), None, name, "<alt>%d" % index, None, f))
            index +=1
        self.action_group.add_actions(data)
            
        if self.active != DISABLED:
            self.enable()

        
class PersonNavigation(BaseNavigation):
    """
    Builds a navigation item for the Person class.
    """
    def __init__(self,uistate):
        """
        Associates the functions with the associated items. Builds the function
        array so that there are unique functions for each possible index (0-9)
        The callback simply calls change_active_handle
        """
        BaseNavigation.__init__(self,uistate,uistate.phistory,'PersonHistory')
        self.func = [ self.f0, self.f1, self.f2, self.f3, self.f4,
                      self.f5, self.f6, self.f7, self.f8, self.f9 ]

    def build_item_name(self, item):
        """
        Builds a name in the format of 'NAME [GRAMPSID]'
        """
        person = self.uistate.dbstate.db.get_person_from_handle(item)
        return  "%s [%s]" % (NameDisplay.displayer.display(person),
                             person.gramps_id)

    def f0(self,obj):
        self.uistate.dbstate.change_active_handle(self.items[0])

    def f1(self,obj):
        self.uistate.dbstate.change_active_handle(self.items[1])

    def f2(self,obj):
        self.uistate.dbstate.change_active_handle(self.items[2])

    def f3(self,obj):
        self.uistate.dbstate.change_active_handle(self.items[3])

    def f4(self,obj):
        self.uistate.dbstate.change_active_handle(self.items[4])

    def f5(self,obj):
        self.uistate.dbstate.change_active_handle(self.items[5])

    def f6(self,obj):
        self.uistate.dbstate.change_active_handle(self.items[6])

    def f7(self,obj):
        self.uistate.dbstate.change_active_handle(self.items[7])

    def f8(self,obj):
        self.uistate.dbstate.change_active_handle(self.items[8])

    def f9(self,obj):
        self.uistate.dbstate.change_active_handle(self.items[9])
        
