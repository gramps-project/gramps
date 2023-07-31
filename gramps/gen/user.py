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

import sys
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager


class UserBase(metaclass=ABCMeta):
    """
    This class provides a means to interact with the user in an abstract way.
    This class should be overridden by each respective user interface to
    provide the appropriate interaction (eg. dialogs for GTK, prompts for CLI).
    """

    def __init__(self, callback=None, error=None, uistate=None, dbstate=None):
        self.callback_function = callback
        self.error_function = error
        self._fileout = sys.stderr  # redirected to mocks by unit tests
        self.uistate = uistate
        self.dbstate = dbstate

    @abstractmethod
    def begin_progress(self, title, message, steps):
        """
        Start showing a progress indicator to the user.

        Don't use this method directly, use progress instead.

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

    @abstractmethod
    def step_progress(self):
        """
        Advance the progress meter.

        Don't use this method directly, use progress instead.
        """

    def callback(self, percentage, text=None):
        """
        Display the precentage.
        """
        if self.callback_function:
            if text:
                self.callback_function(percentage, text)
            else:
                self.callback_function(percentage)
        else:
            self._default_callback(percentage, text)

    def _default_callback(self, percentage, text):
        if text is None:
            self._fileout.write("\r%02d%%" % percentage)
        else:
            self._fileout.write("\r%02d%% %s" % (percentage, text))

    @abstractmethod
    def end_progress(self):
        """
        Stop showing the progress indicator to the user.

        Don't use this method directly, use progress instead.
        """

    # Context-manager wrapper of the begin/step/end_progress above
    @contextmanager
    def progress(self, *args, **kwargs):
        """
        Preferred form of progress reporting.

        Parameters: same as for begin_progress.

        Usage example (see gramps/cli/test/user_test.py)::

            with self.user.progress("Foo", "Bar", 0) as step:
                for i in range(10):
                    step()

        Ensures end_progress will be called even if an exception was thrown.
        """
        self.begin_progress(*args, **kwargs)
        try:
            yield self.step_progress
        except:
            raise
        finally:
            self.end_progress()

    @abstractmethod
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
        :param message: the message, e.g.: "Proceeding with the tool will
            erase the undo history. If you think you may want to revert
            running this tool, please stop here and make a backup of the DB."
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

    @abstractmethod
    def warn(self, title, warning=""):
        """
        Warn the user.

        :param title: the title of the warning
        :type title: str
        :param warning: the warning
        :type warning: str
        :returns: none
        """

    @abstractmethod
    def notify_error(self, title, error=""):
        """
        Notify the user of an error.

        :param title: the title of the error
        :type title: str
        :param error: the error message
        :type error: str
        :returns: none
        """

    @abstractmethod
    def notify_db_error(self, error):
        """
        Notify the user of a DB error.

        :param error: the error message
        :type error: str
        :returns: none
        """

    @abstractmethod
    def notify_db_repair(self, error):
        """
        Notify the user their DB might need repair.

        :param error: the error message
        :type error: str
        :returns: none
        """

    @abstractmethod
    def info(self, msg1, infotext, parent=None, monospaced=False):
        """
        Displays information to the user
        """


class User(UserBase):
    """
    An implementation of the :class:`.gen.user.UserBase` class which supresses
    output and accepts prompts.  This is useful for unit tests.
    """

    def __init__(self, callback=None, error=None, uistate=None, dbstate=None):
        UserBase.__init__(self, callback=self.__cb)

    def __cb(self, percent, text=None):
        return

    def begin_progress(self, title, message, steps):
        pass

    def step_progress(self):
        pass

    def end_progress(self):
        pass

    def prompt(
        self,
        title,
        message,
        accept_label,
        reject_label,
        parent=None,
        default_label=None,
    ):
        return True

    def warn(self, title, warning=""):
        pass

    def notify_error(self, title, error=""):
        pass

    def notify_db_error(self, error):
        pass

    def notify_db_repair(self, error):
        pass

    def info(self, msg1, infotext, parent=None, monospaced=False):
        pass
