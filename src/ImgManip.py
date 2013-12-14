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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Image manipulation routines.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import tempfile

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import Utils

def crop_percentage_to_subpixel(width, height, crop):
    """
    Convert from Gramps cropping coordinates [0, 100] to
    pixels, given image width and height. No rounding to pixel resolution.
    """
    return (
        crop[0]/100.0*width,
        crop[1]/100.0*height,
        crop[2]/100.0*width,
        crop[3]/100.0*height )

def crop_percentage_to_pixel(width, height, crop):
    return map (int, crop_percentage_to_subpixel(width, height, crop))

#-------------------------------------------------------------------------
#
# resize_to_jpeg
#
#-------------------------------------------------------------------------
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
    import gtk

    img = gtk.gdk.pixbuf_new_from_file(source)

    if crop:
        (start_x, start_y, end_x, end_y
                ) = crop_percentage_to_pixel(
                        img.get_width(), img.get_height(), crop)
        img = img.subpixbuf(start_x, start_y, end_x-start_x, end_y-start_y)

    # Need to keep the ratio intact, otherwise scaled images look stretched
    # if the dimensions aren't close in size
    (width, height) = image_actual_size(width, height, img.get_width(), img.get_height())

    scaled = img.scale_simple(int(width), int(height), gtk.gdk.INTERP_BILINEAR)
    scaled.save(destination, 'jpeg')

#-------------------------------------------------------------------------
#
# image_dpi
#
#-------------------------------------------------------------------------
INCH_PER_MM = 1/25.4
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
        logging.warning(_("WARNING: PIL module not loaded.  "
                "Image cropping in report files will not be available."))
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
        import gtk
        dpi = (
            gtk.gdk.screen_width() / (INCH_PER_MM * gtk.gdk.screen_width_mm()),
            gtk.gdk.screen_height() / (INCH_PER_MM * gtk.gdk.screen_height_mm())
            )
    except:
        dpi = (96.0,96.0) #LibOO 3.6 assumes this if image contains no DPI info
        # This isn't safe even within a single platform (Windows), but we
        # can't do better if all of the above failed. See bug# 7290.
    return dpi

#-------------------------------------------------------------------------
#
# image_size
#
#-------------------------------------------------------------------------
def image_size(source):
    """
    Return the width and size of the specified image.

    :param source: source image file, in any format that gtk recongizes
    :type source: unicode
    :rtype: tuple(int, int)
    :returns: a tuple consisting of the width and height
    """
    import gtk
    import gobject
    try:
        img = gtk.gdk.pixbuf_new_from_file(source)
        width = img.get_width()
        height = img.get_height()
    except gobject.GError:
        width = 0
        height = 0
    return (width, height)

#-------------------------------------------------------------------------
#
# image_actual_size
#
#-------------------------------------------------------------------------
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

    ratio = float(x_cm)*float(y)/(float(y_cm)*float(x))

    if ratio < 1:
        act_width = x_cm
        act_height = y_cm*ratio
    else:
        act_height = y_cm
        act_width = x_cm/ratio

    return (act_width, act_height)

#-------------------------------------------------------------------------
#
# resize_to_buffer
#
#-------------------------------------------------------------------------
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
    import gtk
    img = gtk.gdk.pixbuf_new_from_file(source)

    if crop:
        (start_x, start_y, end_x, end_y
                ) = crop_percentage_to_pixel(
                        img.get_width(), img.get_height(), crop)
        img = img.subpixbuf(start_x, start_y, end_x-start_x, end_y-start_y)

    # Need to keep the ratio intact, otherwise scaled images look stretched
    # if the dimensions aren't close in size
    (size[0], size[1]) = image_actual_size(size[0], size[1], img.get_width(), img.get_height())

    scaled = img.scale_simple(int(size[0]), int(size[1]), gtk.gdk.INTERP_BILINEAR)

    return scaled

#-------------------------------------------------------------------------
#
# resize_to_jpeg_buffer
#
#-------------------------------------------------------------------------
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
    import gtk
    filed, dest = tempfile.mkstemp()
    img = gtk.gdk.pixbuf_new_from_file(source)

    if crop:
        (start_x, start_y, end_x, end_y
                ) = crop_percentage_to_pixel(
                        img.get_width(), img.get_height(), crop)

        img = img.subpixbuf(start_x, start_y, end_x-start_x, end_y-start_y)

    # Need to keep the ratio intact, otherwise scaled images look stretched
    # if the dimensions aren't close in size
    (size[0], size[1]) = image_actual_size(size[0], size[1], img.get_width(), img.get_height())

    scaled = img.scale_simple(int(size[0]), int(size[1]), gtk.gdk.INTERP_BILINEAR)
    os.close(filed)
    dest = Utils.get_unicode_path_from_env_var(dest)
    scaled.save(dest, 'jpeg')
    ofile = open(dest, mode='rb')
    data = ofile.read()
    ofile.close()
    try:
        os.unlink(dest)
    except:
        pass
    return data

