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

_ = intl.gettext

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
        GnomeErrorDialog(_("Currently only JPEG files are supported"))
        return None
        
    for index in range(0,1000):
        base = "%s_%d.jpg" % (prefix,index)
        name = path + os.sep + base
        if os.path.exists(name) == 0:
            break

    try:
        if type == "image/jpeg":
            shutil.copy(filename,name)
        else:
            cmd = const.convert + " " + filename + " " + name
            os.system(cmd)
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
    
    image1 = GdkImlib.Image(path)
    width  = image1.rgb_width
    height = image1.rgb_height

    scale = size / float(max(width,height))
    image2 = image1.clone_scaled_image(int(scale*width), int(scale*height))
    return image2
