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

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from intl import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import const
import Utils
import ListModel

#-------------------------------------------------------------------------
#
# SelectChild
#
#-------------------------------------------------------------------------
class SelectChild:

    def __init__(self,db,family,person,redraw,add_person):
        self.db = db
        self.person = person
        self.family = family
        self.redraw = redraw
        self.add_person = add_person
        self.xml = gtk.glade.XML(const.gladeFile,"select_child")
    
        self.xml.signal_autoconnect({
            "on_save_child_clicked"    : self.on_save_child_clicked,
            "on_show_toggled"          : self.on_show_toggled,
            "on_add_person_clicked"    : self.on_add_person_clicked,
            "destroy_passed_object"    : self.close
            })

        self.select_child_list = {}
        self.top = self.xml.get_widget("select_child")

        title_label = self.xml.get_widget('title')
        title_label.set_text(Utils.title(_('Add Children')))
        title_label.set_use_markup(gtk.TRUE)
        
        self.add_child = self.xml.get_widget("childlist")

        if (self.family):
            father = self.family.getFather()
            mother = self.family.getMother()

            if father != None:
                fname = father.getPrimaryName().getName()
                label = _("Relationship to %s") % fname
                self.xml.get_widget("flabel").set_text(label)

            if mother != None:
                mname = mother.getPrimaryName().getName()
                label = _("Relationship to %s") % mname
                self.xml.get_widget("mlabel").set_text(label)
        else:
            fname = self.person.getPrimaryName().getName()
            label = _("Relationship to %s") % fname
            
            if self.person.getGender() == RelLib.Person.male:
                self.xml.get_widget("flabel").set_text(label)
                self.xml.get_widget("mrel_combo").set_sensitive(0)
            else:
                self.xml.get_widget("mlabel").set_text(label)
                self.xml.get_widget("frel_combo").set_sensitive(0)

        self.mrel = self.xml.get_widget("mrel")
        self.frel = self.xml.get_widget("frel")
        self.mrel.set_text(_("Birth"))

        self.frel.set_text(_("Birth"))

        titles = [(_('Name'),3,150),(_('ID'),1,50), (_('Birth date'),4,100),
                  ('',-1,0),('',-1,0)]
        
        self.refmodel = ListModel.ListModel(self.add_child,titles)
        self.redraw_child_list(2)

    def close(self,obj):
        self.top.destroy()
        
    def redraw_child_list(self,filter):
        self.refmodel.clear()
        bday = self.person.getBirth().getDateObj()
        dday = self.person.getDeath().getDateObj()

        slist = {}
        for f in self.person.getParentList():
            if f:
                if f[0].getFather():
                    slist[f[0].getFather().getId()] = 1
                elif f[0].getMother():
                    slist[f[0].getMother().getId()] = 1
                for c in f[0].getChildList():
                    slist[c.getId()] = 1
            
        person_list = []
        for key in self.db.getPersonKeys():
            person = self.db.getPerson(key)
            if filter:
                if slist.has_key(key) or person.getMainParents():
                    continue
            
                pdday = person.getDeath().getDateObj()
                pbday = person.getBirth().getDateObj()

        	if bday.getYearValid():
                    if pbday.getYearValid():
                        # reject if child birthdate < parents birthdate + 10
                        if pbday.getLowYear() < bday.getHighYear()+10:
                            continue

                        # reject if child birthdate > parents birthdate + 90
                        if pbday.getLowYear() > bday.getHighYear()+90:
                            continue

                    if pdday.getYearValid():
                        # reject if child deathdate < parents birthdate+ 10
                        if pdday.getLowYear() < bday.getHighYear()+10:
                            continue
                
                if dday.getYearValid():
                    if pbday.getYearValid():
                        # reject if childs birth date > parents deathday + 3
                        if pbday.getLowYear() > dday.getHighYear()+3:
                            continue

                    if pdday.getYearValid():
                        # reject if childs death date > parents deathday + 150
                        if pdday.getLowYear() > dday.getHighYear() + 150:
                            continue
        
            person_list.append(person.getId())

        for idval in person_list:
            dinfo = self.db.getPersonDisplay(idval)
            rdata = [dinfo[0],dinfo[1],dinfo[3],dinfo[5],dinfo[6]]
            self.refmodel.add(rdata)

    def on_save_child_clicked(self,obj):
        store,iter = self.refmodel.selection.get_selected()

        if not iter:
            return

        id = self.refmodel.model.get_value(iter,1)
        select_child = self.db.getPerson(id)
        if self.family == None:
            self.family = self.db.newFamily()
            self.person.addFamily(self.family)
            if self.person.getGender() == RelLib.Person.male:
                self.family.setFather(self.person)
            else:	
                self.family.setMother(self.person)
                
        self.family.addChild(select_child)
		
        mrel = const.childRelations[self.mrel.get_text()]
        mother = self.family.getMother()
        if mother and mother.getGender() != RelLib.Person.female:
            if mrel == "Birth":
                mrel = "Unknown"
                
        frel = const.childRelations[self.frel.get_text()]
        father = self.family.getFather()
        if father and father.getGender() !=RelLib. Person.male:
            if frel == "Birth":
                frel = "Unknown"

        select_child.addAltFamily(self.family,mrel,frel)

        Utils.modified()
        self.top.destroy()
        self.redraw(self.family)
        
    def on_show_toggled(self,obj):
        self.redraw_child_list(not obj.get_active())

    def on_add_person_clicked(self,obj):
        """Called with the Add button is pressed. Calls the QuickAdd
        class to create a new person."""
        
        import QuickAdd
        QuickAdd.QuickAdd(self.db,"male",self.add_new_parent)

    def add_new_parent(self,person):
        """Adds a new person to either the father list or the mother list,
        depending on the gender of the person."""
        id = person.getId()
        dinfo = self.db.getPersonDisplay(id)
        rdata = [dinfo[0],dinfo[1],dinfo[3],dinfo[5],dinfo[6]]
        self.refmodel.add_and_select(rdata)
        self.add_person(person)
