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
import pickle

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
from gnome.ui import GnomeErrorDialog, GnomeWarningDialog
import libglade
import GdkImlib
from GDK import ACTION_COPY, BUTTON1_MASK, _2BUTTON_PRESS

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsCfg
import Date
from RelLib import *
import ImageSelect
import sort
import AutoComp
from DateEdit import DateEdit
from QuestionDialog import QuestionDialog

from intl import gettext
_ = gettext

_temple_names = const.lds_temple_codes.keys()
_temple_names.sort()
_temple_names = [""] + _temple_names

pycode_tgts = [('url', 0, 0),
               ('pevent', 0, 1),
               ('pattr', 0, 2),
               ('paddr', 0, 3)]

#-------------------------------------------------------------------------
#
# EditPerson class
#
#-------------------------------------------------------------------------
class EditPerson:

    def __init__(self,person,db,callback=None):
        """Creates an edit window.  Associates a person with the window."""
        self.person = person
        self.original_id = person.getId()
        self.db = db
        self.callback = callback
        self.path = db.getSavePath()
        self.not_loaded = 1
        self.lds_not_loaded = 1
        self.lists_changed = 0
        self.update_birth = 0
        self.update_death = 0
        self.pmap = {}
        self.add_places = []

        for key in db.getPlaceKeys():
            p = db.getPlaceDisplay(key)
            self.pmap[p[0]] = key
            
        self.load_obj = None
        self.top = libglade.GladeXML(const.editPersonFile, "editPerson")
        gwidget = self.top.get_widget("photolist")
        self.gallery = ImageSelect.Gallery(person, self.path, gwidget, self.db, self)

        self.name_update_btn = self.top.get_widget('aka_update')
        self.name_delete_btn = self.top.get_widget('aka_delete')

        self.web_update_btn = self.top.get_widget('update_url')
        self.web_delete_btn = self.top.get_widget('delete_url')

        self.event_edit_btn = self.top.get_widget('event_edit_btn')
        self.event_delete_btn = self.top.get_widget('event_delete_btn')
        
        self.attr_edit_btn = self.top.get_widget('attr_edit_btn')
        self.attr_delete_btn = self.top.get_widget('attr_delete_btn')

        self.addr_edit_btn = self.top.get_widget('addr_edit_btn')
        self.addr_delete_btn = self.top.get_widget('addr_delete_btn')

        self.top.signal_autoconnect({
            "destroy_passed_object"     : self.on_cancel_edit,
            "on_up_clicked"             : self.on_up_clicked,
            "on_down_clicked"           : self.on_down_clicked,
            "on_add_address_clicked"    : self.on_add_addr_clicked,
            "on_add_aka_clicked"        : self.on_add_aka_clicked,
            "on_add_attr_clicked"       : self.on_add_attr_clicked,
            "on_add_url_clicked"        : self.on_add_url_clicked,
            "on_addr_button_press"      : self.addr_double_click,
            "on_web_button_press"       : self.url_double_click,
            "on_addphoto_clicked"       : self.gallery.on_add_photo_clicked,
            "on_addr_select_row"        : self.on_addr_select_row,
            "on_addr_unselect_row"      : self.on_addr_unselect_row,
            "on_aka_delete_clicked"     : self.on_aka_delete_clicked,
            "on_aka_update_clicked"     : self.on_aka_update_clicked,
            "on_apply_person_clicked"   : self.on_apply_person_clicked,
            "on_attr_button_press"      : self.attr_double_click,
            "on_attr_select_row"        : self.on_attr_select_row,
            "on_attr_unselect_row"      : self.on_attr_unselect_row,
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
            "on_event_unselect_row"     : self.on_event_unselect_row,
            "on_event_update_clicked"   : self.on_event_update_clicked,
            "on_name_button_press"      : self.aka_double_click,
            "on_name_select_row"        : self.on_name_select_row,
            "on_name_unselect_row"      : self.on_name_unselect_row,
            "on_name_note_clicked"      : self.on_name_note_clicked,
            "on_ldsbap_note_clicked"    : self.on_ldsbap_note_clicked,
            "on_ldsendow_note_clicked"  : self.on_ldsendow_note_clicked,
            "on_ldsseal_note_clicked"   : self.on_ldsseal_note_clicked,
            "on_ldsbap_src_clicked"     : self.on_ldsbap_source_clicked,
            "on_ldsendow_src_clicked"   : self.on_ldsendow_source_clicked,
            "on_ldsseal_src_clicked"    : self.on_ldsseal_source_clicked,
            "on_name_source_clicked"    : self.on_primary_name_source_clicked,
            "on_photolist_button_press_event" : self.gallery.on_button_press_event,
            "on_photolist_select_icon"  : self.gallery.on_photo_select_icon,
            "on_update_address_clicked" : self.on_update_addr_clicked,
            "on_update_attr_clicked"    : self.on_update_attr_clicked,
            "on_update_url_clicked"     : self.on_update_url_clicked,
            "on_web_go_clicked"         : self.on_web_go_clicked,
            "on_web_select_row"         : self.on_web_select_row,
            "on_web_unselect_row"       : self.on_web_unselect_row,
            })

        self.window = self.get_widget("editPerson")
        self.notes_field = self.get_widget("personNotes")
        self.event_name_field  = self.get_widget("eventName")
        self.event_place_field = self.get_widget("eventPlace")
        self.event_cause_field = self.get_widget("eventCause")
        self.event_date_field  = self.get_widget("eventDate")
        self.event_descr_field = self.get_widget("eventDescription")
        self.event_src_field = self.get_widget("event_srcinfo")
        self.event_conf_field = self.get_widget("event_conf")
        self.attr_conf_field = self.get_widget("attr_conf")
        self.addr_conf_field = self.get_widget("addr_conf")
        self.name_conf_field = self.get_widget("name_conf")
        self.attr_src_field = self.get_widget("attr_srcinfo")
        self.name_src_field = self.get_widget("name_srcinfo")
        self.addr_src_field = self.get_widget("addr_srcinfo")
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
        self.alt_title_field = self.get_widget("alt_title")
        self.alt_suffix_field = self.get_widget("alt_suffix")
        self.name_type_field = self.get_widget("name_type")
        self.surname_field = self.get_widget("surname")
        self.ntype_field = self.get_widget("ntype")
        self.suffix = self.get_widget("suffix")
        self.given = self.get_widget("givenName")
        self.nick = self.get_widget("nickname")
        self.title = self.get_widget("title")
        self.bdate  = self.get_widget("birthDate")
        self.bplace = self.get_widget("birthPlace")
        self.bpcombo = self.get_widget("bpcombo")
        self.dpcombo = self.get_widget("dpcombo")
        self.sncombo = self.get_widget("sncombo")
        self.ddate  = self.get_widget("deathDate")
        self.dplace = self.get_widget("deathPlace")
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

        self.death = Event(person.getDeath())
        self.birth = Event(person.getBirth())
        self.pname = Name(person.getPrimaryName())

        self.elist = person.getEventList()[:]
        self.nlist = person.getAlternateNames()[:]
        self.alist = person.getAttributeList()[:]
        self.ulist = person.getUrlList()[:]
        self.plist = person.getAddressList()[:]

        # Typing CR selects OK button
        self.window.editable_enters(self.notes_field);
        self.window.editable_enters(self.given);
        self.window.editable_enters(self.surname_field);
        self.window.editable_enters(self.suffix);
        self.window.editable_enters(self.title);
        self.window.editable_enters(self.nick);
        self.window.editable_enters(self.ntype_field.entry)
        self.window.editable_enters(self.bdate);
        self.window.editable_enters(self.bplace);
        self.window.editable_enters(self.ddate);
        self.window.editable_enters(self.dplace);
        
        self.autoplace = AutoComp.AutoCombo(self.bpcombo,self.pmap.keys())
        self.autodeath = AutoComp.AutoCombo(self.dpcombo,self.pmap.keys(),
                                            self.autoplace)
        self.comp = AutoComp.AutoCombo(self.sncombo,self.db.getSurnames())
            
        self.gid.set_text(person.getId())
        self.gid.set_editable(GrampsCfg.id_edit)
        self.event_list.set_column_visibility(4,GrampsCfg.show_detail)
        self.name_list.set_column_visibility(2,GrampsCfg.show_detail)
        self.attr_list.set_column_visibility(2,GrampsCfg.show_detail)
        self.addr_list.set_column_visibility(2,GrampsCfg.show_detail)

        self.event_list = self.get_widget("eventList")

        if GrampsCfg.display_attr:
            self.get_widget("user_label").set_text(GrampsCfg.attr_name)
            val = ""
            for attr in self.person.getAttributeList():
                if attr.getType() == const.save_pattr(GrampsCfg.attr_name):
                    val = attr.getValue()
                    break
            self.get_widget("user_data").set_text(val)
            self.get_widget("user_colon").show()
        else:
            self.get_widget("user_label").hide()
            self.get_widget("user_colon").hide()
            self.get_widget("user_data").hide()

        self.lds_baptism = LdsOrd(self.person.getLdsBaptism())
        self.lds_endowment = LdsOrd(self.person.getLdsEndowment())
        self.lds_sealing = LdsOrd(self.person.getLdsSeal())

        if GrampsCfg.uselds or self.lds_baptism or self.lds_endowment or self.lds_sealing:
            self.get_widget("lds_tab").show()
            self.get_widget("lds_page").show()

        types = const.NameTypesMap.keys()
        types.sort()
        self.ntype_field.set_popdown_strings(types)
        self.autotype = AutoComp.AutoEntry(self.ntype_field.entry,types)
        self.write_primary_name()
        
        if person.getGender() == Person.male:
            self.is_male.set_active(1)
        elif person.getGender() == Person.female:
            self.is_female.set_active(1)
        else:
            self.is_unknown.set_active(1)

        self.nick.set_text(person.getNickName())
        self.update_birth_death()

        self.load_person_image()
        
        # set notes data
        self.notes_field.set_point(0)
        self.notes_field.insert_defaults(person.getNote())
        self.notes_field.set_word_wrap(1)

        self.event_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                      pycode_tgts,ACTION_COPY)
        self.event_list.drag_source_set(BUTTON1_MASK, pycode_tgts, ACTION_COPY)
        self.event_list.connect('drag_data_get', self.ev_drag_data_get)
        self.event_list.connect('drag_data_received',
                                self.ev_drag_data_received)

        self.web_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                    pycode_tgts,ACTION_COPY)
        self.web_list.drag_source_set(BUTTON1_MASK, pycode_tgts, ACTION_COPY)
        self.web_list.connect('drag_data_get', self.url_drag_data_get)
        self.web_list.connect('drag_data_received',
                              self.url_drag_data_received)
        
        self.attr_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,pycode_tgts,
                                     ACTION_COPY)
        self.attr_list.drag_source_set(BUTTON1_MASK, pycode_tgts, ACTION_COPY)
        self.attr_list.connect('drag_data_get', self.at_drag_data_get)
        self.attr_list.connect('drag_data_received',
                               self.at_drag_data_received)

        self.addr_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                     pycode_tgts,ACTION_COPY)
        self.addr_list.drag_source_set(BUTTON1_MASK, pycode_tgts, ACTION_COPY)
        self.addr_list.connect('drag_data_get', self.ad_drag_data_get)
        self.addr_list.connect('drag_data_received',
                               self.ad_drag_data_received)

        self.redraw_event_list()
        self.redraw_attr_list()
        self.redraw_addr_list()
        self.redraw_name_list()
        self.redraw_url_list()

    def lds_field(self,ord,combo,date,place):
        combo.set_popdown_strings(_temple_names)
        if ord:
            stat = ord.getStatus()
            date.set_text(ord.getDate())
            if ord.getTemple() != "":
                name = const.lds_temple_to_abrev[ord.getTemple()]
            else:
                name = ""
            combo.entry.set_text(name)
        else:
            stat = 0
            combo.entry.set_text("")

        AutoComp.AutoEntry(place,None,self.autoplace)
        if ord and ord.getPlace():
            place.set_text(ord.getPlace().get_title())
        return stat

    def draw_lds(self):
        """Draws the LDS window. This window is not always drawn, and in
        may cases is hidden."""

        self.ldsbap_date = self.get_widget("ldsbapdate")
        self.ldsbap_temple = self.get_widget("ldsbaptemple")
        self.ldsend_date = self.get_widget("endowdate")
        self.ldsend_temple = self.get_widget("endowtemple")
        self.ldsseal_date = self.get_widget("sealdate")
        self.ldsseal_temple = self.get_widget("sealtemple")
        self.ldsseal_fam = self.get_widget("sealparents")
        self.ldsbapstat = self.get_widget("ldsbapstat")
        self.ldssealstat = self.get_widget("sealstat")
        self.ldsendowstat = self.get_widget("endowstat")
        self.ldsbapplace = self.get_widget("lds_bap_place")
        self.ldssealplace = self.get_widget("lds_seal_place")
        self.ldsendowplace = self.get_widget("lds_end_place")

        self.bstat = self.lds_field(self.lds_baptism,
                                    self.ldsbap_temple,
                                    self.ldsbap_date,
                                    self.ldsbapplace)
        
        self.estat = self.lds_field(self.lds_endowment,
                                    self.ldsend_temple,
                                    self.ldsend_date,
                                    self.ldsendowplace)

        self.seal_stat = self.lds_field(self.lds_sealing,
                                        self.ldsseal_temple,
                                        self.ldsseal_date,
                                        self.ldssealplace)
        if self.lds_sealing:
            self.ldsfam = self.lds_sealing.getFamily()
        else:
            self.ldsfam = None

        myMenu = gtk.GtkMenu()
        item = gtk.GtkMenuItem(_("None"))
        item.set_data("f",None)
        item.connect("activate",self.menu_changed)
        item.show()
        myMenu.append(item)
        
        index = 0
        hist = 0
        flist = [self.person.getMainParents()]
        for (fam,mrel,frel) in self.person.getParentList():
            flist.append(fam)
        for fam in flist:
            if fam == None:
                continue
            f = fam.getFather()
            m = fam.getMother()
            if f and m:
                name = _("%(father)s and %(mother)s") % {
                    'father' : GrampsCfg.nameof(f),
                    'mother' : GrampsCfg.nameof(m) }
            elif f:
                name = GrampsCfg.nameof(f)
            elif m:
                name = GrampsCfg.nameof(m)
            else:
                name = _("unknown")
            item = gtk.GtkMenuItem(name)
            item.set_data("f",fam)
            item.connect("activate",self.menu_changed)
            item.show()
            myMenu.append(item)
            index = index + 1
            if fam == self.ldsfam:
                hist = index
        self.ldsseal_fam.set_menu(myMenu)
        self.ldsseal_fam.set_history(hist)

        self.build_bap_menu()
        self.build_seal_menu()
        self.build_endow_menu()

    def build_menu(self,list,task,opt_menu):
        menu = gtk.GtkMenu()
        index = 0
        for val in list:
            menuitem = gtk.GtkMenuItem(val)
            menuitem.set_data("val",index)
            menuitem.connect('activate',task)
            menuitem.show()
            menu.append(menuitem)
            index = index + 1
        opt_menu.set_menu(menu)
        opt_menu.set_history(self.bstat)
                   
    def build_bap_menu(self):
        self.build_menu(const.lds_baptism,self.set_lds_bap,self.ldsbapstat)

    def build_endow_menu(self):
        self.build_menu(const.lds_baptism,self.set_lds_endow,self.ldsendowstat)

    def build_seal_menu(self):
        self.build_menu(const.lds_csealing,self.set_lds_seal,self.ldssealstat)

    def set_lds_bap(self,obj):
        self.bstat = obj.get_data("val")

    def set_lds_endow(self,obj):
        self.estat = obj.get_data("val")

    def set_lds_seal(self,obj):
        self.seal_stat = obj.get_data("val")
    
    def ev_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if person == self.person.getId() or mytype != 'pevent':
                return
            foo = pickle.loads(data[2]);
            for src in foo.getSourceRefList():
                base = src.getBase()
                newbase = self.db.findSourceNoMap(base.getId())
                src.setBase(newbase)
            place = foo.getPlace()
            if place:
                foo.setPlace(self.db.findPlaceNoMap(place.getId()))
            self.elist.append(foo)
            self.lists_changed = 1
            self.redraw_event_list()

    def ev_drag_data_get(self,widget, context, sel_data, info, time):
        ev = widget.get_row_data(widget.focus_row)
        
        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev);
        data = str(('pevent',self.person.getId(),pickled));
        sel_data.set(sel_data.target, bits_per, data)

    def url_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if person == self.person.getId() or mytype != 'url':
                return
            foo = pickle.loads(data[2]);
            self.ulist.append(foo)
            self.lists_changed = 1
            self.redraw_url_list()

    def url_drag_data_get(self,widget, context, sel_data, info, time):
        ev = widget.get_row_data(widget.focus_row)
        
        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev);
        data = str(('url',self.person.getId(),pickled));
        sel_data.set(sel_data.target, bits_per, data)

    def at_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if person == self.person.getId() or mytype != 'pattr':
                return
            foo = pickle.loads(data[2]);
            for src in foo.getSourceRefList():
                base = src.getBase()
                newbase = self.db.findSourceNoMap(base.getId())
                src.setBase(newbase)
            self.alist.append(foo)
            self.lists_changed = 1
            self.redraw_attr_list()

    def at_drag_data_get(self,widget, context, sel_data, info, time):
        ev = widget.get_row_data(widget.focus_row)
        
        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev);
        data = str(('pattr',self.person.getId(),pickled));
        sel_data.set(sel_data.target, bits_per, data)

    def ad_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if person == self.person.getId() or mytype != 'paddr':
                return
            foo = pickle.loads(data[2]);
            for src in foo.getSourceRefList():
                base = src.getBase()
                newbase = self.db.findSourceNoMap(base.getId())
                src.setBase(newbase)
            self.plist.append(foo)
            self.lists_changed = 1
            self.redraw_addr_list()

    def ad_drag_data_get(self,widget, context, sel_data, info, time):
        ev = widget.get_row_data(widget.focus_row)
        
        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev);
        data = str(('paddr',self.person.getId(),pickled));
        sel_data.set(sel_data.target, bits_per, data)

    def menu_changed(self,obj):
        self.ldsfam = obj.get_data("f")
        
    def get_widget(self,str):
        """returns the widget related to the passed string"""
        return self.top.get_widget(str)

    def redraw_name_list(self):
        """redraws the name list"""
        Utils.redraw_list(self.nlist,self.name_list,disp_name)

    def redraw_url_list(self):
        """redraws the url list, disabling the go button if no url
        is selected"""
        length = Utils.redraw_list(self.ulist,self.web_list,disp_url)
        if length > 0:
            self.web_go.set_sensitive(1)
        else:
            self.web_go.set_sensitive(0)
            self.web_url.set_text("")
            self.web_description.set_text("")

    def redraw_attr_list(self):
        """Redraws the attribute list"""
        Utils.redraw_list(self.alist,self.attr_list,disp_attr)

    def redraw_addr_list(self):
        """redraws the address list for the person"""
        Utils.redraw_list(self.plist,self.addr_list,disp_addr)

    def redraw_event_list(self):
        """redraw_event_list - Update both the birth and death place combo
        boxes for any changes that occurred in the 'Event Edit' window.
        Make sure not to allow the editing of a birth event to change
        any values in the death event, and vice versa.  Since updating a
        combo list resets its present value, this code will have to save
        and restore the value for the event *not* being edited."""
        
        Utils.redraw_list(self.elist,self.event_list,disp_event)

        # Remember old combo list input
        prev_btext = Utils.strip_id(self.bplace.get_text())
        prev_dtext = Utils.strip_id(self.dplace.get_text())

        # Update birth with new values, make sure death values don't change
        if self.update_birth:
            self.update_birth = 0
            self.update_birth_info()
            self.dplace.set_text(prev_dtext)
        self.bdate_check = DateEdit(self.bdate,self.get_widget("birth_stat"))

        # Update death with new values, make sure birth values don't change
        if self.update_death:
            self.update_death = 0
            self.update_death_info()
            self.bplace.set_text(prev_btext)
        self.ddate_check = DateEdit(self.ddate,self.get_widget("death_stat"))

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

    def on_up_clicked(self,obj):
        if obj.selection:
            row = obj.selection[0]
            if row != 0:
                obj.select_row(row-1,0)

    def on_down_clicked(self,obj):
        if obj.selection:
            row = obj.selection[0]
            if row != obj.rows-1:
                obj.select_row(row+1,0)

    def on_event_add_clicked(self,obj):
        """Brings up the EventEditor for a new event"""
        import EventEdit
        pname = self.person.getPrimaryName().getName()
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.save_fevent,None,None,0,self.callback)

    def on_edit_birth_clicked(self,obj):
        """Brings up the EventEditor for the birth record, event
        name cannot be changed"""
        
        import EventEdit
        self.update_birth = 1
        pname = self.person.getPrimaryName().getName()
        event = self.birth
        event.setDate(self.bdate.get_text())
        def_placename = self.bplace.get_text()
        p = self.get_place(self.bplace)
        if p:
            event.setPlace(p)
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.save_fevent,event,def_placename,1,
                              self.callback)

    def on_edit_death_clicked(self,obj):
        """Brings up the EventEditor for the death record, event
        name cannot be changed"""
        
        import EventEdit
        self.update_death = 1
        pname = self.person.getPrimaryName().getName()
        event = self.death
        event.setDate(self.ddate.get_text())
        def_placename = self.dplace.get_text()
        p = self.get_place(self.dplace)
        if p:
            event.setPlace(p)
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.save_fevent,event,def_placename,1,
                              self.callback)

    def on_aka_delete_clicked(self,obj):
        """Deletes the selected name from the name list"""
        if Utils.delete_selected(obj,self.nlist):
            self.lists_changed = 1
            self.redraw_name_list()

    def on_delete_url_clicked(self,obj):
        """Deletes the selected URL from the URL list"""
        if Utils.delete_selected(obj,self.ulist):
            self.lists_changed = 1
            self.redraw_url_list()

    def on_delete_attr_clicked(self,obj):
        """Deletes the selected attribute from the attribute list"""
        if Utils.delete_selected(obj,self.alist):
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_delete_addr_clicked(self,obj):
        """Deletes the selected address from the address list"""
        if Utils.delete_selected(obj,self.plist):
            self.lists_changed = 1
            self.redraw_addr_list()

    def on_web_go_clicked(self,obj):
        """Attempts to display the selected URL in a web browser"""
        import gnome.url

        text = obj.get()
        if text:
            gnome.url.show(text)
        
    def on_cancel_edit(self,obj):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        if self.did_data_change():
            QuestionDialog(_('Abandon Changes'),
                           _("Are you sure you want to abandon your changes?"),
                           _("Abandon Changes"),
                           self.cancel_callback,
                           _("Continue Editing"))
        else:
            Utils.destroy_passed_object(obj)

    def on_delete_event(self,obj,b):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        if self.did_data_change():
            QuestionDialog(_('Abandon Changes'),
                           _("Are you sure you want to abandon your changes?"),
                           _("Abandon Changes"),
                           self.cancel_callback,
                           _("Continue Editing"))
            return 1
        else:
            Utils.destroy_passed_object(obj)
            return 0

    def cancel_callback(self):
        """If the user answered yes to abandoning changes, close the window"""
        Utils.destroy_passed_object(self.window)

    def did_data_change(self):
        """Check to see if any of the data has changed from the
        original record"""
        surname = self.surname_field.get_text()
        ntype = self.ntype_field.entry.get_text()
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
        if suffix != name.getSuffix():
            changed = 1
        if surname != name.getSurname():
            changed = 1
        if ntype != name.getType():
            changed = 1
        if given != name.getFirstName():
            changed = 1
        if nick != self.person.getNickName():
            changed = 1
        if title != name.getTitle():
            changed = 1
        if self.pname.getNote() != name.getNote():
            changed = 1
        if self.lds_not_loaded == 0 and self.check_lds():
            changed == 1

        bplace = string.strip(self.bplace.get_text())
        dplace = string.strip(self.dplace.get_text())

        if self.pmap.has_key(bplace):
            p1 = self.db.getPlaceMap()[self.pmap[bplace]]
        else:
            p1 = None
            if bplace != "":
                changed = 1
        self.birth.setPlace(p1)

        if self.pmap.has_key(dplace):
            p1 = self.db.getPlaceMap()[self.pmap[dplace]]
        else:
            p1 = None
            if dplace != "":
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

        if self.lds_not_loaded == 0:
            if not self.lds_baptism.are_equal(self.person.getLdsBaptism()):
                changed= 1

            if not self.lds_endowment.are_equal(self.person.getLdsEndowment()):
                changed = 1

            if not self.lds_sealing.are_equal(self.person.getLdsSeal()):
                changed = 1
                
        return changed

    def check_lds(self):
        self.lds_baptism.setDate(self.ldsbap_date.get_text())
        temple = self.ldsbap_temple.entry.get_text()
        if const.lds_temple_codes.has_key(temple):
            self.lds_baptism.setTemple(const.lds_temple_codes[temple])
        else:
            self.lds_baptism.setTemple("")
        self.lds_baptism.setPlace(self.get_place(self.ldsbapplace,1))

        self.lds_endowment.setDate(self.ldsend_date.get_text())
        temple = self.ldsend_temple.entry.get_text()
        if const.lds_temple_codes.has_key(temple):
            self.lds_endowment.setTemple(const.lds_temple_codes[temple])
        else:
            self.lds_endowment.setTemple("")
        self.lds_endowment.setPlace(self.get_place(self.ldsendowplace,1))

        self.lds_sealing.setDate(self.ldsseal_date.get_text())
        temple = self.ldsseal_temple.entry.get_text()
        if const.lds_temple_codes.has_key(temple):
            self.lds_sealing.setTemple(const.lds_temple_codes[temple])
        else:
            self.lds_sealing.setTemple("")
        self.lds_sealing.setFamily(self.ldsfam)
        self.lds_sealing.setPlace(self.get_place(self.ldssealplace,1))

    def on_event_delete_clicked(self,obj):
        """Delete the selected event"""
        if Utils.delete_selected(obj,self.elist):
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
        if event.button == 1 and event.type == _2BUTTON_PRESS:
            self.on_update_attr_clicked(obj)

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        if obj.selection:
            attr = obj.get_row_data(obj.selection[0])
            pname = self.person.getPrimaryName().getName()
            AttrEdit.AttributeEditor(self,attr,pname,const.personalAttributes)

    def addr_double_click(self,obj,event):
        if event.button == 1 and event.type == _2BUTTON_PRESS:
            self.on_update_addr_clicked(obj)

    def on_update_addr_clicked(self,obj):
        import AddrEdit
        if obj.selection:
            AddrEdit.AddressEditor(self,obj.get_row_data(obj.selection[0]))

    def url_double_click(self,obj,event):
        if event.button == 1 and event.type == _2BUTTON_PRESS:
            self.on_update_url_clicked(obj)

    def on_update_url_clicked(self,obj):
        import UrlEdit
        if obj.selection:
            pname = self.person.getPrimaryName().getName()
            url = obj.get_row_data(obj.selection[0])
            UrlEdit.UrlEditor(self,pname,url)

    def event_double_click(self,obj,event):
        if event.button == 1 and event.type == _2BUTTON_PRESS:
            self.on_event_update_clicked(obj)
        
    def on_event_update_clicked(self,obj):
        import EventEdit
        if obj.selection:
            pname = self.person.getPrimaryName().getName()
            event = obj.get_row_data(obj.selection[0])
            EventEdit.EventEditor(self,pname,const.personalEvents,
                                  const.save_fevent,event,None,0,
                                  self.callback)
        
    def on_event_select_row(self,obj,row,b,c):
        self.event_edit_btn.set_sensitive(1)
        self.event_delete_btn.set_sensitive(1)
        event = obj.get_row_data(row)
        self.event_date_field.set_text(event.getDate())
        self.event_place_field.set_text(event.getPlaceName())
        self.event_name_field.set_label(const.display_pevent(event.getName()))
        self.event_cause_field.set_text(event.getCause())
        self.event_descr_field.set_text(event.getDescription())
        if len(event.getSourceRefList()) > 0:
            psrc = event.getSourceRefList()[0]
            self.event_src_field.set_text(psrc.getBase().getTitle())
            self.event_conf_field.set_text(const.confidence[psrc.getConfidence()])
        else:
            self.event_src_field.set_text('')
            self.event_conf_field.set_text('')

    def on_event_unselect_row(self,obj,a,b,c):
        enable = len(obj.selection) > 0
        self.event_edit_btn.set_sensitive(enable)
        self.event_delete_btn.set_sensitive(enable)

    def on_addr_unselect_row(self,obj,row,b,c):
        enable = len(obj.selection) > 0
        self.addr_edit_btn.set_sensitive(enable)
        self.addr_delete_btn.set_sensitive(enable)

    def on_addr_select_row(self,obj,row,b,c):
        addr = obj.get_row_data(row)
        self.addr_edit_btn.set_sensitive(1)
        self.addr_delete_btn.set_sensitive(1)

        label = "%s %s %s" % (addr.getCity(),addr.getState(),addr.getCountry())
        self.addr_label.set_label(label)
        self.addr_start.set_text(addr.getDate())
        self.addr_street.set_text(addr.getStreet())
        self.addr_city.set_text(addr.getCity())
        self.addr_state.set_text(addr.getState())
        self.addr_country.set_text(addr.getCountry())
        self.addr_postal.set_text(addr.getPostal())
        if len(addr.getSourceRefList()) > 0:
            psrc = addr.getSourceRefList()[0]
            self.addr_conf_field.set_text(const.confidence[psrc.getConfidence()])
            self.addr_src_field.set_text(psrc.getBase().getTitle())
        else:
            self.addr_src_field.set_text('')
            self.addr_conf_field.set_text('')

    def on_name_select_row(self,obj,row,b,c):
        self.name_update_btn.set_sensitive(1)
        self.name_delete_btn.set_sensitive(1)
        name = obj.get_row_data(row)
        self.name_frame.set_label(name.getName())
        self.alt_given_field.set_text(name.getFirstName())
        self.alt_title_field.set_text(name.getTitle())
        self.alt_last_field.set_text(name.getSurname())
        self.alt_suffix_field.set_text(name.getSuffix())
        self.name_type_field.set_text(name.getType())
        if len(name.getSourceRefList()) > 0:
            psrc = name.getSourceRefList()[0]
            self.name_src_field.set_text(psrc.getBase().getTitle())
            self.name_conf_field.set_text(const.confidence[psrc.getConfidence()])
        else:
            self.name_src_field.set_text('')
            self.name_conf_field.set_text('')

    def on_name_unselect_row(self,obj,a,b,c):
        enable = len(obj.selection) > 0
        self.name_update_btn.set_sensitive(enable)
        self.name_delete_btn.set_sensitive(enable)

    def on_web_select_row(self,obj,row,b,c):
        self.web_update_btn.set_sensitive(1)
        self.web_delete_btn.set_sensitive(1)
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

    def on_web_unselect_row(self,obj,row,b,c):
        enable = len(obj.selection) > 0
        self.web_update_btn.set_sensitive(enable)
        self.web_delete_btn.set_sensitive(enable)

    def on_attr_select_row(self,obj,row,b,c):
        self.attr_edit_btn.set_sensitive(1)
        self.attr_delete_btn.set_sensitive(1)
        attr = obj.get_row_data(row)
        self.attr_type.set_label(const.display_pattr(attr.getType()))
        self.attr_value.set_text(attr.getValue())
        if len(attr.getSourceRefList()) > 0:
            psrc = attr.getSourceRefList()[0]
            self.attr_src_field.set_text(psrc.getBase().getTitle())
            self.attr_conf_field.set_text(const.confidence[psrc.getConfidence()])
        else:
            self.attr_src_field.set_text('')
            self.attr_conf_field.set_text('')

    def on_attr_unselect_row(self,obj,row,b,c):
        enable = len(obj.selection) > 0
        self.attr_edit_btn.set_sensitive(enable)
        self.attr_delete_btn.set_sensitive(enable)

    def aka_double_click(self,obj,event):
        if event.button == 1 and event.type == _2BUTTON_PRESS:
            self.on_aka_update_clicked(obj)
        elif event.button == 3:
            menu = gtk.GtkMenu()
            item = gtk.GtkTearoffMenuItem()
            item.show()
            menu.append(item)
            msg = _("Make the selected name the preferred name")
            Utils.add_menuitem(menu,msg,None,self.change_name)
            menu.popup(None,None,None,0,0)

    def on_aka_update_clicked(self,obj):
        import NameEdit
        if obj.selection:
            NameEdit.NameEditor(self,obj.get_row_data(obj.selection[0]))

    def load_photo(self,photo):
        """loads, scales, and displays the person's main photo"""
        self.load_obj = photo
        if photo == None:
            self.get_widget("personPix").hide()
        else:
            try:
                i = GdkImlib.Image(photo)
                ratio = float(max(i.rgb_height,i.rgb_width))
                scale = float(const.picWidth)/ratio
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
            self.person.setBirth(self.birth)
            self.person.setDeath(self.death)
            Utils.modified()

    def on_apply_person_clicked(self,obj):
    
        surname = self.surname_field.get_text()
        suffix = self.suffix.get_text()
        ntype = self.ntype_field.entry.get_text()
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
                Utils.modified()
            else:
                n = GrampsCfg.nameof(m[idval])
                msg1 = _("GRAMPS ID value was not changed.")
                msg2 = _("%(grampsid)s is already used by %(person)s") % {
                    'grampsid' : idval,
                    'person' : n }
                GnomeWarningDialog("%s\n%s" % (msg1,msg2))

        if suffix != name.getSuffix():
            name.setSuffix(suffix)

        if const.NameTypesMap.has_key(ntype):
            ntype = const.NameTypesMap[ntype]
        else:
            ntype = "Birth Name"

        if ntype != name.getType():
            name.setType(ntype)
            
        if surname != name.getSurname():
            name.setSurname(surname)
            self.db.addSurname(surname)

        if given != name.getFirstName():
            name.setFirstName(given)

        if title != name.getTitle():
            name.setTitle(title)

        name.setSourceRefList(self.pname.getSourceRefList())

        if not name.are_equal(self.person.getPrimaryName()):
            self.person.setPrimaryName(name)
            Utils.modified()

        if nick != self.person.getNickName():
            self.person.setNickName(nick)
            Utils.modified()

        self.pmap = {}
        for key in self.db.getPlaceKeys():
            p = self.db.getPlaceDisplay(key)
            self.pmap[p[0]] = key

        self.birth.setDate(self.bdate.get_text())
        self.birth.setPlace(self.get_place(self.bplace,1))

        if not self.person.getBirth().are_equal(self.birth):
            self.person.setBirth(self.birth)

        # Update each of the families child lists to reflect any
        # change in ordering due to the new birth date
        family = self.person.getMainParents()
        if (family):
            new_order = reorder_child_list(self.person,family.getChildList())
            family.setChildList(new_order)
        for (family, rel1, rel2) in self.person.getParentList():
            new_order = reorder_child_list(self.person,family.getChildList())
            family.setChildList(new_order)
    
        self.death.setDate(self.ddate.get_text())
        self.death.setPlace(self.get_place(self.dplace,1))

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
            Utils.modified()
        elif female and self.person.getGender() != Person.female:
            self.person.setGender(Person.female)
            for temp_family in self.person.getFamilyList():
                if self.person == temp_family.getFather():
                    if temp_family.getMother() != None:
                        error = 1
                    else:
                        temp_family.setFather(None)
                        temp_family.setMother(self.person)
            Utils.modified()
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
            Utils.modified()

        if error == 1:
            msg = _("Changing the gender caused problems "
                    "with marriage information.\nPlease check "
                    "the person's marriages.")
            GnomeErrorDialog(msg)
        
        text = self.notes_field.get_chars(0,-1)
        if text != self.person.getNote():
            self.person.setNote(text)
            Utils.modified()

        if self.lds_not_loaded == 0:
            self.check_lds()
            ord = LdsOrd(self.person.getLdsBaptism())
            if not self.lds_baptism.are_equal(ord):
                self.person.setLdsBaptism(self.lds_baptism)
                Utils.modified()

            ord = LdsOrd(self.person.getLdsEndowment())
            if not self.lds_endowment.are_equal(ord):
                self.person.setLdsEndowment(self.lds_endowment)
                Utils.modified()

            ord = LdsOrd(self.person.getLdsSeal())
            if not self.lds_sealing.are_equal(ord):
                self.person.setLdsSeal(self.lds_sealing)
                Utils.modified()

        self.update_lists()
        if self.callback:
            self.callback(self,self.add_places)
        Utils.destroy_passed_object(obj)

    def get_place(self,field,makenew=0):
        text = string.strip(field.get_text())
        if text:
            if self.pmap.has_key(text):
                return self.db.getPlaceMap()[self.pmap[text]]
            elif makenew:
                place = Place()
                place.set_title(text)
                self.db.addPlace(place)
                self.pmap[text] = place.getId()
                self.add_places.append(place)
                Utils.modified()
                return place
            else:
                return None
        else:
            return None

    def on_primary_name_source_clicked(self,obj):
        import Sources
        Sources.SourceSelector(self.pname.getSourceRefList(),self,self.update_primary_name)

    def update_primary_name(self,list):
        self.pname.setSourceRefList(list)
        self.lists_changed = 1

    def on_name_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.pname)

    def on_ldsbap_source_clicked(self,obj):
        import Sources
        Sources.SourceSelector(self.lds_baptism.getSourceRefList(),self,self.update_ldsbap_list)

    def update_ldsbap_list(self,list):
        self.lds_baptism.setSourceRefList(list)
        self.lists_changed = 1
        
    def on_ldsbap_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.lds_baptism)

    def on_ldsendow_source_clicked(self,obj):
        import Sources
        Sources.SourceSelector(self.lds_endowment.getSourceRefList(),self,self.set_ldsendow_list)

    def set_ldsendow_list(self,list):
        self.lds_endowment.setSourceRefList(list)
        self.lists_changed = 1

    def on_ldsendow_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.lds_endowment)

    def on_ldsseal_source_clicked(self,obj):
        import Sources
        ord = self.person.getLdsSeal()
        Sources.SourceSelector(self.lds_sealing.getSourceRefList(),self,self.lds_seal_list)

    def lds_seal_list(self,list):
        self.lds_sealing.setSourceRefList(list)
        self.lists_changed = 1

    def on_ldsseal_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.lds_sealing)

    def load_person_image(self):
        photo_list = self.person.getPhotoList()
        if photo_list:
            ph = photo_list[0]
            object = ph.getReference()
            if self.load_obj != object.getPath():
                if object.getMimeType()[0:5] == "image":
                    self.load_photo(object.getPath())
                else:
                    self.load_photo(None)
        else:
            self.load_photo(None)

    def update_birth_info(self):
        self.bdate.set_text(self.birth.getDate())
        self.bplace.set_text(self.birth.getPlaceName())

    def update_death_info(self):
        self.ddate.set_text(self.death.getDate())
        self.dplace.set_text(self.death.getPlaceName())
        
    def on_switch_page(self,obj,a,page):
        if page == 0:
            self.load_person_image()
            self.update_death_info()
            self.update_birth_info()
        elif page == 2:
            self.redraw_event_list()
        elif page == 6 and self.not_loaded:
            self.not_loaded = 0
            self.gallery.load_images()
        elif page == 8 and self.lds_not_loaded:
            self.lds_not_loaded = 0
            self.draw_lds()

    def change_name(self,obj):
        if self.name_list.selection:
            old = self.pname
            row = self.name_list.selection[0]
            new = self.name_list.get_row_data(row)
            self.nlist.remove(new)
            self.nlist.append(old)
            self.redraw_name_list()
            self.pname = Name(new)
            self.lists_changed = 1
            self.write_primary_name()

    def write_primary_name(self):
        # initial values
        name = GrampsCfg.nameof(self.person)
        self.get_widget("activepersonTitle").set_text(name)
        self.suffix.set_text(self.pname.getSuffix())

        self.surname_field.set_text(self.pname.getSurname())
        self.given.set_text(self.pname.getFirstName())

        self.ntype_field.entry.set_text(_(self.pname.getType()))
        self.title.set_text(self.pname.getTitle())

