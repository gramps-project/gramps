#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

import logging

class RotateHandler(logging.Handler):
    """
  A handler class which buffers logging records in memory. A rotating
  buffer is used so that the last X records are always available.
    """
    def __init__(self, capacity):
        """
        Initialize the handler with the buffer size.
        """
        logging.Handler.__init__(self)

        self.set_capacity(capacity)


    def emit(self, record):
        """
        Add the record to the rotating buffer.

        """
        self._buffer[self._index] = record
        self._index = (self._index + 1 ) % self._capacity


    def get_buffer(self):
        """
        Return the buffer with the records in the correct order.
        """

        return [_f for _f in self._buffer[self._index:] + self._buffer[:self._index] if _f]

    def get_formatted_log(self, remove_tail_duplicate=None):
        """
        Return the log buffer after it has been formatted.

        Returns a list of strings.
        """

        return [self.format(record) for record in self._buffer[self._index:] + self._buffer[:self._index]
                if record is not None and record != remove_tail_duplicate]

    def set_capacity(self,capacity):
        """
        Set the number of log records that will be stored.
        """
        self._capacity = capacity
        self._index = 0
        self._buffer = self._capacity * [None]
