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
from intl import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
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

        self.glade = gtk.glade.XML(const.gladeFile, "spouseDialog")

        self.rel_combo = self.glade.get_widget("rel_combo")
        self.relation_type = self.glade.get_widget("rel_type")
        self.spouse_list = self.glade.get_widget("spouse_list")
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)
        self.spouse_list.set_model(self.model)
        self.selection = self.spouse_list.get_selection()
        self.selection.connect('changed',self.select_row)
        
        self.relation_def = self.glade.get_widget("reldef")
        self.ok = self.glade.get_widget('spouse_ok')

        colno = 0
        for title in [ (_('Name'),3,200),
                       (_('ID'),1,50),
                       (_('Birth Date'),4,50),
                       ('',0,50),
                       ('',0,0)]:
            renderer = gtk.CellRendererText ()
            column = gtk.TreeViewColumn (title[0], renderer, text=colno)
            colno = colno + 1
            column.set_clickable (gtk.TRUE)
            if title[0] == '':
                column.set_clickable(gtk.TRUE)
                column.set_visible(gtk.FALSE)
            else:
                column.set_resizable(gtk.TRUE)
            column.set_sort_column_id(title[1])
            column.set_min_width(title[2])
            self.spouse_list.append_column(column)
            if colno == 1:
                column.clicked()

        self.ok.set_sensitive(0)
                     
        self.rel_combo.set_popdown_strings(const.familyRelations)
        title = _("Choose Spouse/Partner of %s") % GrampsCfg.nameof(person)
        self.glade.get_widget("spouseTitle").set_text(title)

        self.glade.signal_autoconnect({
            "on_select_spouse_clicked" : self.select_spouse_clicked,
            "on_new_spouse_clicked"    : self.new_spouse_clicked,
            "on_rel_type_changed"      : self.relation_type_changed,
            "destroy_passed_object"    : Utils.destroy_passed_object
            })

        self.relation_type.set_text(_("Married"))
        self.relation_type_changed(None)
        
    def select_row(self,obj):
        """
        Called with a row has be unselected. Used to ensable the OK button
        when a row has been selected.
        """

        model,iter = self.selection.get_selected()
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

        model,iter = self.selection.get_selected()
        if not iter:
            return
        
        row = model.get_path(iter)
        id = self.entries[row[0]]
        spouse = self.db.getPerson(id)

        # don't do anything if the marriage already exists
        for f in self.person.getFamilyList():
            if spouse == f.getMother() or spouse == f.getFather():
                Utils.destroy_passed_object(obj)
                return

        Utils.modified()
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
        Utils.destroy_passed_object(obj)
        self.update(family)

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

        self.entries = []
        self.model.clear()
        for key in self.db.getPersonKeys():
            data = self.db.getPersonDisplay(key)
            if data[2] == sgender:
                continue
            iter = self.model.append()
            self.entries.append(key)
            self.model.set(iter,0,data[0],1,data[1],2,data[3],3,data[5],4,data[6])
            if person == key:
                self.selection.select_iter(iter)

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

        self.glade = gtk.glade.XML(const.gladeFile, "spouseDialog")

        self.rel_combo = self.glade.get_widget("rel_combo")
        self.relation_type = self.glade.get_widget("rel_type")
        self.spouse_list = self.glade.get_widget("spouseList")
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
        if self.family.getFather() == self.person:
            self.family.setMother(spouse)
        else:
            self.family.setFather(spouse)
            
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
