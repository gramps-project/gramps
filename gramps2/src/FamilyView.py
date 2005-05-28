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

# $Id$

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
from gtk.gdk import ACTION_COPY, BUTTON1_MASK

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsKeys
import AddSpouse
import SelectChild
import DisplayTrace
import Marriage
import ChooseParents
import RelLib
import EditPerson
import DateHandler
import DisplayModels
import NameDisplay

from QuestionDialog import QuestionDialog,WarningDialog

from DdTargets import DdTargets

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_BORN = _('b.')
_DIED = _('d.')


column_names = [
    (_('#'),0) ,
    (_('ID'),1) ,
    (_('Name'),9),
    (_('Gender'),3),
    (_('Birth Date'),10),
    (_('Death Date'),11),
    (_('Birth Place'),6),
    (_('Death Place'),7),
    ]

_HANDLE_COL = 8

#-------------------------------------------------------------------------
#
# FamilyView
#
#-------------------------------------------------------------------------
class FamilyView:

    def __init__(self,parent):
        self.parent = parent
        self.parent.connect('database-changed',self.change_db)
        self.top = parent.gtop
        self.family = None
        self.cadded = [ 0, 0 ]
        self.in_drag = False
        self.init_interface()
        self.parent.connect('active-changed',self.update_callback)
                            
    def change_db(self,db):
        db.connect('family-add', self.update_callback)
        db.connect('family-update', self.update_callback)
        db.connect('family-delete', self.update_callback)
        db.connect('family-rebuild', self.load_family)

        db.connect('person-add', self.update_callback)
        db.connect('person-update', self.update_callback)
        db.connect('person-delete', self.update_callback)
        db.connect('person-rebuild', self.load_family)

    def update_callback(self,handle):
        self.load_family(self.family)

    def set_widgets(self,val):
        already_init = self.cadded[val]

        self.columns = []
        if (val):
            self.ap_data = self.top.get_widget('ap_data2')
            self.swap_btn = self.top.get_widget('swap_btn2')
            self.ap_parents = self.top.get_widget('ap_parents2')
            self.add_spouse_btn = self.top.get_widget('add_spouse2')
            self.sp_parents = self.top.get_widget('sp_parents2')
            self.spouse_list = self.top.get_widget('sp_list2')
            self.select_spouse_btn = self.top.get_widget('select_spouse2')
            self.remove_spouse_btn = self.top.get_widget('remove_spouse2')
            self.child_list = self.top.get_widget('chlist2')
            self.ap_swap_arrow = "Right"
            self.sp_swap_arrow = "Left"
            self.ap_par_arrow = "Down"
            self.sp_par_arrow = "Down"
            self.child_arrow = "Up"
            if not already_init:
                self.top.get_widget('add_parents2').connect('clicked',
                                                            self.add_parents_clicked)
                self.top.get_widget('del_parents2').connect('clicked',
                                                            self.del_parents_clicked)
                self.top.get_widget('add_spparents2').connect('clicked',
                                                              self.add_sp_parents)
                self.top.get_widget('del_spparents2').connect('clicked',
                                                              self.del_sp_parents)
                self.top.get_widget('fam_back2').connect('clicked',
                                                         self.child_back)
                self.top.get_widget('del_child_btn2').connect('clicked',
                                                              self.remove_child_clicked)
                self.top.get_widget('add_child_btn2').connect('clicked',
                                                              self.add_child_clicked)
                self.top.get_widget('select_child2').connect('clicked',
                                                             self.select_child_clicked)
                self.top.get_widget('ap_parents_btn2').connect('clicked',
                                                               self.ap_parents_clicked)
                self.top.get_widget('sp_parents_btn2').connect('clicked',
                                                               self.sp_parents_clicked)

            self.parent.views.get_nth_page(2).show_all()
            if self.parent.views.get_current_page() == 1:
                self.parent.views.set_current_page(2)
            self.parent.views.get_nth_page(1).hide()
        else:
            self.ap_data = self.top.get_widget('ap_data')
            self.swap_btn = self.top.get_widget('swap_spouse_btn')
            self.ap_parents = self.top.get_widget('ap_parents')
            self.add_spouse_btn = self.top.get_widget('add_spouse')
            self.sp_parents = self.top.get_widget('sp_parents')
            self.spouse_list = self.top.get_widget('sp_list')
            self.select_spouse_btn = self.top.get_widget('select_spouse')
            self.remove_spouse_btn = self.top.get_widget('remove_spouse')
            self.child_list = self.top.get_widget('chlist')
            self.ap_swap_arrow = "Down"
            self.sp_swap_arrow = "Up"
            self.ap_par_arrow = "Right"
            self.sp_par_arrow = "Right"
            self.child_arrow = "Left"
            if not already_init:
                self.top.get_widget('add_parents').connect('clicked',
                                                           self.add_parents_clicked)
                self.top.get_widget('del_parents').connect('clicked',
                                                           self.del_parents_clicked)
                self.top.get_widget('add_spparents').connect('clicked',
                                                             self.add_sp_parents)
                self.top.get_widget('del_spparents').connect('clicked',
                                                             self.del_sp_parents)
                self.top.get_widget('fam_back').connect('clicked',
                                                        self.child_back)
                self.top.get_widget('del_child_btn').connect('clicked',
                                                             self.remove_child_clicked)
                self.top.get_widget('add_child_btn').connect('clicked',
                                                             self.add_child_clicked)
                self.top.get_widget('select_child').connect('clicked',
                                                            self.select_child_clicked)
                self.top.get_widget('ap_parents_btn').connect('clicked',
                                                              self.ap_parents_clicked)
                self.top.get_widget('sp_parents_btn').connect('clicked',
                                                              self.sp_parents_clicked)

            self.parent.views.get_nth_page(1).show_all()
            if self.parent.views.get_current_page() == 2:
                self.parent.views.set_current_page(1)
            self.parent.views.get_nth_page(2).hide()

        self.spouse_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                       [DdTargets.SPOUSE.target()],
                                       ACTION_COPY)
        self.spouse_list.drag_source_set(BUTTON1_MASK,
                                         [DdTargets.SPOUSE.target()],
                                         ACTION_COPY)
        self.spouse_list.connect('drag_data_get',
                                 self.sp_drag_data_get)
        self.spouse_list.connect('drag_data_received',
                                 self.sp_drag_data_received)

    def init_interface(self):
        fv = GrampsKeys.get_family_view()
        self.set_widgets(fv)

        already_init = self.cadded[fv]
        
        self.ap_model = gtk.ListStore(str)
        self.ap_data.set_model(self.ap_model)
        if not already_init:
            column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
            self.ap_data.append_column(column)
            self.ap_data.connect('button-press-event',self.ap_button_press)
            self.ap_data.connect('key-press-event',self.ap_key_press)

        self.ap_parents_model = gtk.ListStore(str)
        self.ap_parents.set_model(self.ap_parents_model)
        self.ap_selection = self.ap_parents.get_selection()
        if not already_init:
            column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
            self.ap_parents.append_column(column)
            self.ap_parents.connect('button-press-event',self.ap_par_button_press)
            self.ap_parents.connect('key-press-event',self.ap_par_key_press)

        self.sp_parents_model = gtk.ListStore(str)
        self.sp_parents.set_model(self.sp_parents_model)
        self.sp_selection = self.sp_parents.get_selection()
        if not already_init:
            column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
            self.sp_parents.append_column(column)
            self.sp_parents.connect('button-press-event',self.sp_par_button_press)
            self.sp_parents.connect('key-press-event',self.sp_par_key_press)

        self.spouse_model = gtk.ListStore(str,str)
        self.spouse_list.set_model(self.spouse_model)
        self.spouse_selection = self.spouse_list.get_selection()
        if not already_init:
            self.spouse_selection.connect('changed',self.spouse_changed)
            self.spouse_list.connect('button-press-event',self.sp_button_press)
            self.spouse_list.connect('key-press-event',self.sp_key_press)
        
        if not already_init:
            column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
            self.spouse_list.append_column(column)
        self.selected_spouse = None

        self.child_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                      [DdTargets.CHILD.target(),
                                       DdTargets.PERSON_LINK.target()],
                                      ACTION_COPY)
        self.child_list.drag_source_set(BUTTON1_MASK,
                                        [DdTargets.CHILD.target()],
                                        ACTION_COPY)
        self.child_list.connect('drag_data_get', self.drag_data_get)
        self.child_list.connect('drag_data_received',self.drag_data_received)

        if not already_init:
            self.child_list.connect('button-press-event',
                                    self.on_child_list_button_press)
            self.child_list.connect('key-press-event',self.child_key_press)

            self.swap_btn.connect('clicked',self.spouse_swap)
            self.remove_spouse_btn.connect('clicked',self.remove_spouse)
            self.add_spouse_btn.connect('clicked',self.add_spouse)
            self.select_spouse_btn.connect('clicked',self.select_spouse)

        if not already_init:
            self.build_columns()

        self.child_model = DisplayModels.ChildModel([],self.parent.db)
        self.child_list.set_model(self.child_model)
        #self.child_list.set_search_column(2)
        self.child_selection = self.child_list.get_selection()

        self.cadded[fv] = 1

    def build_columns(self):
        for column in self.columns:
            self.child_list.remove_column(column)
        self.columns = []

        for pair in self.parent.db.get_child_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]][0]
            column = gtk.TreeViewColumn(name, gtk.CellRendererText(),
                                        text=pair[1])
            column.set_resizable(True)
            column.set_min_width(40)
            column.set_sort_column_id(column_names[pair[1]][1])
            self.columns.append(column)
            self.child_list.append_column(column)
        
    def ap_button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.parent.load_person(self.person)
        elif (event.type == gtk.gdk.BUTTON_PRESS and event.button == 3
              and self.person):
            self.build_ap_menu(event)

    def ap_key_press(self,obj,event):
        if event.keyval == gtk.gdk.keyval_from_name("Return") \
                                    and not event.state:
            self.parent.load_person(self.person)
        elif event.keyval == gtk.gdk.keyval_from_name(self.ap_swap_arrow) \
                                    and event.state == gtk.gdk.CONTROL_MASK:
            self.spouse_swap(obj)
                
    def sp_key_press(self,obj,event):
        if event.keyval == gtk.gdk.keyval_from_name("Return") and not event.state:
            if self.selected_spouse:
                self.edit_marriage_callback(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Return") \
                                    and event.state == gtk.gdk.SHIFT_MASK:
            self.edit_spouse_callback(obj)
        elif event.keyval == gtk.gdk.keyval_from_name(self.sp_swap_arrow) \
                                    and event.state == gtk.gdk.CONTROL_MASK:
            self.spouse_swap(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Delete") and not event.state:
            self.remove_spouse(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") and not event.state:
            self.select_spouse(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") \
                                    and event.state == gtk.gdk.SHIFT_MASK:
            self.add_spouse(obj)

    def ap_par_key_press(self,obj,event):
        if self.person == None:
            return
        if event.keyval == gtk.gdk.keyval_from_name("Return") and not event.state:
            self.edit_ap_relationships(obj)
        elif event.keyval == gtk.gdk.keyval_from_name(self.ap_par_arrow) \
                                    and event.state == gtk.gdk.CONTROL_MASK:
            self.ap_parents_clicked(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Delete") and not event.state:
            self.del_parents_clicked(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") and not event.state:
            self.add_parents_clicked(obj)

    def sp_par_key_press(self,obj,event):
        if self.person == None:
            return
        if event.keyval == gtk.gdk.keyval_from_name("Return") and not event.state:
            self.edit_sp_relationships(obj)
        elif event.keyval == gtk.gdk.keyval_from_name(self.sp_par_arrow) \
                                    and event.state == gtk.gdk.CONTROL_MASK:
            self.sp_parents_clicked(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Delete") and not event.state:
            self.del_sp_parents(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") and not event.state:
            self.add_sp_parents(obj)

    def child_key_press(self,obj,event):
        model, node = self.child_selection.get_selected()
        if not node:
            return
        handle = self.child_model.get_value(node,_HANDLE_COL)
        if event.keyval == gtk.gdk.keyval_from_name("Return") and not event.state:
            self.child_rel_by_id(handle)
        elif event.keyval == gtk.gdk.keyval_from_name("Return") \
                                    and event.state == gtk.gdk.SHIFT_MASK:
            self.edit_child_callback(obj)
        elif event.keyval == gtk.gdk.keyval_from_name(self.child_arrow) \
                                    and event.state == gtk.gdk.CONTROL_MASK:
            self.child_back(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Delete") and not event.state:
            self.remove_child_clicked(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") and not event.state:
            self.select_child_clicked(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") \
                                    and event.state == gtk.gdk.SHIFT_MASK:
            self.add_child_clicked(obj)

    def build_ap_menu(self,event):
        """Builds the menu with navigation for the active person box"""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity,False),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity,False),
            #FIXME: revert to stock item when German gtk translation is fixed
            #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1,False),
            (_("Add Bookmark"),self.parent.on_add_bookmark_activate,1,True),
        ]
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))
        for stock_id,callback,sensitivity,ro in entries:
            if ro and self.parent.db.readonly:
                continue
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
            if stock_id == _("Home"):
                im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
                im.show()
                item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def build_nav_menu(self,event):
        """Builds the menu with navigation (no bookmark)"""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
            #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
        ]
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
            if stock_id == _("Home"):
                im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
                im.show()
                item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def build_parents_nosel_menu(self,event):
        """Builds the menu with navigation and Add parents"""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity,False),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity,False),
            (gtk.STOCK_HOME,self.parent.on_home_clicked,1,False),
            (None,None,0,True),
            (_("Add parents"),self.add_parents_clicked,1,True),
        ]

        menu = gtk.Menu()
        menu.set_title(_('People Menu'))
        
        for (stock_id,callback,sensitivity,ro) in entries:
            if self.parent.db.readonly and ro:
                continue
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
            if stock_id == _("Home"):
                im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
                im.show()
                item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def build_sp_parents_nosel_menu(self,event):
        """Builds the menu with navigation and Add parents"""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity,False),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity,False),
            (gtk.STOCK_HOME,self.parent.on_home_clicked,1,False),
            (None,None,0,True),
            (_("Add parents"),self.add_sp_parents,1,True),
        ]
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))
        for stock_id,callback,sensitivity,ro in entries:
            if ro and self.parent.db.readonly:
                continue
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def on_child_list_button_press(self,obj,event):
        model, node = self.child_selection.get_selected()
        if not node:
            if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
                self.build_nav_menu(event)
            return
        handle = self.child_model.get_value(node,_HANDLE_COL)
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.child_rel_by_id(handle)
        elif event.state == gtk.gdk.SHIFT_MASK and \
                    event.type == gtk.gdk.BUTTON_PRESS and \
                    event.button == 1:
            self.edit_child_callback(obj)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_child_menu(handle,event)

    def build_child_menu(self,handle,event):
        """Builds the menu that allows editing operations on the child list"""

        menu = gtk.Menu()
        menu.set_title(_('Child Menu'))

        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        nav_entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
            #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
        ]
        for stock_id,callback,sensitivity in nav_entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
            if stock_id == _("Home"):
                im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
                im.show()
                item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)

        entries = [
            (_("Make the selected child an active person"), self.child_back),
            (_("Edit the child/parent relationships"), self.child_rel),
            (_("Edit the selected child"),self.edit_child_callback),
            (_("Remove the selected child"),self.remove_child_clicked),
            ]
        if not self.parent.db.readonly:
            for msg,callback in entries:
                Utils.add_menuitem(menu,msg,handle,callback)
        menu.popup(None,None,None,event.button,event.time)

    def edit_child_callback(self,obj):
        model, node = self.child_selection.get_selected()
        if not node:
            return
        handle = self.child_model.get_value(node,_HANDLE_COL)
        child = self.parent.db.get_person_from_handle(handle)
        try:
            EditPerson.EditPerson(self.parent, child, self.parent.db,
                                  self.spouse_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def child_rel(self,obj):
        handle = obj.get_data('o')
        person = self.parent.db.get_person_from_handle(handle)
        ChooseParents.ModifyParents(self.parent.db, person,
                                    self.family.get_handle())
        
    def child_rel_by_id(self,handle):
        person = self.parent.db.get_person_from_handle(handle)
        ChooseParents.ModifyParents(self.parent.db, person,
                                    self.family.get_handle())

    def spouse_changed(self,obj):
        if self.in_drag:
            return
        model, node = obj.get_selected()
        if not node:
            self.display_marriage(None)
            self.family = None
        else:
            row = model.get_path(node)
            family_handle = self.person.get_family_handle_list()[row[0]]
            fam = self.parent.db.get_family_from_handle(family_handle)
            self.display_marriage(fam)
            self.family = fam

    def build_spouse_menu(self,event):

        menu = gtk.Menu()
        menu.set_title(_('Spouse Menu'))

        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        nav_entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
            #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
        ]
        for stock_id,callback,sensitivity in nav_entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
            if stock_id == _("Home"):
                im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
                im.show()
                item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)

        entries = [
            (_("Make the selected spouse an active person"), self.spouse_swap),
            (_("Edit relationship"), self.edit_marriage_callback),
            (_("Remove the selected spouse"), self.remove_spouse),
            (_("Edit the selected spouse"), self.edit_spouse_callback),
            (_("Set the selected spouse as the preferred spouse"), self.set_preferred_spouse),
            ]
        if not self.parent.db.readonly:
            for msg,callback in entries:
                Utils.add_menuitem(menu,msg,None,callback)
        menu.popup(None,None,None,event.button,event.time)

    def set_preferred_spouse(self,obj):
        if self.selected_spouse:
            self.person.set_preferred_family_handle(self.family)
            trans = self.parent.db.transaction_begin()
            self.parent.db.commit_person(self.person,trans)
            n = NameDisplay.displayer.display(self.person)
            self.parent.db.transaction_commit(trans,_("Set Preferred Spouse (%s)") % n)
            self.load_family()
            
    def edit_spouse_callback(self,obj):
        if self.selected_spouse:
            try:
                EditPerson.EditPerson(self.parent, self.selected_spouse,
                                      self.parent.db, self.spouse_after_edit)
            except:
                DisplayTrace.DisplayTrace()

    def edit_marriage_callback(self,obj):
        Marriage.Marriage(self.parent, self.family,self.parent.db)

    def sp_button_press(self,obj,event):
        if event.state & gtk.gdk.SHIFT_MASK and \
                    event.type == gtk.gdk.BUTTON_PRESS and \
                    event.button == 1 and self.selected_spouse:
            self.edit_spouse_callback(None)
            
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            if self.selected_spouse:
                self.build_spouse_menu(event)
            else:
                self.build_nav_menu(event)
        elif event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
           if self.person:
               try:
                   if self.selected_spouse:
                       Marriage.Marriage(self.parent,self.family,self.parent.db)
                   else:
                       AddSpouse.AddSpouse(self.parent,self.parent.db,self.person,
                                           self.family)
               except:
                   DisplayTrace.DisplayTrace()
        
    def select_spouse(self,obj):
        if not self.person:
            return
        try:
            AddSpouse.AddSpouse(self.parent, self.parent.db, self.person)
        except:
            DisplayTrace.DisplayTrace()

    def add_spouse(self,obj):
        if not self.person:
            return
        person = RelLib.Person()
        if self.person.get_gender() == RelLib.Person.MALE:
            person.set_gender(RelLib.Person.FEMALE)
        else:
            person.set_gender(RelLib.Person.MALE)
        try:
            EditPerson.EditPerson(self.parent, person, self.parent.db,
                                  self.new_spouse_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def spouse_after_edit(self,epo,val):
        ap = self.parent.active_person
        self.parent.active_person = ap
        
    def new_spouse_after_edit(self,epo,val):

        new_person = epo.person
        old_person = self.person
        trans = self.parent.db.transaction_begin()
        fhandle = self.parent.db.create_id()
        family = RelLib.Family()
        family.set_handle(fhandle)
        family.set_gramps_id(self.parent.db.find_next_family_gramps_id())

        old_person.add_family_handle(fhandle)
        new_person.add_family_handle(fhandle)

        if self.person.get_gender() == RelLib.Person.MALE:
            family.set_mother_handle(epo.person.get_handle())
            family.set_father_handle(self.person.get_handle())
        else:
            family.set_father_handle(epo.person.get_handle())
            family.set_mother_handle(self.person.get_handle())

        self.parent.db.commit_family(family,trans)
        self.parent.db.commit_person(new_person,trans)
        self.parent.db.commit_person(old_person,trans)
        self.parent.db.transaction_commit(trans,_("Add Spouse"))

        self.family = family
        self.person = old_person
        m = Marriage.Marriage(self.parent,self.family,self.parent.db)

        m.on_add_clicked()

    def add_child_clicked(self,obj):
        if not self.person:
            return

        person = RelLib.Person()
        autoname = GrampsKeys.get_lastnamegen()
        
        if autoname == 0:
            name = self.north_american(0)
        elif autoname == 2:
            name = self.latin_american(0)
        elif autoname == 3:
            name = self.icelandic(0)
        else:
            name = self.no_name(0)
        person.get_primary_name().set_surname(name[1])
        person.get_primary_name().set_surname_prefix(name[0])

        try:
            EditPerson.EditPerson(self.parent, person, self.parent.db,
                                  self.new_child_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def update_person_list(self,person):
        trans = self.parent.db.transaction_begin()

        if not self.family:
            self.family = RelLib.Family()
            self.parent.db.add_family(self.family,trans)
            person.add_family_handle(self.family.get_handle())
            if person.get_gender() == RelLib.Person.MALE:
                self.family.set_father_handle(person)
            else:
                self.family.set_mother_handle(person)

        self.family.add_child_handle(person)
        person.add_parent_family_handle(self.family.get_handle(),"Birth","Birth")
        self.parent.db.commit_person(person,trans)
        self.parent.db.commit_family(self.family,trans)
        self.parent.db.transaction_commit(trans,_("Modify family"))
            
    def new_child_after_edit(self,epo,value):
        family = self.family
        person = self.person
        new_person = epo.person
        trans = self.parent.db.transaction_begin()
        if not family:
            # Add family to active person, 
            # if it does not exist yet (child with no spouse)
            family = RelLib.Family()
            self.parent.db.add_family(family,trans)
            person.add_family_handle(family.get_handle())
            if person.get_gender() == RelLib.Person.MALE:
                family.set_father_handle(person.get_handle())
            else:
                family.set_mother_handle(person.get_handle())
            self.parent.db.commit_family(family,trans)
            self.parent.db.commit_person(person,trans)

        # TODO: Add child ordered by birth day
        family.add_child_handle(new_person.get_handle())
        new_person.add_parent_family_handle(family.get_handle(),
                                            RelLib.Person.CHILD_REL_BIRTH,
                                            RelLib.Person.CHILD_REL_BIRTH)
        self.parent.db.commit_person(new_person,trans)
        self.parent.db.commit_family(family,trans)
        self.parent.db.transaction_commit(trans,_("Add Child to Family"))
        self.load_family(family)

    def select_child_clicked(self,obj):
        if not self.person:
            return
        try:
            SelectChild.SelectChild(self.parent, self.parent.db, self.family,
                                    self.person, self.load_family)
        except:
            DisplayTrace.DisplayTrace()

    def remove_child_clicked(self,obj):
        if self.family == None or self.person == None:
            return

        family = self.family
        
        model, node = self.child_selection.get_selected()
        if not node:
            return

        handle = self.child_model.get_value(node,_HANDLE_COL)
        child = self.parent.db.get_person_from_handle(handle)

        trans = self.parent.db.transaction_begin()
        
        family.remove_child_handle(child.get_handle())
        child.remove_parent_family_handle(family.get_handle())
        
        if len(family.get_child_handle_list()) == 0:
            if family.get_father_handle() == None:
                self.delete_family_from(family.get_mother_handle(),trans)
            elif family.get_mother_handle() == None:
                self.delete_family_from(family.get_father_handle(),trans)

        self.parent.db.commit_person(child,trans)
        self.parent.db.commit_family(family,trans)
        n = child.get_primary_name().get_regular_name()
        self.parent.db.transaction_commit(trans,_("Remove Child (%s)") % n)

    def remove_spouse(self,obj):
        if self.selected_spouse:
            nap = NameDisplay.displayer.display(self.person)
            nsp = NameDisplay.displayer.display(self.selected_spouse)
            QuestionDialog(_('Remove %s as a spouse of %s?') % (nsp,nap),
                           _('Removing a spouse removes the relationship between '
                             'the spouse and the active person. It does not '
                             'remove the spouse from the database'),
                           _('_Remove Spouse'),
                           self.really_remove_spouse)
        elif self.family and not self.family.get_child_handle_list():
            self.really_remove_spouse()
                       
    def really_remove_spouse(self):
        """Delete the currently selected spouse from the family"""
        if self.person == None:
            return

        cur_person = self.person
        cur_spouse = self.selected_spouse
        cur_family = self.family

        if cur_spouse.get_handle() == cur_family.get_father_handle():
            cur_family.set_father_handle(None)
        else:
            cur_family.set_mother_handle(None)

        trans = self.parent.db.transaction_begin()
        
        if cur_spouse:
            cur_spouse.remove_family_handle(cur_family.get_handle())
            self.parent.db.commit_person(cur_spouse,trans)

        self.parent.db.commit_family(cur_family,trans)

        if len(cur_family.get_child_handle_list()) == 0:
            mother_id = cur_family.get_mother_handle()
            father_id = cur_family.get_father_handle()

            for handle in [father_id, mother_id]:
                if handle:
                    p = self.parent.db.get_person_from_handle(handle)
                    p.remove_family_handle(cur_family.get_handle())
                    self.parent.db.commit_person(p,trans)

#             if len(cur_person.get_family_handle_list()) > 0:
#                 handle = cur_person.get_family_handle_list()[0]
#                 family = self.parent.db.find_family_from_handle(handle,trans)

        person_id = cur_person.get_handle()
        self.person = self.parent.db.get_person_from_handle(person_id)
        n = self.person.get_primary_name().get_regular_name()
        self.parent.db.transaction_commit(trans,_("Remove Spouse (%s)") % n)

        if len(self.person.get_family_handle_list()) <= 1:
            self.spouse_selection.set_mode(gtk.SELECTION_NONE)

    def spouse_swap(self,obj):
        if self.selected_spouse:
            self.parent.change_active_person(self.selected_spouse)
            self.load_family(self.family)

    def ap_parents_clicked(self,obj):
        self.change_families(self.person, self.ap_selection)
            
    def sp_parents_clicked(self,obj):
        self.change_families(self.selected_spouse, self.sp_selection)

    def change_families(self,person,select):
        if not person:
            return
        plist = person.get_parent_family_handle_list()

        if len(plist) == 0:
            return
        if len(plist) == 1:
            family_handle,m,r = plist[0]
        else:
            model, node = select.get_selected()
            path = model.get_path(node)
            family_handle,m,r = plist[path[0]]
        family = self.parent.db.get_family_from_handle(family_handle)

        if family.get_father_handle():
            person_handle = family.get_father_handle()
        else:
            person_handle = family.get_mother_handle()
        person = self.parent.db.get_person_from_handle(person_handle)
        self.parent.change_active_person(person)

        n = NameDisplay.displayer.display(person)
        trans = self.parent.db.transaction_begin()
        self.parent.db.commit_family(family,trans)
        self.parent.db.transaction_commit(trans,_("Select Parents (%s)") % n)
        self.load_family(family)

    def clear(self):
        self.spouse_model.clear()
        self.sp_parents_model.clear()
        self.ap_parents_model.clear()
        self.ap_model.clear()
        self.child_model = DisplayModels.ChildModel([],self.parent.db)
        self.child_list.set_model(self.child_model)

    def set_buttons(self):
        mode = not self.parent.db.readonly
        
        self.top.get_widget('add_child_btn').set_sensitive(mode)
        self.top.get_widget('add_child_btn2').set_sensitive(mode)
        self.top.get_widget('add_parents').set_sensitive(mode)
        self.top.get_widget('add_parents2').set_sensitive(mode)
        self.top.get_widget('add_spparents').set_sensitive(mode)
        self.top.get_widget('add_spparents2').set_sensitive(mode)
        self.top.get_widget('del_child_btn').set_sensitive(mode)
        self.top.get_widget('del_child_btn2').set_sensitive(mode)
        self.top.get_widget('del_parents').set_sensitive(mode)
        self.top.get_widget('del_parents2').set_sensitive(mode)
        self.top.get_widget('del_spparents').set_sensitive(mode)
        self.top.get_widget('del_spparents2').set_sensitive(mode)
        self.top.get_widget('select_child2').set_sensitive(mode)
        self.top.get_widget('select_child').set_sensitive(mode)
        self.add_spouse_btn.set_sensitive(mode)
        self.remove_spouse_btn.set_sensitive(mode)
        self.select_spouse_btn.set_sensitive(mode)
        
    def load_family(self,family=None):
        self.set_buttons()
        if self.parent.active_person:
            handle = self.parent.active_person.get_handle()
            self.person = self.parent.db.get_person_from_handle(handle)
            if not self.person:
                self.clear()
                return
            splist = self.person.get_family_handle_list()
        else:
            self.person = None
            self.clear()
            return

        person = self.person
        bhandle = person.get_birth_handle()
        dhandle = person.get_death_handle()
        bd = self.parent.db.get_event_from_handle(bhandle)
        dd = self.parent.db.get_event_from_handle(dhandle)

        if bd and dd:
            n = "%s [%s]\n\t%s %s\n\t%s %s " % (
                NameDisplay.displayer.display(person),
                person.get_gramps_id(),
                _BORN,DateHandler.displayer.display(bd.get_date_object()),
                _DIED,DateHandler.displayer.display(dd.get_date_object()))
        elif bd:
            n = "%s [%s]\n\t%s %s" % (
                NameDisplay.displayer.display(person),
                person.get_gramps_id(),
                _BORN,DateHandler.displayer.display(bd.get_date_object()))
        elif dd:
            n = "%s [%s]\n\t%s %s" % (
                NameDisplay.displayer.display(person),
                person.get_gramps_id(),
                _DIED,DateHandler.displayer.display(dd.get_date_object()))
        else:
            n = "%s [%s]" % (NameDisplay.displayer.display(person),
                             person.get_gramps_id())

        self.ap_model.clear()
        self.ap_data.get_selection().set_mode(gtk.SELECTION_NONE)
        node = self.ap_model.append()
        self.ap_model.set(node,0,n)

        self.selected_spouse = None
        self.spouse_model.clear()
        self.sp_parents_model.clear()

        if len(splist) > 1:
            self.spouse_selection.set_mode(gtk.SELECTION_SINGLE)
        else:
            self.spouse_selection.set_mode(gtk.SELECTION_NONE)

        flist = {}

        for f in splist:
            fm = self.parent.db.get_family_from_handle(f)
            if not fm:
                continue
            if fm.get_father_handle() == person.get_handle():
                sp_id = fm.get_mother_handle()
            else:
                sp_id = fm.get_father_handle()

            node = self.spouse_model.append()
            flist[f] = node
                
            if sp_id:
                sp = self.parent.db.get_person_from_handle(sp_id)
                event = self.find_marriage(fm)
                if event:
                    dobj = event.get_date_object()
                    mdate = " - %s" % DateHandler.displayer.display(dobj)
                else:
                    mdate = ""
                v = "%s [%s]\n\t%s%s" % (
                    NameDisplay.displayer.display(sp),
                    sp.get_gramps_id(),
                    const.family_relations[fm.get_relationship()][0], mdate)
                self.spouse_model.set(node,0,v)
                self.spouse_model.set(node,1,f)
            else:
                self.spouse_model.set(node,0,"%s\n" % _("<double click to add spouse>"))
                self.spouse_model.set(node,1,f)

        try:
            if family and family.get_handle() in flist:
                self.display_marriage(family)
                node = flist[family.get_handle()]
                self.spouse_selection.select_iter(node)
            elif len(flist) > 0:
                fid = splist[0]
                fam = self.parent.db.get_family_from_handle(fid)
                self.display_marriage(fam)
                node = flist[fid]
                self.spouse_selection.select_iter(node)
            else:
                self.display_marriage(None)
        except KeyError:
            WarningDialog(_('Database corruption detected'),
                          _('A problem was detected with the database. Please '
                            'run the Check and Repair Database tool to fix the '
                            'problem.'))

        self.update_list(self.ap_parents_model,self.ap_parents,person)

    def find_marriage(self,family):
        for event_handle in family.get_event_list():
            if event_handle:
                event = self.parent.db.get_event_from_handle(event_handle)
                if event.get_name() == "Marriage":
                    return event
        return None

    def update_list(self,model,tree,person):
        model.clear()
        sel = None
        selection = tree.get_selection()
        family_list = person.get_parent_family_handle_list()

        count = 0
        for (f,mrel,frel) in family_list:
            fam = self.parent.db.get_family_from_handle(f)
            if not fam:
                continue
            count += 1
            father_handle = fam.get_father_handle()
            mother_handle = fam.get_mother_handle()
            f = self.parent.db.get_person_from_handle(father_handle)
            m = self.parent.db.get_person_from_handle(mother_handle)

            father = self.nameof(_("Father"),f,
                                 const.child_rel_list[frel])
            mother = self.nameof(_("Mother"),m,
                                 const.child_rel_list[mrel])

            node = model.append()
            if not sel:
                sel = node
            v = "%s\n%s" % (father,mother)
            model.set(node,0,v)
        if count > 1:
            selection.set_mode(gtk.SELECTION_SINGLE)
            selection.select_iter(sel)
        else:
            selection.set_mode(gtk.SELECTION_NONE)
            
    def nameof(self,l,p,mode):
        if p:
            n = NameDisplay.displayer.display(p)
            pid = p.get_gramps_id()
            return _("%s: %s [%s]\n\tRelationship: %s") % (l,n,pid,_(mode))
        else:
            return _("%s: unknown") % (l)

    def delete_family_from(self,person_handle,trans):
        person = self.parent.db.get_person_from_handle(person_handle)
        person.remove_family_handle(self.family.get_handle())
        self.parent.db.remove_family(self.family.get_handle(),trans)
        flist = self.person.get_family_handle_list()
        if len(flist) > 0:
            self.family = self.parent.db.get_family_from_handle(flist[0])
        else:
            self.family = None

    def display_marriage(self,family):
        if not family:
            self.family = None
            self.child_model = DisplayModels.ChildModel([],self.parent.db)
            self.child_list.set_model(self.child_model)
            return

        hlist = family.get_child_handle_list()
        self.child_model = DisplayModels.ChildModel(hlist,self.parent.db)
        self.child_list.set_model(self.child_model)
        self.family = self.parent.db.get_family_from_handle(family.get_handle())

        if self.family.get_father_handle() == self.person.get_handle():
            sp_id = self.family.get_mother_handle()
            if sp_id:
                self.selected_spouse = self.parent.db.get_person_from_handle(sp_id)
            else:
                self.selected_spouse = None
        else:
            sp_id = self.family.get_father_handle()
            if sp_id:
                self.selected_spouse = self.parent.db.get_person_from_handle(sp_id)
            else:
                self.selected_spouse = None

        if self.selected_spouse:
            self.update_list(self.sp_parents_model,self.sp_parents,
                             self.selected_spouse)

    def build_parents_menu(self,family,event):
        """Builds the menu that allows editing operations on the child list"""
        menu = gtk.Menu()
        menu.set_title(_('Parents Menu'))

        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        nav_entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
            #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
        ]
        for stock_id,callback,sensitivity in nav_entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
            if stock_id == _("Home"):
                im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
                im.show()
                item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)

        entries = [
            (_("Make the selected parents the active family"), self.ap_parents_clicked),
            (_("Edit the child/parent relationships"), self.edit_ap_relationships),
            (_("Add parents"), self.add_parents_clicked),
            (_("Remove parents"),self.del_parents_clicked),
            ]
        if not self.parent.db.readonly:
            for msg,callback in entries:
                Utils.add_menuitem(menu,msg,family,callback)
        menu.popup(None,None,None,event.button,event.time)

    def build_sp_parents_menu(self,family,event):
        """Builds the menu that allows editing operations on the child list"""
        menu = gtk.Menu()
        menu.set_title(_('Spouse Parents Menu'))

        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        nav_entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
            #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
        ]
        for stock_id,callback,sensitivity in nav_entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
            if stock_id == _("Home"):
                im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
                im.show()
                item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)

        entries = [
            (_("Make the selected parents the active family"), self.sp_parents_clicked),
            (_("Edit the child/parent relationships"), self.edit_sp_relationships),
            (_("Add parents"), self.add_sp_parents),
            (_("Remove parents"),self.del_sp_parents),
            ]
        if not self.parent.db.readonly:
            for msg,callback in entries:
                Utils.add_menuitem(menu,msg,family,callback)
        menu.popup(None,None,None,event.button,event.time)

    def edit_ap_relationships(self,obj):
        self.parent_editor(self.person,self.ap_selection)

    def edit_sp_relationships(self,obj):
        self.parent_editor(self.selected_spouse,self.sp_selection)

    def ap_par_button_press(self,obj,event):
        if self.person == None:
            return
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.parent_editor(self.person,self.ap_selection)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            plist = self.person.get_parent_family_handle_list()

            if len(plist) == 0:
                self.build_parents_nosel_menu(event)
                return
            elif len(plist) == 1:
                family,m,r = plist[0]
            else:
                model, node = self.ap_selection.get_selected()
                path = model.get_path(node)
                family,m,r = plist[path[0]]
            self.build_parents_menu(family,event)

    def sp_par_button_press(self,obj,event):
        if self.selected_spouse == None:
            if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
                self.build_nav_menu(event)
            return
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.parent_editor(self.selected_spouse,self.sp_selection)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            plist = self.selected_spouse.get_parent_family_handle_list()
            if len(plist) == 0:
                self.build_sp_parents_nosel_menu(event)
                return
            elif len(plist) == 1:
                family,m,r = plist[0]
            else:
                model, node = self.sp_selection.get_selected()
                path = model.get_path(node)
                family,m,r = plist[path[0]]
            self.build_sp_parents_menu(family,event)

    def add_parents_clicked(self,obj):
        self.parent_add(self.person)

    def add_sp_parents(self,obj):
        if self.selected_spouse:
            self.parent_add(self.selected_spouse)

    def del_parents_clicked(self,obj):
        if not self.person or len(self.person.get_parent_family_handle_list()) == 0:
            return
        n = NameDisplay.displayer.display(self.person)
        QuestionDialog(_('Remove Parents of %s') % n,
                       _('Removing the parents of a person removes the person as a '
                         'child of the parents. The parents are not removed from the '
                         'database, and the relationship between the parents '
                         'is not removed.'),
                       _('_Remove Parents'),
                       self.really_del_parents)
        
    def really_del_parents(self):
        self.parent_deleter(self.person,self.ap_selection)

    def del_sp_parents(self,obj):
        if not self.selected_spouse or len(self.selected_spouse.get_parent_family_handle_list()) == 0:
            return
        n = NameDisplay.displayer.display(self.selected_spouse)
        QuestionDialog(_('Remove Parents of %s') % n,
                       _('Removing the parents of a person removes the person as a '
                         'child of the parents. The parents are not removed from the '
                         'database, and the relationship between the parents '
                         'is not removed.'),
                       _('_Remove Parents'),
                       self.really_del_sp_parents)

    def really_del_sp_parents(self):
        self.parent_deleter(self.selected_spouse,self.sp_selection)

    def child_back(self,obj):
        """makes the currently select child the active person"""
        model, node = self.child_selection.get_selected()
        if node:
            handle = self.child_model.get_value(node,_HANDLE_COL)
            child = self.parent.db.get_person_from_handle(handle)
            self.parent.change_active_person(child)
            self.load_family()
        elif self.family:
            child_list = self.family.get_child_handle_list()
            if len(child_list) == 1:
                p = self.parent.db.get_person_from_handle(child_list[0])
                self.parent.change_active_person(p)
                self.load_family()

    def parent_editor(self,person,selection):
        if not person:
            return

        plist = person.get_parent_family_handle_list()

        if len(plist) == 0:
            return
        elif len(plist) == 1:
            parents,mrel,frel = plist[0]
        else:
            model, node = selection.get_selected()
            if not node:
                return

            row = model.get_path(node)
            parents,mrel,frel = plist[row[0]]

        try:
            ChooseParents.ModifyParents(self.parent.db,person,parents,
                                        self.parent.topWindow)
        except:
            DisplayTrace.DisplayTrace()

    def parent_add(self,person):
        if not person:
            return
        try:
            ChooseParents.ChooseParents(self.parent,
                                        self.parent.db,
                                        person,
                                        None)
        except:
            DisplayTrace.DisplayTrace()
        
    def parent_deleter(self,person,selection):
        if not person:
            return

        trans = self.parent.db.transaction_begin()
        plist = person.get_parent_family_handle_list()

        if len(plist) == 0:
            return
        if len(plist) == 1:
            person.clear_parent_family_handle_list()
        else:
            model, node = selection.get_selected()
            if not node:
                return

            row = model.get_path(node)
            family_handle = person.get_parent_family_handle_list()[row[0]][0]
            person.remove_parent_family_handle(family_handle)
            fam = self.parent.db.get_family_from_handle(family_handle)

            if len(fam.get_child_handle_list()) == 0:
                father_handle = fam.get_father_handle()
                mother_handle = fam.get_mother_handle()
                if father_handle == None and mother_handle:
                    mother = self.parent.db.get_person_from_handle(mother_handle)
                    mother.remove_family_handle(fam)
                    self.parent.db.commit_person(mother,trans)
                    self.parent.db.remove_family(fam,trans)
                elif mother_handle == None and father_handle:
                    father = self.parent.db.get_person_from_handle(father_handle)
                    father.remove_family_handle(fam,trans)
                    self.parent.db.commit_person(father,trans)
                    self.parent.db.remove_family(fam,trans)

        self.parent.db.commit_person(person,trans)
        n = person.get_primary_name().get_regular_name()
        self.parent.db.transaction_commit(trans,_("Remove Parents (%s)") % n)
        
        self.load_family()

    def drag_data_received(self,widget,context,x,y,sel_data,info,time):

        if DdTargets.PERSON_LINK.drag_type in context.targets:
            drop_person_handle = sel_data.data
            
            # Check child is not already in the family
            if self.family and \
                   drop_person_handle in self.family.get_child_handle_list():
                return

            family = self.family
            person = self.person
            new_person = self.parent.db.get_person_from_handle(drop_person_handle)
            trans = self.parent.db.transaction_begin()
            if not family:
                # Add family to active person, 
                # if it does not exist yet (child with no spouse)
                family = RelLib.Family()
                self.parent.db.add_family(family,trans)
                person.add_family_handle(family.get_handle())
                if person.get_gender() == RelLib.Person.MALE:
                    family.set_father_handle(person.get_handle())
                else:
                    family.set_mother_handle(person.get_handle())
                self.parent.db.commit_family(family,trans)
                self.parent.db.commit_person(person,trans)

            family.add_child_handle(new_person.get_handle())
            new_person.add_parent_family_handle(family.get_handle(),
                                                RelLib.Person.CHILD_REL_BIRTH,
                                                RelLib.Person.CHILD_REL_BIRTH)
            self.parent.db.commit_person(new_person,trans)
            self.parent.db.commit_family(family,trans)
            self.parent.db.transaction_commit(trans,_("Add Child to Family"))
            self.display_marriage(family)
        
        elif sel_data and sel_data.data:

            path = self.child_list.get_path_at_pos(x,y)
            if path == None:
                row = len(self.family.get_child_handle_list())
            else:
                row = path[0][0] -1

            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]

            if mytype != 'child':
                return

            s,i = self.child_selection.get_selected()
            if not i:
                return

            spath = s.get_path(i)
            src = spath[0] 
            child_list = self.family.get_child_handle_list()

            # Check if the children were in order before the attempt to reorder
            was_ordered = self.birth_dates_in_order(child_list)

            obj = child_list[src]
            child_list.remove(obj)
            child_list.insert(row,obj)
            
            # abort if a valid order was attempt to destroy
            if was_ordered and self.birth_dates_in_order(child_list) == False:
                WarningDialog(_("Attempt to Reorder Children Failed"),
                              _("Children must be ordered by their birth dates."))
                return
            self.family.set_child_handle_list(child_list)
            trans = self.parent.db.transaction_begin()
            self.parent.db.commit_family(self.family,trans)
            self.parent.db.transaction_commit(trans,_('Reorder children'))
            self.load_family(self.family)

    def sp_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        self.in_drag = True
        path = self.spouse_list.get_path_at_pos(x,y)
        if path == None:
            row = len(self.person.get_family_handle_list())
        else:
            row = path[0][0] -1
        
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]

            if mytype != 'spouse':
                return

            s,i = self.spouse_selection.get_selected()
            if not i:
                return

            spath = s.get_path(i)
            src = spath[0] 
            family_list = self.person.get_family_handle_list()

            obj = family_list[src]
            family_list.remove(obj)
            family_list.insert(row,obj)

            self.person.set_family_handle_list(family_list)
            trans = self.parent.db.transaction_begin()
            self.parent.db.commit_person(self.person,trans)
            self.parent.db.transaction_commit(trans,_('Reorder spouses'))
            self.load_family()
            #self.display_marriage(self.family)
        self.in_drag = False
            
    def drag_data_get(self,widget, context, sel_data, info, time):
        store,node = self.child_selection.get_selected()
        if not node:
            return
        handle = self.child_model.get_value(node,_HANDLE_COL)
        bits_per = 8; # we're going to pass a string

        if sel_data.target == DdTargets.PERSON_LINK.drag_type:
            sel_data.set(sel_data.target, bits_per, handle)
        else:
            data = str(('child',handle));
            sel_data.set(sel_data.target, bits_per, data)

    def sp_drag_data_get(self,widget, context, sel_data, info, time):
        store,node = self.spouse_selection.get_selected()
        if not node:
            return
        handle = self.spouse_model.get_value(node,1)
        bits_per = 8; # we're going to pass a string
        data = str(('spouse',handle));
        sel_data.set(sel_data.target, bits_per, data)

    def north_american(self,val):
        if self.person.get_gender() == RelLib.Person.MALE:
            pname = self.person.get_primary_name()
            return (pname.get_surname_prefix(),pname.get_surname())
        elif self.family:
            fid = self.family.get_father_handle()
            f = self.parent.db.get_family_from_handle(fid)
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
        if self.person.get_gender() == RelLib.Person.MALE:
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

    def birth_dates_in_order(self,list):
        """Check any *valid* birthdates in the list to insure that they are in
        numerically increasing order."""
        inorder = True
        prev_date = 0
        for i in range(len(list)):
            child_handle = list[i]
            child = self.parent.db.get_person_from_handle(child_handle)
            birth_handle = child.get_birth_handle()
            birth = self.parent.db.get_event_from_handle(birth_handle)
            if not birth:
                continue
            child_date = birth.get_date_object().get_sort_value()
            if child_date == 0:
                continue
            if prev_date <= child_date: # <= allows for twins
                prev_date = child_date
            else:
                inorder = False
        return inorder
