#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import string

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
from gnome.ui import GnomeErrorDialog, GnomeWarningDialog

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import ImgManip
from intl import gettext
_ = gettext


#-------------------------------------------------------------------------
#
# import_media_object
#
#-------------------------------------------------------------------------
def import_media_object(filename,path,base):
    import shutil

    if not os.path.exists(filename):
        GnomeErrorDialog(_("Could not import %s\nThe file has been moved or deleted") % filename)
        return ""

    ext = os.path.splitext(filename)[1]
    
    type = Utils.get_mime_type(filename)
    if type[0:5] == "image":
        name = "%s/%s%s" % (path,base,ext)
        #base = "%s%s" % (base,ext)

        thumb = "%s/.thumb" % (path)

        try:
            if not os.path.exists(thumb):
                os.mkdir(thumb)
        except IOError,msg:
            GnomeErrorDialog(_("Could not create %s") % thumb + "\n" + str(msg))
            return ""
        except:
            GnomeErrorDialog(_("Could not create %s") % thumb)
            return ""
        
        try:
            path = "%s/%s.jpg" % (thumb,base)
            mk_thumb(filename,path,const.thumbScale)
        except:
            GnomeErrorDialog(_("Error creating the thumbnail : %s"))
            return ""

        try:
            shutil.copy(filename,name)
        except IOError,msg:
            GnomeErrorDialog(_("Error copying %s") % filename + "\n" + msg)
            return ""

    else:
        bname = os.path.basename(filename)
        l = string.split(bname,'.')
        name = "%s/%s.%s" % (path,base,l[-1])
        shutil.copy(filename,name)

    return name

#-------------------------------------------------------------------------
#
# scale_image
#
#-------------------------------------------------------------------------
def scale_image(path,size):
    import GdkImlib

    try:
        image1 = GdkImlib.Image(path)
    except:
        GnomeWarningDialog(_("Could not load image file %s") % path)
        return GdkImlib.Image(const.icon)
    
    width  = image1.rgb_width
    height = image1.rgb_height

    scale = size / float(max(width,height))
    try:
        image2 = image1.clone_scaled_image(int(scale*width), int(scale*height))
    except:
        GnomeWarningDialog(_("Could not load image file %s") % path)
        return GdkImlib.Image(const.icon)

    return image2

#-------------------------------------------------------------------------
#
# scale_image
#
#-------------------------------------------------------------------------
def mk_thumb(source,dest,size):
    dir = os.path.dirname(dest)

    source = os.path.normpath(source)
    dest = os.path.normpath(dest)
    
    try:
        if not os.path.exists(dir):
            os.mkdir(dir)
    except IOError,msg:
        GnomeErrorDialog(_("Could not create %s") % dir + "\n" + str(msg))
        return
    except:
        GnomeErrorDialog(_("Could not create %s") % dir)
        return

    if os.path.exists(dest):
        try:
            os.remove(dest)
        except IOError,msg:
            errmsg = _("Could not replace %s") % dir
            GnomeErrorDialog(errmsg + "\n" + msg)
            return

    if not os.path.exists(source):
        GnomeErrorDialog(_("Could not create a thumbnail for %s\nThe file has been moved or deleted") % source)

    try:
        img = ImgManip.ImgManip(source)
        img.jpg_thumbnail(dest,size,size)
    except:
        import sys
        msg = "%s\n%s %s" % (source,sys.exc_type,sys.exc_value)
        GnomeErrorDialog(_("Could not create a thumbnail for %s") % msg)
        return

#-------------------------------------------------------------------------
#
# scale_image
#
#-------------------------------------------------------------------------
def check_thumb(source,dest,size):
    if not os.path.isfile(source):
        return 0
    if not os.path.isfile(dest):
        mk_thumb(source,dest,size)
    elif os.path.getmtime(source) > os.path.getmtime(dest):
        mk_thumb(source,dest,size)
    return 1


