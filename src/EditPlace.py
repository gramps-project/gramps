#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import string

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *

import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import intl
import const
import utils
from RelLib import *
import Sources
import ImageSelect

_ = intl.gettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_PLACE  = "p"

class EditPlace:

    def __init__(self,place,db,func):
        self.place = place
        self.db = db
        self.callback = func
        self.path = db.getSavePath()
        self.not_loaded = 1
        self.lists_changed = 0
        if place:
            self.srcreflist = place.getSourceRefList()
        else:
            self.srcreflist = []
            
        self.top_window = libglade.GladeXML(const.placesFile,"placeEditor")
        idval = "p%s" % place.getId()
        plwidget = self.top_window.get_widget("photolist")
        self.gallery = ImageSelect.Gallery(place, self.path, idval, plwidget, db)
        self.title = self.top_window.get_widget("place_title")
        self.city = self.top_window.get_widget("city")
        self.county = self.top_window.get_widget("county")
        self.state = self.top_window.get_widget("state")
        self.country = self.top_window.get_widget("country")
        self.longitude = self.top_window.get_widget("longitude")
        self.latitude = self.top_window.get_widget("latitude")
        self.note = self.top_window.get_widget("place_note")

        self.web_list = self.top_window.get_widget("web_list")
        self.web_url = self.top_window.get_widget("web_url")
        self.web_go = self.top_window.get_widget("web_go")
        self.web_description = self.top_window.get_widget("url_des")
        
        self.loc_list = self.top_window.get_widget("loc_list")
        self.loc_city = self.top_window.get_widget("loc_city")
        self.loc_county = self.top_window.get_widget("loc_county")
        self.loc_state  = self.top_window.get_widget("loc_state")
        self.loc_country = self.top_window.get_widget("loc_country")

        self.lists_changed = 0
        self.ulist = place.getUrlList()[:]
        self.llist = place.get_alternate_locations()[:]

        self.title.set_text(place.get_title())
        mloc = place.get_main_location()
        self.city.set_text(mloc.get_city())
        self.county.set_text(mloc.get_county())
        self.state.set_text(mloc.get_state())
        self.country.set_text(mloc.get_country())
        self.longitude.set_text(place.get_longitude())
        self.latitude.set_text(place.get_latitude())

        self.note.set_point(0)
        self.note.insert_defaults(place.getNote())
        self.note.set_word_wrap(1)

        self.top_window.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_source_clicked" : self.on_source_clicked,
            "on_photolist_select_icon" : self.gallery.on_photo_select_icon,
            "on_photolist_button_press_event" : self.gallery.on_photolist_button_press_event,
            "on_switch_page" : self.on_switch_page,
            "on_addphoto_clicked" : self.gallery.on_add_photo_clicked,
            "on_deletephoto_clicked" : self.gallery.on_delete_photo_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_add_url_clicked" : self.on_add_url_clicked,
            "on_delete_url_clicked" : self.on_delete_url_clicked,
            "on_update_url_clicked" : self.on_update_url_clicked,
            "on_add_loc_clicked" : self.on_add_loc_clicked,
            "on_delete_loc_clicked" : self.on_delete_loc_clicked,
            "on_update_loc_clicked" : self.on_update_loc_clicked,
            "on_web_list_select_row" : self.on_web_list_select_row,
            "on_web_go_clicked": self.on_web_go_clicked,
            "on_loc_list_select_row" : self.on_loc_list_select_row,
            "on_apply_clicked" : self.on_place_apply_clicked
            })

        self.top = self.top_window.get_widget("placeEditor")

        # Typing CR selects OK button
        self.top.editable_enters(self.title);
        self.top.editable_enters(self.city);
        self.top.editable_enters(self.county);
        self.top.editable_enters(self.state);
        self.top.editable_enters(self.country);
        self.top.editable_enters(self.longitude);
        self.top.editable_enters(self.latitude);
        
        if self.place.getId() == "":
            self.top_window.get_widget("add_photo").set_sensitive(0)
            self.top_window.get_widget("delete_photo").set_sensitive(0)

        self.redraw_url_list()
        self.redraw_location_list()

    def update_lists(self):
        self.place.setUrlList(self.ulist)
        self.place.set_alternate_locations(self.llist)
        if self.lists_changed:
            utils.modified()
            
    def redraw_url_list(self):
        length = utils.redraw_list(self.ulist,self.web_list,disp_url)
        if length > 0:
            self.web_go.set_sensitive(1)
        else:
            self.web_go.set_sensitive(0)
            self.web_url.set_text("")
            self.web_description.set_text("")

    def redraw_location_list(self):
        utils.redraw_list(self.llist,self.loc_list,disp_loc)


    def on_web_go_clicked(self,obj):
        import gnome.url

        text = obj.get()
        if text != "":
            gnome.url.show(text)

    def on_place_apply_clicked(self,obj):

        title = self.title.get_text()
        city = self.city.get_text()
        county = self.county.get_text()
        state = self.state.get_text()
        country = self.country.get_text()
        longitude = self.longitude.get_text()
        latitude = self.latitude.get_text()
        note = self.note.get_chars(0,-1)

        mloc = self.place.get_main_location()
        if city != mloc.get_city():
            mloc.set_city(city)
            utils.modified()

        if self.lists_changed:
            self.place.setSourceRefList(self.srcreflist)
            utils.modified()

        if state != mloc.get_state():
            mloc.set_state(state)
            utils.modified()

        if county != mloc.get_county():
            mloc.set_county(county)
            utils.modified()

        if country != mloc.get_country():
            mloc.set_country(country)
            utils.modified()

        if title != self.place.get_title():
            self.place.set_title(title)
            utils.modified()
        
        if longitude != self.place.get_longitude():
            self.place.set_longitude(longitude)
            utils.modified()

        if latitude != self.place.get_latitude():
            self.place.set_latitude(latitude)
            utils.modified()
        
        if note != self.place.getNote():
            self.place.setNote(note)
            utils.modified()

        self.update_lists()

        utils.destroy_passed_object(self.top)
        self.callback(self.place)

    def on_switch_page(self,obj,a,page):
        if page == 3 and self.not_loaded:
            self.not_loaded = 0
            self.gallery.load_images()

    def on_update_url_clicked(self,obj):
        import UrlEdit
        if len(obj.selection) > 0:
            row = obj.selection[0]
            if self.place:
                name = _("Internet Address Editor for %s") % self.place.get_title()
            else:
                name = _("Internet Address Editor")
            UrlEdit.UrlEditor(self,name,obj.get_row_data(row))

    def on_update_loc_clicked(self,obj):
        import LocEdit
        if len(obj.selection) > 0:
            row = obj.selection[0]
            LocEdit.LocationEditor(self,obj.get_row_data(row))

    def on_delete_url_clicked(self,obj):
        if utils.delete_selected(obj,self.ulist):
            self.lists_changed = 1
            self.redraw_url_list()

    def on_delete_loc_clicked(self,obj):
        if utils.delete_selected(obj,self.llist):
            self.lists_changed = 1
            self.redraw_location_list()

    def on_add_url_clicked(self,obj):
        import UrlEdit
        if self.place:
            name = _("Internet Address Editor for %s") % self.place.get_title()
        else:
            name = _("Internet Address Editor")
        UrlEdit.UrlEditor(self,name,None)

    def on_add_loc_clicked(self,obj):
        import LocEdit
        LocEdit.LocationEditor(self,None)

    def on_source_clicked(self,obj):
        Sources.SourceSelector(self.srcreflist,self,src_changed)

    def on_web_list_select_row(self,obj,row,b,c):
        url = obj.get_row_data(row)
        if url == None:
            self.web_url.set_text("")
            self.web_go.set_sensitive(0)
            self.web_description.set_text("")
        else:
            path = url.get_path()
            self.web_url.set_text(path)
            self.web_go.set_sensitive(1)
            self.web_description.set_text(url.get_description())

    def on_loc_list_select_row(self,obj,row,b,c):
        loc = obj.get_row_data(row)

        self.loc_city.set_text(loc.get_city())
        self.loc_county.set_text(loc.get_county())
        self.loc_state.set_text(loc.get_state())
        self.loc_country.set_text(loc.get_country())

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_url(url):
    return [url.get_path(),url.get_description()]

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_loc(loc):
    return [loc.get_city(),loc.get_county(),loc.get_state(),loc.get_country()]

def src_changed(parent):
    parent.lists_changed = 1
