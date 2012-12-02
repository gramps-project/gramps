#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012        Nick Hall
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

# $Id$

__all__ = ["LocationEntry2"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.locationentry2")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
MIN_CHARACTERS = 3
MAX_ENTRIES = 20

#-------------------------------------------------------------------------
#
# LocationEntry2 class
#
#-------------------------------------------------------------------------
class LocationEntry2(Gtk.Entry):

    def __init__(self, dbstate):
        Gtk.Entry.__init__(self)
        self.dbstate = dbstate
        self.set_width_chars(5)
        self.connect('changed', self.changed)
        self.connect('focus-out-event', self.lost_focus)
        self.show()
        
        self.handle = None

        self.pwin = Gtk.Window(Gtk.WindowType.POPUP)
        self.vbox = Gtk.VBox()
        self.pwin.add(self.vbox)

    def get_handle(self):
        return self.handle

    def set_handle(handle):
        self.set_text(self.get_location_text(handle))

    def changed(self, widget):
        txt = self.get_text()
        if len(txt) >= MIN_CHARACTERS:
            loc_list = self.get_location_list(txt)
            if loc_list:
                self.build_menu(loc_list)
        else:
            self.pwin.hide()
            self.handle = None

    def lost_focus(self, widget, event):
        self.pwin.hide()

    def build_menu(self, loc_list):
        self.pwin.hide() # required to get correct allocation
        self.pwin.resize(1, 1)
        map(self.vbox.remove, self.vbox.get_children())
        count = 0
        for loc in loc_list:
            item = Gtk.Button(loc[1])
            item.set_alignment(0, 0.5)
            item.set_relief(Gtk.ReliefStyle.NONE)
            item.connect("clicked", self.item_selected, loc[0])
            item.show()
            self.vbox.pack_start(item, False, False, 0)
            count += 1
            if count >= MAX_ENTRIES:
                break
        self.pwin.show_all()

        unused, x_pos, y_pos = self.get_window().get_origin()
        x_pos += self.get_allocation().x
        y_pos += self.get_allocation().y
        y_pos += self.get_allocation().height
        screen = self.pwin.get_screen()
        width = self.pwin.get_allocation().width
        height = self.pwin.get_allocation().height

        if x_pos + width > screen.get_width():
            x_pos = screen.get_width() - width

        if y_pos + height > screen.get_height():
            y_pos -= height + self.get_allocation().height

        self.pwin.move(x_pos, y_pos)
        
    def item_selected(self, menu_item, handle):
        self.set_text(menu_item.get_label())
        self.handle = handle
        self.pwin.hide()

    def get_location_list(self, txt):
        loc_list = []
        for handle in self.dbstate.db.find_location_from_name(txt):
            loc_list.append((handle, self.get_location_text(handle)))
        return loc_list

    def get_location_text(self, handle):
        loc = self.dbstate.db.get_location_from_handle(handle)
        lines = [loc.name]
        while loc.parent != str(None):
            loc = self.dbstate.db.get_location_from_handle(loc.parent)
            lines.append(loc.name)
        return ', '.join(lines)
