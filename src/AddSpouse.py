#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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
import GrampsCfg
import ListModel

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
    def __init__(self,db,person,update,addperson,family=None):
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
        self.active_family = family

        self.glade = gtk.glade.XML(const.gladeFile, "spouseDialog")

        self.rel_combo = self.glade.get_widget("rel_combo")
        self.relation_type = self.glade.get_widget("rel_type")
        self.spouse_list = self.glade.get_widget("spouse_list")
        self.showall = self.glade.get_widget('showall')

        titles = [ (_('Name'),3,200), (_('ID'),1,50), (_('Birth date'),4,50),
                   ('',0,50), ('',0,0)]
        
        self.slist = ListModel.ListModel(self.spouse_list, titles,
                                         self.select_row )
        
        self.relation_def = self.glade.get_widget("reldef")
        self.ok = self.glade.get_widget('spouse_ok')
        self.ok.set_sensitive(0)
                     
        self.rel_combo.set_popdown_strings(const.familyRelations)
        title = _("Choose Spouse/Partner of %s") % GrampsCfg.nameof(person)

        Utils.set_titles(self.glade.get_widget('spouseDialog'),
                         self.glade.get_widget('title'),title,
                         _('Choose Spouse/Partner'))

        self.glade.signal_autoconnect({
            "on_select_spouse_clicked" : self.select_spouse_clicked,
            "on_show_toggled"          : self.on_show_toggled,
            "on_new_spouse_clicked"    : self.new_spouse_clicked,
            "on_rel_type_changed"      : self.relation_type_changed,
            "destroy_passed_object"    : Utils.destroy_passed_object
            })

        self.relation_type.set_text(_("Married"))
        self.relation_type_changed(None)
        
    def select_row(self,obj):
        """
        Called with a row has be unselected. Used to enable the OK button
        when a row has been selected.
        """

        model,iter = self.slist.get_selected()
        if iter:
            self.ok.set_sensitive(1)
        else:
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
        self.update_data(person.getId())

    def select_spouse_clicked(self,obj):
        """
        Called when the spouse to be added already exists and has been
        selected from the list.
        """

        model,iter = self.slist.get_selected()
        if not iter:
            return
        
        id = self.slist.get_object(iter)
        spouse = self.db.getPerson(id)

        # don't do anything if the marriage already exists
        for f in self.person.getFamilyList():
            if spouse == f.getMother() or spouse == f.getFather():
                Utils.destroy_passed_object(obj)
                return

        Utils.modified()
        if not self.active_family:
            self.active_family = self.db.newFamily()
            self.person.addFamily(self.active_family)
        spouse.addFamily(self.active_family)

        if self.person.getGender() == RelLib.Person.male:
            self.active_family.setMother(spouse)
            self.active_family.setFather(self.person)
        else:	
            self.active_family.setFather(spouse)
            self.active_family.setMother(self.person)

        self.active_family.setRelationship(const.save_frel(self.relation_type.get_text()))
        Utils.destroy_passed_object(obj)
        self.update(self.active_family)

    def relation_type_changed(self,obj):
        self.update_data()

    def update_data(self,person = None):
        """
        Called whenever the relationship type changes. Rebuilds the
        the potential spouse list.
        """

        text = self.relation_type.get_text()
        self.relation_def.set_text(const.relationship_def(text))
    
        # determine the gender of the people to be loaded into
        # the potential spouse list. If Partners is selected, use
        # the same gender as the current person.
        gender = self.person.getGender()
        bday = self.person.getBirth().getDateObj()
        dday = self.person.getDeath().getDateObj()

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
            
        self.entries = []
        self.slist.clear()
        self.slist.new_model()
        for key in self.db.getPersonKeys():
            data = self.db.getPersonDisplay(key)
            if data[2] == sgender:
                continue

            if not self.showall.get_active():
                pdday = self.db.getPerson(key).getDeath().getDateObj()
                pbday = self.db.getPerson(key).getBirth().getDateObj()

                if bday.getYearValid():
                    if pbday.getYearValid():
                        # reject if person birthdate differs more than
                        # 100 years from spouse birthdate 
                        if abs(pbday.getYear() - bday.getYear()) > 100:
                            continue

                    if pdday.getYearValid():
                        # reject if person birthdate is after the spouse deathdate 
                        if bday.getLowYear() + 10 > pdday.getHighYear():
                            continue
                
                        # reject if person birthdate is more than 100 years 
                        # before the spouse deathdate
                        if bday.getHighYear() + 100 < pdday.getLowYear():
                            continue

                if dday.getYearValid():
                    if pbday.getYearValid():
                        # reject if person deathdate was prior to 
                        # the spouse birthdate 
                        if dday.getHighYear() < pbday.getLowYear() + 10:
                            continue

                    if pdday.getYearValid():
                        # reject if person deathdate differs more than
                        # 100 years from spouse deathdate 
                        if abs(pdday.getYear() - dday.getYear()) > 100:
                            continue

            self.slist.add([data[0],data[1],data[3],data[5],data[6]],key,person==key)

        self.slist.connect_model()

    def on_show_toggled(self,obj):
        self.update_data()
