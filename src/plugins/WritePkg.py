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

"Export to GRAMPS package"

from RelLib import *

import const
import WriteXML
import time
import os
import TarFile
import utils
import libglade

from cStringIO import StringIO
import intl
_ = intl.gettext

def writeData(database,person):
    global db
    global topDialog
    global active_person
    
    db = database
    active_person = person
    
    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "pkgexport.glade"
        
    dic = {
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_ok_clicked" : on_ok_clicked
        }

    topDialog = libglade.GladeXML(glade_file,"packageExport")
    topDialog.signal_autoconnect(dic)

    topDialog.get_widget("packageExport").show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    global db
    global topDialog
    
    name = topDialog.get_widget("filename").get_text()
    utils.destroy_passed_object(obj)
    exportData(db,name)

def callback(a):
    pass

def exportData(database, filename):

    t = TarFile.TarFile(filename)
    g = StringIO()
    WriteXML.write_xml_data(database,g,callback,1)
    mtime = time.time()
    t.add_file("data.gramps",mtime,g)
    g.close()

    for f in database.getPersonMap().values():
        for p in f.getPhotoList():
            base = os.path.basename(p.getPath())
            try:
                g = open(p.getPath(),"rb")
                t.add_file(base,mtime,g)
                g.close()
            except:
                pass
    for f in database.getFamilyMap().values():
        for p in f.getPhotoList():
            base = os.path.basename(p.getPath())
            try:
                g = open(p.getPath(),"rb")
                t.add_file(base,mtime,g)
                g.close()
            except:
                pass
    for f in database.getSourceMap().values():
        for p in f.getPhotoList():
            base = os.path.basename(p.getPath())
            try:
                g = open(p.getPath(),"rb")
                t.add_file(base,mtime,g)
                g.close()
            except:
                pass
    for f in database.getPlaceMap().values():
        for p in f.getPhotoList():
            base = os.path.basename(p.getPath())
            try:
                g = open(p.getPath(),"rb")
                t.add_file(base,mtime,g)
                g.close()
            except:
                pass
            
    t.close()
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_export

register_export(writeData,_("Export to GRAMPS package"))
