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
import gnome

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import traceback
import os
import sys
import string
import re
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsKeys
import Errors
import Report
import PluginMgr

#-------------------------------------------------------------------------
#
# PluginDialog interface class
#
#-------------------------------------------------------------------------

class PluginDialog:
    """Displays the dialog box that allows the user to select the
    report that is desired."""

    def __init__(self,parent,db,active,item_list,msg,label=None,
                 button_label=None,tool_tip=None):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""
        
        self.parent = parent
        if self.parent.child_windows.has_key(msg):
            self.parent.child_windows[msg].present(None)
            return
        self.db = db
        self.active = active
        self.update = None
        self.imap = {}
        self.msg = msg
        
        self.dialog = gtk.glade.XML(const.pluginsFile,"report","gramps")
        self.dialog.signal_autoconnect({
            "on_report_apply_clicked" : self.on_apply_clicked,
            "destroy_passed_object"   : self.close,
            "on_delete_event"         : self.on_delete_event,
            })

        self.tree = self.dialog.get_widget("tree")
        self.top = self.dialog.get_widget("report")
        self.title = self.dialog.get_widget("title")

        Utils.set_titles(self.top, self.title, msg )

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
        self.statbox = self.dialog.get_widget("statbox")
        
        self.apply_button = self.dialog.get_widget("apply")
        if button_label:
            self.apply_button.set_label(button_label)
        else:
            self.apply_button.set_label(_("_Apply"))
        self.apply_button.set_use_underline(gtk.TRUE)
        if tool_tip:
            try:
                tt = gtk.tooltips_data_get(self.apply_button)
                if tt:
                    tt[0].set_tip(self.apply_button,tool_tip)
            except AttributeError:
                pass

        self.run_tool = None
        self.report_vs_tool = len(item_list[0]) == 9
        if self.report_vs_tool:
            self.build_report_tree(item_list)
        else:
            self.build_tool_tree(item_list)
        self.add_itself_to_menu()
        self.top.show()

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,ok=0):
        self.remove_itself_from_menu()
        self.top.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.msg] = self
        self.win_menu_item = gtk.MenuItem(self.msg)
        self.win_menu_item.connect("activate",self.present)
        self.win_menu_item.show()
        self.parent.winsmenu.append(self.win_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.msg]
        self.win_menu_item.destroy()

    def present(self,obj):
        self.top.present()

    def on_apply_clicked(self,obj):
        """Execute the selected report"""

        if self.report_vs_tool:
            (report_class,options_class,title,category,name) = self.run_tool
            Report.report(self.db,self.active,
                        report_class,options_class,title,name,category)
        elif self.run_tool:
            if self.update:
                self.run_tool(self.db,self.active,self.update,self.parent)
            else:
                self.run_tool(self.db,self.active)

    def on_node_selected(self,obj):
        """Updates the informational display on the right hand side of
        the dialog box with the description of the selected report"""

        store,node = self.selection.get_selected()
        if node:
            path = store.get_path(node)
        if not node or not self.imap.has_key(path):
            self.statbox.hide()
            return 
        self.statbox.show()
        data = self.imap[path]

        if self.report_vs_tool:
            (report_class,options_class,title,
                category,name,doc,status,author,email) = data
        else:
            title = data[0]
            task = data[1]
            doc = data[2]
            status = data[3]
            author = data[4]
            email = data[5]

        self.description.set_text(doc)
        self.status.set_text(status)
        self.title.set_text('<span weight="bold" size="larger">%s</span>' % title)
        self.title.set_use_markup(1)
        self.author_name.set_text(author)
        self.author_email.set_text(email)
        if self.report_vs_tool:
            self.run_tool = (report_class,options_class,title,category,name)
        else:
            self.run_tool = task

    def build_tool_tree(self,item_list):
        """Populates a GtkTree with each menu item assocated with a entry
        in the lists. The list must consist of a tuples with the following
        format:
        
        (task_to_call, category, report name, description, image, status, author_name, author_email)
        
        Items in the same category are grouped under the same submen. The
        task_to_call is bound to the 'select' callback of the menu entry."""

        ilist = []

        # build the tree items and group together based on the category name
        item_hash = {}
        for report in item_list:
            t = (report[2],report[0],report[3],report[4],report[5],report[6])
            if item_hash.has_key(report[1]):
                item_hash[report[1]].append(t)
            else:
                item_hash[report[1]] = [t]

        # add a submenu for each category, and populate it with the
        # GtkTreeItems that are associated with it.
        key_list = item_hash.keys()
        key_list.sort()
        key_list.reverse()
        
        prev = None
        for key in key_list:
            data = item_hash[key]
            node = self.store.insert_after(None,prev)
            self.store.set(node,0,key)
            next = None
            data.sort()
            for item in data:
                next = self.store.insert_after(node,next)
                ilist.append((next,item))
                self.store.set(next,0,item[0])
        for next,tab in ilist:
            path = self.store.get_path(next)
            self.imap[path] = tab

    def build_report_tree(self,item_list):
        """Populates a GtkTree with each menu item assocated with a entry
        in the lists. The list must consist of a tuples with the following
        format:
        
        (task_to_call, category, report name, description, image, status, author_name, author_email)
        
        Items in the same category are grouped under the same submen. The
        task_to_call is bound to the 'select' callback of the menu entry."""

        ilist = []

        # build the tree items and group together based on the category name
        item_hash = {}
        for report in item_list:
            category = const.standalone_categories[report[3]]
            if item_hash.has_key(category):
                item_hash[category].append(report)
            else:
                item_hash[category] = [report]

        # add a submenu for each category, and populate it with the
        # GtkTreeItems that are associated with it.
        key_list = item_hash.keys()
        key_list.sort()
        key_list.reverse()
        
        prev = None
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

    def __init__(self,parent,db,active):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""
        PluginDialog.__init__(
            self,parent,
            db,
            active,
            PluginMgr.report_list,_("Report Selection"),
            _("Select a report from those available on the left."),
            _("_Generate"), _("Generate selected report"))

