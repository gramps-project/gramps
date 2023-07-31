#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Doug Blank <doug.blank@gmail.com>
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
An override to allow easy multiselections.
"""

from gi.repository import Gdk
from gi.repository import Gtk
from ..utils import no_match_primary_mask

# -------------------------------------------------------------------------
#
# MultiTreeView class
#
# -------------------------------------------------------------------------


# TODO GTK3: Is this not duplicate of the class in clipboard py ?? We should reuse pieces
class MultiTreeView(Gtk.TreeView):
    """
    TreeView that captures mouse events to make drag and drop work properly
    """

    def __init__(self):
        Gtk.TreeView.__init__(self)
        self.connect("button_press_event", self.on_button_press)
        self.connect("button_release_event", self.on_button_release)
        self.connect("drag-end", self.on_drag_end)
        self.connect("key_press_event", self.key_press_event)
        self.defer_select = False

    def key_press_event(self, widget, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Delete:
                model, paths = self.get_selection().get_selected_rows()
                # reverse, to delete from the end
                paths.sort(key=lambda x: -x[0])
                for path in paths:
                    try:
                        node = model.get_iter(path)
                    except:
                        node = None
                    if node:
                        model.remove(node)
                return True

    def on_button_press(self, widget, event):
        # Here we intercept mouse clicks on selected items so that we can
        # drag multiple items without the click selecting only one
        target = self.get_path_at_pos(int(event.x), int(event.y))
        if (
            target
            and event.type == Gdk.EventType.BUTTON_PRESS
            and no_match_primary_mask(event.get_state(), Gdk.ModifierType.SHIFT_MASK)
            and self.get_selection().path_is_selected(target[0])
        ):
            # disable selection
            self.get_selection().set_select_function(lambda *ignore: False, None)
            self.defer_select = target[0]

    def on_button_release(self, widget, event):
        # re-enable selection
        self.get_selection().set_select_function(lambda *ignore: True, None)

        target = self.get_path_at_pos(int(event.x), int(event.y))
        if (
            self.defer_select
            and target
            and self.defer_select == target[0]
            and not (event.x == 0 and event.y == 0)
        ):  # certain drag and drop
            self.set_cursor(target[0], target[1], False)

        self.defer_select = False

    def on_drag_end(self, widget, event):
        # re-enable selection
        self.get_selection().set_select_function(lambda *ignore: True, None)
        self.defer_select = False
