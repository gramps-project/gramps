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

"Analysis and Exploration/Interactive descendant browser"

from RelLib import *
import re
import string
import os
import utils
import intl

_ = intl.gettext

from gtk import *
from gnome.ui import *
from libglade import *

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def runTool(database,person,callback):
    global active_person
    global topDialog
    global glade_file
    global db
    
    active_person = person
    db = database

    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "desbrowse.glade"

    topDialog = GladeXML(glade_file,"top")
    topDialog.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
    })
    top = topDialog.get_widget("top")
    tree= topDialog.get_widget("tree1")

    add_to_tree(tree,active_person)

    top.show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_to_tree(tree,person):
    item = GtkTreeItem(person.getPrimaryName().getName())
    item.show()
    tree.append(item)
    subtree = None
    for family in person.getFamilyList():
        for child in family.getChildList():
            if subtree == None:
                subtree = GtkTree()
                subtree.show()
                item.set_subtree(subtree)
            add_to_tree(subtree,child)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_name():
    return _("Analysis and Exploration/Interactive descendant browser")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_description():
    return _("Provides a browsable hierarchy of the active person")

