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

"Import from Gramps"

from ReadXML import *
import Utils
import intl
import gtk
import const

_ = intl.gettext

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
        
        self.top = gtk.GtkFileSelection("%s - GRAMPS" % _("Import from GRAMPS"))
        self.top.hide_fileop_buttons()
        self.top.ok_button.connect('clicked', self.on_ok_clicked)
        self.top.cancel_button.connect_object('clicked', Utils.destroy_passed_object,self.top)
        self.top.show()

    def show_display(self):
        self.window = gtk.GtkWindow(title=_("Import from GRAMPS"))
        vbox = gtk.GtkVBox()
        self.window.add(vbox)
        label = gtk.GtkLabel(_("Import from GRAMPS"))
        vbox.add(label)
        adj = gtk.GtkAdjustment(lower=0,upper=100)
        self.progress_bar = gtk.GtkProgressBar(adj)
        vbox.add(self.progress_bar)
        self.window.show_all()
        
    def on_ok_clicked(self,obj):

        name = self.top.get_filename()
        if name == "":
            return

        name = "%s/%s" % (name,const.xmlFile)
        Utils.destroy_passed_object(self.top)
        self.show_display()
        try:
            importData(self.db,name,self.progress)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()
        self.window.destroy()
        self.callback(1)

    def progress(self,val):
        self.progress_bar.set_value(val*100.0)
        while gtk.events_pending():
            gtk.mainiteration()
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_import

register_import(readData,_("Import from GRAMPS"))

