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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import os
import const
import intl
from gnome.ui import *

_ = intl.gettext

try:
    import PIL.Image
    no_pil = 0
except:
    no_pil = 1

#-------------------------------------------------------------------------
#
# import_photo
#
#-------------------------------------------------------------------------
def import_photo(filename,path,prefix):
    import gnome.mime
    import shutil

    type = gnome.mime.type_of_file(filename)
    if type[0:6] != "image/":
        GnomeErrorDialog(_("Currently only image files are supported"))
        return None
        
    for index in range(0,1000):
        base = "%s_%d.jpg" % (prefix,index)
        name = path + os.sep + base
        if os.path.exists(name) == 0:
            break

    thumb = path+os.sep+".thumb"

    try:
        if not os.path.exists(thumb):
            os.mkdir(thumb)
    except IOError,msg:
        GnomeErrorDialog(_("Could not create %s") % thumb + "\n" + str(msg))
    except:
        GnomeErrorDialog(_("Could not create %s") % thumb)
        
    try:
        path = thumb + os.sep + base
        
        mk_thumb(filename,path,const.thumbScale)
        
        if type == "image/jpeg":
            shutil.copy(filename,name)
        else:
            if no_pil:
                cmd = "%s '%s' '%s'" % (const.convert,filename,name)
                os.system(cmd)
            else:
                PIL.Image.open(filename).save(name)
    except:
        return None

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
            print "Creating thumbnail",dest,"from",source
            im = PIL.Image.open(source)
            im.thumbnail((size,size))
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
    


