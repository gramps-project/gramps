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
ChooseParents interface allows users to select the paretns of an
individual.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import os

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
from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# ChooseParents
#
#-------------------------------------------------------------------------
class ChooseParents:
    """
    Displays the Choose Parents dialog box, allowing the parents
    to be edited.
    """
    def __init__(self,parent,db,person,family,family_update,full_update):
        """
        Creates a ChoosePerson dialog box.

        db - database associated the person
        person - person whose parents we are selecting
        family - current family
        family_update - task that updates the family display
        full_update - task that updates the main display 
        """
        self.nosort = os.environ.has_key('NOSORT')
        self.parent = parent
        self.db = db
        self.child_windows = {}
        self.person = self.db.try_to_find_person_from_id(person.get_id())
        if family:
            self.family = self.db.find_family_from_id(family.get_id())
        else:
            self.family = None
        self.family_update = family_update
        self.full_update = full_update
        self.old_type = ""
        self.type = ""
        self.parent_selected = 0
        self.renderer = gtk.CellRendererText()

        # set default filters
        self.father_filter = self.likely_father_filter
        self.mother_filter = self.likely_mother_filter

        birth_event = self.db.find_event_from_id(self.person.get_birth_id())
        if birth_event:
            self.bday = birth_event.get_date_object()
        else:
            self.bday = None

        death_event = self.db.find_event_from_id(self.person.get_death_id())
        if death_event:
            self.dday = death_event.get_date_object()
        else:
            self.dday = None

        if self.family:
            self.father = self.family.get_father_id()
            self.mother = self.family.get_mother_id()
        else:
            self.mother = None
            self.father = None

        self.glade = gtk.glade.XML(const.gladeFile,"familyDialog","gramps")
        self.top = self.glade.get_widget("familyDialog")

        self.title_text = _("Choose the Parents of %s") % GrampsCfg.nameof(self.person)
        Utils.set_titles(self.top,self.glade.get_widget('title'),
                         self.title_text,_('Choose Parents'))
        
        self.mother_rel = self.glade.get_widget("mrel")
        self.father_rel = self.glade.get_widget("frel")
        self.fcombo = self.glade.get_widget("prel_combo")
        self.prel = self.glade.get_widget("prel")
        self.title = self.glade.get_widget("chooseTitle")
        self.mother_list = self.glade.get_widget("mother_list")
        self.flabel = self.glade.get_widget("flabel")
        self.mlabel = self.glade.get_widget("mlabel")
        self.showallf = self.glade.get_widget('showallf')
        self.showallm = self.glade.get_widget('showallm')
        
        self.fcombo.set_popdown_strings(const.familyRelations)

        self.build_father_list()
        self.build_mother_list()

        for (f,mr,fr) in self.person.get_parent_family_id_list():
            if f == self.family:
                self.mother_rel.set_text(_(mr))
                self.father_rel.set_text(_(fr))
                break
        else:
            self.mother_rel.set_text(_("Birth"))
            self.father_rel.set_text(_("Birth"))

        if self.family:
            self.type = self.family.get_relationship()
        else:
            self.type = "Married"

        self.prel.set_text(_(self.type))
        self.redrawm()
        
        self.glade.signal_autoconnect({
            "on_save_parents_clicked"  : self.save_parents_clicked,
            "on_add_parent_clicked"    : self.add_parent_clicked,
            "on_prel_changed"          : self.parent_relation_changed,
            "on_showallf_toggled"      : self.showallf_toggled,
            "on_showallm_toggled"      : self.showallm_toggled,
            "destroy_passed_object"    : self.close,
            "on_help_familyDialog_clicked"  : self.on_help_clicked,
            "on_familyDialog_delete_event" : self.on_delete_event,
            })

        self.add_itself_to_menu()
        self.top.show()

    def build_father_list(self):
        self.father_list = self.glade.get_widget("father_list")
        self.father_selection = self.father_list.get_selection()
        self.father_selection.connect('changed',self.father_list_select_row)
        self.add_columns(self.father_list)
        self.redrawf()

    def build_mother_list(self):
        self.mother_list = self.glade.get_widget("mother_list")
        self.mother_selection = self.mother_list.get_selection()
        self.mother_selection.connect('changed',self.mother_list_select_row)
        self.add_columns(self.mother_list)
        self.redrawm()
        
    def add_columns(self,tree):
        column = gtk.TreeViewColumn(_('Name'), self.renderer,text=0)
        column.set_resizable(gtk.TRUE)        
        column.set_clickable(gtk.TRUE)
        column.set_sort_column_id(0)
        column.set_min_width(225)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('ID'), self.renderer,text=1)
        column.set_resizable(gtk.TRUE)        
        column.set_clickable(gtk.TRUE)
        column.set_sort_column_id(1)
        column.set_min_width(75)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('Birth date'), self.renderer,text=3)
        #column.set_resizable(gtk.TRUE)        
        column.set_clickable(gtk.TRUE)
        tree.append_column(column)

    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()

    def close(self,obj):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.top.destroy()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.child_windows[self] = self
        self.win_menu_item = gtk.MenuItem(self.title_text)
        self.win_menu_item.set_submenu(gtk.Menu())
        self.win_menu_item.show()
        self.parent.winsmenu.append(self.win_menu_item)
        self.winsmenu = self.win_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Choose Parents'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.win_menu_item.destroy()

    def present(self,obj):
        self.top.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-quick')

    def all_males_filter(self,person):
        return (person.get_gender() == RelLib.Person.male)

    def all_females_filter(self,person):
        return (person.get_gender() == RelLib.Person.female)

    def likely_father_filter(self,person):
        if person.get_gender() != RelLib.Person.male:
            return 0
        return self.likely_filter(person)

    def likely_mother_filter(self,person):
        if person.get_gender() != RelLib.Person.female:
            return 0
        return self.likely_filter(person)

    def likely_filter(self,person):
        birth_event = self.db.find_event_from_id(person.get_birth_id())
        if birth_event:
            pbday = birth_event.get_date_object()
        else:
            pbday = None
                
        death_event = self.db.find_event_from_id(person.get_death_id())
        if death_event:
            pdday = death_event.get_date_object()
        else:
            pdday = None
 
        if self.bday and self.bday.get_year_valid():
            if pbday and pbday.get_year_valid():
                # reject if parents birthdate + 10 > child birthdate
                if pbday.get_low_year()+10 > self.bday.get_high_year():
                    return 0

                # reject if parents birthdate + 90 < child birthdate 
                if pbday.get_high_year()+90 < self.bday.get_low_year():
                    return 0

                if pdday and pdday.get_year_valid():
                    # reject if parents birthdate + 10 > child deathdate 
                    if self.dday and pbday.get_low_year()+10 > self.dday.get_high_year():
                        return 0
                
        if self.dday and self.dday.get_year_valid():
            if pbday and pbday.get_year_valid():
                # reject if parents deathday + 3 < childs birth date 
                if pdday and self.bday and pdday.get_high_year()+3 < self.bday.get_low_year():
                    return 0

            if pdday and pdday.get_year_valid():
                # reject if parents deathday + 150 < childs death date 
                if pdday.get_high_year() + 150 < self.dday.get_low_year():
                    return 0
        return 1

    def redrawf(self):
        """Redraws the potential father list"""
        self.father_nsort = PeopleModel.PeopleModel(self.db, self.father_filter)
        if self.nosort:
            self.father_model = self.father_nsort
        else:
            self.father_model = gtk.TreeModelSort(self.father_nsort)
        self.father_list.set_model(self.father_model)
        if self.type == "Partners":
            self.flabel.set_label("<b>%s</b>" % _("Par_ent"))
        else:
            self.flabel.set_label("<b>%s</b>" % _("Fath_er"))

    def redrawm(self):
        """Redraws the potential mother list"""
        self.mother_nsort = PeopleModel.PeopleModel(self.db, self.mother_filter)
        if self.nosort:
            self.mother_model = self.mother_nsort
        else:
            self.mother_model = gtk.TreeModelSort(self.mother_nsort)
            
        self.mother_list.set_model(self.mother_model)
        if self.type == "Partners":
            self.mlabel.set_label("<b>%s</b>" % _("Pa_rent"))
        else:
            self.mlabel.set_label("<b>%s</b>" % _("Mothe_r"))

    def parent_relation_changed(self,obj):
        """Called everytime the parent relationship information is changegd"""
        self.old_type = self.type
        self.type = const.save_frel(unicode(obj.get_text()))
        if self.old_type == "Partners" or self.type == "Partners":
            self.redrawf()
            self.redrawm()

    def showallf_toggled(self,obj):
        if self.father_filter == self.likely_father_filter:
            self.father_filter = self.all_males_filter
        else:
            self.father_filter = self.likely_father_filter
        self.redrawf()

    def showallm_toggled(self,obj):
        if self.mother_filter == self.likely_mother_filter:
            self.mother_filter = self.all_females_filter
        else:
            self.mother_filter = self.likely_mother_filter
        self.redrawm()
        
    def find_family(self,father_id,mother_id,trans):
        """
        Finds the family associated with the father and mother.
        If one does not exist, it is created.
        """
        if not father_id and not mother_id:
            return None
	
        for family_id in self.db.get_family_keys():
            family = self.db.find_family_from_id(family_id)
            if family.get_father_id() == father_id and family.get_mother_id() == mother_id:
                family.add_child_id(self.person.get_id())
                self.db.commit_family(family,trans)
                return family
            elif family.get_father_id() == mother_id and family.get_mother_id() == father_id:
                family.add_child_id(self.person.get_id())
                self.db.commit_family(family,trans)
                return family

        family = self.db.new_family(trans)
        family.set_father_id(father_id)
        family.set_mother_id(mother_id)
        family.add_child_id(self.person.get_id())

        if father_id:
            self.father = self.db.try_to_find_person_from_id(father_id)
            self.father.add_family_id(family.get_id())
            self.db.commit_person(self.father,trans)
        if mother_id:
            self.mother = self.db.try_to_find_person_from_id(mother_id)
            self.mother.add_family_id(family.get_id())
            self.db.commit_person(self.mother,trans)

        self.db.commit_family(family,trans)
        return family

    def mother_list_select_row(self,obj):
        """Called when a row is selected in the mother list. Sets the
        active mother based off the id associated with the row."""
        
        idlist = self.get_selected_mother_ids()
        if idlist and idlist[0]:
            self.mother = self.db.get_person(idlist[0])
        else:
            self.mother = None

        if not self.parent_selected and self.mother:
            self.parent_selected = 1
            family_id_list = self.mother.get_family_id_list()
            if len(family_id_list) >= 1:
                family = self.db.find_family_from_id(family_id_list[0])
                father_id = family.get_father_id()
                self.father_selection.select(father_id)
                #self.father_model.center_selected()

    def father_select_function(self,store,path,iter,id_list):
        id_list.append(self.father_model.get_value(iter,1))

    def mother_select_function(self,store,path,iter,id_list):
        id_list.append(self.mother_model.get_value(iter,1))

    def get_selected_father_ids(self):
        mlist = []
        self.father_selection.selected_foreach(self.father_select_function,mlist)
        return mlist

    def get_selected_mother_ids(self):
        mlist = []
        self.mother_selection.selected_foreach(self.mother_select_function,mlist)
        return mlist

    def father_list_select_row(self,obj):
        """Called when a row is selected in the father list. Sets the
        active father based off the id associated with the row."""

        idlist = self.get_selected_father_ids()
        if idlist and idlist[0]:
            self.father = self.db.get_person(idlist[0])
        else:
            self.father = None

        if not self.parent_selected and self.father:
            self.parent_selected = 1
            family_id_list = self.father.get_family_id_list()
            if len(family_id_list) >= 1:
                family = self.db.find_family_from_id(family_id_list[0])
                mother_id = family.get_mother_id()
                mother = self.db.try_to_find_person_from_id(mother_id)
                sname = mother.get_primary_name().get_surname()
                tpath = self.mother_nsort.on_get_path(sname)
                self.mother_list.expand_row(tpath,0)
                path = self.mother_nsort.on_get_path(mother_id)
                self.mother_selection.select_path(path)
                self.mother_list.scroll_to_cell(path,None,1,0.5,0)

    def mother_list_select_row(self,obj):
        """Called when a row is selected in the father list. Sets the
        active father based off the id associated with the row."""

        idlist = self.get_selected_mother_ids()
        if idlist and idlist[0]:
            self.mother = self.db.get_person(idlist[0])
        else:
            self.mother = None

        if not self.parent_selected and self.mother:
            self.parent_selected = 1
            family_id_list = self.mother.get_family_id_list()
            if len(family_id_list) >= 1:
                family = self.db.find_family_from_id(family_id_list[0])
                father_id = family.get_mother_id()
                father = self.db.try_to_find_person_from_id(father_id)
                sname = father.get_primary_name().get_surname()
                tpath = self.father_nsort.on_get_path(sname)
                self.father_list.expand_row(tpath,0)
                path = self.father_nsort.on_get_path(father_id)
                self.father_selection.select_path(path)
                self.father_list.scroll_to_cell(path,None,1,0.5,0)

    def save_parents_clicked(self,obj):
        """
        Called with the OK button is pressed. Saves the selected people as parents
        of the main perosn.
        """
        try:
            mother_rel = const.child_relations.find_value(self.mother_rel.get_text())
        except KeyError:
            mother_rel = const.child_relations.find_value("Birth")

        try:
            father_rel = const.child_relations.find_value(self.father_rel.get_text())
        except KeyError:
            father_rel = const.child_relations.find_value("Birth")

        trans = self.db.start_transaction()
        if self.father or self.mother:
            if self.mother and not self.father:
                if self.mother.get_gender() == RelLib.Person.male:
                    self.father = self.mother
                    father_id = self.father.get_id()
                    self.mother = None
                    mother_id = None
                else:
                    mother_id = self.mother.get_id()
                    father_id = None
            elif self.father and not self.mother: 
                if self.father.get_gender() == RelLib.Person.female:
                    self.mother = self.father
                    self.father = None
                    mother_id = self.mother.get_id()
                    father_id = None
                else:
                    father_id = self.father.get_id()
                    mother_id = None
            elif self.mother.get_gender() != self.father.get_gender():
                if self.type == "Partners":
                    self.type = "Unknown"
                if self.father.get_gender() == RelLib.Person.female:
                    self.father, self.mother = self.mother, self.father
                father_id = self.father.get_id()
                mother_id = self.mother.get_id()
            else:
                self.type = "Partners"
                father_id = self.father.get_id()
                mother_id = self.mother.get_id()
            self.family = self.find_family(father_id,mother_id,trans)
        else:    
            self.family = None

        if self.family:
            if self.person.get_id() in (father_id,mother_id):
                ErrorDialog(_("Error selecting a child"),
                            _("A person cannot be linked as his/her own parent"),
                            self.top)
                return
            self.family.add_child_id(self.person.get_id())
            self.family.set_relationship(self.type)
            self.change_family_type(self.family,mother_rel,father_rel)
            self.db.commit_family(self.family,trans)
        self.family_update(None)
        self.db.add_transaction(trans,_("Choose Parents"))
        self.close(obj)

    def add_new_parent(self,epo):
        """Adds a new person to either the father list or the mother list,
        depending on the gender of the person."""

        person = epo.person
        id = person.get_id()

        if id == "":
            id = self.db.add_person(person)
        else:
            self.db.add_person_no_map(person,id)

        self.type = const.save_frel(unicode(self.prel.get_text()))
        dinfo = self.db.get_person_display(id)
        rdata = [dinfo[0],dinfo[1],dinfo[3],dinfo[5],dinfo[6]]

        if self.type == "Partners":
            self.parent_relation_changed(self.prel)
        elif person.get_gender() == RelLib.Person.male:
            self.father_model.add(rdata,None,1)
            self.father_model.center_selected()
        else:
            self.mother_model.add(rdata,None,1)
            self.mother_model.center_selected()
        self.full_update()
        
    def add_parent_clicked(self,obj):
        """Called with the Add New Person button is pressed. Calls the QuickAdd
        class to create a new person."""
        
        person = RelLib.Person()
        person.set_gender(RelLib.Person.male)
        
        try:
            import EditPerson
            EditPerson.EditPerson(self, person,self.db,self.add_new_parent)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

    def change_family_type(self,family,mother_rel,father_rel):
        """
        Changes the family type of the specified family. If the family
        is None, the the relationship type shoud be deleted.
        """
        family_id = family.get_id()
        if self.person.get_id() not in family.get_child_id_list():
            family.add_child_id(self.person.get_id())
        for fam in self.person.get_parent_family_id_list():
            if family_id == fam[0]:
                if mother_rel == fam[1] and father_rel == fam[2]:
                    return
                if mother_rel != fam[1] or father_rel != fam[2]:
                    self.person.remove_parent_family_id(family.get_id())
                    self.person.add_parent_family_id(family.get_id(),mother_rel,father_rel)
                    break
        else:
            self.person.add_parent_family_id(family.get_id(),mother_rel,father_rel)

        trans = self.db.start_transaction()
        self.db.commit_person(self.person,trans)
        self.db.commit_family(family,trans)
        if self.father:
            self.db.commit_person(self.father,trans)
        if self.mother:
            self.db.commit_person(self.mother,trans)
        self.db.add_transaction(trans,_("Choose Parents"))

