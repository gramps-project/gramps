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

from gen.plug import Gramplet
from gui.widgets import Photo
import Utils
import gtk

class MediaPreview(Gramplet):
    """
    Displays a preview of the media object.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = gtk.HBox()
        self.photo = Photo(190.0)
        self.top.pack_start(self.photo, fill=True, expand=False, padding=5)
        self.top.show_all()
        return self.top

    def db_changed(self):
        self.dbstate.db.connect('media-update', self.update)
        self.connect_signal('Media', self.update)
        self.update()

    def main(self):
        active_handle = self.get_active('Media')
        media = self.dbstate.db.get_object_from_handle(active_handle)
        self.top.hide()
        if media:
            self.load_image(media)
        else:
            self.photo.set_image(None)
        self.top.show()

    def load_image(self, media):
        """
        Load the primary image if it exists.
        """
        full_path = Utils.media_path_full(self.dbstate.db, media.get_path())
        mime_type = media.get_mime_type()
        if mime_type and mime_type.startswith("image"):
            self.photo.set_image(full_path)
        else:
            self.photo.set_image(None)
