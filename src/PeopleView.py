# -*- coding: utf-8 -*-
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

# $Id$

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

from gtk.gdk import ACTION_COPY, BUTTON1_MASK

_sel_mode = gtk.SELECTION_MULTIPLE

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
import PeopleStore
import Filter

#-------------------------------------------------------------------------
#
# PeopleView
#
#-------------------------------------------------------------------------
class PeopleView:

    def __init__(self,parent):
        self.parent = parent

        self.DataFilter = Filter.Filter("")
        self.ptabs      = self.parent.gtop.get_widget("ptabs")
        self.pl_other   = self.parent.gtop.get_widget("pl_other")

        self.ptabs.set_show_tabs(0)

        self.pl_page = [
            PeopleStore.PeopleStore(self.pl_other, self, self.row_changed,
                                    self.alpha_event, _sel_mode),
            ]

        self.person_tree = self.pl_page[0]
        self.person_list = self.pl_page[0].tree
        self.person_model = self.pl_page[0].model
        self.person_list.connect('button-press-event',self.on_plist_button_press)        
        
        self.default_list = self.pl_page[-1]

        self.alpha_page = {}
        self.model2page = {}
        self.model_used = {}
        self.tab_list = []
        self.clearing_tabs = 0

    def row_changed(self,obj):
        """Called with a row is changed. Check the selected objects from the person_tree
        to get the IDs of the selected objects. Set the active person to the first person
        in the list. If no one is selected, set the active person to None"""
        selected_id_list = self.person_tree.get_selected_objects()
        if selected_id_list:
            assert(selected_id_list[0])
            try:
                self.parent.change_active_person(self.parent.db.get_person(selected_id_list[0]))
            except:
                self.parent.change_active_person(None)
                self.person_tree.unselect()
                
    def change_alpha_page(self,obj,junk,page):
        """Change the page. Be careful not to take action while the pages
        are begin removed. If clearing_tabs is set, then we don't do anything"""
        
        if self.clearing_tabs:
            return
	self.person_tree = self.pl_page[page]
        self.person_list = self.pl_page[page].tree
        self.person_model = self.pl_page[page].model
        if not self.model_used.has_key(self.person_tree) or self.model_used[self.person_tree] == 0:
            self.model_used[self.person_tree] = 1
            self.apply_filter(self.person_tree)
            self.person_list.connect('button-press-event',self.on_plist_button_press)
        
    def clear_person_tabs(self):
        self.clearing_tabs = 1
        self.ptabs.hide()
        for i in range(0,len(self.tab_list)):
            self.ptabs.remove_page(0)
        self.ptabs.set_show_tabs(0)
        self.ptabs.show()
        self.clearing_tabs = 0

        self.default_list.clear()

        for page in self.pl_page[0:-1]:
            del page
        
        self.pl_page = [
            self.default_list
            ]

        self.person_tree = self.pl_page[-1]
        self.person_list = self.pl_page[-1].tree
        self.person_model = self.pl_page[-1].model

        self.id2col  = {}
        self.tab_list = []
        self.alpha_page = {}
        self.model2page = {self.default_list : 0}
        self.model_used = {}

    def change_db(self,db):
        self.id2col = {}

    def clear(self):
        for model in self.pl_page:
            model.clear()

    def remove_from_person_list(self,person,old_id=None):
        """Remove the selected person from the list. A person object is expected,
        not an ID"""

        person_id = person.get_id()
        if old_id:
            del_id = old_id
        else:
            del_id = person_id

        if self.id2col.has_key(del_id):
            (model,iter) = self.id2col[del_id]
            if iter:
                model.remove(iter)
            del self.id2col[del_id]
            
            if person == self.parent.active_person:
                self.parent.active_person = None
    
    def remove_from_history(self,person,old_id=None):
        """Removes a person from the history list"""
        
        person_id = person.get_id()
        if old_id:
            del_id = old_id
        else:
            del_id = person_id

        hc = self.parent.history.count(del_id)
        for c in range(hc):
            self.parent.history.remove(del_id)
            self.parent.hindex = self.parent.hindex - 1
        
        mhc = self.parent.mhistory.count(del_id)
        for c in range(mhc):
            self.parent.mhistory.remove(del_id)

    def apply_filter_clicked(self):
        invert_filter = self.parent.filter_inv.get_active()
        qualifer = unicode(self.parent.filter_text.get_text())
        mi = self.parent.filter_list.get_menu().get_active()
        class_init = mi.get_data("function")
        self.DataFilter = class_init(qualifer)
        self.DataFilter.set_invert(invert_filter)
        self.model_used = {}
        self.clear_person_tabs()
        self.apply_filter(self.person_tree)
        self.goto_active_person()

    def add_to_person_list(self,person,change):
        key = person.get_id()
        val = self.parent.db.get_person_display(person.get_id())
        pg = unicode(val[5])
        pg = pg[0]
        model = None
        if self.DataFilter.compare(person):

            if pg and pg != '@':
                if not self.alpha_page.has_key(pg):
                    self.create_new_panel(pg)
                model = self.alpha_page[pg]
            else:
                model = self.default_list

            iter = model.add([val[0],val[1],val[2],val[3],val[4],val[5],
                              val[6],val[7],val[8]],1)

            self.id2col[key] = (model,iter)

        if change:
            self.parent.change_active_person(person)
        self.goto_active_person()
        if model:
            model.enable_sort()

    def goto_active_person(self,first=0):
        if not self.parent.active_person:
            if first:
                page = 0
            else:
                page = self.ptabs.get_current_page()

            self.person_tree = self.pl_page[page]
            self.person_list = self.pl_page[page].tree
            self.person_model = self.pl_page[page].model
            self.ptabs.set_current_page(page)
            return
        
        id = self.parent.active_person.get_id()
        val = self.parent.db.get_person_display(id)
        if self.id2col.has_key(id):
            (model,iter) = self.id2col[id]
        else:
            pg = val[5]
            if pg and pg != '@':
                pg = pg[0]
            else:
                pg = ''
            if not self.alpha_page.has_key(pg):
                self.create_new_panel(pg)
            model = self.alpha_page[pg]
            iter = None

        self.ptabs.set_current_page(self.model2page[model])

        if not self.model_used.has_key(model) or self.model_used[model] == 0 or not iter:
            self.model_used[model] = 1
            self.apply_filter(model)
            try:
                (model,iter) = self.id2col[id]
            except KeyError:
                return

        if not iter:
            self.parent.status_text(_('Updating display...'))
            model.expand_row(val[-1])
            (m,iter) = self.id2col[id]
            self.parent.modify_statusbar()

        try:
            model.selection.unselect_all()
            model.selection.select_iter(iter)
        except:
            print iter
            
        itpath = model.model.get_path(iter)
        col = model.tree.get_column(0)
        model.tree.scroll_to_cell(itpath,col,1,0.5,0)

    def alpha_event(self,obj):
        self.parent.load_person(self.parent.active_person)

    def apply_filter(self,current_model=None):
        self.parent.status_text(_('Updating display...'))

        datacomp = self.DataFilter.compare
        if current_model == None:
            self.id2col = {}

        for key in self.parent.db.sort_person_keys():
            person = self.parent.db.get_person(key)
            val = self.parent.db.get_person_display(key)
            pg = val[5]
            if pg and pg != '@':
                pg = pg[0]
            else:
                pg = ''

            if datacomp(person):
                if self.id2col.has_key(key):
                    continue
                if pg and pg != '@':
                    if not self.alpha_page.has_key(pg):
                        self.create_new_panel(pg)
                    model = self.alpha_page[pg]
                else:
                    model = self.default_list

                if current_model == model:
                    iter = model.add([val[0],val[1],val[2],val[3],val[4],val[5],
                                      val[6],val[7],val[8]])
                    self.id2col[key] = (model,iter)
            else:
                if self.id2col.has_key(key):
                    (model,iter) = self.id2col[key]
                    if iter:
                        model.remove(iter)
                    del self.id2col[key]

        for i in self.pl_page:
            i.sort()

        self.parent.modify_statusbar()

    def create_new_panel(self,pg):
        
        display = gtk.ScrolledWindow()
        display.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        tree = gtk.TreeView()
        tree.show()
        display.add(tree)
        display.show()
        model = PeopleStore.PeopleStore(tree, self, self.row_changed,
                                        self.alpha_event,_sel_mode)
        self.alpha_page[pg] = model
        for index in range(0,len(self.tab_list)):
            try:
                if pg < self.tab_list[index]:
                    self.ptabs.insert_page(display,gtk.Label(pg),index)
                    self.ptabs.set_show_tabs(1)
                    self.tab_list.insert(index,pg)
                    self.pl_page.insert(index,model)
                    break
            except:
                print index
        else:
            #added by EARNEY on 5/5/2003
            #modified the block below because sometimes certain
            #letters under people panel
            #will not load properly after a quick add
            #(ie, adding a parent under the family panel)
            index=len(self.tab_list)
            self.ptabs.insert_page(display,gtk.Label(pg),index)
            self.ptabs.set_show_tabs(1)
            self.tab_list.insert(index,pg)
            self.pl_page.insert(index,model)

            #instead of the following..
            #self.ptabs.insert_page(display,gtk.Label(pg),len(self.tab_list))
            #self.ptabs.set_show_tabs(1)
            #self.tab_list.append(pg)
            #self.pl_page = self.pl_page[0:-1] + [model,self.default_list]


        for index in range(0,len(self.tab_list)):
            model = self.alpha_page[self.tab_list[index]]
            self.model2page[model] = index
            self.model_used[model] = 0
        self.model2page[self.default_list] = len(self.tab_list)
        self.model_used[self.default_list] = 0

        
    def on_plist_button_press(self,obj,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_people_context_menu(event)

    def build_people_context_menu(self,event):
        """Builds the menu with navigation and 
        editing operations on the people's list"""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        mlist = self.person_tree.get_selected_objects()
        if mlist:
            sel_sensitivity = 1
        else:
            sel_sensitivity = 0
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
	    #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (_("Add Bookmark"),self.parent.on_add_bookmark_activate,sel_sensitivity),
            (None,None,0),
            (gtk.STOCK_ADD, self.parent.add_button_clicked,1),
            (gtk.STOCK_REMOVE, self.parent.remove_button_clicked,sel_sensitivity),
            (_("Edit"), self.parent.edit_button_clicked,sel_sensitivity),
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
        
    def redisplay_person_list(self,person):
        self.add_to_person_list(person,1)

    def update_person_list(self,person,old_id):
        key = person.get_id()
        if old_id != key:
            (model,iter) = self.id2col[old_id]
            del self.id2col[old_id]
            self.id2col[key] = (model,iter)
        else:
            (model,iter) = self.id2col[key]
            
        val = self.parent.db.get_person_display(person.get_id())
        pg = unicode(val[5])[0]
        if self.DataFilter.compare(person):
            col = 0
            for object in val[:-1]:
                model.model.set_value(iter,col,object)
                col = col + 1
