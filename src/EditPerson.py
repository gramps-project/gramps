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
import utils

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *
import gnome.mime
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import intl
import const
import utils
import Config
from RelLib import *
import RelImage
import Sources

_ = intl.gettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
INDEX      = "i"
EDITPERSON = "p"

#-------------------------------------------------------------------------
#
# EditPerson class
#
#-------------------------------------------------------------------------
class EditPerson:

    #---------------------------------------------------------------------
    #
    # __init__ - Creates an edit window.  Associates a person with the 
    # window.
    #
    #---------------------------------------------------------------------
    def __init__(self,person,db,callback):
        self.person = person
        self.db = db
        self.callback = callback
        self.path = db.getSavePath()
        self.not_loaded = 1
        self.events_changed = 0
        self.urls_changed = 0
        self.addr_changed = 0
        self.names_changed = 0
        self.attr_changed = 0
        
        self.top_window = libglade.GladeXML(const.editPersonFile, "editPerson")

        # widgets
        self.notes_field = self.get_widget("personNotes")
        self.event_name_field  = self.get_widget("eventName")
        self.event_place_field = self.get_widget("eventPlace")
        self.event_date_field  = self.get_widget("eventDate")
        self.event_descr_field = self.get_widget("eventDescription")
        self.event_details_field = self.get_widget("event_details")
        self.attr_details_field = self.get_widget("attr_details")
        self.name_details_field = self.get_widget("name_details")
        self.addr_details_field = self.get_widget("addr_details")
        self.photo_list = self.get_widget("photolist")
        self.attr_list = self.get_widget("attr_list")
        self.attr_type = self.get_widget("attr_type")
        self.attr_value = self.get_widget("attr_value")
        self.web_list = self.get_widget("web_list")
        self.web_url = self.get_widget("url_addr")
        self.web_description = self.get_widget("url_des")
        self.web_browse = self.get_widget("browse")
        self.address_label = self.get_widget("address_label")
        self.address_list = self.get_widget("address_list")
        self.address_start = self.get_widget("address_start")
        self.address_street = self.get_widget("street")
        self.address_city = self.get_widget("city")
        self.address_state = self.get_widget("state")
        self.address_country = self.get_widget("country")
        self.address_postal = self.get_widget("postal")
        self.event_list = self.get_widget("eventList")
        self.edit_person = self.get_widget("editPerson")
        self.name_list = self.get_widget("nameList")
        self.name_frame = self.get_widget("name_frame")
        self.alt_given_field = self.get_widget("alt_given")
        self.alt_last_field = self.get_widget("alt_last")
        self.alt_suffix_field = self.get_widget("alt_suffix")
        self.surname_field = self.get_widget("surname")
        self.suffix = self.get_widget("suffix")
        self.given = self.get_widget("givenName")
        self.nick = self.get_widget("nickname")
        self.title = self.get_widget("title")
        self.bdate  = self.get_widget("birthDate")
        self.bplace = self.get_widget("birthPlace")
        self.ddate  = self.get_widget("deathDate")
        self.dplace = self.get_widget("deathPlace")
        self.is_male = self.get_widget("genderMale")
        self.is_female = self.get_widget("genderFemale")
        self.addr_note = self.get_widget("addr_note")
        self.addr_source = self.get_widget("addr_source")
        self.attr_note = self.get_widget("attr_note")
        self.attr_source = self.get_widget("attr_source")
        self.name_note = self.get_widget("name_note")
        self.name_source = self.get_widget("name_source")

        self.elist = person.getEventList()[:]
        self.nlist = person.getAlternateNames()[:]
        self.alist = person.getAttributeList()[:]
        self.ulist = person.getUrlList()[:]
        self.plist = person.getAddressList()[:]

        self.selectedIcon = -1
        
        self.top_window.signal_autoconnect({
            "on_death_note_clicked" : on_death_note_clicked,
            "on_death_source_clicked" : on_death_source_clicked,
            "on_name_note_clicked" : on_name_note_clicked,
            "on_name_source_clicked" : on_name_source_clicked,
            "on_birth_note_clicked" : on_birth_note_clicked,
            "on_birth_source_clicked" : on_birth_source_clicked,
            "on_event_add_clicked" : on_event_add_clicked,
            "on_event_delete_clicked" : on_event_delete_clicked,
            "on_name_list_select_row" : on_name_list_select_row,
            "on_browse_clicked": on_browse_clicked,
            "on_web_list_select_row" : on_web_list_select_row,
            "on_attr_list_select_row" : on_attr_list_select_row,
            "on_address_list_select_row" : on_address_list_select_row,
            "on_aka_update_clicked" : on_aka_update_clicked,
            "on_aka_delete_clicked" : on_aka_delete_clicked,
            "on_add_aka_clicked" : on_add_aka_clicked,
            "on_update_url_clicked" : on_update_url_clicked,
            "on_delete_url_clicked" : on_delete_url_clicked,
            "on_add_attr_clicked" : on_add_attr_clicked,
            "on_update_attr_clicked" : on_update_attr_clicked,
            "on_delete_attr_clicked" : on_delete_attr_clicked,
            "on_add_url_clicked" : on_add_url_clicked,
            "on_update_address_clicked" : on_update_address_clicked,
            "on_delete_address_clicked" : on_delete_address_clicked,
            "on_add_address_clicked" : on_add_address_clicked,
            "on_event_update_clicked" : on_event_update_clicked,
            "on_event_select_row" : on_event_select_row,
            "on_editperson_switch_page" : on_switch_page,
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_makeprimary_clicked" : on_primary_photo_clicked,
            "on_photolist_select_icon" : on_photo_select_icon,
            "on_photolist_button_press_event" : on_photolist_button_press_event,
            "on_addphoto_clicked" : on_add_photo_clicked,
            "on_deletephoto_clicked" : on_delete_photo_clicked,
            "on_showsource_clicked" : on_showsource_clicked,
            "on_apply_person_clicked" : on_apply_person_clicked
            })

        if len(const.surnames) > 0:
            const.surnames.sort()
            self.get_widget("lastNameList").set_popdown_strings(const.surnames)

        name = person.getPrimaryName()
        birth = person.getBirth()
        death = person.getDeath()

        self.get_widget("gid").set_text(": %s" % person.getId())
        self.event_list.set_column_visibility(3,Config.show_detail)
        self.name_list.set_column_visibility(1,Config.show_detail)
        self.attr_list.set_column_visibility(2,Config.show_detail)
        self.address_list.set_column_visibility(2,Config.show_detail)
        if len(const.places) > 0:
            self.get_widget("dp_combo").set_popdown_strings(const.places)
            self.get_widget("bp_combo").set_popdown_strings(const.places)

        if Config.display_attr:
            self.get_widget("user_label").set_text(Config.attr_name)
            val = ""
            for attr in self.person.getAttributeList():
                if attr.getType() == const.save_pattr(Config.attr_name):
                    val = attr.getValue()
                    break
            self.get_widget("user_data").set_text(": %s" % val)
                
        else:
            self.get_widget("user_label").hide()
            self.get_widget("user_data").hide()

        # initial values
        self.get_widget("activepersonTitle").set_text(Config.nameof(person))
        self.suffix.set_text(name.getSuffix())

        self.surname_field.set_text(name.getSurname())
        self.given.set_text(name.getFirstName())

        if person.getGender() == Person.male:
            self.is_male.set_active(1)
        else:
            self.is_female.set_active(1)

        self.nick.set_text(person.getNickName())
        self.title.set_text(name.getTitle())
        self.bdate.set_text(birth.getDate())
        self.bplace.set_text(birth.getPlace())
        self.ddate.set_text(death.getDate())
        self.dplace.set_text(death.getPlace())
        
        # load photos into the photo window
        photo_list = person.getPhotoList()
        if len(photo_list) != 0:
            self.load_photo(photo_list[0].getPath())
    
        # set notes data
        self.notes_field.set_point(0)
        self.notes_field.insert_defaults(person.getNote())
        self.notes_field.set_word_wrap(1)

        # stored object data
        self.edit_person.set_data(EDITPERSON,self)
        self.event_list.set_data(EDITPERSON,self)
        self.event_list.set_data(INDEX,-1)
        self.name_list.set_data(EDITPERSON,self)
        self.name_list.set_data(INDEX,-1)
        self.web_list.set_data(EDITPERSON,self)
        self.web_list.set_data(INDEX,-1)
        self.attr_list.set_data(EDITPERSON,self)
        self.attr_list.set_data(INDEX,-1)
        self.address_list.set_data(EDITPERSON,self)
        self.address_list.set_data(INDEX,-1)

        # draw lists
        self.redraw_event_list()
        self.redraw_attr_list()
        self.redraw_address_list()
        self.redraw_name_list()
        self.redraw_url_list()

    #---------------------------------------------------------------------
    #
    # get_widget - returns the widget related to the passed string
    #
    #---------------------------------------------------------------------
    def get_widget(self,str):
        return self.top_window.get_widget(str)

    #---------------------------------------------------------------------
    #
    # redraw_name_list - redraws the altername name list for the person
    #
    #---------------------------------------------------------------------
    def redraw_name_list(self):
        self.name_list.freeze()
        self.name_list.clear()

	self.name_index = 0
        for name in self.nlist:
            attr = get_detail_flags(name)
            self.name_list.append([name.getName(),attr])
            self.name_list.set_row_data(self.name_index,name)
            self.name_index = self.name_index + 1

        current_row = self.name_list.get_data(INDEX)
        
        if self.name_index > 0:
            if current_row <= 0:
                current_row = 0
            elif self.name_index <= current_row:
                current_row = current_row - 1
            self.name_list.select_row(current_row,0)
            self.name_list.moveto(current_row,0)
        self.name_list.set_data(INDEX,current_row)
        self.name_list.thaw()

    #---------------------------------------------------------------------
    #
    # redraw_url_list - redraws the altername name list for the person
    #
    #---------------------------------------------------------------------
    def redraw_url_list(self):
        self.web_list.freeze()
        self.web_list.clear()

	self.web_index = 0
        for url in self.ulist:
            self.web_list.append([url.get_path(),url.get_description()])
            self.web_list.set_row_data(self.web_index,url)
            self.web_index = self.web_index + 1

        current_row = self.web_list.get_data(INDEX)
        
        if self.web_index > 0:
            if current_row <= 0:
                current_row = 0
            elif self.web_index <= current_row:
                current_row = current_row - 1
            self.web_list.select_row(current_row,0)
            self.web_list.moveto(current_row,0)
        self.web_list.set_data(INDEX,current_row)
        self.web_list.thaw()

    #---------------------------------------------------------------------
    #
    # redraw_attr_list - redraws the attribute list for the person
    #
    #---------------------------------------------------------------------
    def redraw_attr_list(self):
        self.attr_list.freeze()
        self.attr_list.clear()

	self.attr_index = 0
        for attr in self.alist:
            detail = get_detail_flags(attr)
            self.attr_list.append([const.display_pattr(attr.getType()),\
                                   attr.getValue(),detail])
            self.attr_list.set_row_data(self.attr_index,attr)
            self.attr_index = self.attr_index + 1

        current_row = self.attr_list.get_data(INDEX)
        
        if self.attr_index > 0:
            if current_row <= 0:
                current_row = 0
            elif self.attr_index <= current_row:
                current_row = current_row - 1
            self.attr_list.select_row(current_row,0)
            self.attr_list.moveto(current_row,0)
        self.attr_list.set_data(INDEX,current_row)
        self.attr_list.thaw()

    #---------------------------------------------------------------------
    #
    # redraw_address_list - redraws the address list for the person
    #
    #---------------------------------------------------------------------
    def redraw_address_list(self):
        self.address_list.freeze()
        self.address_list.clear()

	self.address_index = 0
        for address in self.plist:
            detail = get_detail_flags(address)
            location = address.getCity() + " " + address.getState() + " " + \
                       address.getCountry()
            self.address_list.append([address.getDate(),location,detail])
            self.address_list.set_row_data(self.address_index,address)
            self.address_index = self.address_index + 1

        current_row = self.address_list.get_data(INDEX)
        
        if self.address_index > 0:
            if current_row <= 0:
                current_row = 0
            elif self.address_index <= current_row:
                current_row = current_row - 1
            self.address_list.select_row(current_row,0)
            self.address_list.moveto(current_row,0)
        self.address_list.set_data(INDEX,current_row)
        self.address_list.thaw()

    #---------------------------------------------------------------------
    #
    # redraw_event_list - redraws the event list for the person
    #
    #---------------------------------------------------------------------
    def redraw_event_list(self):

        self.event_list.freeze()
        self.event_list.clear()

        self.event_index = 0
        for event in self.elist:
            attr = get_detail_flags(event)
            self.event_list.append([const.display_pevent(event.getName()),\
                                    event.getQuoteDate(), event.getPlace(),attr])
            self.event_list.set_row_data(self.event_index,event)
            self.event_index = self.event_index + 1

        current_row = self.event_list.get_data(INDEX)
        
        if self.event_index > 0:
            if current_row <= 0:
                current_row = 0
            elif self.event_index <= current_row:
                current_row = current_row - 1
            self.event_list.select_row(current_row,0)
            self.event_list.moveto(current_row,0)
            
        self.event_list.set_data(INDEX,current_row)
        self.event_list.thaw()

    #-------------------------------------------------------------------------
    #
    # add_thumbnail - Scale the image and add it to the IconList. 
    #
    #-------------------------------------------------------------------------
    def add_thumbnail(self,photo):
        src = photo.getPath()
        thumb = "%s%s.thumb%s%s" % (self.path,os.sep,os.sep,os.path.basename(src))

        RelImage.check_thumb(src,thumb,const.thumbScale)

        self.photo_list.append(thumb,photo.getDescription())
        
    #-------------------------------------------------------------------------
    #
    # load_images - add each photo in the person's list of photos to the 
    # photolist window.
    #
    #-------------------------------------------------------------------------
    def load_images(self):
        if len(self.person.getPhotoList()) == 0:
            return
        self.photo_list.freeze()
        self.photo_list.clear()
        for photo in self.person.getPhotoList():
            self.add_thumbnail(photo)
        self.photo_list.thaw()

    #-------------------------------------------------------------------------
    #
    # load_photo - loads the specfied photo, scales it, and displays it 
    # as the person's main photo.  Imlib does not scale in place, so a second
    # copy must be made to get a scaled image.
    #
    #-------------------------------------------------------------------------
    def load_photo(self,photo):
        import GdkImlib

        i = GdkImlib.Image(photo)
        scale = float(const.picWidth)/float(max(i.rgb_height,i.rgb_width))
        x = int(scale*(i.rgb_width))
        y = int(scale*(i.rgb_height))
        i = i.clone_scaled_image(x,y)
        self.get_widget("personPix").load_imlib(i)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def update_events(self):
        self.person.setEventList(self.elist)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def update_names(self):
        self.person.setAlternateNames(self.nlist)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def update_urls(self):
        self.person.setUrlList(self.ulist)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def update_attributes(self):
        self.person.setAttributeList(self.alist)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def update_addresses(self):
        self.person.setAddressList(self.plist)

