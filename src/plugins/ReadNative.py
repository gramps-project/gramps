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

import libglade
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
def progress(val):
    pass

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

    def on_ok_clicked(self,obj):

        name = self.top.get_filename()
        if name == "":
            return

        name = "%s/%s" % (name,const.indexFile)
        Utils.destroy_passed_object(self.top)
        importData(self.db,name,progress)
        self.callback(1)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_import

register_import(readData,_("Import from GRAMPS"))

