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
# Standard Python modules
#
#-------------------------------------------------------------------------
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
import Errors

#-------------------------------------------------------------------------
#
# Global lists
#
#-------------------------------------------------------------------------
report_list = []
tool_list   = []
import_list = []
export_list = []
expect_list  = []
attempt_list = []
loaddir_list = []
textdoc_list = []
bookdoc_list = []
drawdoc_list = []
failmsg_list = []
bkitems_list = []
cl_list = []

_success_list = []

status_up = None
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
# load_plugins
#
#-------------------------------------------------------------------------
def load_plugins(direct):
    """Searches the specified directory, and attempts to load any python
    modules that it finds, adding name to the attempt_lists list. If the module
    successfully loads, it is added to the _success_list list. Each plugin is
    responsible for registering itself in the correct manner. No attempt
    is done in this routine to register the tasks."""
    
    global _success_list,attempt_list,loaddir_list,failmsg_list
    
    # if the directory does not exist, do nothing
    if not os.path.isdir(direct):
        return True

    # if the path has not already been loaded, save it in the loaddir_list
    # list for use on reloading

    if direct not in loaddir_list:
        loaddir_list.append(direct)

    # add the directory to the python search path
    sys.path.append(direct)

    pymod = re.compile(r"^(.*)\.py$")

    # loop through each file in the directory, looking for files that
    # have a .py extention, and attempt to load the file. If it succeeds,
    # add it to the _success_list list. If it fails, add it to the _failure
    # list
    
    for filename in os.listdir(direct):
        name = os.path.split(filename)
        match = pymod.match(name[1])
        if not match:
            continue
        attempt_list.append(filename)
        plugin = match.groups()[0]
        try: 
            a = __import__(plugin)
            _success_list.append(a)
        except Errors.PluginError, msg:
            expect_list.append((filename,str(msg)))
        except:
            failmsg_list.append((filename,sys.exc_info()))

    if len(expect_list)+len(failmsg_list):
        return False
    else:
        return True

#-------------------------------------------------------------------------
#
# reload_plugins
#
#-------------------------------------------------------------------------
def reload_plugins(obj=None,junk1=None,junk2=None,junk3=None):
    """Treated as a callback, causes all plugins to get reloaded. This is
    useful when writing and debugging a plugin"""
    
    pymod = re.compile(r"^(.*)\.py$")

    global _success_list,attempt_list,loaddir_list,failmsg_list

    oldfailmsg = failmsg_list[:]
    failmsg_list = []

    # attempt to reload all plugins that have succeeded in the past
    for plugin in _success_list:
        filename = os.path.basename(plugin.__file__)
        filename = filename.replace('pyc','py')
        filename = filename.replace('pyo','py')
        try: 
            reload(plugin)
        except:
            failmsg_list.append((filename,sys.exc_info()))
            
    # attempt to load the plugins that have failed in the past
    
    for (filename,message) in oldfailmsg:
        name = os.path.split(filename)
        match = pymod.match(name[1])
        if not match:
            continue
        attempt_list.append(filename)
        plugin = match.groups()[0]
        try: 
            # For some strange reason second importing of a failed plugin
            # results in success. Then reload reveals the actual error.
            # Looks like a bug in Python.
            a = __import__(plugin)
            reload(a)
            _success_list.append(a)
        except:
            failmsg_list.append((filename,sys.exc_info()))

    # attempt to load any new files found
    for directory in loaddir_list:
        for filename in os.listdir(directory):
            name = os.path.split(filename)
            match = pymod.match(name[1])
            if not match:
                continue
            if filename in attempt_list:
                continue
            attempt_list.append(filename)
            plugin = match.groups()[0]
            try: 
                a = __import__(plugin)
                if a not in _success_list:
                    _success_list.append(a)
            except:
                failmsg_list.append((filename,sys.exc_info()))

    global status_up
    if not len(failmsg_list):
        status_up.close(None)
        status_up = None

#-------------------------------------------------------------------------
#
# Plugin registering
#
#-------------------------------------------------------------------------
def register_export(exportData,title,description='',config=None,filename=''):
    """
    Register an export filter, taking the task, file filter, 
    and the list of patterns for the filename matching.
    """
    if description and filename:
        export_list.append((exportData,title,description,config,filename))

def register_import(task, ffilter, mime=None, native_format=0):
    """Register an import filter, taking the task and file filter"""
    if mime:
        import_list.append((task, ffilter, mime, native_format))


