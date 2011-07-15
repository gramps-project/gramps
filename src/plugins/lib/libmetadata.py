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
from gen.ggettext import gettext as _
from PlaceUtils import conv_lat_lon
from fractions import Fraction
import gen.lib
import DateHandler
import datetime
import gtk
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
        return _('Invalid format')
    date_part = gen.lib.Date()
    date_part.set_yr_mon_day(exif_dt.year, exif_dt.month, exif_dt.day)
    date_str = DateHandler.displayer.display(date_part)
    time_str = _('%(hr)02d:%(min)02d:%(sec)02d') % {'hr': exif_dt.hour,
                                                    'min': exif_dt.minute,
                                                    'sec': exif_dt.second}
    return _('%(date)s %(time)s') % {'date': date_str, 'time': time_str}

def format_gps(dms_list, nsew_ref):
    """
    Convert a [degrees, minutes, seconds] list of Fractions and a direction
    reference into a string for display.
    """
    try:
        degs, mins, secs = dms_list
    except (TypeError, ValueError):
        return _('Invalid format')

    if not isinstance(degs, Fraction):
        # Old API uses pyexiv2.Rational
        degs = Fraction(str(degs))
        mins = Fraction(str(mins))
        secs = Fraction(str(secs))

    value = float(degs) + float(mins) / 60 + float(secs) / 3600

    if nsew_ref == 'N':
        result = conv_lat_lon(str(value), '0', 'DEG')[0]
    elif nsew_ref == 'S':
        result = conv_lat_lon('-' + str(value), '0', 'DEG')[0]
    elif nsew_ref == 'E':
        result = conv_lat_lon('0', str(value), 'DEG')[1]
    elif nsew_ref == 'W':
        result = conv_lat_lon('0', '-' + str(value), 'DEG')[1]
    else:
        result = None

    return result if result is not None else _('Invalid format')

DESCRIPTION = _('Description')
IMAGE = _('Image')
CAMERA = _('Camera')
GPS = _('GPS')
ADVANCED = _('Advanced')

TAGS = [(DESCRIPTION, 'Exif.Image.ImageDescription', None, None), 
        (DESCRIPTION, 'Exif.Image.Artist', None, None),
        (DESCRIPTION, 'Exif.Image.Copyright', None, None),
        (DESCRIPTION, 'Exif.Photo.DateTimeOriginal', None, format_datetime),
        (DESCRIPTION, 'Exif.Photo.DateTimeDigitized', None, format_datetime),
        (DESCRIPTION, 'Exif.Image.DateTime', None, format_datetime),
        (DESCRIPTION, 'Exif.Image.TimeZoneOffset', None, None),
        (DESCRIPTION, 'Exif.Image.XPSubject', None, None),
        (DESCRIPTION, 'Exif.Image.XPComment', None, None),
        (DESCRIPTION, 'Exif.Image.XPKeywords', None, None),
        (DESCRIPTION, 'Exif.Image.Rating', None, None),
        (IMAGE, 'Exif.Image.DocumentName', None, None),
        (IMAGE, 'Exif.Photo.PixelXDimension', None, None), 
        (IMAGE, 'Exif.Photo.PixelYDimension', None, None),
        (IMAGE, 'Exif.Image.XResolution', 'Exif.Image.ResolutionUnit', None),
        (IMAGE, 'Exif.Image.YResolution', 'Exif.Image.ResolutionUnit', None),
        (IMAGE, 'Exif.Image.Orientation', None, None),
        (IMAGE, 'Exif.Photo.ColorSpace', None, None),
        (IMAGE, 'Exif.Image.YCbCrPositioning', None, None),
        (IMAGE, 'Exif.Photo.ComponentsConfiguration', None, None),
        (IMAGE, 'Exif.Image.Compression', None, None),
        (IMAGE, 'Exif.Photo.CompressedBitsPerPixel', None, None),
        (IMAGE, 'Exif.Image.PhotometricInterpretation', None, None),
        (CAMERA, 'Exif.Image.Make', None, None), 
        (CAMERA, 'Exif.Image.Model', None, None), 
        (CAMERA, 'Exif.Photo.FNumber', None, None), 
        (CAMERA, 'Exif.Photo.ExposureTime', None, None), 
        (CAMERA, 'Exif.Photo.ISOSpeedRatings', None, None), 
        (CAMERA, 'Exif.Photo.FocalLength', None, None),
        (CAMERA, 'Exif.Photo.FocalLengthIn35mmFilm', None, None),
        (CAMERA, 'Exif.Photo.MaxApertureValue', None, None), 
        (CAMERA, 'Exif.Photo.MeteringMode', None, None), 
        (CAMERA, 'Exif.Photo.ExposureProgram', None, None),
        (CAMERA, 'Exif.Photo.ExposureBiasValue', None, None),
        (CAMERA, 'Exif.Photo.Flash', None, None),
        (CAMERA, 'Exif.Image.FlashEnergy', None, None),
        (CAMERA, 'Exif.Image.SelfTimerMode', None, None),
        (CAMERA, 'Exif.Image.SubjectDistance', None, None),
        (CAMERA, 'Exif.Photo.Contrast', None, None),
        (CAMERA, 'Exif.Photo.LightSource', None, None),
        (CAMERA, 'Exif.Photo.Saturation', None, None),
        (CAMERA, 'Exif.Photo.Sharpness', None, None),
        (CAMERA, 'Exif.Photo.WhiteBalance', None, None),
        (CAMERA, 'Exif.Photo.DigitalZoomRatio', None, None),
        (GPS, 'Exif.GPSInfo.GPSLatitude',
              'Exif.GPSInfo.GPSLatitudeRef', format_gps), 
        (GPS, 'Exif.GPSInfo.GPSLongitude',
              'Exif.GPSInfo.GPSLongitudeRef', format_gps),
        (GPS, 'Exif.GPSInfo.GPSAltitude',
              'Exif.GPSInfo.GPSAltitudeRef', None),
        (GPS, 'Exif.GPSInfo.GPSTimeStamp', None, None),
        (GPS, 'Exif.GPSInfo.GPSSatellites', None, None),
        (ADVANCED, 'Exif.Image.Software', None, None),
        (ADVANCED, 'Exif.Photo.ImageUniqueID', None, None),
        (ADVANCED, 'Exif.Image.CameraSerialNumber', None, None),
        (ADVANCED, 'Exif.Photo.ExifVersion', None, None),
        (ADVANCED, 'Exif.Photo.FlashpixVersion', None, None),
        (ADVANCED, 'Exif.Image.ExifTag', None, None),
        (ADVANCED, 'Exif.Image.GPSTag', None, None),
        (ADVANCED, 'Exif.Image.BatteryLevel', None, None)]

