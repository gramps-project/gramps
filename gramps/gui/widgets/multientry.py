#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2022        Christopher Horn
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
Provide a basic multi-line text entry widget.
"""

__all__ = ["MultiLineEntry"]


# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject, Gtk


# -------------------------------------------------------------------------
#
# MultiLineEntry class
#
# -------------------------------------------------------------------------
class MultiLineEntry(Gtk.Box):
    """
    Provide a simple multi-line text entry widget with a frame that
    should look like a normal single line text entry widget.
    """

    __gtype_name__ = "MultiLineEntry"

    __gsignals__ = {
        "changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
    }

    def __init__(self, hexpand=True, vexpand=True, text=""):
        super().__init__(self)
        self.frame = Gtk.Frame(hexpand=hexpand, vexpand=vexpand)
        css = ".frame { border-style: solid; border-radius: 5px; }"
        self.provider = Gtk.CssProvider()
        self.provider.load_from_data(css.encode("utf-8"))
        context = self.frame.get_style_context()
        context.add_provider(self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")

        self.buffer = Gtk.TextBuffer()
        self.buffer.set_text(text)
        self.buffer.connect("changed", self.changed)
        self.view = Gtk.TextView(
            buffer=self.buffer, hexpand=True, vexpand=True
        )
        self.view.set_accepts_tab(False)
        self.view.set_left_margin(6)
        self.view.set_right_margin(6)
        self.view.set_top_margin(6)
        self.view.set_bottom_margin(6)
        self.view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.connect("focus-in-event", self.focus_outer_set)
        self.view.connect("focus-in-event", self.focus_inner_set)
        self.view.connect("focus-out-event", self.focus_unset)
        self.frame.add(self.view)
        self.add(self.frame)
        self.show()

    def changed(self, _cb_obj):
        """
        Emit change signal in case being monitored.
        """
        self.emit("changed")

    def set_editable(self, *args):
        """
        Set text view edit state.
        """
        self.view.set_editable(*args)

    def set_text(self, text):
        """
        Set the text.
        """
        self.buffer.set_text(text)

    def get_text(self):
        """
        Get the text.
        """
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, False)

    def focus_outer_set(self, *_dummy_args):
        """
        Pivot focus to the view.
        """
        self.view.grab_focus()

    def focus_inner_set(self, *_dummy_args):
        """
        Set border when in focus.
        """
        css = (
            ".frame { border-style: solid; border-width: 2px; "
            "border-radius: 5px; border-color: rgb(53,132,228); }"
        )
        self.provider.load_from_data(css.encode("utf-8"))
        self.frame.queue_draw()
        self.buffer.place_cursor(self.buffer.get_start_iter())
        self.set_can_focus(False)

    def focus_unset(self, *_dummy_args):
        """
        Reset border when releasing focus.
        """
        css = ".frame { border-style: solid; border-radius: 5px; }"
        self.provider.load_from_data(css.encode("utf-8"))
        self.frame.queue_draw()
        self.set_can_focus(True)
        return False
