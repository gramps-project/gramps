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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Gtk modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.widgets import Photo
from gramps.gen.utils.file import media_path_full

class MediaPreview(Gramplet):
    """
    Displays a preview of the media object.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = Gtk.Box()
        self.photo = Photo(self.uistate.screen_height() < 1000)
        self.top.pack_start(self.photo, fill=True, expand=False, padding=5)
        self.top.show_all()
        return self.top

    def db_changed(self):
        self.connect(self.dbstate.db, 'media-update', self.update)
        self.connect_signal('Media', self.update)

    def update_has_data(self):
        active_handle = self.get_active('Media')
        if active_handle:
            active_media = self.dbstate.db.get_media_from_handle(active_handle)
            self.set_has_data(active_media is not None)
        else:
            self.set_has_data(False)

    def main(self):
        active_handle = self.get_active('Media')
        if active_handle:
            media = self.dbstate.db.get_media_from_handle(active_handle)
            self.top.hide()
            if media:
                self.load_image(media)
                self.set_has_data(True)
            else:
                self.photo.set_image(None)
                self.set_has_data(False)
            self.top.show()
        else:
            self.photo.set_image(None)
            self.set_has_data(False)

    def load_image(self, media):
        """
        Load the primary image if it exists.
        """
        self.full_path = media_path_full(self.dbstate.db, media.get_path())
        mime_type = media.get_mime_type()
        self.photo.set_image(self.full_path, mime_type)
        self.photo.set_uistate(self.uistate, None)
