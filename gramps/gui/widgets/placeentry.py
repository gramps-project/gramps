#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015        Nick Hall
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

__all__ = ["PlaceEntry"]

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".widgets.placeentry")

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
from ..selectors import SelectorFactory


# -------------------------------------------------------------------------
#
# PlaceEntry class
#
# -------------------------------------------------------------------------
class PlaceEntry(Gtk.Box):
    def __init__(self, dbstate, uistate, track):
        Gtk.Box.__init__(self)
        self.dbstate = dbstate
        self.uistate = uistate
        self.track = track
        self.entry = Gtk.Entry()
        self.entry.set_width_chars(5)
        self.pack_start(self.entry, True, True, 0)
        image = Gtk.Image()
        image.set_from_icon_name("gtk-index", Gtk.IconSize.BUTTON)
        button = Gtk.Button()
        button.set_image(image)
        button.set_relief(Gtk.ReliefStyle.NORMAL)
        self.pack_start(button, False, True, 0)
        button.connect("clicked", self.on_clicked)
        self.show_all()

    def on_clicked(self, button):
        SelectPlace = SelectorFactory("Place")
        sel = SelectPlace(self.dbstate, self.uistate, self.track)
        place = sel.run()
        if place:
            self.set_text(place.gramps_id)

    def get_text(self):
        return self.entry.get_text()

    def set_text(self, text):
        self.entry.set_text(text)
