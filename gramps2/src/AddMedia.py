#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
from QuestionDialog import ErrorDialog, WarningDialog
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib
import Mime
import GrampsDisplay
import ManagedWindow

_last_directory = None

#-------------------------------------------------------------------------
#
# AddMediaObject
#
#-------------------------------------------------------------------------
class AddMediaObject(ManagedWindow.ManagedWindow):
    """
    Displays the Add Media Dialog window, allowing the user to select
    a media object from the file system, while providing a description.
    """
    
    def __init__(self,dbstate, uistate, track):
        """
        Creates and displays the dialog box

        db - the database in which the new object is to be stored
        """

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.db = dbstate.db
        self.glade = gtk.glade.XML(const.gladeFile,"imageSelect","gramps")
        
        self.set_window(
            self.glade.get_widget("imageSelect"),
            self.glade.get_widget('title'),
            _('Select a media object'))
            
        self.description = self.glade.get_widget("photoDescription")
        self.image = self.glade.get_widget("image")
        self.file_text = self.glade.get_widget("fname")
        if _last_directory and os.path.isdir(_last_directory):
            self.file_text.set_current_folder(_last_directory)
            
        self.internal = self.glade.get_widget('internal')
        self.internal.connect('toggled',self.internal_toggled)
        self.relpath = self.glade.get_widget('relpath')
        self.temp_name = ""
        self.object = None

        self.glade.get_widget('fname').connect('update_preview',
                                               self.on_name_changed)
        self.show()

    def build_menu_names(self, obj):
        return(_('Select media object'),None)

    def internal_toggled(self, obj):
        self.file_text.set_sensitive(not obj.get_active())
        
    def on_help_imagesel_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-edit-quick')
        self.val = self.window.run()

    def save(self):
        """
        Callback function called with the save button is pressed.
        A new media object is created, and added to the database.
        """
        global _last_directory
        
        description = unicode(self.description.get_text())

        if self.internal.get_active():
            mobj = RelLib.MediaObject()
            mobj.set_description(description)
            mobj.set_handle(Utils.create_id())
            mobj.set_mime_type(None)
        else:
            filename = self.file_text.get_filename()
            full_file = filename

            if self.relpath.get_active():
                p = self.db.get_save_path()
                if not os.path.isdir(p):
                    p = os.path.dirname(p)
                filename = Utils.relative_path(filename,p)

            print os.getcwd(), filename, full_file

            if os.path.exists(filename) == 0:
                msgstr = _("Cannot import %s")
                msgstr2 = _("The filename supplied could not be found.")
                ErrorDialog(msgstr % filename, msgstr2)
                return

            mtype = Mime.get_type(full_file)
            if description == "":
                description = os.path.basename(filename)

            mobj = RelLib.MediaObject()
            mobj.set_description(description)
            mobj.set_mime_type(mtype)
            name = filename
            mobj.set_path(name)
            _last_directory = os.path.dirname(filename)

        mobj.set_handle(Utils.create_id())
        if not mobj.get_gramps_id():
            mobj.set_gramps_id(self.db.find_next_object_gramps_id())
        trans = self.db.transaction_begin()
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
        
        filename = Utils.find_file( filename)
        if filename:
            mtype = Mime.get_type(filename)
            if mtype and mtype.startswith("image"):
                image = scale_image(filename,const.thumbScale)
            else:
                image = Mime.find_mime_type_pixbuf(mtype)
            self.image.set_from_pixbuf(image)

    def run(self):
        while True:
            val = self.window.run()

            if val == gtk.RESPONSE_OK:
                self.save()
                self.close()
                return self.object
            elif val == gtk.RESPONSE_HELP: 
                self.on_help_imagesel_clicked(None)
            else:
                self.close()
                return None
        return None

#-------------------------------------------------------------------------
#
# scale_image
#
#-------------------------------------------------------------------------
def scale_image(path,size):

    title_msg = _("Cannot display %s") % path
    detail_msg =  _('GRAMPS is not able to display the image file. '
                    'This may be caused by a corrupt file.')
    
    try:
        image1 = gtk.gdk.pixbuf_new_from_file(path)
        width  = image1.get_width()
        height = image1.get_height()
        
        scale = size / float(max(width,height))
        return image1.scale_simple(int(scale*width), int(scale*height),
                                   gtk.gdk.INTERP_BILINEAR)
    except:
        WarningDialog(title_msg, detail_msg)
        return gtk.gdk.pixbuf_new_from_file(const.icon)
    
