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

"""
Handles the place view for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import GDK
import gnome.ui

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *
from QuestionDialog import QuestionDialog

import EditPlace
import Utils
import GrampsCfg
import Sorter

from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# PlaceView class
#
#-------------------------------------------------------------------------
class PlaceView:
    
    def __init__(self,db,glade,update):
        self.db = db
        self.glade = glade
        self.place_list    = glade.get_widget("place_list")
        self.update_display= update

        for i in range(7,13):
            self.place_list.set_column_visibility(i,0)

        self.place_list.connect('button-press-event',self.on_button_press_event)
        self.place_list.connect('select-row',self.select_row)
        self.active = None

        plist_map = [(7,  glade.get_widget("place_arrow")),
                     (1,  glade.get_widget("place_id_arrow")),
                     (8,  glade.get_widget("parish_arrow")),
                     (9,  glade.get_widget("city_arrow")),
                     (10, glade.get_widget("county_arrow")),
                     (11, glade.get_widget("state_arrow")),
                     (12, glade.get_widget("country_arrow"))]

        self.place_sort = Sorter.Sorter(self.place_list,plist_map,'place')


    def change_db(self,db):
        self.db = db

    def load_places(self,id=None):
        """Rebuilds the entire place view. This can be very time consuming
        on large databases, and should only be called when absolutely
        necessary"""

        self.place_list.freeze()
        self.place_list.clear()
        self.place_list.set_column_visibility(1,GrampsCfg.id_visible)

        if len(self.place_list.selection) == 0:
            current_row = 0
        else:
            current_row = self.place_list.selection[0]

        index = 0
        for key in self.db.getPlaceKeys():
            self.place_list.append(self.db.getPlaceDisplay(key))
            self.place_list.set_row_data(index,key)
            index = index + 1

        self.place_sort.sort_list()

        if id:
            current_row = self.place_list.find_row_from_data(id)

        if index > 0:
            self.place_list.select_row(current_row,0)
            self.place_list.moveto(current_row)
            id = self.place_list.get_row_data(current_row)
            self.active = self.db.getPlace(id)
        else:
            self.active = None

        self.place_list.thaw()
        
    def select_row(self,obj,row,b,c):
        if row == obj.selection[0]:
            id = self.place_list.get_row_data(row)
            self.active = self.db.getPlace(id)
            
    def merge(self):
        if len(self.place_list.selection) != 2:
            msg = _("Exactly two places must be selected to perform a merge")
            gnome.ui.GnomeErrorDialog(msg)
        else:
            import MergeData
            p1 = self.place_list.get_row_data(self.place_list.selection[0])
            p2 = self.place_list.get_row_data(self.place_list.selection[1])
            p1 = self.db.getPlace(p1)
            p2 = self.db.getPlace(p2)
            MergeData.MergePlaces(self.db,p1,p2,self.load_places)

    def on_button_press_event(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            if self.active:
                EditPlace.EditPlace(self,self.active,
                                    self.update_display_after_edit)

    def insert_place(self,place):
        self.place_list.append(place.getDisplayInfo())
        self.place_list.set_row_data(self.place_list.rows-1,place.getId())
        
    def new_place_after_edit(self,place):
        self.place_list.freeze()
        self.db.addPlace(place)
        self.insert_place(place)
        self.place_sort.sort_list()
        self.place_list.thaw()

    def update_display_after_edit(self,place):
        self.place_list.freeze()
        val = place.getId()
        for index in range(0,self.place_list.rows):
            if self.place_list.get_row_data(index) == val:
                break
        else:
            index = -1

        self.place_list.remove(index)
        self.insert_place(place)
        self.place_sort.sort_list()
        self.place_list.thaw()

    def on_add_place_clicked(self,obj):
        EditPlace.EditPlace(self,Place(),self.new_place_after_edit)

    def moveto(self,row):
        self.place_list.unselect_all()
        self.place_list.select_row(row,0)
        self.place_list.moveto(row)
        
    def on_delete_clicked(self,obj):
        if len(obj.selection) == 0:
            return
        elif len(obj.selection) > 1:
            msg = _("Currently, you can only delete one place at a time")
            gnome.ui.GnomeErrorDialog(msg)
            return
        else:
            index = obj.selection[0]

        used = 0
        place = self.db.getPlace(obj.get_row_data(index))
        for key in self.db.getPersonKeys():
            p = self.db.getPerson(key)
            event_list = [p.getBirth(), p.getDeath()] + p.getEventList()
            if p.getLdsBaptism():
                event_list.append(p.getLdsBaptism())
            if p.getLdsEndowment():
                event_list.append(p.getLdsEndowment())
            if p.getLdsSeal():
                event_list.append(p.getLdsSeal())
            for event in event_list:
                if event.getPlace() == place:
                    used = 1

        for f in self.db.getFamilyMap().values():
            event_list = f.getEventList()
            if f.getLdsSeal():
                event_list.append(f.getLdsSeal())
            for event in event_list:
                if event.getPlace() == place:
                    used = 1

        if used == 1:
            ans = EditPlace.DeletePlaceQuery(place,self.db,self.update_display)
            QuestionDialog(_('Delete Place'),
                           _("This place is currently being used. Delete anyway?"),
                           _('Delete Place'),ans.query_response,
                           _('Keep Place'))
        else:
            obj.remove(index)
            self.db.removePlace(place.getId())
            Utils.modified()

    def on_edit_place_clicked(self,obj):
        """Display the selected places in the EditPlace display"""
        if len(obj.selection) > 5:
            msg = _("You requested too many places to edit at the same time")
            gnome.ui.GnomeErrorDialog(msg)
        else:
            for p in obj.selection:
                place = self.db.getPlace(obj.get_row_data(p))
                EditPlace.EditPlace(self,place,
                                    self.update_display_after_edit)




