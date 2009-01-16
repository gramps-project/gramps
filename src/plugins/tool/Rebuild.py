#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

"""Tools/Database Processing/Rebuild Secondary Indices"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".Rebuild")

#-------------------------------------------------------------------------
#
# gtk modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from PluginUtils import Tool
from gen.plug import PluginManager
from QuestionDialog import OkDialog
from BasicUtils import UpdateCallback

#-------------------------------------------------------------------------
#
# runTool
#
#-------------------------------------------------------------------------
class Rebuild(Tool.Tool,UpdateCallback):

    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        
        Tool.Tool.__init__(self, dbstate, options_class, name)

        if self.db.readonly:
            return

        self.db.disable_signals()
        
        if uistate:
            self.callback = uistate.pulse_progressbar
            uistate.set_busy_cursor(1)
            uistate.progress.show()
            uistate.push_message(dbstate, _("Rebuilding secondary indices..."))
            
            UpdateCallback.__init__(self,self.callback)
            self.set_total(11)
            self.db.rebuild_secondary(self.update)
            self.reset()
            
            uistate.set_busy_cursor(0)
            uistate.progress.hide()
            OkDialog(_("Secondary indices rebuilt"),
                     _('All secondary indices have been rebuilt.'))
        else:
            print "Rebuilding Secondary Indices..."
            self.db.rebuild_secondary(self.update_empty)
            print "All secondary indices have been rebuilt."

        self.db.enable_signals()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class RebuildOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        Tool.ToolOptions.__init__(self, name,person_id)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_tool(
    name = 'rebuild',
    category = Tool.TOOL_DBFIX,
    tool_class = Rebuild,
    options_class = RebuildOptions,
    modes = PluginManager.TOOL_MODE_GUI | PluginManager.TOOL_MODE_CLI,
    translated_name = _("Rebuild Secondary Indices"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Rebuilds secondary indices")
    )
