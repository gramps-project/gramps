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
import sys

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
import Config
import Utils
import gen.lib
import Mime
import GrampsDisplay
import ManagedWindow

#-------------------------------------------------------------------------
#
# global variables
#
#-------------------------------------------------------------------------



#-------------------------------------------------------------------------
#
# AddMediaObject
#
#-------------------------------------------------------------------------
class AddMediaObject(ManagedWindow.ManagedWindow):
    """
    Displays the Add Media Dialog window, allowing the user to select
    a file from the file system, while providing a description.
    """
    
    def __init__(self, dbstate, uistate, track, mediaobj, callback=None):
        """
        Creates and displays the dialog box

        db - the database in which the new object is to be stored
        The mediaobject is updated with the information, and on save, the 
        callback function is called
        """
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.dbase = dbstate.db
        self.obj = mediaobj
        self.callback = callback

        self.last_directory = Config.get(Config.ADDMEDIA_IMGDIR)
        self.relative_path  = Config.get(Config.ADDMEDIA_RELPATH)

        self.glade = gtk.glade.XML(const.GLADE_FILE, "imageSelect", "gramps")
        
        self.set_window(
            self.glade.get_widget("imageSelect"),
            self.glade.get_widget('title'),
            _('Select a media object'))
            
        self.description = self.glade.get_widget("photoDescription")
        self.image = self.glade.get_widget("image")
        self.file_text = self.glade.get_widget("fname")
        if not(self.last_directory and os.path.isdir(self.last_directory)):
            self.last_directory = const.HOME_DIR
        print 'test', self.last_directory
        self.file_text.set_current_folder(self.last_directory)

        self.relpath = self.glade.get_widget('relpath')
        self.relpath.set_active(self.relative_path)
        self.temp_name = ""
        self.object = None

        self.glade.get_widget('fname').connect('update_preview',
                                               self.on_name_changed)
        self.ok_button = self.glade.get_widget('button79')
        self.help_button = self.glade.get_widget('button103')
        self.cancel_button = self.glade.get_widget('button81')
        self.ok_button.connect('clicked',self.save)
        self.ok_button.set_sensitive(not self.dbase.readonly)
        self.help_button.connect('clicked', lambda x: GrampsDisplay.help(
                                                        'gramps-edit-quick'))
        self.cancel_button.connect('clicked', self.close)
        self.show()
        self.modal_call()

    def build_menu_names(self, obj):
        """
        Build the menu name for the window manager
        """
        return(_('Select media object'), None)

    def save(self, *obj):
        """
        Callback function called with the save button is pressed.
        The media object is updated, and callback called
        """
        description = unicode(self.description.get_text())

        if self.file_text.get_filename() is None:
            msgstr = _("Import failed")
            msgstr2 = _("The filename supplied could not be found.")
            ErrorDialog(msgstr, msgstr2)
            return

        filename = Utils.get_unicode_path(self.file_text.get_filename())
        full_file = filename

        pname = self.dbase.get_save_path()
        if not os.path.isdir(pname):
            pname = os.path.dirname(pname)
                
        if self.relpath.get_active():
            filename = Utils.relative_path(filename, pname)

        if os.path.exists(pname) == 0:
            msgstr = _("Cannot import %s")
            msgstr2 = _("The filename supplied could not be found.")
            ErrorDialog(msgstr % filename, msgstr2)
            return

        mtype = Mime.get_type(full_file)
        if description == "":
            description = os.path.basename(filename)

        self.obj.set_description(description)
        self.obj.set_mime_type(mtype)
        name = filename
        self.obj.set_path(name)
        
        self.last_directory = os.path.dirname(full_file)
        self.relative_path = self.relpath.get_active()

        self._cleanup_on_exit()
        if self.callback:
            self.callback(self.obj)

    def on_name_changed(self, *obj):
        """
        Called anytime the filename text window changes. Checks to
        see if the file exists. If it does, the imgae is loaded into
        the preview window.
        """
        fname = self.file_text.get_filename()
        if not fname:
            return
        filename = Utils.get_unicode_path(fname)
        basename = os.path.basename(filename)
        (root, ext) = os.path.splitext(basename)
        old_title  = unicode(self.description.get_text())

        if old_title == '' or old_title == self.temp_name:
            self.description.set_text(root)
        self.temp_name = root
        
        filename = Utils.find_file( filename)
        if filename:
            mtype = Mime.get_type(filename)
            if mtype and mtype.startswith("image"):
                image = scale_image(filename, const.THUMBSCALE)
            else:
                image = Mime.find_mime_type_pixbuf(mtype)
            self.image.set_from_pixbuf(image)

    def _cleanup_on_exit(self):
        Config.set(Config.ADDMEDIA_IMGDIR, self.last_directory)
        Config.set(Config.ADDMEDIA_RELPATH, self.relative_path)
        Config.sync()

#-------------------------------------------------------------------------
#
# scale_image
#
#-------------------------------------------------------------------------
def scale_image(path, size):
    """
    Scales the image to the specified size
    """

    title_msg = _("Cannot display %s") % path
    detail_msg =  _('GRAMPS is not able to display the image file. '
                    'This may be caused by a corrupt file.')
    
    try:
        image1 = gtk.gdk.pixbuf_new_from_file(path)
        width  = image1.get_width()
        height = image1.get_height()
        
        scale = size / float(max(width, height))
        return image1.scale_simple(int(scale*width), int(scale*height),
                                   gtk.gdk.INTERP_BILINEAR)
    except:
        WarningDialog(title_msg, detail_msg)
        return gtk.gdk.pixbuf_new_from_file(const.ICON)
    
