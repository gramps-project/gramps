#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import re
import os
import sys
import intl
import gtk

_ = intl.gettext

#-------------------------------------------------------------------------
#
# Base filter class
#
#-------------------------------------------------------------------------
class Filter:
    
    #-------------------------------------------------------------------------
    #
    # Initializes the class
    #
    #-------------------------------------------------------------------------
    def __init__(self,text):
        self.text = text
        self.invert = 0

    #-------------------------------------------------------------------------
    #
    # compare
    #
    #-------------------------------------------------------------------------
    def set_invert(self,invert):
        self.invert = invert

    #-------------------------------------------------------------------------
    #
    # compare
    #
    #-------------------------------------------------------------------------
    def compare(self,person):
        val = self.match(person)
        if self.invert:
            return not val
        else:
            return val

    #-------------------------------------------------------------------------
    #
    # __repr__ - print representation
    #
    #-------------------------------------------------------------------------
    def __repr__(self):
        return str(self.__class__)

    #-------------------------------------------------------------------------
    #
    # match - returns true if a match is made.  The base class matches 
    # everything.  
    #
    #-------------------------------------------------------------------------
    def match(self,person):
        return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

_filter_list = [(Filter, _("All people"), 0)]

def register_filter(class_name, description=None, qualifier=0):
    if description == None:
        description = _("No description")
    _filter_list.append((class_name,description,qualifier))

#-------------------------------------------------------------------------
#
# load_filters - loads all filters in the specfied directory.  Assumes
# that the filters will register themselves
#
#-------------------------------------------------------------------------
def load_filters(dir):
    pymod = re.compile(r"^(.*)\.py$")

    if not os.path.isdir(dir):
        return
    sys.path.append(dir)
        
    for file in os.listdir(dir):
        name = os.path.split(file)
        match = pymod.match(name[1])
        if match:
            groups = match.groups()
            try: 
                plugin = __import__(groups[0])
            except:
                print _("Failed to load the module: %s") % groups[0]
                import traceback
                traceback.print_exc()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def build_filter_menu(callback):
    myMenu = gtk.GtkMenu()
    for filter in _filter_list:
        menuitem = gtk.GtkMenuItem(filter[1])
        myMenu.append(menuitem)
        menuitem.set_data("filter",filter[0])
        menuitem.set_data("qual",filter[2])
        menuitem.connect("activate",callback)
        menuitem.show()
    return myMenu


