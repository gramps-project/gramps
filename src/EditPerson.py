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
import string

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
from gnome.ui import GnomeErrorDialog, GnomeWarningDialog, GnomeQuestionDialog
import libglade
import GdkImlib
import GDK

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import utils
import Config
from RelLib import *
import ImageSelect
import sort

from intl import gettext
_ = gettext

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
        self.update_birth = 0
        self.update_death = 0
        pid = "i%s" % person.getId()

        self.load_obj = None
        self.top = libglade.GladeXML(const.editPersonFile, "editPerson")
        self.gallery_widget = self.top.get_widget("photolist")
        self.gallery = ImageSelect.Gallery(person, self.path, pid, self.gallery_widget, self.db)
        self.top.signal_autoconnect({
            "destroy_passed_object"     : self.on_cancel_edit,
            "on_add_address_clicked"    : self.on_add_addr_clicked,
            "on_add_aka_clicked"        : self.on_add_aka_clicked,
            "on_add_attr_clicked"       : self.on_add_attr_clicked,
            "on_add_url_clicked"        : self.on_add_url_clicked,
            "on_addr_button_press"      : self.addr_double_click,
            "on_web_button_press"       : self.url_double_click,
            "on_addphoto_clicked"       : self.gallery.on_add_photo_clicked,
            "on_address_list_select_row": self.on_addr_list_select_row,
            "on_aka_delete_clicked"     : self.on_aka_delete_clicked,
            "on_aka_update_clicked"     : self.on_aka_update_clicked,
            "on_apply_person_clicked"   : self.on_apply_person_clicked,
            "on_attr_button_press"      : self.attr_double_click,
            "on_attr_list_select_row"   : self.on_attr_list_select_row,
            "on_combo_insert_text"      : utils.combo_insert_text,
            "on_edit_birth_clicked"     : self.on_edit_birth_clicked,
            "on_edit_death_clicked"     : self.on_edit_death_clicked,
            "on_delete_address_clicked" : self.on_delete_addr_clicked,
            "on_delete_attr_clicked"    : self.on_delete_attr_clicked,
            "on_delete_event"           : self.on_delete_event,
            "on_delete_url_clicked"     : self.on_delete_url_clicked,
            "on_deletephoto_clicked"    : self.gallery.on_delete_photo_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_editperson_switch_page" : self.on_switch_page,
            "on_event_add_clicked"      : self.on_event_add_clicked,
            "on_event_button_press"     : self.event_double_click,
            "on_event_delete_clicked"   : self.on_event_delete_clicked,
            "on_event_select_row"       : self.on_event_select_row,
            "on_event_update_clicked"   : self.on_event_update_clicked,
            "on_name_button_press"      : self.aka_double_click,
            "on_name_list_select_row"   : self.on_name_list_select_row,
            "on_name_note_clicked"      : self.on_name_note_clicked,
            "on_name_source_clicked"    : self.on_primary_name_source_clicked,
            "on_photolist_button_press_event" : self.gallery.on_photolist_button_press_event,
            "on_photolist_select_icon"  : self.gallery.on_photo_select_icon,
            "on_update_address_clicked" : self.on_update_addr_clicked,
            "on_update_attr_clicked"    : self.on_update_attr_clicked,
            "on_update_url_clicked"     : self.on_update_url_clicked,
            "on_web_go_clicked"         : self.on_web_go_clicked,
            "on_web_list_select_row"    : self.on_web_list_select_row,
            })

        self.window = self.get_widget("editPerson")
        self.notes_field = self.get_widget("personNotes")
        self.event_name_field  = self.get_widget("eventName")
        self.event_place_field = self.get_widget("eventPlace")
        self.event_cause_field = self.get_widget("eventCause")
        self.event_date_field  = self.get_widget("eventDate")
        self.event_descr_field = self.get_widget("eventDescription")
        self.event_details_field = self.get_widget("event_details")
        self.attr_details_field = self.get_widget("attr_details")
        self.name_details_field = self.get_widget("name_details")
        self.addr_details_field = self.get_widget("addr_details")
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
        self.bpcombo = self.get_widget("bpcombo")
        self.ddate  = self.get_widget("deathDate")
        self.dplace = self.get_widget("deathPlace")
        self.dpcombo = self.get_widget("dpcombo")
        self.is_male = self.get_widget("genderMale")
        self.is_female = self.get_widget("genderFemale")
        self.is_unknown = self.get_widget("genderUnknown")
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
        
        utils.attach_surnames(self.get_widget("lastNameList"))

        self.gid.set_text(person.getId())
        self.gid.set_editable(Config.id_edit)
        self.event_list.set_column_visibility(3,Config.show_detail)
        self.name_list.set_column_visibility(1,Config.show_detail)
        self.attr_list.set_column_visibility(2,Config.show_detail)
        self.addr_list.set_column_visibility(2,Config.show_detail)

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
        elif person.getGender() == Person.female:
            self.is_female.set_active(1)
        else:
            self.is_unknown.set_active(1)

        self.nick.set_text(person.getNickName())
        self.title.set_text(self.pname.getTitle())
        self.update_birth_death()

        self.load_person_image()
        
        # set notes data
        self.notes_field.set_point(0)
        self.notes_field.insert_defaults(person.getNote())
        self.notes_field.set_word_wrap(1)


        # draw lists
        self.redraw_event_list()
        self.redraw_attr_list()
        self.redraw_addr_list()
        self.redraw_name_list()
        self.redraw_url_list()
        self.window.show()

    def get_widget(self,str):
        """returns the widget related to the passed string"""
        return self.top.get_widget(str)

    def redraw_name_list(self):
        """redraws the name list"""
        utils.redraw_list(self.nlist,self.name_list,disp_name)

    def redraw_url_list(self):
        """redraws the url list, disabling the go button if no url is selected"""
        length = utils.redraw_list(self.ulist,self.web_list,disp_url)
        if length > 0:
            self.web_go.set_sensitive(1)
        else:
            self.web_go.set_sensitive(0)
            self.web_url.set_text("")
            self.web_description.set_text("")

    def redraw_attr_list(self):
        """Redraws the attribute list"""
        utils.redraw_list(self.alist,self.attr_list,disp_attr)

    def redraw_addr_list(self):
        """redraws the address list for the person"""
        utils.redraw_list(self.plist,self.addr_list,disp_addr)

    #---------------------------------------------------------------------
    #
    # redraw_event_list - Update both the birth and death place combo
    # boxes for any changes that occurred in the 'Event Edit' window.
    # Make sure not to allow the editing of a birth event to change
    # any values in the death event, and vice versa.  Since updating a
    # combo list resets its present value, this code will have to save
    # and restore the value for the event *not* being edited.
    #
    #---------------------------------------------------------------------
    def redraw_event_list(self):
        """redraws the event list for the person"""
        utils.redraw_list(self.elist,self.event_list,disp_event)

        # Remember old combo list input
        prev_btext = self.bpcombo.entry.get_text()
        prev_dtext = self.dpcombo.entry.get_text()

        # Update combo lists to add in any new places
        plist = self.db.getPlaceMap().values()
        if len(plist) > 0:
            utils.attach_places(plist,self.dpcombo,self.death.getPlace())
            utils.attach_places(plist,self.bpcombo,self.birth.getPlace())

        # Update birth with new values, make sure death values don't change
        if (self.update_birth):
            self.update_birth = 0
            self.bdate.set_text(self.birth.getDate())
            self.bplace.set_text(self.birth.getPlaceName())
            self.dplace.set_text(prev_dtext)

        # Update death with new values, make sure birth values don't change
        if (self.update_death):
            self.update_death = 0
            self.ddate.set_text(self.death.getDate())
            self.dplace.set_text(self.death.getPlaceName())
            self.bplace.set_text(prev_btext)

    def on_add_addr_clicked(self,obj):
        """Invokes the address editor to add a new address"""
        import AddrEdit
        AddrEdit.AddressEditor(self,None)

    def on_add_aka_clicked(self,obj):
        """Invokes the name editor to add a new name"""
        import NameEdit
        NameEdit.NameEditor(self,None)

    def on_add_url_clicked(self,obj):
        """Invokes the url editor to add a new name"""
        import UrlEdit
        pname = self.person.getPrimaryName().getName()
        UrlEdit.UrlEditor(self,pname,None)

    def on_add_attr_clicked(self,obj):
        """Brings up the AttributeEditor for a new attribute"""
        import AttrEdit
        pname = self.person.getPrimaryName().getName()
        AttrEdit.AttributeEditor(self,None,pname,const.personalAttributes)

    def on_event_add_clicked(self,obj):
        """Brings up the EventEditor for a new event"""
        import EventEdit
        pname = self.person.getPrimaryName().getName()
        EventEdit.EventEditor(self,pname,const.personalEvents,const.save_fevent,None,None,0)

    def on_edit_birth_clicked(self,obj):
        """Brings up the EventEditor for the birth record, event name cannot be changed"""
        import EventEdit
        self.update_birth = 1
        pname = self.person.getPrimaryName().getName()
        event = self.birth
        event.setDate(self.bdate.get_text())
        p = utils.get_place_from_list(self.bpcombo)
        if p != None:
            event.setPlace(p)
            def_placename = None
        else:
            def_placename = self.bpcombo.entry.get_text()
        EventEdit.EventEditor(self,pname,const.personalEvents,\
                              const.save_fevent,event,def_placename,1)

    def on_edit_death_clicked(self,obj):
        """Brings up the EventEditor for the death record, event name cannot be changed"""
        import EventEdit
        self.update_death = 1
        pname = self.person.getPrimaryName().getName()
        event = self.death
        event.setDate(self.ddate.get_text())
        p = utils.get_place_from_list(self.dpcombo)
        if p != None:
            event.setPlace(p)
            def_placename = None
        else:
            def_placename = self.dpcombo.entry.get_text()
        EventEdit.EventEditor(self,pname,const.personalEvents,\
                              const.save_fevent,event,def_placename,1)

    def on_aka_delete_clicked(self,obj):
        """Deletes the selected name from the name list"""
        if utils.delete_selected(obj,self.nlist):
            self.lists_changed = 1
            self.redraw_name_list()

    def on_delete_url_clicked(self,obj):
        """Deletes the selected URL from the URL list"""
        if utils.delete_selected(obj,self.ulist):
            self.lists_changed = 1
            self.redraw_url_list()

    def on_delete_attr_clicked(self,obj):
        """Deletes the selected attribute from the attribute list"""
        if utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_delete_addr_clicked(self,obj):
        """Deletes the selected address from the address list"""
        if utils.delete_selected(obj,self.plist):
            self.lists_changed = 1
            self.redraw_addr_list()

    def on_web_go_clicked(self,obj):
        """Attempts to display the selected URL in a web browser"""
        import gnome.url

        text = obj.get()
        if text != "":
            gnome.url.show(text)
        
    def on_cancel_edit(self,obj):
        """If the data has changed, give the user a chance to cancel the close window"""
        if self.did_data_change():
            q = _("Are you sure you want to abandon your changes?")
            GnomeQuestionDialog(q,self.cancel_callback)
        else:
            utils.destroy_passed_object(obj)

    def on_delete_event(self,obj,b):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        if self.did_data_change():
            q = _("Are you sure you want to abandon your changes?")
            GnomeQuestionDialog(q,self.cancel_callback)
            return 1
        else:
            utils.destroy_passed_object(obj)
            return 0
    
    def cancel_callback(self,a):
        """If the user answered yes to abandoning changes, close the window"""
        if a==0:
            utils.destroy_passed_object(self.window)

    def did_data_change(self):
        """Check to see if any of the data has changed from the original record"""
        surname = self.surname_field.get_text()
        suffix = self.suffix.get_text()
        given = self.given.get_text()
        nick = self.nick.get_text()
        title = self.title.get_text()
        male = self.is_male.get_active()
        female = self.is_female.get_active()
        unknown = self.is_unknown.get_active()
        text = self.notes_field.get_chars(0,-1)
        idval = self.gid.get_text()

        changed = 0
        name = self.person.getPrimaryName()

        if self.person.getId() != idval:
            changed = 1
        if suffix != name.getSuffix() or surname != name.getSurname():
            changed = 1
        if given != name.getFirstName() or nick != self.person.getNickName():
            changed = 1
        if title != name.getTitle():
            changed = 1
        if self.pname.getNote() != name.getNote():
            changed = 1

        bplace = string.strip(self.bplace.get_text())
        dplace = string.strip(self.dplace.get_text())

        p1 = utils.get_place_from_list(self.bpcombo)
        if p1 == None and bplace != "":
            changed = 1
        self.birth.setPlace(p1)

        p1 = utils.get_place_from_list(self.dpcombo)
        if p1 == None and dplace != "":
            changed = 1
        self.death.setPlace(p1)

        if not self.birth.are_equal(self.person.getBirth()):
            changed = 1

        if not self.death.are_equal(self.person.getDeath()):
            changed = 1

        if male and self.person.getGender() != Person.male:
            changed = 1
        elif female and self.person.getGender() != Person.female:
            changed = 1
        elif unknown and self.person.getGender() != Person.unknown:
            changed = 1
        if text != self.person.getNote() or self.lists_changed:
            changed = 1

        return changed

    def on_event_delete_clicked(self,obj):
        """Delete the selected event"""
        if utils.delete_selected(obj,self.elist):
            self.lists_changed = 1
            self.redraw_event_list()

    def update_birth_death(self):
        self.bdate.set_text(self.birth.getDate())
        self.bplace.set_text(self.birth.getPlaceName())
        self.ddate.set_text(self.death.getDate())
        self.dplace.set_text(self.death.getPlaceName())
        self.dplace.set_text(self.death.getPlaceName())
        self.bdate.set_position(0)
        self.ddate.set_position(0)
        self.bplace.set_position(0)
        self.dplace.set_position(0)

    def attr_double_click(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            self.on_update_attr_clicked(obj)

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        if len(obj.selection) <= 0:
            return
        attr = obj.get_row_data(obj.selection[0])
        pname = self.person.getPrimaryName().getName()
        AttrEdit.AttributeEditor(self,attr,pname,const.personalAttributes)

    def addr_double_click(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            self.on_update_addr_clicked(obj)

    def on_update_addr_clicked(self,obj):
        import AddrEdit
        if len(obj.selection) > 0:
            AddrEdit.AddressEditor(self,obj.get_row_data(obj.selection[0]))

    def url_double_click(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            self.on_update_url_clicked(obj)

    def on_update_url_clicked(self,obj):
        import UrlEdit
        if len(obj.selection) <= 0:
            return
        pname = self.person.getPrimaryName().getName()
        url = obj.get_row_data(obj.selection[0])
        UrlEdit.UrlEditor(self,pname,url)

    def event_double_click(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            self.on_event_update_clicked(obj)
        
    def on_event_update_clicked(self,obj):
        import EventEdit
        if len(obj.selection) <= 0:
            return
        pname = self.person.getPrimaryName().getName()
        event = obj.get_row_data(obj.selection[0])
        EventEdit.EventEditor(self,pname,const.personalEvents,const.save_fevent,event,None,0)

    def on_event_select_row(self,obj,row,b,c):
        event = obj.get_row_data(row)
        self.event_date_field.set_text(event.getDate())
        self.event_place_field.set_text(event.getPlaceName())
        self.event_name_field.set_label(const.display_pevent(event.getName()))
        self.event_cause_field.set_text(event.getCause())
        self.event_descr_field.set_text(event.getDescription())
        self.event_details_field.set_text(utils.get_detail_text(event))

    def on_addr_list_select_row(self,obj,row,b,c):

        a = obj.get_row_data(row)

        label = "%s %s %s" % (a.getCity(),a.getState(),a.getCountry())
        self.addr_label.set_label(label)
        self.addr_start.set_text(a.getDate())
        self.addr_street.set_text(a.getStreet())
        self.addr_city.set_text(a.getCity())
        self.addr_state.set_text(a.getState())
        self.addr_country.set_text(a.getCountry())
        self.addr_postal.set_text(a.getPostal())
        self.addr_details_field.set_text(utils.get_detail_text(a))

    def on_name_list_select_row(self,obj,row,b,c):

        name = obj.get_row_data(row)
        self.name_frame.set_label(name.getName())
        self.alt_given_field.set_text(name.getFirstName())
        self.alt_last_field.set_text(name.getSurname())
        self.alt_suffix_field.set_text(name.getSuffix())
        self.name_details_field.set_text(utils.get_detail_text(name))

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

    def on_attr_list_select_row(self,obj,row,b,c):

        attr = obj.get_row_data(row)
        self.attr_type.set_label(const.display_pattr(attr.getType()))
        self.attr_value.set_text(attr.getValue())
        self.attr_details_field.set_text(utils.get_detail_text(attr))

    def aka_double_click(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            self.on_aka_update_clicked(obj)

    def on_aka_update_clicked(self,obj):
        import NameEdit
        if len(obj.selection) > 0:
            NameEdit.NameEditor(self,obj.get_row_data(obj.selection[0]))

    def load_photo(self,photo):
        """loads, scales, and displays the person's main photo"""
        self.load_obj = photo
        if photo == None:
            self.get_widget("personPix").hide()
        else:
            try:
                i = GdkImlib.Image(photo)
                scale = float(const.picWidth)/float(max(i.rgb_height,i.rgb_width))
                x = int(scale*(i.rgb_width))
                y = int(scale*(i.rgb_height))
                i = i.clone_scaled_image(x,y)
                self.get_widget("personPix").load_imlib(i)
                self.get_widget("personPix").show()
            except:
                self.get_widget("personPix").hide()

    def update_lists(self):
        """Updates the person's lists if anything has changed"""
        if self.lists_changed:
            self.person.setEventList(self.elist)
            self.person.setAlternateNames(self.nlist)
            self.person.setUrlList(self.ulist)
            self.person.setAttributeList(self.alist)
            self.person.setAddressList(self.plist)
            utils.modified()

    def on_apply_person_clicked(self,obj):
    
        surname = self.surname_field.get_text()
        suffix = self.suffix.get_text()
        given = self.given.get_text()
        nick = self.nick.get_text()
        title = self.title.get_text()
        idval = self.gid.get_text()
        
        name = self.pname

        if idval != self.person.getId():
            m = self.db.getPersonMap() 
            if not m.has_key(idval):
                if m.has_key(self.person.getId()):
                    del m[self.person.getId()]
                    m[idval] = self.person
                self.person.setId(idval)
                utils.modified()
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

        if not name.are_equal(self.person.getPrimaryName()):
            self.person.setPrimaryName(name)
            utils.modified()

        if nick != self.person.getNickName():
            self.person.setNickName(nick)
            utils.modified()

        self.birth.setDate(self.bdate.get_text())
        bplace_obj = utils.get_place_from_list(self.bpcombo)
        bplace = string.strip(self.bplace.get_text())
        if bplace_obj == None and bplace != "":
            bplace_obj = Place()
            bplace_obj.set_title(bplace)
            self.db.addPlace(bplace_obj)
            utils.modified()
        self.birth.setPlace(bplace_obj)

        if not self.person.getBirth().are_equal(self.birth):
            self.person.setBirth(self.birth)

        # Update each of the families child lists to reflect any
        # change in ordering due to the new birth date
        family = self.person.getMainFamily()
        if (family):
            new_order = reorder_child_list(self.person,family.getChildList())
            family.setChildList(new_order)
        for (family, rel1, rel2) in self.person.getAltFamilyList():
            new_order = reorder_child_list(self.person,family.getChildList())
            family.setChildList(new_order)
    
        self.death.setDate(self.ddate.get_text())
        dplace_obj = utils.get_place_from_list(self.dpcombo)
        dplace = string.strip(self.dplace.get_text())
        if dplace_obj == None and dplace != "":
            dplace_obj = Place()
            dplace_obj.set_title(dplace)
            self.db.addPlace(dplace_obj)
            utils.modified()
        self.death.setPlace(dplace_obj)

        if not self.person.getDeath().are_equal(self.death):
            self.person.setDeath(self.death)

        male = self.is_male.get_active()
        female = self.is_female.get_active()
        unknown = self.is_unknown.get_active()
        error = 0
        if male and self.person.getGender() != Person.male:
            self.person.setGender(Person.male)
            for temp_family in self.person.getFamilyList():
                if self.person == temp_family.getMother():
                    if temp_family.getFather() != None:
                        error = 1
                    else:
                        temp_family.setMother(None)
                        temp_family.setFather(self.person)
            utils.modified()
        elif female and self.person.getGender() != Person.female:
            self.person.setGender(Person.female)
            for temp_family in self.person.getFamilyList():
                if self.person == temp_family.getFather():
                    if temp_family.getMother() != None:
                        error = 1
                    else:
                        temp_family.setFather(None)
                        temp_family.setMother(self.person)
            utils.modified()
        elif unknown and self.person.getGender() != Person.unknown:
            self.person.setGender(Person.unknown)
            for temp_family in self.person.getFamilyList():
                if self.person == temp_family.getFather():
                    if temp_family.getMother() != None:
                        error = 1
                    else:
                        temp_family.setFather(None)
                        temp_family.setMother(self.person)
                if self.person == temp_family.getMother():
                    if temp_family.getFather() != None:
                        error = 1
                    else:
                        temp_family.setMother(None)
                        temp_family.setFather(self.person)
            utils.modified()

        if error == 1:
            msg = _("Changing the gender caused problems with marriage information.")
            msg2 = _("Please check the person's marriages.")
            GnomeErrorDialog("%s\n%s" % (msg,msg2))
        
        text = self.notes_field.get_chars(0,-1)
        if text != self.person.getNote():
            self.person.setNote(text)
            utils.modified()

        self.update_lists()
        self.callback(self)
        utils.destroy_passed_object(obj)

    def on_primary_name_source_clicked(self,obj):
        import Sources
        Sources.SourceSelector(self.pname.getSourceRefList(),self,src_changed)

    def on_name_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.pname)

    def load_person_image(self):
        photo_list = self.person.getPhotoList()
        if len(photo_list) != 0:
            ph = photo_list[0]
            object = ph.getReference()
            if self.load_obj != object.getPath():
                if object.getMimeType()[0:5] == "image":
                    self.load_photo(object.getPath())
                else:
                    self.load_photo(None)
        else:
            self.load_photo(None)
        
    def on_switch_page(self,obj,a,page):
        if page == 0:
            self.load_person_image()
        elif page == 6 and self.not_loaded:
            self.not_loaded = 0
            self.gallery.load_images()

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

def src_changed(parent):
    parent.lists_changed = 1
    
#-------------------------------------------------------------------------
# 
# birth_dates_in_order
# 
# Check any *valid* birthdates in the list to insure that they are in
# numerically increasing order.
# 
#-------------------------------------------------------------------------
def birth_dates_in_order(list):
    inorder = 1
    prev_date = "00000000"
    for i in range(len(list)):
        child = list[i]
        bday = child.getBirth().getDateObj()
        child_date = sort.build_sort_event(bday)
        if (child_date == "99999999"):
            continue
        if (prev_date <= child_date):	# <= allows for twins
            prev_date = child_date
        else:
            inorder = 0
    return inorder


#-------------------------------------------------------------------------
# 
# reorder_child_list
# 
# Reorder the child list to put the specified person in his/her
# correct birth orde.  Only check *valid* birthdates.  Move the person
# as short a distance as possible.
# 
#-------------------------------------------------------------------------
def reorder_child_list(person, list):
    if (birth_dates_in_order(list)):
        return(list)

    # Build the person's date string once
    person_bday = sort.build_sort_event(person.getBirth().getDateObj())

    # First, see if the person needs to be moved forward in the list
    index = list.index(person)
    target = index
    for i in range(index-1, -1, -1):
        other_bday = sort.build_sort_event(list[i].getBirth().getDateObj())
        if (other_bday == "99999999"):
            continue;
        if (person_bday < other_bday):
            target = i

    # Now try moving to a later position in the list
    if (target == index):
        for i in range(index, len(list)):
            other_bday = sort.build_sort_event(list[i].getBirth().getDateObj())
            if (other_bday == "99999999"):
                continue;
            if (person_bday > other_bday):
                target = i

    # Actually need to move?  Do it now.
    if (target != index):
        list.remove(person)
        list.insert(target,person)
    return list
    
