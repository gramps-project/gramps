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
    global db
    global topDialog
    global callback
    global glade_file

    db = database
    callback = cb
    
    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "grampsimport.glade"
        
    dic = {
        "destroy_passed_object" : Utils.destroy_passed_object,
        "on_ok_clicked" : on_ok_clicked
        }

    topDialog = libglade.GladeXML(glade_file,"grampsImport")
    topDialog.signal_autoconnect(dic)
    topDialog.get_widget("grampsImport").show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    global db
    global topDialog

    import const
    
    if topDialog.get_widget("new").get_active():
        db.new()

    name = topDialog.get_widget("filename").get_text()
    name = name + os.sep + const.indexFile

    Utils.destroy_passed_object(obj)
    importData(db,name,progress)
    callback(1)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_import

register_import(readData,_("Import from GRAMPS"))

