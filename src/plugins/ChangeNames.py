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

"Database Processing/Extract information from names"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
import re

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
from QuestionDialog import OkDialog
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Search each name in the database, and compare the firstname against the
# form of "Name (Nickname)".  If it matches, change the first name entry
# to "Name" and add "Nickname" into the nickname field.
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback,parent=None):
    try:
        ChangeNames(database,callback,parent)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#-------------------------------------------------------------------------
#
# ChangeNames
#
#-------------------------------------------------------------------------
class ChangeNames:

    def __init__(self,db,callback,parent):
        self.cb = callback
        self.db = db
        self.parent = parent
        self.trans = db.transaction_begin()
        self.win_key = self
        self.child_windows = {}
        self.name_list = []

        for name in self.db.get_surname_list():
            if name != name.capitalize():
                self.name_list.append(name)
        
        if self.name_list:
            self.display()
        else:
            OkDialog(_('No modifications made'),
                     _("No capitalization changes where detected."))

    def display(self):

        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "patchnames.glade"
        
        self.top = gtk.glade.XML(glade_file,"top","gramps")
        self.window = self.top.get_widget('top')
        self.top.signal_autoconnect({
            "destroy_passed_object" : self.close,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_delete_event" : self.on_delete_event
            })
        self.list = self.top.get_widget("list")
        self.label = _('Capitalization changes')
        Utils.set_titles(self.window,self.top.get_widget('title'),self.label)

        self.model = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)

        r = gtk.CellRendererToggle()
        c = gtk.TreeViewColumn(_('Select'),r,active=0)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('Original Name'),
                               gtk.CellRendererText(),text=1)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('Capitalization Change'),
                               gtk.CellRendererText(),text=2)
        self.list.append_column(c)

        self.list.set_model(self.model)

        self.iter_list = []
        for name in self.name_list:
            handle = self.model.append()
            self.model.set_value(handle,0,1)
            self.model.set_value(handle,1,name)
            self.model.set_value(handle,2,name.capitalize())
            self.iter_list.append(handle)
            
        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(self.label)
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()
                
    def on_ok_clicked(self,obj):
        changelist = []
        for node in self.iter_list:
            if self.model.get_value(node,0):
                changelist.append(self.model.get_value(node,1))

        anychange = False
        for handle in self.db.get_person_handles():
            change = False
            person = self.db.get_person_from_handle(handle)
            for name in [person.get_primary_name()] + person.get_alternate_names():
                sname = name.get_surname()
                if sname in changelist:
                    change = True
                    anychange = True
                    name.set_surname(sname.capitalize())
            if change:
                self.db.commit_person(person,self.trans)

        if anychange:
            self.db.transaction_commit(self.trans,_("Capitalization changes"))
        self.close(obj)
        self.cb(1)
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from PluginMgr import register_tool

register_tool(
    runTool,
    _("Fix capitalization of family names"),
    category=_("Database Processing"),
    description=_("Searches the entire database and attempts to "
                  "fix capitalization of the names.")
    )
