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

#
# Modified by Alex Roitman to handle media object files.
#

"Import from Gramps database"

from ReadXML import *
import Utils
from gettext import gettext as _
import gtk
import const
import os

_title_string = _("Import from GRAMPS database")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def readData(database,active_person,cb):
    ReadNative(database,active_person,cb)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class ReadNative:
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

        imp_dbpath = self.top.get_filename()
        if imp_dbpath == "":
            return

        Utils.destroy_passed_object(self.top)
        self.show_display()

	dbname = os.path.join(imp_dbpath,const.xmlFile)  

        try:
            importData(self.db,dbname,self.progress)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()
        
	self.window.destroy()
        self.callback()

    def progress(self,val):
        self.progress_bar.set_fraction(val)
        while gtk.events_pending():
            gtk.mainiteration()
        
#------------------------------------------------------------------------
#
#  Register with the plugin system
#
#------------------------------------------------------------------------
from Plugins import register_import

register_import(readData,_title_string)
