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

# $Id$

"Export to Web Family Tree"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os
from cStringIO import StringIO

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Utils
import GenericFilter
import Errors

from QuestionDialog import MissingMediaDialog, ErrorDialog

from gettext import gettext as _

_title_string = _("Export to Web Family Tree")

#-------------------------------------------------------------------------
#
# writeData
#
#-------------------------------------------------------------------------
def writeData(database,person):
    try:
        FtreeWriter(database,person)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()
    
#-------------------------------------------------------------------------
#
# FtreeWriter
#
#-------------------------------------------------------------------------
class FtreeWriter:

    def __init__(self,database,person,cl=0,name=""):
        self.db = database
        self.person = person
        self.plist = {}

        if cl:
            if name:
                self.export(name,None,0)
        else:
            base = os.path.dirname(__file__)
            glade_file = "%s/%s" % (base,"writeftree.glade")
        
            dic = {
                "destroy_passed_object" : self.close,
                "on_ok_clicked" : self.on_ok_clicked,
                "on_help_clicked" : self.on_help_clicked,
                }

            self.top = gtk.glade.XML(glade_file,"top","gramps")

            Utils.set_titles(self.top.get_widget('top'),
                         self.top.get_widget('title'),
                         _title_string)
        
            self.top.signal_autoconnect(dic)

            self.topwin = self.top.get_widget("top")
            self.restrict = self.top.get_widget("restrict")
            self.filter = self.top.get_widget("filter")

            all = GenericFilter.GenericFilter()
            all.set_name(_("Entire Database"))
            all.add_rule(GenericFilter.Everyone([]))
        
            des = GenericFilter.GenericFilter()
            des.set_name(_("Descendants of %s") % person.getPrimaryName().getName())
            des.add_rule(GenericFilter.IsDescendantOf([person.getId()]))
        
            ans = GenericFilter.GenericFilter()
            ans.set_name(_("Ancestors of %s") % person.getPrimaryName().getName())
            ans.add_rule(GenericFilter.IsAncestorOf([person.getId()]))
        
            com = GenericFilter.GenericFilter()
            com.set_name(_("People with common ancestor with %s") %
                     person.getPrimaryName().getName())
            com.add_rule(GenericFilter.HasCommonAncestorWith([person.getId()]))
        
            self.filter_menu = GenericFilter.build_filter_menu([all,des,ans,com])
            self.filter.set_menu(self.filter_menu)
        
            self.topwin.show()

    def close(self,obj):
        self.topwin.destroy()

    def on_ok_clicked(self,obj):
        name = self.top.get_widget("filename").get_text()
        restrict = self.top.get_widget('restrict').get_active()
        pfilter = self.filter_menu.get_active().get_data("filter")
        
        Utils.destroy_passed_object(self.topwin)
        try:
            self.export(name, pfilter, restrict)
        except (IOError,OSError),msg:
            ErrorDialog(_("Could not create %s") % name, msg)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','export-data')

    def export(self, filename, cfilter, restrict ):

        if cfilter == None:
            for p in self.db.getPersonKeys():
                self.plist[p] = 1
        else:
            try:
                for p in cfilter.apply(self.db, self.db.getPersonMap().values()):
                    self.plist[p.getId()] = 1
            except Errors.FilterError, msg:
                (m1,m2) = msg.messages()
                ErrorDialog(m1,m2)
                return
            
        name_map = {}
        id_map = {}
        id_name = {}
        for key in self.plist:
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
                    count += 1
                name_map[nn] = key
                id_map[key] = nn
            else:
                name_map[n] = key
                id_map[key] = n
            id_name[key] = get_name(pn,count)

        f = open(filename,"w")

        for key in self.plist:
            p = self.db.getPerson(key)
            name = id_name[key]
            father = ""
            mother = ""
            email = ""
            web = ""

            family = p.getMainParents()
            if family:
                if family.getFather() and id_map.has_key(family.getFather().getId()):
                    father = id_map[family.getFather().getId()]
                if family.getMother() and id_map.has_key(family.getMother().getId()):
                    mother = id_map[family.getMother().getId()]

            #
            # Calculate Date
            #
            birth = p.getBirth().getDateObj()
            death = p.getDeath().getDateObj()

            if restrict:
                alive = p.probablyAlive()
            else:
                alive = 0
                
            if birth.isValid() and not alive:
                if death.isValid() and not alive :
                    dates = "%s-%s" % (fdate(birth),fdate(death))
                else:
                    dates = fdate(birth)
            else:
                if death.isValid() and not alive:
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
