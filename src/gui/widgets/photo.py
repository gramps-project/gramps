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
import gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gui.utils import open_file_with_default_application
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# Photo class
#
#-------------------------------------------------------------------------
class Photo(gtk.EventBox):
    """
    Displays an image and allows it to be viewed in an external image viewer.
    """
    def __init__(self, size=100.0):
        gtk.EventBox.__init__(self)
        self.size = size
        self.full_path = None
        self.photo = gtk.Image()
        self.add(self.photo)
        self.connect('button-press-event', self.display_image)
        tip = _('Double-click on the picture to view it in the default image '
                'viewer application.')
        self.set_tooltip_text(tip)

    def set_image(self, full_path, rectangle=None):
        """
        Set the image to be displayed.
        """
        self.full_path = full_path
        if full_path:
            pb = self.get_pixbuf(full_path, rectangle, self.size)
            self.photo.set_from_pixbuf(pb)
            self.photo.show()
        else:
            self.photo.hide()

    def display_image(self, widget, event):
        """
        Display the image with the default external viewer.
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            open_file_with_default_application(self.full_path)

    def get_pixbuf(self, full_path, rectangle=None, size=100.0):
        """
        Load, scale and display the image from the path.
        """
        try:
            image = gtk.gdk.pixbuf_new_from_file(full_path)
        except:
            return None

        width = image.get_width()
        height = image.get_height()
        if rectangle is not None:
            upper_x = min(rectangle[0], rectangle[2])/100.
            lower_x = max(rectangle[0], rectangle[2])/100.
            upper_y = min(rectangle[1], rectangle[3])/100.
            lower_y = max(rectangle[1], rectangle[3])/100.
            sub_x = int(upper_x * width)
            sub_y = int(upper_y * height)
            sub_width = int((lower_x - upper_x) * width)
            sub_height = int((lower_y - upper_y) * height)
            if sub_width > 0 and sub_height > 0:
                image = image.subpixbuf(sub_x, sub_y, sub_width, sub_height)

        ratio = float(max(image.get_height(), image.get_width()))
        scale = float(size)/ratio
        x = int(scale*(image.get_width()))
        y = int(scale*(image.get_height()))
        image = image.scale_simple(x, y, gtk.gdk.INTERP_BILINEAR)
        return image
