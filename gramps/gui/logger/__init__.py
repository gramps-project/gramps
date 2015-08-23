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

"""
This package implements some extensions to the standard Python logging module that
support a consistent logging and bug reporting framework for Gramps.

The package provides:

  GtkHandler - a log handler that will pop up a gtk dialog when a log message is
               sent to it. The dialog offers the user the chance to start
               ErrorReportAssistant to send a bug report.

  RotateHandler - a log handler that just keeps a rotating buffer of the last N
               log messages sent to it. This can be used with the GtkHandler to
               pass a history of log messages to the ErrorReportAssistant.

Usage:

   These handlers can be used in same way a all the other logger module handlers.

   Simple example:

        from gramps.gui.logger import GtkHandler, RotateHandler

        rh = RotateHandler(capacity=20)
        rh.setLevel(logging.DEBUG)

        gtkh = GtkHandler(rotate_handler=rh)
        gtkh.setLevel(logging.ERROR)

        l = logging.getLogger("GtkHandlerTest")
        l.setLevel(logging.DEBUG)

        l.addHandler(rh)
        l.addHandler(gtkh)

        log_message = "Debug message"
        try:
            wibble
        except:
            l.error(log_message,exc_info=True)

        Gtk.main()

"""

from ._gtkhandler import GtkHandler
from ._rotatehandler import RotateHandler
