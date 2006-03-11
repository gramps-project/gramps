#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
from gettext import gettext as _

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
import GrampsDisplay
from PluginUtils import Tool, register_tool

#-------------------------------------------------------------------------
#
# ChangeNames
#
#-------------------------------------------------------------------------
class ChangeNames(Tool.Tool):

    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        Tool.Tool.__init__(self,db,person,options_class,name)

        self.cb = callback
        self.parent = parent
        if self.parent.child_windows.has_key(self.__class__):
            self.parent.child_windows[self.__class__].present(None)
            return
        self.win_key = self.__class__
        
        self.progress = Utils.ProgressMeter(_('Checking family names'),'')
        self.progress.set_pass(_('Searching family names'),
                               len(self.db.get_surname_list()))
        self.name_list = []
        for name in self.db.get_surname_list():
            if name != name.capitalize():
                self.name_list.append(name)
            if self.parent:
                self.progress.step()
        
        if self.name_list:
            self.display()
        else:
            self.progress.close()
            OkDialog(_('No modifications made'),
                     _("No capitalization changes were detected."))

    def display(self):

        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "patchnames.glade"
        
        self.top = gtk.glade.XML(glade_file,"top","gramps")
        self.window = self.top.get_widget('top')
        self.window.set_icon(self.parent.topWindow.get_icon())
        self.top.signal_autoconnect({
            "destroy_passed_object" : self.close,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_help_clicked"       : self.on_help_clicked,
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
        self.progress.set_pass(_('Building display'),len(self.name_list))
        for name in self.name_list:
            handle = self.model.append()
            self.model.set_value(handle,0,1)
            self.model.set_value(handle,1,name)
            self.model.set_value(handle,2,name.capitalize())
            self.iter_list.append(handle)
            self.progress.step()
        self.progress.close()
            
        self.add_itself_to_menu()
        self.window.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-db')

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
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
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

        self.db.transaction_commit(self.trans,_("Capitalization changes"))
        self.db.enable_signals()
        self.db.request_rebuild()
        self.parent.bookmarks.redraw()
        self.close(obj)
        self.cb(None,1)
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class ChangeNamesOptions(Tool.ToolOptions):
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
    name = 'chname',
    category = Tool.TOOL_DBPROC,
    tool_class = ChangeNames,
    options_class = ChangeNamesOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Fix capitalization of family names"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Searches the entire database and attempts to "
                    "fix capitalization of the names.")
    )
