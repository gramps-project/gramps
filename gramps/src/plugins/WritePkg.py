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

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import time
import os
from cStringIO import StringIO

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import libglade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from RelLib import *

import WriteXML
import TarFile
import Utils

import intl
_ = intl.gettext

#-------------------------------------------------------------------------
#
# writeData
#
#-------------------------------------------------------------------------
def writeData(database,person):
    try:
        PackageWriter(database)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()
    
#-------------------------------------------------------------------------
#
# PackageWriter
#
#-------------------------------------------------------------------------
class PackageWriter:

    def __init__(self,database):
        self.db = database
        
        base = os.path.dirname(__file__)
        glade_file = "%s/%s" % (base,"pkgexport.glade")
        
        
        dic = {
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_ok_clicked" : self.on_ok_clicked
            }
        
        self.top = libglade.GladeXML(glade_file,"packageExport")
        self.top.signal_autoconnect(dic)
        self.top.get_widget("packageExport").show()

    def on_ok_clicked(self,obj):
        name = self.top.get_widget("filename").get_text()
        Utils.destroy_passed_object(obj)
        self.export(name)

    def export(self, filename):

        t = TarFile.TarFile(filename)
        g = StringIO()
        
        gfile = WriteXML.XmlWriter(self.db,None,1)
        gfile.write_handle(g)
        mtime = time.time()
        t.add_file("data.gramps",mtime,g)
        g.close()

        for f in self.db.getPersonMap().values():
            for p in f.getPhotoList():
                object = p.getReference()
                base = os.path.basename(object.getPath())
                try:
                    g = open(object.getPath(),"rb")
                    t.add_file(base,mtime,g)
                    g.close()
                except:
                    pass
        for f in self.db.getFamilyMap().values():
            for p in f.getPhotoList():
                object = p.getReference()
                base = os.path.basename(object.getPath())
                try:
                    g = open(object.getPath(),"rb")
                    t.add_file(base,mtime,g)
                    g.close()
                except:
                    pass
        for f in self.db.getSourceMap().values():
            for p in f.getPhotoList():
                object = p.getReference()
                base = os.path.basename(object.getPath())
                try:
                    g = open(object.getPath(),"rb")
                    t.add_file(base,mtime,g)
                    g.close()
                except:
                    pass
        for f in self.db.getPlaceMap().values():
            for p in f.getPhotoList():
                object = p.getReference()
                base = os.path.basename(object.getPath())
                try:
                    g = open(object.getPath(),"rb")
                    t.add_file(base,mtime,g)
                    g.close()
                except:
                    pass
        t.close()
    
#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
from Plugins import register_export

register_export(writeData,_("Export to GRAMPS package"))
