#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import logging
from hashlib import md5

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GLib
from gi.repository import GdkPixbuf

try:
    from gi.repository import Gtk
    _icon_theme = Gtk.IconTheme.get_default()
except:
    _icon_theme = None

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import (ICON, IMAGE_DIR, THUMB_LARGE, THUMB_NORMAL,
                              THUMBSCALE, THUMBSCALE_LARGE, USE_THUMBNAILER)
from gramps.gen.constfunc import win

#-------------------------------------------------------------------------
#
# gconf - try loading gconf for GNOME based systems. If we find it, we
#         might be able to generate thumbnails for non-image files.
#
#-------------------------------------------------------------------------
try:
    #test first for the key to avoid an error in the importer that causes
    #the error logger to activate
    ##TODO GTK3: Is this the best way to avoid error?
    import gi.repository as repo
    repo.__dict__['GConf']
    from gi.repository import GConf
    GCONF = True
    CLIENT = GConf.Client.get_default()
except (ImportError, KeyError) as msg:
    GCONF = False

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
LOG = logging.getLogger(".thumbnail")
SIZE_NORMAL = 0
SIZE_LARGE = 1

#-------------------------------------------------------------------------
#
# __get_gconf_string
#
#-------------------------------------------------------------------------
def __get_gconf_string(key):
    """
    Attempt to retrieve a value from the GNOME gconf database based of the
    passed key.

    :param key: GCONF key
    :type key: unicode
    :returns: Value associated with the GCONF key
    :rtype: unicode
    """
    try:
        val = CLIENT.get_string(key)
    except GLib.GError:
        val = None
    return str(val)

#-------------------------------------------------------------------------
#
# __get_gconf_bool
#
#-------------------------------------------------------------------------
def __get_gconf_bool(key):
    """
    Attempt to retrieve a value from the GNOME gconf database based of the
    passed key.

    :param key: GCONF key
    :type key: unicode
    :returns: Value associated with the GCONF key
    :rtype: bool
    """
    try:
        val = CLIENT.get_bool(key)
    except GLib.GError:
        val = None
    return val

#-------------------------------------------------------------------------
#
# __build_thumb_path
#
#-------------------------------------------------------------------------
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
    prehash = prehash.encode('utf-8')
    md5_hash = md5(prehash)
    if size == SIZE_LARGE:
        base_dir = THUMB_LARGE
    else:
        base_dir = THUMB_NORMAL
    return os.path.join(base_dir, md5_hash.hexdigest()+'.png')

#-------------------------------------------------------------------------
#
# __create_thumbnail_image
#
#-------------------------------------------------------------------------
def __create_thumbnail_image(src_file, mtype=None, rectangle=None,
                             size=SIZE_NORMAL):
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
    filename = __build_thumb_path(src_file, rectangle, size)

    if mtype and not mtype.startswith('image/'):
        # Not an image, so run the thumbnailer
        return run_thumbnailer(mtype, src_file, filename)
    else:
        # build a thumbnail by scaling the image using GTK's built in
        # routines.
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(src_file)
            width = pixbuf.get_width()
            height = pixbuf.get_height()

            if rectangle is not None:
                upper_x = min(rectangle[0], rectangle[2])/100.
                lower_x = max(rectangle[0], rectangle[2])/100.
                upper_y = min(rectangle[1], rectangle[3])/100.
                lower_y = max(rectangle[1], rectangle[3])/100.
                sub_x = int(upper_x * width)
                sub_y = int(upper_y * height)
                sub_width = int((lower_x - upper_x) * width)
                sub_height = int((lower_y - upper_y) * height)
                if sub_width > 0 and sub_height > 0:
                    pixbuf = pixbuf.new_subpixbuf(sub_x, sub_y, sub_width, sub_height)
                    width = sub_width
                    height = sub_height

            if size == SIZE_LARGE:
                thumbscale = THUMBSCALE_LARGE
            else:
                thumbscale = THUMBSCALE
            scale = thumbscale / (float(max(width, height)))

            scaled_width = int(width * scale)
            scaled_height = int(height * scale)

            pixbuf = pixbuf.scale_simple(scaled_width, scaled_height,
                                         GdkPixbuf.InterpType.BILINEAR)
            pixbuf.savev(filename, "png", "", "")
            return True
        except Exception as err:
            LOG.warning("Error scaling image down: %s", str(err))
            return False

#-------------------------------------------------------------------------
#
# find_mime_type_pixbuf
#
#-------------------------------------------------------------------------

def find_mime_type_pixbuf(mime_type):
    try:
        icontmp = mime_type.replace('/','-')
        newicon = "gnome-mime-%s" % icontmp
        try:
            return _icon_theme.load_icon(newicon,48,0)
        except:
            icontmp = mime_type.split('/')[0]
            try:
                newicon = "gnome-mime-%s" % icontmp
                return _icon_theme.load_icon(newicon,48,0)
            except:
                return GdkPixbuf.Pixbuf.new_from_file(ICON)
    except:
        return GdkPixbuf.Pixbuf.new_from_file(ICON)
#-------------------------------------------------------------------------
#
# run_thumbnailer
#
#-------------------------------------------------------------------------
def run_thumbnailer(mime_type, src_file, dest_file, size=SIZE_NORMAL):
    """
    This function attempts to generate a thumbnail image for a non-image.
    This includes things such as video and PDF files. This will currently
    only succeed if the GNOME environment is installed, since at this point,
    only the GNOME environment has the ability to generate thumbnails.

    :param mime_type: mime type of the source file
    :type mime_type: unicode
    :param src_file: filename of the source file
    :type src_file: unicode
    :param dest_file: destination file for the thumbnail image
    :type dest_file: unicode
    :param size: option parameters specifying the desired size of the
      thumbnail
    :type size: int
    :returns: True if the thumbnail was successfully generated
    :rtype: bool
    """
    # only try this if GCONF is present, the thumbnailer has not been
    # disabled, and if the src_file actually exists
    if GCONF and USE_THUMBNAILER and os.path.isfile(src_file):

        # find the command and enable for the associated mime types by
        # querying the gconf database
        base = '/desktop/gnome/thumbnailers/%s' % mime_type.replace('/', '@')
        cmd = __get_gconf_string(base + '/command')
        enable = __get_gconf_bool(base + '/enable')

        # if we found the command and it has been enabled, then spawn
        # of the command to build the thumbnail
        if cmd and enable:
            if size == SIZE_LARGE:
                thumbscale = THUMBSCALE_LARGE
            else:
                thumbscale = THUMBSCALE
            sublist = {
                '%s' : "%d" % int(thumbscale),
                '%u' : src_file,
                '%o' : dest_file,
                }
            cmdlist = [ sublist.get(x, x) for x in cmd.split() ]
            return os.spawnvpe(os.P_WAIT, cmdlist[0], cmdlist, os.environ) == 0
    return False

#-------------------------------------------------------------------------
#
# get_thumbnail_image
#
#-------------------------------------------------------------------------
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

#-------------------------------------------------------------------------
#
# get_thumbnail_path
#
#-------------------------------------------------------------------------
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
                os.path.getmtime(src_file) > os.path.getmtime(filename)):
            if not __create_thumbnail_image(src_file, mtype, rectangle, size):
                return os.path.join(IMAGE_DIR, "document.png")
        return os.path.abspath(filename)
