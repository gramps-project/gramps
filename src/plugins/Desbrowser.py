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
import Utils
from gettext import gettext as _
import GrampsCfg

#------------------------------------------------------------------------
#
# GTK/GNOME modules
#
#------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade

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

        self.glade = gtk.glade.XML(glade_file,"top","gramps")
        self.glade.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            })
        top = self.glade.get_widget("top")

        Utils.set_titles(top,self.glade.get_widget('title'),
                         _("Descendant Browser"))
        
        self.tree= self.glade.get_widget("tree1")
        col = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.tree.append_column(col)
        self.model = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_PYOBJECT)
        self.tree.set_model(self.model)
        self.tree.set_rules_hint(gtk.TRUE)
        self.tree.set_headers_visible(gtk.FALSE)
        
        self.add_to_tree(None,None,self.active)
        self.tree.expand_all()
        self.tree.connect('event',self.button_press_event)

        top.show()

    def add_to_tree(self,parent,sib,person):
        item = self.model.insert_after(parent,sib)
        self.model.set(item,0,GrampsCfg.nameof(person))
        self.model.set(item,1,person)
        prev = None
        for family in person.get_family_id_list():
            for child in family.get_child_id_list():
                prev = self.add_to_tree(item,prev,child)
        return item
    
    def button_press_event(self,obj,event):
        import EditPerson

        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            store,iter = self.tree.get_selection().get_selected()
            if iter:
                person = store.get_value(iter,1)
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
    description=_("Provides a browsable hierarchy based on the active person"),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )


