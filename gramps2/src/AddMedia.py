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
import gc

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
import GrampsDisplay

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
    
    def __init__(self,db):
        """
        Creates and displays the dialog box

        db - the database in which the new object is to be stored
        """
        self.db = db
        self.glade = gtk.glade.XML(const.imageselFile,"imageSelect","gramps")
        self.window = self.glade.get_widget("imageSelect")
        self.description = self.glade.get_widget("photoDescription")
        self.image = self.glade.get_widget("image")
        self.file_text = self.glade.get_widget("fname")
        self.internal = self.glade.get_widget('internal')
        self.internal.connect('toggled',self.internal_toggled)
        self.temp_name = ""
        self.object = None

        Utils.set_titles(self.window,self.glade.get_widget('title'),
                         _('Select a media object'))
        
        self.glade.signal_autoconnect({
            "on_fname_update_preview" : self.on_name_changed,
            "on_help_imagesel_clicked" : self.on_help_imagesel_clicked,
            })
        
        self.window.show()

    def internal_toggled(self, obj):
        self.file_text.set_sensitive(not obj.get_active())
        
    def on_help_imagesel_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-edit-quick')
        self.val = self.window.run()

    def on_savephoto_clicked(self):
        """
        Callback function called with the save button is pressed.
        A new media object is created, and added to the database.
        """

        description = unicode(self.description.get_text())

        if self.internal.get_active():
            mobj = RelLib.MediaObject()
            mobj.set_description(description)
            mobj.set_mime_type(None)
        else:
            filename = self.file_text.get_filename()
        
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
            name = filename
            mobj.set_path(name)

        trans = self.db.transaction_begin()
        self.db.add_object(mobj,trans)
        self.object = mobj
        self.db.commit_media_object(mobj,trans)
        self.db.transaction_commit(trans,_("Add Media Object"))
        
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
            if mtype and mtype.startswith("image"):
                image = RelImage.scale_image(filename,const.thumbScale)
            else:
                image = Utils.find_mime_type_pixbuf(mtype)
            self.image.set_from_pixbuf(image)

    def run(self):
        while True:
            val = self.window.run()

            if val == gtk.RESPONSE_OK:
                self.on_savephoto_clicked()
                self.window.destroy()
                gc.collect()
                return self.object
            elif val == gtk.RESPONSE_HELP: 
                self.on_help_imagesel_clicked(None)
            else:
                self.window.destroy()
                gc.collect()
                return None
        return None
