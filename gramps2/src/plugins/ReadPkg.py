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

#
# Written by Alex Roitman, largely based on ReadNative.py by Don Allingham 
#

"Import from Gramps package"

from ReadXML import *
import Utils
from gettext import gettext as _
import gtk
import const
import os
from QuestionDialog import ErrorDialog, WarningDialog
import TarFile

_title_string = _("Import from GRAMPS package")
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def readData(database,active_person,cb):
    ReadPkg(database,active_person,cb)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class ReadPkg:
    def __init__(self,database,active_person,cb):
        self.db = database
        self.callback = cb
        
        self.top = gtk.FileSelection("%s - GRAMPS" % _title_string)
        self.top.hide_fileop_buttons()
        self.top.ok_button.connect('clicked', self.on_ok_clicked)
        self.top.cancel_button.connect('clicked', self.close_window)
        self.top.show()

    def close_window(self,obj):
        self.top.destroy()
        
    def show_display(self):
        self.window = gtk.Window()
        self.window.set_title(_title_string)
        vbox = gtk.VBox()
        self.window.add(vbox)
        label = gtk.Label(_title_string)
        vbox.add(label)
        adj = gtk.Adjustment(lower=0,upper=100)
        self.progress_bar = gtk.ProgressBar(adj)
        vbox.add(self.progress_bar)
        self.window.show_all()
        
    def on_ok_clicked(self,obj):

        name = self.top.get_filename()
        if name == "":
            return

        Utils.destroy_passed_object(self.top)
        self.show_display()

        # Create tempdir, if it does not exist, then check for writability
        tmpdir_path = os.path.expanduser("~/.gramps/tmp" )
        if not os.path.isdir(tmpdir_path):
            try:
                os.mkdir(tmpdir_path,0700)
            except:
                ErrorDialog( _("Could not create temporary directory %s") % 
                                tmpdir_path )
                return
        elif not os.access(tmpdir_path,os.W_OK):
            ErrorDialog( _("Temporary directory %s is not writable") % tmpdir_path )
            return
        else:    # tempdir exists and writable -- clean it up if not empty
	    files = os.listdir(tmpdir_path) ;
            for filename in files:
                os.remove( os.path.join(tmpdir_path,filename) )

        try:
            t = TarFile.ReadTarFile(name,tmpdir_path)
	    t.extract()
	    t.close()
        except:
            ErrorDialog(_("Error extracting into %s") % tmpdir_path )
            return

	dbname = os.path.join(tmpdir_path,const.xmlFile)  

        try:
            importData(self.db,dbname,self.progress)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

        # Clean up tempdir after ourselves
        files = os.listdir(tmpdir_path) 
        for filename in files:
            os.remove(os.path.join(tmpdir_path,filename))

        os.rmdir(tmpdir_path)

        self.window.destroy()
        self.callback(1)

    def progress(self,val):
        self.progress_bar.set_fraction(val)
        while gtk.events_pending():
            gtk.mainiteration()
        
#------------------------------------------------------------------------
#
# Register with the plugin system
#
#------------------------------------------------------------------------
from Plugins import register_import

register_import(readData,_title_string)
