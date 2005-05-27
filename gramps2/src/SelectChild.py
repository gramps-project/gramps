# -*- coding: utf-8 -*-
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
import PeopleModel
import NameDisplay

from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# SelectChild
#
#-------------------------------------------------------------------------
class SelectChild:

    def __init__(self,parent,db,family,person,callback):
        self.parent = parent
        self.db = db
        self.callback = callback
        self.person = person
        self.family = family
        self.renderer = gtk.CellRendererText()
        self.xml = gtk.glade.XML(const.gladeFile,"select_child","gramps")
    
        if person:
            self.default_name = person.get_primary_name().get_surname().upper()
        else:
            self.default_name = ""

        self.xml.signal_autoconnect({
            "on_save_child_clicked"    : self.on_save_child_clicked,
            "on_child_help_clicked"    : self.on_child_help_clicked,
            "on_show_toggled"          : self.on_show_toggled,
            "destroy_passed_object"    : self.close,
            "on_select_child_delete_event" : self.on_delete_event,
            })

        self.select_child_list = {}
        self.top = self.xml.get_widget("select_child")
        title_label = self.xml.get_widget('title')

        Utils.set_titles(self.top,title_label,_('Add Child to Family'))
        
        self.add_child = self.xml.get_widget("childlist")

        self.mrel = self.xml.get_widget("mrel_combo")
        self.frel = self.xml.get_widget("frel_combo")

        self.build_list(self.mrel,const.CHILD_BIRTH)
        self.build_list(self.frel,const.CHILD_BIRTH)

        if self.family:
            father = self.db.get_person_from_handle(self.family.get_father_handle())
            mother = self.db.get_person_from_handle(self.family.get_mother_handle())
        else:
            if self.person.get_gender() == const.MALE:
                self.mrel.set_sensitive(False)
            else:
                self.frel.set_sensitive(False)

        self.refmodel = PeopleModel.PeopleModel(self.db)

        self.add_child.set_model(self.refmodel)
        self.redraw_child_list(2)
        self.add_itself_to_menu()
        self.add_columns(self.add_child)
        self.top.show()

    def build_list(self,opt_menu,sel):
        cell = gtk.CellRendererText()
        opt_menu.pack_start(cell,True)
        opt_menu.add_attribute(cell,'text',0)
        
        store = gtk.ListStore(str)
        for val in const.child_rel_list:
            store.append(row=[val])
        opt_menu.set_model(store)
        opt_menu.set_active(sel)

    def add_columns(self,tree):
        column = gtk.TreeViewColumn(_('Name'), self.renderer,text=0)
        column.set_resizable(True)        
        #column.set_clickable(True)
        column.set_min_width(225)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('ID'), self.renderer,text=1)
        column.set_resizable(True)        
        #column.set_clickable(True)
        column.set_min_width(75)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('Birth date'), self.renderer,text=3)
        #column.set_resizable(True)        
        column.set_clickable(True)
        tree.append_column(column)

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.top.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self] = self
        self.parent_menu_item = gtk.MenuItem(_('Add Child to Family'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.top.present()

    def on_child_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-quick')

    def redraw_child_list(self,filter):
        return
    
        birth = self.db.get_event_from_handle(self.person.get_birth_handle())
        death = self.db.get_event_from_handle(self.person.get_death_handle())
        if birth:
            bday = birth.get_date_object()
        else:
            bday = None
        if death:
            dday = death.get_date_object()
        else:
            dday = None

        slist = {}
        for f in self.person.get_parent_family_handle_list():
            if f:
                family = self.db.get_family_from_handle(f[0])
                if family.get_father_handle():
                    slist[family.get_father_handle()] = 1
                elif family.get_mother_handle():
                    slist[family.get_mother_handle()] = 1
                for c in family.get_child_handle_list():
                    slist[c] = 1
            
        person_list = []
        for key in self.db.get_person_handles(sort_handles=True):
            person = self.db.get_person_from_handle(key)
            if filter:
                if slist.has_key(key) or person.get_main_parents_family_handle():
                    continue
            
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
 
                if bday and bday.getYearValid():
                    if pbday and pbday.getYearValid():
                        # reject if child birthdate < parents birthdate + 10
                        if pbday.getLowYear() < bday.getHighYear()+10:
                            continue

                        # reject if child birthdate > parents birthdate + 90
                        if pbday.getLowYear() > bday.getHighYear()+90:
                            continue

                    if pdday and pdday.getYearValid():
                        # reject if child deathdate < parents birthdate+ 10
                        if pdday.getLowYear() < bday.getHighYear()+10:
                            continue
                
                if dday and dday.getYearValid():
                    if pbday and pbday.getYearValid():
                        # reject if childs birth date > parents deathday + 3
                        if pbday.getLowYear() > dday.getHighYear()+3:
                            continue

                    if pdday and pdday.getYearValid():
                        # reject if childs death date > parents deathday + 150
                        if pdday.getLowYear() > dday.getHighYear() + 150:
                            continue
        
            person_list.append(person.get_handle())

        node = None
        for idval in person_list:
            person = self.db.get_person_from_handle(idval)
            name = NameDisplay.displayer.display(person)
            if person.gender == const.MALE:
                gender = _("male")
            elif person.gender == const.FEMALE:
                gender = _("female")
            else:
                gender = _("unknown")

            bh = person.get_birth_handle()
            dh = person.get_death_handle()
            if bh:
                bdate = self.db.get_event_from_handle(bh).get_date()
            else:
                bdate = ""
            if dh:
                ddate = self.db.get_event_from_handle(bh).get_date()
            else:
                ddate = ""
                
            rdata = [name,person.get_gramps_id(),gender,bdate,ddate]
            node = self.refmodel.add(rdata)

        self.refmodel.connect_model()

        if node:
            self.refmodel.selection.select_iter(node)
            path = self.refmodel.model.get_path(node)
            col = self.add_child.get_column(0)
            self.add_child.scroll_to_cell(path,col,1,0.5,0.0)

    def select_function(self,store,path,node,id_list):
        id_list.append(self.refmodel.get_value(node,PeopleModel.COLUMN_INT_ID))

    def get_selected_ids(self):
        mlist = []
        self.add_child.get_selection().selected_foreach(self.select_function,mlist)
        return mlist

    def on_save_child_clicked(self,obj):

        idlist = self.get_selected_ids()

        if not idlist or not idlist[0]:
            return

        handle = idlist[0]
        select_child = self.db.get_person_from_handle(handle)
        if self.person.get_handle() == handle:
            ErrorDialog(_("Error selecting a child"),
                        _("A person cannot be linked as his/her own child"),
                        self.top)
            return

        trans = self.db.transaction_begin()
        
        if self.family == None:
            self.family = RelLib.Family()
            self.db.add_family(self.family,trans)
            self.person.add_family_handle(self.family.get_handle())
            self.db.commit_person(self.person,trans)
            if self.person.get_gender() == const.MALE:
                self.family.set_father_handle(self.person.get_handle())
            else:	
                self.family.set_mother_handle(self.person.get_handle())
            self.db.commit_family(self.family,trans)
                
        if handle in (self.family.get_father_handle(),self.family.get_mother_handle()):
            ErrorDialog(_("Error selecting a child"),
                        _("A person cannot be linked as his/her own child"),
                        self.top)
            return

        self.family.add_child_handle(select_child.get_handle())
        
        mrel = self.mrel.get_active()
        mother = self.db.get_person_from_handle(self.family.get_mother_handle())
        if mother and mother.get_gender() != const.FEMALE:
            if mrel == const.CHILD_BIRTH:
                mrel = const.CHILD_UNKNOWN
                
        frel = self.frel.get_active()
        father = self.db.get_person_from_handle(self.family.get_father_handle())
        if father and father.get_gender() != const.MALE:
            if frel == const.CHILD_BIRTH:
                frel = const.CHILD_UNKNOWN

        select_child.add_parent_family_handle(self.family.get_handle(),
                                              mrel,frel)

        self.db.commit_person(select_child,trans)
        self.db.commit_family(self.family,trans)
        n = select_child.get_primary_name().get_regular_name()
        self.db.transaction_commit(trans,_("Add Child to Family (%s)") % n)
        self.close(obj)
        self.callback()
        
    def on_show_toggled(self,obj):
        self.redraw_child_list(not obj.get_active())

    def north_american(self,val):
        if self.person.get_gender() == const.MALE:
            return self.person.get_primary_name().get_surname()
        elif self.family:
            f = self.family.get_father_handle()
            if f:
                pname = f.get_primary_name()
                return (pname.get_surname_prefix(),pname.get_surname())
        return ("","")

    def no_name(self,val):
        return ("","")

    def latin_american(self,val):
        if self.family:
            father = self.family.get_father_handle()
            mother = self.family.get_mother_handle()
            if not father or not mother:
                return ("","")
            fsn = father.get_primary_name().get_surname()
            msn = mother.get_primary_name().get_surname()
            if not father or not mother:
                return ("","")
            try:
                return ("","%s %s" % (fsn.split()[0],msn.split()[0]))
            except:
                return ("","")
        else:
            return ("","")

    def icelandic(self,val):
        fname = ""
        if self.person.get_gender() == const.MALE:
            fname = self.person.get_primary_name().get_first_name()
        elif self.family:
            f = self.family.get_father_handle()
            if f:
                fname = f.get_primary_name().get_first_name()
        if fname:
            fname = fname.split()[0]
        if val == 0:
            return ("","%ssson" % fname)
        elif val == 1:
            return ("","%sdóttir" % fname)
        else:
            return ("","")
