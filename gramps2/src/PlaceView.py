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

"""
Handles the place view for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import EditPlace
import Utils
import DisplayModels
import ColumnOrder
import const

from QuestionDialog import QuestionDialog, ErrorDialog
from gettext import gettext as _

column_names = [
    _('Place Name'),
    _('ID'),
    _('Church Parish'),
    _('City'),
    _('County'),
    _('State'),
    _('Country'),
    _('Longitude'),
    _('Latitude'),
    ]

#-------------------------------------------------------------------------
#
# PlaceView class
#
#-------------------------------------------------------------------------
class PlaceView:
    
    def __init__(self,parent,db,glade,update):
        self.parent = parent
        self.glade  = glade
        self.db     = db
        self.list   = glade.get_widget("place_list")
        self.list.connect('button-press-event',self.button_press)
        self.list.connect('key-press-event',self.key_press)
        self.selection = self.list.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)

        self.renderer = gtk.CellRendererText()

        if const.nosort_tree:
            self.model = DisplayModels.PlaceModel(self.db)
        else:
            self.model = gtk.TreeModelSort(DisplayModels.PlaceModel(self.db))
            
        self.list.set_model(self.model)
        self.topWindow = self.glade.get_widget("gramps")

        self.columns = []
        self.build_columns()

    def build_columns(self):
        for column in self.columns:
            self.list.remove_column(column)
            
        column = gtk.TreeViewColumn(_('Place Name'), self.renderer,text=0)
        column.set_resizable(gtk.TRUE)
        if not const.nosort_tree:
            column.set_clickable(gtk.TRUE)
            column.set_sort_column_id(0)

        column.set_min_width(225)
        self.list.append_column(column)
        self.columns = [column]

        index = 1
        for pair in self.parent.db.get_place_column_order():
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
            self.model = DisplayModels.PlaceModel(self.parent.db)
        else:
            self.model = gtk.TreeModelSort(DisplayModels.PlaceModel(self.parent.db))
        self.list.set_model(self.model)
        self.selection = self.list.get_selection()

    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            if mlist:
                EditPlace.EditPlace(self.parent,mlist[0],self.update_display,self.topWindow)
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
        """Builds the menu with editing operations on the place's list"""
        
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        if mlist:
            sel_sensitivity = 1
        else:
            sel_sensitivity = 0
        entries = [
            (gtk.STOCK_ADD, self.on_add_place_clicked,1),
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

    def on_add_place_clicked(self,obj):
        EditPlace.EditPlace(self.parent,RelLib.Place(),self.new_place_after_edit)

    def new_place_after_edit(self,place):
        self.db.add_place(place)

    def update_display(self,place):
        self.build_tree()

    def on_delete_clicked(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        
        trans = self.db.start_transaction()
        
        for place in mlist:
            used = 0
            for key in self.db.get_person_keys():
                p = self.db.try_to_find_person_from_id(key)
                event_list = []
                for e in [p.get_birth_id(),p.get_death_id()] + p.get_event_list():
                    event = self.db.find_event_from_id(e)
                    if event:
                        event_list.append(event)
                if p.get_lds_baptism():
                    event_list.append(p.get_lds_baptism())
                if p.get_lds_endowment():
                    event_list.append(p.get_lds_endowment())
                if p.get_lds_sealing():
                    event_list.append(p.get_lds_sealing())
                for event in event_list:
                    if event.get_place_id() == place.get_id():
                        print event.get_id()
                        used = 1

            for fid in self.db.get_family_keys():
                f = self.db.find_family_from_id(fid)
                event_list = []
                for e in f.get_event_list():
                    event = self.db.find_event_from_id(e)
                    if event:
                        event_list.append(event)
                if f.get_lds_sealing():
                    event_list.append(f.get_lds_sealing())
                for event in event_list:
                    if event.get_place_id() == place.get_id():
                        print event.get_id()
                        used = 1

            if used == 1:
                ans = EditPlace.DeletePlaceQuery(place,self.db,self.update_display)
                QuestionDialog(_('Delete %s?') %  place.get_title(),
                               _('This place is currently being used by at least one '
                                 'record in the database. Deleting it will remove it '
                                 'from the database and remove it from all records '
                                 'that reference it.'),
                               _('_Delete Place'),
                               ans.query_response)
            else:
                trans = self.db.start_transaction()
                self.db.remove_place(place.get_id(),trans)
                self.db.add_transaction(trans,_("Delete Place (%s)") % place.title())
                self.build_tree()

    def on_edit_clicked(self,obj):
        """Display the selected places in the EditPlace display"""
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for place in mlist:
            EditPlace.EditPlace(self.parent, place, self.update_display)

    def blist(self,store,path,iter,list):
        id = self.db.get_place_id(store.get_value(iter,1))
        list.append(id)

    def merge(self):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        
        if len(mlist) != 2:
            msg = _("Cannot merge places.")
            msg2 = _("Exactly two places must be selected to perform a merge. "
                "A second place can be selected by holding down the "
                "control key while clicking on the desired place.")
            ErrorDialog(msg,msg2)
        else:
            import MergeData
            MergeData.MergePlaces(self.db,mlist[0],mlist[1],self.build_tree)

