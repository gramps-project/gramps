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

from QuestionDialog import QuestionDialog, ErrorDialog
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# PlaceView class
#
#-------------------------------------------------------------------------
class PlaceView:
    
    def __init__(self,db,glade,update):
        self.db     = db
        self.glade  = glade
        self.list   = glade.get_widget("place_list")
        self.update = update

        self.column_headers = [
            (_('Place Name'),7,200), (_('ID'),1,50), (_('Church Parish'),8,75),
            (_('City'),9,75), (_('County'),10,75), (_('State'),11,75),
            (_('Country'),12,75), ('',7,0), ('',8,0), ('',9,0), ('',10,0),
            ('',11,0), ('',12,0)]

        self.active = None

        self.id2col = {}
        self.selection = self.list.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)
        colno = 0
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
            column.connect('clicked',self.on_click)
            self.list.append_column(column)

        self.click_col = None

        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)
        self.list.set_model(self.model)
        self.selection = self.list.get_selection()
        self.list.connect('button-press-event',self.button_press)
        self.list.connect('key-press-event',self.key_press)
        self.topWindow = self.glade.get_widget("gramps")

    def on_click(self,column):
        self.click_col = column

    def change_db(self,db):
        self.db = db

    def load_places(self,id=None):
        """Rebuilds the entire place view. This can be very time consuming
        on large databases, and should only be called when absolutely
        necessary"""

        del self.model
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)
        self.id2col = {}

        for key in self.db.sort_place_keys():
            val = self.db.get_place_display(key)
                
            iter = self.model.append()
            self.id2col[key] = iter
            self.model.set(iter,
                           0,   val[0], 1, val[1], 2,   val[2],  3,  val[3],
                           4,   val[4], 5, val[5], 6,   val[6],  7,  val[7],
                           8,   val[8], 9, val[9], 10, val[10], 11,  val[11],
                           12, val[12]
                           )
        self.list.set_model(self.model)
        if self.click_col:
            self.click_col.clicked()
        
    def goto(self,id):
        self.selection.unselect_all()
        iter = self.id2col[id]
        self.selection.select_iter(iter)
        itpath = self.model.get_path (iter)
        col = self.list.get_column (0)
        self.list.scroll_to_cell (itpath, col, gtk.TRUE, 0.5, 0)

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
            MergeData.MergePlaces(self.db,mlist[0],mlist[1],self.load_places)

    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            if mlist:
                EditPlace.EditPlace(self,mlist[0],self.update_display,self.topWindow)
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

    def new_place_after_edit(self,place):
        self.db.add_place(place)
        self.update(0)

    def update_display(self,place):
        if place:
            self.db.build_place_display(place.get_id())
        self.update(0)

    def on_add_place_clicked(self,obj):
        EditPlace.EditPlace(self,RelLib.Place(),self.new_place_after_edit)

    def on_delete_clicked(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for place in mlist:
            used = 0
            for key in self.db.get_person_keys():
                p = self.db.get_person(key)
                event_list = [p.get_birth(), p.get_death()] + p.get_event_list()[:]
                if p.get_lds_baptism():
                    event_list.append(p.get_lds_baptism())
                if p.get_lds_endowment():
                    event_list.append(p.get_lds_endowment())
                if p.get_lds_sealing():
                    event_list.append(p.get_lds_sealing())
                for event in event_list:
                    if event.get_place_id() == place:
                        used = 1

            for f in self.db.get_family_id_map().values():
                event_list = f.get_event_list()[:]
                if f.get_lds_sealing():
                    event_list.append(f.get_lds_sealing())
                for event in event_list:
                    if event.get_place_id() == place:
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
                self.db.remove_place(place.get_id())
                self.update(0)
                Utils.modified()

    def on_edit_clicked(self,obj):
        """Display the selected places in the EditPlace display"""
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for place in mlist:
            EditPlace.EditPlace(self, place, self.update_display)

    def blist(self,store,path,iter,list):
        id = self.db.get_place_id(store.get_value(iter,1))
        list.append(id)
