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

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
import gtk
import libglade

from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
import os
import sys
from re import compile

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
import const
import utils

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
_reports = []
_tools   = []
_imports = []
_exports = []
_success = []
_failed  = []
_attempt = []
_loaddir = []

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
DOCSTRING = "d"
IMAGE     = "i"
TASK      = "f"
TITLE     = "t"
STATUS    = "s"

pymod = compile(r"^(.*)\.py$")

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class ReportPlugins:

    def __init__(self,db,active):
        self.db = db
        self.active = active
        
        self.dialog = libglade.GladeXML(const.pluginsFile,"report")
        self.dialog.signal_autoconnect({
            "on_report_apply_clicked" : self.on_report_apply_clicked,
            "on_report_ok_clicked"    : self.on_report_apply_clicked,
            "destroy_passed_object"   : utils.destroy_passed_object
            })

        tree = self.dialog.get_widget("tree1")
        self.run_tool = None
        build_tree(tree,_reports,self.on_report_node_selected)

    def on_report_apply_clicked(self,obj):
        utils.destroy_passed_object(obj)
        if self.run_tool:
            self.run_tool(self.db,self.active)

    def on_report_node_selected(self,obj):
        doc = obj.get_data(DOCSTRING)
        xpm = obj.get_data(IMAGE)
        status = ": %s" % obj.get_data(STATUS)
        title = obj.get_data(TITLE)
        img = self.dialog.get_widget("image")
    
        self.dialog.get_widget("description").set_text(doc)
        self.dialog.get_widget("report_status").set_text(status)
        self.dialog.get_widget("report_label").show()

        i,m = gtk.create_pixmap_from_xpm_d(gtk.GtkWindow(),None,xpm)
        img.set(i,m)
    
        self.dialog.get_widget("report_title").set_text(title)
        self.run_tool = obj.get_data(TASK)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class ToolPlugins:
    def __init__(self,db,active,update):
        self.db = db
        self.active = active
        self.update = update
        
        self.dialog = libglade.GladeXML(const.pluginsFile,"pluginsel")
        self.dialog.signal_autoconnect({
            "on_apply_clicked"      : self.on_apply_clicked,
            "on_ok_clicked"         : self.on_apply_clicked,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        tree = self.dialog.get_widget("tree")
        self.run_tool = None
        build_tree(tree,_tools,self.on_node_selected)

    def on_apply_clicked(self,obj):
        utils.destroy_passed_object(obj)
        if self.run_tool:
            self.run_tool(self.db,self.active,self.update)

    def on_node_selected(self,obj):
        doc = obj.get_data(DOCSTRING)
        title = obj.get_data(TITLE)
    
        self.dialog.get_widget("description").set_text(doc)
        self.dialog.get_widget("pluginTitle").set_text(title)
        self.run_tool = obj.get_data(TASK)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def build_tree(tree,list,task):
    item_hash = {}
    for report in list:
        item = gtk.GtkTreeItem(report[2])
        item.connect("select",task)
        item.set_data(TASK,report[0])
        item.set_data(TITLE,report[2])
        item.set_data(DOCSTRING,report[3])
        item.set_data(IMAGE,report[4])
        item.set_data(STATUS,report[5])
        
        if item_hash.has_key(report[1]):
            item_hash[report[1]].append(item)
        else:
            item_hash[report[1]] = [item]

    key_list = item_hash.keys()
    key_list.sort()
    for key in key_list:
        top_item = gtk.GtkTreeItem(key)
        top_item.show()
        tree.append(top_item)
        subtree = gtk.GtkTree()
        subtree.show()
        top_item.set_subtree(subtree)
        subtree.show()
        for item in item_hash[key]:
            item.show()
            subtree.append(item)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def load_plugins(dir):
    global _success,_failed,_attempt,_loaddir
    
    if not os.path.isdir(dir):
        return

    if dir not in _loaddir:
	_loaddir.append(dir)

    sys.path.append(dir)
    for file in os.listdir(dir):
        name = os.path.split(file)
        match = pymod.match(name[1])
        if not match:
            continue
	_attempt.append(file)
        plugin = match.groups()[0]
        try: 
            a = __import__(plugin)
            _success.append(a)
        except:
            print _("Failed to load the module: %s") % plugin
            import traceback
            traceback.print_exc()
            _failed.append(plugin)

def reload_plugins(obj):
    for plugin in _success:
        try: 
            reload(plugin)
        except:
            print _("Failed to load the module: %s") % plugin
            import traceback
            traceback.print_exc()
            _failed.append(plugin)
    for plugin in _failed:
        try: 
            __import__(plugin)
        except:
            print _("Failed to load the module: %s") % plugin
            import traceback
            traceback.print_exc()
            _failed.append(plugin)

    for dir in _loaddir:
 	for file in os.listdir(dir):
            name = os.path.split(file)
	    match = pymod.match(name[1])
            if not match:
                continue
            _attempt.append(file)
            plugin = match.groups()[0]
            try: 
                a = __import__(plugin)
                _success.append(a)
            except:
                print _("Failed to load the module: %s") % plugin
                import traceback
                traceback.print_exc()
                _failed.append(plugin)

#-------------------------------------------------------------------------
#
# Plugin registering
#
#-------------------------------------------------------------------------
def register_export(task, name):
    _exports.append((task, name))

def register_import(task, name):
    _imports.append((task, name))

def register_report(task, name,
                    category=_("Uncategorized"),
                    description=_("No description was provided"),
                    xpm=None,
                    status=_("Unknown")):
    if xpm == None:
        xpm_data = no_image()
    elif type(xpm) == type([]):
        xpm_data = xpm
    else:
        xpm_data = xpm

    _reports.append((task, category, name, description, xpm_data, status))

def register_tool(task, name,
                  category=_("Uncategorized"),
                  description=_("No description was provided"),
                  xpm=None,
                  status=_("Unknown")):
    if xpm == None:
        xpm_data = no_image()
    elif type(xpm) == type([]):
        xpm_data = xpm
    else:
        xpm_data = xpm

    _tools.append((task, category, name, description, xpm_data, status))

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

def build_report_menu(top_menu,callback):
    build_menu(top_menu,_reports,callback)

def build_tools_menu(top_menu,callback):
    build_menu(top_menu,_tools,callback)

def build_export_menu(top_menu,callback):
    myMenu = gtk.GtkMenu()

    for report in _exports:
        item = gtk.GtkMenuItem(report[1])
        item.connect("activate", callback ,report[0])
        item.show()
        myMenu.append(item)
    top_menu.set_submenu(myMenu)

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
# 
#
#-------------------------------------------------------------------------
def no_image():
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
