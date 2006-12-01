#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# Written by Alex Roitman

"Rebuild reference map tables"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
import cStringIO
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".RebuildRefMap")

#-------------------------------------------------------------------------
#
# gtk modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
import Utils
import const
from PluginUtils import Tool, register_tool
from QuestionDialog import OkDialog

#-------------------------------------------------------------------------
#
# runTool
#
#-------------------------------------------------------------------------
class RebuildRefMap(Tool.Tool):

    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        
        Tool.Tool.__init__(self, dbstate, options_class, name)

        if self.db.readonly:
            return

        self.db.disable_signals()
        if uistate:
            self.db.reindex_reference_map()
            OkDialog(_("Reference maps rebuilt"),
                     _('All reference maps have been rebuilt.'))
        else:
            print "Rebuilding reference maps..."
            self.db.reindex_reference_map()
            print "All reference maps have been rebuilt."
        self.db.enable_signals()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class RebuildRefMapOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_tool(
    name = 'rebuild_refmap',
    category = Tool.TOOL_DBFIX,
    tool_class = RebuildRefMap,
    options_class = RebuildRefMapOptions,
    modes = Tool.MODE_GUI | Tool.MODE_CLI,
    translated_name = _("Rebuild reference map"),
    status=(_("Stable")),
    author_name = "Alex Roitman",
    author_email = "shura@gramps-project.org",
    description=_("Rebuilds reference map")
    )
