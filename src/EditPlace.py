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
import RelImage
import Sources

_ = intl.gettext

_DEFHTTP = "http://gramps.sourceforge.net"

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_INDEX  = "i"
_PLACE  = "p"

class EditPlace:

    def __init__(self,place,db,func):
        self.place = place
        self.db = db
        self.callback = func
        self.path = db.getSavePath()
        self.not_loaded = 1
        self.sref = SourceRef(place.getSourceRef())

        self.selectedIcon = -1
        self.currentImages = []
        self.top_window = libglade.GladeXML(const.placesFile,"placeEditor")
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
        self.web_description = self.top_window.get_widget("url_des")
        self.source_field = self.top_window.get_widget("source_field")
        
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
        if self.sref.getBase():
            self.source_field.set_text(self.sref.getBase().getTitle())
        else:
            self.source_field.set_text("")

        self.note.set_point(0)
        self.note.insert_defaults(place.getNote())
        self.note.set_word_wrap(1)

        self.photo_list = self.top_window.get_widget("photolist")

        self.top_window.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_source_clicked" : on_source_clicked,
            "on_photolist_select_icon" : on_photo_select_icon,
            "on_photolist_button_press_event" : on_photolist_button_press_event,
            "on_switch_page" : on_switch_page,
            "on_addphoto_clicked" : on_add_photo_clicked,
            "on_deletephoto_clicked" : on_delete_photo_clicked,
            "on_add_url_clicked" : on_add_url_clicked,
            "on_delete_url_clicked" : on_delete_url_clicked,
            "on_update_url_clicked" : on_update_url_clicked,
            "on_add_loc_clicked" : on_add_loc_clicked,
            "on_delete_loc_clicked" : on_delete_loc_clicked,
            "on_update_loc_clicked" : on_update_loc_clicked,
            "on_web_list_select_row" : on_web_list_select_row,
            "on_loc_list_select_row" : on_loc_list_select_row,
            "on_apply_clicked" : on_place_apply_clicked
            })

        self.top = self.top_window.get_widget("placeEditor")
        self.top.set_data(_PLACE,self)

        if self.place.getId() == "":
            self.top_window.get_widget("add_photo").set_sensitive(0)
            self.top_window.get_widget("delete_photo").set_sensitive(0)

        self.web_list.set_data(_PLACE,self)
        self.web_list.set_data(_INDEX,-1)
        self.redraw_url_list()

        self.loc_list.set_data(_PLACE,self)
        self.loc_list.set_data(_INDEX,-1)
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
            self.web_url.set_sensitive(1)
        else:
            self.web_url.set_sensitive(0)
            self.web_url.set_label("")
            self.web_url.set_url(_DEFHTTP)
            self.web_description.set_text("")

    #---------------------------------------------------------------------
    #
    # redraw_location_list
    #
    #---------------------------------------------------------------------
    def redraw_location_list(self):
        utils.redraw_list(self.llist,self.loc_list,disp_loc)

    #-------------------------------------------------------------------------
    #
    # add_thumbnail - Scale the image and add it to the IconList. 
    #
    #-------------------------------------------------------------------------
    def add_thumbnail(self,photo):
        src = os.path.basename(photo.getPath())
        if photo.getPrivate():
            thumb = "%s%s.thumb%s%s" % (self.path,os.sep,os.sep,src)
        else:
            thumb = "%s%s.thumb%s%s.jpg" % (self.path,os.sep,os.sep,os.path.basename(src))
        RelImage.check_thumb(src,thumb,const.thumbScale)
        self.photo_list.append(thumb,photo.getDescription())
        
    #-------------------------------------------------------------------------
    #
    # load_images - clears the currentImages list to free up any cached 
    # Imlibs.  Then add each photo in the place's list of photos to the 
    # photolist window.
    #
    #-------------------------------------------------------------------------
    def load_images(self):
        self.photo_list.freeze()
        self.photo_list.clear()
        for photo in self.place.getPhotoList():
            self.add_thumbnail(photo)
        self.photo_list.thaw()

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

    if not edit.place.getSourceRef().are_equal(edit.sref):
        edit.place.setSourceRef(edit.sref)
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
        src.load_images()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_photo_select_icon(obj,iconNumber,event):
    obj.get_data(_PLACE).selectedIcon = iconNumber

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_photo_clicked(obj):
    epo = obj.get_data(_PLACE)
    print epo
    icon = epo.selectedIcon

    if icon != -1:
        epo.photo_list.remove(icon)
        del epo.place.getPhotoList()[icon]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_photo_clicked(obj):

    edit_place = obj.get_data(_PLACE)
    image_select = libglade.GladeXML(const.imageselFile,"imageSelect")
    edit_place.isel = image_select

    image_select.signal_autoconnect({
        "on_savephoto_clicked" : on_savephoto_clicked,
        "on_name_changed" : on_name_changed,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    edit_place.fname = image_select.get_widget("fname")
    edit_place.add_image = image_select.get_widget("image")
    edit_place.external = image_select.get_widget("private")
    image_select.get_widget("imageSelect").set_data(_PLACE,edit_place)
    image_select.get_widget("imageSelect").show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_savephoto_clicked(obj):
    edit_place_obj = obj.get_data(_PLACE)
    image_select = edit_place_obj.isel
    
    filename = image_select.get_widget("photosel").get_full_path(0)
    description = image_select.get_widget("photoDescription").get_text()

    if os.path.exists(filename) == 0:
        return

    prefix = "p%s" % edit_place_obj.place.getId()
    if edit_place_obj.external.get_active() == 1:
        if os.path.isfile(filename):
            name = filename
        else:
            return
    else:
        name = RelImage.import_photo(filename,edit_place_obj.path,prefix)
        if name == None:
            return
        
    photo = Photo()
    photo.setPath(name)
    photo.setDescription(description)
    
    edit_place_obj.place.addPhoto(photo)
    edit_place_obj.add_thumbnail(photo)

    utils.modified()
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_photolist_button_press_event(obj,event):

    myobj = obj.get_data(_PLACE)
    icon = myobj.selectedIcon
    if icon == -1:
        return
    
    if event.button == 3:
        photo = myobj.place.getPhotoList()[icon]
        menu = GtkMenu()
        item = GtkTearoffMenuItem()
        item.show()
        menu.append(item)
        utils.add_menuitem(menu,_("View Image"),myobj,on_view_photo)
        utils.add_menuitem(menu,_("Edit Image"),myobj,on_edit_photo)
        utils.add_menuitem(menu,_("Edit Description"),myobj,
                           on_change_description)
        if photo.getPrivate() == 0:
            utils.add_menuitem(menu,_("Convert to private copy"),myobj,
                         on_convert_to_private)
        menu.popup(None,None,None,0,0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_convert_to_private(obj):
    edit_place_obj = obj.get_data("m")
    photo = edit_place_obj.place.getPhotoList()[edit_place_obj.selectedIcon]

    prefix = "p%s" % edit_place_obj.place.getId()
    name = RelImage.import_photo(photo.getPath(),edit_place_obj.path,prefix)

    photo.setPath(name)
    photo.setPrivate(1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_view_photo(obj):
    myobj = obj.get_data("m")
    photo = myobj.place.getPhotoList()[myobj.selectedIcon]

    utils.view_photo(photo)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_photo(obj):
    myobj = obj.get_data("m")
    photo = myobj.place.getPhotoList()[myobj.selectedIcon]
    if os.fork() == 0:
        os.execvp(const.editor,[const.editor, photo.getPath()])

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_change_description(obj):
    myobj = obj.get_data("m")
    photo = myobj.place.getPhotoList()[myobj.selectedIcon]
    window = libglade.GladeXML(const.imageselFile,"dialog1")

    text = window.get_widget("text")
    text.set_text(photo.getDescription())

    image2 = RelImage.scale_image(photo.getPath(),200.0)
    window.get_widget("photo").load_imlib(image2)
    window.get_widget("dialog1").set_data("p",photo)
    window.get_widget("dialog1").set_data("t",text)
    window.get_widget("dialog1").set_data("m",obj.get_data("m"))
    window.signal_autoconnect({
        "on_cancel_clicked" : utils.destroy_passed_object,
        "on_ok_clicked" : on_ok_clicked,
        "on_apply_clicked" : on_apply_clicked
        })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    on_apply_clicked(obj)
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_apply_clicked(obj):
    photo = obj.get_data("p")
    text = obj.get_data("t").get_text()
    if text != photo.getDescription():
        photo.setDescription(text)
        edit_window = obj.get_data("m")
        edit_window.load_images()
        utils.modified()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_name_changed(obj):
    edit_person = obj.get_data(_PLACE)
    file = edit_person.fname.get_text()
    if os.path.isfile(file):
        image = RelImage.scale_image(file,const.thumbScale)
        edit_person.add_image.load_imlib(image)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_url_clicked(obj):
    row = obj.get_data(_INDEX)
    if row >= 0:
        UrlEditor(obj.get_data(_PLACE),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_loc_clicked(obj):
    row = obj.get_data(_INDEX)
    if row >= 0:
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
    UrlEditor(obj.get_data(_PLACE),None)

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
    Sources.SourceEditor(epo.sref,epo.db,epo.source_field)

#-------------------------------------------------------------------------
#
# UrlEditor class
#
#-------------------------------------------------------------------------
class UrlEditor:

    def __init__(self,parent,url):
        self.parent = parent
        self.url = url
        self.top = libglade.GladeXML(const.editPersonFile, "url_edit")
        self.window = self.top.get_widget("url_edit")
        self.des  = self.top.get_widget("url_des")
        self.addr = self.top.get_widget("url_addr")
        self.priv = self.top.get_widget("priv")

        if parent.place:
            name = _("Internet Address Editor for %s") % parent.place.get_title()
        else:
            name = _("Internet Address Editor")
            
        self.top.get_widget("urlTitle").set_text(name) 

        if url != None:
            self.des.set_text(url.get_description())
            self.addr.set_text(url.get_path())
            self.priv.set_active(url.getPrivacy())

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_url_edit_ok_clicked" : on_url_edit_ok_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_url_edit_ok_clicked(obj):
    ee = obj.get_data("o")
    url = ee.url

    des = ee.des.get_text()
    addr = ee.addr.get_text()
    priv = ee.priv.get_active()

    if url == None:
        url = Url()
        ee.parent.ulist.append(url)
        
    if update_url(url,des,addr,priv):
        ee.parent.lists_changed = 1
        
    ee.parent.redraw_url_list()
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
# on_web_list_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_web_list_select_row(obj,row,b,c):
    obj.set_data(_INDEX,row)

    epo = obj.get_data(_PLACE)
    url = obj.get_row_data(row)

    if url == None:
        epo.web_url.set_label("")
        epo.web_url.set_url(_DEFHTTP)
        epo.web_url.set_sensitive(0)
        epo.web_description.set_text("")
    else:
        path = url.get_path()
        if path == "":
            path = _DEFHTTP
        epo.web_url.set_label(path)
        epo.web_url.set_url(path)
        epo.web_url.set_sensitive(1)
        epo.web_description.set_text(url.get_description())

#-------------------------------------------------------------------------
#
# on_loclist_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_loc_list_select_row(obj,row,b,c):
    obj.set_data(_INDEX,row)

    epo = obj.get_data(_PLACE)
    loc = obj.get_row_data(row)

    epo.loc_city.set_text(loc.get_city())
    epo.loc_county.set_text(loc.get_county())
    epo.loc_state.set_text(loc.get_state())
    epo.loc_country.set_text(loc.get_country())

#-------------------------------------------------------------------------
#
# update_url
# 
# Updates the specified event with the specified date.  Compares against
# the previous value, so the that modified flag is not set if nothing has
# actually changed.
#
#-------------------------------------------------------------------------
def update_url(url,des,addr,priv):
    changed = 0
        
    if url.get_path() != addr:
        url.set_path(addr)
        changed = 1
        
    if url.get_description() != des:
        url.set_description(des)
        changed = 1

    if url.getPrivacy() != priv:
        url.setPrivacy(priv)
        changed = 1

    return changed

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

