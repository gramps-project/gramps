#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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

import os
import gtk

class FileEntry(gtk.HBox):
    def __init__(self,defname,title):
        gtk.HBox.__init__(self)

        self.title = title
        self.dir = False
        self.entry = gtk.Entry()
        self.entry.set_text(defname)
        self.set_filename(defname)
        self.set_spacing(6)
        self.set_homogeneous(False)
        self.button = gtk.Button()
        im = gtk.Image()
        im.set_from_stock(gtk.STOCK_OPEN,gtk.ICON_SIZE_BUTTON)
        self.button.add(im)
        self.button.connect('clicked',self.select_file)
        self.pack_start(self.entry,True,True)
        self.pack_end(self.button,False,False)

    def select_file(self,obj):
        if self.dir:
            my_action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
        else:
            my_action = gtk.FILE_CHOOSER_ACTION_SAVE
        
        f = gtk.FileChooserDialog(self.title,
                                  action=my_action,
                                  buttons=(gtk.STOCK_CANCEL,
                                           gtk.RESPONSE_CANCEL,
                                           gtk.STOCK_OPEN,
                                           gtk.RESPONSE_OK))

        name = os.path.basename(self.entry.get_text())
        if self.dir:
            if os.path.isdir(name):
                f.set_current_name(name)
            elif os.path.isdir(os.path.basename(name)):
                f.set_current_name(os.path.basename(name))
        else:
            f.set_current_name(name)
        f.set_current_folder(self.spath)
        f.present()
        status = f.run()
        if status == gtk.RESPONSE_OK:
            self.set_filename(f.get_filename())
        f.destroy()

    def set_filename(self,path):
        if not path:
            return
        if os.path.dirname(path):
            self.spath = os.path.dirname(path)
            self.defname = os.path.basename(path)

        else:
            self.spath = os.getcwd()
            self.defname = path
        self.entry.set_text(os.path.join(self.spath,self.defname))

    def gtk_entry(self):
        return self.entry

    def get_full_path(self,val):
        return self.entry.get_text()

    def set_directory_entry(self,opt):
        self.dir = opt
