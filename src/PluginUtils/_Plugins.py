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

"""
The core of the GRAMPS plugin system. This module provides tasks to load
plugins from specfied directories, build menus for the different categories,
and provide dialog to select and execute plugins.

Plugins are divided into several categories. This are: reports, tools,
importers, exporters, and document generators.
"""

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import traceback
import os
import sys
import re
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Utils
import Config
import Errors
import _Report
import _Tool
import _PluginMgr
import GrampsDisplay
import ManagedWindow

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
REPORTS = 0
TOOLS   = 1
UNSUPPORTED = _("Unsupported")

#-------------------------------------------------------------------------
#
# PluginDialog interface class
#
#-------------------------------------------------------------------------

class PluginDialog(ManagedWindow.ManagedWindow):
    """Displays the dialog box that allows the user to select the
    report that is desired."""

    def __init__(self,state, uistate, track, item_list,categories,msg,label=None,
                 button_label=None,tool_tip=None,content=REPORTS):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""
        
        self.active = state.active
        self.imap = {}
        self.msg = msg
        self.content = content

        ManagedWindow.ManagedWindow.__init__(self, uistate, [], None)

        self.state = state
        self.uistate = uistate
        
        self.dialog = gtk.glade.XML(const.plugins_glade,"report","gramps")
        self.dialog.signal_autoconnect({
            "on_report_apply_clicked" : self.on_apply_clicked,
            "destroy_passed_object"   : self.close_window,
            })

        self.tree = self.dialog.get_widget("tree")
        self.window = self.dialog.get_widget("report")
        self.title = self.dialog.get_widget("title")

        Utils.set_titles(self.window, self.title, msg )

        self.store = gtk.TreeStore(gobject.TYPE_STRING)
        self.selection = self.tree.get_selection()
        self.selection.connect('changed', self.on_node_selected)
        col = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.tree.append_column(col)
        self.tree.set_model(self.store)
        
        self.description = self.dialog.get_widget("description")
        if label:
            self.description.set_text(label)
        self.status = self.dialog.get_widget("report_status")

        Utils.set_title_label(self.dialog,msg)
        
        self.author_name = self.dialog.get_widget("author_name")
        self.author_email = self.dialog.get_widget("author_email")
        
        self.apply_button = self.dialog.get_widget("apply")
        if button_label:
            self.apply_button.set_label(button_label)
        else:
            self.apply_button.set_label(_("_Apply"))
        self.apply_button.set_use_underline(True)
        if tool_tip:
            try:
                tt = gtk.tooltips_data_get(self.apply_button)
                if tt:
                    tt[0].set_tip(self.apply_button,tool_tip)
            except AttributeError:
                pass

        self.item = None
        self.build_plugin_tree(item_list,categories)
        self.window.show()

    def close_window(self, obj):
        self.close()

    def on_apply_clicked(self,obj):
        """Execute the selected report"""

        (item_class,options_class,title,category,name) = self.item
        if self.content == REPORTS:
            _Report.report(self.state.db,self.state.active,
                          item_class,options_class,title,name,category)
        else:
            _Tool.gui_tool(self.state.db,self.state.active,
                          item_class,options_class,title,name,category,
                          self.state.db.request_rebuild,self.parent)

    def on_node_selected(self,obj):
        """Updates the informational display on the right hand side of
        the dialog box with the description of the selected report"""

        store,node = self.selection.get_selected()
        if node:
            path = store.get_path(node)
        if not node or not self.imap.has_key(path):
            return 
        data = self.imap[path]

        (report_class,options_class,title,category,name,
         doc,status,author,email,unsupported) = data
        self.description.set_text(doc)
        if unsupported:
            status = UNSUPPORTED
        self.status.set_text(status)
        self.title.set_text('<span weight="bold" size="larger">%s</span>' % title)
        self.title.set_use_markup(1)
        self.author_name.set_text(author)
        self.author_email.set_text(email)
        self.item = (report_class,options_class,title,category,name)

    def build_plugin_tree(self,item_list,categories):
        """Populates a GtkTree with each menu item assocated with a entry
        in the lists. The list must consist of a tuples with the following
        format:
        
        (item_class,options_class,title,category,name,
         doc,status,author,email)

        Items in the same category are grouped under the same submenu.
        The categories must be dicts from integer to string.
        """

        ilist = []

        # build the tree items and group together based on the category name
        item_hash = {}
        for plugin in item_list:
            if plugin[9]:
                category = UNSUPPORTED
            else:
                category = categories[plugin[3]]
            if item_hash.has_key(category):
                item_hash[category].append(plugin)
            else:
                item_hash[category] = [plugin]

        # add a submenu for each category, and populate it with the
        # GtkTreeItems that are associated with it.
        key_list = [ item for item in item_hash.keys() if item != UNSUPPORTED]
        key_list.sort()
        key_list.reverse()
        
        prev = None
        if item_hash.has_key(UNSUPPORTED):
            key = UNSUPPORTED
            data = item_hash[key]
            node = self.store.insert_after(None,prev)
            self.store.set(node,0,key)
            next = None
            data.sort(lambda x,y: cmp(x[2],y[2]))
            for item in data:
                next = self.store.insert_after(node,next)
                ilist.append((next,item))
                self.store.set(next,0,item[2])
        for key in key_list:
            data = item_hash[key]
            node = self.store.insert_after(None,prev)
            self.store.set(node,0,key)
            next = None
            data.sort(lambda x,y: cmp(x[2],y[2]))
            for item in data:
                next = self.store.insert_after(node,next)
                ilist.append((next,item))
                self.store.set(next,0,item[2])
        for next,tab in ilist:
            path = self.store.get_path(next)
            self.imap[path] = tab

