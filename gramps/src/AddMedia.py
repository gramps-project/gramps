#! /usr/bin/python -O
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

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------

from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
#from gtk import *
from gnome.ui import GnomeErrorDialog
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import utils
import RelImage
from RelLib import Photo

class AddMediaObject:

    def __init__(self,db,update):
        self.db = db
        self.glade       = libglade.GladeXML(const.imageselFile,"imageSelect")
        self.window      = self.glade.get_widget("imageSelect")
        self.description = self.glade.get_widget("photoDescription")
        self.image       = self.glade.get_widget("image")
        self.update      = update
        
        self.glade.signal_autoconnect({
            "on_savephoto_clicked"  : self.on_savephoto_clicked,
            "on_name_changed"       : self.on_name_changed,
            "destroy_passed_object" : utils.destroy_passed_object
            })
        
        self.window.editable_enters(self.description)
        self.window.show()

    def on_savephoto_clicked(self,obj):
        filename = self.glade.get_widget("photosel").get_full_path(0)
        description = self.description.get_text()
        external = self.glade.get_widget("private")
        
        if os.path.exists(filename) == 0:
            err = _("%s is not a valid file name or does not exist.") % filename
            GnomeErrorDialog(err)
            return

        type = utils.get_mime_type(filename)
        mobj = Photo()
        if description == "":
            description = os.path.basename(filename)
        mobj.setDescription(description)
        mobj.setMimeType(type)
        self.db.addObject(mobj)
        
        if external.get_active() == 0:
            path = self.db.getSavePath()
            name = RelImage.import_media_object(filename,path,mobj.getId())
        else:
            name = filename
        mobj.setPath(name)

        utils.modified()
        self.update()
        utils.destroy_passed_object(obj)
        
    def on_name_changed(self,obj):
        filename = self.glade.get_widget("fname").get_text()
        if os.path.isfile(filename):
            type = utils.get_mime_type(filename)
            if type[0:5] == "image":
                image = RelImage.scale_image(filename,const.thumbScale)
                self.image.load_imlib(image)
            else:
                self.image.load_file(utils.find_icon(type))
