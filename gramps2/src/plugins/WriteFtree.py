#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003  Donald N. Allingham
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

"Export to Web Family Tree"

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
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import WriteXML
import TarFile
import Utils
from QuestionDialog import MissingMediaDialog

from intl import gettext as _

_title_string = _("Export to Web Family Tree")
#-------------------------------------------------------------------------
#
# writeData
#
#-------------------------------------------------------------------------
def writeData(database,person):
    try:
        FtreeWriter(database)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()
    
#-------------------------------------------------------------------------
#
# FtreeWriter
#
#-------------------------------------------------------------------------
class FtreeWriter:

    def __init__(self,database):
        self.db = database

        base = os.path.dirname(__file__)
        glade_file = "%s/%s" % (base,"pkgexport.glade")
        
        
        dic = {
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_ok_clicked" : self.on_ok_clicked
            }
        
        self.top = gtk.glade.XML(glade_file,"packageExport")

        Utils.set_titles(self.top.get_widget('packageExport'),
                         self.top.get_widget('title'),
                         _title_string)
        
        self.top.signal_autoconnect(dic)
        self.top.get_widget("packageExport").show()

    def on_ok_clicked(self,obj):
        name = self.top.get_widget("filename").get_text()
        Utils.destroy_passed_object(obj)
        try:
            self.export(name)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

    def export(self, filename):

        name_map = {}
        id_map = {}
        id_name = {}
        for key in self.db.getPersonKeys():
            pn = self.db.getPerson(key).getPrimaryName()
            fn = ""
            sn = pn.getSurname()
            items = pn.getFirstName().split()
            if len(items) > 0:
                n = "%s %s" % (items[0],sn)
            else:
                n = sn

            count = -1
            if name_map.has_key(n):
                count = 0
                while 1:
                    nn = "%s%d" % (n,count)
                    if not name_map.has_key(nn):
                        break;
                name_map[nn] = key
                id_map[key] = nn
            else:
                name_map[n] = key
                id_map[key] = n
            id_name[key] = get_name(pn,count)

        f = open(filename,"w")

        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            name = id_name[key]
            father = ""
            mother = ""
            email = ""
            web = ""

            family = p.getMainParents()
            if family:
                if family.getFather():
                    father = id_map[family.getFather().getId()]
                if family.getMother():
                    mother = id_map[family.getMother().getId()]

            #
            # Calculate Date
            #
            birth = p.getBirth().getDateObj()
            death = p.getDeath().getDateObj()

            if birth.isValid():
                if death.isValid():
                    dates = "%s-%s" % (fdate(birth),fdate(death))
                else:
                    dates = fdate(birth)
            else:
                if death.isValid():
                    dates = fdate(death)
                else:
                    dates = ""
                        
            f.write('%s;%s;%s;%s;%s;%s\n' % (name,father,mother,email,web,dates))
            
        f.close()

def fdate(val):
    if val.getYearValid():
        if val.getMonthValid():
            if val.getDayValid():
                return "%d/%d/%d" % (val.getDay(),val.getMonth(),val.getYear())
            else:
                return "%d/%d" % (val.getMonth(),val.getYear())
        else:
            return "%d" % val.getYear()
    else:
        return ""

def get_name(name,count):
    """returns a name string built from the components of the Name
    instance, in the form of Firstname Surname"""
    if count == -1:
        val = ""
    else:
        val = str(count)
        
    if (name.Suffix == ""):
        if name.Prefix:
            return "%s %s %s%s" % (name.FirstName, name.Prefix, name.Surname, val)
        else:
            return "%s %s%s" % (name.FirstName, name.Surname, val)
    else:
        if name.Prefix:
            return "%s %s %s%s, %s" % (name.FirstName, name.Prefix, name.Surname, val, name.Suffix)
        else:
            return "%s %s%s, %s" % (name.FirstName, name.Surname, val, name.Suffix)

#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
from Plugins import register_export

register_export(writeData,_title_string)