#-------------------------------------------------------------------------
#
# ReportPlugins interface class
#
#-------------------------------------------------------------------------
class ReportPlugins(PluginDialog):
    """Displays the dialog box that allows the user to select the
    report that is desired."""

    def __init__(self,dbstate,uistate,track):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""
        PluginDialog.__init__(
            self,
            dbstate,
            uistate,
            track,
            _PluginMgr.report_list,
            _Report.standalone_categories,
            _("Report Selection"),
            _("Select a report from those available on the left."),
            _("_Generate"), _("Generate selected report"),
            REPORTS)

#-------------------------------------------------------------------------
#
# ToolPlugins interface class
#
#-------------------------------------------------------------------------
class ToolPlugins(PluginDialog):
    """Displays the dialog box that allows the user to select the tool
    that is desired."""

    def __init__(self,dbstate,uistate,track):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""

        PluginDialog.__init__(
            self,
            dbstate,
            uistate,
            track,
            _PluginMgr.tool_list,
            _Tool.tool_categories,
            _("Tool Selection"),
            _("Select a tool from those available on the left."),
            _("_Run"),
            _("Run selected tool"),
            TOOLS)

#-------------------------------------------------------------------------
#
# Building pulldown menus
#
#-------------------------------------------------------------------------
def build_tools_menu(top_menu,callback):
    build_plugin_menu(_PluginMgr.tool_list,
                      _Tool.tool_categories,
                      _Tool.gui_tool,
                      top_menu,callback)
    
def build_report_menu(top_menu,callback):
    build_plugin_menu(_PluginMgr.report_list,
                      _Report.standalone_categories,
                      _Report.report,
                      top_menu,callback)

def build_plugin_menu(item_list,categories,func,top_menu,callback):
    menu = gtk.Menu()
    menu.show()
    
    hash_data = {}
    for item in item_list:
        if item[9]:
            category = UNSUPPORTED
        else:
            category = categories[item[3]]
        if hash_data.has_key(category):
            hash_data[category].append(
                    (item[0],item[1],item[2],item[4],item[3]))
        else:
            hash_data[category] = [
                    (item[0],item[1],item[2],item[4],item[3])]

    # Sort categories, skipping the unsupported
    catlist = [item for item in hash_data.keys() if item != UNSUPPORTED]
    catlist.sort()
    for key in catlist:
        entry = gtk.MenuItem(key)
        entry.show()
        menu.append(entry)
        submenu = gtk.Menu()
        submenu.show()
        entry.set_submenu(submenu)
        lst = hash_data[key]
        lst.sort(by_menu_name)
        for name in lst:
            subentry = gtk.MenuItem("%s..." % name[2])
            subentry.show()
            subentry.connect("activate",callback,func,
                             name[0],name[1],name[2],name[3],name[4])
            submenu.append(subentry)

    # If there are any unsupported items we add separator
    # and the unsupported category at the end of the menu
    if hash_data.has_key(UNSUPPORTED):
        entry = gtk.MenuItem(None)
        entry.show()
        menu.append(entry)
        key = UNSUPPORTED
        entry = gtk.MenuItem(key)
        entry.show()
        menu.append(entry)
        submenu = gtk.Menu()
        submenu.show()
        entry.set_submenu(submenu)
        lst = hash_data[key]
        lst.sort(by_menu_name)
        for name in lst:
            subentry = gtk.MenuItem("%s..." % name[2])
            subentry.show()
            subentry.connect("activate",callback,func,
                             name[0],name[1],name[2],name[3],name[4])
            submenu.append(subentry)

    top_menu.set_submenu(menu)

