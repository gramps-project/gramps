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

import GTK
import GDK
import gnome.ui
import string

from RelLib import *
import EditPlace
import utils
import Config

from intl import gettext
_ = gettext

class PlaceView:
    def __init__(self,db,glade,update):
        self.db = db
        self.glade = glade
        self.place_list    = glade.get_widget("place_list")
        self.place_arrow   = glade.get_widget("place_arrow")
        self.place_id_arrow= glade.get_widget("place_id_arrow")
        self.city_arrow    = glade.get_widget("city_arrow")
        self.parish_arrow  = glade.get_widget("parish_arrow")
        self.county_arrow  = glade.get_widget("county_arrow")
        self.state_arrow   = glade.get_widget("state_arrow")
        self.country_arrow = glade.get_widget("country_arrow")
        self.update_display= update

        self.sort_arrow = [ self.place_arrow, self.place_id_arrow,
                            self.parish_arrow, self.city_arrow,
                            self.county_arrow, self.state_arrow,
                            self.country_arrow ]

        self.place_list.set_column_visibility(7,0)
        self.place_list.set_column_visibility(8,0)
        self.place_list.set_column_visibility(9,0)
        self.place_list.set_column_visibility(10,0)
        self.place_list.set_column_visibility(11,0)
        self.place_list.set_column_visibility(12,0)
        self.place_list.connect('button-press-event',self.on_button_press_event)
        self.place_list.connect('select-row',self.select_row)
        self.active = None
        self.sort_map = [7,1,8,9,10,11,12]

        # Restore the previous sort column
        
        self.sort_col,self.sort_dir = Config.get_sort_cols("place",0,GTK.SORT_ASCENDING)
        self.set_arrow(self.sort_col)
        self.place_list.set_sort_column(self.sort_map[self.sort_col])
        self.place_list.set_sort_type(self.sort_dir)

    def load_places(self):
        if len(self.place_list.selection) == 0:
            current_row = 0
        else:
            current_row = self.place_list.selection[0]

        self.place_list.freeze()
        self.place_list.clear()

        self.place_list.set_column_visibility(1,Config.id_visible)
        
        index = 0
        places = self.db.getPlaceMap().values()

        u = string.upper
        for src in places:
            title = src.get_title()
            id = src.getId()
            mloc = src.get_main_location()
            city = mloc.get_city()
            county = mloc.get_county()
            state = mloc.get_state()
            parish = mloc.get_parish()
            country = mloc.get_country()
            self.place_list.append([title,id,parish,city,county,state,country,
                                    u(title), u(parish), u(city),
                                    u(county),u(state), u(country)])
            self.place_list.set_row_data(index,src)
            index = index + 1

        self.place_list.sort()

        if index > 0:
            self.place_list.select_row(current_row,0)
            self.place_list.moveto(current_row)
            self.active = self.place_list.get_row_data(current_row)
        else:
            self.active = None
            
        self.place_list.thaw()

    def select_row(self,obj,row,b,c):
        if row == obj.selection[0]:
            self.active = self.place_list.get_row_data(row)
            
    def merge(self):
        if len(self.place_list.selection) != 2:
            msg = _("Exactly two places must be selected to perform a merge")
            gnome.ui.GnomeErrorDialog(msg)
        else:
            import MergeData
            p1 = self.place_list.get_row_data(self.place_list.selection[0])
            p2 = self.place_list.get_row_data(self.place_list.selection[1])
            MergeData.MergePlaces(self.db,p1,p2,self.load_places)

    def on_button_press_event(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            if self.active:
                EditPlace.EditPlace(self.active,self.db,
                                    self.update_display_after_edit)

    def set_arrow(self,column):
        for a in self.sort_arrow:
            a.hide()

        a = self.sort_arrow[column]
        a.show()
        if self.sort_dir == GTK.SORT_ASCENDING:
            a.set(GTK.ARROW_DOWN,2)
        else:
            a.set(GTK.ARROW_UP,2)

    def on_click_column(self,obj,column):
        obj.freeze()
        if len(obj.selection):
            sel = obj.get_row_data(obj.selection[0])
        else:
            sel = None
        
        for a in self.sort_arrow:
            a.hide()
        if self.sort_col == column:
            if self.sort_direct == GTK.SORT_DESCENDING:
                self.sort_direct = GTK.SORT_ASCENDING
            else:
                self.sort_direct = GTK.SORT_DESCENDING
        else:
            self.sort_direct = GTK.SORT_ASCENDING
        self.sort_col = column
        self.set_arrow(column)
        self.place_list.set_sort_type(self.sort_direct)
        self.place_list.set_sort_column(self.sort_map[self.sort_col])
        Config.save_sort_cols("place",self.sort_col,self.sort_direct)

        self.place_list.sort()
        if sel:
            self.place_list.moveto(self.place_list.find_row_from_data(sel))
        obj.thaw()

    def new_place_after_edit(self,place):
        self.db.addPlace(place)
        self.update_display(0)

    def update_display_after_edit(self,place):
        self.update_display(0)

    def on_add_place_clicked(self,obj):
        EditPlace.EditPlace(Place(),self.db,self.new_place_after_edit)

    def on_delete_place_clicked(self,obj):
        if len(obj.selection) == 0:
            return
        elif len(obj.selection) > 1:
            msg = _("Currently, you can only delete one place at a time")
            gnome.ui.GnomeErrorDialog(msg)
            return
        else:
            index = obj.selection[0]

        used = 0
        place = obj.get_row_data(index)
        for p in self.db.getPersonMap().values():
            for event in [p.getBirth(), p.getDeath()] + p.getEventList():
                if event.getPlace() == place:
                    used = 1
        for f in self.db.getFamilyMap().values():
            for event in f.getEventList():
                if event.getPlace() == place:
                    used = 1

        if used == 1:
            ans = EditPlace.DeletePlaceQuery(place,self.db,self.update_display)
            msg = _("This place is currently being used. Delete anyway?")
            gnome.ui.GnomeQuestionDialog(msg,ans.query_response)
        else:
            map = self.db.getPlaceMap()
            del map[place.getId()]
            utils.modified()
            self.update_display(0)

    def on_edit_place_clicked(self,obj):
        """Display the selected places in the EditPlace display"""
        if len(obj.selection) > 5:
            msg = _("You requested too many places to edit at the same time")
            gnome.ui.GnomeErrorDialog(msg)
        else:
            for p in obj.selection:
                place = obj.get_row_data(p)
                EditPlace.EditPlace(place,self.db,self.update_display_after_edit)

