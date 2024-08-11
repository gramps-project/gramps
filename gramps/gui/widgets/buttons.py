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

__all__ = ["IconButton", "WarnButton", "SimpleButton", "PrivacyButton"]

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

import logging

_LOG = logging.getLogger(".widgets.buttons")

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk


# -------------------------------------------------------------------------
#
# IconButton class
#
# -------------------------------------------------------------------------
class IconButton(Gtk.Button):
    def __init__(self, func, handle, icon="gtk-edit", size=Gtk.IconSize.MENU):
        Gtk.Button.__init__(self)
        image = Gtk.Image()
        image.set_from_icon_name(icon, size)
        image.show()
        self.add(image)
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.show()

        if func:
            self.connect("button-press-event", func, handle)
            self.connect("key-press-event", func, handle)


##    def destroy(self):
##        """
##        Unset all elements that can prevent garbage collection
##        """
##        Gtk.Button.destroy(self)


# -------------------------------------------------------------------------
#
# WarnButton class
#
# -------------------------------------------------------------------------
class WarnButton(Gtk.Button):
    def __init__(self):
        Gtk.Button.__init__(self)

        image = Gtk.Image()
        image.set_from_icon_name("dialog-information", Gtk.IconSize.MENU)
        image.show()
        self.add(image)

        self.set_relief(Gtk.ReliefStyle.NONE)
        self.show()
        self.func = None
        self.hide()

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.func = None
    ##        Gtk.Button.destroy(self)

    def on_clicked(self, func):
        self.connect("button-press-event", self._button_press)
        self.func = func

    def _button_press(self, obj, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.func(obj)


# -------------------------------------------------------------------------
#
# SimpleButton class
#
# -------------------------------------------------------------------------
class SimpleButton(Gtk.Button):
    def __init__(self, image, func):
        Gtk.Button.__init__(self)
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.add(Gtk.Image.new_from_icon_name(image, Gtk.IconSize.BUTTON))
        self.connect("clicked", func)
        self.show()


##    def destroy(self):
##        """
##        Unset all elements that can prevent garbage collection
##        """
##        Gtk.Button.destroy(self)


# -------------------------------------------------------------------------
#
# PrivacyButton class
#
# -------------------------------------------------------------------------
class PrivacyButton:
    def __init__(self, button, obj, readonly=False):
        self.button = button
        self.button.connect("toggled", self._on_toggle)
        self.obj = obj
        self.set_active(obj.get_privacy())
        self.button.set_sensitive(not readonly)

    ##    def destroy(self):
    ##        """
    ##        Unset all elements that can prevent garbage collection
    ##        """
    ##        self.obj = None

    def set_sensitive(self, val):
        self.button.set_sensitive(val)

    def set_active(self, val):
        self.button.set_active(val)
        self._on_toggle(self.button)

    def get_active(self):
        return self.button.get_active()

    def _on_toggle(self, obj):
        child = obj.get_child()
        if child:
            obj.remove(child)
        image = Gtk.Image()
        if obj.get_active():
            image.set_from_icon_name("gramps-lock", Gtk.IconSize.MENU)
            obj.set_tooltip_text(_("Record is private"))
            self.obj.set_privacy(True)
        else:
            image.set_from_icon_name("gramps-unlock", Gtk.IconSize.MENU)
            obj.set_tooltip_text(_("Record is public"))
            self.obj.set_privacy(False)
        image.show()
        obj.add(image)
