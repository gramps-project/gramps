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
import RelLib
import const
import sort
import Utils
import GrampsCfg

class ChooseParents:
    """
    Displays the Choose Parents dialog box, allowing the parents
    to be edited.
    """
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
	self.mother_rel = self.glade.get_widget("mrel")
	self.father_rel = self.glade.get_widget("frel")
        self.fcombo = self.glade.get_widget("prel_combo")
        self.prel = self.glade.get_widget("prel")
        self.title = self.glade.get_widget("chooseTitle")
        self.father_name = self.glade.get_widget("fatherName")
        self.mother_name = self.glade.get_widget("motherName")
        self.father_list = self.glade.get_widget("fatherList")
        self.mother_list = self.glade.get_widget("motherList")
        self.flabel = self.glade.get_widget("flabel")
        self.mlabel = self.glade.get_widget("mlabel")
        self.fcombo.set_popdown_strings(const.familyRelations)

        if self.family and self.family == self.person.getMainFamily():
            self.mother_rel.set_text(_("Birth"))
            self.father_rel.set_text(_("Birth"))
        else:
            for (f,mr,fr) in self.person.getAltFamilyList():
                if f == self.family:
                    self.mother_rel.set_text(_(mr))
                    self.father_rel.set_text(_(fr))
                    break
            else:
                self.mother_rel.set_text(_("Birth"))
                self.father_rel.set_text(_("Birth"))

        self.glade.signal_autoconnect({
            "on_motherList_select_row" : self.mother_list_select_row,
            "on_fatherList_select_row" : self.father_list_select_row,
            "on_save_parents_clicked"  : self.save_parents_clicked,
            "on_addmother_clicked"     : self.add_mother_clicked,
            "on_addfather_clicked"     : self.add_father_clicked,
            "on_prel_changed"          : self.parent_relation_changed,
            "on_combo_insert_text"     : Utils.combo_insert_text,
            "destroy_passed_object"    : Utils.destroy_passed_object
            })

        text = _("Choose the Parents of %s") % GrampsCfg.nameof(self.person)
        self.title.set_text(text)
        if self.family:
            self.prel.set_text(_(self.family.getRelationship()))
        else:
            self.parent_relation_changed(self.prel)
        self.top.show()

    def parent_relation_changed(self,obj):

        type = obj.get_text()

        self.father_name.set_text(GrampsCfg.nameof(self.father))
        self.mother_name.set_text(GrampsCfg.nameof(self.mother))
        
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
            if person == self.person:
                continue
            if person.getGender() == RelLib.Person.unknown:
                continue
            rdata = [Utils.phonebook_name(person),Utils.birthday(person)]
            if type == "Partners":
                self.father_list.append(rdata)
                self.father_list.set_row_data(father_index,person)
                father_index = father_index + 1
                self.mother_list.append(rdata)
                self.mother_list.set_row_data(mother_index,person)
                mother_index = mother_index + 1
            elif person.getGender() == RelLib.Person.male:
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
        """
        Finds the family associated with the father and mother.
        If one does not exist, it is created.
        """
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

    def mother_list_select_row(self,obj,a,b,c):
        self.mother = obj.get_row_data(a)
        self.mother_name.set_text(GrampsCfg.nameof(self.mother))

    def father_list_select_row(self,obj,a,b,c):
        self.father = obj.get_row_data(a)
        self.father_name.set_text(GrampsCfg.nameof(self.father))

    def save_parents_clicked(self,obj):
        mother_rel = const.childRelations[self.mother_rel.get_text()]
        father_rel = const.childRelations[self.father_rel.get_text()]
        type = const.save_frel(self.prel.get_text())

        if self.father or self.mother:
            if self.mother and not self.father:
                if self.mother.getGender() == RelLib.Person.male:
                    self.father = self.mother
                    self.mother = None
                self.family = self.find_family(self.father,self.mother)
            elif self.father and not self.mother: 
                if self.father.getGender() == RelLib.Person.female:
                    self.mother = self.father
                    self.father = None
                self.family = self.find_family(self.father,self.mother)
            elif self.mother.getGender() != self.father.getGender():
                if type == "Partners":
                    type = "Unknown"
                if self.father.getGender() == RelLib.Person.female:
                    x = self.father
                    self.father = self.mother
                    self.mother = x
                self.family = self.find_family(self.father,self.mother)
            else:
                type = "Partners"
                self.family = self.find_family(self.father,self.mother)
        else:    
            self.family = None

        Utils.destroy_passed_object(obj)
        if self.family:
            self.family.setRelationship(type)
            self.change_family_type(self.family,mother_rel,father_rel)
        self.family_update(None)

    def add_parent_clicked(self,obj,sex):
        self.xml = libglade.GladeXML(const.gladeFile,"addperson")
        self.xml.get_widget(sex).set_active(1)
        self.xml.signal_autoconnect({
            "on_addfather_close": self.add_parent_close,
            "on_combo_insert_text" : Utils.combo_insert_text,
            "destroy_passed_object" : Utils.destroy_passed_object
            })

        window = self.xml.get_widget("addperson")
        window.editable_enters(self.xml.get_widget("given"))
        window.editable_enters(self.xml.get_widget("surname"))
        Utils.attach_surnames(self.xml.get_widget("surnameCombo"))

    def add_father_clicked(self,obj):
        self.add_parent_clicked(obj,"male")

    def add_mother_clicked(self,obj):
        self.add_parent_clicked(obj,"female")

    def change_family_type(self,family,mother_rel,father_rel):
        """
        Changes the family type of the specified family. If the family
        is None, the the relationship type shoud be deleted.
        """
        is_main = mother_rel == "Birth" and father_rel == "Birth"

        if family == self.person.getMainFamily():
            # make sure that the person is listed as a child
            if self.person not in family.getChildList():
                family.addChild(self.person)
            # if the relationships indicate that this is no longer
            # the main family, we need to delete the main family,
            # and add it as an alternate family (assuming that it
            # does not already in the list)
            if not is_main:
                self.person.setMainFamily(None)
                for fam in self.person.getAltFamilyList():
                    if fam[0] == family:
                        if fam[1] == mother_rel and fam[2] == father_rel:
                            return
                        else:
                            self.person.removeFamily(fam[0])
                else:
                    self.person.addAltFamily(family,mother_rel,father_rel)
        # The family is not already the main family
        else:
            if self.person not in family.getChildList():
                family.addChild(self.person)
            for fam in self.person.getAltFamilyList():
                if family == fam[0]:
                    if is_main:
                        self.person.setMainFamily(family)
                        self.person.removeAltFamily(family)
                        break
                    if mother_rel == fam[1] and father_rel == fam[2]:
                        return
                    if mother_rel != fam[1] or father_rel != fam[2]:
                        self.person.removeAltFamily(family)
                        self.person.addAltFamily(family,mother_rel,father_rel)
                        break
            else:
                if is_main:
                    self.person.setMainFamily(family)
                else:
                    self.person.addAltFamily(family,mother_rel,father_rel)
        Utils.modified()

    def add_parent_close(self,obj):

        surname = self.xml.get_widget("surname").get_text()
        given = self.xml.get_widget("given").get_text()
        person = RelLib.Person()
        self.db.addPerson(person)
        name = person.getPrimaryName()
        name.setSurname(surname)
        name.setFirstName(given)
        if self.xml.get_widget("male").get_active():
            person.setGender(RelLib.Person.male)
            self.father = person
        else:
            person.setGender(RelLib.Person.female)
            self.mother = person
        Utils.modified()
        self.parent_relation_changed(self.prel)
        Utils.destroy_passed_object(obj)
        self.full_update()

