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
import GdkImlib

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

_DEFHTTP = "http://gramps.sourceforge.net"

#-------------------------------------------------------------------------
#
# Constants - quite frequently, data needs to be attached to a widget.
# this is done to prevent the use of globals, and to allow data to be
# passed with a widget (especially critical, since more that one window
# can be opened at a time). Data is attached to an widget using a string
# as the key. To avoid a lot of hard coded text strings floating around
# everywhere, values are defined here as constants with more meaningful
# names.
#
#-------------------------------------------------------------------------
INDEX      = "i"
EDITPERSON = "p"
OBJECT     = "o"
MENUVAL    = "a"
PHOTO      = "p"
TEXT       = "t"
NOTEOBJ    = "n"
TEXTOBJ    = "w"

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
        self.lists_changed = 0
        
        self.top = libglade.GladeXML(const.editPersonFile, "editPerson")

        # widgets
        self.window = self.get_widget("editPerson")
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
        self.web_url = self.get_widget("web_url")
        self.web_go = self.get_widget("web_go")
        self.web_description = self.get_widget("url_des")
        self.addr_label = self.get_widget("address_label")
        self.addr_list = self.get_widget("address_list")
        self.addr_start = self.get_widget("address_start")
        self.addr_street = self.get_widget("street")
        self.addr_city = self.get_widget("city")
        self.addr_state = self.get_widget("state")
        self.addr_country = self.get_widget("country")
        self.addr_postal = self.get_widget("postal")
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
        self.bpcombo = self.get_widget("bp_combo")
        self.dpcombo = self.get_widget("dp_combo")
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
        self.gid = self.get_widget("gid")

        self.elist = person.getEventList()[:]
        self.nlist = person.getAlternateNames()[:]
        self.alist = person.getAttributeList()[:]
        self.ulist = person.getUrlList()[:]
        self.plist = person.getAddressList()[:]

        self.death = Event(person.getDeath())
        self.birth = Event(person.getBirth())
        self.pname = Name(person.getPrimaryName())
        self.selected_icon = -1

        # Typing CR selects OK button
        self.window.editable_enters(self.notes_field);
        self.window.editable_enters(self.given);
        self.window.editable_enters(self.surname_field);
        self.window.editable_enters(self.suffix);
        self.window.editable_enters(self.title);
        self.window.editable_enters(self.nick);
        self.window.editable_enters(self.bdate);
        self.window.editable_enters(self.bplace);
        self.window.editable_enters(self.ddate);
        self.window.editable_enters(self.dplace);
        
        self.top.signal_autoconnect({
            "destroy_passed_object"     : on_cancel_edit,
            "on_add_address_clicked"    : on_add_addr_clicked,
            "on_add_aka_clicked"        : on_add_aka_clicked,
            "on_add_attr_clicked"       : on_add_attr_clicked,
            "on_add_url_clicked"        : on_add_url_clicked,
            "on_addphoto_clicked"       : on_add_photo_clicked,
            "on_address_list_select_row": on_addr_list_select_row,
            "on_aka_delete_clicked"     : on_aka_delete_clicked,
            "on_aka_update_clicked"     : on_aka_update_clicked,
            "on_apply_person_clicked"   : on_apply_person_clicked,
            "on_attr_list_select_row"   : on_attr_list_select_row,
            "on_birth_note_clicked"     : on_birth_note_clicked,
            "on_birth_source_clicked"   : on_birth_source_clicked,
            "on_death_note_clicked"     : on_death_note_clicked,
            "on_death_source_clicked"   : on_death_source_clicked,
            "on_delete_address_clicked" : on_delete_addr_clicked,
            "on_delete_attr_clicked"    : on_delete_attr_clicked,
            "on_delete_event"           : on_delete_event,
            "on_delete_url_clicked"     : on_delete_url_clicked,
            "on_deletephoto_clicked"    : on_delete_photo_clicked,
            "on_editperson_switch_page" : on_switch_page,
            "on_event_add_clicked"      : on_event_add_clicked,
            "on_event_delete_clicked"   : on_event_delete_clicked,
            "on_event_select_row"       : on_event_select_row,
            "on_event_update_clicked"   : on_event_update_clicked,
            "on_makeprimary_clicked"    : on_primary_photo_clicked,
            "on_name_list_select_row"   : on_name_list_select_row,
            "on_name_note_clicked"      : on_name_note_clicked,
            "on_name_source_clicked"    : on_primary_name_source_clicked,
            "on_photolist_button_press_event" : on_photolist_button_press,
            "on_photolist_select_icon"  : on_photo_select_icon,
            "on_update_address_clicked" : on_update_addr_clicked,
            "on_update_attr_clicked"    : on_update_attr_clicked,
            "on_update_url_clicked"     : on_update_url_clicked,
            "on_web_go_clicked"         : on_web_go_clicked,
            "on_web_list_select_row"    : on_web_list_select_row,
            })

        if len(const.surnames) > 0:
            const.surnames.sort()
            self.get_widget("lastNameList").set_popdown_strings(const.surnames)

        self.gid.set_text(person.getId())
        self.gid.set_editable(Config.id_edit)
        self.event_list.set_column_visibility(3,Config.show_detail)
        self.name_list.set_column_visibility(1,Config.show_detail)
        self.attr_list.set_column_visibility(2,Config.show_detail)
        self.addr_list.set_column_visibility(2,Config.show_detail)

        plist = self.db.getPlaceMap().values()
        if len(plist) > 0:
            utils.attach_places(plist,self.dpcombo,self.death.getPlace())
            utils.attach_places(plist,self.bpcombo,self.birth.getPlace())

        if Config.display_attr:
            self.get_widget("user_label").set_text(Config.attr_name)
            val = ""
            for attr in self.person.getAttributeList():
                if attr.getType() == const.save_pattr(Config.attr_name):
                    val = attr.getValue()
                    break
            self.get_widget("user_data").set_text(val)
            self.get_widget("user_colon").show()
        else:
            self.get_widget("user_label").hide()
            self.get_widget("user_colon").hide()
            self.get_widget("user_data").hide()

        # initial values
        self.get_widget("activepersonTitle").set_text(Config.nameof(person))
        self.suffix.set_text(self.pname.getSuffix())

        self.surname_field.set_text(self.pname.getSurname())
        self.given.set_text(self.pname.getFirstName())

        if person.getGender() == Person.male:
            self.is_male.set_active(1)
        else:
            self.is_female.set_active(1)

        self.nick.set_text(person.getNickName())
        self.title.set_text(self.pname.getTitle())
        self.bdate.set_text(self.birth.getDate())
        self.bplace.set_text(self.birth.getPlaceName())
        self.ddate.set_text(self.death.getDate())
        self.dplace.set_text(self.death.getPlaceName())
        
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
        self.addr_list.set_data(EDITPERSON,self)
        self.addr_list.set_data(INDEX,-1)

        # draw lists
        self.redraw_event_list()
        self.redraw_attr_list()
        self.redraw_addr_list()
        self.redraw_name_list()
        self.redraw_url_list()

    #---------------------------------------------------------------------
    #
    # get_widget - returns the widget related to the passed string
    #
    #---------------------------------------------------------------------
    def get_widget(self,str):
        return self.top.get_widget(str)

    #---------------------------------------------------------------------
    #
    # redraw_name_list - redraws the altername name list for the person
    #
    #---------------------------------------------------------------------
    def redraw_name_list(self):
        utils.redraw_list(self.nlist,self.name_list,disp_name)

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
    # redraw_attr_list - redraws the attribute list for the person
    #
    #---------------------------------------------------------------------
    def redraw_attr_list(self):
        utils.redraw_list(self.alist,self.attr_list,disp_attr)

    #---------------------------------------------------------------------
    #
    # redraw_addr_list - redraws the address list for the person
    #
    #---------------------------------------------------------------------
    def redraw_addr_list(self):
        utils.redraw_list(self.plist,self.addr_list,disp_addr)

    #---------------------------------------------------------------------
    #
    # redraw_event_list - redraws the event list for the person
    #
    #---------------------------------------------------------------------
    def redraw_event_list(self):
        utils.redraw_list(self.elist,self.event_list,disp_event)

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
        RelImage.check_thumb(photo.getPath(),thumb,const.thumbScale)
        self.photo_list.append(thumb,photo.getDescription())
        
    #-------------------------------------------------------------------------
    #
    # load_images - add each photo in the person's list of photos to the 
    # photolist window.
    #
    #-------------------------------------------------------------------------
    def load_images(self):
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
        i = GdkImlib.Image(photo)
        scale = float(const.picWidth)/float(max(i.rgb_height,i.rgb_width))
        x = int(scale*(i.rgb_width))
        y = int(scale*(i.rgb_height))
        i = i.clone_scaled_image(x,y)
        self.get_widget("personPix").load_imlib(i)

    #-------------------------------------------------------------------------
    #
    # update_lists - Updates the person's list with the new lists, and sets
    # the modified flag the if the lists have changed
    #
    #-------------------------------------------------------------------------
    def update_lists(self):
        if self.lists_changed:
            self.person.setEventList(self.elist)
            self.person.setAlternateNames(self.nlist)
            self.person.setUrlList(self.ulist)
            self.person.setAttributeList(self.alist)
            self.person.setAddressList(self.plist)
            utils.modified()

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_name(name):
    return [name.getName(),utils.get_detail_flags(name)]

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
def disp_attr(attr):
    detail = utils.get_detail_flags(attr)
    return [const.display_pattr(attr.getType()),attr.getValue(),detail]

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_addr(addr):
    location = "%s %s %s" % (addr.getCity(),addr.getState(),addr.getCountry())
    return [addr.getDate(),location,utils.get_detail_flags(addr)]

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def disp_event(event):
    attr = utils.get_detail_flags(event)
    return [const.display_pevent(event.getName()),
            event.getQuoteDate(),event.getPlaceName(),attr]