def register_tool(
    task,
    name,
    category=_("Uncategorized"),
    description=_unavailable,
    status=_("Unknown"),
    author_name=_("Unknown"),
    author_email=_("Unknown")
    ):
    """Register a tool with the plugin system"""
    del_index = -1
    for i in range(0,len(tool_list)):
        val = tool_list[i]
        if val[2] == name:
            del_index = i
    if del_index != -1:
        del tool_list[del_index]
    tool_list.append((task, category, name, description,
                      status, author_name, author_name))

#-------------------------------------------------------------------------
#
# Report registration
#
#-------------------------------------------------------------------------
def register_report(
    name,
    category,
    report_class,
    options_class,
    modes,
    translated_name,
    status=_("Unknown"),
    description=_unavailable,
    author_name=_("Unknown"),
    author_email=_("Unknown")
    ):
    """
    Registers report for all possible flavors.

    This function should be used to register report as a stand-alone,    book item, or command-line flavor in any combination of those.
    The low-level functions (starting with '_') should not be used
    on their own. Instead, this function will call them as needed.
    """

    import Report
    (junk,standalone_task) = divmod(modes,2**Report.MODE_GUI)
    if standalone_task:
        _register_standalone(report_class,options_class,translated_name,
                        name,category,description,
                        status,author_name,author_email)

    (junk,book_item_task) = divmod(modes-standalone_task,2**Report.MODE_BKI)
    if book_item_task:
        book_item_category = const.book_categories[category]
        register_book_item(translated_name,book_item_category,
                    report_class,options_class,name)

    (junk,command_line_task) = divmod(modes-standalone_task-book_item_task,
                                        2**Report.MODE_CLI)
    if command_line_task:
        _register_cl_report(name,category,report_class,options_class)

def _register_standalone(report_class, options_class, translated_name, 
                    name, category,
                    description=_unavailable,
                    status=_("Unknown"),
                    author_name=_("Unknown"),
                    author_email=_("Unknown")
                    ):
    """Register a report with the plugin system"""

    import Report
    
    del_index = -1
    for i in range(0,len(report_list)):
        val = report_list[i]
        if val[2] == name:
            del_index = i
    if del_index != -1:
        del report_list[del_index]
    report_list.append((report_class, options_class, translated_name, 
            category, name, description, status, author_name, author_email))

def register_book_item(translated_name, category, report_class,
                        option_class, name):
    """Register a book item"""
    
    for n in bkitems_list:
        if n[0] == name:
            return
    bkitems_list.append((translated_name, category, report_class,
                         option_class, name))

def _register_cl_report(name,category,report_class,options_class):
    for n in cl_list:
        if n[0] == name:
            return
    cl_list.append((name,category,report_class,options_class))

#-------------------------------------------------------------------------
#
# Text document generator registration
#
#-------------------------------------------------------------------------
def register_text_doc(name,classref, table, paper, style, ext,
                      print_report_label=None,clname=''):
    """Register a text document generator"""
    for n in textdoc_list:
        if n[0] == name:
            return
    if not clname:
        clname = ext[1:]
    textdoc_list.append(
        (name, classref, table, paper, style,
         ext, print_report_label, clname))

#-------------------------------------------------------------------------
#
# Book document generator registration
#
#-------------------------------------------------------------------------
def register_book_doc(name,classref, table, paper, style, ext, clname=''):
    """Register a text document generator"""
    for n in bookdoc_list:
        if n[0] == name:
            return
    if not clname:
        clname = ext[1:]
    bookdoc_list.append((name,classref,table,paper,style,ext,clname))

#-------------------------------------------------------------------------
#
# Drawing document generator registration
#
#-------------------------------------------------------------------------
def register_draw_doc(name,classref,paper,style, ext,
                      print_report_label=None,clname=''):
    """Register a drawing document generator"""
    for n in drawdoc_list:
        if n[0] == name:
            return
    if not clname:
        clname = ext[1:]
    drawdoc_list.append((name, classref, paper,style, ext,
                         print_report_label, clname))

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
# Register the plugin reloading tool
#
#-------------------------------------------------------------------------
register_tool(
    reload_plugins,
    _("Reload plugins"),
    category=_("Debug"),
    description=_("Attempt to reload plugins. Note: This tool itself is not reloaded!"),
    )
