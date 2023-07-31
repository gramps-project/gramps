# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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
# Gtk
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.widgets import Photo
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gen.utils.file import media_path_full


class Gallery(Gramplet):
    """
    Displays a gallery of media objects.
    """

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.image_list = []
        self.top = Gtk.Box(spacing=3)
        return self.top

    def set_orientation(self, orientation):
        """
        Called when the gramplet orientation changes.
        """
        self.top.set_orientation(orientation)

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
        count = 0
        for media_ref in media_list:
            media_handle = media_ref.get_reference_handle()
            media = self.dbstate.db.get_media_from_handle(media_handle)
            full_path = media_path_full(self.dbstate.db, media.get_path())
            mime_type = media.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                photo = Photo(self.uistate.screen_height() < 1000)
                photo.set_image(full_path, mime_type, media_ref.get_rectangle())
                photo.set_uistate(self.uistate, media_handle)
            else:
                photo = Photo(self.uistate.screen_height() < 1000)
                photo.set_pixbuf(
                    full_path,
                    get_thumbnail_image(
                        full_path, mime_type, media_ref.get_rectangle()
                    ),
                )
            self.image_list.append(photo)
            self.top.pack_start(photo, False, False, 0)
            count += 1
        self.top.show_all()
        self.set_has_data(count > 0)

    def get_has_data(self, obj):
        """
        Return True if the gramplet has data, else return False.
        """
        if obj is None:
            return False
        media_list = obj.get_media_list()
        for media_ref in media_list:
            media_handle = media_ref.get_reference_handle()
            media = self.dbstate.db.get_media_from_handle(media_handle)
            mime_type = media.get_mime_type()
            # bug 7390 : tab is not highlighted if there are only media
            #           like pdf, open document, ...
            if mime_type:
                return True
        return False


class PersonGallery(Gallery):
    """
    Displays a gallery of media objects for a person.
    """

    def db_changed(self):
        self.connect(self.dbstate.db, "person-update", self.update)

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active("Person")
        if active_handle:
            active = self.dbstate.db.get_person_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.clear_images()
        active_handle = self.get_active("Person")
        if active_handle:
            active = self.dbstate.db.get_person_from_handle(active_handle)
            if active:
                self.load_images(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)


class FamilyGallery(Gallery):
    """
    Displays a gallery of media objects for a family.
    """

    def db_changed(self):
        self.connect(self.dbstate.db, "family-update", self.update)
        self.connect_signal("Family", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Family")
        if active_handle:
            active = self.dbstate.db.get_family_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.clear_images()
        active_handle = self.get_active("Family")
        if active_handle:
            active = self.dbstate.db.get_family_from_handle(active_handle)
            if active:
                self.load_images(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)


class EventGallery(Gallery):
    """
    Displays a gallery of media objects for an event.
    """

    def db_changed(self):
        self.connect(self.dbstate.db, "event-update", self.update)
        self.connect_signal("Event", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Event")
        if active_handle:
            active = self.dbstate.db.get_event_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.clear_images()
        active_handle = self.get_active("Event")
        if active_handle:
            active = self.dbstate.db.get_event_from_handle(active_handle)
            if active:
                self.load_images(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)


class PlaceGallery(Gallery):
    """
    Displays a gallery of media objects for a place.
    """

    def db_changed(self):
        self.connect(self.dbstate.db, "place-update", self.update)
        self.connect_signal("Place", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Place")
        if active_handle:
            active = self.dbstate.db.get_place_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.clear_images()
        active_handle = self.get_active("Place")
        if active_handle:
            active = self.dbstate.db.get_place_from_handle(active_handle)
            if active:
                self.load_images(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)


class SourceGallery(Gallery):
    """
    Displays a gallery of media objects for a source.
    """

    def db_changed(self):
        self.connect(self.dbstate.db, "event-update", self.update)
        self.connect_signal("Source", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Source")
        if active_handle:
            active = self.dbstate.db.get_source_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.clear_images()
        active_handle = self.get_active("Source")
        if active_handle:
            active = self.dbstate.db.get_source_from_handle(active_handle)
            if active:
                self.load_images(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)


class CitationGallery(Gallery):
    """
    Displays a gallery of media objects for a Citation.
    """

    def db_changed(self):
        self.connect(self.dbstate.db, "event-update", self.update)
        self.connect_signal("Citation", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Citation")
        if active_handle:
            active = self.dbstate.db.get_citation_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def main(self):
        self.clear_images()
        active_handle = self.get_active("Citation")
        if active_handle:
            active = self.dbstate.db.get_citation_from_handle(active_handle)
            if active:
                self.load_images(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)
