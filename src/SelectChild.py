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
from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *

import const
import sort
import Utils
import GrampsCfg
import string
import AutoComp

#-------------------------------------------------------------------------
#
# SelectChild
#
#-------------------------------------------------------------------------
class SelectChild:

    def __init__(self,db,family,person,redraw):
        self.db = db
        self.person = person
        self.family = family
        self.redraw = redraw
        self.xml = libglade.GladeXML(const.gladeFile,"selectChild")
    
        self.xml.signal_autoconnect({
            "on_save_child_clicked"    : self.on_save_child_clicked,
            "on_show_toggled"          : self.on_show_toggled,
            "destroy_passed_object"    : Utils.destroy_passed_object
            })

        self.select_child_list = {}
        self.top = self.xml.get_widget("selectChild")
        self.add_child = self.xml.get_widget("addChild")
        self.add_child.set_column_visibility(1,GrampsCfg.id_visible)

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
            
            if self.person.getGender() == Person.male:
                self.xml.get_widget("flabel").set_text(label)
                self.xml.get_widget("mrel_combo").set_sensitive(0)
            else:
                self.xml.get_widget("mlabel").set_text(label)
                self.xml.get_widget("frel_combo").set_sensitive(0)

        self.mrel = self.xml.get_widget("mrel")
        self.frel = self.xml.get_widget("frel")
        self.mrel.set_text(_("Birth"))
        self.frel.set_text(_("Birth"))
    
        self.redraw_child_list(2)
        self.top.show()

    def redraw_child_list(self,filter):
        self.add_child.freeze()
        self.add_child.clear()
        index = 0

        bday = self.person.getBirth().getDateObj()
        dday = self.person.getDeath().getDateObj()

        slist = []
        for f in self.person.getParentList():
            if f:
                if f[0].getFather():
                    slist.append(f[0].getFather())
                elif f[0].getMother():
                    slist.append(f[0].getMother())
                for c in f[0].getChildList():
                    slist.append(c)
            
        person_list = []
        for key in self.db.getPersonKeys():
            person = self.db.getPerson(key)
            if filter:
                if person in slist or person.getMainParents():
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
        
            person_list.append(person)

        person_list.sort(sort.by_last_name)
        for person in person_list:
            self.add_child.append([Utils.phonebook_name(person),
                                   Utils.birthday(person),
                                   person.getId()])
            self.add_child.set_row_data(index,person)
            index = index + 1
        self.add_child.thaw()

    def on_save_child_clicked(self,obj):
        for row in self.add_child.selection:
            select_child = self.add_child.get_row_data(row)
            if self.family == None:
                self.family = self.db.newFamily()
                self.person.addFamily(self.family)
                if self.person.getGender() == Person.male:
                    self.family.setFather(self.person)
                else:	
                    self.family.setMother(self.person)

            self.family.addChild(select_child)
		
            mrel = const.childRelations[self.mrel.get_text()]
            mother = self.family.getMother()
            if mother and mother.getGender() != Person.female:
                if mrel == "Birth":
                    mrel = "Unknown"
                
            frel = const.childRelations[self.frel.get_text()]
            father = self.family.getFather()
            if father and father.getGender() != Person.male:
                if frel == "Birth":
                    frel = "Unknown"

#            if mrel == "Birth" and frel == "Birth":
#                family = select_child.getMainFamily()
#                if family != None and family != self.family:
#                    family.removeChild(select_child)
#
#                select_child.setMainFamily(self.family)
#            else:
            select_child.addAltFamily(self.family,mrel,frel)

            Utils.modified()
        
        Utils.destroy_passed_object(obj)
        self.redraw(self.family)
        
    def on_show_toggled(self,obj):
        self.redraw_child_list(obj.get_active())

