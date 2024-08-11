#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Paul Franklin
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"ToolGeneration Framework"

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.const import TOOL_OPTIONS
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.plug._options import (
    Options,
    OptionHandler,
    OptionList,
    OptionListCollection,
)
from gramps.gen.plug import (
    TOOL_DEBUG,
    TOOL_ANAL,
    TOOL_DBPROC,
    TOOL_DBFIX,
    TOOL_REVCTL,
    TOOL_UTILS,
)

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

tool_categories = {
    TOOL_DEBUG: ("ToolDebug", _("Debug")),
    TOOL_ANAL: ("ToolAnExp", _("Analysis and Exploration")),
    TOOL_DBPROC: ("ToolProc", _("Family Tree Processing")),
    TOOL_DBFIX: ("ToolRep", _("Family Tree Repair")),
    TOOL_REVCTL: ("ToolRev", _("Revision Control")),
    TOOL_UTILS: ("ToolUtil", _("Utilities")),
}


# -------------------------------------------------------------------------
#
# Tool
#
# -------------------------------------------------------------------------
class Tool:
    """
    The Tool base class.  This is a base class for generating
    customized tools.  It cannot be used as is, but it can be easily
    sub-classed to create a functional tool.
    """

    def __init__(self, dbstate, options_class, name):
        from . import MenuToolOptions

        self.db = dbstate.db
        try:
            if issubclass(options_class, MenuToolOptions):
                # FIXME: pass in person_id
                self.options = options_class(name, None, dbstate)
            else:  # must be some kind of class or we get a TypeError
                self.options = options_class(name)
        except TypeError:
            self.options = options_class

        self.options.load_previous_values()
        if hasattr(options_class, "options_dict"):
            old_opts = options_class.saved_options_dict
            for key in options_class.options_dict:
                if options_class.options_dict[key] != old_opts[key]:
                    self.options.options_dict[key] = old_opts[key]

    def run_tool(self):
        pass


class BatchTool(Tool):
    """
    Same as Tool, except the warning is given about the potential
    loss of undo history.
    Should be used for tools using batch transactions.
    """

    def __init__(self, dbstate, user, options_class, name, parent=None):
        self._user = user
        if user.uistate:
            parent = user.uistate.window
        if not user.prompt(
            _("Undo history warning"),
            _(
                "Proceeding with this tool will erase the undo history "
                "for this session. In particular, you will not be able "
                "to revert the changes made by this tool or any changes "
                "made prior to it.\n\n"
                "If you think you may want to revert running this tool, "
                "please stop here and backup your database."
            ),
            _("_Proceed with the tool"),
            _("_Stop"),
            parent,
        ):
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

    def __init__(self, dbstate, uistate, options_class, name):
        if not uistate.get_active("Person"):
            # TODO: should we replace this with a callback?
            from ..dialog import ErrorDialog

            ErrorDialog(
                _("Active person has not been set"),
                _(
                    "You must select an active person for this "
                    "tool to work properly."
                ),
                parent=uistate.window,
            )
            self.fail = True
            return

        Tool.__init__(self, dbstate, options_class, name)
        self.fail = False