#-------------------------------------------------------------------------
#
# did_data_change
#
#-------------------------------------------------------------------------
def did_data_change(obj):
    
    epo = obj.get_data(EDITPERSON)
    person = epo.person
    
    surname = epo.surname_field.get_text()
    suffix = epo.suffix.get_text()
    given = epo.given.get_text()
    nick = epo.nick.get_text()
    title = epo.title.get_text()
    bdate  = epo.bdate.get_text()
    bplace = string.strip(epo.bplace.get_text())
    ddate  = epo.ddate.get_text()
    dplace = epo.dplace.get_text()
    gender = epo.is_male.get_active()
    text = epo.notes_field.get_chars(0,-1)
    idval = epo.gid.get_text()

    changed = 0
    name = person.getPrimaryName()

    if person.getId() != idval:
        changed = 1
    if suffix != name.getSuffix() or surname != name.getSurname():
        changed = 1
    if given != name.getFirstName() or nick != person.getNickName():
        changed = 1
    if title != name.getTitle():
        changed = 1
    if epo.pname.getNote() != name.getNote():
        changed = 1
    if not epo.pname.getSourceRef().are_equal(name.getSourceRef()):
        changed = 1

    epo.birth.setDate(bdate)

    bplace_obj = utils.get_place_from_list(epo.bpcombo)
    if bplace_obj == None and bplace != "":
        changed = 1
    epo.birth.setPlace(bplace_obj)

    if not epo.birth.are_equal(epo.person.getBirth()):
        changed = 1

    epo.death.setDate(ddate)
    dplace_obj = utils.get_place_from_list(epo.dpcombo)
    if dplace_obj == None and dplace != "":
        changed = 1
    epo.death.setPlace(dplace_obj)

    if not epo.death.are_equal(epo.person.getDeath()):
        changed = 1

    if gender and person.getGender() == Person.female:
        changed = 1
    if not gender and person.getGender() == Person.male:
        changed = 1
    if text != person.getNote() or epo.lists_changed:
        changed = 1

    return changed