class NewChild:

    def __init__(self,db,family,person,update,update_disp,autoname=3):
        self.db = db
        self.person = person
        self.family = family
        self.update = update
        self.edit_update = update_disp
        
        self.xml = libglade.GladeXML(const.gladeFile,"addChild")
        self.xml.signal_autoconnect({
            "on_addchild_ok_clicked" : self.on_addchild_ok_clicked,
            "on_edit_new_child"      : self.on_edit_new_child,
            "on_male_toggled"        : self.on_male_toggled,
            "on_female_toggled"      : self.on_female_toggled,
            "on_gender_toggled"      : self.on_gender_toggled,
            "destroy_passed_object"  : Utils.destroy_passed_object
            })

        if autoname == 0:
            self.update_surname = self.north_american
        elif autoname == 2:
            self.update_surname = self.latin_american
        elif autoname == 3:
            self.update_surname = self.icelandic
        else:
            self.update_surname = self.no_name

        self.mrel = self.xml.get_widget("mrel")
        self.frel = self.xml.get_widget("frel")
        self.top  = self.xml.get_widget("addChild")
        self.surname = self.xml.get_widget("surname")
        self.given = self.xml.get_widget("childGiven")
        if GrampsCfg.autocomp:
            self.comp = AutoComp.AutoEntry(self.surname,self.db.getSurnames())

        self.surname.set_text(self.update_surname(2))

        if self.family:
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
            
            if self.person.getGender() == Person.male:
                self.xml.get_widget("flabel").set_text(label)
                self.xml.get_widget("mcombo").set_sensitive(0)
            else:
                self.xml.get_widget("mlabel").set_text(label)
                self.xml.get_widget("fcombo").set_sensitive(0)

        self.mrel.set_text(_("Birth"))
        self.frel.set_text(_("Birth"))

        # Typing CR selects OK button
        self.top.editable_enters(self.given)
        self.top.editable_enters(self.surname)
        self.top.editable_enters(self.mrel)
        self.top.editable_enters(self.frel)
        self.top.show()

    def on_male_toggled(self,obj):
        if obj.get_active():
            txt = self.surname.get_text()
            if txt == "" or txt == self.update_surname(1):
                self.surname.set_text(self.update_surname(0))
            
    def on_female_toggled(self,obj):
        if obj.get_active():
            txt = self.surname.get_text()
            if txt == "" or txt == self.update_surname(0):
                self.surname.set_text(self.update_surname(1))

    def on_gender_toggled(self,obj):
        pass

    def combo_insert_text(self,combo,new_text,new_text_len,i_dont_care):
        Utils.combo_insert_text(combo,new_text,new_text_len,i_dont_care)

    def north_american(self,val):
        if self.person.getGender() == Person.male:
            return self.person.getPrimaryName().getSurname()
        elif self.family:
            f = self.family.getFather()
            if f:
                return f.getPrimaryName().getSurname()
        return ""

    def no_name(self,val):
        return ""

    def latin_american(self,val):
        if self.family:
            father = self.family.getFather()
            mother = self.family.getMother()
            if not father or not mother:
                return ""
            fsn = father.getPrimaryName().getSurname()
            msn = mother.getPrimaryName().getSurname()
            if not father or not mother:
                return ""
            try:
                return "%s %s" % (string.split(fsn)[0],string.split(msn)[0])
            except:
                return ""
        else:
            return ""

    def icelandic(self,val):
        fname = ""
        if self.person.getGender() == Person.male:
            fname = self.person.getPrimaryName().getFirstName()
        elif self.family:
            f = self.family.getFather()
            if f:
                fname = f.getPrimaryName().getFirstName()
        if fname:
            fname = string.split(fname)[0]
        if val == 0:
            return "%ssson" % fname
        elif val == 1:
            return "%sdóttir" % fname
        else:
            return ""

    def on_addchild_ok_clicked(self,obj):
    
        surname = self.surname.get_text()
        given = self.given.get_text()
    
        person = Person()
        self.db.addPerson(person)

        name = Name()
        name.setSurname(surname)
        name.setFirstName(given)
        person.setPrimaryName(name)

        if self.xml.get_widget("childMale").get_active():
            person.setGender(Person.male)
        elif self.xml.get_widget("childFemale").get_active():
            person.setGender(Person.female)
        else:
            person.setGender(Person.unknown)
        
        if not self.family:
            self.family = self.db.newFamily()
            if self.person.getGender() == Person.male:
                self.family.setFather(self.person)
            else:
                self.family.setMother(self.person)
            self.person.addFamily(self.family)

        mrel = const.childRelations[self.mrel.get_text()]
        frel = const.childRelations[self.frel.get_text()]

        person.addAltFamily(self.family,mrel,frel)
            
        self.family.addChild(person)
        
        # must do an apply filter here to make sure the main window gets updated
    
        self.update(self.family,person,[])
        Utils.modified()
        Utils.destroy_passed_object(obj)
        self.new_child = person

    def on_edit_new_child(self,obj):
        import EditPerson
        
        self.on_addchild_ok_clicked(obj)
        EditPerson.EditPerson(self.new_child,self.db,self.edit_update)
        

