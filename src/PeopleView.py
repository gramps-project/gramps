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

_sel_mode = gtk.SELECTION_SINGLE

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
import PeopleModel
import Filter

column_names = [
    _('Name'),
    _('ID') ,
    _('Gender'),
    _('Birth Date'),
    _('Birth Place'),
    _('Death Date'),
    _('Death Place'),
    ]

#-------------------------------------------------------------------------
#
# PeopleView
#
#-------------------------------------------------------------------------
class PeopleView:

    def __init__(self,parent):
        self.parent = parent

        self.DataFilter = Filter.Filter("")
        self.pscroll = self.parent.gtop.get_widget("pscroll")
        self.person_tree = self.parent.gtop.get_widget("person_tree")
        self.person_tree.set_rules_hint(gtk.TRUE)
        self.renderer = gtk.CellRendererText()

        self.columns = []
        self.build_columns()
        self.build_tree()

    def build_columns(self):
        for column in self.columns:
            self.person_tree.remove_column(column)
            
        column = gtk.TreeViewColumn(_('Name'), self.renderer,text=0)
        column.set_resizable(gtk.TRUE)        
        column.set_clickable(gtk.TRUE)
        column.set_min_width(225)
        column.set_sort_column_id(PeopleModel.COLUMN_NAME_SORT)
        self.person_tree.append_column(column)
        self.columns = [column]

        index = 1
        for pair in self.parent.db.get_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = gtk.TreeViewColumn(name, self.renderer, text=pair[1])
            column.set_resizable(gtk.TRUE)
            #column.set_clickable(gtk.TRUE)
            column.set_min_width(60)
            column.set_sort_column_id(index)
            self.columns.append(column)
            self.person_tree.append_column(column)
            index += 1

    def build_tree(self):
        self.person_tree.set_model(None)
        self.person_model = PeopleModel.PeopleModel(self.parent.db)

        self.sort_model = gtk.TreeModelSort(self.person_model)
        self.person_tree.set_model(self.sort_model)

        #self.person_tree.set_model(self.person_model)

        self.person_selection = self.person_tree.get_selection()
        self.person_selection.connect('changed',self.row_changed)
        self.person_tree.connect('row_activated', self.alpha_event)
        self.person_tree.connect('button-press-event',self.on_plist_button_press)        

    def blist(self,store,path,iter,id_list):
        #id_list.append(self.person_model.get_value(iter,1))
        id_list.append(self.sort_model.get_value(iter,1))

    def get_selected_objects(self):
        mlist = []
        self.person_selection.selected_foreach(self.blist,mlist)
        return mlist
        
    def row_changed(self,obj):
        """Called with a row is changed. Check the selected objects from the person_tree
        to get the IDs of the selected objects. Set the active person to the first person
        in the list. If no one is selected, set the active person to None"""

        selected_ids = self.get_selected_objects()

        try:
            person = self.parent.db.get_person(selected_ids[0])
            self.parent.change_active_person(person)
        except:
            self.parent.change_active_person(None)
            self.person_selection.unselect_all()

    def change_db(self,db):
        self.build_columns()
        self.build_tree()

    def clear(self):
        pass

    def remove_from_person_list(self,person,old_id=None):
        """Remove the selected person from the list. A person object is expected,
        not an ID"""
        if old_id == None or person.get_id() == old_id:
            path = self.person_model.on_get_path(person.get_id())
            self.person_model.row_deleted(path)
        else:
            self.person_model.rebuild_data()
    
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
        self.rebuild_data()

    def goto_active_person(self,first=0):
        if not self.parent.active_person:
            return
        p = self.parent.active_person
        id = p.get_id()
        path = self.person_model.on_get_path(id)
        top_path = self.person_model.on_get_path(p.get_primary_name().get_surname())
        self.person_tree.expand_row(top_path,0)
        self.person_selection.select_path(path)
        self.person_tree.scroll_to_cell(path,None,1,0.5,0)

    def alpha_event(self,obj,a,b):
        self.parent.load_person(self.parent.active_person)

    def apply_filter(self,current_model=None):
        self.parent.status_text(_('Updating display...'))
        self.parent.modify_statusbar()
        
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
        self.person_model.rebuild_data()