def by_menu_name(a,b):
    return cmp(a[2],b[2])

#-------------------------------------------------------------------------
#
# Reload plugins
#
#-------------------------------------------------------------------------
class Reload(_Tool.Tool):
    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        _Tool.Tool.__init__(self,db,person,options_class,name)

        """
        Treated as a callback, causes all plugins to get reloaded.
        This is useful when writing and debugging a plugin.
        """
    
        pymod = re.compile(r"^(.*)\.py$")

        oldfailmsg = _PluginMgr.failmsg_list[:]
        _PluginMgr.failmsg_list = []

        # attempt to reload all plugins that have succeeded in the past
        for plugin in _PluginMgr._success_list:
            filename = os.path.basename(plugin.__file__)
            filename = filename.replace('pyc','py')
            filename = filename.replace('pyo','py')
            try: 
                reload(plugin)
            except:
                _PluginMgr.failmsg_list.append((filename,sys.exc_info()))
            
        # Remove previously good plugins that are now bad
        # from the registered lists
        (_PluginMgr.export_list,
         _PluginMgr.import_list,
         _PluginMgr.tool_list,
         _PluginMgr.cli_tool_list,
         _PluginMgr.report_list,
         _PluginMgr.bkitems_list,
         _PluginMgr.cl_list,
         _PluginMgr.textdoc_list,
         _PluginMgr.bookdoc_list,
         _PluginMgr.drawdoc_list) = _PluginMgr.purge_failed(
            _PluginMgr.failmsg_list,
            _PluginMgr.export_list,
            _PluginMgr.import_list,
            _PluginMgr.tool_list,
            _PluginMgr.cli_tool_list,
            _PluginMgr.report_list,
            _PluginMgr.bkitems_list,
            _PluginMgr.cl_list,
            _PluginMgr.textdoc_list,
            _PluginMgr.bookdoc_list,
            _PluginMgr.drawdoc_list)

        # attempt to load the plugins that have failed in the past
        for (filename,message) in oldfailmsg:
            name = os.path.split(filename)
            match = pymod.match(name[1])
            if not match:
                continue
            _PluginMgr.attempt_list.append(filename)
            plugin = match.groups()[0]
            try: 
                # For some strange reason second importing of a failed plugin
                # results in success. Then reload reveals the actual error.
                # Looks like a bug in Python.
                a = __import__(plugin)
                reload(a)
                _PluginMgr._success_list.append(a)
            except:
                _PluginMgr.failmsg_list.append((filename,sys.exc_info()))

        # attempt to load any new files found
        for directory in _PluginMgr.loaddir_list:
            for filename in os.listdir(directory):
                name = os.path.split(filename)
                match = pymod.match(name[1])
                if not match:
                    continue
                if filename in _PluginMgr.attempt_list:
                    continue
                _PluginMgr.attempt_list.append(filename)
                plugin = match.groups()[0]
                try: 
                    a = __import__(plugin)
                    if a not in _PluginMgr._success_list:
                        _PluginMgr._success_list.append(a)
                except:
                    _PluginMgr.failmsg_list.append((filename,sys.exc_info()))

        if Config.get_pop_plugin_status() and len(_PluginMgr.failmsg_list):
            PluginStatus()
        else:
            global status_up
            if status_up:
                status_up.close(None)
            status_up = None

        # Re-generate tool and report menus
        parent.build_plugin_menus(rebuild=True)

class ReloadOptions(_Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        _Tool.ToolOptions.__init__(self,name,person_id)

#-------------------------------------------------------------------------
#
# Register the plugin reloading tool
#
#-------------------------------------------------------------------------

if __debug__:
    _PluginMgr.register_tool(
        name = 'reload',
        category = _Tool.TOOL_DEBUG,
        tool_class = Reload,
        options_class = ReloadOptions,
        modes = _Tool.MODE_GUI,
        translated_name = _("Reload plugins"),
        description=_("Attempt to reload plugins. "
                      "Note: This tool itself is not reloaded!"),
        )
