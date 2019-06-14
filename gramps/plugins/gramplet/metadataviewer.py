#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011      Nick Hall
# Copyright (C) 2011      Rob G. Healey <robhealey1@gmail.com>
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

"""
Image Metadata Gramplet
"""
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.plugins.lib.libmetadata import MetadataView
from gramps.gen.plug import Gramplet
from gramps.gen.utils.file import media_path_full

class MetadataViewer(Gramplet):
    """
    Displays the exif tags of an image.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def db_changed(self):
        self.connect_signal('Media', self.update)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.view = MetadataView()
        return self.view

    def main(self):
        active_handle = self.get_active('Media')
        if active_handle:
            media = self.dbstate.db.get_media_from_handle(active_handle)
            if media:
                full_path = media_path_full(self.dbstate.db, media.get_path())
                has_data = self.view.display_exif_tags(full_path)
                self.set_has_data(has_data)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)

    def update_has_data(self):
        active_handle = self.get_active('Media')
        if active_handle:
            active = self.dbstate.db.get_media_from_handle(active_handle)
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def get_has_data(self, media):
        """
        Return True if the gramplet has data, else return False.
        """
        if media is None:
            return False

        full_path = media_path_full(self.dbstate.db, media.get_path())
        return self.view.get_has_data(full_path)
