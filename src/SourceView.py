#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2003  Donald N. Allingham
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
# standard python modules
#
#-------------------------------------------------------------------------

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

from QuestionDialog import QuestionDialog

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# SouceView
#
#-------------------------------------------------------------------------
class SourceView:
    def __init__(self,db,glade,update):
        self.glade = glade
        self.db = db
        self.update = update
        self.list = glade.get_widget("source_list")
        self.selection = self.list.get_selection()
        colno = 0

        self.column_headers = [(_('Title'),3,350),(_('ID'),1,50),
                               (_('Author'),4,70),('',3,0),('',4,0) ]

        for title in self.column_headers:
            renderer = gtk.CellRendererText ()
            renderer.set_fixed_height_from_font(1)
            column = gtk.TreeViewColumn (title[0], renderer, text=colno)
            colno = colno + 1
            column.set_clickable (gtk.TRUE)
            if title[0] == '':
                column.set_visible(gtk.FALSE)
            else:
                column.set_resizable(gtk.TRUE)
                column.set_visible(gtk.TRUE)
            column.set_sort_column_id(title[1])
            column.set_min_width(title[2])
            self.list.append_column(column)

        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)
        self.list.set_model(self.model)
        self.topWindow = self.glade.get_widget("gramps")

    def change_db(self,db):
        self.db = db

    def goto(self,id):
        iter = self.map[id]
        self.list.get_selection().select_iter(iter)
        itpath = self.model.get_path (iter)
        col = self.list.get_column (0)
        self.list.scroll_to_cell (itpath, col, gtk.TRUE, 0.5, 0)

    def load_sources(self):
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)
        self.map = {}
        
        for key in self.db.getSourceKeys():
            val = self.db.getSourceDisplay(key)
                
            iter = self.model.append()
            self.map[val[1]] = iter
            self.model.set(iter, 0, val[0], 1, val[1], 2, val[2],
                           3, val[3], 4, val[4])
            self.list.connect('button-press-event',self.button_press)
        self.list.set_model(self.model)
                
    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            store,iter = self.selection.get_selected()
            id = store.get_value(iter,1)
            source = self.db.getSource(id)
            EditSource.EditSource(source,self.db,self.topWindow,self.update_display)
            return 1
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu(event)
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
        EditSource.EditSource(RelLib.Source(),self.db,self.topWindow,self.new_after_edit)

    def on_delete_clicked(self,obj):
        
        store,iter = self.selection.get_selected()
        if not iter:
            return
        
        id = store.get_value(iter,1)
        source = self.db.getSource(id)

        if self.is_used(source):
            ans = EditSource.DelSrcQuery(source,self.db,self.update)

            QuestionDialog(_('Delete %s?') % source.getTitle(),
                           _('This source is currently being used. Deleting it '
                             'will remove it from the database and from all '
                             'records that reference it.'),
                           _('_Delete Source'),
                           ans.query_response,self.topWindow)
        else:
            self.db.removeSource(source.getId())
            Utils.modified()
            self.update(0)

    def is_used(self,source):
        for key in self.db.getPlaceKeys():
            p = self.db.getPlace(key)
            for sref in p.getSourceRefList():
                if sref.getBase() == source:
                    return 1
        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            for v in p.getEventList() + [p.getBirth(), p.getDeath()]:
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
            for v in p.getAttributeList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
            for v in p.getAlternateNames() + [p.getPrimaryName()]:
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
            for v in p.getAddressList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
        for p in self.db.getObjectMap().values():
            for sref in p.getSourceRefList():
                if sref.getBase() == source:
                    return 1
        for p in self.db.getFamilyMap().values():
            for v in p.getEventList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
            for v in p.getAttributeList():
                for sref in v.getSourceRefList():
                    if sref.getBase() == source:
                        return 1
        return 0

    def on_edit_clicked(self,obj):
        list_store, iter = self.selection.get_selected()
        if iter:
            id = list_store.get_value(iter,1)
            source = self.db.getSource(id)
            EditSource.EditSource(source, self.db, self.topWindow, self.update_display)

    def new_after_edit(self,source):
        self.db.addSource(source)
        self.update(0)

    def update_display(self,place):
        self.db.buildSourceDisplay(place.getId())
        self.update(0)

