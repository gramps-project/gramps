#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

# $Id$

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
import gtk.glade
import gnome

from gtk.gdk import ACTION_COPY, BUTTON1_MASK, INTERP_BILINEAR, pixbuf_new_from_file

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsCfg
import ImageSelect
import sort
import AutoComp
import ListModel
import RelLib
import Sources
import DateEdit

from QuestionDialog import QuestionDialog, WarningDialog, ErrorDialog, SaveDialog

from gettext import gettext as _

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
        self.pdmap = {}
        self.add_places = []
        self.should_guess_gender = (self.original_id == '' and
                                    person.getGender () ==
                                    RelLib.Person.unknown)

        for key in db.getPlaceKeys():
            p = db.getPlaceDisplay(key)
            self.pdmap[p[0]] = key
            
        self.load_obj = None
        self.top = gtk.glade.XML(const.editPersonFile, "editPerson","gramps")
        self.window = self.get_widget("editPerson")
        self.window.set_title("%s - GRAMPS" % _('Edit Person'))
        
        self.icon_list = self.top.get_widget("iconlist")
        self.gallery = ImageSelect.Gallery(person, self.path, self.icon_list,
                                           self.db,self,self.window)

        self.complete = self.get_widget('complete')
        self.name_delete_btn = self.top.get_widget('aka_delete')
        self.name_edit_btn = self.top.get_widget('aka_edit')
        self.web_delete_btn = self.top.get_widget('delete_url')
        self.web_edit_btn = self.top.get_widget('edit_url')
        self.event_delete_btn = self.top.get_widget('event_delete_btn')
        self.event_edit_btn = self.top.get_widget('event_edit_btn')
        self.attr_delete_btn = self.top.get_widget('attr_delete_btn')
        self.attr_edit_btn = self.top.get_widget('attr_edit_btn')
        self.addr_delete_btn = self.top.get_widget('addr_delete_btn')
        self.addr_edit_btn = self.top.get_widget('addr_edit_btn')

        self.notes_field = self.get_widget("personNotes")
        self.flowed = self.get_widget("flowed")
        self.preform = self.get_widget("preform")
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
        self.addr_list = self.get_widget("address_list")
        self.addr_start = self.get_widget("address_start")
        self.addr_street = self.get_widget("street")
        self.addr_city = self.get_widget("city")
        self.addr_state = self.get_widget("state")
        self.addr_country = self.get_widget("country")
        self.addr_postal = self.get_widget("postal")
        self.addr_phone = self.get_widget("phone")
        self.event_list = self.get_widget("eventList")
        self.edit_person = self.get_widget("editPerson")
        self.name_list = self.get_widget("nameList")
        self.alt_given_field = self.get_widget("alt_given")
        self.alt_last_field = self.get_widget("alt_last")
        self.alt_title_field = self.get_widget("alt_title")
        self.alt_suffix_field = self.get_widget("alt_suffix")
        self.alt_prefix_field = self.get_widget("alt_prefix")
        self.name_type_field = self.get_widget("name_type")
        self.surname_field = self.get_widget("surname")
        self.ntype_field = self.get_widget("ntype")
        self.suffix = self.get_widget("suffix")
        self.prefix = self.get_widget("prefix")
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
        self.slist = self.get_widget("slist")

        self.general_label = self.get_widget("general_label")
        self.names_label = self.get_widget("names_label")
        self.events_label = self.get_widget("events_label")
        self.attr_label = self.get_widget("attr_label")
        self.addr_label = self.get_widget("addr_label")
        self.notes_label = self.get_widget("notes_label")
        self.sources_label = self.get_widget("sources_label")
        self.inet_label = self.get_widget("inet_label")
        self.gallery_label = self.get_widget("gallery_label")
        self.lds_tab = self.get_widget("lds_tab")

        self.death = RelLib.Event(person.getDeath())
        self.birth = RelLib.Event(person.getBirth())
        self.pname = RelLib.Name(person.getPrimaryName())

        self.elist = person.getEventList()[:]
        self.nlist = person.getAlternateNames()[:]
        self.alist = person.getAttributeList()[:]
        self.ulist = person.getUrlList()[:]
        self.plist = person.getAddressList()[:]

        if person:
            self.srcreflist = person.getSourceRefList()
        else:
            self.srcreflist = []

        Utils.bold_label(self.general_label)
        if self.srcreflist:
            Utils.bold_label(self.sources_label)
        if self.elist:
            Utils.bold_label(self.events_label)
        if self.nlist:
            Utils.bold_label(self.names_label)
        if self.alist:
            Utils.bold_label(self.attr_label)
        if self.ulist:
            Utils.bold_label(self.inet_label)
        if self.plist:
            Utils.bold_label(self.addr_label)
        if self.person.getPhotoList():
            Utils.bold_label(self.gallery_label)

        # event display
        etitles = [(_('Event'),-1,150),(_('Description'),-1,150),
                   (_('Date'),-1,100),(_('Place'),-1,100)]
        
        self.etree = ListModel.ListModel(self.event_list,etitles,
                                         self.on_event_select_row,
                                         self.on_event_update_clicked)

        # attribute display
        atitles = [(_('Attribute'),-1,150),(_('Value'),-1,150)]
        self.atree = ListModel.ListModel(self.attr_list,atitles,
                                         self.on_attr_select_row,
                                         self.on_update_attr_clicked)
                                         
        # address display
        ptitles = [(_('Date'),-1,150),(_('Address'),-1,150)]
        self.ptree = ListModel.ListModel(self.addr_list, ptitles,
                                         self.on_addr_select_row,
                                         self.on_update_addr_clicked)

        # name display
        ntitles = [(_('Name'),-1,250),(_('Type'),-1,100)]
        self.ntree = ListModel.ListModel(self.name_list,ntitles,
                                         self.on_name_select_row)
        self.ntree.tree.connect('event',self.aka_double_click)

        # web display
        wtitles = [(_('Path'),-1,250),(_('Description'),-1,100)]
        self.wtree = ListModel.ListModel(self.web_list,wtitles,
                                         self.on_web_select_row,
                                         self.on_update_url_clicked)

        place_list = self.pdmap.keys()
        place_list.sort()
        self.autoplace = AutoComp.AutoCombo(self.bpcombo, place_list)
        self.autodeath = AutoComp.AutoCombo(self.dpcombo, place_list, self.autoplace)
        self.comp = AutoComp.AutoCombo(self.sncombo,self.db.getSurnames())
            
        self.gid.set_text(person.getId())
        self.gid.set_editable(GrampsCfg.id_edit)

        self.lds_baptism = RelLib.LdsOrd(self.person.getLdsBaptism())
        self.lds_endowment = RelLib.LdsOrd(self.person.getLdsEndowment())
        self.lds_sealing = RelLib.LdsOrd(self.person.getLdsSeal())

        if GrampsCfg.uselds \
                        or (not self.lds_baptism.isEmpty()) \
                        or (not self.lds_endowment.isEmpty()) \
                        or (not self.lds_sealing.isEmpty()):
            self.get_widget("lds_tab").show()
            self.get_widget("lds_page").show()
            if (not self.lds_baptism.isEmpty()) \
                        or (not self.lds_endowment.isEmpty()) \
                        or (not self.lds_sealing.isEmpty()):
                Utils.bold_label(self.lds_tab)

        types = const.NameTypesMap.keys()
        types.sort()
        self.autotype = AutoComp.AutoCombo(self.ntype_field,types)
        self.write_primary_name()
        
        if person.getGender() == RelLib.Person.male:
            self.is_male.set_active(1)
        elif person.getGender() == RelLib.Person.female:
            self.is_female.set_active(1)
        else:
            self.is_unknown.set_active(1)

        self.nick.set_text(person.getNickName())
        self.load_person_image()
        
        # set notes data
        self.notes_buffer = self.notes_field.get_buffer()
        if person.getNote():
            self.notes_buffer.set_text(person.getNote())
            if person.getNoteObj().getFormat() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)
            Utils.bold_label(self.notes_label)

        self.event_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,pycode_tgts,ACTION_COPY)
        self.event_list.drag_source_set(BUTTON1_MASK, pycode_tgts, ACTION_COPY)
        self.event_list.connect('drag_data_get', self.ev_drag_data_get)
        self.event_list.connect('drag_begin', self.ev_drag_begin)
        self.event_list.connect('drag_data_received',self.ev_drag_data_received)

        self.web_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,pycode_tgts,ACTION_COPY)
        self.web_list.drag_source_set(BUTTON1_MASK, pycode_tgts, ACTION_COPY)
        self.web_list.connect('drag_data_get', self.url_drag_data_get)
        self.web_list.connect('drag_begin', self.url_drag_begin)
        self.web_list.connect('drag_data_received',self.url_drag_data_received)
        
        self.attr_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,pycode_tgts,ACTION_COPY)
        self.attr_list.drag_source_set(BUTTON1_MASK, pycode_tgts, ACTION_COPY)
        self.attr_list.connect('drag_data_get', self.at_drag_data_get)
        self.attr_list.connect('drag_data_received',self.at_drag_data_received)
        self.attr_list.connect('drag_begin', self.at_drag_begin)

        self.addr_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,pycode_tgts,ACTION_COPY)
        self.addr_list.drag_source_set(BUTTON1_MASK, pycode_tgts,ACTION_COPY)
        self.addr_list.connect('drag_data_get', self.ad_drag_data_get)
        self.addr_list.connect('drag_data_received',self.ad_drag_data_received)
        self.addr_list.connect('drag_begin', self.ad_drag_begin)

        self.bdate_check = DateEdit.DateEdit(self.bdate,
                                             self.get_widget("birth_stat"))
        self.bdate_check.set_calendar(self.birth.getDateObj().get_calendar())

        self.ddate_check = DateEdit.DateEdit(self.ddate,
                                             self.get_widget("death_stat"))
        self.ddate_check.set_calendar(self.death.getDateObj().get_calendar())

        self.top.signal_autoconnect({
            "destroy_passed_object"     : self.on_cancel_edit,
            "on_up_clicked"             : self.on_up_clicked,
            "on_down_clicked"           : self.on_down_clicked,
            "on_add_address_clicked"    : self.on_add_addr_clicked,
            "on_add_aka_clicked"        : self.on_add_aka_clicked,
            "on_add_attr_clicked"       : self.on_add_attr_clicked,
            "on_add_url_clicked"        : self.on_add_url_clicked,
            "on_addphoto_clicked"       : self.gallery.on_add_photo_clicked,
            "on_selectphoto_clicked"    : self.gallery.on_select_photo_clicked,
            "on_aka_delete_clicked"     : self.on_aka_delete_clicked,
            "on_aka_update_clicked"     : self.on_aka_update_clicked,
            "on_apply_person_clicked"   : self.on_apply_person_clicked,
            "on_edit_birth_clicked"     : self.on_edit_birth_clicked,
            "on_edit_death_clicked"     : self.on_edit_death_clicked,
            "on_delete_address_clicked" : self.on_delete_addr_clicked,
            "on_delete_attr_clicked"    : self.on_delete_attr_clicked,
            "on_delete_event"           : self.on_delete_event,
            "on_delete_url_clicked"     : self.on_delete_url_clicked,
            "on_deletephoto_clicked"    : self.gallery.on_delete_photo_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_editphoto_clicked"      : self.gallery.on_edit_photo_clicked,
            "on_editperson_switch_page" : self.on_switch_page,
            "on_event_add_clicked"      : self.on_event_add_clicked,
            "on_event_delete_clicked"   : self.on_event_delete_clicked,
            "on_event_update_clicked"   : self.on_event_update_clicked,
            "on_name_note_clicked"      : self.on_name_note_clicked,
            "on_ldsbap_note_clicked"    : self.on_ldsbap_note_clicked,
            "on_ldsendow_note_clicked"  : self.on_ldsendow_note_clicked,
            "on_ldsseal_note_clicked"   : self.on_ldsseal_note_clicked,
            "on_ldsbap_src_clicked"     : self.on_ldsbap_source_clicked,
            "on_ldsendow_src_clicked"   : self.on_ldsendow_source_clicked,
            "on_ldsseal_src_clicked"    : self.on_ldsseal_source_clicked,
            "on_name_source_clicked"    : self.on_primary_name_source_clicked,
            "on_update_address_clicked" : self.on_update_addr_clicked,
            "on_update_attr_clicked"    : self.on_update_attr_clicked,
            "on_update_url_clicked"     : self.on_update_url_clicked,
            "on_web_go_clicked"         : self.on_web_go_clicked,
            "on_gender_activate"        : self.on_gender_activate,
            "on_givenName_focus_out_event": self.on_givenName_focus_out_event,
            "on_help_person_clicked"    : self.on_help_clicked,
            })

        self.update_birth_death()

        self.sourcetab = Sources.SourceTab(self.srcreflist,self,
                                           self.top,self.window,self.slist,
                                           self.top.get_widget('add_src'),
                                           self.top.get_widget('edit_src'),
                                           self.top.get_widget('del_src'))

        if self.person.getComplete():
            self.complete.set_active(1)

        self.redraw_event_list()
        self.redraw_attr_list()
        self.redraw_addr_list()
        self.redraw_name_list()
        self.redraw_url_list()
        self.get_widget("notebook").set_current_page(0)
        self.given.grab_focus()
        self.window.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')

    def build_columns(self,tree,list):
        cnum = 0
        for name in list:
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(name[0],renderer,text=cnum)
            column.set_min_width(name[1])
            cnum = cnum + 1
            tree.append_column(column)

    def lds_field(self,ord,combo,date,place):
        combo.set_popdown_strings(_temple_names)
        if not ord.isEmpty():
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

        myMenu = gtk.Menu()
        item = gtk.MenuItem(_("None"))
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
            item = gtk.MenuItem(name)
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

    def on_gender_activate (self, button):
        self.should_guess_gender = 0

    def on_givenName_focus_out_event (self, entry, event):
        if not self.should_guess_gender:
            return

        gender = self.db.genderStats.guess_gender(unicode(entry.get_text ()))
        if gender == RelLib.Person.unknown:
            self.is_unknown.set_active (1)
        elif gender == RelLib.Person.male:
            self.is_male.set_active (1)
        else:
            self.is_female.set_active (1)

    def build_menu(self,list,task,opt_menu,type):
        menu = gtk.Menu()
        index = 0
        for val in list:
            menuitem = gtk.MenuItem(val)
            menuitem.set_data("val",index)
            menuitem.connect('activate',task)
            menuitem.show()
            menu.append(menuitem)
            index = index + 1
        opt_menu.set_menu(menu)
        opt_menu.set_history(type)
                   
    def build_bap_menu(self):
        self.build_menu(const.lds_baptism,self.set_lds_bap,self.ldsbapstat,
                        self.bstat)

    def build_endow_menu(self):
        self.build_menu(const.lds_baptism,self.set_lds_endow,self.ldsendowstat,
                        self.estat)

    def build_seal_menu(self):
        self.build_menu(const.lds_csealing,self.set_lds_seal,self.ldssealstat,
                        self.seal_stat)

    def set_lds_bap(self,obj):
        self.lds_baptism.setStatus(obj.get_data("val"))

    def set_lds_endow(self,obj):
        self.lds_endowment.setStatus(obj.get_data("val"))

    def set_lds_seal(self,obj):
        self.lds_sealing.setStatus(obj.get_data("val"))
    
    def ev_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.etree.get_row_at(x,y)
        
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if mytype != 'pevent':
                return
            elif person == self.person.getId():
                self.move_element(self.elist,self.etree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                for src in foo.getSourceRefList():
                    base = src.getBase()
                    newbase = self.db.findSourceNoMap(base.getId())
                    src.setBase(newbase)
                place = foo.getPlace()
                if place:
                    foo.setPlace(self.db.findPlaceNoMap(place.getId()))
                self.elist.insert(row,foo)

            self.lists_changed = 1
            self.redraw_event_list()

    def move_element(self,list,src,dest):
        if src == -1:
            return
        obj = list[src]
        list.remove(obj)
        list.insert(dest,obj)

    def ev_drag_data_get(self,widget, context, sel_data, info, time):
        ev = self.etree.get_selected_objects()

        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(ev[0]);
        data = str(('pevent',self.person.getId(),pickled));
        sel_data.set(sel_data.target, bits_per, data)

    def ev_drag_begin(self, context, a):
        return
        icon = self.etree.get_icon()
        t = self.etree.tree
        (x,y) = icon.get_size()
        mask = gtk.gdk.Pixmap(self.window.window,x,y,1)
        mask.draw_rectangle(t.get_style().white_gc, gtk.TRUE, 0,0,x,y)
        t.drag_source_set_icon(t.get_colormap(),icon,mask)

    def url_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.wtree.get_row_at(x,y)
        
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if mytype != "url":
                return
            elif person == self.person.getId():
                self.move_element(self.ulist,self.wtree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                self.ulist.append(foo)
            self.lists_changed = 1
            self.redraw_url_list()

    def url_drag_begin(self, context, a):
        return

    def url_drag_data_get(self,widget, context, sel_data, info, time):
        ev = self.wtree.get_selected_objects()

        if len(ev):
            bits_per = 8; # we're going to pass a string
            pickled = pickle.dumps(ev[0]);
            data = str(('url',self.person.getId(),pickled));
            sel_data.set(sel_data.target, bits_per, data)

    def at_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.atree.get_row_at(x,y)

        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if mytype != 'pattr':
                return
            elif person == self.person.getId():
                self.move_element(self.alist,self.atree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                for src in foo.getSourceRefList():
                    base = src.getBase()
                    newbase = self.db.findSourceNoMap(base.getId())
                    src.setBase(newbase)
                self.alist.append(foo)
            self.lists_changed = 1
            self.redraw_attr_list()

    def at_drag_begin(self, context, a):
        return

    def at_drag_data_get(self,widget, context, sel_data, info, time):
        ev = self.atree.get_selected_objects()

        if len(ev):
            bits_per = 8; # we're going to pass a string
            pickled = pickle.dumps(ev[0]);
            data = str(('pattr',self.person.getId(),pickled));
            sel_data.set(sel_data.target, bits_per, data)
            
    def ad_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.ptree.get_row_at(x,y)

        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if mytype != 'paddr':
                return
            elif person == self.person.getId():
                self.move_element(self.plist,self.ptree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                for src in foo.getSourceRefList():
                    base = src.getBase()
                    newbase = self.db.findSourceNoMap(base.getId())
                    src.setBase(newbase)
                self.plist.insert(row,foo)
                
            self.lists_changed = 1
            self.redraw_addr_list()

    def ad_drag_data_get(self,widget, context, sel_data, info, time):
        ev = self.ptree.get_selected_objects()
        
        if len(ev):
            bits_per = 8; # we're going to pass a string
            pickled = pickle.dumps(ev[0]);
            data = str(('paddr',self.person.getId(),pickled));
            sel_data.set(sel_data.target, bits_per, data)

    def ad_drag_begin(self, context, a):
        return

    def menu_changed(self,obj):
        self.ldsfam = obj.get_data("f")
        
    def get_widget(self,str):
        """returns the widget related to the passed string"""
        return self.top.get_widget(str)

    def redraw_name_list(self):
        """redraws the name list"""
        self.ntree.clear()
        self.nmap = {}
        for name in self.nlist:
            iter = self.ntree.add([name.getName(),_(name.getType())],name)
            self.nmap[str(name)] = iter
        if self.nlist:
            self.ntree.select_row(0)
            Utils.bold_label(self.names_label)
        else:
            Utils.unbold_label(self.names_label)

    def redraw_url_list(self):
        """redraws the url list, disabling the go button if no url
        is selected"""
        self.wtree.clear()
        self.wmap = {}
        for url in self.ulist:
            iter = self.wtree.add([url.get_path(),url.get_description()],url)
            self.wmap[str(url)] = iter
            
        if len(self.ulist) > 0:
            self.web_go.set_sensitive(0)
            self.wtree.select_row(0)
            Utils.bold_label(self.inet_label)
        else:
            self.web_go.set_sensitive(0)
            self.web_url.set_text("")
            self.web_description.set_text("")
            Utils.unbold_label(self.inet_label)

    def redraw_addr_list(self):
        """Redraws the address list"""
        self.ptree.clear()
        self.pmap = {}
        for addr in self.plist:
            location = "%s %s %s %s" % (addr.getStreet(),addr.getCity(),
                                        addr.getState(),addr.getCountry())
            iter = self.ptree.add([addr.getDate(),location],addr)
            self.pmap[str(addr)] = iter
        if self.plist:
            self.ptree.select_row(0)
            Utils.bold_label(self.addr_label)
        else:
            Utils.unbold_label(self.addr_label)

    def redraw_attr_list(self):
        """redraws the attribute list for the person"""
        self.atree.clear()
        self.amap = {}
        for attr in self.alist:
            iter = self.atree.add([const.display_pattr(attr.getType()),attr.getValue()],attr)
            self.amap[str(attr)] = iter
        if self.alist:
            self.atree.select_row(0)
            Utils.bold_label(self.attr_label)
        else:
            Utils.unbold_label(self.attr_label)

    def name_edit_callback(self,name):
        self.redraw_name_list()
        self.ntree.select_iter(self.nmap[str(name)])

    def addr_edit_callback(self,addr):
        self.redraw_addr_list()
        self.ptree.select_iter(self.pmap[str(addr)])

    def url_edit_callback(self,url):
        self.redraw_url_list()
        self.wtree.select_iter(self.wmap[str(url)])

    def event_edit_callback(self,event):
        """Birth and death events may not be in the map"""
        self.redraw_event_list()
        try:
            self.etree.select_iter(self.emap[str(event)])
        except:
            pass

    def attr_edit_callback(self,attr):
        self.redraw_attr_list()
        self.atree.select_iter(self.amap[str(attr)])

    def redraw_event_list(self):
        """redraw_event_list - Update both the birth and death place combo
        boxes for any changes that occurred in the 'Event Edit' window.
        Make sure not to allow the editing of a birth event to change
        any values in the death event, and vice versa.  Since updating a
        combo list resets its present value, this code will have to save
        and restore the value for the event *not* being edited."""

        self.etree.clear()
        self.emap = {}
        for event in self.elist:
            iter = self.etree.add([const.display_pevent(event.getName()),event.getDescription(),
                                    event.getQuoteDate(),event.getPlaceName()],event)
            self.emap[str(event)] = iter
        if self.elist:
            self.etree.select_row(0)
            Utils.bold_label(self.events_label)
        else:
            Utils.unbold_label(self.events_label)

        # Remember old combo list input

        bplace_text = unicode(self.bplace.get_text())
        dplace_text = unicode(self.dplace.get_text())
            
        prev_btext = Utils.strip_id(bplace_text)
        prev_dtext = Utils.strip_id(dplace_text)

        # Update birth with new values, make sure death values don't change
        if self.update_birth:
            self.update_birth = 0
            self.update_birth_info()
            self.dplace.set_text(prev_dtext)

        # Update death with new values, make sure birth values don't change
        if self.update_death:
            self.update_death = 0
            self.update_death_info()
            self.bplace.set_text(prev_btext)

    def on_add_addr_clicked(self,obj):
        """Invokes the address editor to add a new address"""
        import AddrEdit
        AddrEdit.AddressEditor(self,None,self.addr_edit_callback,self.window)

    def on_add_aka_clicked(self,obj):
        """Invokes the name editor to add a new name"""
        import NameEdit
        NameEdit.NameEditor(self,None,self.name_edit_callback,self.window)

    def on_add_url_clicked(self,obj):
        """Invokes the url editor to add a new name"""
        import UrlEdit
        pname = self.person.getPrimaryName().getName()
        UrlEdit.UrlEditor(self,pname,None,self.url_edit_callback,self.window)

    def on_add_attr_clicked(self,obj):
        """Brings up the AttributeEditor for a new attribute"""
        import AttrEdit
        pname = self.person.getPrimaryName().getName()
        AttrEdit.AttributeEditor(self,None,pname,const.personalAttributes,
                                 self.attr_edit_callback,self.window)

    def on_up_clicked(self,obj):
        sel = obj.get_selection()
        store,iter = sel.get_selected()
        if iter:
            row = store.get_path(iter)
            sel.select_path((row[0]-1))

    def on_down_clicked(self,obj):
        sel = obj.get_selection()
        store,iter = sel.get_selected()
        if iter:
            row = store.get_path(iter)
            sel.select_path((row[0]+1))

    def on_event_add_clicked(self,obj):
        """Brings up the EventEditor for a new event"""
        import EventEdit
        pname = self.person.getPrimaryName().getName()
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.save_event,None,None,0,self.event_edit_callback)

    def on_edit_birth_clicked(self,obj):
        """Brings up the EventEditor for the birth record, event
        name cannot be changed"""
        
        import EventEdit
        self.update_birth = 1
        pname = self.person.getPrimaryName().getName()
        event = self.birth
        event.setDate(unicode(self.bdate.get_text()))
        def_placename = unicode(self.bplace.get_text())

        p = self.get_place(self.bplace)
        if p:
            event.setPlace(p)
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.save_event,event,def_placename,1,
                              self.event_edit_callback)

    def on_edit_death_clicked(self,obj):
        """Brings up the EventEditor for the death record, event
        name cannot be changed"""
        
        import EventEdit
        self.update_death = 1
        pname = self.person.getPrimaryName().getName()
        event = self.death
        event.setDate(unicode(self.ddate.get_text()))
        def_placename = unicode(self.dplace.get_text())

        p = self.get_place(self.dplace)
        if p:
            event.setPlace(p)
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.save_event,event,def_placename,1,
                              self.event_edit_callback)

    def on_aka_delete_clicked(self,obj):
        """Deletes the selected name from the name list"""
        store,iter = self.ntree.get_selected()
        if iter:
            self.nlist.remove(self.ntree.get_object(iter))
            self.lists_changed = 1
            self.redraw_name_list()

    def on_delete_url_clicked(self,obj):
        """Deletes the selected URL from the URL list"""
        store,iter = self.wtree.get_selected()
        if iter:
            self.ulist.remove(self.wtree.get_object(iter))
            self.lists_changed = 1
            self.redraw_url_list()

    def on_delete_attr_clicked(self,obj):
        """Deletes the selected attribute from the attribute list"""
        store,iter = self.atree.get_selected()
        if iter:
            self.alist.remove(self.atree.get_object(iter))
            self.lists_changed = 1
            self.redraw_attr_list()

    def on_delete_addr_clicked(self,obj):
        """Deletes the selected address from the address list"""
        store,iter = self.ptree.get_selected()
        if iter:
            self.plist.remove(self.ptree.get_object(iter))
            self.lists_changed = 1
            self.redraw_addr_list()

    def on_web_go_clicked(self,obj):
        """Attempts to display the selected URL in a web browser"""
        text = obj.get()
        if text:
            gnome.url_show(text)
        
    def on_cancel_edit(self,obj):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        if self.did_data_change():
            n = "<i>%s</i>" % self.person.getPrimaryName().getRegularName()
            SaveDialog(_('Save changes to %s?') % n,
                       _('If you close without saving, the changes you '
                         'have made will be lost'),
                       self.cancel_callback,
                       self.save)
        else:
            self.gallery.close()
            self.window.destroy()

    def save(self):
        self.on_apply_person_clicked(None)

    def on_delete_event(self,obj,b):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        if self.did_data_change():
            n = "<i>%s</i>" % self.person.getPrimaryName().getRegularName()
            SaveDialog(_('Save Changes to %s?') % n,
                       _('If you close without saving, the changes you '
                         'have made will be lost'),
                       self.cancel_callback,
                       self.save)
            return 1
        else:
            self.gallery.close()
            self.window.destroy()
            return 0

    def cancel_callback(self):
        """If the user answered yes to abandoning changes, close the window"""
        self.gallery.close()
        self.window.destroy()

    def did_data_change(self):
        """Check to see if any of the data has changed from the
        original record"""

        surname = unicode(self.surname_field.get_text())
        self.birth.setDate(unicode(self.bdate.get_text()))
        self.death.setDate(unicode(self.ddate.get_text()))

        ntype = unicode(self.ntype_field.entry.get_text())
        suffix = unicode(self.suffix.get_text())
        prefix = unicode(self.prefix.get_text())
        given = unicode(self.given.get_text())
        nick = unicode(self.nick.get_text())
        title = unicode(self.title.get_text())
        male = self.is_male.get_active()
        female = self.is_female.get_active()
        unknown = self.is_unknown.get_active()
        text = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                          self.notes_buffer.get_end_iter(),gtk.FALSE))
        format = self.preform.get_active()
        idval = unicode(self.gid.get_text())

        changed = 0
        name = self.person.getPrimaryName()

        if self.complete.get_active() != self.person.getComplete():
            changed = 1

        if self.person.getId() != idval:
            changed = 1
        if suffix != name.getSuffix():
            changed = 1
        if prefix != name.getSurnamePrefix():
            changed = 1
        if surname.upper() != name.getSurname().upper():
            changed = 1
        if ntype != const.InverseNameTypesMap[name.getType()]:
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
            changed = 1

        bplace = unicode(string.strip(self.bplace.get_text()))
        dplace = unicode(string.strip(self.dplace.get_text()))

        if self.pdmap.has_key(bplace):
            p1 = self.db.getPlaceMap()[self.pdmap[bplace]]
        else:
            p1 = None
            if bplace != "":
                changed = 1
        self.birth.setPlace(p1)

        if self.pdmap.has_key(dplace):
            p1 = self.db.getPlaceMap()[self.pdmap[dplace]]
        else:
            p1 = None
            if dplace != "":
                changed = 1
        self.death.setPlace(p1)

        if not self.birth.are_equal(self.person.getBirth()):
            changed = 1
        if not self.death.are_equal(self.person.getDeath()):
            changed = 1
        if male and self.person.getGender() != RelLib.Person.male:
            changed = 1
        elif female and self.person.getGender() != RelLib.Person.female:
            changed = 1
        elif unknown and self.person.getGender() != RelLib.Person.unknown:
            changed = 1
        if text != self.person.getNote() or self.lists_changed:
            changed = 1
        if format != self.person.getNoteFormat():
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
        self.lds_baptism.setDate(unicode(self.ldsbap_date.get_text()))
        temple = unicode(self.ldsbap_temple.entry.get_text())
        if const.lds_temple_codes.has_key(temple):
            self.lds_baptism.setTemple(const.lds_temple_codes[temple])
        else:
            self.lds_baptism.setTemple("")
        self.lds_baptism.setPlace(self.get_place(self.ldsbapplace,1))

        self.lds_endowment.setDate(unicode(self.ldsend_date.get_text()))
        temple = unicode(self.ldsend_temple.entry.get_text())
        if const.lds_temple_codes.has_key(temple):
            self.lds_endowment.setTemple(const.lds_temple_codes[temple])
        else:
            self.lds_endowment.setTemple("")
        self.lds_endowment.setPlace(self.get_place(self.ldsendowplace,1))

        self.lds_sealing.setDate(unicode(self.ldsseal_date.get_text()))
        temple = unicode(self.ldsseal_temple.entry.get_text())
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
        self.bdate_check.set_calendar(self.birth.getDateObj().get_calendar())
        self.ddate.set_text(self.death.getDate())
        self.ddate_check.set_calendar(self.death.getDateObj().get_calendar())
        self.dplace.set_text(self.death.getPlaceName())
        self.dplace.set_text(self.death.getPlaceName())

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        store,iter = self.atree.get_selected()
        if iter:
            attr = self.atree.get_object(iter)
            pname = self.person.getPrimaryName().getName()
            AttrEdit.AttributeEditor(self,attr,pname,const.personalAttributes,
                                     self.attr_edit_callback,self.window)

    def on_update_addr_clicked(self,obj):
        import AddrEdit
        store,iter = self.ptree.get_selected()
        if iter:
            AddrEdit.AddressEditor(self,self.ptree.get_object(iter),
                            self.addr_edit_callback,self.window)

    def on_update_url_clicked(self,obj):
        import UrlEdit
        store,iter = self.wtree.get_selected()
        if iter:
            pname = self.person.getPrimaryName().getName()
            url = self.wtree.get_object(iter)
            UrlEdit.UrlEditor(self,pname,url,self.url_edit_callback,self.window)

    def on_event_update_clicked(self,obj):
        import EventEdit

        store,iter = self.etree.get_selected()
        if not iter:
            return
        pname = self.person.getPrimaryName().getName()
        event = self.etree.get_object(iter)
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.save_event,event,None,0,
                              self.event_edit_callback)
        
    def on_event_select_row(self,obj):
        store,iter = obj.get_selected()
        if iter:
            row = store.get_path(iter)
            event = self.elist[row[0]]
            self.event_date_field.set_text(event.getDate())
            self.event_place_field.set_text(event.getPlaceName())
            self.event_name_field.set_text(const.display_pevent(event.getName()))
            self.event_cause_field.set_text(event.getCause())
            self.event_descr_field.set_text(short(event.getDescription()))
            if len(event.getSourceRefList()) > 0:
                psrc = event.getSourceRefList()[0]
                self.event_src_field.set_text(short(psrc.getBase().getTitle()))
                self.event_conf_field.set_text(const.confidence[psrc.getConfidence()])
            else:
                self.event_src_field.set_text('')
                self.event_conf_field.set_text('')
            self.event_delete_btn.set_sensitive(1)
            self.event_edit_btn.set_sensitive(1)
        else:
            self.event_date_field.set_text('')
            self.event_place_field.set_text('')
            self.event_name_field.set_text('')
            self.event_cause_field.set_text('')
            self.event_descr_field.set_text('')
            self.event_src_field.set_text('')
            self.event_conf_field.set_text('')
            self.event_delete_btn.set_sensitive(0)
            self.event_edit_btn.set_sensitive(0)

    def on_addr_select_row(self,obj):
        store,iter = self.ptree.get_selected()
        if iter:
            addr = self.ptree.get_object(iter)
            self.addr_start.set_text(addr.getDate())
            self.addr_street.set_text(addr.getStreet())
            self.addr_city.set_text(addr.getCity())
            self.addr_state.set_text(addr.getState())
            self.addr_country.set_text(addr.getCountry())
            self.addr_postal.set_text(addr.getPostal())
            self.addr_phone.set_text(addr.getPhone())
            if len(addr.getSourceRefList()) > 0:
                psrc = addr.getSourceRefList()[0]
                self.addr_conf_field.set_text(const.confidence[psrc.getConfidence()])
                self.addr_src_field.set_text(short(psrc.getBase().getTitle()))
            else:
                self.addr_src_field.set_text('')
                self.addr_conf_field.set_text('')
            self.addr_delete_btn.set_sensitive(1)
            self.addr_edit_btn.set_sensitive(1)
        else:
            self.addr_start.set_text('')
            self.addr_street.set_text('')
            self.addr_city.set_text('')
            self.addr_state.set_text('')
            self.addr_country.set_text('')
            self.addr_postal.set_text('')
            self.addr_phone.set_text('')
            self.addr_conf_field.set_text('')
            self.addr_src_field.set_text('')
            self.addr_delete_btn.set_sensitive(0)
            self.addr_edit_btn.set_sensitive(0)

    def on_name_select_row(self,obj):
        store,iter = self.ntree.get_selected()
        if iter:
            name = self.ntree.get_object(iter)
            self.alt_given_field.set_text(name.getFirstName())
            self.alt_title_field.set_text(name.getTitle())
            self.alt_last_field.set_text(name.getSurname())
            self.alt_suffix_field.set_text(name.getSuffix())
            self.alt_prefix_field.set_text(name.getSurnamePrefix())
            self.name_type_field.set_text(const.InverseNameTypesMap[name.getType()])
            if len(name.getSourceRefList()) > 0:
                psrc = name.getSourceRefList()[0]
                self.name_src_field.set_text(short(psrc.getBase().getTitle()))
                self.name_conf_field.set_text(const.confidence[psrc.getConfidence()])
            else:
                self.name_src_field.set_text('')
                self.name_conf_field.set_text('')
            self.name_delete_btn.set_sensitive(1)
            self.name_edit_btn.set_sensitive(1)
        else:
            self.alt_given_field.set_text('')
            self.alt_title_field.set_text('')
            self.alt_last_field.set_text('')
            self.alt_suffix_field.set_text('')
            self.alt_prefix_field.set_text('')
            self.name_type_field.set_text('')
            self.name_src_field.set_text('')
            self.name_conf_field.set_text('')
            self.name_delete_btn.set_sensitive(0)
            self.name_edit_btn.set_sensitive(0)

    def on_web_select_row(self,obj):
        store,iter = self.wtree.get_selected()
        if iter:
            url = self.wtree.get_object(iter)
            path = url.get_path()
            self.web_url.set_text(path)
            self.web_description.set_text(url.get_description())
            self.web_go.set_sensitive(0)
            self.web_go.set_sensitive(1)
            self.web_delete_btn.set_sensitive(1)
            self.web_edit_btn.set_sensitive(1)
        else:
            self.web_url.set_text('')
            self.web_description.set_text('')
            self.web_go.set_sensitive(0)
            self.web_delete_btn.set_sensitive(0)
            self.web_edit_btn.set_sensitive(0)
            
    def on_attr_select_row(self,obj):
        store,iter = self.atree.get_selected()
        if iter:
            attr = self.atree.get_object(iter)
            self.attr_type.set_text(const.display_pattr(attr.getType()))
            self.attr_value.set_text(short(attr.getValue()))
            if len(attr.getSourceRefList()) > 0:
                psrc = attr.getSourceRefList()[0]
                self.attr_src_field.set_text(short(psrc.getBase().getTitle()))
                self.attr_conf_field.set_text(const.confidence[psrc.getConfidence()])
            else:
                self.attr_src_field.set_text('')
                self.attr_conf_field.set_text('')
            self.attr_delete_btn.set_sensitive(1)
            self.attr_edit_btn.set_sensitive(1)
        else:
            self.attr_type.set_text('')
            self.attr_value.set_text('')
            self.attr_src_field.set_text('')
            self.attr_conf_field.set_text('')
            self.attr_delete_btn.set_sensitive(0)
            self.attr_edit_btn.set_sensitive(0)

    def aka_double_click(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_aka_update_clicked(obj)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu = gtk.Menu()
            item = gtk.TearoffMenuItem()
            item.show()
            menu.append(item)
            msg = _("Make the selected name the preferred name")
            Utils.add_menuitem(menu,msg,None,self.change_name)
            menu.popup(None,None,None,event.button,event.time)

    def on_aka_update_clicked(self,obj):
        import NameEdit
        store,iter = self.ntree.get_selected()
        if iter:
            NameEdit.NameEditor(self,self.ntree.get_object(iter),self.name_edit_callback,self.window)

    def load_photo(self,photo):
        """loads, scales, and displays the person's main photo"""
        self.load_obj = photo
        if photo == None:
            self.get_widget("personPix").hide()
        else:
            try:
                i = pixbuf_new_from_file(photo)
                ratio = float(max(i.get_height(),i.get_width()))
                scale = float(const.picWidth)/ratio
                x = int(scale*(i.get_width()))
                y = int(scale*(i.get_height()))
                i = i.scale_simple(x,y,INTERP_BILINEAR)
                self.get_widget("personPix").set_from_pixbuf(i)
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
        surname = unicode(self.surname_field.get_text())
        suffix = unicode(self.suffix.get_text())
        prefix = unicode(self.prefix.get_text())
        ntype = unicode(self.ntype_field.entry.get_text())
        given = unicode(self.given.get_text())
        nick = unicode(self.nick.get_text())
        title = unicode(self.title.get_text())
        idval = unicode(self.gid.get_text())

        name = self.pname

        self.birth.setDate(unicode(self.bdate.get_text()))
        self.birth.setPlace(self.get_place(self.bplace,1))

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
                msg2 = _("You have attempted to change the GRAMPS ID to a value "
                         "of %(grampsid)s. This value is already used by %(person)s.") % {
                    'grampsid' : idval,
                    'person' : n }
                WarningDialog(msg1,msg2)

        if suffix != name.getSuffix():
            name.setSuffix(suffix)

        if prefix != name.getSurnamePrefix():
            name.setSurnamePrefix(prefix)

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

        self.pdmap.clear()
        for key in self.db.getPlaceKeys():
            p = self.db.getPlaceDisplay(key)
            self.pdmap[p[0]] = key

        if not self.person.getBirth().are_equal(self.birth):
            self.person.setBirth(self.birth)
            Utils.modified()

        # Update each of the families child lists to reflect any
        # change in ordering due to the new birth date
        family = self.person.getMainParents()
        if (family):
            new_order = reorder_child_list(self.person,family.getChildList())
            family.setChildList(new_order)
        for (family, rel1, rel2) in self.person.getParentList():
            new_order = reorder_child_list(self.person,family.getChildList())
            family.setChildList(new_order)
    
        self.death.setDate(unicode(self.ddate.get_text()))
        self.death.setPlace(self.get_place(self.dplace,1))

        if not self.person.getDeath().are_equal(self.death):
            self.person.setDeath(self.death)
            Utils.modified()

        male = self.is_male.get_active()
        female = self.is_female.get_active()
        unknown = self.is_unknown.get_active()
        error = 0
        if male and self.person.getGender() != RelLib.Person.male:
            self.person.setGender(RelLib.Person.male)
            for temp_family in self.person.getFamilyList():
                if self.person == temp_family.getMother():
                    if temp_family.getFather() != None:
                        error = 1
                    else:
                        temp_family.setMother(None)
                        temp_family.setFather(self.person)
            Utils.modified()
        elif female and self.person.getGender() != RelLib.Person.female:
            self.person.setGender(RelLib.Person.female)
            for temp_family in self.person.getFamilyList():
                if self.person == temp_family.getFather():
                    if temp_family.getMother() != None:
                        error = 1
                    else:
                        temp_family.setFather(None)
                        temp_family.setMother(self.person)
            Utils.modified()
        elif unknown and self.person.getGender() != RelLib.Person.unknown:
            self.person.setGender(RelLib.Person.unknown)
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
            msg2 = _("Problem changing the gender")
            msg = _("Changing the gender caused problems "
                    "with marriage information.\nPlease check "
                    "the person's marriages.")
            ErrorDialog(msg)

        text = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                          self.notes_buffer.get_end_iter(),gtk.FALSE))

        if text != self.person.getNote():
            self.person.setNote(text)
            Utils.modified()

        format = self.preform.get_active()
        if format != self.person.getNoteFormat():
            self.person.setNoteFormat(format)
            Utils.modified()

        if self.complete.get_active() != self.person.getComplete():
            self.person.setComplete(self.complete.get_active())
            Utils.modified()

        if self.lds_not_loaded == 0:
            self.check_lds()
            ord = RelLib.LdsOrd(self.person.getLdsBaptism())
            if not self.lds_baptism.are_equal(ord):
                self.person.setLdsBaptism(self.lds_baptism)
                Utils.modified()

            ord = RelLib.LdsOrd(self.person.getLdsEndowment())
            if not self.lds_endowment.are_equal(ord):
                self.person.setLdsEndowment(self.lds_endowment)
                Utils.modified()

            ord = RelLib.LdsOrd(self.person.getLdsSeal())
            if not self.lds_sealing.are_equal(ord):
                self.person.setLdsSeal(self.lds_sealing)
                Utils.modified()

        if self.lists_changed:
            self.person.setSourceRefList(self.srcreflist)
            Utils.modified()

        self.update_lists()
        if self.callback:
            self.callback(self)

        self.gallery.close()
        self.window.destroy()

    def get_place(self,field,makenew=0):
        text = unicode(string.strip(field.get_text()))
        if text:
            if self.pdmap.has_key(text):
                return self.db.getPlaceMap()[self.pdmap[text]]
            elif makenew:
                place = RelLib.Place()
                place.set_title(text)
                self.db.addPlace(place)
                self.pdmap[text] = place.getId()
                self.add_places.append(place)
                Utils.modified()
                return place
            else:
                return None
        else:
            return None

    def on_primary_name_source_clicked(self,obj):
        Sources.SourceSelector(self.pname.getSourceRefList(),self,
                               self.update_primary_name)

    def update_primary_name(self,list):
        self.pname.setSourceRefList(list)
        self.lists_changed = 1

    def on_name_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.pname,self.window)

    def on_ldsbap_source_clicked(self,obj):
        Sources.SourceSelector(self.lds_baptism.getSourceRefList(),
                               self,self.update_ldsbap_list)

    def update_ldsbap_list(self,list):
        self.lds_baptism.setSourceRefList(list)
        self.lists_changed = 1
        
    def on_ldsbap_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.lds_baptism,self.window)

    def on_ldsendow_source_clicked(self,obj):
        Sources.SourceSelector(self.lds_endowment.getSourceRefList(),
                               self,self.set_ldsendow_list)

    def set_ldsendow_list(self,list):
        self.lds_endowment.setSourceRefList(list)
        self.lists_changed = 1

    def on_ldsendow_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.lds_endowment,self.window)

    def on_ldsseal_source_clicked(self,obj):
        Sources.SourceSelector(self.lds_sealing.getSourceRefList(),
                               self,self.lds_seal_list)

    def lds_seal_list(self,list):
        self.lds_sealing.setSourceRefList(list)
        self.lists_changed = 1

    def on_ldsseal_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.lds_sealing,self.window)

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
        elif page == 2:
            self.redraw_event_list()
        elif page == 7 and self.not_loaded:
            self.not_loaded = 0
        elif page == 9 and self.lds_not_loaded:
            self.lds_not_loaded = 0
            self.draw_lds()
        text = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                            self.notes_buffer.get_end_iter(),gtk.FALSE))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)

        if self.lds_not_loaded == 0:
            self.check_lds()
        if self.lds_baptism.isEmpty() \
                        and self.lds_endowment.isEmpty() \
                        and self.lds_sealing.isEmpty():
            Utils.unbold_label(self.lds_tab)
        else:
            Utils.bold_label(self.lds_tab)

    def change_name(self,obj):
        sel_objs = self.ntree.get_selected_objects()
        if sel_objs:
            old = self.pname
            new = sel_objs[0]
            self.nlist.remove(new)
            self.nlist.append(old)
            self.redraw_name_list()
            self.pname = RelLib.Name(new)
            self.lists_changed = 1
            self.write_primary_name()

    def write_primary_name(self):
        # initial values
        name = '<span size="larger" weight="bold">%s</span>' % GrampsCfg.nameof(self.person)
        self.get_widget("activepersonTitle").set_text(name)
        self.get_widget("activepersonTitle").set_use_markup(gtk.TRUE)
        self.suffix.set_text(self.pname.getSuffix())
        self.prefix.set_text(self.pname.getSurnamePrefix())

        self.surname_field.set_text(self.pname.getSurname())
        self.given.set_text(self.pname.getFirstName())

        self.ntype_field.entry.set_text(_(self.pname.getType()))
        self.title.set_text(self.pname.getTitle())

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


def short(val,size=60):
    if len(val) > size:
        return "%s..." % val[0:size]
    else:
        return val
