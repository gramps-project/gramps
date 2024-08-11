#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2022       Nick Hall
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
Handles generation and access to thumbnails used in Gramps.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import os
import logging
from hashlib import md5

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import GLib
from gi.repository import GdkPixbuf

try:
    from gi.repository import Gtk

    _icon_theme = Gtk.IconTheme.get_default()
except:
    _icon_theme = None

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import (
    ICON,
    IMAGE_DIR,
    THUMB_LARGE,
    THUMB_NORMAL,
    SIZE_NORMAL,
    SIZE_LARGE,
)
from gramps.gen.plug import BasePluginManager, START
from gramps.gen.mime import get_type

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
LOG = logging.getLogger(".thumbnail")

THUMBNAILERS = []


def get_thumbnailers():
    if len(THUMBNAILERS):
        return THUMBNAILERS

    plugman = BasePluginManager.get_instance()
    for pdata in plugman.get_reg_thumbnailers():
        module = plugman.load_plugin(pdata)
        if not module:
            print("Error loading thumbnailer '%s': skipping content" % pdata.name)
            continue
        thumbnailer = getattr(module, pdata.thumbnailer)()
        if pdata.order == START:
            THUMBNAILERS.insert(0, thumbnailer)
        else:
            THUMBNAILERS.append(thumbnailer)
    return THUMBNAILERS


# -------------------------------------------------------------------------
#
# __build_thumb_path
#
# -------------------------------------------------------------------------
def __build_thumb_path(path, rectangle=None, size=SIZE_NORMAL):
    """
    Convert the specified path into a corresponding path for the thumbnail
    image. We do this by converting the original path into an MD5SUM value
    (which should be unique), adding the '.png' extension, and prepending
    with the Gramps thumbnail directory.

    :type path: unicode
    :param path: filename of the source file
    :type rectangle: tuple
    :param rectangle: subsection rectangle
    :rtype: unicode
    :returns: full path name to the corresponding thumbnail file.
    """
    extra = ""
    if rectangle is not None:
        extra = "?" + str(rectangle)
    prehash = path + extra
    prehash = prehash.encode("utf-8")
    md5_hash = md5(prehash)
    if size == SIZE_LARGE:
        base_dir = THUMB_LARGE
    else:
        base_dir = THUMB_NORMAL
    return os.path.join(base_dir, md5_hash.hexdigest() + ".png")


# -------------------------------------------------------------------------
#
# __create_thumbnail_image
#
# -------------------------------------------------------------------------
def __create_thumbnail_image(src_file, mtype=None, rectangle=None, size=SIZE_NORMAL):
    """
    Generates the thumbnail image for a file. If the mime type is specified,
    and is not an 'image', then we attempt to find and run a thumbnailer
    utility to create a thumbnail. For images, we simply create a smaller
    image, scaled to thumbnail size.

    :param src_file: filename of the source file
    :type src_file: unicode
    :param mtype: mime type of the specified file (optional)
    :type mtype: unicode
    :param rectangle: subsection rectangle
    :type rectangle: tuple
    :rtype: bool
    :returns: True is the thumbnailwas successfully generated
    """
    if mtype is None:
        mtype = get_type(src_file)
    filename = __build_thumb_path(src_file, rectangle, size)
    return run_thumbnailer(mtype, src_file, filename, size, rectangle)


def run_thumbnailer(mime_type, src_file, dest_file, size, rectangle=None):
    """
    This function attempts to generate a thumbnail image.  It runs the first
    thumbnailer plugin that supports the given mime type.

    :param mime_type: mime type of the source file
    :type mime_type: unicode
    :param src_file: filename of the source file
    :type src_file: unicode
    :param dest_file: destination file for the thumbnail image
    :type dest_file: unicode
    :param size: option parameters specifying the desired size of the
      thumbnail
    :type size: int
    :param rectangle: subsection rectangle (optional)
    :type rectangle: tuple
    :returns: True if the thumbnail was successfully generated
    :rtype: bool
    """
    for thumbnailer in get_thumbnailers():
        if thumbnailer.is_supported(mime_type):
            if thumbnailer.run(mime_type, src_file, dest_file, size, rectangle):
                return True
    return False


# -------------------------------------------------------------------------
#
# find_mime_type_pixbuf
#
# -------------------------------------------------------------------------


def find_mime_type_pixbuf(mime_type):
    try:
        icontmp = mime_type.replace("/", "-")
        newicon = "gnome-mime-%s" % icontmp
        try:
            return _icon_theme.load_icon(newicon, 48, 0)
        except:
            icontmp = mime_type.split("/")[0]
            try:
                newicon = "gnome-mime-%s" % icontmp
                return _icon_theme.load_icon(newicon, 48, 0)
            except:
                return GdkPixbuf.Pixbuf.new_from_file(ICON)
    except:
        return GdkPixbuf.Pixbuf.new_from_file(ICON)


# -------------------------------------------------------------------------
#
# get_thumbnail_image
#
# -------------------------------------------------------------------------
def get_thumbnail_image(src_file, mtype=None, rectangle=None, size=SIZE_NORMAL):
    """
    Return the thumbnail image (in GTK Pixbuf format) associated with the
    source file passed to the function. If no thumbnail could be found,
    the associated icon for the mime type is returned, or if that cannot be
    found, a generic document icon is returned.

    The image is not generated every time, but only if the thumbnail does not
    exist, or if the source file is newer than the thumbnail.

    :param src_file: Source media file
    :type src_file: unicode
    :param mime_type: mime type of the source file
    :type mime_type: unicode
    :param rectangle: subsection rectangle
    :type rectangle: tuple
    :returns: thumbnail representing the source file
    :rtype: GdkPixbuf.Pixbuf
    """
    try:
        filename = get_thumbnail_path(src_file, mtype, rectangle, size)
        return GdkPixbuf.Pixbuf.new_from_file(filename)
    except (GLib.GError, OSError):
        if mtype:
            return find_mime_type_pixbuf(mtype)
        else:
            default = os.path.join(IMAGE_DIR, "document.png")
            return GdkPixbuf.Pixbuf.new_from_file(default)


# -------------------------------------------------------------------------
#
# get_thumbnail_path
#
# -------------------------------------------------------------------------
def get_thumbnail_path(src_file, mtype=None, rectangle=None, size=SIZE_NORMAL):
    """
    Return the path to the thumbnail image associated with the
    source file passed to the function. If the thumbnail does not exist,
    or if it is older than the source file, we create a new thumbnail image.

    :param src_file: Source media file
    :type src_file: unicode
    :param mime_type: mime type of the source file
    :type mime_type: unicode
    :param rectangle: subsection rectangle
    :type rectangle: tuple
    :returns: thumbnail representing the source file
    :rtype: GdkPixbuf.Pixbuf
    """
    filename = __build_thumb_path(src_file, rectangle, size)
    if not os.path.isfile(src_file):
        return os.path.join(IMAGE_DIR, "image-missing.png")
    else:
        if (not os.path.isfile(filename)) or (
            os.path.getmtime(src_file) > os.path.getmtime(filename)
        ):
            if not __create_thumbnail_image(src_file, mtype, rectangle, size):
                return os.path.join(IMAGE_DIR, "document.png")
        return os.path.abspath(filename)
