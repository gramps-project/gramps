#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Brian Matherly
# Copyright (C) 2008       Gary Burton
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
#
from _GuiOptions import GuiMenuOptions, make_gui_option
from _Options import Options, OptionListCollection, OptionList, OptionHandler

import _Tool as Tool
from _PluginDialogs import ReportPluginDialog, ToolPluginDialog
import _PluginWindows as PluginWindows

# This needs to go above Tool and MenuOption as it needs both
class MenuToolOptions(GuiMenuOptions,Tool.ToolOptions):
    """
    The MenuToolOptions class implements the ToolOptions
    functionality in a generic way so that the user does not need to
    be concerned with the graphical representation of the options.
    
    The user should inherit the MenuToolOptions class and override the
    add_menu_options function. The user can add options to the menu
    and the MenuToolOptions class will worry about setting up the GUI.
    """
    def __init__(self, name, person_id=None, dbstate=None):
        Tool.ToolOptions.__init__(self, name, person_id)
        GuiMenuOptions.__init__(self)


