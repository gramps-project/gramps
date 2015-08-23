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

from ._errorview import ErrorView


class GtkHandler(logging.Handler):
    """
    A handler class which pops up a Gtk Window when a log message occurs.
    """

    def __init__(self,rotate_handler=None):
        """
        Initialize the handler with a optional rotate_logger instance.
        """
        logging.Handler.__init__(self)
        self._rotate_handler = rotate_handler

    def emit(self, record):
        """
        Add the record to the rotating buffer.
        """
        self._record = record
        ErrorView(error_detail=self, rotate_handler=self._rotate_handler)

    def get_formatted_log(self):
        return self.format(self._record)

    def get_record(self):
        return self._record