def on_web_go_clicked(obj):
    import gnome.url

    text = obj.get()
    if text != "":
        gnome.url.show(text)
        
#-------------------------------------------------------------------------
#
# on_cancel_edit
#
#-------------------------------------------------------------------------
def on_cancel_edit(obj):
    global quit

    if did_data_change(obj):
        q = _("Data was modified. Are you sure you want to abandon your changes?")
        quit = obj
        GnomeQuestionDialog(q,cancel_callback)
    else:
        utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def cancel_callback(a):
    if a==0:
        utils.destroy_passed_object(quit)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def on_delete_event(obj,b):
    global quit

    if did_data_change(obj):
        q = _("Data was modified. Are you sure you want to abandon your changes?")
        quit = obj
        GnomeQuestionDialog(q,cancel_callback)
        return 1
    else:
        utils.destroy_passed_object(obj)
        return 0

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
    epo.alt_given_field.set_text(name.getFirstName())
    epo.alt_last_field.set_text(name.getSurname())
    epo.alt_suffix_field.set_text(name.getSuffix())
    epo.name_details_field.set_text(utils.get_detail_text(name))

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
    epo.attr_value.set_text(attr.getValue())
    epo.attr_details_field.set_text(utils.get_detail_text(attr))

#-------------------------------------------------------------------------
#
# on_name_list_select_row - sets the row object attached to the passed
# object, and then updates the display with the data corresponding to
# the row.
#
#-------------------------------------------------------------------------
def on_addr_list_select_row(obj,row,b,c):
    obj.set_data(INDEX,row)

    epo = obj.get_data(EDITPERSON)
    a = obj.get_row_data(row)

    label = "%s %s %s" % (a.getCity(),a.getState(),a.getCountry())
    epo.addr_label.set_label(label)
    epo.addr_start.set_text(a.getDate())
    epo.addr_street.set_text(a.getStreet())
    epo.addr_city.set_text(a.getCity())
    epo.addr_state.set_text(a.getState())
    epo.addr_country.set_text(a.getCountry())
    epo.addr_postal.set_text(a.getPostal())
    epo.addr_details_field.set_text(utils.get_detail_text(a))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_aka_update_clicked(obj):
    row = obj.get_data(INDEX)
    if row >= 0:
        NameEditor(obj.get_data(EDITPERSON),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_url_clicked(obj):
    row = obj.get_data(INDEX)
    if row >= 0:
        UrlEditor(obj.get_data(EDITPERSON),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_attr_clicked(obj):
    row = obj.get_data(INDEX)
    if row >= 0:
        AttributeEditor(obj.get_data(EDITPERSON),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_update_addr_clicked(obj):
    row = obj.get_data(INDEX)
    if row >= 0:
        AddressEditor(obj.get_data(EDITPERSON),obj.get_row_data(row))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_aka_delete_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    if utils.delete_selected(obj,epo.nlist):
        epo.lists_changed = 1
        epo.redraw_name_list()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_url_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    if utils.delete_selected(obj,epo.ulist):
        epo.lists_changed = 1
        epo.redraw_url_list()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_attr_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    if utils.delete_selected(obj,epo.alist):
        epo.lists_changed = 1
        epo.redraw_attr_list()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_addr_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    if utils.delete_selected(obj,epo.plist):
        epo.lists_changed = 1
        epo.redraw_addr_list()

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
    if utils.delete_selected(obj,epo.elist):
        epo.lists_changed = 1
        epo.redraw_event_list()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_aka_clicked(obj):
    NameEditor(obj.get_data(EDITPERSON),None)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_add_url_clicked(obj):
    UrlEditor(obj.get_data(EDITPERSON),None)

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
def on_add_addr_clicked(obj):
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
    EventEditor(obj.get_data(EDITPERSON),None)

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
    if row >= 0:
        EventEditor(obj.get_data(EDITPERSON),obj.get_row_data(row))

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
    epo.event_date_field.set_text(event.getDate())
    epo.event_place_field.set_text(event.getPlaceName())
    epo.event_name_field.set_label(const.display_pevent(event.getName()))
    epo.event_descr_field.set_text(event.getDescription())
    epo.event_details_field.set_text(utils.get_detail_text(event))

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
    obj.get_data(EDITPERSON).selected_icon = iconNumber

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_delete_photo_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    icon = epo.selected_icon

    if icon != -1:
        epo.photo_list.remove(icon)
        del epo.person.getPhotoList()[icon]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_primary_photo_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    if epo.selected_icon == None or epo.selected_icon == 0:
        return

    photolist = epo.person.getPhotoList()
    selected_icon = epo.selected_icon
    savePhoto = photolist[selected_icon]
    for i in range(0,selected_icon):
        photolist[selected_icon-i] = photolist[selected_icon-i-1]
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

    if addr.getStreet() != street:
        addr.setStreet(street)
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
    window = image_select.get_widget("imageSelect")

    image_select.signal_autoconnect({
        "on_savephoto_clicked" : on_savephoto_clicked,
        "on_name_changed" : on_name_changed,
        "destroy_passed_object" : utils.destroy_passed_object
        })

    edit_person.fname = image_select.get_widget("fname")
    edit_person.add_image = image_select.get_widget("image")
    edit_person.external = image_select.get_widget("private")
    window.editable_enters(image_select.get_widget("photoDescription"))
    window.set_data(EDITPERSON,edit_person)
    window.show()

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
    save_person(obj)
    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def save_person(obj):
    epo = obj.get_data(EDITPERSON)
    person = epo.person
    
    surname = epo.surname_field.get_text()
    suffix = epo.suffix.get_text()
    given = epo.given.get_text()
    nick = epo.nick.get_text()
    title = epo.title.get_text()
    idval = epo.gid.get_text()

    name = epo.pname

    if idval != person.getId():
        m = epo.db.getPersonMap() 
        if not m.has_key(idval):
            if m.has_key(person.getId()):
                del m[person.getId()]
                m[idval] = person
            person.setId(idval)
        else:
            n = Config.nameof(m[idval])
            msg1 = _("GRAMPS ID value was not changed.")
            msg2 = _("%s is already used by %s") % (idval,n)
            GnomeWarningDialog("%s\n%s" % (msg1,msg2))

    if suffix != name.getSuffix():
        name.setSuffix(suffix)

    if surname != name.getSurname():
        name.setSurname(surname)
        if surname not in const.surnames:
            const.surnames.append(surname)
            const.surnames.sort()

    if given != name.getFirstName():
        name.setFirstName(given)

    if title != name.getTitle():
        name.setTitle(title)

    if not name.are_equal(epo.person.getPrimaryName()):
        epo.person.setPrimaryName(name)
        utils.modified()

    if nick != person.getNickName():
        person.setNickName(nick)
        utils.modified()

    bplace = string.strip(epo.bplace.get_text())
    dplace = string.strip(epo.dplace.get_text())
    
    epo.birth.setDate(epo.bdate.get_text())

    p1 = utils.get_place_from_list(epo.bpcombo)
    if p1 == None and bplace != "":
        p1 = Place()
        p1.set_title(bplace)
        epo.db.addPlace(p1)
    epo.birth.setPlace(p1)
    if not person.getBirth().are_equal(epo.birth):
        person.setBirth(epo.birth)
    
    epo.death.setDate(epo.ddate.get_text())

    p2 = utils.get_place_from_list(epo.dpcombo)
    if p2 == None and dplace != "":
        p2 = Place()
        p2.set_title(dplace)
        epo.db.addPlace(p2)
    epo.death.setPlace(p2)
    if not person.getDeath().are_equal(epo.death):
        person.setDeath(epo.death)

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

    epo.update_lists()
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
            thumb = "%s%s.thumb.jpg" % (path,os.sep,os.path.basename(filename))
            RelImage.mk_thumb(filename,thumb,const.thumbScale)
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
    textbox = obj.get_data(TEXTOBJ)
    data = obj.get_data(NOTEOBJ)

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
def display_note(obj,data):
    editnote = libglade.GladeXML(const.editnoteFile,"editnote")
    textobj = editnote.get_widget("notetext")
    en_obj = editnote.get_widget("editnote")
    en_obj.set_data(NOTEOBJ,data)
    en_obj.set_data(TEXTOBJ,textobj)
    en_obj.editable_enters(textobj);

    textobj.set_point(0)
    textobj.insert_defaults(data.getNote())
    textobj.set_word_wrap(1)
        
    editnote.signal_autoconnect({
        "on_save_note_clicked"  : on_save_note_clicked,
        "destroy_passed_object" : utils.destroy_passed_object
    })
    
#-------------------------------------------------------------------------
#
# Display the note editor for the birth event
#
#-------------------------------------------------------------------------
def on_birth_note_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    display_note(obj,epo.birth)

#-------------------------------------------------------------------------
#
# Display the note editor for the name event
#
#-------------------------------------------------------------------------
def on_name_note_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    display_note(obj,epo.pname)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_death_note_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    display_note(obj,epo.death)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_death_source_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    Sources.SourceEditor(epo.death.getSourceRef(),epo.db)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_primary_name_source_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    Sources.SourceEditor(epo.pname.getSourceRef(),epo.db)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_birth_source_clicked(obj):
    epo = obj.get_data(EDITPERSON)
    Sources.SourceEditor(epo.birth.getSourceRef(),epo.db)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_photolist_button_press(obj,event):
    myobj = obj.get_data(EDITPERSON)
    icon = myobj.selected_icon
    if icon == -1:
        return
    
    if event.button == 3:
        photo = myobj.person.getPhotoList()[icon]
        menu = GtkMenu()
        item = GtkTearoffMenuItem()
        item.show()
        menu.append(item)
        utils.add_menuitem(menu,_("View Image"),myobj,on_view_photo)
        utils.add_menuitem(menu,_("Edit Image"),myobj,on_edit_photo)
        utils.add_menuitem(menu,_("Edit Description"),myobj,
                           on_change_description)
        if photo.getPrivate() == 0:
            utils.add_menuitem(menu,_("Convert to private copy"),
                               myobj, on_convert_to_private)
        menu.popup(None,None,None,0,0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_convert_to_private(obj):
    epo = obj.get_data(OBJECT)
    photo = epo.person.getPhotoList()[epo.selected_icon]

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
    myobj = obj.get_data(OBJECT)
    photo = myobj.person.getPhotoList()[myobj.selected_icon]
    utils.view_photo(photo)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_photo(obj):
    myobj = obj.get_data(OBJECT)
    photo = myobj.person.getPhotoList()[myobj.selected_icon]
    if os.fork() == 0:
        os.execvp(const.editor,[const.editor, photo.getPath()])

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_change_description(obj):
    myobj = obj.get_data(OBJECT)
    photo = myobj.person.getPhotoList()[myobj.selected_icon]
    window = libglade.GladeXML(const.imageselFile,"dialog1")

    text = window.get_widget("text")
    text.set_text(photo.getDescription())

    image2 = RelImage.scale_image(photo.getPath(),200.0)
    window.get_widget("photo").load_imlib(image2)
    window.get_widget("dialog1").set_data(PHOTO,photo)
    window.get_widget("dialog1").set_data(TEXT,text)
    window.get_widget("dialog1").set_data(OBJECT,obj.get_data(OBJECT))
    window.get_widget("dialog1").editable_enters(text)
    window.signal_autoconnect({
        "on_cancel_clicked" : utils.destroy_passed_object,
        "on_ok_clicked"     : on_ok_clicked,
        "on_apply_clicked"  : on_apply_clicked
        })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_apply_clicked(obj):
    photo = obj.get_data(PHOTO)
    text = obj.get_data(TEXT).get_text()
    if text != photo.getDescription():
        photo.setDescription(text)
        obj.get_data(OBJECT).load_images()
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
# EventEditor class
#
#-------------------------------------------------------------------------
class EventEditor:

    def __init__(self,parent,event):
        self.parent = parent
        self.event = event
        if self.event:
            self.srcref = SourceRef(self.event.getSourceRef())
        else:
            self.srcref = SourceRef()
        self.top = libglade.GladeXML(const.dialogFile, "event_edit")
        self.window = self.top.get_widget("event_edit")
        self.name_field  = self.top.get_widget("eventName")
        self.place_field = self.top.get_widget("eventPlace")
        self.place_combo = self.top.get_widget("eventPlace_combo")
        self.date_field  = self.top.get_widget("eventDate")
        self.descr_field = self.top.get_widget("eventDescription")
        self.note_field = self.top.get_widget("eventNote")
        self.event_menu = self.top.get_widget("personalEvents")
        self.source_field = self.top.get_widget("event_source")
        self.conf_menu = self.top.get_widget("conf")
        self.priv = self.top.get_widget("priv")
        
        name = parent.person.getPrimaryName().getName()
        title = _("Event Editor for %s") % name 
        self.top.get_widget("eventTitle").set_text(title)
        self.event_menu.set_popdown_strings(const.personalEvents)

        # Typing CR selects OK button
        self.window.editable_enters(self.name_field);
        self.window.editable_enters(self.place_field);
        self.window.editable_enters(self.date_field);
        self.window.editable_enters(self.descr_field);

        utils.build_confidence_menu(self.conf_menu)

        values = self.parent.db.getPlaceMap().values()
        if event != None:
            self.name_field.set_text(event.getName())

            utils.attach_places(values,self.place_combo,event.getPlace())
            self.place_field.set_text(event.getPlaceName())
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
            utils.attach_places(values,self.place_combo,None)
            self.conf_menu.set_history(2)

        self.window.set_data(OBJECT,self)
        self.top.signal_autoconnect({
            "destroy_passed_object"    : utils.destroy_passed_object,
            "on_event_edit_ok_clicked" : on_event_edit_ok_clicked,
            "on_source_clicked"        : on_edit_source_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_edit_source_clicked(obj):
    ee = obj.get_data(OBJECT)
    Sources.SourceEditor(ee.srcref,ee.parent.db,ee.source_field)
            
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_event_edit_ok_clicked(obj):
    ee = obj.get_data(OBJECT)
    event = ee.event

    ename = ee.name_field.get_text()
    edate = ee.date_field.get_text()
    eplace = string.strip(ee.place_field.get_text())
    eplace_obj = utils.get_place_from_list(ee.place_combo)
    enote = ee.note_field.get_chars(0,-1)
    edesc = ee.descr_field.get_text()
    epriv = ee.priv.get_active()
    econf = ee.conf_menu.get_menu().get_active().get_data(MENUVAL)

    if event == None:
        event = Event()
        ee.parent.elist.append(event)

    if eplace_obj == None and eplace != "":
        eplace_obj = Place()
        eplace_obj.set_title(eplace)
        ee.parent.db.addPlace(eplace_obj)
        
    if update_event(event,ename,edate,eplace_obj,edesc,enote,epriv,econf):
        ee.parent.lists_changed = 1
        
    if not event.getSourceRef().are_equal(ee.srcref):
        event.setSourceRef(ee.srcref)
        ee.parent.lists_changed = 1
        
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
        if self.attrib:
            self.srcref = SourceRef(self.attrib.getSourceRef())
        else:
            self.srcref = SourceRef()

        # Typing CR selects OK button
        self.window.editable_enters(self.type_field);
        self.window.editable_enters(self.value_field);

        name = parent.person.getPrimaryName().getName()
        
        self.top.get_widget("attrTitle").set_text(_("Attribute Editor for %s") % name) 
        self.attrib_menu.set_popdown_strings(const.personalAttributes)

        myMenu = GtkMenu()
        index = 0
        for name in const.confidence:
            item = GtkMenuItem(name)
            item.set_data(MENUVAL,index)
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

        self.window.set_data(OBJECT,self)
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
    ee = obj.get_data(OBJECT)
    Sources.SourceEditor(ee.srcref,ee.parent.db,ee.source_field)
            
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_attrib_edit_ok_clicked(obj):
    ee = obj.get_data(OBJECT)
    attrib = ee.attrib

    type = ee.type_field.get_text()
    value = ee.value_field.get_text()
    note = ee.note_field.get_chars(0,-1)
    priv = ee.priv.get_active()
    conf = ee.conf_menu.get_menu().get_active().get_data(MENUVAL)

    if attrib == None:
        attrib = Attribute()
        ee.parent.alist.append(attrib)
        
    if update_attrib(attrib,type,value,note,priv,conf):
        ee.parent.lists_changed = 1
        
    if not attrib.getSourceRef().are_equal(ee.srcref):
        attrib.setSourceRef(ee.srcref)
        ee.parent.lists_changed = 1

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
        if self.name:
            self.srcref = SourceRef(self.name.getSourceRef())
        else:
            self.srcref = SourceRef()

        full_name = parent.person.getPrimaryName().getName()
        
        self.top.get_widget("altTitle").set_text(
            _("Alternate Name Editor for %s") % full_name)

        # Typing CR selects OK button
        self.window.editable_enters(self.given_field);
        self.window.editable_enters(self.surname_field);
        self.window.editable_enters(self.suffix_field);
        
        utils.build_confidence_menu(self.conf_menu)

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

        self.window.set_data(OBJECT,self)
        self.top.signal_autoconnect({
            "destroy_passed_object"   : utils.destroy_passed_object,
            "on_name_edit_ok_clicked" : on_name_edit_ok_clicked,
            "on_source_clicked"       : on_name_source_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_name_source_clicked(obj):
    ee = obj.get_data(OBJECT)
    Sources.SourceEditor(ee.srcref,ee.parent.db,ee.source_field)
            
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_name_edit_ok_clicked(obj):
    ee = obj.get_data(OBJECT)
    name = ee.name

    first = ee.given_field.get_text()
    last = ee.surname_field.get_text()
    suffix = ee.suffix_field.get_text()
    note = ee.note_field.get_chars(0,-1)
    priv = ee.priv.get_active()
    conf = ee.conf_menu.get_menu().get_active().get_data(MENUVAL)

    if name == None:
        name = Name()
        ee.parent.nlist.append(name)
        
    if update_name(name,first,last,suffix,note,priv,conf):
        ee.parent.lists_changed = 1

    if not name.getSourceRef().are_equal(ee.srcref):
        name.setSourceRef(ee.srcref)
        ee.parent.lists_changed = 1

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
        self.addr_start  = self.top.get_widget("address_start")
        self.street = self.top.get_widget("street")
        self.city = self.top.get_widget("city")
        self.state = self.top.get_widget("state")
        self.country = self.top.get_widget("country")
        self.postal = self.top.get_widget("postal")
        self.note_field = self.top.get_widget("addr_note")
        self.source_field = self.top.get_widget("addr_source")
        self.conf_menu = self.top.get_widget("conf")
        self.priv = self.top.get_widget("priv")
        if self.addr:
            self.srcref = SourceRef(self.addr.getSourceRef())
        else:
            self.srcref = SourceRef()

        name = parent.person.getPrimaryName().getName()
        text = _("Address Editor for %s") % name
        self.top.get_widget("addrTitle").set_text(text)

        # Typing CR selects OK button
        self.window.editable_enters(self.addr_start);
        self.window.editable_enters(self.street);
        self.window.editable_enters(self.city);
        self.window.editable_enters(self.state);
        self.window.editable_enters(self.country);
        self.window.editable_enters(self.postal);
        self.window.editable_enters(self.source_field);
        self.window.editable_enters(self.note_field);
        
        utils.build_confidence_menu(self.conf_menu)

        if addr != None:
            self.street.set_text(addr.getStreet())
            self.city.set_text(addr.getCity())
            self.state.set_text(addr.getState())
            self.country.set_text(addr.getCountry())
            self.postal.set_text(addr.getPostal())
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

        self.window.set_data(OBJECT,self)
        self.top.signal_autoconnect({
            "destroy_passed_object"   : utils.destroy_passed_object,
            "on_addr_edit_ok_clicked" : on_addr_edit_ok_clicked,
            "on_source_clicked"       : on_addr_source_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_addr_source_clicked(obj):
    ee = obj.get_data(OBJECT)
    Sources.SourceEditor(ee.srcref,ee.parent.db,ee.source_field)
            
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_addr_edit_ok_clicked(obj):
    ee = obj.get_data(OBJECT)
    addr = ee.addr

    date = ee.addr_start.get_text()
    street = ee.street.get_text()
    city = ee.city.get_text()
    state = ee.state.get_text()
    country = ee.country.get_text()
    postal = ee.postal.get_text()
    note = ee.note_field.get_chars(0,-1)
    priv = ee.priv.get_active()
    conf = ee.conf_menu.get_menu().get_active().get_data(MENUVAL)

    if addr == None:
        addr = Address()
        ee.parent.plist.append(addr)
        
    if update_address(addr,date,street,city,state,country,postal,note,priv,conf):
        ee.parent.lists_changed = 1
        
    if not addr.getSourceRef().are_equal(ee.srcref):
        addr.setSourceRef(ee.srcref)
        ee.parent.lists_changed = 1

    ee.parent.redraw_addr_list()
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
        title = _("Internet Address Editor for %s") % name
        self.top.get_widget("urlTitle").set_text(title) 

        self.window.editable_enters(self.url_addr);
        self.window.editable_enters(self.url_des);
        
        if url != None:
            self.des.set_text(url.get_description())
            self.addr.set_text(url.get_path())
            self.priv.set_active(url.getPrivacy())

        self.window.set_data(OBJECT,self)
        self.top.signal_autoconnect({
            "destroy_passed_object"  : utils.destroy_passed_object,
            "on_url_edit_ok_clicked" : on_url_edit_ok_clicked
            })

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_url_edit_ok_clicked(obj):
    ee = obj.get_data(OBJECT)
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

