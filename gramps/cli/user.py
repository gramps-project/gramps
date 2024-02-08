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

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.const import URL_BUGHOME
from gramps.gen import user

# ------------------------------------------------------------------------
#
# Private Constants
#
# ------------------------------------------------------------------------
_SPINNER = ["|", "/", "-", "\\"]


# -------------------------------------------------------------------------
#
# User class
#
# -------------------------------------------------------------------------
class User(user.UserBase):
    """
    This class provides a means to interact with the user via CLI.
    It implements the interface in :class:`.gen.user.UserBase`
    """

    def __init__(
        self,
        callback=None,
        error=None,
        auto_accept=False,
        quiet=False,
        uistate=None,
        dbstate=None,
    ):
        """
        Init.

        :param error: If given, notify_error delegates to this callback
        :type error: function(title, error)
        """
        user.UserBase.__init__(self, callback, error, uistate, dbstate)
        self.steps = 0
        self.current_step = 0
        self._input = input

        def yes(*args, **kwargs):
            return True

        if auto_accept:
            self.prompt = yes
        if quiet:
            self.begin_progress = self.end_progress = self.step_progress = (
                self._default_callback
            ) = yes

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
        self.steps = steps
        self.current_step = 0
        self.display_progress()
        self._fileout.write(message)

    def step_progress(self):
        """
        Advance the progress meter.
        """
        self.current_step += 1
        self.display_progress()

    def end_progress(self):
        """
        Stop showing the progress indicator to the user.
        """
        self.display_progress(end=True)

    def display_progress(self, end=False):
        if end:
            self.steps = self.current_step = 1
        if self.steps == 0:
            self.current_step %= 4
            self._fileout.write("\r  %s  " % _SPINNER[self.current_step])
        else:
            percent = int((float(self.current_step) / self.steps) * 100)
            self._fileout.write("\r%3d%% " % percent)
        if end:
            self._fileout.write("\n")

    def prompt(
        self,
        title,
        message,
        accept_label,
        reject_label,
        parent=None,
        default_label=None,
    ):
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
        :type reject_label: str
        :param default_label: the label of the default
        :type default_label: str or None
        :returns: the user's answer to the question
        :rtype: bool
        """
        accept_text = accept_label.replace("_", "")
        reject_text = reject_label.replace("_", "")
        if default_label is None or default_label == accept_label:
            accept_text = "[%s]" % accept_text
            default = True
        else:
            reject_text = "[%s]" % reject_text
            default = False
        text = "{t}\n{m} ({y}/{n}): ".format(
            t=title, m=message, y=accept_text, n=reject_text
        )
        print(text, file=self._fileout)  # TODO: python 3.3 add flush=True
        try:
            reply = self._input()
        except EOFError:
            reply = ""
        ### Turn response into True/False:
        if reply == "":
            return default == accept_label
        elif reply == accept_label:
            return True
        else:
            return False

    def warn(self, title, warning=""):
        """
        Warn the user.

        :param title: the title of the warning
        :type title: str
        :param warning: the warning
        :type warning: str
        :returns: none
        """
        self._fileout.write("%s\n%s\n" % (title, warning))

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
            self.error_function(title, error)
        else:
            self._fileout.write("%s\n%s\n" % (title, error))

    def notify_db_error(self, error):
        """
        Notify the user of a DB error.

        :param error: the error message
        :type error: str
        :returns: none

        These exact strings are also in gui/dialog.py -- keep them in sync
        """
        self.notify_error(
            _("Low level database corruption detected"),
            _(
                "Gramps has detected a problem in the underlying "
                "database. This can sometimes be repaired from "
                "the Family Tree Manager. Select the database and "
                "click on the Repair button"
            )
            + "\n\n"
            + error,
        )

    def notify_db_repair(self, error):
        """
        Notify the user their DB might need repair.

        :param error: the error message
        :type error: str
        :returns: none

        These exact strings are also in gui/dialog.py -- keep them in sync
        """
        self.notify_error(
            _("Error detected in database"),
            _(
                "Gramps has detected an error in the database. This can "
                'usually be resolved by running the "Check and Repair Database" '
                "tool.\n\nIf this problem continues to exist after running this "
                "tool, please file a bug report at "
                "%(gramps_bugtracker_url)s\n\n"
            )
            % {"gramps_bugtracker_url": URL_BUGHOME}
            + error
            + "\n\n",
        )

    def info(self, msg1, infotext, parent=None, monospaced=False):
        """
        Displays information to the CLI
        """
        self._fileout.write("{} {}\n".format(msg1, infotext))
