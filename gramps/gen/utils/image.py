#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2011       Adam Stein <adam@csh.rit.edu>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Image manipulation routines.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import os
import sys
import tempfile

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


def crop_percentage_to_subpixel(width, height, crop):
    """
    Convert from Gramps cropping coordinates [0, 100] to
    pixels, given image width and height. No rounding to pixel resolution.
    """
    return (
        crop[0] / 100.0 * width,
        crop[1] / 100.0 * height,
        crop[2] / 100.0 * width,
        crop[3] / 100.0 * height,
    )


def crop_percentage_to_pixel(width, height, crop):
    return map(int, crop_percentage_to_subpixel(width, height, crop))


# -------------------------------------------------------------------------
#
# resize_to_jpeg
#
# -------------------------------------------------------------------------
def resize_to_jpeg(source, destination, width, height, crop=None):
    """
    Create the destination, derived from the source, resizing it to the
    specified size, while converting to JPEG.

    :param source: source image file, in any format that gtk recognizes
    :type source: unicode
    :param destination: destination image file, output written in jpeg format
    :type destination: unicode
    :param width: desired width of the destination image
    :type width: int
    :param height: desired height of the destination image
    :type height: int
    :param crop: cropping coordinates
    :type crop: array of integers ([start_x, start_y, end_x, end_y])
    """
    from gi.repository import GdkPixbuf

    img = GdkPixbuf.Pixbuf.new_from_file(source)

    if crop:
        start_x, start_y, end_x, end_y = crop_percentage_to_pixel(
            img.get_width(), img.get_height(), crop
        )
        if end_x - start_x > 0 and end_y - start_y > 0:
            img = img.new_subpixbuf(start_x, start_y, end_x - start_x, end_y - start_y)

    # Need to keep the ratio intact, otherwise scaled images look stretched
    # if the dimensions aren't close in size
    width, height = image_actual_size(width, height, img.get_width(), img.get_height())

    scaled = img.scale_simple(int(width), int(height), GdkPixbuf.InterpType.BILINEAR)
    scaled.savev(destination, "jpeg", "", "")


# -------------------------------------------------------------------------
#
# image_dpi
#
# -------------------------------------------------------------------------
MM_PER_INCH = 25.4


def image_dpi(source):
    """
    Return the dpi found in the image header. Use a sensible
    default of the screen DPI or 96.0 dpi if N/A.

    :param source: source image file, in any format that PIL recognizes
    :type source: unicode
    :rtype: int
    :returns: (x_dpi, y_dpi)
    """
    try:
        import PIL.Image
    except ImportError:
        import logging

        logging.warning(
            _(
                "WARNING: PIL module not loaded.  "
                "Image cropping in report files will be impaired."
            )
        )
    else:
        try:
            img = PIL.Image.open(source)
        except IOError:
            pass
        else:
            try:
                dpi = img.info["dpi"]
                return dpi
            except (AttributeError, KeyError):
                pass
    try:
        from gi.repository import Gdk

        mon = Gdk.Display.get_default().get_primary_monitor()
        mon_geom = mon.get_geometry()
        scale = mon.get_scale_factor() * MM_PER_INCH
        dpi = (
            mon_geom.width * scale / mon.get_width_mm(),
            mon_geom.height * scale / mon.get_height_mm(),
        )
    except:
        dpi = (96.0, 96.0)  # LibOO 3.6 assumes this if image contains no DPI info
        # This isn't safe even within a single platform (Windows), but we
        # can't do better if all of the above failed. See bug# 7290.
    return dpi


# -------------------------------------------------------------------------
#
# image_size
#
# -------------------------------------------------------------------------
def image_size(source: str) -> tuple[int, int]:
    """
    Return the width and size of the specified image.

    :param source: source image file, in any format that gtk recongizes
    :type source: unicode
    :rtype: tuple(int, int)
    :returns: a tuple consisting of the width and height
    """
    try:
        # For performance reasons, we'll try to get image size from imagesize.
        import imagesize

        return imagesize.get(source)
    except (ImportError, FileNotFoundError, ValueError):
        # python-imagesize is not installed, the file does not exist, or
        # the size cannot be determined by imagesize.
        pass
    try:
        # PIL is available on every supported platform and does not need
        # GTK, so prefer it over GdkPixbuf for headless/CLI use.
        from PIL import Image

        with Image.open(source) as img:
            return img.size
    except Exception:
        # Not a readable image (missing file, PDF, non-image media).
        pass
    try:
        # Fall back to Gdk for formats PIL cannot read but gtk can.
        from gi.repository import GdkPixbuf
        from gi.repository import GLib

        try:
            img = GdkPixbuf.Pixbuf.new_from_file(source)
            width = img.get_width()
            height = img.get_height()
        except (GLib.GError, Exception):
            width = 0
            height = 0
        return (width, height)
    except ImportError:
        return (0, 0)


# -------------------------------------------------------------------------
#
# image_actual_size
#
# -------------------------------------------------------------------------
def image_actual_size(x_cm, y_cm, x, y):
    """
    Calculate what the actual width & height of the image should be.

    :param x_cm: width in centimeters
    :type source: int
    :param y_cm: height in centimeters
    :type source: int
    :param x: desired width in pixels
    :type source: int
    :param y: desired height in pixels
    :type source: int
    :rtype: tuple(int, int)
    :returns: a tuple consisting of the width and height in centimeters
    """

    ratio = float(x_cm) * float(y) / (float(y_cm) * float(x))

    if ratio < 1:
        act_width = x_cm
        act_height = y_cm * ratio
    else:
        act_height = y_cm
        act_width = x_cm / ratio

    return (act_width, act_height)


