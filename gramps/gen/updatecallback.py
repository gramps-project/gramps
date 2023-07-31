#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007 Donald N. Allingham
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
A set of basic utilities that everything in Gramps can depend upon.

The goal is to have this module not depend on any other gramps module.
That way, e.g. database classes can safely depend on that without
other Gramps baggage.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import time
from collections import abc
import logging

_LOG = logging.getLogger(".gen")


# -------------------------------------------------------------------------
#
# Callback updater
#
# -------------------------------------------------------------------------
class UpdateCallback:
    """
    Basic class providing way of calling the callback to update
    things during lengthy operations.
    """

    def __init__(self, callback, interval=1):
        """
        :param callback: a function with one arg to execute every so often
        :type callback: function
        :param interval: number of seconds at most between the updates
        :type interval: int
        """
        if isinstance(callback, abc.Callable):
            # callback is really callable
            self.update = self.update_real
            self.callback = callback
            self.interval = interval
        else:
            self.update = self.update_empty
        self.count = 0
        self.oldval = 0
        self.oldtime = 0
        self.text = ""
        self.total = 1

    def reset(self, text=""):
        """
        Reset the count to zero.
        """
        self.count = 0
        self.oldval = -1
        self.oldtime = 0
        self.text = text

    def set_text(self, text):
        """
        Set the text.
        """
        self.text = text
        self.oldval = -1

    def set_total(self, total):
        """
        Set the total.
        """
        self.total = total
        if self.total == 0:
            _LOG.warning("UpdateCallback with total == 0 created")
            self.total = 1

    def update_empty(self, count=None):
        """
        Dummy update used when no callback is specified.
        """
        pass

    def update_real(self, count=None):
        """
        Called when the count is updated.
        """
        self.count += 1
        if count is None:
            count = self.count
        newval = int(100 * count / self.total)
        newtime = time.time()
        time_has_come = self.interval and (newtime - self.oldtime > self.interval)
        value_changed = newval != self.oldval
        if value_changed or time_has_come:
            if self.text:
                self.callback(newval, text=self.text)
            else:
                self.callback(newval)
            self.oldval = newval
            self.oldtime = newtime
