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
import utils

class AddSpouse:
    """
    Displays the AddSpouse dialog, allowing the user to create a new
    family with the passed person as one spouse, and another person to
    be selected.
    """
    def __init__(self,db,person,update,addperson):
        """
        Displays the AddSpouse dialog box.

        db - database to which to add the new family
        person - the current person, will be one of the parents
        update - function that updates the family display
        addperson - function that adds a person to the person view
        """
        self.db = db
        self.update = update
        self.person = person
        self.addperson = addperson

        self.glade = libglade.GladeXML(const.gladeFile, "spouseDialog")

        self.rel_combo = self.glade.get_widget("rel_combo")
        self.relation_type = self.glade.get_widget("rel_type")
        self.spouse_list = self.glade.get_widget("spouseList")
        self.relation_def = self.glade.get_widget("reldef")
        self.top = self.glade.get_widget("spouseDialog")
        self.given = self.glade.get_widget("given")
        self.surname = self.glade.get_widget("surname")
        self.surname_combo = self.glade.get_widget("surname_combo")

        self.rel_combo.set_popdown_strings(const.familyRelations)
        utils.attach_surnames(self.surname_combo)

        # Typing CR selects 'Add Existing' button
        self.top.editable_enters(self.given)
        self.top.editable_enters(self.surname)

        self.name_list = self.db.getPersonMap().values()
        self.name_list.sort(sort.by_last_name)

        self.glade.signal_autoconnect({
            "on_select_spouse_clicked" : self.select_spouse_clicked,
            "on_new_spouse_clicked"    : self.new_spouse_clicked,
            "on_rel_type_changed"      : self.relation_type_changed,
            "on_combo_insert_text"     : utils.combo_insert_text,
            "destroy_passed_object"    : utils.destroy_passed_object
            })

        self.relation_type.set_text(_("Married"))

    def new_spouse_clicked(self,obj):
        """
        Called when the spouse to be added does not exist, and needs
        to be created and added to the database
        """
        spouse = RelLib.Person()
        self.db.addPerson(spouse)

        name = spouse.getPrimaryName()
        name.setSurname(string.strip(self.surname.get_text()))
        name.setFirstName(string.strip(self.given.get_text()))

        relation = const.save_frel(self.relation_type.get_text())
        if relation == "Partners":
            spouse.setGender(self.person.getGender())
        elif self.person.getGender() == RelLib.Person.male:
            spouse.setGender(RelLib.Person.female)
        else:
            spouse.setGender(RelLib.Person.male)

        family = self.db.newFamily()
        family.setRelationship(relation)

        self.person.addFamily(family)
        spouse.addFamily(family)

        if self.person.getGender() == RelLib.Person.male:
            family.setMother(spouse)
            family.setFather(self.person)
        else:	
            family.setFather(spouse)
            family.setMother(self.person)
            
        utils.destroy_passed_object(obj)
        utils.modified()
        self.addperson(spouse)
        self.update(family)

    def select_spouse_clicked(self,obj):
        """
        Called when the spouse to be added already exists and has been
        selected from the list.
        """
        if len(self.spouse_list.selection) == 0:
            return
        row = self.spouse_list.selection[0]
        spouse = self.spouse_list.get_row_data(row)

        # don't do anything if the marriage already exists
        for f in self.person.getFamilyList():
            if spouse == f.getMother() or spouse == f.getFather():
                utils.destroy_passed_object(obj)
                return

        utils.modified()
        family = self.db.newFamily()
        self.person.addFamily(family)
        spouse.addFamily(family)

        if self.person.getGender() == RelLib.Person.male:
            family.setMother(spouse)
            family.setFather(self.person)
        else:	
            family.setFather(spouse)
            family.setMother(self.person)

        family.setRelationship(const.save_frel(self.relation_type.get_text()))
        utils.destroy_passed_object(obj)
        self.update(family)

    def relation_type_changed(self,obj):
        """
        Called whenever the relationship type changes. Rebuilds the
        the potential spouse list.
        """
        text = obj.get_text()
        self.relation_def.set_text(const.relationship_def(text))
    
        # determine the gender of the people to be loaded into
        # the potential spouse list. If Partners is selected, use
        # the same gender as the current person.
        gender = self.person.getGender()
        if text == _("Partners"):
            if gender == RelLib.Person.male:
                gender = RelLib.Person.female
            else:
                gender = RelLib.Person.male
	
        index = 0
        self.spouse_list.clear()
        self.spouse_list.freeze()
        for person in self.name_list:
            if person.getGender() == gender:
                continue
            name = person.getPrimaryName().getName()
            self.spouse_list.append([name,utils.birthday(person)])
            self.spouse_list.set_row_data(index,person)
            index = index + 1
        self.spouse_list.thaw()