# -------------------------------------------------------------------------
#
# image_crop_to_ratio
#
# -------------------------------------------------------------------------
def image_crop_to_ratio(width, height, box_width, box_height):
    """
    Return the cropping coordinates, as percentages, of the largest centred
    region of an image that has the same aspect ratio as the given box.

    Passing the result to a drawing function together with the box size gives
    a "fill the box" result, as opposed to the default "fit inside the box".

    :param width: width of the source image in pixels
    :type width: int
    :param height: height of the source image in pixels
    :type height: int
    :param box_width: width of the target box
    :type box_width: float
    :param box_height: height of the target box
    :type box_height: float
    :rtype: list(int)
    :returns: cropping coordinates ([start_x, start_y, end_x, end_y])
    """
    if width <= 0 or height <= 0 or box_width <= 0 or box_height <= 0:
        return [0, 0, 100, 100]

    # The region to keep is as tall as the box ratio allows, or as wide.
    box_ratio = float(box_width) / float(box_height)
    image_ratio = float(width) / float(height)

    if image_ratio > box_ratio:
        # Image is too wide, so trim the sides.
        keep = box_ratio / image_ratio * 100.0
        offset = (100.0 - keep) / 2.0
        return [int(offset), 0, int(100.0 - offset), 100]

    # Image is too tall, so trim the top and the bottom.
    keep = image_ratio / box_ratio * 100.0
    offset = (100.0 - keep) / 2.0
    return [0, int(offset), 100, int(100.0 - offset)]


# -------------------------------------------------------------------------
#
# resize_to_buffer
#
# -------------------------------------------------------------------------
def resize_to_buffer(source, size, crop=None):
    """
    Loads the image and resizes it. Instead of saving the file, the data
    is returned in a buffer.

    :param source: source image file, in any format that gtk recognizes
    :type source: unicode
    :param size: desired size of the destination image ([width, height])
    :type size: list
    :param crop: cropping coordinates
    :type crop: array of integers ([start_x, start_y, end_x, end_y])
    :rtype: buffer of data
    :returns: raw data
    """
    from gi.repository import GdkPixbuf
    from gi.repository import GLib

    if not crop:
        # No cropping is required, so Gdk can scale the image while decoding
        # it.  This avoids holding the full sized image in memory, which
        # matters for the large scans people keep in their media objects.
        width, height = image_size(source)
        if (width, height) == (0, 0):
            raise GLib.GError("not a supported image: %s" % source)
        width, height = image_actual_size(size[0], size[1], width, height)
        return GdkPixbuf.Pixbuf.new_from_file_at_scale(
            source,
            max(1, int(width)),
            max(1, int(height)),
            GdkPixbuf.InterpType.BILINEAR,
        )

    img = GdkPixbuf.Pixbuf.new_from_file(source)

    start_x, start_y, end_x, end_y = crop_percentage_to_pixel(
        img.get_width(), img.get_height(), crop
    )
    if end_x - start_x > 0 and end_y - start_y > 0:
        img = img.new_subpixbuf(start_x, start_y, end_x - start_x, end_y - start_y)

    # Need to keep the ratio intact, otherwise scaled images look stretched
    # if the dimensions aren't close in size
    size[0], size[1] = image_actual_size(
        size[0], size[1], img.get_width(), img.get_height()
    )

    scaled = img.scale_simple(int(size[0]), int(size[1]), GdkPixbuf.InterpType.BILINEAR)

    return scaled


# -------------------------------------------------------------------------
#
# resize_to_jpeg_buffer
#
# -------------------------------------------------------------------------
def resize_to_jpeg_buffer(source, size, crop=None):
    """
    Loads the image, converting the file to JPEG, and resizing it. Instead of
    saving the file, the data is returned in a buffer.

    :param source: source image file, in any format that gtk recognizes
    :type source: unicode
    :param size: desired size of the destination image ([width, height])
    :type size: list
    :param crop: cropping coordinates
    :type crop: array of integers ([start_x, start_y, end_x, end_y])
    :rtype: buffer of data
    :returns: jpeg image as raw data
    """
    from gi.repository import GdkPixbuf

    filed, dest = tempfile.mkstemp()
    img = GdkPixbuf.Pixbuf.new_from_file(source)

    if crop:
        start_x, start_y, end_x, end_y = crop_percentage_to_pixel(
            img.get_width(), img.get_height(), crop
        )
        if end_x - start_x > 0 and end_y - start_y > 0:
            img = img.new_subpixbuf(start_x, start_y, end_x - start_x, end_y - start_y)

    # Need to keep the ratio intact, otherwise scaled images look stretched
    # if the dimensions aren't close in size
    size[0], size[1] = image_actual_size(
        size[0], size[1], img.get_width(), img.get_height()
    )

    scaled = img.scale_simple(int(size[0]), int(size[1]), GdkPixbuf.InterpType.BILINEAR)
    os.close(filed)
    scaled.savev(dest, "jpeg", "", "")
    with open(dest, mode="rb") as ofile:
        data = ofile.read()
    try:
        os.unlink(dest)
    except:
        pass
    return data
