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
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------

from gramps.gui.listmodel import ListModel
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.utils.place import conv_lat_lon
from fractions import Fraction
from gramps.gen.lib import Date
from gramps.gen.datehandler import displayer
from datetime import datetime

def format_datetime(datestring):
    """
    Convert an exif timestamp into a string for display, using the
    standard Gramps date format.
    """
    try:
        timestamp = datetime.strptime(datestring, '%Y:%m:%d %H:%M:%S')
    except ValueError:
        return _('Invalid format')
    date_part = Date()
    date_part.set_yr_mon_day(timestamp.year, timestamp.month, timestamp.day)
    date_str = displayer.display(date_part)
    time_str = _('%(hr)02d:%(min)02d:%(sec)02d') % {'hr': timestamp.hour,
                                                    'min': timestamp.minute,
                                                    'sec': timestamp.second}
    return _('%(date)s %(time)s') % {'date': date_str, 'time': time_str}

def format_gps(raw_dms, nsew):
    """
    Convert raw degrees, minutes, seconds and a direction
    reference into a string for display.
    """
    value = 0.0
    divisor = 1.0
    for val in raw_dms.split(' '):
        try:
            num = float(val.split('/')[0]) / float(val.split('/')[1])
        except (ValueError, IndexError):
            value = None
            break
        value += num / divisor
        divisor *= 60

    if nsew == 'N':
        result = conv_lat_lon(str(value), '0', 'DEG')[0]
    elif nsew == 'S':
        result = conv_lat_lon('-' + str(value), '0', 'DEG')[0]
    elif nsew == 'E':
        result = conv_lat_lon('0', str(value), 'DEG')[1]
    elif nsew == 'W':
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

class MetadataView(Gtk.TreeView):

    def __init__(self):
        Gtk.TreeView.__init__(self)
        self.sections = {}
        titles = [(_('Key'), 1, 235),
                  (_('Value'), 2, 325)]
        self.model = ListModel(self, titles, list_mode="tree")

    def display_exif_tags(self, full_path):
        """
        Display the exif tags.
        """
        self.sections = {}
        self.model.clear()

        if not os.path.exists(full_path):
            return False

        retval = False
        with open(full_path, 'rb') as fd:
            try:
                buf = fd.read()
                metadata = GExiv2.Metadata()
                metadata.open_buf(buf)

                get_human = metadata.get_tag_interpreted_string

                for section, key, key2, func in TAGS:
                    if not key in metadata.get_exif_tags():
                        continue

                    if func is not None:
                        if key2 is None:
                            human_value = func(metadata[key])
                        else:
                            if key2 in metadata.get_exif_tags():
                                human_value = func(metadata[key], metadata[key2])
                            else:
                                human_value = func(metadata[key], None)
                    else:
                        human_value = get_human(key)
                        if key2 in metadata.get_exif_tags():
                            human_value += ' ' + get_human(key2)

                    label = metadata.get_tag_label(key)
                    node = self.__add_section(section)
                    if human_value is None:
                        human_value = ''
                    self.model.add((label, human_value), node=node)

                    self.model.tree.expand_all()
                    retval = self.model.count > 0
            except:
                pass

        return retval

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
        if not os.path.exists(full_path):
            return False
        with open(full_path, 'rb') as fd:
            retval = False
            try:
                buf = fd.read()
                metadata = GExiv2.Metadata()
                metadata.open_buf(buf)
                for tag in TAGS:
                    if tag in metadata.get_exif_tags():
                        retval = True
                        break
            except:
                pass

        return retval