#-------------------------------------------------------------------------
#
# on_name_list_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_name_list_select_row(obj,row,b,c):
    obj.set_data(INDEX,row)

    epo = obj.get_data(EDITPERSON)
    name = obj.get_row_data(row)

    epo.name_frame.set_label(name.getName())
    epo.alt_given_field.set_text(": %s" % name.getFirstName())
    epo.alt_last_field.set_text(": %s" % name.getSurname())
    epo.alt_suffix_field.set_text(": %s" % name.getSuffix())
    epo.name_details_field.set_text(": %s" % get_detail_text(name))

#-------------------------------------------------------------------------
#
# on_name_list_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_web_list_select_row(obj,row,b,c):
    obj.set_data(INDEX,row)

    epo = obj.get_data(EDITPERSON)
    url = obj.get_row_data(row)

    epo.web_url.set_text(":%s " % url.get_path())
    epo.web_description.set_text(": %s" % url.get_description())

#-------------------------------------------------------------------------
#
# on_attr_list_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_attr_list_select_row(obj,row,b,c):
    obj.set_data(INDEX,row)

    epo = obj.get_data(EDITPERSON)
    attr = obj.get_row_data(row)

    epo.attr_type.set_label(const.display_pattr(attr.getType()))
    epo.attr_value.set_text(": %s" % attr.getValue())
    epo.attr_details_field.set_text(": %s" % get_detail_text(attr))

