#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Brian G. Matherly
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

"""
The User class provides basic interaction with the user.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import sys

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen import user
from .utils import ProgressMeter
from .dialog import (WarningDialog, ErrorDialog, DBErrorDialog,
                     RunDatabaseRepair, InfoDialog, QuestionDialog2)

#-------------------------------------------------------------------------
#
# User class
#
#-------------------------------------------------------------------------
class User(user.UserBase):
    """
    This class provides a means to interact with the user via GTK.
    It implements the interface in :class:`.gen.user.UserBase`
    """
    def __init__(self, callback=None, error=None, parent=None,
                 uistate=None, dbstate=None): # TODO User API: gen==cli==gui
        user.UserBase.__init__(self, callback, error, uistate, dbstate)
        self._progress = None

        if parent:
            self.parent = parent
        elif uistate:
            self.parent = uistate.window
        else:
            self.parent = None

    def begin_progress(self, title, message, steps):
        """
        Start showing a progress indicator to the user.

        :param title: the title of the progress meter
        :type title: str
        :param message: the message associated with the progress meter
        :type message: str
        :param steps: the total number of steps for the progress meter.
                      a value of 0 indicates that the ending is unknown and the
                      meter should just show activity.
        :type steps: int
        :returns: none
        """
        self._progress = ProgressMeter(title, parent=self.parent)
        if steps > 0:
            self._progress.set_pass(message, steps, ProgressMeter.MODE_FRACTION)
        else:
            self._progress.set_pass(message, mode=ProgressMeter.MODE_ACTIVITY)

    def step_progress(self):
        """
        Advance the progress meter.
        """
        if self._progress:
            self._progress.step()

    def end_progress(self):
        """
        Stop showing the progress indicator to the user.
        """
        if self._progress:
            self._progress.close()
            self._progress = None

    def prompt(self, title, message, accept_label, reject_label, parent=None,
               default_label=None):
        """
        Prompt the user with a message to select an alternative.

        :param title: the title of the question, e.g.: "Undo history warning"
        :type title: str
        :param message: the message, e.g.: "Proceeding with the tool will erase
                        the undo history. If you think you may want to revert
                        running this tool, please stop here and make a backup
                        of the DB."
        :type question: str
        :param accept_label: what to call the positive choice, e.g.: "Proceed"
        :type accept_label: str
        :param reject_label: what to call the negative choice, e.g.: "Stop"
        :param default_label: the label of the default
        :type default_label: str or None
        :type reject_label: str
        :returns: the user's answer to the question
        :rtype: bool
        """
        dialog = QuestionDialog2(title, message,
                                 accept_label, reject_label,
                                 parent=parent)
        return dialog.run()

    def warn(self, title, warning=""):
        """
        Warn the user.

        :param title: the title of the warning
        :type title: str
        :param warning: the warning
        :type warning: str
        :returns: none
        """
        WarningDialog(title, warning, parent=self.parent)

    def notify_error(self, title, error=""):
        """
        Notify the user of an error.

        :param title: the title of the error
        :type title: str
        :param error: the error message
        :type error: str
        :returns: none
        """
        if self.error_function:
            self.error_function(title, error, parent=self.parent)
        else:
            ErrorDialog(title, error, parent=self.parent)

    def notify_db_error(self, error):
        """
        Notify the user of a DB error.

        :param error: the DB error message
        :type error: str
        :returns: none
        """
        DBErrorDialog(error, parent=self.parent)

    def notify_db_repair(self, error):
        """
        Notify the user their DB might need repair.

        :param error: the DB error message
        :type error: str
        :returns: none
        """
        RunDatabaseRepair(error, parent=self.parent)

    def info(self, msg1, infotext, parent=None, monospaced=False):
        """
        Calls the GUI InfoDialog
        """
        InfoDialog(msg1, infotext, parent, monospaced)
