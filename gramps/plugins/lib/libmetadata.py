#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011,2014  Nick Hall
# Copyright (C) 2011       Rob G. Healey <robhealey1@gmail.com>
# Copyright (C) 2022       Bruce Jackson
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
# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import os
import logging

_LOG = logging.getLogger(".libmetadata")


# -------------------------------------------------------------------------
#
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
import gi

gi.require_version("GExiv2", "0.10")
from gi.repository import GExiv2
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject


# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gui.listmodel import ListModel, NOSORT, IMAGE as COL_IMAGE
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.utils.place import conv_lat_lon
from fractions import Fraction
from gramps.gen.lib import Date
from gramps.gen.datehandler import displayer
from datetime import datetime

THUMBNAIL_IMAGE_SIZE = (50, 50)


def format_datetime(datestring):
    """
    Convert an exif timestamp into a string for display, using the
    standard Gramps date format.  Function not used for XMP Date Metatags:
    https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata#date-value-type
    """
    try:
        timestamp = datetime.strptime(datestring, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return _("Invalid format")

    date_part = Date()
    date_part.set_yr_mon_day(timestamp.year, timestamp.month, timestamp.day)
    date_str = displayer.display(date_part)
    time_str = _("%(hr)02d:%(min)02d:%(sec)02d") % {
        "hr": timestamp.hour,
        "min": timestamp.minute,
        "sec": timestamp.second,
    }
    return _("%(date)s %(time)s") % {"date": date_str, "time": time_str}


def format_gps(raw_dms, nsew):
    """
    Convert raw degrees, minutes, seconds and a direction
    reference into a string for display.
    """
    value = 0.0
    divisor = 1.0
    for val in raw_dms.split(" "):
        try:
            num = float(val.split("/")[0]) / float(val.split("/")[1])
        except (ValueError, IndexError):
            value = None
            break
        value += num / divisor
        divisor *= 60

    if nsew == "N":
        result = conv_lat_lon(str(value), "0", "DEG")[0]
    elif nsew == "S":
        result = conv_lat_lon("-" + str(value), "0", "DEG")[0]
    elif nsew == "E":
        result = conv_lat_lon("0", str(value), "DEG")[1]
    elif nsew == "W":
        result = conv_lat_lon("0", "-" + str(value), "DEG")[1]
    else:
        result = None

    return result if result is not None else _("Invalid format")


DESCRIPTION = _("Descriptive Tags")
DATE = _("Date and Time Tags")
PEOPLE = _("People Tags")
EVENT = _("Event Tags")
IMAGE = _("Image Tags")
CAMERA = _("Camera Information")
LOCATION = _("Location Tags")
ADVANCED = _("Advanced Tags")
RIGHTS = _("Rights Tags")
TAGGING = _("Keyword Tags")

"""
List of tags available to plugin can be found at the Exiv2 project
https://www.exiv2.org/metadata.html
"""

TAGS = [
    (DESCRIPTION, "Exif.Image.ImageDescription", None, None),
    (DESCRIPTION, "Exif.Image.XPSubject", None, None),
    (DESCRIPTION, "Exif.Image.XPComment", None, None),
    (DESCRIPTION, "Exif.Image.Rating", None, None),
    (DESCRIPTION, "Xmp.dc.title", None, None),
    (DESCRIPTION, "Xmp.dc.description", None, None),
    (DESCRIPTION, "Xmp.dc.subject", None, None),
    (DESCRIPTION, "Xmp.acdsee.caption", None, None),
    (DESCRIPTION, "Xmp.acdsee.notes", None, None),
    (DESCRIPTION, "Iptc.Application2.Caption", None, None),
    (DESCRIPTION, "Exif.Photo.UserComment", None, None),
    (DESCRIPTION, "Xmp.iptcExt.AOTitle", None, None),
    (DATE, "Exif.Photo.DateTimeOriginal", None, format_datetime),
    (DATE, "Exif.Photo.DateTimeDigitized", None, format_datetime),
    (DATE, "Exif.Image.DateTime", None, format_datetime),
    (DATE, "Exif.Image.TimeZoneOffset", None, None),
    (DATE, "Xmp.Xmp.CreateDate", None, None),
    (DATE, "Xmp.photoshop.DateCreated", None, None),
    (PEOPLE, "Xmp.mwg-rs.Regions/mwg-rs:RegionList[1]/mwg-rs:Name", None, None),
    (PEOPLE, "Xmp.mwg-rs.Regions", None, None),
    (PEOPLE, "Xmp.iptcExt.PersonInImage", None, None),
    (EVENT, "Xmp.iptcExt.Event", None, None),
    (LOCATION, "Xmp.iptcExt.LocationShown", None, None),
    (LOCATION, "Exif.GPSInfo.GPSLatitude", "Exif.GPSInfo.GPSLatitudeRef", format_gps),
    (LOCATION, "Exif.GPSInfo.GPSLongitude", "Exif.GPSInfo.GPSLongitudeRef", format_gps),
    (LOCATION, "Exif.GPSInfo.GPSAltitude", "Exif.GPSInfo.GPSAltitudeRef", None),
    (LOCATION, "Exif.GPSInfo.GPSTimeStamp", None, None),
    (LOCATION, "Exif.GPSInfo.GPSSatellites", None, None),
    (TAGGING, "Exif.Image.XPKeywords", None, None),
    (TAGGING, "Iptc.Application2.Keywords", None, None),
    (TAGGING, "Xmp.mwg-kw.Hierarchy", None, None),
    (TAGGING, "Xmp.mwg-kw.Keywords", None, None),
    (TAGGING, "Xmp.digiKam.TagsList", None, None),
    (TAGGING, "Xmp.MicrosoftPhoto.LastKeywordXMP", None, None),
    (TAGGING, "Xmp.MicrosoftPhoto.LastKeywordIPTC", None, None),
    (TAGGING, "Xmp.lr.hierarchicalSubject", None, None),
    (TAGGING, "Xmp.acdsee.categories", None, None),
    (IMAGE, "Exif.Image.DocumentName", None, None),
    (IMAGE, "Exif.Photo.PixelXDimension", None, None),
    (IMAGE, "Exif.Photo.PixelYDimension", None, None),
    (IMAGE, "Exif.Image.XResolution", "Exif.Image.ResolutionUnit", None),
    (IMAGE, "Exif.Image.YResolution", "Exif.Image.ResolutionUnit", None),
    (IMAGE, "Exif.Image.Orientation", None, None),
    (IMAGE, "Exif.Photo.ColorSpace", None, None),
    (IMAGE, "Exif.Image.YCbCrPositioning", None, None),
    (IMAGE, "Exif.Photo.ComponentsConfiguration", None, None),
    (IMAGE, "Exif.Image.Compression", None, None),
    (IMAGE, "Exif.Photo.CompressedBitsPerPixel", None, None),
    (IMAGE, "Exif.Image.PhotometricInterpretation", None, None),
    (RIGHTS, "Exif.Image.Copyright", None, None),
    (RIGHTS, "Exif.Image.Artist", None, None),
    (RIGHTS, "Xmp.xmpRights.Owner", None, None),
    (RIGHTS, "Xmp.xmpRights.UsageTerms", None, None),
    (RIGHTS, "Xmp.xmpRights.WebStatement", None, None),
    (CAMERA, "Exif.Image.Make", None, None),
    (CAMERA, "Exif.Image.Model", None, None),
    (CAMERA, "Exif.Photo.FNumber", None, None),
    (CAMERA, "Exif.Photo.ExposureTime", None, None),
    (CAMERA, "Exif.Photo.ISOSpeedRatings", None, None),
    (CAMERA, "Exif.Photo.FocalLength", None, None),
    (CAMERA, "Exif.Photo.FocalLengthIn35mmFilm", None, None),
    (CAMERA, "Exif.Photo.MaxApertureValue", None, None),
    (CAMERA, "Exif.Photo.MeteringMode", None, None),
    (CAMERA, "Exif.Photo.ExposureProgram", None, None),
    (CAMERA, "Exif.Photo.ExposureBiasValue", None, None),
    (CAMERA, "Exif.Photo.Flash", None, None),
    (CAMERA, "Exif.Image.FlashEnergy", None, None),
    (CAMERA, "Exif.Image.SelfTimerMode", None, None),
    (CAMERA, "Exif.Image.SubjectDistance", None, None),
    (CAMERA, "Exif.Photo.Contrast", None, None),
    (CAMERA, "Exif.Photo.LightSource", None, None),
    (CAMERA, "Exif.Photo.Saturation", None, None),
    (CAMERA, "Exif.Photo.Sharpness", None, None),
    (CAMERA, "Exif.Photo.WhiteBalance", None, None),
    (CAMERA, "Exif.Photo.DigitalZoomRatio", None, None),
    (ADVANCED, "Exif.Image.Software", None, None),
    (ADVANCED, "Exif.Photo.ImageUniqueID", None, None),
    (ADVANCED, "Exif.Image.CameraSerialNumber", None, None),
    (ADVANCED, "Exif.Photo.ExifVersion", None, None),
    (ADVANCED, "Exif.Photo.FlashpixVersion", None, None),
    (ADVANCED, "Exif.Image.ExifTag", None, None),
    (ADVANCED, "Exif.Image.GPSTag", None, None),
    (ADVANCED, "Exif.Image.BatteryLevel", None, None),
]


class MetadataView(Gtk.TreeView):
    def __init__(self):
        Gtk.TreeView.__init__(self)
        self.sections = {}
        titles = [
            (_("Namespace"), 0, 150),
            (_("Label"), 1, 150),
            (_(" "), NOSORT, 60, COL_IMAGE),
            (_("Value"), NOSORT, 325),
        ]

        self.model = ListModel(self, titles, list_mode="tree")

    def display_exif_tags(self, image_path):
        """
        Display the exif tags.
        """
        self.sections = {}

        # set fixed_height_mode to FALSE so thumbnails are not truncated.
        self.model.tree.set_fixed_height_mode(False)
        self.model.clear()

        if not os.path.exists(image_path):
            return False

        retval = False
        with open(image_path, "rb") as fd:
            try:
                buf = fd.read()
                metadata = GExiv2.Metadata()
                metadata.open_buf(buf)
                self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
                get_human = metadata.get_tag_interpreted_string

                for section, key, key2, func in TAGS:
                    if not key in self.__get_all_tags(metadata):
                        continue

                    if func is not None:
                        if key2 is None:
                            human_value = func(metadata[key])
                        else:
                            if key2 in self.__get_all_tags(metadata):
                                human_value = func(metadata[key], metadata[key2])
                            else:
                                human_value = func(metadata[key], None)
                    else:
                        human_value = get_human(key)
                        if key2 in self.__get_all_tags(metadata):
                            human_value += " " + get_human(key2)

                    if human_value is None:
                        human_value = ""

                    # If first named region is found - find all named regions
                    if key == "Xmp.mwg-rs.Regions/mwg-rs:RegionList[1]/mwg-rs:Name":
                        self.__get_named_regions(metadata)
                        continue

                    label = metadata.get_tag_label(key)
                    namespace = self.__get_tag_namespace(key)

                    node = self.__add_section(section)
                    self.model.add([namespace, label, None, human_value], node=node)

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
            node = self.model.add([section, "", None, ""])
            self.sections[section] = node
        else:
            node = self.sections[section]
        return node

    def get_has_data(self, image_path):
        """
        Return True if the gramplet has data, else return False.
        """
        if not os.path.exists(image_path):
            return False
        with open(image_path, "rb") as fd:
            retval = False
            try:
                buf = fd.read()
                metadata = GExiv2.Metadata()
                metadata.open_buf(buf)
                for tag in TAGS:
                    if tag in self.__get_all_tags(metadata):
                        retval = True
                        break
            except:
                pass

        return retval

    def __get_all_tags(self, metadata):
        """
        Return a list of all XMP, IPTC and EXIF tags in the media file
        """
        tag_list = (
            metadata.get_exif_tags()
            + metadata.get_xmp_tags()
            + metadata.get_iptc_tags()
        )

        return tag_list

    def __get_named_regions(self, metadata):
        """
        Retrieve all XMP named regions in an image and populate the treeview row.
        """

        region_tag = "Xmp.mwg-rs.Regions/mwg-rs:RegionList[%s]/"
        region_name = region_tag + "mwg-rs:Name"
        region_x = region_tag + "mwg-rs:Area/stArea:x"
        region_y = region_tag + "mwg-rs:Area/stArea:y"
        region_w = region_tag + "mwg-rs:Area/stArea:w"
        region_h = region_tag + "mwg-rs:Area/stArea:h"

        pixbuf_width = self.pixbuf.get_width()
        pixbuf_height = self.pixbuf.get_height()

        i = 1
        while True:
            name = metadata.get(region_name % i)
            region_name_display = region_name % i

            if name is None:
                break
            try:
                x = float(metadata.get(region_x % i)) * pixbuf_width
                y = float(metadata.get(region_y % i)) * pixbuf_height
                w = float(metadata.get(region_w % i)) * pixbuf_width
                h = float(metadata.get(region_h % i)) * pixbuf_height
            except ValueError:
                x = pixbuf_width / 2
                y = pixbuf_height / 2
                w = pixbuf_width
                h = pixbuf_height

            # ensure region does not exceed bounds of image
            region_p1 = x - (w / 2)
            if region_p1 < 0:
                region_p1 = 0
            region_p2 = y - (h / 2)
            if region_p2 < 0:
                region_p2 = 0
            region_p3 = x + (w / 2)
            if region_p3 > pixbuf_width:
                region_p3 = pixbuf_width
            region_p4 = y + (h / 2)
            if region_p4 > pixbuf_height:
                region_p4 = pixbuf_height

            region = (region_p1, region_p2, region_p3, region_p4)
            person_thumbnail = self.__get_thumbnail(region, THUMBNAIL_IMAGE_SIZE)

            label = metadata.get_tag_label(region_name % i)
            namespace = self.__get_tag_namespace(region_name % i)

            node = self.__add_section(PEOPLE)
            self.model.add([namespace, label, person_thumbnail, name], node=node)

            i += 1

    def __get_thumbnail(self, region, thumbnail_size):
        """
        Returns the thumbnail of the given region.
        """
        w = region[2] - region[0]
        h = region[3] - region[1]

        if (
            w <= self.pixbuf.get_width()
            and h <= self.pixbuf.get_height()
            and self.pixbuf
        ):
            subpixbuf = self.pixbuf.new_subpixbuf(region[0], region[1], w, h)
            size = self.__resize_keep_aspect(w, h, *thumbnail_size)
            return subpixbuf.scale_simple(
                size[0], size[1], GdkPixbuf.InterpType.BILINEAR
            )
        else:
            return None

    def __resize_keep_aspect(self, orig_x, orig_y, target_x, target_y):
        """
        Calculates the dimensions of the rectangle obtained from
        the rectangle orig_x * orig_y by scaling to fit
        target_x * target_y keeping the aspect ratio.
        """
        orig_aspect = orig_x / orig_y
        target_aspect = target_x / target_y
        if orig_aspect > target_aspect:
            return (target_x, target_x * orig_y // orig_x)
        else:
            return (target_y * orig_x // orig_y, target_y)

    def __get_tag_namespace(self, key):
        x = key.split(".")
        del x[-1]
        namespace = ".".join(x)

        return namespace
