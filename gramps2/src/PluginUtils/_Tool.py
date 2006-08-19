#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2006  Donald N. Allingham
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

"ToolGeneration Framework"

__author__ =  "Alex Roitman"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from types import ClassType, InstanceType
from gettext import gettext as _
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import Utils
from Filters import CustomFilters
import NameDisplay
import Errors
from _Options import *

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
# Modes for running tools
MODE_GUI = 1    # Standrt tool using GUI
MODE_CLI = 2    # Command line interface (CLI)

# Tool categories
TOOL_DEBUG  = -1
TOOL_ANAL   = 0
TOOL_DBPROC = 1
TOOL_DBFIX  = 2
TOOL_REVCTL = 3
TOOL_UTILS  = 4

tool_categories = {
    TOOL_DEBUG  : _("Debug"),
    TOOL_ANAL   : _("Analysis and Exploration"),
    TOOL_DBPROC : _("Database Processing"),
    TOOL_DBFIX  : _("Database Repair"),
    TOOL_REVCTL : _("Revision Control"),
    TOOL_UTILS  : _("Utilities"),
    }

#-------------------------------------------------------------------------
#
# Tool
#
#-------------------------------------------------------------------------
class Tool:
    """
    The Tool base class.  This is a base class for generating
    customized tools.  It cannot be used as is, but it can be easily
    sub-classed to create a functional tool.
    """

    def __init__(self, dbstate, options_class, name):
        self.db = dbstate.db
        self.person = dbstate.active
        if type(options_class) == ClassType:
            self.options = options_class(name)
        elif type(options_class) == InstanceType:
            self.options = options_class

    def run_tool(self):
        pass


class BatchTool(Tool):
    """
    Same as Tool, except the warning is displayed about the potential
    loss of undo history. Should be used for tools using batch transactions.

    """

    def __init__(self, dbstate, options_class, name):
        from QuestionDialog import QuestionDialog2
        warn_dialog = QuestionDialog2(
            _('Undo history warning'),
            _('Proceeding with this tool will erase the undo history '
              'for this session. In particular, you will not be able '
              'to revert the changes made by this tool or any changes '
              'made prior to it.\n\n'
              'If you think you may want to revert running this tool, '
              'please stop here and backup your database.'),
            _('_Proceed with the tool'), _('_Stop'))
        if not warn_dialog.run():
            self.fail = True
            return

        Tool.__init__(self, dbstate, options_class, name)
        self.fail = False


class ActivePersonTool(Tool):
    """
    Same as Tool , except the existence of the active person is checked
    and the tool is aborted if no active person exists. Should be used
    for tools that depend on active person.
    """

    def __init__(self, dbstate, options_class, name):
        
        if not dbstate.get_active_person():
            from QuestionDialog import ErrorDialog
            
            ErrorDialog(_('Active person has not been set'),
                        _('You must select an active person for this '
                          'tool to work properly.'))
            self.fail = True
            return

        Tool.__init__(self, dbstate, options_class, name)
        self.fail = False

