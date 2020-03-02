#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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

# Written by Alex Roitman

"Rebuild reference map tables"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

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

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gui.plug import tool
from gramps.gui.dialog import OkDialog

#-------------------------------------------------------------------------
#
# runTool
#
#-------------------------------------------------------------------------
class RebuildRefMap(tool.Tool):

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate

        tool.Tool.__init__(self, dbstate, options_class, name)

        if self.db.readonly:
            return

        self.db.disable_signals()
        if uistate:
            self.callback = uistate.pulse_progressbar
            uistate.set_busy_cursor(True)
            uistate.progress.show()
            uistate.push_message(dbstate, _("Rebuilding reference maps..."))
        else:
            self.callback = None
            print(_("Rebuilding reference maps..."))

        self.db.reindex_reference_map(self.callback)

        if uistate:
            uistate.set_busy_cursor(False)
            uistate.progress.hide()
            OkDialog(_("Reference maps rebuilt"),
                     _('All reference maps have been rebuilt.'),
                     parent=uistate.window)
        else:
            print(_("All reference maps have been rebuilt."))
        self.db.enable_signals()

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class RebuildRefMapOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        tool.ToolOptions.__init__(self, name,person_id)