#-------------------------------------------------------------------------
#
# disp_name
#
#-------------------------------------------------------------------------
def disp_name(name):
    return [name.getName(),_(name.getType()),Utils.get_detail_flags(name)]

#-------------------------------------------------------------------------
#
# disp_url
#
#-------------------------------------------------------------------------
def disp_url(url):
    return [url.get_path(),url.get_description()]

#-------------------------------------------------------------------------
#
# disp_attr
#
#-------------------------------------------------------------------------
def disp_attr(attr):
    detail = Utils.get_detail_flags(attr)
    return [const.display_pattr(attr.getType()),attr.getValue(),detail]

#-------------------------------------------------------------------------
#
# disp_addr
#
#-------------------------------------------------------------------------
def disp_addr(addr):
    location = "%s %s %s" % (addr.getCity(),addr.getState(),addr.getCountry())
    return [addr.getDate(),location,Utils.get_detail_flags(addr)]

#-------------------------------------------------------------------------
#
# disp_event
#
#-------------------------------------------------------------------------
def disp_event(event):
    attr = Utils.get_detail_flags(event)
    return [const.display_pevent(event.getName()),event.getDescription(),
            event.getQuoteDate(),event.getPlaceName(),attr]

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
        child_date = sort.build_sort_date(bday)
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
# correct birth order.  Only check *valid* birthdates.  Move the person
# as short a distance as possible.
# 
#-------------------------------------------------------------------------
def reorder_child_list(person, list):
    if (birth_dates_in_order(list)):
        return(list)

    # Build the person's date string once
    person_bday = sort.build_sort_date(person.getBirth().getDateObj())

    # First, see if the person needs to be moved forward in the list
    index = list.index(person)
    target = index
    for i in range(index-1, -1, -1):
        other_bday = sort.build_sort_date(list[i].getBirth().getDateObj())
        if (other_bday == "99999999"):
            continue;
        if (person_bday < other_bday):
            target = i

    # Now try moving to a later position in the list
    if (target == index):
        for i in range(index, len(list)):
            other_bday = sort.build_sort_date(list[i].getBirth().getDateObj())
            if (other_bday == "99999999"):
                continue;
            if (person_bday > other_bday):
                target = i

    # Actually need to move?  Do it now.
    if (target != index):
        list.remove(person)
        list.insert(target,person)
    return list