# ------------------------------------------------------------------------
#
# Command-line tool
#
# ------------------------------------------------------------------------
class CommandLineTool:
    """
    Provide a way to run tool from the command line.

    """

    def __init__(
        self, database, name, category, option_class, options_str_dict, noopt=False
    ):
        self.database = database
        self.category = category
        self.option_class = option_class(name)
        self.option_class.load_previous_values()
        self.show = options_str_dict.pop("show", None)
        self.options_str_dict = options_str_dict
        self.init_options(noopt)
        self.parse_option_str()
        self.show_options()

    def init_options(self, noopt):
        self.options_dict = {"id": ""}
        self.options_help = {
            "id": ["=ID", "Gramps ID of a central person."],
        }

        if noopt:
            return

        # Add tool-specific options
        for key in self.option_class.handler.options_dict:
            if key not in self.options_dict:
                self.options_dict[key] = self.option_class.handler.options_dict[key]

        # Add help for tool-specific options
        for key in self.option_class.options_help:
            if key not in self.options_help:
                self.options_help[key] = self.option_class.options_help[key]

    def parse_option_str(self):
        from gramps.cli.plug import _convert_str_to_match_type

        for opt in self.options_str_dict:
            if opt in self.options_dict:
                self.options_dict[opt] = _convert_str_to_match_type(
                    self.options_str_dict[opt], self.options_dict[opt]
                )
                self.option_class.handler.options_dict[opt] = self.options_dict[opt]
            else:
                print("Ignoring unknown option: %s" % opt)

        person_id = self.options_dict["id"]
        self.person = self.database.get_person_from_gramps_id(person_id)
        id_list = []

        for person in self.database.iter_people():
            id_list.append(
                "%s\t%s" % (person.get_gramps_id(), name_displayer.display(person))
            )
        self.options_help["id"].append(id_list)
        self.options_help["id"].append(False)

    def show_options(self):
        if not self.show:
            return
        elif self.show == "all":
            print("   Available options:")
            for key in self.options_dict:
                print("      %s" % key)
            print("   Use 'show=option' to see description and acceptable values")
        elif self.show in self.options_dict:
            print(
                "   %s%s\t%s"
                % (
                    self.show,
                    self.options_help[self.show][0],
                    self.options_help[self.show][1],
                )
            )
            print("   Available values are:")
            vals = self.options_help[self.show][2]
            if isinstance(vals, (list, tuple)):
                if self.options_help[self.show][3]:
                    for num, value in enumerate(vals):
                        print("      %d\t%s" % (num, value))
                else:
                    for val in vals:
                        print("      %s" % val)
            else:
                print("      %s" % self.options_help[self.show][2])

        else:
            self.show = None


# ------------------------------------------------------------------------
#
# Generic task functions for tools
#
# ------------------------------------------------------------------------
# Standard GUI tool generic task


def gui_tool(
    dbstate, user, tool_class, options_class, translated_name, name, category, callback
):
    """
    tool - task starts the report. The plugin system requires that the
    task be in the format of task that takes a database and a person as
    its arguments.
    """

    try:
        tool_class(
            dbstate=dbstate,
            user=user,
            options_class=options_class,
            name=name,
            callback=callback,
        )
    except WindowActiveError:
        pass
    except:
        log.error("Failed to start tool.", exc_info=True)


# Command-line generic task
def cli_tool(
    dbstate, name, category, tool_class, options_class, options_str_dict, user=None
):
    clt = CommandLineTool(dbstate.db, name, category, options_class, options_str_dict)
    clt.option_class.saved_options_dict = clt.options_dict

    # Exit here if show option was given
    if clt.show:
        return

    if user is None:
        from ...cli.user import User

        user = User()
    # run tool
    try:
        tool_class(
            dbstate=dbstate,
            user=user,
            options_class=clt.option_class,
            name=name,
            callback=None,
        )
    except:
        log.error("Failed to start tool.", exc_info=True)


# -------------------------------------------------------------------------
#
# Class handling options for plugins
#
# -------------------------------------------------------------------------
class ToolOptionHandler(OptionHandler):
    """
    Implements handling of the options for the plugins.
    """

    def __init__(self, module_name, options_dict, person_id=None):
        OptionHandler.__init__(self, module_name, options_dict, person_id)

    def init_subclass(self):
        self.collection_class = OptionListCollection
        self.list_class = OptionList
        self.filename = TOOL_OPTIONS


# ------------------------------------------------------------------------
#
# Tool Options class
#
# ------------------------------------------------------------------------
class ToolOptions(Options):
    """
    Defines options and provides handling interface.

    This is a base Options class for the tools. All tools, options
    classes should derive from it.
    """

    def __init__(self, name, person_id=None):
        """
        Initialize the class, performing usual house-keeping tasks.
        Subclasses MUST call this in their __init__() method.
        """
        self.name = name
        self.person_id = person_id
        self.options_dict = {}
        self.options_help = {}
        self.handler = None

    def load_previous_values(self):
        self.handler = ToolOptionHandler(self.name, self.options_dict, self.person_id)
