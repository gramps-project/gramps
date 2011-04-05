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
from gui.utils import open_file_with_default_application
import ThumbNails
import const
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
        self.thumbnail = gtk.Image()
        ebox = gtk.EventBox()
        ebox.add(self.thumbnail)
        ebox.connect('button-press-event', self.display_image)
        ebox.set_tooltip_text(
            _('Double click image to view in an external viewer'))
        self.top.pack_start(ebox, fill=True, expand=False, padding=5)
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
            self.thumbnail.clear()
        self.top.show()

    def load_image(self, media):
        """
        Load the primary image if it exists.
        """
        self.full_path = Utils.media_path_full(self.dbstate.db,
                                               media.get_path())
        mime_type = media.get_mime_type()
        pixbuf = ThumbNails.get_thumbnail_image(self.full_path, mime_type)
        self.thumbnail.set_from_pixbuf(pixbuf)

    def display_image(self, widget, event):
        """
        Display the image with the default external viewer.
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            open_file_with_default_application(self.full_path)

