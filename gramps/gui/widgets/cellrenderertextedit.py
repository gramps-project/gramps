#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017      Paul Culley
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

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk


# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
class CellRendererTextEdit(Gtk.CellRendererText):
    """To be used where you normally use Gtk.CellRendererText and you want to
    avoid losing the text if the user clicks outside the cell (Like an 'OK'
    button."""

    __gtype_name__ = "CellRendererTextEdit"

    def __init__(self):
        Gtk.CellRendererText.__init__(self)

    def do_start_editing(
        self, event, treeview, path, background_area, cell_area, flags
    ):
        if not self.get_property("editable"):
            return
        entry = Gtk.Entry()
        entry.set_has_frame(False)
        xalign, yalign = self.get_alignment()
        entry.set_alignment(xalign)
        entry.set_width_chars(5)
        entry.set_text(self.get_property("text"))  # get original cell text
        entry.add_events(Gdk.EventMask.FOCUS_CHANGE_MASK)
        entry.connect("focus-out-event", self.focus_out, path)
        entry.connect("key-press-event", self._key_press)
        entry.show()
        return entry

    def focus_out(self, entry, event, path):
        self.emit("edited", path, entry.get_text())
        return False

    def _key_press(self, entry, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Escape:
                # get original cell text
                entry.set_text(self.get_property("text"))
        return False
