#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
def runTool(database,person,callback,parent=None):
    try:
        DesBrowse(database,person,callback,parent)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

class DesBrowse:
    def __init__(self,database,person,callback,parent):
        self.active = person
        self.db = database
        self.callback = callback
        self.parent = parent
        self.win_key = self

        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "desbrowse.glade"

        self.glade = gtk.glade.XML(glade_file,"top","gramps")
        self.glade.signal_autoconnect({
            "destroy_passed_object" : self.close,
            "on_delete_event": self.on_delete_event,
            })
        self.window = self.glade.get_widget("top")

        Utils.set_titles(self.window,self.glade.get_widget('title'),
                         _("Descendant Browser"))
        
        self.tree = self.glade.get_widget("tree1")
        col = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.tree.append_column(col)
        self.model = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_PYOBJECT)
        self.tree.set_model(self.model)
        self.tree.set_rules_hint(gtk.TRUE)
        self.tree.set_headers_visible(gtk.FALSE)
        
        self.add_to_tree(None,None,self.active.get_id())
        self.tree.expand_all()
        self.tree.connect('event',self.button_press_event)

        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(_("Descendant Browser tool"))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def add_to_tree(self,parent_id,sib_id,person_id):
        item_id = self.model.insert_after(parent_id,sib_id)
        person = self.db.find_person_from_id(person_id)
        self.model.set(item_id,0,GrampsCfg.nameof(person))
        self.model.set(item_id,1,person_id)
        prev_id = None
        for family_id in person.get_family_id_list():
            family = self.db.find_family_from_id(family_id)
            for child_id in family.get_child_id_list():
                prev_id = self.add_to_tree(item_id,prev_id,child_id)
        return item_id
    
    def button_press_event(self,obj,event):
        import EditPerson

        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            store,iter = self.tree.get_selection().get_selected()
            if iter:
                person_id = store.get_value(iter,1)
                person = self.db.find_person_from_id(person_id)
                EditPerson.EditPerson(self.parent,person,self.db,self.callback)

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
