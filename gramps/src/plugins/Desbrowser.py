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

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from RelLib import *
import Utils
import intl
import GrampsCfg

_ = intl.gettext

#------------------------------------------------------------------------
#
# GTK/GNOME modules
#
#------------------------------------------------------------------------
import GDK
import gtk
import libglade

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def runTool(database,person,callback):
    try:
        DesBrowse(database,person,callback)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

class DesBrowse:
    def __init__(self,database,person,callback):
        self.active = person
        self.db = database
        self.callback = callback

        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "desbrowse.glade"

        self.glade = libglade.GladeXML(glade_file,"top")
        self.glade.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            })
        top = self.glade.get_widget("top")
        tree= self.glade.get_widget("tree1")
        
        self.add_to_tree(tree,self.active)
        top.show()

    def add_to_tree(self,tree,person):
        item = gtk.GtkTreeItem(GrampsCfg.nameof(person))
        item.show()
        item.connect('button-press-event',self.button_press_event)
        item.set_data('d',person)
        tree.append(item)
        subtree = None
        for family in person.getFamilyList():
            for child in family.getChildList():
                if subtree == None:
                    subtree = gtk.GtkTree()
                    subtree.show()
                    item.set_subtree(subtree)
                self.add_to_tree(subtree,child)

    def button_press_event(self,obj,event):
        import EditPerson
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            person = obj.get_data('d')
            EditPerson.EditPerson(person,self.db,self.callback)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Interactive descendant browser"),
    category=_("Analysis and Exploration"),
    description=_("Provides a browsable hierarchy based on the active person")
    )


