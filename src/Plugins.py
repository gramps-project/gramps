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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import traceback
import os
import sys
import string
from re import compile

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsCfg
import Errors

import gettext

_ = gettext.gettext

#-------------------------------------------------------------------------
#
# Global lists
#
#-------------------------------------------------------------------------
_reports = []
_tools   = []
_imports = []
_exports = []
_success = []
_failed  = []
_expect  = []
_attempt = []
_loaddir = []
_textdoc = []
_bookdoc = []
_drawdoc = []
_failmsg = []
_bkitems = []

#-------------------------------------------------------------------------
#
# Default relationship calculator
#
#-------------------------------------------------------------------------
import Relationship
_relcalc_class = Relationship.RelationshipCalculator

#-------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------
_unavailable = _("No description was provided"),

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
DOCSTRING = "d"
IMAGE     = "i"
TASK      = "f"
TITLE     = "t"
STATUS    = "s"

#-------------------------------------------------------------------------
#
# PluginDialog interface class
#
#-------------------------------------------------------------------------
class PluginDialog:
    """Displays the dialog box that allows the user to select the
    report that is desired."""

    def __init__(self,parent,db,active,list,msg,label=None,button_label=None,tool_tip=None):
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
        self.build_tree(list)
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

        if self.run_tool:
            if self.update:
                self.run_tool(self.db,self.active,self.update,self.parent)
            else:
                self.run_tool(self.db,self.active)

    def on_node_selected(self,obj):
        """Updates the informational display on the right hand side of
        the dialog box with the description of the selected report"""

        store,iter = self.selection.get_selected()
        if iter:
            path = store.get_path(iter)
        if not iter or not self.imap.has_key(path):
            self.statbox.hide()
            return 
        self.statbox.show()
        data = self.imap[path]

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
        self.run_tool = task

    def build_tree(self,list):
        """Populates a GtkTree with each menu item assocated with a entry
        in the lists. The list must consist of a tuples with the following
        format:
        
        (task_to_call, category, report name, description, image, status, author_name, author_email)
        
        Items in the same category are grouped under the same submen. The
        task_to_call is bound to the 'select' callback of the menu entry."""

        ilist = []

        # build the tree items and group together based on the category name
        item_hash = {}
        for report in list:
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
        PluginDialog.__init__(self,parent,db,active,_reports,_("Report Selection"),
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

        PluginDialog.__init__(self,parent,db,active,_tools,_("Tool Selection"),
                        _("Select a tool from those available on the left."),
                        _("_Run"), _("Run selected tool"))
        self.update = update

#-------------------------------------------------------------------------
#
# PluginStatus
#
#-------------------------------------------------------------------------
class PluginStatus:
    """Displays a dialog showing the status of loaded plugins"""
    
    def __init__(self):
        import cStringIO
        
        self.glade = gtk.glade.XML(const.pluginsFile,"plugstat","gramps")
        self.top = self.glade.get_widget("plugstat")
        self.top.set_title("%s - GRAMPS" % _('Plugin status'))
        window = self.glade.get_widget("text")
        self.glade.signal_autoconnect({
            'on_close_clicked' : self.close
            })

        info = cStringIO.StringIO()

        if len(_expect) + len(_failmsg) == 0:
            window.get_buffer().set_text(_('All modules were successfully loaded.'))
        else:
            info.write(_("The following modules could not be loaded:"))
            info.write("\n\n")
            
            for (file,msg) in _expect:
                info.write("%s: %s\n\n" % (file,msg))

            for (file,msgs) in _failmsg:
                error = str(msgs[0])
                if error[0:11] == "exceptions.":
                    error = error[11:]
                info.write("%s: %s\n" % (file,error) )
                traceback.print_exception(msgs[0],msgs[1],msgs[2],None,info)
                info.write('\n')
            info.seek(0)
            window.get_buffer().set_text(info.read())

    def close(self,obj):
        self.top.destroy()
        
#-------------------------------------------------------------------------
#
# load_plugins
#
#-------------------------------------------------------------------------
def load_plugins(direct):
    """Searches the specified directory, and attempts to load any python
    modules that it finds, adding name to the _attempts list. If the module
    successfully loads, it is added to the _success list. Each plugin is
    responsible for registering itself in the correct manner. No attempt
    is done in this routine to register the tasks."""
    
    global _success,_failed,_attempt,_loaddir
    
    # if the directory does not exist, do nothing
    if not os.path.isdir(direct):
        return

    # if the path has not already been loaded, save it in the _loaddir
    # list for use on reloading

    if direct not in _loaddir:
        _loaddir.append(direct)

    # add the directory to the python search path
    sys.path.append(direct)

    pymod = compile(r"^(.*)\.py$")

    # loop through each file in the directory, looking for files that
    # have a .py extention, and attempt to load the file. If it succeeds,
    # add it to the _success list. If it fails, add it to the _failure
    # list
    
    for file in os.listdir(direct):
        name = os.path.split(file)
        match = pymod.match(name[1])
        if not match:
            continue
        _attempt.append(file)
        plugin = match.groups()[0]
        try: 
            a = __import__(plugin)
            _success.append(a)
        except Errors.PluginError, msg:
            _expect.append((file,str(msg)))
        except:
            _failmsg.append((file,sys.exc_info()))

#-------------------------------------------------------------------------
#
# reload_plugins
#
#-------------------------------------------------------------------------
def reload_plugins(obj):
    """Treated as a callback, causes all plugins to get reloaded. This is
    useful when writing and debugging a plugin"""
    
    pymod = compile(r"^(.*)\.py$")

    # attempt to reload all plugins that have succeeded
    # in the past
    for plugin in _success:
        try: 
            reload(plugin)
        except:
            _failmsg.append((plugin,sys.exc_info()))
            
    # attempt to load the plugins that have failed in the past
    
    for plugin in _failed:
        try: 
            __import__(plugin)
            del _failmsg[plugin]
        except:
            _failmsg.append((plugin,sys.exc_info()))

    # attempt to load any new files found
    for dir in _loaddir:
        for file in os.listdir(dir):
            name = os.path.split(file)
            match = pymod.match(name[1])
            if not match:
                continue
            if file in _attempt:
                return
            _attempt.append(file)
            plugin = match.groups()[0]
            try: 
                a = __import__(plugin)
                if a not in _success:
                    _success.append(a)
            except:
                _failmsg.append((file,sys.exc_info()))

#-------------------------------------------------------------------------
#
# Plugin registering
#
#-------------------------------------------------------------------------
def register_export(exportData,_title,_description='',_config=None,_filename=''):
    """
    Register an export filter, taking the task, file filter, 
    and the list of patterns for the filename matching.
    """
    if _description and _filename:
        _exports.append((exportData,_title,_description,_config,_filename))

def register_import(task, ffilter, mime=None):
    """Register an import filter, taking the task and file filter"""
    if mime:
        _imports.append((task, ffilter, mime))

def register_report(task, name,
                    category=_("Uncategorized"),
                    description=_unavailable,
                    status=_("Unknown"),
                    author_name=_("Unknown"),
                    author_email=_("Unknown")
                    ):
    """Register a report with the plugin system"""
    
    del_index = -1
    for i in range(0,len(_reports)):
        val = _reports[i]
        if val[2] == name:
            del_index = i
    if del_index != -1:
        del _reports[del_index]
    _reports.append((task, category, name, description, status, author_name, author_email))

def register_tool(task, name,
                  category=_("Uncategorized"),
                  description=_unavailable,
                  status=_("Unknown"),
                  author_name=_("Unknown"),
                  author_email=_("Unknown")
                  ):
    """Register a tool with the plugin system"""
    del_index = -1
    for i in range(0,len(_tools)):
        val = _tools[i]
        if val[2] == name:
            del_index = i
    if del_index != -1:
        del _tools[del_index]
    _tools.append((task, category, name, description, status, author_name, author_name))

#-------------------------------------------------------------------------
#
# Text document registration
#
#-------------------------------------------------------------------------
def register_text_doc(name,classref, table, paper, style, ext,
                      print_report_label = None):
    """Register a text document generator"""
    for n in _textdoc:
        if n[0] == name:
            return
    _textdoc.append((name,classref,table,paper,style,ext,print_report_label))

#-------------------------------------------------------------------------
#
# Text document registration
#
#-------------------------------------------------------------------------
def register_book_doc(name,classref, table, paper, style, ext):
    """Register a text document generator"""
    for n in _bookdoc:
        if n[0] == name:
            return
    _bookdoc.append((name,classref,table,paper,style,ext))

#-------------------------------------------------------------------------
#
# Drawing document registration
#
#-------------------------------------------------------------------------
def register_draw_doc(name,classref,paper,style, ext,
                      print_report_label = None):
    """Register a drawing document generator"""
    for n in _drawdoc:
        if n[0] == name:
            return
    _drawdoc.append((name,classref,paper,style,ext,print_report_label))

#-------------------------------------------------------------------------
#
# Relationship calculator registration
#
#-------------------------------------------------------------------------
def register_relcalc(relclass, languages):
    """Register a relationshp calculator"""
    global _relcalc_class

    try:
        if os.environ["LANG"] in languages:
            _relcalc_class = relclass
    except:
        pass

def relationship_class(db):
    global _relcalc_class
    return _relcalc_class(db)

#-------------------------------------------------------------------------
#
# Book item registration
#
#-------------------------------------------------------------------------
def register_book_item(name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style):
    """Register a book item"""
    
    for n in _bkitems:
        if n[0] == name:
            return
    _bkitems.append((name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style))

#-------------------------------------------------------------------------
#
# Image attributes
#
#-------------------------------------------------------------------------
_image_attributes = []
def register_image_attribute(name):
    if name not in _image_attributes:
        _image_attributes.append(name)

def get_image_attributes():
    return _image_attributes

#-------------------------------------------------------------------------
#
# Building pulldown menus
#
#-------------------------------------------------------------------------
def build_menu(top_menu,list,callback):
    report_menu = gtk.Menu()
    report_menu.show()
    
    hash = {}
    for report in list:
        if hash.has_key(report[1]):
            hash[report[1]].append((report[2],report[0]))
        else:
            hash[report[1]] = [(report[2],report[0])]

    catlist = hash.keys()
    catlist.sort()
    for key in catlist:
        entry = gtk.MenuItem(key)
        entry.show()
        report_menu.append(entry)
        submenu = gtk.Menu()
        submenu.show()
        entry.set_submenu(submenu)
        list = hash[key]
        list.sort()
        for name in list:
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
    build_menu(top_menu,_reports,callback)

#-------------------------------------------------------------------------
#
# build_tools_menu
#
#-------------------------------------------------------------------------
def build_tools_menu(top_menu,callback):
    build_menu(top_menu,_tools,callback)

#-------------------------------------------------------------------------
#
# get_text_doc_menu
#
#-------------------------------------------------------------------------
def get_text_doc_menu(main_menu,tables,callback,obj=None):
    index = 0
    myMenu = gtk.Menu()
    _textdoc.sort()
    for item in _textdoc:
        if tables and item[2] == 0:
            continue
        name = item[0]
        menuitem = gtk.MenuItem(name)
        menuitem.set_data("name",item[1])
        menuitem.set_data("styles",item[4])
        menuitem.set_data("paper",item[3])
        menuitem.set_data("ext",item[5])
        menuitem.set_data("obj",obj)
        menuitem.set_data("printable",item[6])
        if callback:
            menuitem.connect("activate",callback)
        menuitem.show()
        myMenu.append(menuitem)
        if name == GrampsCfg.get_output_preference():
            myMenu.set_active(index)
            callback(menuitem)
        index = index + 1
    main_menu.set_menu(myMenu)

#-------------------------------------------------------------------------
#
# get_text_doc_menu
#
#-------------------------------------------------------------------------
def get_book_menu(main_menu,tables,callback,obj=None):

    index = 0
    myMenu = gtk.Menu()
    _bookdoc.sort()
    for item in _bookdoc:
        if tables and item[2] == 0:
            continue
        name = item[0]
        menuitem = gtk.MenuItem(name)
        menuitem.set_data("name",item[1])
        menuitem.set_data("styles",item[4])
        menuitem.set_data("paper",item[3])
        menuitem.set_data("ext",item[5])
        menuitem.set_data("obj",obj)
        if callback:
            menuitem.connect("activate",callback)
        menuitem.show()
        myMenu.append(menuitem)
        if name == GrampsCfg.get_output_preference():
            myMenu.set_active(index)
            callback(menuitem)
        index = index + 1
    main_menu.set_menu(myMenu)

#-------------------------------------------------------------------------
#
# get_text_doc_list
#
#-------------------------------------------------------------------------
def get_text_doc_list():
    l = []
    _textdoc.sort()
    for item in _textdoc:
        l.append(item[0])
    return l

#-------------------------------------------------------------------------
#
# get_text_doc_list
#
#-------------------------------------------------------------------------
def get_book_doc_list():
    l = []
    _bookdoc.sort()
    for item in _bookdoc:
        l.append(item[0])
    return l

#-------------------------------------------------------------------------
#
# get_draw_doc_list
#
#-------------------------------------------------------------------------
def get_draw_doc_list():

    l = []
    _drawdoc.sort()
    for item in _drawdoc:
        l.append(item[0])
    return l

#-------------------------------------------------------------------------
#
# get_draw_doc_menu
#
#-------------------------------------------------------------------------
def get_draw_doc_menu(main_menu,callback=None,obj=None):

    index = 0
    myMenu = gtk.Menu()
    for (name,classref,paper,styles,ext,printable) in _drawdoc:
        menuitem = gtk.MenuItem(name)
        menuitem.set_data("name",classref)
        menuitem.set_data("styles",styles)
        menuitem.set_data("paper",paper)
        menuitem.set_data("ext",ext)
        menuitem.set_data("obj",obj)
        menuitem.set_data("printable",printable)
        if callback:
            menuitem.connect("activate",callback)
        menuitem.show()
        myMenu.append(menuitem)
        if name == GrampsCfg.get_goutput_preference():
            myMenu.set_active(index)
        if callback:
            callback(menuitem)
        index = index + 1
    main_menu.set_menu(myMenu)
