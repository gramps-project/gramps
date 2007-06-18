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

"""
Base history navigation class. Builds the action group and ui for the
uimanager. Changes to the associated history objects are tracked. When
the history changes, the UI XML string and the action groups are updated.

"""

__author__ = "Donald N. Allingham"
__revision__ = "$Revision$"


#-------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------
import gtk
from BasicUtils import NameDisplay

DISABLED = -1

#-------------------------------------------------------------------
#
# UI Manager XML code
#
#-------------------------------------------------------------------
_top = [
    '<ui>'
    '<menubar name="MenuBar">'
    '<menu action="GoMenu">'
    '<placeholder name="CommonHistory">'
    ]

_btm = [
    '</placeholder>'
    '</menu>'
    '</menubar>'
    '</ui>'
    ]


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
    def __init__(self, dbstate, uistate, history, title):
        self.title = title
        self.ui = "".join(_top) + "".join(_btm)
        self.dbstate = dbstate
        self.uistate = uistate
        self.action_group = gtk.ActionGroup(self.title)
        self.active = DISABLED
        self.items = []
        self.func = []
        self.history = history

    def clear(self):
        """
        Clears out the specified history
        """
        self.history.clear()
        
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
            self.uistate.uimanager.ensure_update()

    def build_item_name(self, handle):
        """
        Builds a string from the passed handle. Must be overridden by the
        derrived class.
        """
        return "ERROR"

    def update_menu(self, items):
        """
        Builds the UI and action group. 
        """
        self.items = items
        self.disable()
        menu_len = min(len(items), 10)
        entry = '<menuitem action="%s%02d"/>'
        
        data = [ entry % (self.title, index) for index in range(0, menu_len) ]
        self.ui = "".join(_top) + "".join(data) + "".join(_btm)
        self.action_group = gtk.ActionGroup(self.title)
        data = []
        index = 0

        mitems = items[:]
        mitems.reverse()
        for item in mitems[:10]:
            name = self.build_item_name(item)
            func = self.func[index]
            data.append(('%s%02d'%(self.title, index), None,  name,
                         "<alt>%d" % index, None, func))
            index += 1

        self.action_group.add_actions(data)
        self.enable()

        
class PersonNavigation(BaseNavigation):
    """
    Builds a navigation item for the Person class.
    """
    def __init__(self, dbstate, uistate):
        """
        Associates the functions with the associated items. Builds the function
        array so that there are unique functions for each possible index (0-9)
        The callback simply calls change_active_handle
        """
        BaseNavigation.__init__(self, dbstate, uistate,
                                uistate.phistory, 'PersonHistory')
        fcn_ptr = self.dbstate.change_active_handle
        
        self.func = [ generate(fcn_ptr, self.items, index) \
                      for index in range(0, 10) ]

    def build_item_name(self, item):
        """
        Builds a name in the format of 'NAME [GRAMPSID]'
        """
        person = self.dbstate.db.get_person_from_handle(item)
        return  "%s [%s]" % (NameDisplay.displayer.display(person),
                             person.gramps_id)

def generate(func, items, index):
    """
    Generates a callback function based off the passed arguments
    """
    return lambda x: func(items[index])
