#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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

# $Id: __init__.py 6086 2006-03-06 03:54:58Z dallingham $

"""
A set of basic utilities that everything in GRAMPS can depend upon.

The goal is to have this module not depend on any other gramps module.
That way, e.g. database classes can safely depend on that without
other GRAMPS baggage.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import time

#-------------------------------------------------------------------------
#
# Callback updater
#
#-------------------------------------------------------------------------
class UpdateCallback:
    """
    Basic class providing way of calling the callback to update
    things during lenghty operations.
    """

    def __init__(self,callback,interval=1):
        """
        @param callback: a function with one arg to execute every so often
        @type callback: function
        @param interval: number of seconds at most between the updates
        @type callback: int
        """
        if '__call__' in dir(callback): # callback is really callable
            self.update = self.update_real
            self.callback = callback

            self.count = 0
            self.oldval = 0
            self.oldtime = 0
            self.total = self.get_total()
            self.interval = interval
        else:
            self.update = self.update_empty

    def get_total(self):
        assert False, "Needs to be defined in the derived class"

    def update_empty(self):
        pass

    def update_real(self):
        self.count += 1
        newval = int(100.0*self.count/self.total)
        newtime = time.time()
        time_has_come = self.interval and (newtime-self.oldtime>self.interval)
        value_changed = newval!=self.oldval
        if value_changed or time_has_come:
            self.callback(newval)
            self.oldval = newval
            self.oldtime = newtime
