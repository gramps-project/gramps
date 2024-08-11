# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011       Nick Hall
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
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.utils.thumbnails import get_thumbnail_image, SIZE_NORMAL, SIZE_LARGE
from ..utils import is_right_click, open_file_with_default_application
from ..widgets.menuitem import add_menuitem
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Photo class
#
# -------------------------------------------------------------------------
class Photo(Gtk.EventBox):
    """
    Displays an image and allows it to be viewed in an external image viewer.
    """

    def __init__(self, use_small_size=False):
        Gtk.EventBox.__init__(self)
        self.full_path = None
        self.uistate = None
        self.handle = None
        self.photo = Gtk.Image()
        self.add(self.photo)
        self.connect("button-press-event", self.handle_button_press)
        tip = _(
            "Double-click on the picture to view it in the default image "
            "viewer application."
        )
        self.set_tooltip_text(tip)
        self.__size = SIZE_LARGE
        if use_small_size:
            self.__size = SIZE_NORMAL

    def set_image(self, full_path, mime_type=None, rectangle=None):
        """
        Set the image to be displayed.
        """
        self.full_path = full_path
        if full_path:
            pixbuf = get_thumbnail_image(full_path, mime_type, rectangle, self.__size)
            self.photo.set_from_pixbuf(pixbuf)
            self.photo.show()
        else:
            self.photo.hide()

    def handle_button_press(self, widget, event):
        """
        Display the image with the default external viewer.
        """
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            open_file_with_default_application(self.full_path, self.uistate)
            return True
        elif is_right_click(event):
            if self.handle and self.uistate:
                self.menu = Gtk.Menu()
                add_menuitem(
                    self.menu,
                    _("Make Active Media"),
                    widget,
                    lambda obj: self.uistate.set_active(self.handle, "Media"),
                )
                self.menu.popup_at_pointer(event)
                return True
        return False

    def set_uistate(self, uistate, handle):
        """
        Set uistate and media handle so that Photo can be handled by
        UI.
        """
        self.uistate = uistate
        self.handle = handle

    def set_pixbuf(self, full_path, pixbuf):
        """
        Set the image to be displayed from a pixbuf.
        """
        self.full_path = full_path
        if full_path:
            self.photo.set_from_pixbuf(pixbuf)
            self.photo.show()
        else:
            self.photo.hide()
