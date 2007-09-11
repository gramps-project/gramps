#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
import gtk
import gobject

#-------------------------------------------------------------------------
#
# resize_to_jpeg
#
#-------------------------------------------------------------------------
def resize_to_jpeg(source, destination, width, height):
    """
    Creates the destination, derived from the source, resizing it to the
    specified size, while converting to JPEG.

    @param source: source image file, in any format that gtk recognizes
    @type source: unicode
    @param destination: destination image file, output written in jpeg format
    @type destination: unicode
    @param width: desired width of the destination image
    @type width: int
    @param height: desired height of the destination image
    @type height: int
    """
    img = gtk.gdk.pixbuf_new_from_file(source)
    scaled = img.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)
    scaled.save(destination, 'jpeg')

#-------------------------------------------------------------------------
#
# image_size
#
#-------------------------------------------------------------------------
def image_size(source):
    """
    Returns the width and size of the specified image.

    @param source: source image file, in any format that gtk recongizes
    @type source: unicode
    @rtype: tuple(int, int)
    @returns: a tuple consisting of the width and height
    """
    try:
        img = gtk.gdk.pixbuf_new_from_file(source)
        width = self.img.get_width()
        height = self.img.get_height()
    except gobject.GError:
        width = 0
        height = 0
    return (width, height)

#-------------------------------------------------------------------------
#
# resize_to_jpeg_buffer
#
#-------------------------------------------------------------------------
def resize_to_jpeg_buffer(source, width, height):
    """
    Loads the image, converting the file to JPEG, and resizing it. Instead of
    saving the file, the data is returned in a buffer.

    @param source: source image file, in any format that gtk recognizes
    @type source: unicode
    @param width: desired width of the destination image
    @type width: int
    @param height: desired height of the destination image
    @type height: int
    @rtype: buffer of data 
    @returns: jpeg image as raw data
    """
    fd, dest = tempfile.mkstemp()
    img = gtk.gdk.pixbuf_new_from_file(source)
    scaled = img.scale_simple(int(width), int(height), gtk.gdk.INTERP_BILINEAR)
    scaled.save(dest, 'jpeg')
    fh = open(dest, mode='rb')
    data = fh.read()
    fh.close()
    try:
        os.unlink(dest)
    except:
        pass
    return data

