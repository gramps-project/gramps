#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
import gobject

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import const
import Utils
import PeopleModel
import Date
import DateHandler
import Marriage
import NameDisplay
import GenericFilter
from QuestionDialog import ErrorDialog, QuestionDialog2

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
    def __init__(self,parent,db,person,family=None):
        """
        Displays the AddSpouse dialog box.

        db - database to which to add the new family
        person - the current person, will be one of the parents
        """
        self.parent = parent
        self.db = db
        self.person = person
        self.gender = self.person.get_gender()
        self.active_family = family

        self.likely = self.build_likely(self.gender)
        self.all    = self.build_all()
        self.filter = self.likely

        # determine the gender of the people to be loaded into
        # the potential spouse list. If Partners is selected, use
        # the same gender as the current person.

        self.glade = gtk.glade.XML(const.gladeFile, "spouseDialog","gramps")

        self.relation_def = self.glade.get_widget("reldef")
        self.rel_combo = self.glade.get_widget("rel_combo")
        self.spouse_list = self.glade.get_widget("spouse_list")
        self.showall = self.glade.get_widget('showall')

        self.set_gender()

        self.renderer = gtk.CellRendererText()

        self.selection = self.spouse_list.get_selection()
        self.selection.connect('changed',self.select_row)
        self.add_columns(self.spouse_list)
        
        self.ok = self.glade.get_widget('spouse_ok')
        self.ok.set_sensitive(0)

        name = NameDisplay.displayer.display(person)
        title = _("Choose Spouse/Partner of %s") % name

        self.window = self.glade.get_widget('spouseDialog')
        Utils.set_titles(self.window,
                         self.glade.get_widget('title'),title,
                         _('Choose Spouse/Partner'))
            
        self.glade.signal_autoconnect({
            "on_select_spouse_clicked" : self.select_spouse_clicked,
            "on_spouse_help_clicked"   : self.on_spouse_help_clicked,
            "on_show_toggled"          : self.on_show_toggled,
            "on_new_spouse_clicked"    : self.new_spouse_clicked,
            "destroy_passed_object"    : Utils.destroy_passed_object
            })

        self.rel_combo.set_active(RelLib.Family.MARRIED)
        self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        gobject.idle_add(self.update_data)

    def build_all(self):
        return None

    def build_likely(self,gender):
        filt = GenericFilter.GenericFilter()
        filt.add_rule(LikelyFilter([self.person.handle,self.person.gender]))
        return filt

    def add_columns(self,tree):
        column = gtk.TreeViewColumn(_('Name'), self.renderer,text=0)
        column.set_resizable(True)        
        column.set_min_width(225)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('ID'), self.renderer,text=1)
        column.set_resizable(True)        
        column.set_min_width(75)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('Birth date'), self.renderer,text=3)
        column.set_clickable(True)
        tree.append_column(column)

    def on_spouse_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-quick')

    def get_selected_ids(self):
        mlist = []
        self.selection.selected_foreach(self.select_function,mlist)
        return mlist

    def select_function(self,store,path,iter,id_list):
        id_list.append(store.get_value(iter,PeopleModel.COLUMN_INT_ID))

    def select_row(self,obj):
        """
        Called with a row has be unselected. Used to enable the OK button
        when a row has been selected.
        """
        idlist = self.get_selected_ids()
        if idlist and idlist[0]:
            self.ok.set_sensitive(True)
        else:
            self.ok.set_sensitive(False)
        
    def new_spouse_clicked(self,obj):
        """
        Called when the spouse to be added does not exist, and needs
        to be created and added to the database
        """
        import EditPerson

        relation = self.rel_combo.get_active()
        if relation == RelLib.Family.CIVIL_UNION:
            if self.person.get_gender() == RelLib.Person.MALE:
                gen = RelLib.Person.MALE
            else:
                gen = RelLib.Person.FEMALE
        elif self.person.get_gender() == RelLib.Person.MALE:
            gen = RelLib.Person.FEMALE
        else:
            gen = RelLib.Person.MALE

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
        self.update_data()
        
        self.slist = PeopleModel.PeopleModel(self.db,self.filter)
        self.slist.rebuild_data()
        self.spouse_list.set_model(self.slist)
        
        path = self.slist.on_get_path(person.get_handle())
        top_path = self.slist.on_get_path(person.get_primary_name().get_surname())
        self.spouse_list.expand_row(top_path,0)
        self.selection.select_path(path)

    def select_spouse_clicked(self,obj):
        """
        Called when the spouse to be added already exists and has been
        selected from the list.
        """

        idlist = self.get_selected_ids()
        if not idlist or not idlist[0]:
            return
        
        spouse = self.db.get_person_from_handle(idlist[0])
        spouse_id = spouse.get_handle()

        # don't do anything if adding self
        if spouse_id == self.person.get_handle():
            ErrorDialog(_("Error adding a spouse"),
                        _("A person cannot be linked as his/her spouse"))
            return

        # display warning if adding a parent
        for (family_handle,frel,mrel) in self.person.get_parent_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if spouse_id in [family.get_mother_handle(),family.get_father_handle()]:
                dialog = QuestionDialog2(
                    _("Spouse is a parent"),
                    _("The person selected as a spouse is a parent of the "
                    "active person. Usually, this is a mistake. You may "
                    "choose either to proceed with adding a spouse, or to "
                    "return to the Choose Spouse dialog to fix the problem."),
                    _("Proceed with adding"), _("Return to dialog"),
                    self.window)
                if not dialog.run():
                    return

        # don't do anything if the marriage already exists
        for f in self.person.get_family_handle_list():
            fam = self.db.get_family_from_handle(f)
            if fam:
                if spouse_id in \
                        (fam.get_mother_handle(),fam.get_father_handle()):
                    ErrorDialog(_("Error adding a spouse"),
                            _("The spouse is already present in this family"))
                    return
                if spouse_id in fam.get_child_handle_list():
                    dialog = QuestionDialog2(
                        _("Spouse is a child"),
                        _("The person selected as a spouse is a child of the "
                        "active person. Usually, this is a mistake. You may "
                        "choose either to proceed with adding a spouse, or to "
                        "return to the Choose Spouse dialog to fix the problem."),
                        _("Proceed with adding"), _("Return to dialog"),
                        self.window)
                    if not dialog.run():
                        return

        trans = self.db.transaction_begin()

        if not self.active_family:
            self.active_family = RelLib.Family()
            self.db.add_family(self.active_family,trans)
            self.person.add_family_handle(self.active_family.get_handle())
            self.db.commit_person(self.person,trans)

        spouse.add_family_handle(self.active_family.get_handle())
        self.db.commit_person(spouse,trans)

        if self.person.get_gender() == RelLib.Person.MALE:
            self.active_family.set_mother_handle(spouse.get_handle())
            self.active_family.set_father_handle(self.person.get_handle())
        else:
            self.active_family.set_father_handle(spouse.get_handle())
            self.active_family.set_mother_handle(self.person.get_handle())

        rtype = self.rel_combo.get_active()
        self.active_family.set_relationship(rtype)
        self.db.commit_family(self.active_family,trans)
        self.db.transaction_commit(trans,_("Add Spouse"))

        Utils.destroy_passed_object(obj)
        m = Marriage.Marriage(self.parent, self.active_family, self.parent.db)
        m.on_add_clicked()

    def relation_type_changed(self,obj):
        gobject.idle_add(self.update_data)

    def all_filter(self, person):
        return person.get_gender() != self.sgender

    def likely_filter(self, person):
        if person.get_gender() == self.sgender:
            return False

        pd_id = person.get_death_handle()
        pb_id = person.get_birth_handle()
                
        if pd_id:
            pdday = self.db.get_event_from_handle(pd_id).get_date_object()
        else:
            pdday = Date.Date()

        if pb_id:
            pbday = self.db.get_event_from_handle(pb_id).get_date_object()
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
                if self.bday.get_year() + 10 > pdday.get_high_year():
                    return 0
                
                # reject if person birthdate is more than 100 years 
                # before the spouse deathdate
                if self.bday.get_high_year() + 100 < pdday.get_year():
                    return 0

        if self.dday.get_year_valid():
            if pbday.get_year_valid():
                # reject if person deathdate was prior to 
                # the spouse birthdate 
                if self.dday.get_high_year() < pbday.get_year() + 10:
                    return 0

            if pdday.get_year_valid():
                # reject if person deathdate differs more than
                # 100 years from spouse deathdate 
                if abs(pdday.get_year() - self.dday.get_year()) > 100:
                    return 0
        return 1

    def set_gender(self):
        if self.rel_combo.get_active() == RelLib.Family.CIVIL_UNION:
            if self.gender == RelLib.Person.MALE:
                self.sgender = RelLib.Person.FEMALE
            else:
                self.sgender = RelLib.Person.MALE
        else:
            if self.gender == RelLib.Person.MALE:
                self.sgender = RelLib.Person.MALE
            else:
                self.sgender = RelLib.Person.FEMALE

    def update_data(self):
        """
        Called whenever the relationship type changes. Rebuilds the
        the potential spouse list.
        """
        self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        while(gtk.events_pending()):
            gtk.main_iteration()
        self.slist = PeopleModel.PeopleModel(self.db,self.filter)
        self.spouse_list.set_model(self.slist)
        self.window.window.set_cursor(None)

    def on_show_toggled(self,obj):
        if self.filter == self.likely:
            self.filter = self.all
        else:
            self.filter = self.likely
        gobject.idle_add(self.update_data)


#-------------------------------------------------------------------------
#
# Likely Filters
#
#-------------------------------------------------------------------------
class LikelyFilter(GenericFilter.Rule):

    labels   = [ 'Person handle', 'Person gender' ]
    category = _('General filters')

    def prepare(self,db):
        person = db.get_person_from_handle(self.list[0])
        if person.birth_handle:
            birth = db.get_event_from_handle(person.birth_handle)
            dateobj = Date.Date(birth.date)
            year = dateobj.get_year()
            dateobj.set_year(year+40)
            self.lower = dateobj.sortval
            dateobj.set_year(year-40)
            self.upper = dateobj.sortval
        else:
            self.upper = None
            self.lower = None

        if person.gender == RelLib.Person.MALE:
            self.gender = RelLib.Person.FEMALE
        else:
            self.gender = RelLib.Person.MALE

    def apply(self,db,person):
        if person.gender != self.gender:
            return False
        if not person.birth_handle or (self.upper == None and
                                       self.lower == None):
            return True
        event = db.get_event_from_handle(person.birth_handle)
        return (event.date == None or event.date.sortval == 0 or
                self.lower > event.date.sortval > self.upper)

