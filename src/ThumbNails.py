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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Handles generation and access to thumbnails used in GRAMPS.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import md5

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gobject

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Mime

#-------------------------------------------------------------------------
#
# gconf - try loading gconf for GNOME based systems. If we find it, we
#         might be able to generate thumbnails for non-image files.
#
#-------------------------------------------------------------------------
try:
    import gconf
    GCONF = True
    CLIENT = gconf.client_get_default()
except ImportError:
    GCONF = False

#-------------------------------------------------------------------------
#
# __get_gconf_string
#
#-------------------------------------------------------------------------
def __get_gconf_string(key):
    """
    Attempt to retrieve a value from the GNOME gconf database based of the
    passed key.

    @param key: GCONF key
    @type key: unicode
    @returns: Value associated with the GCONF key
    @rtype: unicode
    """
    try:
        val =  CLIENT.get_string(key)
    except gobject.GError:
        val = None
    return unicode(val)

#-------------------------------------------------------------------------
#
# __get_gconf_bool
#
#-------------------------------------------------------------------------
def __get_gconf_bool(key):
    """
    Attempt to retrieve a value from the GNOME gconf database based of the
    passed key.

    @param key: GCONF key
    @type key: unicode
    @returns: Value associated with the GCONF key
    @rtype: bool
    """
    try:
        val = CLIENT.get_bool(key)
    except gobject.GError:
        val = None
    return val

#-------------------------------------------------------------------------
#
# __build_thumb_path
#
#-------------------------------------------------------------------------
def __build_thumb_path(path, rectangle=None):
    """
    Converts the specified path into a corresponding path for the thumbnail
    image. We do this by converting the original path into an MD5SUM value
    (which should be unique), adding the '.png' extension, and prepending
    with the GRAMPS thumbnail directory.

    @type path: unicode
    @param path: filename of the source file
    @type rectangle: tuple
    @param rectangle: subsection rectangle
    @rtype: unicode
    @returns: full path name to the corresponding thumbnail file.
    """
    extra = ""
    if rectangle != None:
        extra = "?" + str(rectangle)
    md5_hash = md5.md5(path+extra)
    return os.path.join(const.THUMB_DIR, md5_hash.hexdigest()+'.png')

#-------------------------------------------------------------------------
#
# __create_thumbnail_image
#
#-------------------------------------------------------------------------
def __create_thumbnail_image(src_file, mtype=None, rectangle=None):
    """
    Generates the thumbnail image for a file. If the mime type is specified,
    and is not an 'image', then we attempt to find and run a thumbnailer
    utility to create a thumbnail. For images, we simply create a smaller
    image, scaled to thumbnail size.

    @param src_file: filename of the source file
    @type src_file: unicode
    @param mtype: mime type of the specified file (optional)
    @type mtype: unicode
    @param rectangle: subsection rectangle
    @type rectangle: tuple
    """
    filename = __build_thumb_path(src_file, rectangle)

    if mtype and not mtype.startswith('image/'):
        # Not an image, so run the thumbnailer
        run_thumbnailer(mtype, src_file, filename)
    else:
        # build a thumbnail by scaling the image using GTK's built in 
        # routines.
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(src_file)
            width = pixbuf.get_width()
            height = pixbuf.get_height()

            if rectangle != None:
                upper_x = min(rectangle[0], rectangle[2])/100.
                lower_x = max(rectangle[0], rectangle[2])/100.
                upper_y = min(rectangle[1], rectangle[3])/100.
                lower_y = max(rectangle[1], rectangle[3])/100.
                sub_x = int(upper_x * width)
                sub_y = int(upper_y * height)
                sub_width = int((lower_x - upper_x) * width)
                sub_height = int((lower_y - upper_y) * height)
                if sub_width > 0 and sub_height > 0:
                    pixbuf = pixbuf.subpixbuf(sub_x, sub_y, sub_width, sub_height)
                    width = sub_width
                    height = sub_height
                    
            scale = const.THUMBSCALE / (float(max(width, height)))
            
            scaled_width = int(width * scale)
            scaled_height = int(height * scale)
            
            pixbuf = pixbuf.scale_simple(scaled_width, scaled_height, 
                                         gtk.gdk.INTERP_BILINEAR)
            pixbuf.save(filename, "png")
        except:
            return

