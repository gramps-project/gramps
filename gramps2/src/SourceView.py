#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2004  Donald N. Allingham
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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import EditSource
import Utils
import DisplayModels
import const

from QuestionDialog import QuestionDialog

_HANDLE_COL = 5

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _


column_names = [
    _('Title'),
    _('ID'),
    _('Author'),
    _('Abbreviation'),
    _('Publication Information'),
    ]

#-------------------------------------------------------------------------
#
# SouceView
#
#-------------------------------------------------------------------------
class SourceView:
    def __init__(self,parent,db,glade,update):
        self.parent = parent
        self.glade = glade
        self.update = update
        self.list = glade.get_widget("source_list")
        self.list.connect('button-press-event',self.button_press)        
        self.selection = self.list.get_selection()

        self.renderer = gtk.CellRendererText()

        if const.nosort_tree:
            self.model = DisplayModels.SourceModel(self.parent.db)
        else:
            self.model = gtk.TreeModelSort(DisplayModels.SourceModel(self.parent.db))
        self.list.set_model(self.model)
        self.topWindow = self.glade.get_widget("gramps")

        self.columns = []
        self.build_columns()

    def build_columns(self):
        for column in self.columns:
            self.list.remove_column(column)
            
        column = gtk.TreeViewColumn(_('Title'), self.renderer,text=0)
        column.set_resizable(gtk.TRUE)
        if not const.nosort_tree:
            column.set_clickable(gtk.TRUE)
            column.set_sort_column_id(0)
        column.set_min_width(225)
        self.list.append_column(column)
        self.columns = [column]

        index = 1
        for pair in self.parent.db.get_source_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = gtk.TreeViewColumn(name, self.renderer, text=pair[1])
            column.set_resizable(gtk.TRUE)
            if not const.nosort_tree:
                column.set_clickable(gtk.TRUE)
                column.set_sort_column_id(index)
            column.set_min_width(75)
            self.columns.append(column)
            self.list.append_column(column)
            index += 1

    def on_click(self,column):
        self.click_col = column

    def change_db(self,db):
        self.build_columns()
        self.build_tree()

    def build_tree(self):
        self.list.set_model(None)
        if const.nosort_tree:
            self.model = DisplayModels.SourceModel(self.parent.db)
        else:
            self.model = gtk.TreeModelSort(DisplayModels.SourceModel(self.parent.db))
        self.list.set_model(self.model)
        self.selection = self.list.get_selection()

    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            store,iter = self.selection.get_selected()
            id = store.get_value(iter,_HANDLE_COL)
            source = self.parent.db.get_source_from_handle(id)
            EditSource.EditSource(source,self.parent.db,self.parent,
                                  self.topWindow,self.update_display)
            return 1
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu(event)
            return 1
        return 0

    def key_press(self,obj,event):
    	if event.keyval == gtk.gdk.keyval_from_name("Return") \
    	    	    	    	    	and not event.state:
    	    self.on_edit_clicked(obj)
    	    return 1
    	return 0

    def build_context_menu(self,event):
        """Builds the menu with editing operations on the source's list"""
        
        store,iter = self.selection.get_selected()
        if iter:
            sel_sensitivity = 1
        else:
            sel_sensitivity = 0
        entries = [
            (gtk.STOCK_ADD, self.on_add_clicked,1),
            (gtk.STOCK_REMOVE, self.on_delete_clicked,sel_sensitivity),
            (_("Edit"), self.on_edit_clicked,sel_sensitivity),
        ]

        menu = gtk.Menu()
        menu.set_title(_('Source Menu'))
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def on_add_clicked(self,obj):
        EditSource.EditSource(RelLib.Source(),self.parent.db,self.parent,
                              self.topWindow,self.new_after_edit)

    def on_delete_clicked(self,obj):
        store,iter = self.selection.get_selected()
        if not iter:
            return
        
        id = store.get_value(iter,_HANDLE_COL)
        source = self.parent.db.get_source_from_handle(id)

        if self.is_used(source):
            ans = EditSource.DelSrcQuery(source,self.parent.db,self.build_tree)

            QuestionDialog(_('Delete %s?') % source.get_title(),
                           _('This source is currently being used. Deleting it '
                             'will remove it from the database and from all '
                             'records that reference it.'),
                           _('_Delete Source'),
                           ans.query_response,self.topWindow)
        else:
            trans = self.parent.db.start_transaction()
            self.parent.db.remove_source_handle(source.get_handle(),trans)
            n = source.get_title()
            self.parent.db.add_transaction(trans,_("Delete Source (%s)") % n)
            self.build_tree()

    def is_used(self,source):
        for key in self.parent.db.get_place_handle_keys():
            p = self.parent.db.get_place_from_handle(key)
            for sref in p.get_source_references():
                if sref.get_base_handle() == source.get_handle():
                    return 1
        for key in self.parent.db.get_person_keys():
            p = self.parent.db.get_person_from_handle(key)
            for v_id in p.get_event_list() + [p.get_birth_handle(), p.get_death_handle()]:
                v = self.parent.db.find_event_from_handle(v_id)
                if v:
                    for sref in v.get_source_references():
                        if sref.get_base_handle() == source.get_handle():
                            return 1
            for v in p.get_attribute_list():
                for sref in v.get_source_references():
                    if sref.get_base_handle() == source.get_handle():
                        return 1
            for v in p.get_alternate_names() + [p.get_primary_name()]:
                for sref in v.get_source_references():
                    if sref.get_base_handle() == source.get_handle():
                        return 1
            for v in p.get_address_list():
                for sref in v.get_source_references():
                    if sref.get_base_handle() == source.get_handle():
                        return 1
        for p_id in self.parent.db.get_object_keys():
            p = self.parent.db.get_object_from_handle(p_id)
            for sref in p.get_source_references():
                if sref.get_base_handle() == source.get_handle():
                    return 1
        for p_id in self.parent.db.get_family_keys():
            p = self.parent.db.find_family_from_handle(p_id)
            for v_id in p.get_event_list():
                v = self.parent.db.find_event_from_handle(v_id)
                if v:
                    for sref in v.get_source_references():
                        if sref.get_base_handle() == source.get_handle():
                            return 1
            for v in p.get_attribute_list():
                for sref in v.get_source_references():
                    if sref.get_base_handle() == source.get_handle():
                        return 1
        return 0

    def on_edit_clicked(self,obj):
        list_store, iter = self.selection.get_selected()
        if iter:
            id = list_store.get_value(iter,_HANDLE_COL)
            source = self.parent.db.get_source_from_handle(id)
            EditSource.EditSource(source, self.parent.db, self.parent,
                                  self.topWindow, self.update_display)

    def new_after_edit(self,source):
        self.parent.db.add_source(source)
        self.build_tree()

    def update_display(self,place):
        self.build_tree()