class MetadataView(gtk.TreeView):

    def __init__(self):
        gtk.TreeView.__init__(self)
        self.sections = {}
        titles = [(_('Key'), 1, 235), 
          (_('Value'), 2, 325)]
        self.model = ListModel(self, titles, list_mode="tree")

    def display_exif_tags(self, full_path):
        """
        Display the exif tags.
        """
        # pylint: disable=E1101
        self.sections = {}
        self.model.clear()
        if OLD_API: # prior to v0.2.0
            try:
                metadata = pyexiv2.Image(full_path)
            except IOError:
                return False
            metadata.readMetadata()
            for section, key, key2, func in TAGS:
                if key not in metadata.exifKeys():
                    continue

                if func is not None:
                    if key2 is None:
                        human_value = func(metadata[key])
                    else:
                        if key2 in metadata.exifKeys():
                            human_value = func(metadata[key], metadata[key2])
                        else:
                            human_value = func(metadata[key], None)
                else:
                    human_value = metadata.interpretedExifValue(key)
                    if key2 is not None and key2 in metadata.exifKeys():
                        human_value += ' ' + metadata.interpretedExifValue(key2)

                label = metadata.tagDetails(key)[0]
                node = self.__add_section(section)
                self.model.add((label, human_value), node=node)

        else: # v0.2.0 and above
            metadata = pyexiv2.ImageMetadata(full_path)
            try:
                metadata.read()
            except IOError:
                return False
            for section, key, key2, func in TAGS:
                if key not in metadata.exif_keys:
                    continue

                tag = metadata.get(key)
                if key2 is not None and key2 in metadata.exif_keys:
                    tag2 = metadata.get(key2)
                else:
                    tag2 = None

                if func is not None:
                    if key2 is None:
                        human_value = func(tag.value)
                    else:
                        if tag2 is None:
                            human_value = func(tag.value, None)
                        else:
                            human_value = func(tag.value, tag2.value)
                else:
                    human_value = tag.human_value
                    if tag2 is not None:
                        human_value += ' ' + tag2.human_value

                label = tag.label
                node = self.__add_section(section)
                self.model.add((tag.label, human_value), node=node)
                
        self.model.tree.expand_all()
        return self.model.count > 0

    def __add_section(self, section):
        """
        Add the section heading node to the model.
        """
        if section not in self.sections:
            node = self.model.add([section, ''])
            self.sections[section] = node
        else:
            node = self.sections[section]
        return node

    def get_has_data(self, full_path):
        """
        Return True if the gramplet has data, else return False.
        """
        # pylint: disable=E1101
        if OLD_API: # prior to v0.2.0
            try:
                metadata = pyexiv2.Image(full_path)
            except IOError:
                return False
            metadata.readMetadata()
            for tag in TAGS:
                if tag[1] in metadata.exifKeys():
                    return True

        else: # v0.2.0 and above
            metadata = pyexiv2.ImageMetadata(full_path)
            try:
                metadata.read()
            except IOError:
                return False
            for tag in TAGS:
                if tag[1] in metadata.exif_keys:
                    return True

        return False
