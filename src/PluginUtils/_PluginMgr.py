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
from ReportBase import MODE_GUI, MODE_BKI, book_categories
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
attempt_list = []
loaddir_list = []
textdoc_list = []
bookdoc_list = []
drawdoc_list = []
failmsg_list = []
bkitems_list = []
cl_list = []
cli_tool_list = []
success_list = []

mod2text = {}

#-------------------------------------------------------------------------
#
# Default relationship calculator
#
#-------------------------------------------------------------------------
import Relationship
_relcalc_class = Relationship.RelationshipCalculator

#-------------------------------------------------------------------------
#
# Constants
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
    successfully loads, it is added to the success_list list. Each plugin is
    responsible for registering itself in the correct manner. No attempt
    is done in this routine to register the tasks."""
    
    global success_list,attempt_list,loaddir_list,failmsg_list

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
    # add it to the success_list list. If it fails, add it to the _failure
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
            success_list.append((filename,a))
        except:
            failmsg_list.append((filename,sys.exc_info()))

    if len(failmsg_list):
        return False
    else:
        return True

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
        del_index = -1
        for i in range(0,len(export_list)):
            if export_list[i][1] == title:
                del_index = i
        if del_index != -1:
            del export_list[del_index]

        export_list.append((exportData,title,description,config,filename))
        mod2text[exportData.__module__] = description

def register_import(task, ffilter, mime=None, native_format=0, format_name=""):
    """Register an import filter, taking the task and file filter"""
    if mime:
        del_index = -1
        for i in range(0,len(import_list)):
            if import_list[i][2] == mime:
                del_index = i
        if del_index != -1:
            del import_list[del_index]

        import_list.append((task, ffilter, mime, native_format, format_name))
        mod2text[task.__module__] = format_name

#-------------------------------------------------------------------------
#
# Tool registration
#
#-------------------------------------------------------------------------
def register_tool(
    name,
    category,
    tool_class,
    options_class,
    modes,
    translated_name,
    status=_("Unknown"),
    description=_unavailable,
    author_name=_("Unknown"),
    author_email=_("Unknown"),
    unsupported=False
    ):
    """
    Register a tool with the plugin system.

    This function should be used to register tool in GUI and/or
    command-line mode. The low-level functions (starting with '_')
    should not be used on their own. Instead, this functino will call
    them as needed.
    """

    import _Tool

    (junk,gui_task) = divmod(modes,2**_Tool.MODE_GUI)
    if gui_task:
        _register_gui_tool(tool_class,options_class,translated_name,
                           name,category,description,
                           status,author_name,author_email,unsupported)

    (junk,cli_task) = divmod(modes-gui_task,2**_Tool.MODE_CLI)
    if cli_task:
        _register_cli_tool(name,category,tool_class,options_class,
                           translated_name,unsupported)

def _register_gui_tool(tool_class,options_class,translated_name,
                       name,category,
                       description=_unavailable,
                       status=_("Unknown"),
                       author_name=_("Unknown"),
                       author_email=_("Unknown"),
                       unsupported=False):
    del_index = -1
    for i in range(0,len(tool_list)):
        val = tool_list[i]
        if val[4] == name:
            del_index = i
    if del_index != -1:
        del tool_list[del_index]
    mod2text[tool_class.__module__] = description
    tool_list.append((tool_class,options_class,translated_name,
                      category,name,description,status,
                      author_name,author_email,unsupported))

def _register_cli_tool(name,category,tool_class,options_class,
                       translated_name,unsupported=False):
    del_index = -1
    for i in range(0,len(cli_tool_list)):
        val = cli_tool_list[i]
        if val[0] == name:
            del_index = i
    if del_index != -1:
        del cli_tool_list[del_index]
    cli_tool_list.append((name,category,tool_class,options_class,
                          translated_name,unsupported))

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
    author_email=_("Unknown"),
    unsupported=False
    ):
    """
    Registers report for all possible flavors.

    This function should be used to register report as a stand-alone,
    book item, or command-line flavor in any combination of those.
    The low-level functions (starting with '_') should not be used
    on their own. Instead, this function will call them as needed.
    """
    (junk,standalone_task) = divmod(modes,2**MODE_GUI)
    if standalone_task:
        _register_standalone(report_class,options_class,translated_name,
                        name,category,description,
                        status,author_name,author_email,unsupported)

    (junk,book_item_task) = divmod(modes-standalone_task,2**MODE_BKI)
    if book_item_task:
        book_item_category = book_categories[category]
        register_book_item(translated_name,book_item_category,
                    report_class,options_class,name,unsupported)

    (junk,command_line_task) = divmod(modes-standalone_task-book_item_task,
                                        2**MODE_CLI)
    if command_line_task:
        _register_cl_report(name,category,report_class,options_class,
                            translated_name,unsupported)

def _register_standalone(report_class, options_class, translated_name, 
                         name, category,
                         description=_unavailable,
                         status=_("Unknown"),
                         author_name=_("Unknown"),
                         author_email=_("Unknown"),
                         unsupported=False
                         ):
    """Register a report with the plugin system"""
    
    del_index = -1
    for i in range(0,len(report_list)):
        val = report_list[i]
        if val[4] == name:
            del_index = i
    if del_index != -1:
        del report_list[del_index]

    report_list.append((report_class, options_class, translated_name, 
                        category, name, description, status,
                        author_name, author_email, unsupported))
    mod2text[report_class.__module__] = description

def register_book_item(translated_name, category, report_class,
                        option_class, name, unsupported):
    """Register a book item"""
    
    del_index = -1
    for i in range(0,len(bkitems_list)):
        val = bkitems_list[i]
        if val[4] == name:
            del_index = i
    if del_index != -1:
        del bkitems_list[del_index]

    bkitems_list.append((translated_name, category, report_class,
                         option_class, name, unsupported))

def _register_cl_report(name,category,report_class,options_class,
                        translated_name,unsupported):
    del_index = -1
    for i in range(0,len(cl_list)):
        val = cl_list[i]
        if val[0] == name:
            del_index = i
    if del_index != -1:
        del cl_list[del_index]
    cl_list.append((name,category,report_class,options_class,
                    translated_name,unsupported))

#-------------------------------------------------------------------------
#
# Text document generator registration
#
#-------------------------------------------------------------------------
def register_text_doc(name,classref, table, paper, style, ext,
                      print_report_label=None,clname=''):
    """Register a text document generator"""
    del_index = -1
    for i in range(0,len(textdoc_list)):
        val = textdoc_list[i]
        if val[0] == name:
            del_index = i
    if del_index != -1:
        del textdoc_list[del_index]

    if not clname:
        clname = ext[1:]

    textdoc_list.append(
        (name, classref, table, paper, style,
         ext, print_report_label, clname))
    mod2text[classref.__module__] = name

#-------------------------------------------------------------------------
#
# Book document generator registration
#
#-------------------------------------------------------------------------
def register_book_doc(name,classref, table, paper, style, ext, clname=''):
    """Register a text document generator"""
    del_index = -1
    for i in range(0,len(bookdoc_list)):
        val = bookdoc_list[i]
        if val[0] == name:
            del_index = i
    if del_index != -1:
        del bookdoc_list[del_index]

    if not clname:
        clname = ext[1:]
    bookdoc_list.append((name,classref,table,paper,style,ext,None,clname))

#-------------------------------------------------------------------------
#
# Drawing document generator registration
#
#-------------------------------------------------------------------------
def register_draw_doc(name,classref,paper,style, ext,
                      print_report_label=None,clname=''):
    """Register a drawing document generator"""
    del_index = -1
    for i in range(0,len(drawdoc_list)):
        val = drawdoc_list[i]
        if val[0] == name:
            del_index = i
    if del_index != -1:
        del drawdoc_list[del_index]
    if not clname:
        clname = ext[1:]
    drawdoc_list.append((name, classref, paper,style, ext,
                         print_report_label, clname))
    mod2text[classref.__module__] = name

#-------------------------------------------------------------------------
#
# Remove plugins whose reloading failed from the already-registered lists
#
#-------------------------------------------------------------------------
def purge_failed(failed_list,export_list,import_list,tool_list,cli_tool_list,
                 report_list,bkitems_list,cl_list,textdoc_list,bookdoc_list,
                 drawdoc_list):
    failed_module_names = [
        os.path.splitext(os.path.basename(filename))[0]
        for filename,junk in failed_list
        ]

    export_list = [ item for item in export_list
                    if item[0].__module__ not in failed_module_names ]
    import_list = [ item for item in import_list
                    if item[0].__module__ not in failed_module_names ]
    tool_list = [ item for item in tool_list
                  if item[0].__module__ not in failed_module_names ]
    cli_tool_list = [ item for item in cli_tool_list
                      if item[2].__module__ not in failed_module_names ]
    report_list = [ item for item in report_list
                    if item[0].__module__ not in failed_module_names ]
    bkitems_list = [ item for item in bkitems_list
                     if item[2].__module__ not in failed_module_names ]
    cl_list = [ item for item in cl_list
                if item[2].__module__ not in failed_module_names ]
    textdoc_list = [ item for item in textdoc_list
                     if item[1].__module__ not in failed_module_names ]
    bookdoc_list = [ item for item in bookdoc_list
                     if item[1].__module__ not in failed_module_names ]
    drawdoc_list = [ item for item in drawdoc_list
                     if item[1].__module__ not in failed_module_names ]

    # For some funky reason this module's global variables
    # are not seen inside this function. But they are seen
    # from other modules, so we pass them back and forth.
    # Sucks, but I don't know why this happens :-(
    return (export_list,import_list,tool_list,cli_tool_list,
            report_list,bkitems_list,cl_list,textdoc_list,bookdoc_list,
            drawdoc_list)

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