#-------------------------------------------------------------------------
#
# run_thumbnailer
#
#-------------------------------------------------------------------------
def run_thumbnailer(mime_type, src_file, dest_file, size=const.THUMBSCALE):
    """
    This function attempts to generate a thumbnail image for a non-image.
    This includes things such as video and PDF files. This will currently
    only succeed if the GNOME environment is installed, since at this point,
    only the GNOME environment has the ability to generate thumbnails.

    @param mime_type: mime type of the source file
    @type mime_type: unicode
    @param src_file: filename of the source file
    @type src_file: unicode
    @param dest_file: destination file for the thumbnail image
    @type dest_file: unicode
    @param size: option parameters specifying the desired size of the 
      thumbnail
    @type size: int
    @rtype: bool
    @returns: True if the thumbnail was successfully generated
    """

    # only try this if GCONF is present, the thumbnailer has not been 
    # disabled, and if the src_file actually exists
    if GCONF and const.USE_THUMBNAILER and os.path.isfile(src_file):
        
        # find the command and enable for the associated mime types by 
        # querying the gconf database
        base = '/desktop/gnome/thumbnailers/%s' % mime_type.replace('/', '@')
        cmd = __get_gconf_string(base + '/command')
        enable = __get_gconf_bool(base + '/enable')

        # if we found the command and it has been enabled, then spawn
        # of the command to build the thumbnail
        if cmd and enable:
            sublist = {
                '%s' : "%d" % int(size),
                '%u' : src_file, 
                '%o' : dest_file, 
                }
            cmdlist = [ sublist.get(x, x) for x in cmd.split() ]
            os.spawnvpe(os.P_WAIT, cmdlist[0], cmdlist, os.environ)
            return True
    return False

#-------------------------------------------------------------------------
#
# get_thumbnail_image
#
#-------------------------------------------------------------------------
def get_thumbnail_image(src_file, mtype=None, rectangle=None):
    """
    Returns the thumbnail image (in GTK Pixbuf format) associated with the
    source file passed to the function. If no thumbnail could be found, 
    the associated icon for the mime type is returned, or if that cannot be
    found, a generic document icon is returned.

    The image is not generated everytime, but only if the thumbnail does not
    exist, or if the source file is newer than the thumbnail.

    @param src_file: Source media file
    @type src_file: unicode
    @param mime_type: mime type of the source file
    @type mime_type: unicode
    @param rectangle: subsection rectangle
    @type rectangle: tuple
    @returns: thumbnail representing the source file
    @rtype: gtk.gdk.Pixbuf
    """
    try:
        filename = get_thumbnail_path(src_file, mtype, rectangle)
        return gtk.gdk.pixbuf_new_from_file(filename)
    except (gobject.GError, OSError):
        if mtype:
            return Mime.find_mime_type_pixbuf(mtype)
        else:
            default = os.path.join(const.IMAGE_DIR, "document.png")
            return gtk.gdk.pixbuf_new_from_file(default)

#-------------------------------------------------------------------------
#
# get_thumbnail_path
#
#-------------------------------------------------------------------------
def get_thumbnail_path(src_file, mtype=None, rectangle=None):
    """
    Returns the path to the thumbnail image associated with the
    source file passed to the function. If the thumbnail does not exist, 
    or if it is older than the source file, we create a new thumbnail image.

    @param src_file: Source media file
    @type src_file: unicode
    @param mime_type: mime type of the source file
    @type mime_type: unicode
    @param rectangle: subsection rectangle
    @type rectangle: tuple
    @returns: thumbnail representing the source file
    @rtype: gtk.gdk.Pixbuf
    """
    filename = __build_thumb_path(src_file, rectangle)
    if not os.path.isfile(src_file):
        return os.path.join(const.IMAGE_DIR, "image-missing.png")
    else:
        if not os.path.isfile(filename):
            __create_thumbnail_image(src_file, mtype, rectangle)
        elif os.path.getmtime(src_file) > os.path.getmtime(filename):
            __create_thumbnail_image(src_file, mtype, rectangle)
        return os.path.abspath(filename)