#-------------------------------------------------------------------------
#
# on_name_list_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_address_list_select_row(obj,row,b,c):
    obj.set_data(INDEX,row)

    epo = obj.get_data(EDITPERSON)
    a = obj.get_row_data(row)

    epo.address_label.set_label("%s %s %s" % \
                                (a.getCity(),a.getState(),a.getCountry()))
    epo.address_start.set_text(": %s" % a.getDate())
    epo.address_street.set_text(": %s" % a.getStreet())
    epo.address_city.set_text(": %s" % a.getCity())
    epo.address_state.set_text(": %s" % a.getState())
    epo.address_country.set_text(": %s" % a.getCountry())
    epo.address_postal.set_text(": %s" % a.getPostal())
    epo.addr_details_field.set_text(": %s" % get_detail_text(a))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_aka_update_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return

    NameEditor(obj.get_data(EDITPERSON),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_url_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return

    UrlEditor(obj.get_data(EDITPERSON),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_attr_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return

    AttributeEditor(obj.get_data(EDITPERSON),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_address_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return
    AddressEditor(obj.get_data(EDITPERSON),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_aka_delete_clicked(obj):
    row = obj.get_data(INDEX)
    epo = obj.get_data(EDITPERSON)
    if row < 0:
        return

    del epo.nlist[row]

    if row > len(epo.nlist)-1:
        obj.set_data(INDEX,row-1)

    epo.redraw_name_list()
    utils.modified()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_url_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return

    epo = obj.get_data(EDITPERSON)
    del epo.ulist[row]

    if row > len(epo.ulist)-1:
        obj.set_data(INDEX,row-1)

    epo.redraw_url_list()
    utils.modified()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_attr_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return

    epo = obj.get_data(EDITPERSON)
    del epo.alist[row]

    if row > len(epo.alist)-1:
        obj.set_data(INDEX,row-1)

    epo.redraw_attr_list()
    epo.attr_changed = 1
    utils.modified()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_address_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return

    row = obj.get_data(INDEX)
    if row < 0:
        return

    epo = obj.get_data(EDITPERSON)
    del epo.plist[row]

    if row > len(epo.plist)-1:
        obj.set_data(INDEX,row-1)

    epo.redraw_address_list()
    epo.addr_changed = 1
    utils.modified()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_aka_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    NameEditor(epo,None)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_url_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    UrlEditor(epo,None)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_attr_clicked(obj):
    AttributeEditor(obj.get_data(EDITPERSON),None)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_address_clicked(obj):
    AddressEditor(obj.get_data(EDITPERSON),None)

#-------------------------------------------------------------------------
#
# on_event_add_clicked
#
# Called from the Add button on the edit_person window.  A new event is
# created, extracting the data from the text fieldls.  The event is added
# to the person being edited.
#
#-------------------------------------------------------------------------
def on_event_add_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    editor = EventEditor(epo,None)

#-------------------------------------------------------------------------
#
# on_event_delete_clicked
#
# Called from the edit_person window, to update the values on the selected
# event.  The EditPerson object and the selected row are attached to the
# passed object.
#
#-------------------------------------------------------------------------
def on_event_delete_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    row = obj.get_data(INDEX)
    if row < 0:
        return
    
    del epo.elist[row]

    if row > len(epo.elist)-1:
        obj.set_data(INDEX,row-1)
        
    epo.redraw_event_list()
    epo.events_changed = 1

#-------------------------------------------------------------------------
#
# on_event_update_clicked
#
# Called from the edit_person window, to update the values on the selected
# event.  The EditPerson object and the selected row are attached to the
# passed object.
#
#-------------------------------------------------------------------------
def on_event_update_clicked(obj):
    row = obj.get_data(INDEX)
    if row < 0:
        return

    epo = obj.get_data(EDITPERSON)
    event = obj.get_row_data(row)
    editor = EventEditor(epo,event)

#-------------------------------------------------------------------------
#
# on_event_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_event_select_row(obj,row,b,c):
    obj.set_data(INDEX,row)
    event = obj.get_row_data(row)

    epo = obj.get_data(EDITPERSON)
    epo.event_date_field.set_text(": %s" % event.getDate())
    epo.event_place_field.set_text(": %s" % event.getPlace())
    epo.event_name_field.set_label(": %s" % const.display_pevent(event.getName()))
    epo.event_descr_field.set_text(": %s" % event.getDescription())
    epo.event_details_field.set_text(": %s" % get_detail_text(event))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_switch_page(obj,a,page):
    edit_obj = obj.get_data(EDITPERSON)
    if page == 6 and edit_obj.not_loaded:
        edit_obj.not_loaded = 0
        edit_obj.load_images()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_photo_select_icon(obj,iconNumber,event):
    obj.get_data(EDITPERSON).selectedIcon = iconNumber

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_photo_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    icon = epo.selectedIcon

    if icon == -1:
        return
    
    photolist = epo.person.getPhotoList()
    epo.photo_list.remove(icon)
    del photolist[epo.selectedIcon]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_primary_photo_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    if epo.selectedIcon == None or \
       epo.selectedIcon == 0:
        return

    photolist = epo.person.getPhotoList()
    selectedIcon = epo.selectedIcon
    savePhoto = photolist[selectedIcon]
    for i in range(0,selectedIcon):
        photolist[selectedIcon-i] = photolist[selectedIcon-i-1]
    photolist[0] = savePhoto

    epo.load_photo(savePhoto.getPath())
    epo.load_images()
    utils.modified()

#-------------------------------------------------------------------------
#
# update_event
# 
# Updates the specified event with the specified date.  Compares against
# the previous value, so the that modified flag is not set if nothing has
# actually changed.
#
#-------------------------------------------------------------------------
def update_event(event,name,date,place,desc,note,priv,conf):
    changed = 0
    if event.getPlace() != place:
        event.setPlace(place)
        changed = 1
        
    if event.getName() != const.save_pevent(name):
        event.setName(const.save_pevent(name))
        changed = 1
        
    if event.getDescription() != desc:
        event.setDescription(desc)
        changed = 1

    if event.getNote() != note:
        event.setNote(note)
        changed = 1

    if event.getDate() != date:
        event.setDate(date)
        changed = 1

    if event.getPrivacy() != priv:
        event.setPrivacy(priv)
        changed = 1

    if event.getConfidence() != conf:
        event.setConfidence(conf)
        changed = 1
        
    return changed

#-------------------------------------------------------------------------
#
# update_address
# 
# Updates the specified event with the specified date.  Compares against
# the previous value, so the that modified flag is not set if nothing has
# actually changed.
#
#-------------------------------------------------------------------------
def update_address(addr,date,street,city,state,country,postal,note,priv,conf):
    changed = 0

    d = Date()
    d.set(date)
    if addr.getDate() != d.getDate():
        addr.setDate(date)
        changed = 1
        
    if addr.getState() != state:
        addr.setState(state)
        changed = 1

    if addr.getCountry() != country:
        addr.setCountry(country)
        changed = 1

    if addr.getCity() != city:
        addr.setCity(city)
        changed = 1

    if addr.getPostal() != postal:
        addr.setPostal(postal)
        changed = 1

    if addr.getNote() != note:
        addr.setNote(note)
        changed = 1

    if addr.getPrivacy() != priv:
        addr.setPrivacy(priv)
        changed = 1

    if addr.getConfidence() != conf:
        addr.setConfidence(conf)
        changed = 1

    return changed

#-------------------------------------------------------------------------
#
# update_attrib
# 
# Updates the specified event with the specified date.  Compares against
# the previous value, so the that modified flag is not set if nothing has
# actually changed.
#
#-------------------------------------------------------------------------
def update_attrib(attr,type,value,note,priv,conf):
    changed = 0
        
    if attr.getType() != const.save_pattr(type):
        attr.setType(const.save_pattr(type))
        changed = 1
        
    if attr.getValue() != value:
        attr.setValue(value)
        changed = 1

    if attr.getNote() != note:
        attr.setNote(note)
        changed = 1

    if attr.getPrivacy() != priv:
        attr.setPrivacy(priv)
        changed = 1

    if attr.getConfidence() != conf:
        attr.setConfidence(conf)
        changed = 1

    return changed

#-------------------------------------------------------------------------
#
# update_attrib
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
# update_name
# 
# Updates the specified name.  Compares against
# the previous value, so the that modified flag is not set if nothing has
# actually changed.
#
#-------------------------------------------------------------------------
def update_name(name,first,last,suffix,note,priv,conf):
    changed = 0
        
    if name.getFirstName() != first:
        name.setFirstName(first)
        changed = 1
        
    if name.getSurname() != last:
        name.setSurname(last)
        if last not in const.surnames:
            const.surnames.append(last)
            const.surnames.sort()
        changed = 1

    if name.getSuffix() != suffix:
        name.setSuffix(suffix)
        changed = 1

    if name.getNote() != note:
        name.setNote(note)
        changed = 1

    if name.getPrivacy() != priv:
        name.setPrivacy(priv)
        changed = 1

    if name.getConfidence() != conf:
        name.setConfidence(conf)
        changed = 1

    return changed

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_photo_clicked(obj):

    edit_person = obj.get_data(EDITPERSON)
    
    image_select = libglade.GladeXML(const.imageselFile,"imageSelect")

    edit_person.isel = image_select

    image_select.signal_autoconnect({
        "on_savephoto_clicked" : on_savephoto_clicked,
        "on_name_changed" : on_name_changed,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    edit_person.fname = image_select.get_widget("fname")
    edit_person.add_image = image_select.get_widget("image")
    edit_person.external = image_select.get_widget("private")
    image_select.get_widget("imageSelect").set_data(EDITPERSON,edit_person)
    image_select.get_widget("imageSelect").show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_name_changed(obj):
    edit_person = obj.get_data(EDITPERSON)
    file = edit_person.fname.get_text()
    if os.path.isfile(file):
        image = RelImage.scale_image(file,const.thumbScale)
        edit_person.add_image.load_imlib(image)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_apply_person_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    person = epo.person
    
    surname = epo.surname_field.get_text()
    suffix = epo.suffix.get_text()
    given = epo.given.get_text()
    nick = epo.nick.get_text()
    title = epo.title.get_text()

    name = person.getPrimaryName()

    if suffix != name.getSuffix():
        name.setSuffix(suffix)
        utils.modified()

    if surname != name.getSurname():
        name.setSurname(surname)
        if surname not in const.surnames:
            const.surnames.append(surname)
            const.surnames.sort()
        utils.modified()

    if given != name.getFirstName():
        name.setFirstName(given)
        utils.modified()

    if nick != person.getNickName():
        person.setNickName(nick)
        utils.modified()

    if title != name.getTitle():
        name.setTitle(title)
        utils.modified()

    birth  = person.getBirth()
    bdate  = epo.bdate.get_text()
    bplace = epo.bplace.get_text()
    
    death  = person.getDeath()
    ddate  = epo.ddate.get_text()
    dplace = epo.dplace.get_text()

    for place in [ dplace, bplace ]:
        if place not in const.places:
            const.places.append(place)
            const.places.sort()

    newBirth = Event()
    newBirth.set("Birth",bdate,bplace,"")
    
    if newBirth.compare(birth):
        person.setBirth(newBirth)
        utils.modified()

    newDeath = Event()

    newDeath.set("Death",ddate,dplace,"")

    if newDeath.compare(death):
        person.setDeath(newDeath)
        utils.modified()

    gender = epo.is_male.get_active()
    error = 0
    if gender and person.getGender() == Person.female:
        person.setGender(Person.male)
        for temp_family in person.getFamilyList():
            if person == temp_family.getMother():
                if temp_family.getFather() != None:
                    error = 1
                else:
                    temp_family.setMother(None)
                    temp_family.setFather(person)
        utils.modified()
    elif not gender and person.getGender() == Person.male:
        person.setGender(Person.female)
        for temp_family in person.getFamilyList():
            if person == temp_family.getFather():
                if temp_family.getMother() != None:
                    error = 1
                else:
                    temp_family.setFather(None)
                    temp_family.setMother(person)
        utils.modified()

    if error == 1:
        msg = _("Changing the gender caused problems with marriage information.")
        msg2 = _("Please check the person's marriages.")
        GnomeErrorDialog("%s\n%s" % (msg,msg2))
        
    text = epo.notes_field.get_chars(0,-1)
    if text != person.getNote():
        person.setNote(text)
        utils.modified()

    epo.update_events()
    if epo.events_changed:
        utils.modified()

    epo.update_names()
    if epo.names_changed:
        utils.modified()

    epo.update_urls()
    if epo.urls_changed:
        utils.modified()

    epo.update_attributes()
    if epo.attr_changed:
        utils.modified()

    epo.update_addresses()
    if epo.addr_changed:
        utils.modified()
        
    utils.destroy_passed_object(obj)
    epo.callback(epo)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_savephoto_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    image_select = epo.isel
    
    filename = image_select.get_widget("photosel").get_full_path(0)
    description = image_select.get_widget("photoDescription").get_text()

    if os.path.exists(filename) == 0:
        return

    prefix = "i%s" % epo.person.getId()
    if epo.external.get_active() == 1:
        if os.path.isfile(filename):
            name = filename
        else:
            return
    else:
        name = RelImage.import_photo(filename,epo.path,prefix)
        if name == None:
            return
        
    photo = Photo()
    photo.setPath(name)
    photo.setDescription(description)
    
    epo.person.addPhoto(photo)
    epo.add_thumbnail(photo)

    utils.modified()
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_save_note_clicked(obj):
    textbox = obj.get_data("w")
    data = obj.get_data("n")

    text = textbox.get_chars(0,-1)
    if text != data.getNote():
        data.setNote(text)
        utils.modified()

    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_birth_note_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    editnote = libglade.GladeXML(const.editnoteFile,"editnote")
    data = epo.person.getBirth()
    textobj = editnote.get_widget("notetext")
    en_obj = editnote.get_widget("editnote")
    en_obj.set_data("n",data)
    en_obj.set_data("w",textobj)

    textobj.set_point(0)
    textobj.insert_defaults(data.getNote())
    textobj.set_word_wrap(1)
        
    editnote.signal_autoconnect({
        "on_save_note_clicked" : on_save_note_clicked,
        "destroy_passed_object" : utils.destroy_passed_object
    })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_name_note_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    editnote = libglade.GladeXML(const.editnoteFile,"editnote")
    data = epo.person.getPrimaryName()
    textobj = editnote.get_widget("notetext")
    en_obj = editnote.get_widget("editnote")
    en_obj.set_data("n",data)
    en_obj.set_data("w",textobj)

    textobj.set_point(0)
    textobj.insert_defaults(data.getNote())
    textobj.set_word_wrap(1)
        
    editnote.signal_autoconnect({
        "on_save_note_clicked" : on_save_note_clicked,
        "destroy_passed_object" : utils.destroy_passed_object
    })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_death_note_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    editnote = libglade.GladeXML(const.editnoteFile,"editnote")
    textobj = editnote.get_widget("notetext")
    data = epo.person.getDeath()
    en_obj = editnote.get_widget("editnote")
    en_obj.set_data("n",data)
    en_obj.set_data("w",textobj)

    textobj.set_point(0)
    textobj.insert_defaults(data.getNote())
    textobj.set_word_wrap(1)
        
    editnote.signal_autoconnect({
        "on_save_note_clicked" : on_save_note_clicked,
        "destroy_passed_object" : utils.destroy_passed_object
    })
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_death_source_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    Sources.SourceEditor(epo.person.getDeath(),epo.db)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_name_source_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    Sources.SourceEditor(epo.person.getPrimaryName(),epo.db)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_birth_source_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    Sources.SourceEditor(epo.person.getBirth(),epo.db)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_showsource_clicked(obj):
    row = obj.get_data(INDEX)
    epo = obj.get_data(EDITPERSON)
    if row >= 0:
        Sources.SourceEditor(obj.get_row_data(row),epo.db)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_photolist_button_press_event(obj,event):

    myobj = obj.get_data(EDITPERSON)
    icon = myobj.selectedIcon
    if icon == -1:
        return
    
    if event.button == 3:
        photo = myobj.person.getPhotoList()[icon]
        menu = GtkMenu()
        item = GtkTearoffMenuItem()
        item.show()
        view = GtkMenuItem(_("View Image"))
        view.set_data("m",myobj)
        view.connect("activate",on_view_photo)
        view.show()
        edit = GtkMenuItem(_("Edit Image"))
        edit.set_data("m",myobj)
        edit.connect("activate",on_edit_photo)
        edit.show()
        change = GtkMenuItem(_("Edit Description"))
        change.set_data("m",myobj)
        change.connect("activate",on_change_description)
        change.show()
        menu.append(item)
        menu.append(view)
        menu.append(edit)
        menu.append(change)
        if photo.getPrivate() == 0:
            private = GtkMenuItem(_("Convert to private copy"))
            private.set_data("m",myobj)
            private.connect("activate",on_convert_to_private)
            private.show()
            menu.append(private)
        menu.popup(None,None,None,0,0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_convert_to_private(obj):
    epo = obj.get_data("m")
    photo = epo.person.getPhotoList()[epo.selectedIcon]

    prefix = "i%s" % epo.person.getId()
    name = RelImage.import_photo(photo.getPath(),epo.path,prefix)

    photo.setPath(name)
    photo.setPrivate(1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_view_photo(obj):
    myobj = obj.get_data("m")
    photo = myobj.person.getPhotoList()[myobj.selectedIcon]
    type = gnome.mime.type(photo.getPath())
    
    prog = string.split(gnome.mime.get_value(type,'view'))
    args = []
    for val in prog:
        if val == "%f":
            args.append(photo.getPath())
        else:
            args.append(val)
    
    if os.fork() == 0:
        os.execvp(args[0],args)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_photo(obj):
    myobj = obj.get_data("m")
    photo = myobj.person.getPhotoList()[myobj.selectedIcon]
    if os.fork() == 0:
        os.execvp(const.editor,[const.editor, photo.getPath()])

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_change_description(obj):
    myobj = obj.get_data("m")
    photo = myobj.person.getPhotoList()[myobj.selectedIcon]
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
def on_ok_clicked(obj):
    on_apply_clicked(obj)
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_browse_clicked(obj):
    import gnome.url

    path = obj.get()
    if path != "":
        gnome.url.show(path)


#-------------------------------------------------------------------------
#
# EventEditor class
#
#-------------------------------------------------------------------------
class EventEditor:

    def __init__(self,parent,event):
        self.parent = parent
        self.event = event
        self.top = libglade.GladeXML(const.dialogFile, "event_edit")
        self.window = self.top.get_widget("event_edit")
        self.name_field  = self.top.get_widget("eventName")
        self.place_field = self.top.get_widget("eventPlace")
        self.date_field  = self.top.get_widget("eventDate")
        self.descr_field = self.top.get_widget("eventDescription")
        self.note_field = self.top.get_widget("eventNote")
        self.event_menu = self.top.get_widget("personalEvents")
        self.source_field = self.top.get_widget("event_source")
        self.conf_menu = self.top.get_widget("conf")
        self.priv = self.top.get_widget("priv")
        
        name = parent.person.getPrimaryName().getName()
        
        self.top.get_widget("eventTitle").set_text(_("Event Editor for %s") % name) 
        self.event_menu.set_popdown_strings(const.personalEvents)

        myMenu = GtkMenu()
        index = 0
        for name in const.confidence:
            item = GtkMenuItem(name)
            item.set_data("a",index)
            item.show()
            myMenu.append(item)
            index = index + 1

        self.conf_menu.set_menu(myMenu)

        if event != None:
            self.name_field.set_text(event.getName())
            self.place_field.set_text(event.getPlace())
            self.date_field.set_text(event.getDate())
            self.descr_field.set_text(event.getDescription())
            self.conf_menu.set_history(event.getConfidence())

            self.priv.set_active(event.getPrivacy())
            
            srcref_base = self.event.getSourceRef().getBase()
            if srcref_base:
                self.source_field.set_text(srcref_base.getTitle())
            else:
                self.source_field.set_text("")
                 
            self.note_field.set_point(0)
            self.note_field.insert_defaults(event.getNote())
            self.note_field.set_word_wrap(1)
        else:
            self.conf_menu.set_history(2)

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_event_edit_ok_clicked" : on_event_edit_ok_clicked,
            "on_source_clicked" : on_edit_source_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_source_clicked(obj):
    ee = obj.get_data("o")
    Sources.SourceEditor(ee.event,ee.parent.db,ee.source_field)
            
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_event_edit_ok_clicked(obj):
    ee = obj.get_data("o")
    event = ee.event

    ename = ee.name_field.get_text()
    edate = ee.date_field.get_text()
    eplace = ee.place_field.get_text()
    enote = ee.note_field.get_chars(0,-1)
    edesc = ee.descr_field.get_text()
    epriv = ee.priv.get_active()
    econf = ee.conf_menu.get_menu().get_active().get_data("a")

    if event == None:
        event = Event()
        ee.parent.elist.append(event)
        
    if update_event(event,ename,edate,eplace,edesc,enote,epriv,econf):
        ee.parent.events_changed = 1
        
    ee.parent.redraw_event_list()
    utils.destroy_passed_object(obj)


#-------------------------------------------------------------------------
#
# AttributeEditor class
#
#-------------------------------------------------------------------------
class AttributeEditor:

    def __init__(self,parent,attrib):
        self.parent = parent
        self.attrib = attrib
        self.top = libglade.GladeXML(const.dialogFile, "attr_edit")
        self.window = self.top.get_widget("attr_edit")
        self.type_field  = self.top.get_widget("attr_type")
        self.value_field = self.top.get_widget("attr_value")
        self.note_field = self.top.get_widget("attr_note")
        self.attrib_menu = self.top.get_widget("attr_menu")
        self.source_field = self.top.get_widget("attr_source")
        self.conf_menu = self.top.get_widget("conf")
        self.priv = self.top.get_widget("priv")

        name = parent.person.getPrimaryName().getName()
        
        self.top.get_widget("attrTitle").set_text(_("Attribute Editor for %s") % name) 
        self.attrib_menu.set_popdown_strings(const.personalAttributes)

        myMenu = GtkMenu()
        index = 0
        for name in const.confidence:
            item = GtkMenuItem(name)
            item.set_data("a",index)
            item.show()
            myMenu.append(item)
            index = index + 1
        self.conf_menu.set_menu(myMenu)

        if attrib != None:
            self.type_field.set_text(attrib.getType())
            self.value_field.set_text(attrib.getValue())
            srcref_base = self.attrib.getSourceRef().getBase()
            if srcref_base:
                self.source_field.set_text(srcref_base.getTitle())
            else:
                self.source_field.set_text("")
                 
            self.conf_menu.set_history(attrib.getConfidence())

            self.priv.set_active(attrib.getPrivacy())

            self.note_field.set_point(0)
            self.note_field.insert_defaults(attrib.getNote())
            self.note_field.set_word_wrap(1)
        else:
            self.conf_menu.set_history(2)

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_attr_edit_ok_clicked" : on_attrib_edit_ok_clicked,
            "on_source_clicked" : on_attrib_source_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_attrib_source_clicked(obj):
    ee = obj.get_data("o")
    Sources.SourceEditor(ee.attrib,ee.parent.db,ee.source_field)
            
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_attrib_edit_ok_clicked(obj):
    ee = obj.get_data("o")
    attrib = ee.attrib

    type = ee.type_field.get_text()
    value = ee.value_field.get_text()
    note = ee.note_field.get_chars(0,-1)
    priv = ee.priv.get_active()
    conf = ee.conf_menu.get_menu().get_active().get_data("a")

    if attrib == None:
        attrib = Attribute()
        ee.parent.alist.append(attrib)
        
    if update_attrib(attrib,type,value,note,priv,conf):
        ee.parent.attr_changed = 1
        
    ee.parent.redraw_attr_list()
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
# NameEditor class
#
#-------------------------------------------------------------------------
class NameEditor:

    def __init__(self,parent,name):
        self.parent = parent
        self.name = name
        self.top = libglade.GladeXML(const.editPersonFile, "name_edit")
        self.window = self.top.get_widget("name_edit")
        self.given_field  = self.top.get_widget("alt_given")
        self.surname_field = self.top.get_widget("alt_last")
        self.suffix_field = self.top.get_widget("alt_suffix")
        self.note_field = self.top.get_widget("alt_note")
        self.source_field = self.top.get_widget("alt_source")
        self.top.get_widget("alt_surname_list").set_popdown_strings(const.surnames)
        self.conf_menu = self.top.get_widget("conf")
        self.priv = self.top.get_widget("priv")

        full_name = parent.person.getPrimaryName().getName()
        
        self.top.get_widget("altTitle").set_text(
            _("Alternate Name Editor for %s") % full_name)

        myMenu = GtkMenu()
        index = 0
        for val in const.confidence:
            item = GtkMenuItem(val)
            item.set_data("a",index)
            item.show()
            myMenu.append(item)
            index = index + 1

        self.conf_menu.set_menu(myMenu)

        if name != None:
            self.given_field.set_text(name.getFirstName())
            self.surname_field.set_text(name.getSurname())
            self.suffix_field.set_text(name.getSuffix())
            srcref_base = self.name.getSourceRef().getBase()
            if srcref_base:
                self.source_field.set_text(srcref_base.getTitle())
            else:
                self.source_field.set_text("")
                 
            self.conf_menu.set_history(name.getConfidence())

            self.priv.set_active(name.getPrivacy())

            self.note_field.set_point(0)
            self.note_field.insert_defaults(name.getNote())
            self.note_field.set_word_wrap(1)
        else:
            self.conf_menu.set_history(2)

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_name_edit_ok_clicked" : on_name_edit_ok_clicked,
            "on_source_clicked" : on_name_source_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_name_source_clicked(obj):
    ee = obj.get_data("o")
    Sources.SourceEditor(ee.name,ee.parent.db,ee.source_field)
            
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_name_edit_ok_clicked(obj):
    ee = obj.get_data("o")
    name = ee.name

    first = ee.given_field.get_text()
    last = ee.surname_field.get_text()
    suffix = ee.suffix_field.get_text()
    note = ee.note_field.get_chars(0,-1)
    priv = ee.priv.get_active()
    conf = ee.conf_menu.get_menu().get_active().get_data("a")

    if name == None:
        name = Name()
        ee.parent.nlist.append(name)
        
    if update_name(name,first,last,suffix,note,priv,conf):
        ee.parent.name_changed = 1
        
    ee.parent.redraw_name_list()
    utils.destroy_passed_object(obj)


#-------------------------------------------------------------------------
#
# AddressEditor class
#
#-------------------------------------------------------------------------
class AddressEditor:

    def __init__(self,parent,addr):
        self.parent = parent
        self.addr = addr
        self.top = libglade.GladeXML(const.editPersonFile, "addr_edit")
        self.window = self.top.get_widget("addr_edit")
        self.address_start  = self.top.get_widget("address_start")
        self.street = self.top.get_widget("street")
        self.city = self.top.get_widget("city")
        self.state = self.top.get_widget("state")
        self.country = self.top.get_widget("country")
        self.postal = self.top.get_widget("postal")
        self.note_field = self.top.get_widget("addr_note")
        self.source_field = self.top.get_widget("addr_source")
        self.conf_menu = self.top.get_widget("conf")
        self.priv = self.top.get_widget("priv")

        name = parent.person.getPrimaryName().getName()
        text = _("Address Editor for %s") % name
        self.top.get_widget("addrTitle").set_text(text)

        myMenu = GtkMenu()
        index = 0
        for val in const.confidence:
            item = GtkMenuItem(val)
            item.set_data("a",index)
            item.show()
            myMenu.append(item)
            index = index + 1

        self.conf_menu.set_menu(myMenu)

        if addr != None:
            self.street.set_text(addr.getFirstAddr())
            self.suraddr_field.set_text(addr.getSuraddr())
            self.suffix_field.set_text(addr.getSuffix())
            srcref_base = self.addr.getSourceRef().getBase()
            if srcref_base:
                self.source_field.set_text(srcref_base.getTitle())
            else:
                self.source_field.set_text("")
                 
            self.conf_menu.set_history(addr.getConfidence())

            self.priv.set_active(addr.getPrivacy())

            self.note_field.set_point(0)
            self.note_field.insert_defaults(addr.getNote())
            self.note_field.set_word_wrap(1)
        else:
            self.conf_menu.set_history(2)

        self.window.set_data("o",self)
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_addr_edit_ok_clicked" : on_addr_edit_ok_clicked,
            "on_source_clicked" : on_addr_source_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_addr_source_clicked(obj):
    ee = obj.get_data("o")
    Sources.SourceEditor(ee.addr,ee.parent.db,ee.source_field)
            
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_addr_edit_ok_clicked(obj):
    ee = obj.get_data("o")
    addr = ee.addr

    date = ee.address_start.get_text()
    street = ee.street.get_text()
    city = ee.city.get_text()
    state = ee.state.get_text()
    country = ee.country.get_text()
    postal = ee.postal.get_text()
    note = ee.note_field.get_chars(0,-1)
    priv = ee.priv.get_active()
    conf = ee.conf_menu.get_menu().get_active().get_data("a")

    if addr == None:
        addr = Address()
        ee.parent.plist.append(addr)
        
    if update_address(addr,date,street,city,state,country,postal,note,priv,conf):
        ee.parent.addr_changed = 1
        
    ee.parent.redraw_address_list()
    utils.destroy_passed_object(obj)

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

        name = parent.person.getPrimaryName().getName()
        
        self.top.get_widget("urlTitle").set_text(_("Internet Address Editor for %s") % name) 

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
        ee.parent.urls_changed = 1
        
    ee.parent.redraw_url_list()
    utils.destroy_passed_object(obj)


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_detail_flags(obj):
    detail = ""
    if Config.show_detail:
        if obj.getNote() != "":
            detail = "N"
        if obj.getSourceRef().getBase():
            detail = detail + "S"
        if obj.getPrivacy():
            detail = detail + "P"
    return detail

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_detail_text(obj):
    if obj.getNote() != "":
        details = "%s" % _("Note")
    else:
        details = ""
    if obj.getSourceRef().getBase() != None:
        if details == "":
            details = _("Source")
        else:
            details = "%s, %s" % (details,_("Source"))
    if obj.getPrivacy() == 1:
        if details == "":
            details = _("Private")
        else:
            details = "%s, %s" % (details,_("Private"))
    return details