#-------------------------------------------------------------------------
#
# ToolPlugins interface class
#
#-------------------------------------------------------------------------
class ToolPlugins(PluginDialog):
    """Displays the dialog box that allows the user to select the tool
    that is desired."""

    def __init__(self,parent,db,active,update):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""

        PluginDialog.__init__(
            self,
            parent,
            db,
            active,
            PluginMgr.tool_list,
            _("Tool Selection"),
            _("Select a tool from those available on the left."),
            _("_Run"),
            _("Run selected tool"))
        self.update = update

#-------------------------------------------------------------------------
#
# PluginStatus
#
#-------------------------------------------------------------------------
status_up = None

class PluginStatus:
    """Displays a dialog showing the status of loaded plugins"""
    
    def __init__(self):
        global status_up
        if status_up:
            status_up.close(None)
        status_up = self

        import cStringIO
        
        self.glade = gtk.glade.XML(const.pluginsFile,"plugstat","gramps")
        self.top = self.glade.get_widget("plugstat")
        self.top.set_title("%s - GRAMPS" % _('Plugin status'))
        window = self.glade.get_widget("text")
        self.pop_button = self.glade.get_widget("pop_button")
        self.pop_button.set_active(GrampsKeys.get_pop_plugin_status())
        self.pop_button.connect('toggled',
            lambda obj: GrampsKeys.save_pop_plugin_status(self.pop_button.get_active()))
        GrampsKeys.client.notify_add("/apps/gramps/behavior/pop-plugin-status",
                                    self.pop_button_update)
        self.glade.signal_autoconnect({
            'on_close_clicked'  : self.close,
            'on_help_clicked'   : self.help,
            'on_plugstat_delete_event'   : self.on_delete,
            })

        info = cStringIO.StringIO()

        if len(PluginMgr.expect_list) + len(PluginMgr.failmsg_list) == 0:
            window.get_buffer().set_text(_('All modules were successfully loaded.'))
        else:
            info.write(_("The following modules could not be loaded:"))
            info.write("\n\n")
            
            for (filename,msg) in PluginMgr.expect_list:
                info.write("%s: %s\n\n" % (filename,msg))

            for (filename,msgs) in PluginMgr.failmsg_list:
                error = str(msgs[0])
                if error[0:11] == "exceptions.":
                    error = error[11:]
                info.write("%s: %s\n" % (filename,error) )
                traceback.print_exception(msgs[0],msgs[1],msgs[2],None,info)
                info.write('\n')
            info.seek(0)
            window.get_buffer().set_text(info.read())

    def on_delete(self,obj1,obj2):
        status_up = None

    def close(self,obj):
        self.top.destroy()
        status_up = None

    def help(self,obj):
        """Display the GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-getting-started')

    def pop_button_update(self, client,cnxn_id,entry,data):
        self.pop_button.set_active(GrampsKeys.get_pop_plugin_status())

#-------------------------------------------------------------------------
#
# Building pulldown menus
#
#-------------------------------------------------------------------------
def build_menu(top_menu,list,callback):
    report_menu = gtk.Menu()
    report_menu.show()
    
    hash_data = {}
    for report in list:
        if hash_data.has_key(report[1]):
            hash_data[report[1]].append((report[2],report[0]))
        else:
            hash_data[report[1]] = [(report[2],report[0])]

    catlist = hash_data.keys()
    catlist.sort()
    for key in catlist:
        entry = gtk.MenuItem(key)
        entry.show()
        report_menu.append(entry)
        submenu = gtk.Menu()
        submenu.show()
        entry.set_submenu(submenu)
        lst = hash_data[key]
        lst.sort()
        for name in lst:
            subentry = gtk.MenuItem("%s..." % name[0])
            subentry.show()
            subentry.connect("activate",callback,name[1])
            submenu.append(subentry)
    top_menu.set_submenu(report_menu)

#-------------------------------------------------------------------------
#
# build_report_menu
#
#-------------------------------------------------------------------------
def build_report_menu(top_menu,callback):
#    build_menu(top_menu,_reports,callback)
#def build_menu(top_menu,list,callback):
    report_menu = gtk.Menu()
    report_menu.show()
    
    hash_data = {}
    for report in PluginMgr.report_list:
        standalone_category = const.standalone_categories[report[3]]
        if hash_data.has_key(standalone_category):
            hash_data[standalone_category].append(
                    (report[0],report[1],report[2],report[4],report[3]))
        else:
            hash_data[standalone_category] = [
                    (report[0],report[1],report[2],report[4],report[3])]

#   0               1               2           3       4
#report_class, options_class, translated_name, name, category,

    catlist = hash_data.keys()
    catlist.sort()
    for key in catlist:
        entry = gtk.MenuItem(key)
        entry.show()
        report_menu.append(entry)
        submenu = gtk.Menu()
        submenu.show()
        entry.set_submenu(submenu)
        lst = hash_data[key]
        lst.sort()
        for name in lst:
            subentry = gtk.MenuItem("%s..." % name[2])
            subentry.show()
            subentry.connect("activate",callback,Report.report,name[0],name[1],name[2],name[3],name[4])
            submenu.append(subentry)
    top_menu.set_submenu(report_menu)


#-------------------------------------------------------------------------
#
# build_tools_menu
#
#-------------------------------------------------------------------------
def build_tools_menu(top_menu,callback):
    build_menu(top_menu,PluginMgr.tool_list,callback)

#-------------------------------------------------------------------------
#
# get_text_doc_menu
#
#-------------------------------------------------------------------------
class GrampsTextFormatComboBox(gtk.ComboBox):

    def set(self,tables,callback,obj=None,active=None):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)

        out_pref = GrampsKeys.get_output_preference()
        index = 0
        PluginMgr.textdoc_list.sort()
        active_index = 0
        for item in PluginMgr.textdoc_list:
            if tables and item[2] == 0:
                continue
            name = item[0]
            self.store.append(row=[name])
            #if callback:
            #    menuitem.connect("activate",callback)
            if name == active:
                active_index = index
            elif not active and name == out_pref:
                active_index = index
            index = index + 1
        self.set_active(active_index)

    def get_label(self):
        return PluginMgr.textdoc_list[self.get_active()][0]

    def get_reference(self):
        return PluginMgr.textdoc_list[self.get_active()][1]

    def get_paper(self):
        return PluginMgr.textdoc_list[self.get_active()][3]

    def get_styles(self):
        return PluginMgr.textdoc_list[self.get_active()][4]

    def get_ext(self):
        return PluginMgr.textdoc_list[self.get_active()][5]

    def get_printable(self):
        return PluginMgr.textdoc_list[self.get_active()][6]

class GrampsDrawFormatComboBox(gtk.ComboBox):

    def set(self,tables,callback,obj=None,active=None):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)

        out_pref = GrampsKeys.get_output_preference()
        index = 0
        PluginMgr.drawdoc_list.sort()
        active_index = 0
        for item in PluginMgr.drawdoc_list:
            if tables and item[2] == 0:
                continue
            name = item[0]
            self.store.append(row=[name])
            #if callback:
            #    menuitem.connect("activate",callback)
            if name == active:
                active_index = index
            elif not active and name == out_pref:
                active_index = index
            index = index + 1
        self.set_active(active_index)

    def get_reference(self):
        return PluginMgr.drawdoc_list[self.get_active()][1]

    def get_label(self):
        return PluginMgr.drawdoc_list[self.get_active()][0]

    def get_paper(self):
        return PluginMgr.drawdoc_list[self.get_active()][2]

    def get_styles(self):
        return PluginMgr.drawdoc_list[self.get_active()][3]

    def get_ext(self):
        return PluginMgr.drawdoc_list[self.get_active()][4]

    def get_printable(self):
        return PluginMgr.drawdoc_list[self.get_active()][5]

class GrampsBookFormatComboBox(gtk.ComboBox):

    def set(self,tables,callback,obj=None,active=None):
        self.store = gtk.ListStore(str)
        self.set_model(self.store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)

        out_pref = GrampsKeys.get_output_preference()
        index = 0
        PluginMgr.drawdoc_list.sort()
        active_index = 0
        self.data = []
        for item in PluginMgr.bookdoc_list:
            if tables and item[2] == 0:
                continue
            self.data.append(item)
            name = item[0]
            self.store.append(row=[name])
            if name == active:
                active_index = index
            elif not active and name == out_pref:
                active_index = index
            index += 1
        self.set_active(active_index)

    def get_reference(self):
        return self.data[self.get_active()][1]

    def get_label(self):
        return self.data[self.get_active()][0]

    def get_paper(self):
        return self.data[self.get_active()][3]

    def get_ext(self):
        return self.data[self.get_active()][5]

    def get_printable(self):
        return self.data[self.get_active()][6]

#-------------------------------------------------------------------------
#
# reload_plugins
#
#-------------------------------------------------------------------------
def reload_plugins(obj=None,junk1=None,junk2=None,junk3=None):
    """Treated as a callback, causes all plugins to get reloaded. This is
    useful when writing and debugging a plugin"""
    
    pymod = re.compile(r"^(.*)\.py$")

    oldfailmsg = PluginMgr.failmsg_list[:]
    PluginMgr.failmsg_list = []

    # attempt to reload all plugins that have succeeded in the past
    for plugin in PluginMgr._success_list:
        filename = os.path.basename(plugin.__file__)
        filename = filename.replace('pyc','py')
        filename = filename.replace('pyo','py')
        try: 
            reload(plugin)
        except:
            PluginMgr.failmsg_list.append((filename,sys.exc_info()))
            
    # attempt to load the plugins that have failed in the past
    
    for (filename,message) in oldfailmsg:
        name = os.path.split(filename)
        match = pymod.match(name[1])
        if not match:
            continue
        PluginMgr.attempt_list.append(filename)
        plugin = match.groups()[0]
        try: 
            # For some strange reason second importing of a failed plugin
            # results in success. Then reload reveals the actual error.
            # Looks like a bug in Python.
            a = __import__(plugin)
            reload(a)
            PluginMgr._success_list.append(a)
        except:
            PluginMgr.failmsg_list.append((filename,sys.exc_info()))

    # attempt to load any new files found
    for directory in PluginMgr.loaddir_list:
        for filename in os.listdir(directory):
            name = os.path.split(filename)
            match = pymod.match(name[1])
            if not match:
                continue
            if filename in PluginMgr.attempt_list:
                continue
            PluginMgr.attempt_list.append(filename)
            plugin = match.groups()[0]
            try: 
                a = __import__(plugin)
                if a not in PluginMgr._success_list:
                    PluginMgr._success_list.append(a)
            except:
                PluginMgr.failmsg_list.append((filename,sys.exc_info()))

    if GrampsKeys.get_pop_plugin_status() and len(PluginMgr.failmsg_list):
        PluginStatus()
    else:
        status_up.close(None)
        status_up = None

#-------------------------------------------------------------------------
#
# Register the plugin reloading tool
#
#-------------------------------------------------------------------------
PluginMgr.register_tool(
    reload_plugins,
    _("Reload plugins"),
    category=_("Debug"),
    description=_("Attempt to reload plugins. Note: This tool itself is not reloaded!"),
    )
