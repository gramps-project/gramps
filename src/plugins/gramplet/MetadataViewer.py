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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#

from ListModel import ListModel
from gen.plug import Gramplet
from gen.ggettext import gettext as _
import gen.lib
import DateHandler
import datetime
import gtk
import Utils
import pyexiv2

# v0.1 has a different API to v0.2 and above
if hasattr(pyexiv2, 'version_info'):
    OLD_API = False
else:
    # version_info attribute does not exist prior to v0.2.0
    OLD_API = True

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
    time_str = _('%(hr)02d:%(min)02d:%(sec)02d') % {'hr': exif_dt.hour,
                                                    'min': exif_dt.minute,
                                                    'sec': exif_dt.second}
    return _('%(date)s %(time)s') % {'date': date_str, 'time': time_str}

def format_gps(tag_value):
    """
    Convert a (degrees, minutes, seconds) tuple into a string for display.
    """
    return "%d°%02d'%05.2f\"" % (tag_value[0], tag_value[1], tag_value[2])

IMAGE = _('Image')
CAMERA = _('Camera')
GPS = _('GPS')

TAGS = [(IMAGE, 'Exif.Image.ImageDescription', None, None), 
        (IMAGE, 'Exif.Image.Rating', None, None), 
        (IMAGE, 'Exif.Photo.DateTimeOriginal', None, format_datetime), 
        (IMAGE, 'Exif.Image.Artist', None, None), 
        (IMAGE, 'Exif.Image.Copyright', None, None), 
        (IMAGE, 'Exif.Photo.PixelXDimension', None, None), 
        (IMAGE, 'Exif.Photo.PixelYDimension', None, None), 
        (CAMERA, 'Exif.Image.Make', None, None), 
        (CAMERA, 'Exif.Image.Model', None, None), 
        (CAMERA, 'Exif.Photo.FNumber', None, None), 
        (CAMERA, 'Exif.Photo.ExposureTime', None, None), 
        (CAMERA, 'Exif.Photo.ISOSpeedRatings', None, None), 
        (CAMERA, 'Exif.Photo.FocalLength', None, None), 
        (CAMERA, 'Exif.Photo.MeteringMode', None, None), 
        (CAMERA, 'Exif.Photo.ExposureProgram', None, None), 
        (CAMERA, 'Exif.Photo.Flash', None, None), 
        (GPS, 'Exif.GPSInfo.GPSLatitude',
              'Exif.GPSInfo.GPSLatitudeRef', format_gps), 
        (GPS, 'Exif.GPSInfo.GPSLongitude',
              'Exif.GPSInfo.GPSLongitudeRef', format_gps)]

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
        self.model = ListModel(top, titles, list_mode="tree")
        return top
        
    def main(self):
        active_handle = self.get_active('Media')
        media = self.dbstate.db.get_object_from_handle(active_handle)

        self.sections = {}
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
        # pylint: disable-msg=E1101
        if media is None:
            return False

        full_path = Utils.media_path_full(self.dbstate.db, media.get_path())
        
        if OLD_API: # prior to v0.2.0
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
        # pylint: disable-msg=E1101
        full_path = Utils.media_path_full(self.dbstate.db, media.get_path())
        
        if OLD_API: # prior to v0.2.0
            try:
                metadata = pyexiv2.Image(full_path)
            except IOError:
                self.set_has_data(False)
                return
            metadata.readMetadata()
            for section, key, key2, func in TAGS:
                if key in metadata.exifKeys():
                    if section not in self.sections:
                        node = self.model.add([section, ''])
                        self.sections[section] = node
                    else:
                        node = self.sections[section]
                    label = metadata.tagDetails(key)[0]
                    if func:
                        human_value = func(metadata[key])
                    else:
                        human_value = metadata.interpretedExifValue(key)
                    if key2:
                        human_value += ' ' + metadata.interpretedExifValue(key2)
                    self.model.add((label, human_value), node=node)
            self.model.tree.expand_all()

        else: # v0.2.0 and above
            metadata = pyexiv2.ImageMetadata(full_path)
            try:
                metadata.read()
            except IOError:
                self.set_has_data(False)
                return
            for section, key, key2, func in TAGS:
                if key in metadata.exif_keys:
                    if section not in self.sections:
                        node = self.model.add([section, ''])
                        self.sections[section] = node
                    else:
                        node = self.sections[section]
                    tag = metadata[key]
                    if func:
                        human_value = func(tag.value)
                    else:
                        human_value = tag.human_value
                    if key2:
                        human_value += ' ' + metadata[key2].human_value
                    self.model.add((tag.label, human_value), node=node)
            self.model.tree.expand_all()

        self.set_has_data(self.model.count > 0)
