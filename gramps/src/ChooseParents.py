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
# Standard python modules
#
#-------------------------------------------------------------------------
import string
import os

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
import intl
_ = intl.gettext

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *

import const
import sort
import utils
import Config


class ChooseParents:
    def __init__(self,db,person,family,family_update,full_update):
        self.db = db
        self.person = person
        self.family = family
        self.family_update = family_update
        self.full_update = full_update
        
        if self.family:
            self.father = self.family.getFather()
            self.mother = self.family.getMother()
        else:
            self.mother = None
            self.father = None

        self.glade = libglade.GladeXML(const.gladeFile,"familyDialog")

        self.top = self.glade.get_widget("familyDialog")
	self.mrel = self.glade.get_widget("mrel")
	self.frel = self.glade.get_widget("frel")
        self.fcombo = self.glade.get_widget("prel_combo")
        self.prel = self.glade.get_widget("prel")
        self.title = self.glade.get_widget("chooseTitle")
        self.fatherName = self.glade.get_widget("fatherName")
        self.motherName = self.glade.get_widget("motherName")
        self.father_list = self.glade.get_widget("fatherList")
        self.mother_list = self.glade.get_widget("motherList")
        self.flabel = self.glade.get_widget("flabel")
        self.mlabel = self.glade.get_widget("mlabel")

        if self.family and self.family == self.person.getMainFamily():
            self.mrel.set_text(_("Birth"))
            self.frel.set_text(_("Birth"))
        else:
            for (f,mr,fr) in self.person.getAltFamilyList():
                if f == self.family:
                    self.mrel.set_text(_(mr))
                    self.frel.set_text(_(fr))
                    break
                else:
                    self.mrel.set_text(_("Birth"))
                    self.frel.set_text(_("Birth"))

        self.fcombo.set_popdown_strings(const.familyRelations)

        self.glade.signal_autoconnect({
            "on_motherList_select_row" : self.on_mother_list_select_row,
            "on_fatherList_select_row" : self.on_father_list_select_row,
            "on_save_parents_clicked"  : self.on_save_parents_clicked,
            "on_addmother_clicked"     : self.on_addmother_clicked,
            "on_addfather_clicked"     : self.on_addfather_clicked,
            "on_prel_changed"          : self.on_prel_changed,
            "on_combo_insert_text"     : utils.combo_insert_text,
            "destroy_passed_object"    : utils.destroy_passed_object
            })

        text = _("Choose the Parents of %s") % Config.nameof(self.person)
        self.title.set_text(text)
        if self.family:
            self.prel.set_text(self.family.getRelationship())
        else:
            self.on_prel_changed(self.prel)
        self.top.show()

    def on_prel_changed(self,obj):

        type = obj.get_text()

        self.fatherName.set_text(Config.nameof(self.father))
        self.motherName.set_text(Config.nameof(self.mother))
        
        self.father_list.freeze()
        self.mother_list.freeze()
        self.father_list.clear()
        self.mother_list.clear()

        self.father_list.append(["Unknown",""])
        self.father_list.set_row_data(0,None)

        self.mother_list.append(["Unknown",""])
        self.mother_list.set_row_data(0,None)

        people = self.db.getPersonMap().values()
        people.sort(sort.by_last_name)
        father_index = 1
        mother_index = 1
        for person in people:
            if person == self.person or person.getGender() == Person.unknown:
                continue
            rdata = [utils.phonebook_name(person),utils.birthday(person)]
            if type == "Partners":
                self.father_list.append(rdata)
                self.father_list.set_row_data(father_index,person)
                father_index = father_index + 1

                self.mother_list.append(rdata)
                self.mother_list.set_row_data(mother_index,person)
                mother_index = mother_index + 1
            elif person.getGender() == Person.male:
                self.father_list.append(rdata)
                self.father_list.set_row_data(father_index,person)
                father_index = father_index + 1
            else:
                self.mother_list.append(rdata)
                self.mother_list.set_row_data(mother_index,person)
                mother_index = mother_index + 1

        if type == "Partners":
            self.mlabel.set_text(_("Parent"))
            self.flabel.set_text(_("Parent"))
        else:
            self.mlabel.set_text(_("Mother"))
            self.flabel.set_text(_("Father"))

        self.mother_list.thaw()
        self.father_list.thaw()

    def find_family(self,father,mother):

        if not father and not mother:
            return None
	
        families = self.db.getFamilyMap().values()
        for family in families:
            if family.getFather() == father and family.getMother() == mother:
                return family
            elif family.getFather() == mother and family.getMother() == father:
                return family

        family = self.db.newFamily()
        family.setFather(father)
        family.setMother(mother)
        family.addChild(self.person)
    
        if father:
            father.addFamily(family)
        if mother:
            mother.addFamily(family)

        return family

    def on_mother_list_select_row(self,obj,a,b,c):
        self.mother = obj.get_row_data(a)
        self.motherName.set_text(Config.nameof(self.mother))

    def on_father_list_select_row(self,obj,a,b,c):
        self.father = obj.get_row_data(a)
        self.fatherName.set_text(Config.nameof(self.father))

    def on_save_parents_clicked(self,obj):
        mrel = const.childRelations[self.mrel.get_text()]
        frel = const.childRelations[self.frel.get_text()]
        type = const.save_frel(self.prel.get_text())

        if self.father or self.mother:
            if self.mother and not self.father:
                if self.mother.getGender() == Person.male:
                    self.father = self.mother
                    self.mother = None
                self.family = self.find_family(self.father,self.mother)
            elif self.father and not self.mother: 
                if self.father.getGender() == Person.female:
                    self.mother = self.father
                    self.father = None
                self.family = self.find_family(self.father,self.mother)
            elif self.mother.getGender() != self.father.getGender():
                if type == "Partners":
                    type = "Unknown"
                if self.father.getGender() == Person.female:
                    x = self.father
                    self.father = self.mother
                    self.mother = x
                self.family = self.find_family(self.father,self.mother)
            else:
                type = "Partners"
                self.family = self.find_family(self.father,self.mother)
        else:    
            self.family = None

        utils.destroy_passed_object(obj)
        if self.family:
            self.family.setRelationship(type)
            self.change_family_type(self.family,mrel,frel)
        self.family_update(self.family)

    def on_addparent_clicked(self,obj,sex):
        self.xml = libglade.GladeXML(const.gladeFile,"addperson")
        self.xml.get_widget(sex).set_active(1)
        self.xml.signal_autoconnect({
            "on_addfather_close": self.on_addparent_close,
            "on_combo_insert_text" : utils.combo_insert_text,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        window = self.xml.get_widget("addperson")
        window.editable_enters(self.xml.get_widget("given"))
        window.editable_enters(self.xml.get_widget("surname"))
        if len(const.surnames) > 0:
            const.surnames.sort()
            combo = self.xml.get_widget("surnameCombo")
            combo.set_popdown_strings(const.surnames)
            combo.disable_activate()
        self.xml.get_widget("surname").set_text("")

    def on_addfather_clicked(self,obj):
        self.on_addparent_clicked(obj,"male")

    def on_addmother_clicked(self,obj):
        self.on_addparent_clicked(obj,"female")

    def change_family_type(self,family,mrel,frel):

        is_main = (mrel == "Birth") and (frel == "Birth")
    
        if not family:
            if is_main:
                main = self.person.getMainFamily()
                if main:
                    main.removeChild(self.person)
                active_person.setMainFamily(None)
            else:
                for fam in self.person.getAltFamilyList():
                    if is_main:
                        self.person.removeAltFamily(fam[0])
                        fam.removeChild(active_person)
                        return
        elif family == self.person.getMainFamily():
            family.addChild(selfperson)
            if not is_main:
                utils.modified()
                self.person.setMainFamily(None)
                for fam in self.person.getAltFamilyList():
                    if fam[0] == family:
                        fam[1] = type
                        break
                    elif fam[1] == type:
                        fam[0] = family
                        break
                else:
                    self.person.addAltFamily(family,mrel,frel)
        else:
            family.addChild(self.person)
            for fam in self.person.getAltFamilyList():
                if family == fam[0]:
                    if is_main:
                        self.person.setMainFamily(family)
                        self.person.removeAltFamily(family)
                        utils.modified()
                        break
                    if mrel == fam[1] and frel == fam[2]:
                        break
                    if mrel != fam[1] or frel != fam[2]:
                        self.person.removeAltFamily(family)
                        self.person.addAltFamily(family,mrel,frel)
                        utils.modified()
                        break
            else:
                if is_main:
                    self.person.setMainFamily(family)
                else:
                    self.person.addAltFamily(family,mrel,frel)
            utils.modified()

    def on_addparent_close(self,obj):

        surname = self.xml.get_widget("surname").get_text()
        given = self.xml.get_widget("given").get_text()
        person = Person()
        self.db.addPerson(person)
        name = Name()
        name.setSurname(surname)
        name.setFirstName(given)
        person.setPrimaryName(name)
        if self.xml.get_widget("male").get_active():
            person.setGender(Person.male)
            self.father = person
        else:
            person.setGender(Person.female)
            self.mother = person
        utils.modified()
        self.on_prel_changed(self.prel)
        utils.destroy_passed_object(obj)
        self.full_update()

