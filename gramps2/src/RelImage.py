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
from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import ImgManip
from intl import gettext as _

#-------------------------------------------------------------------------
#
# import_media_object
#
#-------------------------------------------------------------------------
def import_media_object(filename,path,base):
    import shutil

    if not os.path.exists(filename):
        ErrorDialog(_("Could not import %s\nThe file has been moved or deleted") % filename)
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
            ErrorDialog(_("Could not create %s") % thumb + "\n" + str(msg))
            return ""
        except:
            ErrorDialog(_("Could not create %s") % thumb)
            return ""
        
        try:
            path = "%s/%s.jpg" % (thumb,base)
            mk_thumb(filename,path,const.thumbScale)
        except:
            ErrorDialog(_("Error creating the thumbnail : %s"))
            return ""

        try:
            shutil.copy(filename,name)
        except IOError,msg:
            ErrorDialog(_("Error copying %s") % filename + "\n" + msg)
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
    try:
        image1 = gtk.gdk.pixbuf_new_from_file(path)
    except:
        GnomeWarningDialog(_("Could not load image file %s") % path)
        return gtk.gdk.pixbuf_new_from_file(const.icon)
    
    width  = image1.get_width()
    height = image1.get_height()

    scale = size / float(max(width,height))
    try:
        image1.scale_simple(int(scale*width), int(scale*height), gtk.gdk.INTERP_BILINEAR)
        return image1
    except:
        GnomeWarningDialog(_("Could not load image file %s") % path)
        return gtk.gdk.pixbuf_new_from_file(const.icon)

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
        ErrorDialog(_("Could not create %s") % dir + "\n" + str(msg))
        return
    except:
        ErrorDialog(_("Could not create %s") % dir)
        return

    if os.path.exists(dest):
        try:
            os.remove(dest)
        except IOError,msg:
            errmsg = _("Could not replace %s") % dir
            ErrorDialog(errmsg + "\n" + msg)
            return

    if not os.path.exists(source):
        ErrorDialog(_("Could not create a thumbnail for %s\nThe file has been moved or deleted") % source)

    try:
        img = ImgManip.ImgManip(source)
        img.jpg_thumbnail(dest,size,size)
    except:
        import sys
        msg = "%s\n%s %s" % (source,sys.exc_type,sys.exc_value)
        ErrorDialog(_("Could not create a thumbnail for %s") % msg)
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


