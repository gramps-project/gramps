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
import GDK
import GTK
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

class AddSpouse:
    def __init__(self,db,person,update,addperson):
        self.db = db
        self.update = update
        self.person = person
        self.addperson = addperson

        self.glade = libglade.GladeXML(const.gladeFile, "spouseDialog")

        self.rel_combo = self.glade.get_widget("rel_combo")
        self.rel_type = self.glade.get_widget("rel_type")
        self.spouse_list = self.glade.get_widget("spouseList")
        self.rel_def = self.glade.get_widget("reldef")
        self.top = self.glade.get_widget("spouseDialog")
        self.given = self.glade.get_widget("given")
        self.surname = self.glade.get_widget("surname")
        self.surname_combo = self.glade.get_widget("surname_combo")

        self.rel_combo.set_popdown_strings(const.familyRelations)
        if len(const.surnames) > 0:
            const.surnames.sort()
            self.surname_combo.set_popdown_strings(const.surnames)
            self.surname_combo.disable_activate()
        self.surname.set_text("")

        # Typing CR selects 'Add Existing' button
        self.top.editable_enters(self.given)
        self.top.editable_enters(self.surname)

        self.glade.signal_autoconnect({
            "on_select_spouse_clicked" : self.on_select_spouse_clicked,
            "on_new_spouse_clicked"    : self.on_new_spouse_clicked,
            "on_rel_type_changed"      : self.on_rel_type_changed,
            "on_combo_insert_text"     : utils.combo_insert_text,
            "destroy_passed_object"    : utils.destroy_passed_object
            })

        self.rel_type.set_text(_("Married"))

    def on_new_spouse_clicked(self,obj):
        select_spouse = Person()
        self.db.addPerson(select_spouse)
        name = Name()
        select_spouse.setPrimaryName(name)
        name.setSurname(string.strip(self.surname.get_text()))
        name.setFirstName(string.strip(self.given.get_text()))
        reltype = const.save_frel(self.rel_type.get_text())

        if reltype == "Partners":
            select_spouse.setGender(self.person.getGender())
        else:
            if self.person.getGender() == Person.male:
                select_spouse.setGender(Person.female)
            else:
                select_spouse.setGender(Person.male)

        utils.modified()

        family = self.db.newFamily()

        self.person.addFamily(family)
        select_spouse.addFamily(family)
        
        if self.person.getGender() == Person.male:
            family.setMother(select_spouse)
            family.setFather(self.person)
        else:	
            family.setFather(select_spouse)
            family.setMother(self.person)
            
        family.setRelationship(reltype)
            
        utils.destroy_passed_object(obj)
        self.addperson(select_spouse)
        self.update(family)

    def on_select_spouse_clicked(self,obj):
        if len(self.spouse_list.selection) == 0:
            return
        row = self.spouse_list.selection[0]
        select_spouse = self.spouse_list.get_row_data(row)
        for f in self.person.getFamilyList():
            if select_spouse == f.getMother() or select_spouse == f.getFather():
                utils.destroy_passed_object(obj)
                return

        utils.modified()
        family = self.db.newFamily()
        self.person.addFamily(family)
        select_spouse.addFamily(family)

        if self.person.getGender() == Person.male:
            family.setMother(select_spouse)
            family.setFather(self.person)
        else:	
            family.setFather(select_spouse)
            family.setMother(self.person)

        family.setRelationship(const.save_frel(self.rel_type.get_text()))
        utils.destroy_passed_object(obj)
        self.update(family)

    def on_rel_type_changed(self,obj):

        nameList = self.db.getPersonMap().values()
        nameList.sort(sort.by_last_name)
        self.spouse_list.clear()
        self.spouse_list.freeze()
        text = obj.get_text()
        self.rel_def.set_text(const.relationship_def(text))
    
        gender = self.person.getGender()
        if text == _("Partners"):
            if gender == Person.male:
                gender = Person.female
            else:
                gender = Person.male
	
        index = 0
        for person in nameList:
            if person.getGender() == gender:
                continue
            name = person.getPrimaryName().getName()
            self.spouse_list.append([name,utils.birthday(person)])
            self.spouse_list.set_row_data(index,person)
            index = index + 1
        self.spouse_list.thaw()

