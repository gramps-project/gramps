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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#

from ListModel import ListModel, NOSORT
from gen.plug import Gramplet
from gen.ggettext import gettext as _
import gen.lib
import DateHandler
import datetime
import gtk
import Utils
import sys
import pyexiv2

# v0.1 has a different API to v0.2 and above
if hasattr(pyexiv2, 'version_info'):
    LesserVersion = False
else:
    # version_info attribute does not exist prior to v0.2.0
    LesserVersion = True

class MetadataViewer(Gramplet):
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
        titles = [(_('Key'), 1, 250),
                  (_('Value'), 2, 350)]
        self.model = ListModel(top, titles)
        return top
        
    def main(self):
        active_handle = self.get_active('Media')
        media = self.dbstate.db.get_object_from_handle(active_handle)

        self.model.clear()
        if media:
            self.display_exif_tags(media)
        else:
            self.set_has_data(False)

    def update_has_data(self):
        active_handle = self.get_active('Media')
        active = self.dbstate.db.get_object_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))

    def get_has_data(self, media):
        """
        Return True if the gramplet has data, else return False.
        """
        if media is None:
            return False

        full_path = Utils.media_path_full(self.dbstate.db, media.get_path())
        
        if LesserVersion: # prior to v0.2.0
            try:
                metadata = pyexiv2.Image(full_path)
            except IOError:
                return False
            metadata.readMetadata()
            if metadata.exifKeys():
                return True

        else: # v0.2.0 and above
            metadata = pyexiv2.ImageMetadata(full_path)
            try:
                metadata.read()
            except IOError:
                return False
            if metadata.exif_keys:
                return True

        return False

    def display_exif_tags(self, media):
        """
        Display the exif tags.
        """
        full_path = Utils.media_path_full(self.dbstate.db, media.get_path())
        
        if LesserVersion: # prior to v0.2.0
            try:
                metadata = pyexiv2.Image(full_path)
            except IOError:
                self.set_has_data(False)
                return
            metadata.readMetadata()
            for key in metadata.exifKeys():
                label = metadata.tagDetails(key)[0]
                if key in ("Exif.Image.DateTime",
                           "Exif.Photo.DateTimeOriginal",
                           "Exif.Photo.DateTimeDigitized"):
                    human_value = format_datetime(metadata[key])
                else:
                    human_value = metadata.interpretedExifValue(key)
                self.model.add((label, human_value))

        else: # v0.2.0 and above
            metadata = pyexiv2.ImageMetadata(full_path)
            try:
                metadata.read()
            except IOError:
                self.set_has_data(False)
                return
            for key in metadata.exif_keys:
                tag = metadata[key]
                if key in ("Exif.Image.DateTime",
                           "Exif.Photo.DateTimeOriginal",
                           "Exif.Photo.DateTimeDigitized"):
                    human_value = format_datetime(tag.value)
                else:
                    human_value = tag.human_value
                self.model.add((tag.label, human_value))
                
        self.set_has_data(self.model.count > 0)

def format_datetime(exif_dt):
    """
    Convert a python datetime object into a string for display, using the
    standard Gramps date format.
    """
    if type(exif_dt) != datetime.datetime:
        return ''
    date_part = gen.lib.Date()
    date_part.set_yr_mon_day(exif_dt.year, exif_dt.month, exif_dt.day)
    date_str = DateHandler.displayer.display(date_part)
    time_str = exif_dt.strftime('%H:%M:%S')
    return _('%(date)s %(time)s') % {'date': date_str, 'time': time_str}