class ModifyParents:
    def __init__(self,db,person,family_id,family_update,full_update,parent_window=None):
        """
        Creates a ChoosePerson dialog box.

        db - database associated the person
        person - person whose parents we are selecting
        family - current family
        family_update - task that updates the family display
        full_update - task that updates the main display 
        """
        self.db = db
        self.person = person
        self.family = self.db.find_family_from_id(family_id)
        self.family_update = family_update
        self.full_update = full_update
        
        self.father = self.db.try_to_find_person_from_id(self.family.get_father_id())
        self.mother = self.db.try_to_find_person_from_id(self.family.get_mother_id())

        self.glade = gtk.glade.XML(const.gladeFile,"modparents","gramps")
        self.top = self.glade.get_widget("modparents")
        self.title = self.glade.get_widget("title")

        title = _("Modify the Parents of %s") % GrampsCfg.nameof(self.person)
        Utils.set_titles(self.top, self.title, title, _("Modify Parents"))
        
        self.mother_rel = self.glade.get_widget("mrel")
        self.father_rel = self.glade.get_widget("frel")
        self.flabel = self.glade.get_widget("flabel")
        self.mlabel = self.glade.get_widget("mlabel")

        self.orig_mrel = _("Birth")
        self.orig_frel = _("Birth")
        for (f,mr,fr) in self.person.get_parent_family_id_list():
            if f == self.family.get_id():
                self.orig_mrel = _(mr)
                self.orig_frel = _(fr)

        self.mother_rel.set_text(self.orig_mrel)
        self.father_rel.set_text(self.orig_frel)

        self.glade.signal_autoconnect({
            "on_parents_help_clicked"  : self.on_help_clicked,
            })

        self.title.set_use_markup(gtk.TRUE)

        if self.family.get_relationship() == "Partners":
            self.mlabel.set_label('<b>%s</b>' % _("Parent"))
            self.flabel.set_label('<b>%s</b>' % _("Parent"))
        else:
            self.mlabel.set_label('<b>%s</b>' % _("Mother"))
            self.flabel.set_label('<b>%s</b>' % _("Father"))


        if self.father:
            fname = self.father.get_primary_name().get_name()
            self.glade.get_widget("fname").set_text(fname)
        else:
            self.father_rel.set_sensitive(0)
            
        if self.mother:
            mname = self.mother.get_primary_name().get_name()
            self.glade.get_widget("mname").set_text(mname)
        else:
            self.mother_rel.set_sensitive(0)

        self.pref = self.glade.get_widget('preferred')
        if len(self.person.get_parent_family_id_list()) > 1:
            self.glade.get_widget('pref_label').show()
            self.pref.show()
            if self.family == self.person.get_parent_family_id_list()[0]:
                self.pref.set_active(1)
            else:
                self.pref.set_active(0)

        if parent_window:
            self.top.set_transient_for(parent_window)
        self.val = self.top.run()
        if self.val == gtk.RESPONSE_OK:
            self.save_parents_clicked()
        self.top.destroy()


    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-spec-par')
        self.val = self.top.run()

    def save_parents_clicked(self):
        """
        Called with the OK button nis pressed. Saves the selected people as parents
        of the main perosn.
        """
        mother_rel = const.child_relations.find_value(self.mother_rel.get_text())
        father_rel = const.child_relations.find_value(self.father_rel.get_text())
        mod = 0

        if mother_rel != self.orig_mrel or father_rel != self.orig_frel:
            self.person.remove_parent_family_id(self.family.get_id())
            self.person.add_parent_family_id(self.family.get_id(),mother_rel,father_rel)
            mod = 1

        if len(self.person.get_parent_family_id_list()):
            make_pref = self.pref.get_active()

            plist = self.person.get_parent_family_id_list()
            if make_pref:
                if self.family != plist[0]:
                    self.person.set_main_parent_family_id(self.family.get_id())
                    mod = 1
            else:
                if self.family == plist[0]:
                    self.person.set_main_parent_family_id(plist[0])
                    mod = 1

        if mod:
            trans = self.db.start_transaction()
            self.db.commit_person(self.person,trans)
            self.db.add_transaction(trans,_("Modify Parents"))
            self.family_update(None)
