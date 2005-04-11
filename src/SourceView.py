# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2005  Donald N. Allingham
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
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import EditSource
import DisplayModels
import const
import Utils
from QuestionDialog import QuestionDialog, ErrorDialog

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
    _('Last Changed'),
    ]

_HANDLE_COL = len(column_names)

#-------------------------------------------------------------------------
#
# SouceView
#
#-------------------------------------------------------------------------
class SourceView:
    def __init__(self,parent,db,glade):
        self.parent = parent
        self.parent.connect('database-changed',self.change_db)
        self.glade = glade
        self.list = glade.get_widget("source_list")
        #self.list.set_property('fixed-height-mode',True)
        self.list.connect('button-press-event',self.button_press)        
        self.selection = self.list.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)

        self.renderer = gtk.CellRendererText()

        self.model = DisplayModels.SourceModel(self.parent.db)
        self.list.set_model(self.model)
        self.topWindow = self.glade.get_widget("gramps")

        self.columns = []

    def build_columns(self):
        for column in self.columns:
            self.list.remove_column(column)
            
        column = gtk.TreeViewColumn(_('Title'), self.renderer,text=0)
        column.set_resizable(True)
        column.set_min_width(225)
        self.list.append_column(column)
        self.columns = [column]

        for pair in self.parent.db.get_source_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = gtk.TreeViewColumn(name, self.renderer, text=pair[1])
            column.set_resizable(True)
            column.set_min_width(75)
            self.columns.append(column)
            self.list.append_column(column)

    def on_click(self,column):
        self.click_col = column

    def change_db(self,db):
        db.connect('source-add',    self.source_add)
        db.connect('source-update', self.source_update)
        db.connect('source-delete', self.source_delete)
        db.connect('source-rebuild',self.build_tree)
        self.build_columns()
        self.build_tree()

    def build_tree(self):
        self.list.set_model(None)
        self.model = DisplayModels.SourceModel(self.parent.db)
        self.list.set_model(self.model)
        self.selection = self.list.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)

    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            handle = mlist[0]
            source = self.parent.db.get_source_from_handle(handle)
            EditSource.EditSource(source,self.parent.db,self.parent,
                                  self.topWindow)
            return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu(event)
            return True
        return False

    def key_press(self,obj,event):
        if event.keyval == gtk.gdk.keyval_from_name("Return") \
                                        and not event.state:
            self.on_edit_clicked(obj)
            return True
        return False

    def build_context_menu(self,event):
        """Builds the menu with editing operations on the source's list"""
        
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        if mlist:
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
                              self.topWindow)

    def on_delete_clicked(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for handle in mlist:
            source = self.parent.db.get_source_from_handle(handle)

            the_lists = Utils.get_source_referents(handle,self.parent.db)
            ans = EditSource.DelSrcQuery(source,self.parent.db,the_lists)

            if filter(None,the_lists): # quick test for non-emptiness
                msg = _('This source is currently being used. Deleting it '
                        'will remove it from the database and from all '
                        'records that reference it.')
            else:
                msg = _('Deleting source will remove it from the database.')
            
            msg = "%s %s" % (msg,Utils.data_recover_msg)
            QuestionDialog(_('Delete %s?') % source.get_title(), msg,
                           _('_Delete Source'),ans.query_response,
                           self.topWindow)

    def on_edit_clicked(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for handle in mlist:
            source = self.parent.db.get_source_from_handle(handle)
            EditSource.EditSource(source, self.parent.db, self.parent,
                                  self.topWindow)

    def source_add(self,handle_list):
        for handle in handle_list:
            self.model.add_row_by_handle(handle)

    def source_update(self,handle_list):
        for handle in handle_list:
            self.model.update_row_by_handle(handle)

    def source_delete(self,handle_list):
        for handle in handle_list:
            self.model.delete_row_by_handle(handle)

    def blist(self,store,path,iter,sel_list):
        handle = store.get_value(iter,_HANDLE_COL)
        sel_list.append(handle)

    def merge(self):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        if len(mlist) != 2:
            msg = _("Cannot merge sources.")
            msg2 = _("Exactly two sources must be selected to perform a merge. "
                "A second source can be selected by holding down the "
                "control key while clicking on the desired source.")
            ErrorDialog(msg,msg2)
        else:
            import MergeData
            MergeData.MergeSources(self.parent.db,mlist[0],mlist[1],
                                   self.build_tree)
