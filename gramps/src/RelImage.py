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
from gnome.ui import GnomeErrorDialog, GnomeWarningDialog

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import const
import utils
from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# Check for the python imaging library
#
#-------------------------------------------------------------------------
try:
    import PIL.Image
    no_pil = 0
except:
    no_pil = 1

#-------------------------------------------------------------------------
#
# import_media_object
#
#-------------------------------------------------------------------------
def import_media_object(filename,path,base):
    import shutil

    type = utils.get_mime_type(filename)
    if type[0:5] == "image":
        name = "%s/%s.jpg" % (path,base)
        base = "%s.jpg" % (base)

        thumb = "%s/.thumb" % (path)

        try:
            if not os.path.exists(thumb):
                os.mkdir(thumb)
        except IOError,msg:
            GnomeErrorDialog(_("Could not create %s") % thumb + "\n" + str(msg))
        except:
            GnomeErrorDialog(_("Could not create %s") % thumb)
        
        try:
            path = "%s/%s" % (thumb,base)

            print filename,path,const.thumbScale
            mk_thumb(filename,path,const.thumbScale)
            shutil.copy(filename,name)
        except:
            return None
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
        return
    
    width  = image1.rgb_width
    height = image1.rgb_height

    scale = size / float(max(width,height))
    image2 = image1.clone_scaled_image(int(scale*width), int(scale*height))
    return image2

#-------------------------------------------------------------------------
#
# scale_image
#
#-------------------------------------------------------------------------
def mk_thumb(source,dest,size):

    dir = os.path.dirname(dest)
    try:
        if not os.path.exists(dir):
            os.mkdir(dir)
    except IOError,msg:
        GnomeErrorDialog(_("Could not create %s") % dir + "\n" + str(msg))
        return
    except:
        GnomeErrorDialog(_("Could not create %s") % dir)
        return

    if no_pil:
        cmd = "%s -geometry %dx%d '%s' '%s'" % (const.convert,size,size,source,dest)
        os.system(cmd)
    else:
        try:
            im = PIL.Image.open(source)
            im.thumbnail((size,size))
            if im.mode != 'RGB':
                im.draft('RGB',im.size)
                im = im.convert("RGB")
            im.save(dest,"JPEG")
        except:
            pass

#-------------------------------------------------------------------------
#
# scale_image
#
#-------------------------------------------------------------------------
def check_thumb(source,dest,size):
    if not os.path.isfile(source):
        return
    if not os.path.isfile(dest):
        mk_thumb(source,dest,size)
    elif os.path.getmtime(source) > os.path.getmtime(dest):
        mk_thumb(source,dest,size)
    


