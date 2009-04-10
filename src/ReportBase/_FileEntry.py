#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2009       Brian G. Matherly
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

# $Id:_FileEntry.py 9912 2008-01-22 09:17:46Z acraphae $

import os
import gtk
import Utils

class FileEntry(gtk.HBox):
    """ A widget that allows the user to select a file from the file system """
    def __init__(self, defname, title):
        gtk.HBox.__init__(self)

        self.title = title
        self.dir = False
        self.__base_path = ""
        self.__file_name = ""
        self.entry = gtk.Entry()
        self.entry.set_text(defname)
        self.set_filename(defname)
        self.set_spacing(6)
        self.set_homogeneous(False)
        self.button = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
        self.button.add(image)
        self.button.connect('clicked', self.__select_file)
        self.pack_start(self.entry, True, True)
        self.pack_end(self.button, False, False)

    def __select_file(self, obj):
        """ Call back function to handle the open button press """
        if self.dir:
            my_action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
        else:
            my_action = gtk.FILE_CHOOSER_ACTION_SAVE
        
        dialog = gtk.FileChooserDialog(self.title,
                                       action=my_action,
                                       buttons=(gtk.STOCK_CANCEL,
                                                gtk.RESPONSE_CANCEL,
                                                gtk.STOCK_OPEN,
                                                gtk.RESPONSE_OK))

        name = os.path.basename(self.entry.get_text())
        if self.dir:
            if os.path.isdir(name):
                dialog.set_current_name(name)
            elif os.path.isdir(os.path.basename(name)):
                dialog.set_current_name(os.path.basename(name))
        else:
            dialog.set_current_name(name)
        dialog.set_current_folder(self.__base_path)
        dialog.present()
        status = dialog.run()
        if status == gtk.RESPONSE_OK:
            self.set_filename(Utils.get_unicode_path(dialog.get_filename()))
        dialog.destroy()

    def set_filename(self, path):
        """ Set the currently selected dialog. """
        if not path:
            return
        if os.path.dirname(path):
            self.__base_path = os.path.dirname(path)
            self.__file_name = os.path.basename(path)
        else:
            self.__base_path = os.getcwd()
            self.__file_name = path
        self.entry.set_text(os.path.join(self.__base_path, self.__file_name))

    def get_full_path(self, val):
        """ Get the full path of the currently selected file. """
        return self.entry.get_text()

    def set_directory_entry(self, opt):
        """ 
        Configure the FileEntry to either select a directory or a file. 
        Set it to True to select a directory.
        Set it to False to select a file.
        """
        self.dir = opt
