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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import sort
from intl import gettext as _
import Utils
import GrampsCfg
from RelLib import Person
from QuestionDialog import QuestionDialog

import AddSpouse
import SelectChild
import DisplayTrace
import Marriage
import ChooseParents

#-------------------------------------------------------------------------
#
# FamilyView
#
#-------------------------------------------------------------------------
class FamilyView:

    def __init__(self,parent):
        self.parent = parent
        self.top = parent.gtop
        self.ap_data = self.top.get_widget('ap_data').get_buffer()

        self.swap_btn = self.top.get_widget('swap_spouse_btn')
        self.add_spouse_btn = self.top.get_widget('add_spouse')
        self.remove_spouse_btn = self.top.get_widget('remove_spouse')

        self.ap_parents = self.top.get_widget('ap_parents')
        self.ap_parents_model = gtk.ListStore(gobject.TYPE_STRING)
        self.ap_parents.set_model(self.ap_parents_model)
        self.ap_selection = self.ap_parents.get_selection()
        column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.ap_parents.append_column(column)
        self.ap_parents.connect('button-press-event',self.edit_ap_parents)

        self.sp_parents = self.top.get_widget('sp_parents')
        self.sp_parents_model = gtk.ListStore(gobject.TYPE_STRING)
        self.sp_parents.set_model(self.sp_parents_model)
        self.sp_selection = self.sp_parents.get_selection()
        column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.sp_parents.append_column(column)
        self.sp_parents.connect('button-press-event',self.edit_sp_parents)

        self.spouse_list = self.top.get_widget('sp_list')
        self.spouse_model = gtk.ListStore(gobject.TYPE_STRING)
        self.spouse_list.set_model(self.spouse_model)
        self.spouse_selection = self.spouse_list.get_selection()
        self.spouse_selection.connect('changed',self.spouse_changed)

        self.top.get_widget('add_parents').connect('clicked',self.add_parents_clicked)
        self.top.get_widget('del_parents').connect('clicked',self.del_parents_clicked)
        self.top.get_widget('add_spparents').connect('clicked',self.add_sp_parents)
        self.top.get_widget('del_spparents').connect('clicked',self.del_sp_parents)
        self.top.get_widget('fam_back').connect('clicked',self.child_back)
        self.top.get_widget('del_child_btn').connect('clicked',self.remove_child_clicked)
        self.top.get_widget('add_child_btn').connect('clicked',self.add_child_clicked)
        
        column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.spouse_list.append_column(column)
        self.selected_spouse = None

        self.child_list = self.top.get_widget('chlist')
        self.child_model = gtk.ListStore(gobject.TYPE_INT,   gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING)
        self.child_selection = self.child_list.get_selection()

        self.child_list.connect('button-press-event',self.on_child_list_button_press)

        self.top.get_widget('ap_parents_btn').connect('clicked',self.ap_parents_clicked)
        self.top.get_widget('sp_parents_btn').connect('clicked',self.sp_parents_clicked)
        
        self.swap_btn.connect('clicked',self.spouse_swap)
        self.remove_spouse_btn.connect('clicked',self.remove_spouse)
        self.add_spouse_btn.connect('clicked',self.add_spouse)
        self.spouse_list.connect('button-press-event',self.edit_releationship)


        self.child_list.set_model(self.child_model)
        self.child_list.set_search_column(0)
        self.child_selection = self.child_list.get_selection()

        Utils.build_columns(self.child_list,
                            [ (_(''),30,0), (_('Name'),250,1), (_('ID'),50,2),
                              (_('Gender'),100,3), (_('Birth Date'),150,4),
                              (_('Status'),150,5), ('',0,6) ])

    def on_child_list_button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            model, iter = self.child_selection.get_selected()
            if iter:
                id = self.child_model.get_value(iter,2)
                self.parent.load_person(self.parent.db.getPerson(id))

    def spouse_changed(self,obj):
        model, iter = obj.get_selected()
        if not iter:
            self.display_marriage(None)
        else:
            row = model.get_path(iter)
            self.display_marriage(self.person.getFamilyList()[row[0]])
            
    def edit_releationship(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
           if self.person:
               try:
                   Marriage.Marriage(self.family,self.parent.db,
                                     self.parent.new_after_edit)
               except:
                   DisplayTrace.DisplayTrace()
        
    def add_spouse(self,obj):
        if not self.person:
            return
        try:
            AddSpouse.AddSpouse(self.parent.db, self.person,
                                self.load_family,
                                self.parent.redisplay_person_list)
        except:
            DisplayTrace.DisplayTrace()

    def add_child_clicked(self,obj):
        if not self.person:
            return
        try:
            SelectChild.SelectChild(self.parent.db, self.family,
                                    self.person, self.load_family,
                                    self.parent.update_person_list)
        except:
            DisplayTrace.DisplayTrace()

    def remove_child_clicked(self,obj):
        if not self.family or not self.person:
            return

        model, iter = self.child_selection.get_selected()
        if not iter:
            return

        id = self.child_model.get_value(iter,2)
        child = self.parent.db.getPerson(id)

        self.family.removeChild(child)
        child.removeAltFamily(child)
        
        if len(self.family.getChildList()) == 0:
            if self.family.getFather() == None:
                self.parent.delete_family_from(self.family.getMother())
            elif self.family.getMother() == None:
                self.parent.delete_family_from(self.family.getFather())

        Utils.modified()
        self.load_family()

    def remove_spouse(self,obj):
        if self.selected_spouse:
            name = self.selected_spouse.getPrimaryName().getRegularName()
            QuestionDialog(_('Delete Spouse'),
                           _('Do you wish to remove %s as a spouse?') % name,
                           self.really_remove_spouse)
                       
    def really_remove_spouse(self):
        """Delete the currently selected spouse from the family"""
        if self.person == None:
            return
        if self.selected_spouse == self.family.getFather():
            self.family.setMother(None)
        else:
            self.family.setFather(None)

        if self.selected_spouse:
            self.selected_spouse.removeFamily(self.family)

        if len(self.family.getChildList()) == 0:
            self.person.removeFamily(self.family)
            self.parent.db.deleteFamily(self.family)
            if len(self.person.getFamilyList()) > 0:
                self.load_family(self.person.getFamilyList()[0])
            else:
                self.load_family()
        else:
            self.load_family()

        if len(self.person.getFamilyList()) <= 1:
            self.spouse_selection.set_mode(gtk.SELECTION_NONE)

        Utils.modified()

    def spouse_swap(self,obj):
        if self.selected_spouse:
            self.parent.active_person = self.selected_spouse
            self.load_family()

    def ap_parents_clicked(self,obj):
        self.change_families(self.person)
            
    def sp_parents_clicked(self,obj):
        self.change_families(self.selected_spouse)

    def change_families(self,person):
        if not person:
            return
        plist = person.getParentList()

        if len(plist) == 0:
            return
        if len(plist) == 1:
            family,m,r = plist[0]
        else:
            model, iter = self.ap_selection.get_selected()
            path = model.get_path(iter)
            family,m,r = plist[path[0]]

        if family.getFather():
            person = family.getFather()
        else:
            person = family.getMother()
        self.parent.change_active_person(person)
        self.load_family(family)
        

    def load_family(self,family=None):
        self.person = self.parent.active_person
        if not self.person:
            return
        
        n = "%s\n\tb. %s\n\td. %s" % (self.person.getPrimaryName().getName(),
                                      self.person.getBirth().getDate(),
                                      self.person.getDeath().getDate())
        self.ap_data.set_text(n,len(n))

        self.selected_spouse = None
        self.spouse_model.clear()
        splist = self.person.getFamilyList()
        f = None
        first_family = None
        first_spouse = None
        for f in splist:
            if not f:
                continue
            if f.getFather() == self.person:
                sp = f.getMother()
            else:
                sp = f.getFather()

            iter = self.spouse_model.append()
            if f == family:
                first_spouse = sp
                first_family = f
            elif first_spouse == None:
                first_spouse = sp
                first_family = f
                
                if len(splist) > 1:
                    self.spouse_selection.set_mode(gtk.SELECTION_SINGLE)
                    self.spouse_selection.select_iter(iter)
                else:
                    self.spouse_selection.set_mode(gtk.SELECTION_NONE)

            if sp:
                if f.getMarriage():
                    mdate = " - %s" % f.getMarriage().getDate()
                else:
                    mdate = ""
                v = "%s\n\t%s%s" % (sp.getPrimaryName().getName(),
                                    f.getRelationship(),mdate)
                self.spouse_model.set(iter,0,v)
            else:
                self.spouse_model.set(iter,0,"unknown\n")

        if first_family:
            self.display_marriage(first_family)

        self.update_list(self.ap_parents_model,self.ap_parents,self.person)
        self.family = first_family

    def update_list(self,model,tree,person):
        model.clear()
        sel = None
        selection = tree.get_selection()
        list = person.getParentList()

        for (f,mrel,frel) in list:

            father = self.nameof(_("Father"),f.getFather(),frel)
            mother = self.nameof(_("Mother"),f.getMother(),mrel)

            iter = model.append()
            if not sel:
                sel = iter
            v = "%s\n%s" % (father,mother)
            model.set(iter,0,v)
        if len(list) > 1:
            selection.set_mode(gtk.SELECTION_SINGLE)
            selection.select_iter(sel)
        else:
            selection.set_mode(gtk.SELECTION_NONE)
            
    def nameof(self,l,p,mode):
        if p:
            n = p.getPrimaryName().getName()
            return "%s: %s\n\tRelationship: %s" % (l,n,mode)
        else:
            return "unknown\n"

    def display_marriage(self,family):

        self.child_model.clear()
        if not family:
            return
        else:
            self.family = family

        if family.getFather() == self.person:
            self.selected_spouse = family.getMother()
        else:
            self.selected_spouse = family.getFather()

        if self.selected_spouse:
            self.update_list(self.sp_parents_model,self.sp_parents,
                             self.selected_spouse)

        i = 0
        fiter = None
        child_list = list(family.getChildList())
        child_list.sort(sort.by_birthdate)

        self.child_map = {}

        attr = ""
        for child in child_list:
            status = _("Unknown")
            if child.getGender() == Person.male:
                gender = const.male
            elif child.getGender() == Person.female:
                gender = const.female
            else:
                gender = const.unknown
            for fam in child.getParentList():
                if fam[0] == family:
                    if self.person == family.getFather():
                        status = "%s/%s" % (_(fam[2]),_(fam[1]))
                    else:
                        status = "%s/%s" % (_(fam[1]),_(fam[2]))

            iter = self.child_model.append()
            self.child_map[iter] = child.getId()
            
            if fiter == None:
                fiter = self.child_model.get_path(iter)
            self.child_model.set(iter,
                                 0,(i+1),
                                 1,GrampsCfg.nameof(child),
                                 2,child.getId(),
                                 3,gender,
                                 4,Utils.birthday(child),
                                 5,status,
                                 6,attr)
                
    def edit_ap_parents(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.parent_editor(self.person,self.ap_selection)

    def edit_sp_parents(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.parent_editor(self.selected_spouse,self.sp_selection)

    def add_parents_clicked(self,obj):
        self.parent_add(self.person)

    def add_sp_parents(self,obj):
        if self.selected_spouse:
            self.parent_add(self.selected_spouse)

    def del_parents_clicked(self,obj):
        if len(self.person.getParentList()) == 0:
            return
        QuestionDialog(_('Delete Parents'),
                       _('Do you wish to remove the selected parents?'),
                       self.really_del_parents)
        
    def really_del_parents(self):
        self.parent_deleter(self.person,self.ap_selection)

    def del_sp_parents(self,obj):
        if not self.selected_spouse or len(self.selected_spouse.getParentList()) == 0:
            return
        QuestionDialog(_('Delete Parents'),
                       _('Do you wish to remove the selected parents?'),
                       self.really_del_parents)

    def really_del_parents(self):
        self.parent_deleter(self.selected_spouse,self.sp_selection)

    def child_back(self,obj):
        """makes the currently select child the active person"""
        model, iter = self.child_selection.get_selected()
        if iter:
            id = self.child_model.get_value(iter,2)
            self.parent.change_active_person(self.parent.db.getPerson(id))
            self.load_family()

    def parent_editor(self,person,selection):
        if not person:
            return

        plist = person.getParentList()

        if len(plist) == 0:
            return
        elif len(plist) == 1:
            parents,mrel,frel = plist[0]
        else:
            model, iter = selection.get_selected()
            if not iter:
                return

            row = model.get_path(iter)
            parents,mrel,frel = plist[row[0]]

        try:
            ChooseParents.ModifyParents(self.parent.db,person,parents,
                                        self.load_family,self.parent.full_update)
        except:
            DisplayTrace.DisplayTrace()

    def parent_add(self,person):
        if not person:
            return
        try:
            ChooseParents.ChooseParents(self.parent.db,person,None,
                                        self.load_family,self.parent.full_update)
        except:
            DisplayTrace.DisplayTrace()
        
    def parent_deleter(self,person,selection):
        if not person:
            return
        plist = person.getParentList()
        if len(plist) == 0:
            return
        if len(plist) == 1:
            person.clearAltFamilyList()
        else:
            model, iter = selection.get_selected()
            if not iter:
                return

            row = model.get_path(iter)
            fam = person.getParentList()[row[0]]
            person.removeAltFamily(fam[0])
        Utils.modified()
        self.load_family()

        
        
