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

"""
Provides the interface to allow a person to add a media object to the database.
"""

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
from gnome.ui import GnomeErrorDialog
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelImage
import RelLib

#-------------------------------------------------------------------------
#
# AddMediaObject
#
#-------------------------------------------------------------------------
class AddMediaObject:
    """
    Displays the Add Media Dialog window, allowing the user to select
    a media object from the file system, while providing a description.
    """
    
    def __init__(self,db,update):
        """
        Creates and displays the dialog box

        db - the database in which the new object is to be stored
        update - a function to call to update the display
        """
        self.db = db
        self.glade = libglade.GladeXML(const.imageselFile,"imageSelect")
        self.window = self.glade.get_widget("imageSelect")
        self.description = self.glade.get_widget("photoDescription")
        self.image = self.glade.get_widget("image")
        self.file_text = self.glade.get_widget("fname")
        self.update = update
        self.temp_name = ""
        
        self.glade.signal_autoconnect({
            "on_savephoto_clicked"  : self.on_savephoto_clicked,
            "on_name_changed"       : self.on_name_changed,
            "destroy_passed_object" : Utils.destroy_passed_object
            })
        
        self.window.editable_enters(self.description)
        self.window.show()

    def on_savephoto_clicked(self,obj):
        """
        Callback function called with the save button is pressed.
        A new media object is created, and added to the database.
        """
        filename = self.glade.get_widget("photosel").get_full_path(0)
        description = self.description.get_text()
        external = self.glade.get_widget("private")
        
        if os.path.exists(filename) == 0:
            msgstr = _("%s is not a valid file name or does not exist.")
            GnomeErrorDialog(msgstr % filename)
            return

        type = Utils.get_mime_type(filename)
        if description == "":
            description = os.path.basename(filename)

        mobj = RelLib.Photo()
        mobj.setDescription(description)
        mobj.setMimeType(type)
        self.db.addObject(mobj)
        
        if external.get_active() == 0:
            path = self.db.getSavePath()
            name = RelImage.import_media_object(filename,path,mobj.getId())
            mobj.setLocal(1)
        else:
            name = filename
        mobj.setPath(name)

        Utils.modified()
        self.update()
        Utils.destroy_passed_object(obj)
        
    def on_name_changed(self,obj):
        """
        Called anytime the filename text window changes. Checks to
        see if the file exists. If it does, the imgae is loaded into
        the preview window.
        """
        filename = self.file_text.get_text()
        basename = os.path.basename(filename)
        (root,ext) = os.path.splitext(basename)
        old_title  = self.description.get_text()

        if old_title == '' or old_title == self.temp_name:
            self.description.set_text(root)
        self.temp_name = root

        if os.path.isfile(filename):
            type = Utils.get_mime_type(filename)
            if type[0:5] == 'image':
                image = RelImage.scale_image(filename,const.thumbScale)
                self.image.load_imlib(image)
            else:
                self.image.load_file(Utils.find_icon(type))
