# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
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

from gui.utils import open_file_with_default_application
from gen.plug import Gramplet
import Utils
import gtk

class Gallery(Gramplet):
    """
    Displays a gallery of media objects.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        tip = _('Double-click on a picture to view it in the default image '
                'viewer application.')
        self.set_tooltip(tip)
        self.image_list = []
        self.top = gtk.HBox(False, 3)
        return self.top
        
    def clear_images(self):
        """
        Remove all images from the Gramplet.
        """
        for image in self.image_list:
            self.top.remove(image)
        self.image_list = []

    def load_images(self, obj):
        """
        Load the primary image into the main form if it exists.
        """
        media_list = obj.get_media_list()
        for photo in media_list:
            object_handle = photo.get_reference_handle()
            obj = self.dbstate.db.get_object_from_handle(object_handle)
            full_path = Utils.media_path_full(self.dbstate.db, obj.get_path())
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                pb = self.get_pixbuf(full_path, photo.get_rectangle())
                eb = gtk.EventBox()
                eb.connect('button-press-event', self.display_image, full_path)
                image = gtk.Image()
                eb.add(image)
                self.image_list.append(eb)
                image.set_from_pixbuf(pb)
                self.top.pack_start(eb, expand=False, fill=False)
                self.top.show_all()

    def display_image(self, widget, event, path):
        """
        Display the image with the default application.
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            open_file_with_default_application(path)
        
    def get_pixbuf(self, path, rectangle=None):
        """
        Load, scale and display the person's main photo from the path.
        """
        try:
            i = gtk.gdk.pixbuf_new_from_file(path)
            width = i.get_width()
            height = i.get_height()

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
                    i = i.subpixbuf(sub_x, sub_y, sub_width, sub_height)

            ratio = float(max(i.get_height(), i.get_width()))
            scale = float(180.0)/ratio
            x = int(scale*(i.get_width()))
            y = int(scale*(i.get_height()))
            i = i.scale_simple(x, y, gtk.gdk.INTERP_BILINEAR)
            return i
        except:
            return None

class PersonGallery(Gallery):
    """
    Displays a gallery of media objects for a person.
    """
    def db_changed(self):
        self.dbstate.db.connect('person-update', self.update)
        self.update()

    def active_changed(self, handle):
        self.update()

    def main(self):
        active_handle = self.get_active('Person')
        active = self.dbstate.db.get_person_from_handle(active_handle)
        
        self.clear_images()
        if active:
            self.load_images(active)

class EventGallery(Gallery):
    """
    Displays a gallery of media objects for an event.
    """
    def db_changed(self):
        self.dbstate.db.connect('event-update', self.update)
        self.connect_signal('Event', self.update)
        self.update()

    def main(self):
        active_handle = self.get_active('Event')
        active = self.dbstate.db.get_event_from_handle(active_handle)
        
        self.clear_images()
        if active:
            self.load_images(active)

class PlaceGallery(Gallery):
    """
    Displays a gallery of media objects for a place.
    """
    def db_changed(self):
        self.dbstate.db.connect('place-update', self.update)
        self.connect_signal('Place', self.update)
        self.update()

    def main(self):
        active_handle = self.get_active('Place')
        active = self.dbstate.db.get_place_from_handle(active_handle)
        
        self.clear_images()
        if active:
            self.load_images(active)

class SourceGallery(Gallery):
    """
    Displays a gallery of media objects for a source.
    """
    def db_changed(self):
        self.dbstate.db.connect('event-update', self.update)
        self.connect_signal('Source', self.update)
        self.update()

    def main(self):
        active_handle = self.get_active('Source')
        active = self.dbstate.db.get_source_from_handle(active_handle)
        
        self.clear_images()
        if active:
            self.load_images(active)

