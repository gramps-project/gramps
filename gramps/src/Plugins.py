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
from gtk import *
from gnome.ui import *

import GTK
import gnome.config
import gnome.help
import libglade
import intl

_ = intl.gettext

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
import os
import sys
import string
import re

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
reports = []
imports = []
exports = []
tools = []

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class ReportPlugins:

    def __init__(self,db,active):
        self.db = db
        self.active = active
        
        self.plugins_dialog = libglade.GladeXML(const.pluginsFile,"report")
        self.plugins_dialog.signal_autoconnect({
            "on_report_apply_clicked" : on_report_apply_clicked,
            "on_report_ok_clicked" : on_report_ok_clicked,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        top = self.plugins_dialog.get_widget("report")
        top.set_data("o",self)
        tree = self.plugins_dialog.get_widget("tree1")
        self.run_tool = None

        item_hash = {}
        for report in reports:
            info = string.split(report.__doc__,"/")
            if len(info) == 1:
                category = "Uncategorized"
                name = info[0]
            else:
                category = info[0]
                name = info[1]
            item = GtkTreeItem(name)
            item.set_data("o",self)
            item.set_data("c",report.report)
            if "get_description" in report.__dict__.keys():
                item.set_data("d",report.get_description)
            else:
                item.set_data("d",no_description)
            if "get_xpm_image" in report.__dict__.keys():
                item.set_data("i",report.get_xpm_image)
            else:
                item.set_data("i",no_image)
            item.set_data("t",report.__doc__)
            item.connect("select",on_report_node_selected)
            if item_hash.has_key(category):
                item_hash[category].append(item)
            else:
                item_hash[category] = [item]

        key_list = item_hash.keys()
        key_list.sort()
        for key in key_list:
            top_item = GtkTreeItem(key)
            top_item.show()
            tree.append(top_item)
            subtree = GtkTree()
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
class ToolPlugins:
    def __init__(self,db,active,update):
        self.db = db
        self.active = active
        self.update = update
        
        self.plugins_dialog = libglade.GladeXML(const.pluginsFile,"pluginsel")
        self.plugins_dialog.signal_autoconnect({
            "on_apply_clicked" : on_apply_clicked,
            "on_ok_clicked" : on_ok_clicked,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        top = self.plugins_dialog.get_widget("pluginsel")
        top.set_data("o",self)
        tree = self.plugins_dialog.get_widget("tree")
        self.run_tool = None

        item_hash = {}
        for report in tools:
            info = string.split(report.__doc__,"/")
            item = GtkTreeItem(info[1])
            item.set_data("o",self)
            item.set_data("c",report.runTool)
            item.set_data("d",report.get_description)
            item.set_data("t",report.__doc__)
            item.connect("select",on_node_selected)
            if item_hash.has_key(info[0]):
                item_hash[info[0]].append(item)
            else:
                item_hash[info[0]] = [item]

        key_list = item_hash.keys()
        key_list.sort()
        for key in key_list:
            top_item = GtkTreeItem(key)
            top_item.show()
            tree.append(top_item)
            subtree = GtkTree()
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
def on_node_selected(obj):
    myobj = obj.get_data("o")
    doc = obj.get_data("d")
    title = string.split(obj.get_data("t"),"/")
    
    myobj.plugins_dialog.get_widget("description").set_text(doc())
    myobj.plugins_dialog.get_widget("pluginTitle").set_text(title[1])
    myobj.run_tool = obj.get_data("c")

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_report_node_selected(obj):
    myobj = obj.get_data("o")
    doc = obj.get_data("d")
    xpm_func = obj.get_data("i")
    
    title = string.split(obj.get_data("t"),"/")
    img = myobj.plugins_dialog.get_widget("image")
    
    myobj.plugins_dialog.get_widget("description").set_text(doc())

    i,m = create_pixmap_from_xpm_d(GtkWindow(),None,xpm_func())
    img.set(i,m)
    
    if len(title) == 1:
        myobj.plugins_dialog.get_widget("report_title").set_text(title[0])
    else:
        myobj.plugins_dialog.get_widget("report_title").set_text(title[1])
    myobj.run_tool = obj.get_data("c")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def by_doc(a,b):
    return cmp(a.__doc__,b.__doc__)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_apply_clicked(obj):
    myobj = obj.get_data("o")
    utils.destroy_passed_object(obj)
    if myobj.run_tool != None:
        myobj.run_tool(myobj.db,myobj.active,myobj.update)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_report_apply_clicked(obj):
    myobj = obj.get_data("o")
    utils.destroy_passed_object(obj)
    if myobj.run_tool != None:
        myobj.run_tool(myobj.db,myobj.active)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    on_apply_clicked(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_report_ok_clicked(obj):
    on_report_apply_clicked(obj)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def load_plugins(dir):
    pymod = re.compile(r"^(.*)\.py$")

    if not os.path.isdir(dir):
        return

    sys.path.append(dir)
    for file in os.listdir(dir):
        name = os.path.split(file)
        match = pymod.match(name[1])
        if not match:
            continue
        groups = match.groups()
        try: 
            plugin = __import__(groups[0])
        except:
            print groups[0]
            continue
        for task in plugin.__dict__.keys():
            if task == "report":
                reports.append(plugin)
            elif task == "writeData":
                exports.append(plugin)
            elif task == "runTool":
                tools.append(plugin)
            elif task == "readData":
                imports.append(plugin)

    tools.sort(by_doc)
    imports.sort(by_doc)
    exports.sort(by_doc)
    reports.sort(by_doc)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def export_menu(callback):
    myMenu = GtkMenu()

    for report in exports:
        item = GtkMenuItem(report.__doc__)
        item.show()
        item.connect("activate", callback ,report.writeData)
        myMenu.append(item)
    return myMenu

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def import_menu(callback):
    myMenu = GtkMenu()

    for report in imports:
        item = GtkMenuItem(report.__doc__)
        item.show()
        item.connect("activate", callback ,report.readData)
        myMenu.append(item)
    return myMenu

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def no_description():
    return _("No description was provided")

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
