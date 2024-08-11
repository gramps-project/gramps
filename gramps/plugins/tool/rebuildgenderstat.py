#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012       Benny Malengier
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

"Rebuild gender stat values"

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging

log = logging.getLogger(".RebuildGenderStat")

# -------------------------------------------------------------------------
#
# gtk modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gui.plug import tool
from gramps.gui.dialog import OkDialog
from gramps.gen.updatecallback import UpdateCallback
from gramps.gen.lib import Name

# -------------------------------------------------------------------------
#
# runTool
#
# -------------------------------------------------------------------------

COLUMN_GENDER = 2
COLUMN_NAME = 3
COLUMN_ALTNAMES = 4


class RebuildGenderStat(tool.Tool, UpdateCallback):
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
            uistate.push_message(
                dbstate, _("Rebuilding gender statistics for name gender guessing...")
            )
        else:
            self.callback = None
            print("Rebuilding gender statistics for name gender guessing...")

        UpdateCallback.__init__(self, self.callback)
        self.set_total(self.db.get_number_of_people())
        self.rebuild_genderstats()
        self.reset()

        if uistate:
            uistate.set_busy_cursor(False)
            uistate.progress.hide()
            OkDialog(
                _("Gender statistics rebuilt"),
                _("Gender statistics for name gender guessing have been rebuilt."),
                parent=uistate.window,
            )
        else:
            print("Gender statistics for name gender guessing have been rebuilt.")
        self.db.enable_signals()

    def rebuild_genderstats(self):
        """
        Function to rebuild the gender stats
        """
        self.db.genderStats.clear_stats()
        with self.db.get_person_cursor() as cursor:
            # loop over database and store the sort field, and the handle, and
            # allow for a third iter
            for key, data in cursor:
                rawprimname = data[COLUMN_NAME]
                rawaltnames = data[COLUMN_ALTNAMES]
                primary_name = Name().unserialize(rawprimname).get_first_name()
                alternate_names = [
                    Name().unserialize(name).get_first_name() for name in rawaltnames
                ]
                self.db.genderStats.count_name(primary_name, data[COLUMN_GENDER])


# ------------------------------------------------------------------------
#
#
#
# ------------------------------------------------------------------------
class RebuildGenderStatOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
