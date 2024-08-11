#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Nick Hall
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

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".widgets.statusbar")

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from . import WarnButton


# -------------------------------------------------------------------------
#
# Statusbar class
#
# -------------------------------------------------------------------------
class Statusbar(Gtk.Box):
    """
    A status bar
    """

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_spacing(4)
        self.set_border_width(2)

        self.__progress = Gtk.ProgressBar()
        self.__progress.set_size_request(100, -1)
        self.__progress.hide()

        self.__warnbtn = WarnButton()

        self.__version = Gtk.Button()
        self.__version.set_relief(Gtk.ReliefStyle.NONE)
        self.__version.get_style_context().add_class("destructive-action")

        self.__status = Gtk.Statusbar()
        self.__status.show()

        self.__filter = Gtk.Label()
        self.__filter.set_halign(Gtk.Align.END)
        self.__filter.show()

        self.pack_start(self.__warnbtn, False, True, 4)
        self.pack_start(self.__progress, False, True, 4)
        self.pack_start(self.__status, True, True, 4)
        self.pack_end(self.__filter, False, True, 4)
        self.pack_end(self.__version, False, True, 4)

    def get_warning_button(self):
        """Return the warning button widget."""
        return self.__warnbtn

    def get_progress_bar(self):
        """Return the progress bar widget."""
        return self.__progress

    def get_version_btn(self):
        """Return the version button widget."""
        return self.__version

    def get_context_id(self, context_description):
        """Return a new or existing context identifier."""
        return self.__status.get_context_id(context_description)

    def push(self, context_id, text):
        """Push message onto a statusbar's stack."""
        return self.__status.push(context_id, text)

    def pop(self, context_id):
        """Remove the top message from a statusbar's stack."""
        self.__status.pop(context_id)

    def remove(self, context_id, message_id):
        """Remove the message with the specified message_id."""
        self.__status.remove(context_id, message_id)

    def set_filter(self, text):
        """Set the filter status text."""
        self.__filter.set_text(text)

    def clear_filter(self):
        """Clear the filter status text."""
        self.__filter.set_text("")
