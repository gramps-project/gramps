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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade
import gtk.gdk
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
        self.parent = parent
        self.db = db
        self.child_windows = {}
        self.person = self.db.get_person_from_handle(person.get_handle())
        if family:
            self.family = self.db.get_family_from_handle(family.get_handle())
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

        birth_event = self.db.get_event_from_handle(self.person.get_birth_handle())
        if birth_event:
            self.bday = birth_event.get_date_object()
        else:
            self.bday = None

        death_event = self.db.get_event_from_handle(self.person.get_death_handle())
        if death_event:
            self.dday = death_event.get_date_object()
        else:
            self.dday = None

        if self.family:
            self.father = self.family.get_father_handle()
            self.mother = self.family.get_mother_handle()
        else:
            self.mother = None
            self.father = None

        self.glade = gtk.glade.XML(const.gladeFile,"familyDialog","gramps")
        self.top = self.glade.get_widget("familyDialog")

        self.title_text = _("Choose the Parents of %s") % \
                          GrampsCfg.get_nameof()(self.person)
        Utils.set_titles(self.top,self.glade.get_widget('title'),
                         self.title_text,_('Choose Parents'))
        
        self.mother_rel = self.glade.get_widget("mrel")
        self.father_rel = self.glade.get_widget("frel")
        self.prel = self.glade.get_widget("prel_combo")
        self.title = self.glade.get_widget("chooseTitle")
        self.father_list = self.glade.get_widget("father_list")
        self.mother_list = self.glade.get_widget("mother_list")
        self.flabel = self.glade.get_widget("flabel")
        self.mlabel = self.glade.get_widget("mlabel")
        self.showallf = self.glade.get_widget('showallf')
        self.showallm = self.glade.get_widget('showallm')
        
        self.build_father_list()
        self.build_mother_list()

        if gtk.gdk.screen_height() > 700:
            self.father_list.set_size_request(-1,150)
            self.mother_list.set_size_request(-1,150)

        for (f,mr,fr) in self.person.get_parent_family_handle_list():
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
            self.type = RelLib.Family.MARRIED

        self.prel.set_active(self.type)
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
        self.father_selection = self.father_list.get_selection()
        self.father_selection.connect('changed',self.father_list_select_row)
        self.add_columns(self.father_list)
        self.redrawf()

    def build_mother_list(self):
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
        if self.exclude.has_key(person.get_handle()):
            return 0
        return self.likely_filter(person)

    def likely_mother_filter(self,person):
        if person.get_gender() != RelLib.Person.female:
            return 0
        if self.exclude.has_key(person.get_handle()):
            return 0
        return self.likely_filter(person)

    def likely_filter(self,person):
        if person.get_handle() == self.person.get_handle():
            return 0
        birth_event = self.db.get_event_from_handle(person.get_birth_handle())
        if birth_event:
            pbday = birth_event.get_date_object()
        else:
            pbday = None
                
        death_event = self.db.get_event_from_handle(person.get_death_handle())
        if death_event:
            pdday = death_event.get_date_object()
        else:
            pdday = None
 
        if self.bday and self.bday.get_year_valid():
            if pbday and pbday.get_year_valid():
                # reject if parents birthdate + 10 > child birthdate
                if pbday.get_year()+10 > self.bday.get_high_year():
                    return 0

                # reject if parents birthdate + 90 < child birthdate 
                if pbday.get_high_year()+90 < self.bday.get_year():
                    return 0

                if pdday and pdday.get_year_valid():
                    # reject if parents birthdate + 10 > child deathdate 
                    if self.dday and pbday.get_year()+10 > self.dday.get_high_year():
                        return 0
                
        if self.dday and self.dday.get_year_valid():
            if pbday and pbday.get_year_valid():
                # reject if parents deathday + 3 < childs birth date 
                if pdday and self.bday and pdday.get_high_year()+3 < self.bday.get_year():
                    return 0

            if pdday and pdday.get_year_valid():
                # reject if parents deathday + 150 < childs death date 
                if pdday.get_high_year() + 150 < self.dday.get_year():
                    return 0
        return 1

    def build_exclude_list(self):
        self.exclude = { self.person.get_handle() : 1 }
        for family_handle in self.person.get_family_handle_list():
            fam = self.db.get_family_from_handle(family_handle)
            for handle in [fam.get_father_handle(), fam.get_mother_handle()] + \
                    fam.get_child_handle_list():
                if handle:
                    self.exclude[handle] = 1

    def redrawf(self):
        """Redraws the potential father list"""
        self.build_exclude_list()
        self.father_nsort = PeopleModel.PeopleModel(self.db)
        
        cursor = self.db.get_person_cursor()
        data = cursor.first()
        while data:
            person = RelLib.Person()
            person.unserialize(data[1])
            visible = self.father_filter(person)
            if visible:
                self.father_nsort.set_visible(data[0],visible)
            data = cursor.next()
        cursor.close()

        self.father_model = gtk.TreeModelSort(self.father_nsort)
        self.father_list.set_model(self.father_model)
        
        if self.type == RelLib.Family.CIVIL_UNION:
            self.flabel.set_label("<b>%s</b>" % _("Par_ent"))
        else:
            self.flabel.set_label("<b>%s</b>" % _("Fath_er"))

    def redrawm(self):
        """Redraws the potential mother list"""
        self.mother_nsort = PeopleModel.PeopleModel(self.db)
        self.build_exclude_list()
        
        cursor = self.db.get_person_cursor()
        data = cursor.first()
        while data:
            person = RelLib.Person()
            person.unserialize(data[1])
            visible = self.mother_filter(person)
            if visible:
                self.mother_nsort.set_visible(data[0],visible)
            data = cursor.next()
        cursor.close()

        self.mother_model = gtk.TreeModelSort(self.mother_nsort)
        self.mother_list.set_model(self.mother_model)
        
        if self.type == RelLib.Family.CIVIL_UNION:
            self.mlabel.set_label("<b>%s</b>" % _("Pa_rent"))
        else:
            self.mlabel.set_label("<b>%s</b>" % _("Mothe_r"))

    def parent_relation_changed(self,obj):
        """Called everytime the parent relationship information is changed"""
        self.old_type = self.type
        self.type = self.prel.get_active()
        if self.old_type == RelLib.Family.CIVIL_UNION or self.type == RelLib.Family.CIVIL_UNION:
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
        
    def find_family(self,father_handle,mother_handle,trans):
        """
        Finds the family associated with the father and mother.
        If one does not exist, it is created.
        """
        if not father_handle and not mother_handle:
            return None
	
        for family_handle in self.db.get_family_handles():
            family = self.db.get_family_from_handle(family_handle)
            if family.get_father_handle() == father_handle and family.get_mother_handle() == mother_handle:
                family.add_child_handle(self.person.get_handle())
                self.db.commit_family(family,trans)
                return family
            elif family.get_father_handle() == mother_handle and family.get_mother_handle() == father_handle:
                family.add_child_handle(self.person.get_handle())
                self.db.commit_family(family,trans)
                return family

        family = RelLib.Family()
        family.set_father_handle(father_handle)
        family.set_mother_handle(mother_handle)
        family.add_child_handle(self.person.get_handle())
        self.db.add_family(family,trans)

        if father_handle:
            self.father = self.db.get_person_from_handle(father_handle)
            self.father.add_family_handle(family.get_handle())
            self.db.commit_person(self.father,trans)
        if mother_handle:
            self.mother = self.db.get_person_from_handle(mother_handle)
            self.mother.add_family_handle(family.get_handle())
            self.db.commit_person(self.mother,trans)

        self.db.commit_family(family,trans)
        return family

    def father_select_function(self,store,path,iter,id_list):
        if len(path) != 1:
            val = self.father_model.get_value(iter,PeopleModel.COLUMN_INT_ID)
            id_list.append(val)

    def mother_select_function(self,store,path,iter,id_list):
        if len(path) != 1:
            val = self.mother_model.get_value(iter,PeopleModel.COLUMN_INT_ID)
            id_list.append(val)

    def get_selected_father_handles(self):
        mlist = []
        self.father_selection.selected_foreach(self.father_select_function,mlist)
        return mlist

    def get_selected_mother_handles(self):
        mlist = []
        self.mother_selection.selected_foreach(self.mother_select_function,mlist)
        return mlist

    def father_list_select_row(self,obj):
        """Called when a row is selected in the father list. Sets the
        active father based off the id associated with the row."""

        idlist = self.get_selected_father_handles()
        if idlist and idlist[0]:
            self.father = self.db.get_person_from_handle(idlist[0])
        else:
            self.father = None

        if not self.parent_selected and self.father:
            self.parent_selected = 1
            family_handle_list = self.father.get_family_handle_list()
            if len(family_handle_list) >= 1:
                family = self.db.get_family_from_handle(family_handle_list[0])
                mother_handle = family.get_mother_handle()
                mother = self.db.get_person_from_handle(mother_handle)
                sname = mother.get_primary_name().get_surname()
                tpath = self.mother_nsort.on_get_path(sname)
                self.mother_list.expand_row(tpath,0)
                path = self.mother_nsort.on_get_path(mother_handle)
                self.mother_selection.select_path(path)
                self.mother_list.scroll_to_cell(path,None,1,0.5,0)

    def mother_list_select_row(self,obj):
        """Called when a row is selected in the father list. Sets the
        active father based off the id associated with the row."""

        idlist = self.get_selected_mother_handles()
        if idlist and idlist[0]:
            self.mother = self.db.get_person_from_handle(idlist[0])
        else:
            self.mother = None

        if not self.parent_selected and self.mother:
            self.parent_selected = 1
            family_handle_list = self.mother.get_family_handle_list()
            if len(family_handle_list) >= 1:
                family = self.db.get_family_from_handle(family_handle_list[0])
                father_handle = family.get_mother_handle()
                father = self.db.get_person_from_handle(father_handle)
                sname = father.get_primary_name().get_surname()
                tpath = self.father_nsort.on_get_path(sname)
                self.father_list.expand_row(tpath,0)
                path = self.father_nsort.on_get_path(father_handle)
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

        trans = self.db.transaction_begin()
        if self.father or self.mother:
            if self.mother and not self.father:
                if self.mother.get_gender() == RelLib.Person.male:
                    self.father = self.mother
                    father_handle = self.father.get_handle()
                    self.mother = None
                    mother_handle = None
                else:
                    mother_handle = self.mother.get_handle()
                    father_handle = None
            elif self.father and not self.mother: 
                if self.father.get_gender() == RelLib.Person.female:
                    self.mother = self.father
                    self.father = None
                    mother_handle = self.mother.get_handle()
                    father_handle = None
                else:
                    father_handle = self.father.get_handle()
                    mother_handle = None
            elif self.mother.get_gender() != self.father.get_gender():
                if self.type == "Partners":
                    self.type = "Unknown"
                if self.father.get_gender() == RelLib.Person.female:
                    self.father, self.mother = self.mother, self.father
                father_handle = self.father.get_handle()
                mother_handle = self.mother.get_handle()
            else:
                self.type = "Partners"
                father_handle = self.father.get_handle()
                mother_handle = self.mother.get_handle()
            self.family = self.find_family(father_handle,mother_handle,trans)
        else:    
            self.family = None

        if self.family:
            if self.person.get_handle() in (father_handle,mother_handle):
                ErrorDialog(_("Error selecting a child"),
                            _("A person cannot be linked as his/her own parent"),
                            self.top)
                return
            self.family.add_child_handle(self.person.get_handle())
            self.family.set_relationship(self.type)
            self.change_family_type(self.family,mother_rel,father_rel)
            self.db.commit_family(self.family,trans)
        self.family_update(None)
        self.db.transaction_commit(trans,_("Choose Parents"))
        self.close(obj)

    def add_new_parent(self,epo,val):
        """Adds a new person to either the father list or the mother list,
        depending on the gender of the person."""

        person = epo.person
        handle = person.get_handle()
        name = person.get_primary_name().get_surname()
        self.type = self.prel.get_active()

        if self.type == RelLib.Family.CIVIL_UNION:
            self.parent_relation_changed(self.prel)
        elif person.get_gender() == RelLib.Person.male:
            self.redrawf()
            path = self.father_nsort.on_get_path(handle)
            top_path = self.father_nsort.on_get_path(name)
            self.father_list.expand_row(top_path,0)
            self.father_selection.select_path(path)
            self.father_list.scroll_to_cell(path,None,1,0.5,0)
        else:
            self.redrawm()
            path = self.mother_nsort.on_get_path(handle)
            top_path = self.mother_nsort.on_get_path(name)
            self.mother_list.expand_row(top_path,0)
            self.mother_selection.select_path(path)
            self.mother_list.scroll_to_cell(path,None,1,0.5,0)
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
        family_handle = family.get_handle()
        if self.person.get_handle() not in family.get_child_handle_list():
            family.add_child_handle(self.person.get_handle())
        for fam in self.person.get_parent_family_handle_list():
            if family_handle == fam[0]:
                if mother_rel == fam[1] and father_rel == fam[2]:
                    return
                if mother_rel != fam[1] or father_rel != fam[2]:
                    self.person.remove_parent_family_handle(family.get_handle())
                    self.person.add_parent_family_handle(family.get_handle(),mother_rel,father_rel)
                    break
        else:
            self.person.add_parent_family_handle(family.get_handle(),mother_rel,father_rel)

        trans = self.db.transaction_begin()
        self.db.commit_person(self.person,trans)
        self.db.commit_family(family,trans)
        if self.father:
            self.db.commit_person(self.father,trans)
        if self.mother:
            self.db.commit_person(self.mother,trans)
        self.db.transaction_commit(trans,_("Choose Parents"))

