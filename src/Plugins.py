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

"""
The core of the GRAMPS plugin system. This module provides tasks to load
plugins from specfied directories, build menus for the different categories,
and provide dialog to select and execute plugins.

Plugins are divided into several categories. This are: reports, tools,
filters, importer, exporters, and document generators.
"""

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import GdkImlib
import gtk
import libglade
#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import traceback
import os
import sys
from re import compile

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsCfg
from intl import gettext
_ = gettext

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
_drawdoc = []
_failmsg = []

_unavailable = _("No description was provided"),
#-------------------------------------------------------------------------
#
# Exception Strings
#
#-------------------------------------------------------------------------
MissingLibraries = _("Missing Libraries")

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

    def __init__(self,db,active,list,msg):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""
        
        self.db = db
        self.active = active
        self.update = None
        
        self.dialog = libglade.GladeXML(const.pluginsFile,"report")
        self.dialog.signal_autoconnect({
            "on_report_apply_clicked" : self.on_apply_clicked,
            "on_report_ok_clicked"    : self.on_apply_clicked,
            "on_tree_select_row"      : self.on_node_selected,
            "destroy_passed_object"   : Utils.destroy_passed_object
            })

        self.tree = self.dialog.get_widget("tree")
        self.top = self.dialog.get_widget("report")
        self.img = self.dialog.get_widget("image")
        self.description = self.dialog.get_widget("description")
        self.status = self.dialog.get_widget("report_status")
        self.label = self.dialog.get_widget("report_label")
        self.title = self.dialog.get_widget("title")
        
        self.run_tool = None
        self.build_tree(list)
        self.title.set_text(msg)
        self.top.set_title("%s - GRAMPS" % msg)

    def on_apply_clicked(self,obj):
        """Execute the selected report"""

        Utils.destroy_passed_object(obj)
        if self.run_tool:
            if self.update:
                self.run_tool(self.db,self.active,self.update)
            else:
                self.run_tool(self.db,self.active)

    def on_node_selected(self,obj,node,other):
        """Updates the informational display on the right hand side of
        the dialog box with the description of the selected report"""

        data = self.tree.node_get_row_data(node)
        if not data:
            return
        task = data[1]
        title = data[0]
        doc = data[2]
        xpm = data[3]
        status = data[4]

        image = GdkImlib.create_image_from_xpm(xpm)
        self.description.set_text(doc)
        self.status.set_text(": %s" % status)
        self.label.show()
        self.img.load_imlib(image)
        self.title.set_text(title)

        self.dialog.get_widget("title").set_text(title)
        self.run_tool = task

    def build_tree(self,list):
        """Populates a GtkTree with each menu item assocated with a entry
        in the lists. The list must consist of a tuples with the following
        format:
        
        (task_to_call, category, report name, description, image, status)
        
        Items in the same category are grouped under the same submen. The
        task_to_call is bound to the 'select' callback of the menu entry."""
        
        # build the tree items and group together based on the category name
        item_hash = {}
        for report in list:
            t = (report[2],report[0],report[3],report[4],report[5])
            if item_hash.has_key(report[1]):
                item_hash[report[1]].append(t)
            else:
                item_hash[report[1]] = [t]

        # add a submenu for each category, and populate it with the
        # GtkTreeItems that are associated with it.
        key_list = item_hash.keys()
        key_list.sort()
        prev = None
        for key in key_list:
            data = item_hash[key]
            node = self.tree.insert_node(None,prev,[key],is_leaf=0,expanded=1)
            self.tree.node_set_row_data(node,0)
            next = None
            data.sort()
            data.reverse()
            for item in data:
                next = self.tree.insert_node(node,next,[item[0]],is_leaf=1,expanded=1)
                self.tree.node_set_row_data(next,item)

#-------------------------------------------------------------------------
#
# ReportPlugins interface class
#
#-------------------------------------------------------------------------
class ReportPlugins(PluginDialog):
    """Displays the dialog box that allows the user to select the
    report that is desired."""

    def __init__(self,db,active):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""
        PluginDialog.__init__(self,db,active,_reports,_("Report Selection"))

#-------------------------------------------------------------------------
#
# ToolPlugins interface class
#
#-------------------------------------------------------------------------
class ToolPlugins(PluginDialog):
    """Displays the dialog box that allows the user to select the tool
    that is desired."""

    def __init__(self,db,active,update):
        """Display the dialog box, and build up the list of available
        reports. This is used to build the selection tree on the left
        hand side of the dailog box."""

        PluginDialog.__init__(self,db,active,_tools,_("Tool Selection"))
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
        
        self.glade = libglade.GladeXML(const.pluginsFile,"plugstat")
        self.top = self.glade.get_widget("plugstat")
        window = self.glade.get_widget("text")

        info = cStringIO.StringIO()
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
        window.show_string(info.read())
        self.top.run_and_close()
        
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
        except MissingLibraries,msg:
            _expect.append((file,msg))
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
                _success.append(a)
            except:
                _failmsg.append((file,sys.exc_info()))

#-------------------------------------------------------------------------
#
# Plugin registering
#
#-------------------------------------------------------------------------
def register_export(task, name):
    """Register an export filter, taking the task and name"""
    _exports.append((task, name))

def register_import(task, name):
    """Register an import filter, taking the task and name"""
    _imports.append((task, name))

def register_report(task, name,
                    category=_("Uncategorized"),
                    description=_unavailable,
                    xpm=None,
                    status=_("Unknown")):
    """Register a report with the plugin system"""
    
    if xpm == None:
        xpm = no_image()
    _reports.append((task, category, name, description, xpm, status))

