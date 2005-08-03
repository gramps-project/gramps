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

"Database Processing/Check and repair database"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
import cStringIO
from gettext import gettext as _

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
from QuestionDialog import OkDialog

#-------------------------------------------------------------------------
#
# runTool
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback,parent=None):

    try:
        if database.readonly:
            # TODO: split plugin in a check and repair part to support
            # checking of a read only database
            return

        total = database.get_number_of_people() + database.get_number_of_families() + \
                database.get_number_of_places() + database.get_number_of_sources() + \
                database.get_number_of_media_objects()

        progress = Utils.ProgressMeter(_('Rebuilding Secondary Indices'))
        progress.set_pass('',total)
        database.disable_signals()
        database.rebuild_secondary(progress.step)
        database.enable_signals()
        progress.close()
        OkDialog(_("Secondary indices rebuilt"),
                 _('All secondary indices have been rebuilt.'))
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from PluginMgr import register_tool

register_tool(
    runTool,
    _("Rebuild secondary indices"),
    category=_("Database Repair"),
    description=_("Rebuilds secondary indices")
    )
