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
# create - creates a new filter object from the passed data. Eliminates
# the need to know the name of the class.
#
#-------------------------------------------------------------------------
def create(text):
    return Filter(text)

#-------------------------------------------------------------------------
#
# need_qualifier - indicates if another parameter is needed.  Used to 
# enable or disable the qualifier field on the display
#
#-------------------------------------------------------------------------
def need_qualifier():
    return 0

filterList = [ _("All people") ]
filterMap  = { _("All people") : create }
filterEnb  = { _("All people") : need_qualifier }

#-------------------------------------------------------------------------
#
# load_filters - loads all filters in the specfied directory.  Looks for
# a task named "create". The create and need_qualifer tasks are loaded in
# hash tables so that the filter description can be used to retrieve the
# create and need_qualifier functions
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
        if match == None:
            continue
        groups = match.groups()
        try: 
            plugin = __import__(groups[0])
        except:
            continue

        if "get_name" in plugin.__dict__.keys():
            name = plugin.get_name()
        else:
            name = plugin.__doc__
            
        for task in plugin.__dict__.keys():
            if task == "create":
                filterMap[name] = plugin.__dict__[task]
                filterList.append(plugin.__doc__)
            if task == "need_qualifier" :
                filterEnb[name] = plugin.__dict__[task]

