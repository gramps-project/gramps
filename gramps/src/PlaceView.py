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
import gtk
import string

from RelLib import *
import EditPlace
import utils
import intl

_ = intl.gettext

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

        self.place_arrows = [ self.place_arrow, self.place_id_arrow, self.parish_arrow,
                              self.city_arrow, self.county_arrow, self.state_arrow,
                              self.country_arrow ]

        self.sort_column = 0
        self.sort_direct = GTK.SORT_ASCENDING

        self.place_list.set_column_visibility(7,0)
        self.place_list.set_column_visibility(8,0)
        self.place_list.set_column_visibility(9,0)
        self.place_list.set_column_visibility(10,0)
        self.place_list.set_column_visibility(11,0)
        self.place_list.set_column_visibility(12,0)
        self.place_list.set_column_visibility(13,0)
        self.place_list.set_sort_column(self.sort_column+7)
        self.place_list.set_sort_type(self.sort_direct)

    def load_places(self):
        self.place_list.freeze()
        self.place_list.clear()

        if len(self.place_list.selection) == 0:
            current_row = 0
        else:
            current_row = self.place_list.selection[0]

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
                                    u(title), u(id), u(parish), u(city),
                                    u(county),u(state), u(country)])
            self.place_list.set_row_data(index,src)
            index = index + 1

        self.place_list.sort()

        if index > 0:
            self.place_list.select_row(current_row,0)
            self.place_list.moveto(current_row)

        self.place_list.thaw()

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
            if len(obj.selection) > 0:
                index = obj.selection[0]
                place = obj.get_row_data(index)
                EditPlace.EditPlace(place,self.db,self.update_display_after_edit)

    def on_click_column(self,obj,column):
        obj.freeze()
        if len(obj.selection):
            sel = obj.get_row_data(obj.selection[0])
        else:
            sel = None
        
        for a in self.place_arrows:
            a.hide()
        arrow = self.place_arrows[column]
        if self.sort_column == column:
            if self.sort_direct == GTK.SORT_DESCENDING:
                self.sort_direct = GTK.SORT_ASCENDING
                arrow.set(GTK.ARROW_DOWN,2)
            else:
                self.sort_direct = GTK.SORT_DESCENDING
                arrow.set(GTK.ARROW_UP,2)
        else:
            self.sort_direct = GTK.SORT_ASCENDING
            arrow.set(GTK.ARROW_DOWN,2)
        self.sort_column = column
        self.place_list.set_sort_type(self.sort_direct)
        self.place_list.set_sort_column(self.sort_column + 7)
        arrow.show()
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

