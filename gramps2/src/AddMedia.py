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
import GrampsMime

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
            "on_fname_update_preview" : self.on_name_changed,
            "on_help_imagesel_clicked" : self.on_help_imagesel_clicked,
            })
        
        self.window.show()

    def on_help_imagesel_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-quick')
        self.val = self.window.run()

    def on_savephoto_clicked(self):
        """
        Callback function called with the save button is pressed.
        A new media object is created, and added to the database.
        """
        filename = self.file_text.get_filename()
        description = unicode(self.description.get_text())
        
        if os.path.exists(filename) == 0:
            msgstr = _("Cannot import %s")
            msgstr2 = _("The filename supplied could not be found.")
            ErrorDialog(msgstr % filename, msgstr2)
            return

        mtype = GrampsMime.get_type(filename)
        if description == "":
            description = os.path.basename(filename)

        mobj = RelLib.MediaObject()
        mobj.set_description(description)
        mobj.set_mime_type(mtype)

        trans = self.db.transaction_begin()
        self.db.add_object(mobj,trans)
        
        name = filename
        mobj.set_path(name)

        self.object = mobj
        self.db.commit_media_object(mobj,trans)
        self.db.transaction_commit(trans,_("Add Media Object"))
        if self.update:
            self.update()
        
    def on_name_changed(self,*obj):
        """
        Called anytime the filename text window changes. Checks to
        see if the file exists. If it does, the imgae is loaded into
        the preview window.
        """
        filename = unicode(self.file_text.get_filename())
        basename = os.path.basename(filename)
        (root,ext) = os.path.splitext(basename)
        old_title  = unicode(self.description.get_text())

        if old_title == '' or old_title == self.temp_name:
            self.description.set_text(root)
        self.temp_name = root

        if os.path.isfile(filename):
            mtype = GrampsMime.get_type(filename)
            
            if mtype[0:5] == "image":
                image = RelImage.scale_image(filename,const.thumbScale)
            else:
                image = gtk.gdk.pixbuf_new_from_file(Utils.find_icon(mtype))
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
        return None
