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
            "on_source_clicked" : on_source_clicked,
            "on_photolist_select_icon" : self.gallery.on_photo_select_icon,
            "on_photolist_button_press_event" : self.gallery.on_photolist_button_press_event,
            "on_switch_page" : on_switch_page,
            "on_addphoto_clicked" : self.gallery.on_add_photo_clicked,
            "on_deletephoto_clicked" : self.gallery.on_delete_photo_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_add_url_clicked" : on_add_url_clicked,
            "on_delete_url_clicked" : on_delete_url_clicked,
            "on_update_url_clicked" : on_update_url_clicked,
            "on_add_loc_clicked" : on_add_loc_clicked,
            "on_delete_loc_clicked" : on_delete_loc_clicked,
            "on_update_loc_clicked" : on_update_loc_clicked,
            "on_web_list_select_row" : on_web_list_select_row,
            "on_web_go_clicked": on_web_go_clicked,
            "on_loc_list_select_row" : on_loc_list_select_row,
            "on_apply_clicked" : on_place_apply_clicked
            })

        self.top = self.top_window.get_widget("placeEditor")
        self.top.set_data(_PLACE,self)

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

        self.web_list.set_data(_PLACE,self)
        self.redraw_url_list()

        self.loc_list.set_data(_PLACE,self)
        self.redraw_location_list()

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def update_lists(self):
        self.place.setUrlList(self.ulist)
        self.place.set_alternate_locations(self.llist)
        if self.lists_changed:
            utils.modified()
            
    #---------------------------------------------------------------------
    #
    # redraw_url_list - redraws the altername name list for the person
    #
    #---------------------------------------------------------------------
    def redraw_url_list(self):
        length = utils.redraw_list(self.ulist,self.web_list,disp_url)
        if length > 0:
            self.web_go.set_sensitive(1)
        else:
            self.web_go.set_sensitive(0)
            self.web_url.set_text("")
            self.web_description.set_text("")

    #---------------------------------------------------------------------
    #
    # redraw_location_list
    #
    #---------------------------------------------------------------------
    def redraw_location_list(self):
        utils.redraw_list(self.llist,self.loc_list,disp_loc)


def on_web_go_clicked(obj):
    import gnome.url

    text = obj.get()
    if text != "":
        gnome.url.show(text)

