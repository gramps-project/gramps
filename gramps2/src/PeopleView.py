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


#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import cPickle as pickle
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

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
import PeopleModel
import GenericFilter
from DdTargets import DdTargets

column_names = [
    _('Name'),
    _('ID') ,
    _('Gender'),
    _('Birth Date'),
    _('Birth Place'),
    _('Death Date'),
    _('Death Place'),
    _('Spouse'),
    _('Last Change'),
    _('Cause of Death'),
    ]

#-------------------------------------------------------------------------
#
# PeopleView
#
#-------------------------------------------------------------------------
class PeopleView:

    def __init__(self,parent):
        self.parent = parent

        self.parent.connect('database-changed',self.change_db)

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        self.DataFilter = None
        self.pscroll = self.parent.gtop.get_widget("pscroll")
        self.person_tree = self.parent.gtop.get_widget("person_tree")
        self.person_tree.set_rules_hint(True)
        self.renderer = gtk.CellRendererText()

        self.columns = []
        self.build_columns()
        self.person_selection = self.person_tree.get_selection()
        self.person_selection.set_mode(gtk.SELECTION_MULTIPLE)
        self.person_selection.connect('changed',self.row_changed)
        self.person_selection.connect('changed',self.set_dnd_target)
        self.person_tree.connect('row_activated', self.alpha_event)
        self.person_tree.connect('button-press-event',
                                 self.on_plist_button_press)

        #
        # DnD support
        #
        self.person_tree.connect('drag_data_get', self.person_drag_data_get)

    def person_drag_data_get(self, widget, context, sel_data, info, time):
        selected_ids = self.get_selected_objects()

        if len(selected_ids) == 1:
            sel_data.set(sel_data.target, 8, selected_ids[0])
        elif len(selected_ids) > 1:
            sel_data.set(DdTargets.PERSON_LINK_LIST.drag_type,8,
                         pickle.dumps(selected_ids))
            
    def set_dnd_target(self,obj):
        selected_ids = self.get_selected_objects()

        if len(selected_ids) == 1:
            self.person_tree.drag_source_set(BUTTON1_MASK,
                                             [DdTargets.PERSON_LINK.target()],
                                             ACTION_COPY)
        elif len(selected_ids) > 1:
            self.person_tree.drag_source_set(BUTTON1_MASK,
                                             [DdTargets.PERSON_LINK_LIST.target()],
                                             ACTION_COPY)
                 


    def sort_clicked(self,obj):
        for col in self.columns:
            if obj == col:
                if col.get_sort_indicator():
                    if col.get_sort_order() == gtk.SORT_ASCENDING:
                        col.set_sort_order(gtk.SORT_DESCENDING)
                    else:
                        col.set_sort_order(gtk.SORT_ASCENDING)
                else:
                    col.set_sort_order(gtk.SORT_ASCENDING)
                col.set_sort_indicator(True)
            else:
                col.set_sort_indicator(False)
        
    def build_columns(self):
        for column in self.columns:
            self.person_tree.remove_column(column)
            
        column = gtk.TreeViewColumn(_('Name'), self.renderer,text=0)
        column.set_resizable(True)
        #column.set_clickable(True)
        #column.connect('clicked',self.sort_clicked)
        column.set_min_width(225)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.person_tree.append_column(column)
        self.columns = [column]

        index = 1
        for pair in self.parent.db.get_person_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = gtk.TreeViewColumn(name, self.renderer, markup=pair[1])
            column.set_resizable(True)
            column.set_min_width(60)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
            self.columns.append(column)
            self.person_tree.append_column(column)
            index += 1

    def build_tree(self):
        self.person_model = PeopleModel.PeopleModel(self.parent.db,
                                                    self.DataFilter,
                                                    self.parent.filter_invert.get_active())
        self.person_tree.set_model(self.person_model)
        
    def blist(self, store, path, node, id_list):
        idval = self.person_model.get_value(node, PeopleModel.COLUMN_INT_ID)
        id_list.append(idval)

    def get_selected_objects(self):
        mlist = []
        self.person_selection.selected_foreach(self.blist,mlist)
        return mlist
        
    def row_changed(self,obj):
        """Called with a row is changed. Check the selected objects from
        the person_tree to get the IDs of the selected objects. Set the
        active person to the first person in the list. If no one is
        selected, set the active person to None"""

        selected_ids = self.get_selected_objects()

        try:
            person = self.parent.db.get_person_from_handle(selected_ids[0])
            self.parent.change_active_person(person)
        except:
            self.parent.change_active_person(None)

    def change_db(self,db):
        self.build_columns()
        self.person_model = PeopleModel.PeopleModel(db,self.DataFilter)
        self.person_tree.set_model(self.person_model)

        db.connect('person-add', self.person_added)
        db.connect('person-update', self.person_updated)
        db.connect('person-delete', self.person_removed)
        db.connect('person-rebuild', self.redisplay_person_list)
        self.apply_filter()

    def remove_from_person_list(self,person):
        """Remove the selected person from the list. A person object is
        expected, not an ID"""
        path = self.person_model.on_get_path(person.get_handle())
        self.person_model.row_deleted(path)
    
    def remove_from_history(self,person_handle,old_id=None):
        """Removes a person from the history list"""
        if old_id:
            del_id = old_id
        else:
            del_id = person_handle

        hc = self.parent.history.count(del_id)
        for c in range(hc):
            self.parent.history.remove(del_id)
            self.parent.hindex -= 1
        
        mhc = self.parent.mhistory.count(del_id)
        for c in range(mhc):
            self.parent.mhistory.remove(del_id)

    def apply_filter_clicked(self):
        index = self.parent.filter_list.get_active()
        self.DataFilter = self.parent.filter_model.get_filter(index)
        if self.DataFilter.need_param:
            qual = unicode(self.parent.filter_text.get_text())
            self.DataFilter.set_parameter(qual)
        self.apply_filter()
        self.goto_active_person()

    def add_to_person_list(self,person,change=0):
        pass

    def goto_active_person(self):
        if not self.parent.active_person:
            return
        p = self.parent.active_person
        try:
            path = self.person_model.on_get_path(p.get_handle())
            group_name = p.get_primary_name().get_group_name()
            top_name = self.parent.db.get_name_group_mapping(group_name)
            top_path = self.person_model.on_get_path(top_name)
            self.person_tree.expand_row(top_path,0)
            self.person_selection.unselect_all()
            self.person_selection.select_path(path)
            self.person_tree.scroll_to_cell(path,None,1,0.5,0)
        except KeyError:
            self.person_selection.unselect_all()
            print "Person not currently available due to filter"
            self.parent.active_person = p

    def alpha_event(self,*obj):
        self.parent.load_person(self.parent.active_person)

    def apply_filter(self,current_model=None):
        self.parent.status_text(_('Updating display...'))
        self.build_tree()
        self.parent.modify_statusbar()
        
    def on_plist_button_press(self,obj,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_people_context_menu(event)

    def build_people_context_menu(self,event):
        """Builds the menu with navigation and 
        editing operations on the people's list"""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        mlist = self.get_selected_objects()
        if mlist:
            sel_sensitivity = 1
        else:
            sel_sensitivity = 0
        merge_sensitivity = len(mlist) == 2
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            (gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Add Bookmark"),self.parent.on_add_bookmark_activate,sel_sensitivity),
            (None,None,0),
            (gtk.STOCK_ADD, self.parent.add_button_clicked,1),
            (gtk.STOCK_REMOVE, self.parent.remove_button_clicked,sel_sensitivity),
            (_("Edit"), self.parent.edit_button_clicked,sel_sensitivity),
            #(None,None,0),
            #(_("Compare and Merge"), self.parent.on_merge_activate,
            # merge_sensitivity),
            #(_("Fast Merge"), self.parent.on_fast_merge_activate,
            # merge_sensitivity),
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
        
    def redisplay_person_list(self):
        self.build_tree()

    def person_added(self,handle_list):
        for node in handle_list:
            person = self.parent.db.get_person_from_handle(node)
            top = person.get_primary_name().get_group_name()
            self.person_model.rebuild_data(self.DataFilter)
            if not self.person_model.is_visable(node):
                continue
            if (not self.person_model.sname_sub.has_key(top) or 
                len(self.person_model.sname_sub[top]) == 1):
                path = self.person_model.on_get_path(top)
                pnode = self.person_model.get_iter(path)
                self.person_model.row_inserted(path,pnode)
            path = self.person_model.on_get_path(node)
            pnode = self.person_model.get_iter(path)
            self.person_model.row_inserted(path,pnode)

    def person_removed(self,handle_list):
        for node in handle_list:
            person = self.parent.db.get_person_from_handle(node)
            if not self.person_model.is_visable(node):
                continue
            top = person.get_primary_name().get_group_name()
            mylist = self.person_model.sname_sub.get(top,[])
            if mylist:
                try:
                    path = self.person_model.on_get_path(node)
                    self.person_model.row_deleted(path)
                    if len(mylist) == 1:
                        path = self.person_model.on_get_path(top)
                        self.person_model.row_deleted(path)
                except KeyError:
                    pass
        self.person_model.rebuild_data(self.DataFilter,skip=node)

    def person_updated(self,handle_list):

        for node in handle_list:
            person = self.parent.db.get_person_from_handle(node)
            try:
                oldpath = self.person_model.iter2path[node]
            except:
                return
            pathval = self.person_model.on_get_path(node)
            pnode = self.person_model.get_iter(pathval)

            # calculate the new data
            self.person_model.calculate_data(self.DataFilter)
            
            # find the path of the person in the new data build
            newpath = self.person_model.temp_iter2path[node]
            
            # if paths same, just issue row changed signal

            if oldpath == newpath:
                self.person_model.row_changed(pathval,pnode)
            else:
                # paths different, get the new surname list
                
                mylist = self.person_model.temp_sname_sub.get(oldpath[0],[])
                path = self.person_model.on_get_path(node)
                
                # delete original
                self.person_model.row_deleted(pathval)
                
                # delete top node of original if necessar
                if len(mylist)==0:
                    self.person_model.row_deleted(pathval[0])
                    
                # determine if we need to insert a new top node',
                insert = not self.person_model.sname_sub.has_key(newpath[0])

                # assign new data
                self.person_model.assign_data()
                
                # insert new row if needed
                if insert:
                    path = self.person_model.on_get_path(newpath[0])
                    pnode = self.person_model.get_iter(path)
                    self.person_model.row_inserted(path,pnode)

                # insert new person
                path = self.person_model.on_get_path(node)
                pnode = self.person_model.get_iter(path)
                self.person_model.row_inserted(path,pnode)
                
        #self.parent.change_active_person(person)
        self.goto_active_person()