class ModifyParents:
    def __init__(self,db,person,family_handle,family_update,full_update,parent_window=None):
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
        self.family = self.db.get_family_from_handle(family_handle)
        self.family_update = family_update
        self.full_update = full_update
        
        self.father = self.db.get_person_from_handle(self.family.get_father_handle())
        self.mother = self.db.get_person_from_handle(self.family.get_mother_handle())

        self.glade = gtk.glade.XML(const.gladeFile,"modparents","gramps")
        self.top = self.glade.get_widget("modparents")
        self.title = self.glade.get_widget("title")

        title = _("Modify the Parents of %s") % GrampsCfg.get_nameof()(self.person)
        Utils.set_titles(self.top, self.title, title, _("Modify Parents"))
        
        self.mother_rel = self.glade.get_widget("mrel")
        self.father_rel = self.glade.get_widget("frel")
        self.flabel = self.glade.get_widget("flabel")
        self.mlabel = self.glade.get_widget("mlabel")

        self.orig_mrel = _("Birth")
        self.orig_frel = _("Birth")
        for (f,mr,fr) in self.person.get_parent_family_handle_list():
            if f == self.family.get_handle():
                self.orig_mrel = _(mr)
                self.orig_frel = _(fr)

        self.mother_rel.set_text(self.orig_mrel)
        self.father_rel.set_text(self.orig_frel)

        self.glade.signal_autoconnect({
            "on_parents_help_clicked"  : self.on_help_clicked,
            })

        self.title.set_use_markup(gtk.TRUE)

        if self.family.get_relationship() == RelLib.Family.CIVIL_UNION:
            self.mlabel.set_label("<b>%s</b>" % _("Pa_rent"))
            self.flabel.set_label("<b>%s</b>" % _("Par_ent"))
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
        if len(self.person.get_parent_family_handle_list()) > 1:
            self.glade.get_widget('pref_label').show()
            self.pref.show()
            if self.family == self.person.get_parent_family_handle_list()[0]:
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
            self.person.remove_parent_family_handle(self.family.get_handle())
            self.person.add_parent_family_handle(self.family.get_handle(),mother_rel,father_rel)
            mod = 1

        if len(self.person.get_parent_family_handle_list()):
            make_pref = self.pref.get_active()

            plist = self.person.get_parent_family_handle_list()
            if make_pref:
                if self.family != plist[0]:
                    self.person.set_main_parent_family_handle(self.family.get_handle())
                    mod = 1
            else:
                if self.family == plist[0]:
                    self.person.set_main_parent_family_handle(plist[0])
                    mod = 1

        if mod:
            trans = self.db.transaction_begin()
            self.db.commit_person(self.person,trans)
            self.db.transaction_commit(trans,_("Modify Parents"))
            self.family_update(None)
