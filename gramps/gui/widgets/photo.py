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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..thumbnails import get_thumbnail_image, SIZE_NORMAL, SIZE_LARGE
from ..utils import open_file_with_default_application
from gramps.gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# Photo class
#
#-------------------------------------------------------------------------
class Photo(Gtk.EventBox):
    """
    Displays an image and allows it to be viewed in an external image viewer.
    """
    def __init__(self, use_small_size=False):
        GObject.GObject.__init__(self)
        self.full_path = None
        self.photo = Gtk.Image()
        self.add(self.photo)
        self.connect('button-press-event', self.display_image)
        tip = _('Double-click on the picture to view it in the default image '
                'viewer application.')
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
            pixbuf = get_thumbnail_image(full_path, mime_type, rectangle,
                                         self.__size)
            self.photo.set_from_pixbuf(pixbuf)
            self.photo.show()
        else:
            self.photo.hide()

    def display_image(self, widget, event):
        """
        Display the image with the default external viewer.
        """
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            open_file_with_default_application(self.full_path)
