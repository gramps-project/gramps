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

# $Id$

"Analysis and Exploration/Interactive descendant browser"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Utils
import NameDisplay
from PluginUtils import Tool, register_tool

#------------------------------------------------------------------------
#
# GTK/GNOME modules
#
#------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade
import GrampsDisplay

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DesBrowse(Tool.Tool):

    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        Tool.Tool.__init__(self,db,person,options_class,name)

        self.active = person
        self.callback = callback
        self.parent = parent
        self.win_key = self

        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "desbrowse.glade"

        self.glade = gtk.glade.XML(glade_file,"top","gramps")
        self.glade.signal_autoconnect({
            "destroy_passed_object" : self.close,
            "on_help_clicked"       : self.on_help_clicked,
            "on_delete_event": self.on_delete_event,
            })
        self.window = self.glade.get_widget("top")
        self.window.set_icon(self.parent.topWindow.get_icon())

        self.active_name = _("Descendant Browser: %s") \
                        % NameDisplay.displayer.display(self.active)
        Utils.set_titles(self.window,self.glade.get_widget('title'),
                         self.active_name)
        
        self.tree = self.glade.get_widget("tree1")
        col = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.tree.append_column(col)
        self.tree.set_rules_hint(True)
        self.tree.set_headers_visible(False)
        self.tree.connect('event',self.button_press_event)
        self.make_new_model()

        self.add_itself_to_menu()
        self.window.show()

    def make_new_model(self):
        self.model = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_PYOBJECT)
        self.tree.set_model(self.model)
        self.add_to_tree(None,None,self.active.get_handle())
        self.tree.expand_all()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-ae')

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(self.active_name)
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def add_to_tree(self,parent_id,sib_id,person_handle):
        item_id = self.model.insert_after(parent_id,sib_id)
        person = self.db.get_person_from_handle(person_handle)
        self.model.set(item_id,0,NameDisplay.displayer.display(person))
        self.model.set(item_id,1,person_handle)
        prev_id = None
        for family_handle in person.get_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            for child_handle in family.get_child_handle_list():
                prev_id = self.add_to_tree(item_id,prev_id,child_handle)
        return item_id
    
    def button_press_event(self,obj,event):
        import EditPerson

        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            store,iter = self.tree.get_selection().get_selected()
            if iter:
                person_handle = store.get_value(iter,1)
                person = self.db.get_person_from_handle(person_handle)
                EditPerson.EditPerson(self.parent,person,self.db,self.this_callback)

    def this_callback(self,epo,val):
        self.callback(epo,val)
        self.make_new_model()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DesBrowseOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_tool(
    name = 'dbrowse',
    category = Tool.TOOL_ANAL,
    tool_class = DesBrowse,
    options_class = DesBrowseOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Interactive descendant browser"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description=_("Provides a browsable hierarchy based on the active person"),
    )
