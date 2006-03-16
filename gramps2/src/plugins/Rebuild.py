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

"Database Processing/Check and repair database"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
import cStringIO
from TransUtils import sgettext as _

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
class Rebuild(Tool.Tool):
    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        Tool.Tool.__init__(self,db,person,options_class,name)

        if db.readonly:
            # TODO: split plugin in a check and repair part to support
            # checking of a read only database
            return

        db.disable_signals()
        if parent:
            progress = Utils.ProgressMeter(
                    _('Rebuilding Secondary Indices'))
            # Six indices to rebuild, and the first step is removing
            # old ones
            total = 7
            progress.set_pass('',total)
            db.rebuild_secondary(progress.step)
            progress.close()
            OkDialog(_("Secondary indices rebuilt"),
                     _('All secondary indices have been rebuilt.'))
        else:
            print "Rebuilding Secondary Indices..."
            db.rebuild_secondary(self.empty)
            print "All secondary indices have been rebuilt."
        db.enable_signals()

    def empty(self):
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class RebuildOptions(Tool.ToolOptions):
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
    name = 'rebuild',
    category = Tool.TOOL_DBFIX,
    tool_class = Rebuild,
    options_class = RebuildOptions,
    modes = Tool.MODE_GUI | Tool.MODE_CLI,
    translated_name = _("Rebuild secondary indices"),
    status=(_("Stable")),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description=_("Rebuilds secondary indices")
    )