def register_tool(task, name,
                  category=_("Uncategorized"),
                  description=_unavailable,
                  xpm=None,
                  status=_("Unknown")):
    """Register a tool with the plugin system"""
    if xpm == None:
        xpm = no_image()
    _tools.append((task, category, name, description, xpm, status))


def register_text_doc(name,classref, table, paper, style):
    """Register a text document generator"""
    for n in _textdoc:
        if n[0] == name:
            return
    _textdoc.append((name,classref,table,paper,style))

def register_draw_doc(name,classref):
    """Register a drawing document generator"""
    for n in _drawdoc:
        if n[0] == name:
            return
    _drawdoc.append((name,classref))

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
    report_menu = gtk.GtkMenu()
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
        entry = gtk.GtkMenuItem(key)
        entry.show()
        report_menu.append(entry)
        submenu = gtk.GtkMenu()
        submenu.show()
        entry.set_submenu(submenu)
        list = hash[key]
        list.sort()
        for name in list:
            subentry = gtk.GtkMenuItem(name[0])
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
# build_export_menu
#
#-------------------------------------------------------------------------
def build_export_menu(top_menu,callback):
    myMenu = gtk.GtkMenu()

    for report in _exports:
        item = gtk.GtkMenuItem(report[1])
        item.connect("activate", callback ,report[0])
        item.show()
        myMenu.append(item)
    top_menu.set_submenu(myMenu)

#-------------------------------------------------------------------------
#
# build_import_menu
#
#-------------------------------------------------------------------------
def build_import_menu(top_menu,callback):
    myMenu = gtk.GtkMenu()

    for report in _imports:
        item = gtk.GtkMenuItem(report[1])
        item.connect("activate", callback ,report[0])
        item.show()
        myMenu.append(item)
    top_menu.set_submenu(myMenu)

#-------------------------------------------------------------------------
#
# get_text_doc_menu
#
#-------------------------------------------------------------------------
def get_text_doc_menu(main_menu,tables,callback,obj=None):

    index = 0
    myMenu = gtk.GtkMenu()
    _textdoc.sort()
    for item in _textdoc:
        if tables and item[2] == 0:
            continue
        name = item[0]
        menuitem = gtk.GtkMenuItem(name)
        menuitem.set_data("name",item[1])
        menuitem.set_data("styles",item[4])
        menuitem.set_data("paper",item[3])
        menuitem.set_data("obj",obj)
        if callback:
            menuitem.connect("activate",callback)
        menuitem.show()
        myMenu.append(menuitem)
        if name == GrampsCfg.output_preference:
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
    myMenu = gtk.GtkMenu()
    for (name,classref) in _drawdoc:
        menuitem = gtk.GtkMenuItem(name)
        menuitem.set_data("name",classref)
        menuitem.set_data("obj",obj)
        if callback:
            menuitem.connect("activate",callback)
        menuitem.show()
        myMenu.append(menuitem)
        if name == GrampsCfg.goutput_preference:
            myMenu.set_active(index)
        if callback:
            callback(menuitem)
        index = index + 1
    main_menu.set_menu(myMenu)

#-------------------------------------------------------------------------
#
# no_image
#
#-------------------------------------------------------------------------
def no_image():
    """Returns XPM data for basic 48x48 icon"""
    return [
        "48 48 5 1",
        " 	c None",
        ".	c #999999",
        "+	c #FFFFCC",
        "@	c #000000",
        "#	c #CCCCCC",
        "                                                ",
        "                                                ",
        "                                                ",
        "                                                ",
        "                                                ",
        "                                                ",
        "                                  ..........    ",
        "                                  .++++++++.    ",
        "                                  .++++++++.    ",
        "                               @@@.++++++++.    ",
        "                               @##.++++++++.    ",
        "                               @# .++++++++.    ",
        "                  ..........   @# ..........    ",
        "                  .++++++++.   @#               ",
        "                  .++++++++.   @#               ",
        "               @@@.++++++++.@@@@#               ",
        "               @##.++++++++.###@# ..........    ",
        "               @# .++++++++.   @# .++++++++.    ",
        "               @# ..........   @# .++++++++.    ",
        "               @#              @@@.++++++++.    ",
        "               @#               ##.++++++++.    ",
        "               @#                 .++++++++.    ",
        "  ..........   @#                 ..........    ",
        "  .++++++++.   @#                               ",
        "  .++++++++.   @#                               ",
        "  .++++++++.@@@@#                               ",
        "  .++++++++.###@#                               ",
        "  .++++++++.   @#                 ..........    ",
        "  ..........   @#                 .++++++++.    ",
        "               @#                 .++++++++.    ",
        "               @#              @@@.++++++++.    ",
        "               @#              @##.++++++++.    ",
        "               @# ..........   @# .++++++++.    ",
        "               @# .++++++++.   @# ..........    ",
        "               @# .++++++++.   @#               ",
        "               @@@.++++++++.@@@@#               ",
        "                ##.++++++++.###@#               ",
        "                  .++++++++.   @# ..........    ",
        "                  ..........   @# .++++++++.    ",
        "                               @# .++++++++.    ",
        "                               @@@.++++++++.    ",
        "                                ##.++++++++.    ",
        "                                  .++++++++.    ",
        "                                  ..........    ",
        "                                                ",
        "                                                ",
        "                                                ",
        "                                                "]
