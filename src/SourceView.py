#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  Donald N. Allingham
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
# standard python modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
try:
    import pygtk; pygtk.require('2.0')
except ImportError: # not set up for parallel install
    pass 
import gobject
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *
from QuestionDialog import QuestionDialog

import EditSource
import Utils
import GrampsCfg

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from intl import gettext as _

_column_headers = [(_('Title'),3,350),(_('ID'),1,50),(_('Author'),4,70),('',3,0),('',4,0) ]

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
        for title in _column_headers:
            renderer = gtk.CellRendererText ()
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

        self.list.set_search_column(0)
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)
        self.list.set_model(self.model)
        self.list.get_column(0).clicked()

    def change_db(self,db):
        self.db = db

    def load_sources(self):
        self.model.clear()

        for key in self.db.getSourceKeys():
            val = self.db.getSourceDisplay(key)
                
            iter = self.model.append()
            self.model.set(iter, 0, val[0], 1, val[1], 2, val[2],
                           3, val[3], 4, val[4])
            self.list.connect('button-press-event',self.button_press)
                
    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            store,iter = self.selection.get_selected()
            id = store.get_value(iter,1)
            source = self.db.getSource(id)
            EditSource.EditSource(source,self.db,self.update_display)
            return 1

    def on_add_clicked(self,obj):
        EditSource.EditSource(Source(),self.db,self.new_after_edit)

    def on_delete_clicked(self,obj):
        
        store,iter = self.selection.get_selected()
        if not iter:
            return
        
        id = store.get_value(iter,1)
        source = self.db.getSource(id)

        if self.is_used(source):
            ans = EditSource.DelSrcQuery(source,self.db,self.update)

            QuestionDialog(_('Delete Source'),
                           _("This source is currently being used. Delete anyway?"),
                           ans.query_response)
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
            EditSource.EditSource(source, self.db, self.update_display)

    def new_after_edit(self,source):
        self.db.addSource(source)
        self.update(0)

    def update_display(self,place):
        self.db.buildSourceDisplay(place.getId())
        self.update(0)