#------------------------------------------------------------------------
#
# Command-line tool
#
#------------------------------------------------------------------------
class CommandLineTool:
    """
    Provides a way to run tool from the command line.
    
    """

    def __init__(self,database,name,category,option_class,options_str_dict,
                 noopt=False):
        self.database = database
        self.category = category
        self.option_class = option_class(name)
        self.show = options_str_dict.pop('show',None)
        self.options_str_dict = options_str_dict
        self.init_options(noopt)
        self.parse_option_str()
        self.show_options()

    def init_options(self,noopt):
        self.options_dict = {
            'id'        : ''
            }

        self.options_help = {
            'id'        : ["=ID","Gramps ID of a central person."],
            'filter'    : ["=num","Filter number."],
            }

        if noopt:
            return

        # Add tool-specific options
        for key in self.option_class.handler.options_dict.keys():
            if key not in self.options_dict.keys():
                self.options_dict[key] = self.option_class.handler.options_dict[key]

        # Add help for tool-specific options
        for key in self.option_class.options_help.keys():
            if key not in self.options_help.keys():
                self.options_help[key] = self.option_class.options_help[key]

    def parse_option_str(self):
        for opt in self.options_str_dict.keys():
            if opt in self.options_dict.keys():
                converter = Utils.get_type_converter(self.options_dict[opt])
                self.options_dict[opt] = converter(self.options_str_dict[opt])
                self.option_class.handler.options_dict[opt] = self.options_dict[opt]
            else:
                print "Ignoring unknown option: %s" % opt

        person_id = self.options_dict['id']
        self.person = self.database.get_person_from_gramps_id(person_id)
        id_list = []
        for person_handle in self.database.get_person_handles():
            person = self.database.get_person_from_handle(person_handle)
            id_list.append("%s\t%s" % (
                person.get_gramps_id(),
                NameDisplay.displayer.display(person)))
        self.options_help['id'].append(id_list)
        self.options_help['id'].append(False)

        if self.options_dict.has_key('filter'):
            filter_num = self.options_dict['filter']
            self.filters = self.option_class.get_report_filters(self.person)
            self.option_class.handler.set_filter_number(filter_num)
            
            filt_list = [ filt.get_name() for filt in self.filters ]
            cust_filt_list = [ filt2.get_name() for filt2 in 
                               CustomFilters.get_filters() ]
            filt_list.extend(cust_filt_list)
            self.options_help['filter'].append(filt_list)
            self.options_help['filter'].append(True)

    def show_options(self):
        if not self.show:
            return
        elif self.show == 'all':
            print "   Available options:"
            for key in self.options_dict.keys():
                print "      %s" % key
            print "   Use 'show=option' to see description and acceptable values"
        elif self.show in self.options_dict.keys():
            print '   %s%s\t%s' % (self.show,
                                    self.options_help[self.show][0],
                                    self.options_help[self.show][1])
            print "   Available values are:"
            vals = self.options_help[self.show][2]
            if type(vals) in [list,tuple]:
                if self.options_help[self.show][3]:
                    for num in range(len(vals)):
                        print "      %d\t%s" % (num,vals[num])
                else:
                    for val in vals:
                        print "      %s" % val
            else:
                print "      %s" % self.options_help[self.show][2]

        else:
            self.show = None

#------------------------------------------------------------------------
#
# Generic task functions for tools
#
#------------------------------------------------------------------------
# Standard GUI tool generic task

def gui_tool(dbstate, uistate, tool_class, options_class, translated_name,
             name, category, callback):
    """
    tool - task starts the report. The plugin system requires that the
    task be in the format of task that takes a database and a person as
    its arguments.
    """

    try:
        tool_class(dbstate, uistate, options_class, name, callback)
    except Errors.WindowActiveError:
        pass
    except:
        log.error("Failed to start tool.", exc_info=True)

# Command-line generic task
def cli_tool( database,name,category,tool_class,options_class,options_str_dict):
    
    clt = CommandLineTool(database,name,category,
                          options_class,options_str_dict)

    # Exit here if show option was given
    if clt.show:
        return

    # run tool
    try:
        tool_class(database,clt.person,clt.option_class,name)
    except:
        log.error("Failed to start tool.", exc_info=True)

#-------------------------------------------------------------------------
#
# Class handling options for plugins 
#
#-------------------------------------------------------------------------
class ToolOptionHandler(OptionHandler):
    """
    Implements handling of the options for the plugins.
    """
    def __init__(self,module_name,options_dict,person_id=None):
        OptionHandler.__init__(self,module_name,options_dict,person_id)

    def init_subclass(self):
        self.collection_class = OptionListCollection
        self.list_class = OptionList
        self.filename = const.tool_options

#------------------------------------------------------------------------
#
# Tool Options class
#
#------------------------------------------------------------------------
class ToolOptions(Options):

    """
    Defines options and provides handling interface.
    
    This is a base Options class for the tools. All tools' options
    classes should derive from it.
    """

    def __init__(self,name,person_id=None):
        """
        Initializes the class, performing usual house-keeping tasks.
        Subclasses MUST call this in their __init__() method.
        """
        self.set_new_options()
        self.enable_options()

        if self.enable_dict:
            self.options_dict.update(self.enable_dict)
        self.handler = ToolOptionHandler(name,self.options_dict,person_id)
