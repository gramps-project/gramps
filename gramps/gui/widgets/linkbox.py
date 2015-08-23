#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

__all__ = ["LinkBox"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.linkbox")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# LinkBox class
#
#-------------------------------------------------------------------------
class LinkBox(Gtk.Box):

    def __init__(self, link, button):
        Gtk.Box.__init__(self)
        self.set_spacing(6)
        self.pack_start(link, False, True, 0)
        if button:
            self.pack_start(button, False, True, 0)
        self.show()
