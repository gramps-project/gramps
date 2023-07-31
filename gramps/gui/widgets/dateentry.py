#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013        Nick Hall
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

__all__ = ["DateEntry"]

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".widgets.dateentry")

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
from .monitoredwidgets import MonitoredDate
from .validatedmaskedentry import ValidatableMaskedEntry
from gramps.gen.lib.date import Date


# -------------------------------------------------------------------------
#
# DateEntry class
#
# -------------------------------------------------------------------------
class DateEntry(Gtk.Box):
    def __init__(self, uistate, track):
        Gtk.Box.__init__(self)
        self.entry = ValidatableMaskedEntry()
        self.entry.set_width_chars(13)
        self.pack_start(self.entry, True, True, 0)
        image = Gtk.Image()
        image.set_from_icon_name("gramps-date-edit", Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.set_image(image)
        button.set_relief(Gtk.ReliefStyle.NORMAL)
        self.pack_start(button, False, True, 0)
        self.date = Date()
        self.date_entry = MonitoredDate(self.entry, button, self.date, uistate, track)
        self.show_all()

    def get_text(self):
        return self.entry.get_text()

    def set_text(self, text):
        self.entry.set_text(text)
