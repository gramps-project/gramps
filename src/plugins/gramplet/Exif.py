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

from ListModel import ListModel, NOSORT
from gen.plug import Gramplet
from gen.ggettext import gettext as _
import gtk
import pyexiv2
import Utils

class Exif(Gramplet):
    """
    Displays the exif tags of an image.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)
        self.gui.WIDGET.show()
        self.connect_signal('Media', self.update)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        top = gtk.TreeView()
        titles = [(_('Section'), 0, 150),
                  (_('Key'), 1, 250),
                  (_('Value'), 2, 350)]
        self.model = ListModel(top, titles)
        return top
        
    def main(self):
        active_handle = self.get_active('Media')
        media = self.dbstate.db.get_object_from_handle(active_handle)

        self.model.clear()
        if media:
            self.display_exif_tags(media)

    def display_exif_tags(self, media):
        """
        Display the exif tags.
        """
        full_path = Utils.media_path_full(self.dbstate.db, media.get_path())
        metadata = pyexiv2.ImageMetadata(full_path)
        metadata.read()
        for key in metadata.exif_keys:
            tag = metadata[key]
            self.model.add((tag.section_name, tag.label, tag.human_value))
