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

import gtk

from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Base filter class
#
#-------------------------------------------------------------------------
class Filter:
    
    def __init__(self,text):
        self.text = text
        self.invert = 0

    def get_text(self):
        return self.text

    def get_invert(self):
        return self.invert

    def set_invert(self,invert):
        self.invert = invert

    def compare(self,person):
        val = self.match(person)
        if self.invert:
            return not val
        else:
            return val

    def get_name(self):
        return str(self.__class__)

    def match(self,person):
        return 1

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

_filter_list = [(Filter, _("All people"), 0, _("Qualifier"))]
_filter2class = {}
_filter2descr = {}

def register_filter(class_name, description=None, qualifier=0, label=None):
    name = str(class_name)
    if label == None:
        label = _("Qualifier")
    if description == None:
        description = _("No description")
    _filter2class[name] = class_name
    _filter2descr[name] = description
    _filter_list.append((class_name,description,qualifier,label))

def get_filter_description(name):
    if _filter2descr.has_key(name):
        return _filter2descr[name]
    else:
        return ""

def make_filter_from_name(name,qualifier,invert):
    a = _filter2class[name](qualifier)
    a.set_invert(invert)
    return a

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
        
    for filename in os.listdir(dir):
        name = os.path.split(filename)
        match = pymod.match(name[1])
        if match:
            plugin = match.groups()[0]
            try: 
                __import__(plugin)
            except:
                print _("Failed to load the module: %s") % plugin
                import traceback
                traceback.print_exc()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def build_filter_menu(callback,fw):
    myMenu = gtk.Menu()
    for filter_obj in _filter_list:
        menuitem = gtk.MenuItem(filter_obj[1])
        myMenu.append(menuitem)
        menuitem.set_data("filter",fw)
        menuitem.set_data("name",filter[1])
        menuitem.set_data("function",filter[0])
        menuitem.set_data("qual",filter[2])
        menuitem.set_data("label",filter[3])
        menuitem.connect("activate",callback)
        menuitem.show()
    return myMenu


