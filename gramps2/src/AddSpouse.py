#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import const
import Utils
import GrampsCfg
import PeopleModel
import Date
import Marriage

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
    def __init__(self,parent,db,person,update,addperson,family=None):
        """
        Displays the AddSpouse dialog box.

        db - database to which to add the new family
        person - the current person, will be one of the parents
        update - function that updates the family display
        addperson - function that adds a person to the person view
        """
        self.parent = parent
        self.db = db
        self.update = update
        self.person = person
        self.gender = self.person.get_gender()
        self.addperson = addperson
        self.active_family = family

        self.filter_func = self.likely_filter

        # determine the gender of the people to be loaded into
        # the potential spouse list. If Partners is selected, use
        # the same gender as the current person.

        birth_id = self.person.get_birth_id()
        death_id = self.person.get_death_id()
        
        self.bday = self.db.find_event_from_id(birth_id)
        self.dday = self.db.find_event_from_id(death_id)
        if birth_id:
            self.bday = self.db.find_event_from_id(birth_id).get_date_object()
        else:
            self.bday = Date.Date()
            
        if death_id:
            self.dday = self.db.find_event_from_id(death_id).get_date_object()
        else:
            self.dday = Date.Date()

        self.glade = gtk.glade.XML(const.gladeFile, "spouseDialog","gramps")

        self.relation_def = self.glade.get_widget("reldef")
        self.rel_combo = self.glade.get_widget("rel_combo")
        self.relation_type = self.glade.get_widget("rel_type")
        self.spouse_list = self.glade.get_widget("spouse_list")
        self.showall = self.glade.get_widget('showall')

        self.set_gender()

        self.renderer = gtk.CellRendererText()

        self.slist = PeopleModel.PeopleModel(self.db,self.filter_func)
        self.spouse_list.set_model(self.slist)
        self.selection = self.spouse_list.get_selection()
        self.selection.connect('changed',self.select_row)
        self.add_columns(self.spouse_list)
        
        self.ok = self.glade.get_widget('spouse_ok')
        self.ok.set_sensitive(0)
                     
        self.rel_combo.set_popdown_strings(const.familyRelations)
        title = _("Choose Spouse/Partner of %s") % GrampsCfg.nameof(person)

        Utils.set_titles(self.glade.get_widget('spouseDialog'),
                         self.glade.get_widget('title'),title,
                         _('Choose Spouse/Partner'))


        self.glade.signal_autoconnect({
            "on_select_spouse_clicked" : self.select_spouse_clicked,
            "on_spouse_help_clicked"   : self.on_spouse_help_clicked,
            "on_show_toggled"          : self.on_show_toggled,
            "on_new_spouse_clicked"    : self.new_spouse_clicked,
            "on_rel_type_changed"      : self.relation_type_changed,
            "destroy_passed_object"    : Utils.destroy_passed_object
            })

        self.relation_type.set_text(_("Married"))
        self.update_data()
        
    def add_columns(self,tree):
        column = gtk.TreeViewColumn(_('Name'), self.renderer,text=0)
        column.set_resizable(gtk.TRUE)        
        #column.set_clickable(gtk.TRUE)
        column.set_min_width(225)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('ID'), self.renderer,text=1)
        column.set_resizable(gtk.TRUE)        
        #column.set_clickable(gtk.TRUE)
        column.set_min_width(75)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('Birth date'), self.renderer,text=3)
        #column.set_resizable(gtk.TRUE)        
        column.set_clickable(gtk.TRUE)
        tree.append_column(column)

    def on_spouse_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-quick')

    def get_selected_ids(self):
        mlist = []
        self.selection.selected_foreach(self.select_function,mlist)
        return mlist

    def select_function(self,store,path,iter,id_list):
        id_list.append(store.get_value(iter,1))

    def select_row(self,obj):
        """
        Called with a row has be unselected. Used to enable the OK button
        when a row has been selected.
        """
        idlist = self.get_selected_ids()
        if idlist and idlist[0]:
            self.ok.set_sensitive(1)
        else:
            self.ok.set_sensitive(0)
        
    def new_spouse_clicked(self,obj):
        """
        Called when the spouse to be added does not exist, and needs
        to be created and added to the database
        """
        import EditPerson

        relation = const.save_frel(unicode(self.relation_type.get_text()))
        if relation == "Partners":
            if self.person.get_gender() == RelLib.Person.male:
                gen = RelLib.Person.male
            else:
                gen = RelLib.Person.female
        elif self.person.get_gender() == RelLib.Person.male:
            gen = RelLib.Person.female
        else:
            gen = RelLib.Person.male

        person = RelLib.Person()
        person.set_gender(gen)
        EditPerson.EditPerson(self.parent,person,self.db,self.update_list)

    def update_list(self,epo,change):
        """
        Updates the potential spouse list after a person has been added
        to database. Called by the QuickAdd class when the dialog has
        been closed.
        """
        person = epo.person
        if person.get_id() == "":
            self.db.add_person(person)
        else:
            self.db.add_person_no_map(person,person.get_id())
        self.addperson(person)
        self.update_data(person.get_id())
        #self.slist.center_selected()

    def select_spouse_clicked(self,obj):
        """
        Called when the spouse to be added already exists and has been
        selected from the list.
        """

        idlist = self.get_selected_ids()
        if not idlist or not idlist[0]:
            return
        
        spouse = self.db.get_person(idlist[0])

        # don't do anything if the marriage already exists
        for f in self.person.get_family_id_list():
            fam = self.db.find_family_from_id(f)
            if spouse.get_id() == fam.get_mother_id() or spouse.get_id() == fam.get_father_id():
                Utils.destroy_passed_object(obj)
                return

        trans = self.db.start_transaction()

        if not self.active_family:
            self.active_family = self.db.new_family()
            self.person.add_family_id(self.active_family.get_id())
            self.db.commit_person(self.person,trans)
        spouse.add_family_id(self.active_family.get_id())
        self.db.commit_person(spouse,trans)

        if self.person.get_gender() == RelLib.Person.male:
            self.active_family.set_mother_id(spouse.get_id())
            self.active_family.set_father_id(self.person.get_id())
        else:	
            self.active_family.set_father_id(spouse.get_id())
            self.active_family.set_mother_id(self.person.get_id())

        rtype = const.save_frel(unicode(self.relation_type.get_text()))
        self.active_family.set_relationship(rtype)
        self.db.commit_family(self.active_family,trans)
        self.db.add_transaction(trans)
        Utils.destroy_passed_object(obj)
        self.update(self.active_family)
        m = Marriage.Marriage(self.parent, self.active_family,
                              self.parent.db, self.parent.new_after_edit,
                              self.parent.family_view.load_family)
        m.on_add_clicked()

    def relation_type_changed(self,obj):
        self.update_data()

    def all_filter(self, person):
        return person.get_gender() != self.sgender

    def likely_filter(self, person):
        if person.get_gender() == self.sgender:
            return 0

        pd_id = person.get_death_id()
        pb_id = person.get_birth_id()
                
        if pd_id:
            pdday = self.db.find_event_from_id(pd_id).get_date_object()
        else:
            pdday = Date.Date()

        if pb_id:
            pbday = self.db.find_event_from_id(pb_id).get_date_object()
        else:
            pbday = Date.Date()
                    
        if self.bday.get_year_valid():
            if pbday.get_year_valid():
                # reject if person birthdate differs more than
                # 100 years from spouse birthdate 
                if abs(pbday.get_year() - self.bday.get_year()) > 100:
                    return 0

            if pdday.get_year_valid():
                # reject if person birthdate is after the spouse deathdate 
                if self.bday.get_low_year() + 10 > pdday.get_high_year():
                    return 0
                
                # reject if person birthdate is more than 100 years 
                # before the spouse deathdate
                if self.bday.get_high_year() + 100 < pdday.get_low_year():
                    return 0

        if self.dday.get_year_valid():
            if pbday.get_year_valid():
                # reject if person deathdate was prior to 
                # the spouse birthdate 
                if self.dday.get_high_year() < pbday.get_low_year() + 10:
                    return 0

            if pdday.get_year_valid():
                # reject if person deathdate differs more than
                # 100 years from spouse deathdate 
                if abs(pdday.get_year() - self.dday.get_year()) > 100:
                    return 0
        return 1

    def set_gender(self):
        text = unicode(self.relation_type.get_text())
        self.relation_def.set_text(const.relationship_def(text))
        if text == _("Partners"):
            if self.gender == RelLib.Person.male:
                self.sgender = RelLib.Person.female
            else:
                self.sgender = RelLib.Person.male
        else:
            if self.gender == RelLib.Person.male:
                self.sgender = RelLib.Person.male
            else:
                self.sgender = RelLib.Person.female

    def update_data(self,person = None):
        """
        Called whenever the relationship type changes. Rebuilds the
        the potential spouse list.
        """

        self.slist = PeopleModel.PeopleModel(self.db,self.filter_func)
        self.spouse_list.set_model(self.slist)

    def on_show_toggled(self,obj):
        if self.filter_func == self.likely_filter:
            self.filter_func = self.all_filter
        else:
            self.filter_func = self.likely_filter
        print self.filter_func
        self.update_data()
