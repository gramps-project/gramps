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
import EventEdit
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
    _('Description'),
    _('ID'),
    _('Type'),
    _('Last Change'),
    _('Date'),
    _('Place'),
    _('Cause'),
    ]

_HANDLE_COL = 7

#-------------------------------------------------------------------------
#
# EventView
#
#-------------------------------------------------------------------------
class EventView:
    def __init__(self,parent,db,glade):
        self.parent = parent
        self.parent.connect('database-changed',self.change_db)

        self.glade = glade
        self.list = glade.get_widget("event_list")
        self.list.connect('button-press-event',self.button_press)        
        self.list.connect('key-press-event',self.key_press)
        self.selection = self.list.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)
        self.renderer = gtk.CellRendererText()
        self.model = DisplayModels.EventModel(self.parent.db,0)
        self.sort_col = 0
        
        self.list.set_model(self.model)
        self.list.set_headers_clickable(True)
        self.topWindow = self.glade.get_widget("gramps")

        self.columns = []
        self.change_db(db)

    def column_clicked(self,obj,data):
        if self.sort_col != data:
            order = gtk.SORT_ASCENDING
        else:
            if (self.columns[data].get_sort_order() == gtk.SORT_DESCENDING
                or self.columns[data].get_sort_indicator() == False):
                order = gtk.SORT_ASCENDING
            else:
                order = gtk.SORT_DESCENDING
        self.sort_col = data
        handle = self.first_selected()
        self.model = DisplayModels.EventModel(self.parent.db,
                                               self.sort_col,order)
        self.list.set_model(self.model)
        colmap = self.parent.db.get_repository_column_order()

        if handle:
            path = self.model.on_get_path(handle)
            self.selection.select_path(path)
            self.list.scroll_to_cell(path,None,1,0.5,0)
        for i in range(0,len(self.columns)):
            self.columns[i].set_sort_indicator(i==colmap[data][1]-1)
        self.columns[self.sort_col].set_sort_order(order)

    def build_columns(self):
        for column in self.columns:
            self.list.remove_column(column)
            
##         column = gtk.TreeViewColumn(_('Type'), self.renderer,text=0)
##         column.set_resizable(True)
##         column.set_min_width(225)
##         column.set_clickable(True)
##         column.connect('clicked',self.column_clicked,0)
##         self.list.append_column(column)
##         self.columns = [column]
        self.columns = []

        index = 0
        for pair in self.parent.db.get_event_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = gtk.TreeViewColumn(name, self.renderer, text=pair[1])
            column.connect('clicked',self.column_clicked,index)
            column.set_resizable(True)
            column.set_min_width(75)
            column.set_clickable(True)
            self.columns.append(column)
            self.list.append_column(column)
            index += 1

    def change_db(self,db):
        db.connect('event-add',    self.event_add)
        db.connect('event-update', self.event_update)
        db.connect('event-delete', self.event_delete)
        db.connect('event-rebuild',self.build_tree)
        self.build_columns()
        self.build_tree()

    def build_tree(self):
        self.list.set_model(None)
        self.model = DisplayModels.EventModel(self.parent.db,self.sort_col)
        self.list.set_model(self.model)
        self.selection = self.list.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)

    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            handle = mlist[0]
            the_event = self.parent.db.get_event_from_handle(handle)
            EventEdit.EventEditor(the_event,self.parent.db,self.parent,
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
        """Builds the menu with editing operations on the repository's list"""
        
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
        menu.set_title(_('Event Menu'))
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def on_add_clicked(self,obj):
        EventEdit.EventEditor(RelLib.Event(),self.parent.db,self.parent,
                              self.topWindow)

    def on_delete_clicked(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for event_handle in mlist:

            person_list = [ handle for handle in
                            self.parent.db.get_person_handles(False)
                            if self.parent.db.get_person_from_handle(handle).has_handle_reference('Event',event_handle) ]
            family_list = [ handle for handle in
                            self.parent.db.get_family_handles()
                            if self.parent.db.get_family_from_handle(handle).has_handle_reference('Event',event_handle) ]
            
            event = self.parent.db.get_event_from_handle(event_handle)

            ans = EventEdit.DelEventQuery(event,self.parent.db,
                                          person_list,family_list)

            if len(person_list) + len(family_list) > 0:
                msg = _('This event is currently being used. Deleting it '
                        'will remove it from the database and from all '
                        'people and families that reference it.')
            else:
                msg = _('Deleting event will remove it from the database.')
            
            msg = "%s %s" % (msg,Utils.data_recover_msg)
            QuestionDialog(_('Delete %s?') % event.get_gramps_id(), msg,
                           _('_Delete Event'),ans.query_response,
                           self.topWindow)

    def on_edit_clicked(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for handle in mlist:
            event = self.parent.db.get_event_from_handle(handle)
            EventEdit.EventEditor(event, self.parent.db, self.parent,
                                  self.topWindow)

    def event_add(self,handle_list):
        for handle in handle_list:
            self.model.add_row_by_handle(handle)

    def event_update(self,handle_list):
        for handle in handle_list:
            self.model.update_row_by_handle(handle)

    def event_delete(self,handle_list):
        for handle in handle_list:
            self.model.delete_row_by_handle(handle)

    def first_selected(self):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        if mlist:
            return mlist[0]
        else:
            return None

    def blist(self,store,path,iter,sel_list):
        handle = store.get_value(iter,_HANDLE_COL)
        sel_list.append(handle)

##    def merge(self):
##        mlist = []
##        self.selection.selected_foreach(self.blist,mlist)

##        if len(mlist) != 2:
##            msg = _("Cannot merge repositorys.")
##            msg2 = _("Exactly two repositorys must be selected to perform a merge. "
##                "A second repository can be selected by holding down the "
##                "control key while clicking on the desired repository.")
##            ErrorDialog(msg,msg2)
##        else:
##            import MergeData
##            MergeData.MergeRepositorys(self.parent.db,mlist[0],mlist[1],
##                                   self.build_tree)
