#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

# $Id$

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

from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from QuestionDialog import ErrorDialog
import gtk.glade
import gnome

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
    
    def __init__(self,db,update=None):
        """
        Creates and displays the dialog box

        db - the database in which the new object is to be stored
        update - a function to call to update the display
        """
        self.db = db
        self.glade = gtk.glade.XML(const.imageselFile,"imageSelect","gramps")
        self.window = self.glade.get_widget("imageSelect")
        self.description = self.glade.get_widget("photoDescription")
        self.image = self.glade.get_widget("image")
        self.file_text = self.glade.get_widget("fname")
        self.update = update
        self.temp_name = ""
        self.object = None

        Utils.set_titles(self.window,self.glade.get_widget('title'),
                         _('Select a media object'))
        
        self.glade.signal_autoconnect({
            "on_name_changed"       : self.on_name_changed,
            })
        
        self.window.show()

    def on_help_imagesel_clicked(self):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-quick')

    def on_savephoto_clicked(self):
        """
        Callback function called with the save button is pressed.
        A new media object is created, and added to the database.
        """
        filename = self.glade.get_widget("photosel").get_full_path(0)
        description = unicode(self.description.get_text())
        external = self.glade.get_widget("private")
        
        if os.path.exists(filename) == 0:
            msgstr = _("Cannot import %s")
            msgstr2 = _("The filename supplied could not be found.")
            ErrorDialog(msgstr % filename, msgstr2)
            return

        type = Utils.get_mime_type(filename)
        if description == "":
            description = os.path.basename(filename)

        mobj = RelLib.MediaObject()
        mobj.set_description(description)
        mobj.set_mime_type(type)
        self.db.add_object(mobj)
        
        if external.get_active() == 0:
            path = self.db.get_save_path()
            name = RelImage.import_media_object(filename,path,mobj.get_id())
            mobj.set_local(1)
        else:
            name = filename
        mobj.set_path(name)

        if self.update:
            self.update()
        self.object = mobj
        self.db.commit_media_object(mobj)
        
    def on_name_changed(self,obj):
        """
        Called anytime the filename text window changes. Checks to
        see if the file exists. If it does, the imgae is loaded into
        the preview window.
        """
        filename = unicode(self.file_text.get_text())
        basename = os.path.basename(filename)
        (root,ext) = os.path.splitext(basename)
        old_title  = unicode(self.description.get_text())

        if old_title == '' or old_title == self.temp_name:
            self.description.set_text(root)
        self.temp_name = root

        if os.path.isfile(filename):
            type = Utils.get_mime_type(filename)

            if type[0:5] == "image":
                image = RelImage.scale_image(filename,const.thumbScale)
            else:
                image = gtk.gdk.pixbuf_new_from_file(Utils.find_icon(type))
            self.image.set_from_pixbuf(image)

    def run(self):
        while 1:
            val = self.window.run()

            if val == gtk.RESPONSE_OK:
                self.on_savephoto_clicked()
                self.window.destroy()
                return self.object
            elif val == gtk.RESPONSE_HELP: 
                self.on_help_imagesel_clicked()
            else:
                self.window.destroy()
                return None
