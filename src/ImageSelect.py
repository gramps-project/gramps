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
from gtk import *
from gnome.ui import *
import libglade
import GdkImlib

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import intl
import const
import utils
import Config
from RelLib import *
import RelImage
import Sources

_ = intl.gettext

#-------------------------------------------------------------------------
#
# ImageSelect class
#
#-------------------------------------------------------------------------
class ImageSelect:

    #---------------------------------------------------------------------
    #
    # __init__ - Creates an edit window.  Associates a person with the 
    # window.
    #
    #---------------------------------------------------------------------
    def __init__(self, path, prefix):
        self.path        = path;
        self.prefix      = prefix;
        self.glade       = libglade.GladeXML(const.imageselFile,"imageSelect")
        self.window      = self.glade.get_widget("imageSelect")
        self.fname       = self.glade.get_widget("fname")
        self.image       = self.glade.get_widget("image")
        self.description = self.glade.get_widget("photoDescription")
        self.external    = self.glade.get_widget("private")

        self.glade.signal_autoconnect({
            "on_savephoto_clicked" : self.on_savephoto_clicked,
            "on_name_changed" : self.on_name_changed,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        self.window.editable_enters(self.description)
        self.window.show()

    def on_name_changed(self, obj):
        filename = self.fname.get_text()
        if os.path.isfile(filename):
            image = RelImage.scale_image(filename,const.thumbScale)
            self.image.load_imlib(image)

    def on_savephoto_clicked(self, obj):
        filename = self.glade.get_widget("photosel").get_full_path(0)
        description = self.glade.get_widget("photoDescription").get_text()

        if os.path.exists(filename) == 0:
            return

        if self.external.get_active() == 1:
            if os.path.isfile(filename):
                name = filename
                thumb = "%s%s.thumb%s%s" % (self.path,os.sep,os.sep,os.path.basename(filename))
                RelImage.mk_thumb(filename,thumb,const.thumbScale)
            else:
                return
        else:
            name = RelImage.import_photo(filename,self.path,self.prefix)
            if name == None:
                return
        
        photo = Photo()
        photo.setPath(name)
        photo.setDescription(description)

        self.savephoto(photo)

        utils.modified()
        utils.destroy_passed_object(obj)

    def savephoto(self, photo):
    	assert 0, "The savephoto function must be subclassed"

