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
"""
The AddSpouse module provides the AddSpouse class that allows the user to
add a new spouse to the active person.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

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
import Sorter
import Utils
import GrampsCfg

#-------------------------------------------------------------------------
#
# AddSpouse
#
#-------------------------------------------------------------------------
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
        self.ok = self.glade.get_widget('spouse_ok')

        self.ok.set_sensitive(0)
        arrow_map = [(2,self.glade.get_widget('NameArrow')),
                     (3,self.glade.get_widget('DateArrow'))]
                     
        self.sorter = Sorter.Sorter(self.spouse_list,arrow_map,'spouse')
        self.spouse_list.set_column_visibility(2,0)
        self.spouse_list.set_column_visibility(3,0)
        self.rel_combo.set_popdown_strings(const.familyRelations)
        title = _("Choose Spouse/Partner of %s") % GrampsCfg.nameof(person)
        self.glade.get_widget("spouseTitle").set_text(title)

        self.glade.signal_autoconnect({
            "on_select_spouse_clicked" : self.select_spouse_clicked,
            "on_new_spouse_clicked"    : self.new_spouse_clicked,
            "on_rel_type_changed"      : self.relation_type_changed,
            "on_combo_insert_text"     : Utils.combo_insert_text,
            "on_select_row"            : self.select_row,
            "on_unselect_row"          : self.unselect_row,
            "destroy_passed_object"    : Utils.destroy_passed_object
            })

        self.relation_type.set_text(_("Married"))

    def select_row(self,obj,a,b,c):
        """
        Called with a row has be unselected. Used to ensable the OK button
        when a row has been selected.
        """
        self.ok.set_sensitive(1)

    def unselect_row(self,obj,a,b,c):
        """
        Called with a row has be unselected. Used to disable the OK button
        when nothing is selected.
        """
        self.ok.set_sensitive(0)
        
    def new_spouse_clicked(self,obj):
        """
        Called when the spouse to be added does not exist, and needs
        to be created and added to the database
        """
        import QuickAdd

        relation = const.save_frel(self.relation_type.get_text())
        if relation == "Partners":
            if self.person.getGender() == RelLib.Person.male:
                gen = "male"
            else:
                gen = "female"
        elif self.person.getGender() == RelLib.Person.male:
            gen = "female"
        else:
            gen = "male"

        QuickAdd.QuickAdd(self.db,gen,self.update_list)

    def update_list(self,person):
        """
        Updates the potential spouse list after a person has been added
        to database. Called by the QuickAdd class when the dialog has
        been closed.
        """
        self.addperson(person)
        self.relation_type_changed(self.relation_type)
        self.sorter.sort_list()
        row = self.spouse_list.find_row_from_data(person.getId())
        self.spouse_list.select_row(row,0)
        self.spouse_list.moveto(row,0)

    def select_spouse_clicked(self,obj):
        """
        Called when the spouse to be added already exists and has been
        selected from the list.
        """
        if len(self.spouse_list.selection) == 0:
            return
        row = self.spouse_list.selection[0]
        spouse = self.db.getPerson(self.spouse_list.get_row_data(row))

        # don't do anything if the marriage already exists
        for f in self.person.getFamilyList():
            if spouse == f.getMother() or spouse == f.getFather():
                Utils.destroy_passed_object(obj)
                return

        Utils.modified()
        family = self.db.newFamily()
        self.person.addFamily(family)
        spouse.addFamily(family)

        if (self.person.getGender() == RelLib.Person.male
            or spouse.getGender() == RelLib.Person.female):
            family.setMother(spouse)
            family.setFather(self.person)
        else:
            family.setFather(spouse)
            family.setMother(self.person)

        family.setRelationship(const.save_frel(self.relation_type.get_text()))
        Utils.destroy_passed_object(obj)
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
                sgender = const.female
            else:
                sgender = const.male
        else:
            if gender == RelLib.Person.male:
                sgender = const.male
            else:
                sgender = const.female
            
        index = 0
        self.spouse_list.clear()
        self.spouse_list.freeze()
        for key in self.db.getPersonKeys():
            data = self.db.getPersonDisplay(key)
            if data[2] == sgender:
                continue

            self.spouse_list.append([data[0],data[3],data[5],data[6]])
            self.spouse_list.set_row_data(index,key)
            index = index + 1
        self.sorter.sort_list()
        self.spouse_list.thaw()

#-------------------------------------------------------------------------
#
# SetSpouse
#
#-------------------------------------------------------------------------
class SetSpouse:
    """
    Displays the AddSpouse dialog, allowing the user to create a new
    family with the passed person as one spouse, and another person to
    be selected.
    """
    def __init__(self,db,person,family,update,addperson):
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
        self.family = family
        self.addperson = addperson

        self.glade = libglade.GladeXML(const.gladeFile, "spouseDialog")

        self.rel_combo = self.glade.get_widget("rel_combo")
        self.relation_type = self.glade.get_widget("rel_type")
        self.spouse_list = self.glade.get_widget("spouseList")

        arrow_map = [(2,self.glade.get_widget('NameArrow')),
                     (3,self.glade.get_widget('DateArrow'))]
                     
        self.sorter = Sorter.Sorter(self.spouse_list,arrow_map,'spouse')
        self.spouse_list.set_column_visibility(2,0)
        self.spouse_list.set_column_visibility(3,0)

        self.relation_def = self.glade.get_widget("reldef")

        self.rel_combo.set_popdown_strings(const.familyRelations)
        title = _("Choose Spouse/Partner of %s") % GrampsCfg.nameof(person)
        self.glade.get_widget("spouseTitle").set_text(title)

        self.glade.signal_autoconnect({
            "on_select_spouse_clicked" : self.select_spouse_clicked,
            "on_new_spouse_clicked"    : self.new_spouse_clicked,
            "on_rel_type_changed"      : self.relation_type_changed,
            "on_combo_insert_text"     : Utils.combo_insert_text,
            "destroy_passed_object"    : Utils.destroy_passed_object
            })

        self.relation_type.set_text(_("Married"))

    def new_spouse_clicked(self,obj):
        """
        Called when the spouse to be added does not exist, and needs
        to be created and added to the database
        """
        import QuickAdd

        relation = const.save_frel(self.relation_type.get_text())
        if relation == "Partners":
            if self.person.getGender() == RelLib.Person.male:
                gen = "male"
            else:
                gen = "female"
        elif self.person.getGender() == RelLib.Person.male:
            gen = "female"
        else:
            gen = "male"
        QuickAdd.QuickAdd(self.db,gen,self.update_list)

    def update_list(self,person):
        self.addperson(person)
        self.relation_type_changed(self.relation_type)
        self.sorter.sort_list()
        row = self.spouse_list.find_row_from_data(person.getId())
        self.spouse_list.select_row(row,0)
        self.spouse_list.moveto(row,0)

    def select_spouse_clicked(self,obj):
        """
        Called when the spouse to be added already exists and has been
        selected from the list.
        """
        if len(self.spouse_list.selection) == 0:
            return
        row = self.spouse_list.selection[0]
        spouse = self.db.getPerson(self.spouse_list.get_row_data(row))

        # don't do anything if the marriage already exists
        for f in self.person.getFamilyList():
            if spouse == f.getMother() or spouse == f.getFather():
                Utils.destroy_passed_object(obj)
                return

        Utils.modified()

        # Recompute the family relation.  self.person is already
        # a father or mother, but in case (s)he had an unknown
        # gender, adding a spouse might swap roles.
        if (self.person.getGender() == RelLib.Person.male
            or spouse.getGender() == RelLib.Person.female):
            self.family.setMother(spouse)
            self.family.setFather(self.person)
        else:
            self.family.setFather(spouse)
            self.family.setMother(self.person)

        spouse.addFamily(self.family)

        reltype = self.relation_type.get_text()
        self.family.setRelationship(const.save_frel(reltype))
        Utils.destroy_passed_object(obj)
        self.update(self.family)

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
                sgender = const.female
            else:
                sgender = const.male
	else:
            if gender == RelLib.Person.male:
                sgender = const.male
            else:
                sgender = const.female
            
        index = 0
        self.spouse_list.clear()
        self.spouse_list.freeze()
        for key in self.db.getPersonKeys():
            data = self.db.getPersonDisplay(key)
            if data[2] == sgender:
                continue

            self.spouse_list.append([data[0],data[3],data[5],data[6]])
            self.spouse_list.set_row_data(index,key)
            index = index + 1
        self.spouse_list.thaw()