#-----------------------------------------------------------------------------
#
#
#
#-----------------------------------------------------------------------------
def on_place_apply_clicked(obj):

    edit = obj.get_data(_PLACE)
    title = edit.title.get_text()
    city = edit.city.get_text()
    county = edit.county.get_text()
    state = edit.state.get_text()
    country = edit.country.get_text()
    longitude = edit.longitude.get_text()
    latitude = edit.latitude.get_text()
    note = edit.note.get_chars(0,-1)

    mloc = edit.place.get_main_location()
    if city != mloc.get_city():
        mloc.set_city(city)
        utils.modified()

    if edit.lists_changed:
        edit.place.setSourceRefList(edit.srcreflist)
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

    if title != edit.place.get_title():
        edit.place.set_title(title)
        utils.modified()
        
    if longitude != edit.place.get_longitude():
        edit.place.set_longitude(longitude)
        utils.modified()

    if latitude != edit.place.get_latitude():
        edit.place.set_latitude(latitude)
        utils.modified()
        
    if note != edit.place.getNote():
        edit.place.setNote(note)
        utils.modified()

    edit.update_lists()

    utils.destroy_passed_object(edit.top)
    edit.callback(edit.place)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_switch_page(obj,a,page):
    src = obj.get_data(_PLACE)
    if page == 3 and src.not_loaded:
        src.not_loaded = 0
        src.gallery.load_images()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_url_clicked(obj):
    import UrlEdit
    if len(obj.selection) > 0:
        row = obj.selection[0]
        mobj = obj.get_data(_PLACE)
        if mobj.place:
            name = _("Internet Address Editor for %s") % mobj.place.get_title()
        else:
            name = _("Internet Address Editor")
        UrlEdit.UrlEditor(mobj,name,obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_loc_clicked(obj):
    if len(obj.selection) > 0:
        row = obj.selection[0]
        LocationEditor(obj.get_data(_PLACE),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_url_clicked(obj):
    epo = obj.get_data(_PLACE)
    if utils.delete_selected(obj,epo.ulist):
        epo.lists_changed = 1
        epo.redraw_url_list()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_loc_clicked(obj):
    epo = obj.get_data(_PLACE)
    if utils.delete_selected(obj,epo.llist):
        epo.lists_changed = 1
        epo.redraw_location_list()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_url_clicked(obj):
    import UrlEdit
    mobj = obj.get_data(_PLACE)
    if mobj.place:
        name = _("Internet Address Editor for %s") % mobj.place.get_title()
    else:
        name = _("Internet Address Editor")
    UrlEdit.UrlEditor(mobj,name,None)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_loc_clicked(obj):
    LocationEditor(obj.get_data(_PLACE),None)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_source_clicked(obj):
    epo = obj.get_data(_PLACE)
    Sources.SourceSelector(epo.srcreflist,epo,src_changed)

def src_changed(parent):
    parent.lists_changed = 1

#-------------------------------------------------------------------------
#
# on_web_list_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_web_list_select_row(obj,row,b,c):

    epo = obj.get_data(_PLACE)
    url = obj.get_row_data(row)

    if url == None:
        epo.web_url.set_text("")
        epo.web_go.set_sensitive(0)
        epo.web_description.set_text("")
    else:
        path = url.get_path()
        epo.web_url.set_text(path)
        epo.web_go.set_sensitive(1)
        epo.web_description.set_text(url.get_description())

#-------------------------------------------------------------------------
#
# on_loclist_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_loc_list_select_row(obj,row,b,c):

    epo = obj.get_data(_PLACE)
    loc = obj.get_row_data(row)

    epo.loc_city.set_text(loc.get_city())
    epo.loc_county.set_text(loc.get_county())
    epo.loc_state.set_text(loc.get_state())
    epo.loc_country.set_text(loc.get_country())

#-------------------------------------------------------------------------
#
# update_location
# 
# Updates the specified event with the specified date.  Compares against
# the previous value, so the that modified flag is not set if nothing has
# actually changed.
#
#-------------------------------------------------------------------------
def update_location(loc,city,county,state,country):
    changed = 0
        
    if loc.get_city() != city:
        loc.set_city(city)
        changed = 1

    if loc.get_county() != county:
        loc.set_county(county)
        changed = 1

    if loc.get_state() != state:
        loc.set_state(state)
        changed = 1

    if loc.get_country() != country:
        loc.set_country(country)
        changed = 1
    return changed

#-------------------------------------------------------------------------
#
# LocationEditor class
#
#-------------------------------------------------------------------------
class LocationEditor:

    def __init__(self,parent,location):
        self.parent = parent
        self.location = location
        self.top = libglade.GladeXML(const.dialogFile, "loc_edit")
        self.window = self.top.get_widget("loc_edit")
        self.city   = self.top.get_widget("city")
        self.state  = self.top.get_widget("state")
        self.county = self.top.get_widget("county")
        self.country = self.top.get_widget("country")

        # Typing CR selects OK button
        self.window.editable_enters(self.city);
        self.window.editable_enters(self.county);
        self.window.editable_enters(self.state);
        self.window.editable_enters(self.country);

        if parent.place:
            name = _("Location Editor for %s") % parent.place.get_title()
        else:
            name = _("Location Editor")
            
        self.top.get_widget("locationTitle").set_text(name) 

        if location != None:
            self.city.set_text(location.get_city())
            self.county.set_text(location.get_county())
            self.country.set_text(location.get_country())
            self.state.set_text(location.get_state())

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_loc_edit_ok_clicked" : on_location_edit_ok_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_location_edit_ok_clicked(obj):
    ee = obj.get_data("o")
    loc = ee.location

    city = ee.city.get_text()
    county = ee.county.get_text()
    country = ee.country.get_text()
    state = ee.state.get_text()

    if loc == None:
        loc = Location()
        ee.parent.llist.append(loc)
        
    if update_location(loc,city,county,state,country):
        ee.parent.lists_changed = 1
        
    ee.parent.redraw_location_list()
    utils.destroy_passed_object(obj)

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

