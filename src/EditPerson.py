#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
import pickle
import os

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gobject
import gnome
import locale

from gtk.gdk import ACTION_COPY, BUTTON1_MASK, INTERP_BILINEAR, pixbuf_new_from_file

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsKeys
import GrampsMime
import ImageSelect
import AutoComp
import ListModel
import RelLib
import Sources
import DateEdit
import Date
import DateHandler
import TransTable
import NameDisplay

from QuestionDialog import WarningDialog, ErrorDialog, SaveDialog

from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

_PICTURE_WIDTH = 200.0

_temple_names = const.lds_temple_codes.keys()
_temple_names.sort()
_temple_names = [""] + _temple_names

pycode_tgts = [('url', 0, 0),
               ('pevent', 0, 1),
               ('pattr', 0, 2),
               ('paddr', 0, 3)]


_use_patronymic = [
    "ru","RU","ru_RU","koi8r","ru_koi8r","russian","Russian",
    ]
    
#-------------------------------------------------------------------------
#
# EditPerson class
#
#-------------------------------------------------------------------------
class EditPerson:

    use_patronymic = locale.getlocale(locale.LC_TIME)[0] in _use_patronymic
    
    def __init__(self,parent,person,db,callback=None):
        """Creates an edit window.  Associates a person with the window."""

        self.dp = DateHandler.parser
        self.dd = DateHandler.displayer
        self.person = person
        self.orig_surname = person.get_primary_name().get_group_name()
        self.parent = parent
        self.orig_handle = self.person.get_handle()
        if self.parent.child_windows.has_key(self.orig_handle):
            self.parent.child_windows[self.person.get_handle()].present(None)
            return
        self.db = db
        self.callback = callback
        self.child_windows = {}
        self.path = db.get_save_path()
        self.not_loaded = True
        self.lds_not_loaded = True
        self.lists_changed = False
        self.update_birth = False
        self.update_death = False
        self.pdmap = {}
        self.add_places = []
        self.name_display = NameDisplay.displayer
        self.should_guess_gender = (person.get_gramps_id() == '' and
                                    person.get_gender () ==
                                    RelLib.Person.UNKNOWN)

        for key in db.get_place_handles():
            p = db.get_place_from_handle(key).get_display_info()
            self.pdmap[p[0]] = key

        mod = not self.db.readonly
            
        self.load_obj = None
        self.top = gtk.glade.XML(const.editPersonFile, "editPerson","gramps")
        self.window = self.get_widget("editPerson")
        self.window.set_title("%s - GRAMPS" % _('Edit Person'))
        
        self.icon_list = self.top.get_widget("iconlist")
        self.gallery = ImageSelect.Gallery(person, self.db.commit_person,
                                           self.path, self.icon_list,
                                           self.db, self, self.window)

        self.complete = self.get_widget('complete')
        self.complete.set_sensitive(mod)
        self.private = self.get_widget('private')
        self.private.set_sensitive(mod)
        self.name_delete_btn = self.top.get_widget('aka_delete')
        self.name_edit_btn = self.top.get_widget('aka_edit')
        self.web_delete_btn = self.top.get_widget('delete_url')
        self.web_edit_btn = self.top.get_widget('edit_url')
        self.event_delete_btn = self.top.get_widget('event_del')
        self.event_edit_btn = self.top.get_widget('event_edit_btn')
        self.attr_delete_btn = self.top.get_widget('attr_delete_btn')
        self.attr_edit_btn = self.top.get_widget('attr_edit_btn')
        self.addr_delete_btn = self.top.get_widget('addr_delete_btn')
        self.addr_edit_btn = self.top.get_widget('addr_edit_btn')

        self.notes_field = self.get_widget("personNotes")
        self.notes_field.set_editable(mod)
        self.flowed = self.get_widget("flowed")
        self.flowed.set_sensitive(mod)
        self.preform = self.get_widget("preform")
        self.preform.set_sensitive(mod)
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
        self.ntype_field = self.get_widget("ntype")
        self.ntype_field.set_sensitive(mod)
        self.suffix = self.get_widget("suffix")
        self.suffix.set_editable(mod)
        self.prefix = self.get_widget("prefix")
        self.prefix.set_editable(mod)
        self.given = self.get_widget("givenName")
        self.given.set_editable(mod)
        self.nick = self.get_widget("nickname")
        self.nick.set_editable(mod)
        self.title = self.get_widget("title")
        self.title.set_editable(mod)
        self.bdate  = self.get_widget("birthDate")
        self.bdate.set_editable(mod)
        self.bplace = self.get_widget("birth_place")
        self.bplace.set_editable(mod)
        self.surname = self.get_widget("surname")
        self.surname.set_editable(mod)
        self.ddate  = self.get_widget("deathDate")
        self.ddate.set_editable(mod)
        self.dplace = self.get_widget("death_place")
        self.dplace.set_editable(mod)
        self.is_male = self.get_widget("genderMale")
        self.is_male.set_sensitive(mod)
        self.is_female = self.get_widget("genderFemale")
        self.is_female.set_sensitive(mod)
        self.is_unknown = self.get_widget("genderUnknown")
        self.is_unknown.set_sensitive(mod)
        self.addr_note = self.get_widget("addr_note")
        self.addr_source = self.get_widget("addr_source")
        self.attr_note = self.get_widget("attr_note")
        self.attr_source = self.get_widget("attr_source")
        self.name_note = self.get_widget("name_note")
        self.name_source = self.get_widget("name_source")
        self.gid = self.get_widget("gid")
        self.gid.set_editable(mod)
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
        self.person_photo = self.get_widget("personPix")
        self.eventbox = self.get_widget("eventbox1")

        self.get_widget("birth_stat").set_sensitive(mod)
        self.get_widget("death_stat").set_sensitive(mod)

        self.prefix_label = self.get_widget('prefix_label')

        if self.use_patronymic:
            self.prefix_label.set_text(_('Patronymic:'))
            self.prefix_label.set_use_underline(True)

        birth_handle = person.get_birth_handle()
        death_handle = person.get_death_handle()
        self.orig_birth = self.db.get_event_from_handle(birth_handle)
        self.orig_death = self.db.get_event_from_handle(death_handle)
        self.death = RelLib.Event(self.orig_death)
        self.birth = RelLib.Event(self.orig_birth)
        self.pname = RelLib.Name(person.get_primary_name())

        self.elist = person.get_event_list()[:]
        self.nlist = person.get_alternate_names()[:]
        self.alist = person.get_attribute_list()[:]
        self.ulist = person.get_url_list()[:]
        self.plist = person.get_address_list()[:]

        if person:
            self.srcreflist = person.get_source_references()
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
        if self.person.get_media_list():
            Utils.bold_label(self.gallery_label)

        # event display

        event_default = [ 'Event', 'Description', 'Date', 'Place' ]
        self.event_trans = TransTable.TransTable(event_default)
        evalues = {
            'Event'       : (_('Event'),-1,150),
            'Description' : (_('Description'),-1,150),
            'Date'        : (_('Date'),-1,100),
            'Place'       : (_('Place'),-1,100)
            }

        if not self.db.readonly:
            values = self.db.metadata.get('event_order',event_default)
        else:
            values = event_default

        etitles = []
        for val in values:
            etitles.append(evalues[val])
            
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

        self.place_list = self.pdmap.keys()
        self.place_list.sort()

        build_dropdown(self.bplace,self.place_list)
        build_dropdown(self.dplace,self.place_list)
        build_dropdown(self.surname,self.db.get_surname_list())

        gid = person.get_gramps_id()
        if gid:
            self.gid.set_text(gid)
        self.gid.set_editable(1)

        self.lds_baptism = RelLib.LdsOrd(self.person.get_lds_baptism())
        self.lds_endowment = RelLib.LdsOrd(self.person.get_lds_endowment())
        self.lds_sealing = RelLib.LdsOrd(self.person.get_lds_sealing())

        if GrampsKeys.get_uselds() \
                        or (not self.lds_baptism.is_empty()) \
                        or (not self.lds_endowment.is_empty()) \
                        or (not self.lds_sealing.is_empty()):
            self.get_widget("lds_tab").show()
            self.get_widget("lds_page").show()
            if (not self.lds_baptism.is_empty()) \
                        or (not self.lds_endowment.is_empty()) \
                        or (not self.lds_sealing.is_empty()):
                Utils.bold_label(self.lds_tab)

        types = const.NameTypesMap.get_values()
        types.sort()
        AutoComp.fill_combo(self.ntype_field,types)
        self.write_primary_name()
        
        if person.get_gender() == RelLib.Person.MALE:
            self.is_male.set_active(1)
        elif person.get_gender() == RelLib.Person.FEMALE:
            self.is_female.set_active(1)
        else:
            self.is_unknown.set_active(1)

        self.nick.set_text(person.get_nick_name())
        self.load_person_image()
        
        # set notes data
        self.notes_buffer = self.notes_field.get_buffer()
        if person.get_note():
            self.notes_buffer.set_text(person.get_note())
            if person.get_note_object().get_format() == 1:
                self.preform.set_active(1)
            else:
                self.flowed.set_active(1)
            Utils.bold_label(self.notes_label)

        self.event_list.drag_dest_set(gtk.DEST_DEFAULT_ALL, pycode_tgts,
                                      ACTION_COPY)
        self.event_list.drag_source_set(BUTTON1_MASK, pycode_tgts, ACTION_COPY)
        self.event_list.connect('drag_data_get', self.ev_drag_data_get)
        self.event_list.connect('drag_begin', self.ev_drag_begin)
        self.event_list.connect('drag_data_received',
                                self.ev_drag_data_received)

        self.web_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,pycode_tgts,
                                    ACTION_COPY)
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

        self.birth_date_object = self.birth.get_date_object()
        self.death_date_object = self.death.get_date_object()
        self.update_birth_death()

        self.bdate_check = DateEdit.DateEdit(self.birth_date_object,
                                            self.bdate,
                                            self.get_widget("birth_stat"),
                                            self.window)

        self.ddate_check = DateEdit.DateEdit(self.death_date_object,
                                            self.ddate,
                                            self.get_widget("death_stat"),
                                            self.window)

        self.top.signal_autoconnect({
            "destroy_passed_object"     : self.on_cancel_edit,
            "on_up_clicked"             : self.on_up_clicked,
            "on_down_clicked"           : self.on_down_clicked,
            "on_add_address_clicked"    : self.on_add_addr_clicked,
            "on_add_aka_clicked"        : self.on_add_aka_clicked,
            "on_add_attr_clicked"       : self.on_add_attr_clicked,
            "on_add_url_clicked"        : self.on_add_url_clicked,
            "on_addphoto_clicked"       : self.gallery.on_add_media_clicked,
            "on_selectphoto_clicked"    : self.gallery.on_select_media_clicked,
            "on_aka_delete_clicked"     : self.on_aka_delete_clicked,
            "on_aka_update_clicked"     : self.on_aka_update_clicked,
            "on_apply_person_clicked"   : self.on_apply_person_clicked,
            "on_edit_birth_clicked"     : self.on_edit_birth_clicked,
            "on_edit_death_clicked"     : self.on_edit_death_clicked,
            "on_delete_address_clicked" : self.on_delete_addr_clicked,
            "on_delete_attr_clicked"    : self.on_delete_attr_clicked,
            "on_delete_event"           : self.on_delete_event,
            "on_delete_url_clicked"     : self.on_delete_url_clicked,
            "on_deletephoto_clicked"    : self.gallery.on_delete_media_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_editphoto_clicked"      : self.gallery.on_edit_media_clicked,
            "on_editperson_switch_page" : self.on_switch_page,
            "on_event_add_clicked"      : self.on_event_add_clicked,
            "on_event_delete_clicked"   : self.on_event_delete_clicked,
            "on_event_update_clicked"   : self.on_event_update_clicked,
            "on_edit_name_clicked"      : self.on_edit_name_clicked,
            "on_ldsbap_note_clicked"    : self.on_ldsbap_note_clicked,
            "on_ldsendow_note_clicked"  : self.on_ldsendow_note_clicked,
            "on_ldsseal_note_clicked"   : self.on_ldsseal_note_clicked,
            "on_ldsbap_src_clicked"     : self.on_ldsbap_source_clicked,
            "on_ldsendow_src_clicked"   : self.on_ldsendow_source_clicked,
            "on_ldsseal_src_clicked"    : self.on_ldsseal_source_clicked,
            "on_update_address_clicked" : self.on_update_addr_clicked,
            "on_update_attr_clicked"    : self.on_update_attr_clicked,
            "on_update_url_clicked"     : self.on_update_url_clicked,
            "on_web_go_clicked"         : self.on_web_go_clicked,
            "on_gender_activate"        : self.on_gender_activate,
            "on_given_focus_out"        : self.on_given_focus_out_event,
            "on_help_person_clicked"    : self.on_help_clicked,
            })

        self.sourcetab = Sources.SourceTab(self.srcreflist,self,
                                           self.top,self.window,self.slist,
                                           self.top.get_widget('add_src'),
                                           self.top.get_widget('edit_src'),
                                           self.top.get_widget('del_src'))

        self.complete.set_active(self.person.get_complete_flag())
        self.private.set_active(self.person.get_privacy())

        self.eventbox.connect('button-press-event',self.image_button_press)

        self.redraw_event_list()
        self.redraw_attr_list()
        self.redraw_addr_list() 
        self.redraw_name_list()
        self.redraw_url_list()
        self.get_widget("notebook").set_current_page(0)
        self.given.grab_focus()
        self.add_itself_to_winsmenu()

        for i in ["ok", "add_aka", "aka_delete", "event_del",
                  "event_add", "attr_add", "attr_del", "addr_add",
                  "addr_del", "media_add", "media_sel", "media_del",
                  "add_url", "delete_url", "add_src", "del_src" ]:
            self.get_widget(i).set_sensitive(not self.db.readonly)

        self.window.show()

    def image_button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:

            media_list = self.person.get_media_list()
            if media_list:
                ph = media_list[0]
                object_handle = ph.get_reference_handle()
                obj = self.db.get_object_from_handle(object_handle)
                ImageSelect.LocalMediaProperties(ph,obj.get_path(),
                                                 self,self.window)

        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            media_list = self.person.get_media_list()
            if media_list:
                ph = media_list[0]
                self.show_popup(ph,event)

    def show_popup(self, photo, event):
        """Look for right-clicks on a picture and create a popup
        menu of the available actions."""
        
        menu = gtk.Menu()
        menu.set_title(_("Media Object"))
        obj = self.db.get_object_from_handle(photo.get_reference_handle())
        mtype = obj.get_mime_type()
        progname = GrampsMime.get_application(mtype)
        
        if progname and len(progname) > 1:
            Utils.add_menuitem(menu,_("Open in %s") % progname[1],
                               photo,self.popup_view_photo)
        if mtype[0:5] == "image":
            Utils.add_menuitem(menu,_("Edit with the GIMP"),
                               photo,self.popup_edit_photo)
        Utils.add_menuitem(menu,_("Edit Object Properties"),photo,
                           self.popup_change_description)
        menu.popup(None,None,None,event.button,event.time)

    def popup_view_photo(self, obj):
        """Open this picture in a picture viewer"""
        media_list = self.person.get_media_list()
        if media_list:
            ph = media_list[0]
            object_handle = ph.get_reference_handle()
            Utils.view_photo(self.db.get_object_from_handle(object_handle))

    def popup_edit_photo(self, obj):
        """Open this picture in a picture editor"""
        media_list = self.person.get_media_list()
        if media_list:
            ph = media_list[0]
            object_handle = ph.get_reference_handle()
            if os.fork() == 0:
                obj = self.db.get_object_from_handle(object_handle)
                os.execvp(const.editor,[const.editor, obj.get_path()])

    def popup_change_description(self,obj):
        media_list = self.person.get_media_list()
        if media_list:
            ph = media_list[0]
            object_handle = ph.get_reference_handle()
            obj = self.db.get_object_from_handle(object_handle)
            ImageSelect.LocalMediaProperties(ph,obj.get_path(),self,self.window)

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def close(self):
        event_list = []
        for col in self.event_list.get_columns():
            event_list.append(self.event_trans.find_key(col.get_title()))
        if not self.db.readonly:
            self.db.metadata['event_order'] = event_list
        
        self.gallery.close()
        self.close_child_windows()
        self.remove_itself_from_winsmenu()
        self.window.destroy()

    def add_itself_to_winsmenu(self):
        self.parent.child_windows[self.orig_handle] = self
        win_menu_label = self.name_display.display(self.person)
        if not win_menu_label.strip():
            win_menu_label = _("New Person")
        self.win_menu_item = gtk.MenuItem(win_menu_label)
        self.win_menu_item.set_submenu(gtk.Menu())
        self.win_menu_item.show()
        self.parent.winsmenu.append(self.win_menu_item)
        self.winsmenu = self.win_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Edit Person'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_winsmenu(self):
        del self.parent.child_windows[self.orig_handle]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.win_menu_item.destroy()

    def present(self,obj):
        self.window.present()

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

    def lds_field(self,lds_ord,combo,date,place):
        build_combo(combo,_temple_names)
        temple_code = const.lds_temple_to_abrev.get(lds_ord.get_temple(),"")
        index = _temple_names.index(temple_code)
        combo.set_active(index)
        if not lds_ord.is_empty():
            stat = lds_ord.get_status()
            date.set_text(lds_ord.get_date())
        else:
            stat = 0

        build_dropdown(place,self.place_list)
        if lds_ord and lds_ord.get_place_handle():
            lds_ord_place = self.db.get_place_from_handle(lds_ord.get_place_handle())
            place.set_text(lds_ord_place.get_title())
        return stat

    def draw_lds(self):
        """Draws the LDS window. This window is not always drawn, and in
        may cases is hidden."""

        self.ldsbap_date = self.get_widget("ldsbapdate")
        self.ldsbap_date.set_editable(not self.db.readonly)
        self.ldsbap_temple = self.get_widget("ldsbaptemple")
        self.ldsbap_temple.set_sensitive(not self.db.readonly)
        self.ldsbapplace = self.get_widget("lds_bap_place")
        self.ldsbapplace.set_editable(not self.db.readonly)

        self.ldsend_date = self.get_widget("endowdate")
        self.ldsend_date.set_editable(not self.db.readonly)
        self.ldsend_temple = self.get_widget("endowtemple")
        self.ldsend_temple.set_sensitive(not self.db.readonly)
        self.ldsendowplace = self.get_widget("lds_end_place")
        self.ldsendowplace.set_editable(not self.db.readonly)
        self.ldsendowstat = self.get_widget("endowstat")
        self.ldsendowstat.set_sensitive(not self.db.readonly)

        self.ldsseal_date = self.get_widget("sealdate")
        self.ldsseal_temple = self.get_widget("sealtemple")
        self.ldssealplace = self.get_widget("lds_seal_place")
        self.ldsseal_date.set_editable(not self.db.readonly)
        self.ldsseal_temple.set_sensitive(not self.db.readonly)
        self.ldssealplace.set_editable(not self.db.readonly)
        
        self.ldsseal_fam = self.get_widget("sealparents")
        self.ldsseal_fam.set_sensitive(not self.db.readonly)
        
        self.ldsbapstat = self.get_widget("ldsbapstat")
        self.ldsbapstat.set_sensitive(not self.db.readonly)

        self.ldssealstat = self.get_widget("sealstat")
        self.ldssealstat.set_sensitive(not self.db.readonly)


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
            self.ldsfam = self.lds_sealing.get_family_handle()
        else:
            self.ldsfam = None

        cell = gtk.CellRendererText()
        self.ldsseal_fam.pack_start(cell,True)
        self.ldsseal_fam.add_attribute(cell,'text',0)

        store = gtk.ListStore(str)
        store.append(row=[_("None")])
        
        index = 0
        hist = 0
        self.lds_fam_list = [None]
        flist = [self.person.get_main_parents_family_handle()]
        for (fam,mrel,frel) in self.person.get_parent_family_handle_list():
            if fam not in flist:
                flist.append(fam)

        for fam_id in flist:
            index += 1
            fam = self.db.get_family_from_handle(fam_id)
            if fam == None:
                continue
            f_id = fam.get_father_handle()
            m_id = fam.get_mother_handle()
            f = self.db.get_person_from_handle(f_id)
            m = self.db.get_person_from_handle(m_id)
            if f and m:
                name = _("%(father)s and %(mother)s") % {
                    'father' : self.name_display.display(f),
                    'mother' : self.name_display.display(m) }
            elif f:
                name = self.name_display.display(f)
            elif m:
                name = self.name_display.display(m)
            else:
                name = _("unknown")
            store.append(row=[name])
            self.lds_fam_list.append(fam_id)
            if fam_id == self.ldsfam:
                hist = index
        self.ldsseal_fam.set_model(store)
        self.ldsseal_fam.set_active(hist)
        self.ldsseal_fam.connect("changed",self.menu_changed)

        self.build_bap_menu()
        self.build_seal_menu()
        self.build_endow_menu()

    def on_gender_activate (self, button):
        self.should_guess_gender = False

    def on_given_focus_out_event (self, entry, event):
        if not self.should_guess_gender:
            return

        gender = self.db.genderStats.guess_gender(unicode(entry.get_text ()))
        if gender == RelLib.Person.UNKNOWN:
            self.is_unknown.set_active(True)
        elif gender == RelLib.Person.MALE:
            self.is_male.set_active(True)
        else:
            self.is_female.set_active(True)

    def build_menu(self,list,task,opt_menu,type):
        cell = gtk.CellRendererText()
        opt_menu.pack_start(cell,True)
        opt_menu.add_attribute(cell,'text',0)

        store = gtk.ListStore(str)
        for val in list:
            store.append(row=[val])
        opt_menu.set_model(store)
        opt_menu.connect('changed',task)
        opt_menu.set_active(type)

    def build_bap_menu(self):
        self.build_menu(const.lds_baptism,self.set_lds_bap,self.ldsbapstat,
                        self.bstat)

    def build_endow_menu(self):
        self.build_menu(const.lds_baptism,self.set_lds_endow,self.ldsendowstat,
                        self.estat)

    def build_seal_menu(self):
        self.build_menu(const.lds_csealing,self.set_lds_seal,self.ldssealstat,
                        self.seal_stat)

                   
    def build_seal_menu(self):
        self.build_menu(const.lds_csealing,self.set_lds_seal,self.ldssealstat,
                        self.seal_stat)

    def set_lds_bap(self,obj):
        self.lds_baptism.set_status(obj.get_active())

    def set_lds_endow(self,obj):
        self.lds_endowment.set_status(obj.get_active())

    def set_lds_seal(self,obj):
        self.lds_sealing.set_status(obj.get_active())
    
    def ev_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.etree.get_row_at(x,y)
        
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if mytype != 'pevent':
                return
            elif person == self.person.get_handle():
                self.move_element(self.elist,self.etree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                for src in foo.get_source_references():
                    base_handle = src.get_base_handle()
                    newbase = self.db.get_source_from_handle(base_handle)
                    src.set_base_handle(newbase)
                place = foo.get_place_handle()
                if place:
                    foo.set_place_handle(place.get_handle())
                self.elist.insert(row,foo)

            self.lists_changed = True
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
        data = str(('pevent',self.person.get_handle(),pickled));
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
            elif person == self.person.get_handle():
                self.move_element(self.ulist,self.wtree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                self.ulist.append(foo)
            self.lists_changed = True
            self.redraw_url_list()

    def url_drag_begin(self, context, a):
        return

    def url_drag_data_get(self,widget, context, sel_data, info, time):
        ev = self.wtree.get_selected_objects()

        if len(ev):
            bits_per = 8; # we're going to pass a string
            pickled = pickle.dumps(ev[0]);
            data = str(('url',self.person.get_handle(),pickled));
            sel_data.set(sel_data.target, bits_per, data)

    def at_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.atree.get_row_at(x,y)

        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if mytype != 'pattr':
                return
            elif person == self.person.get_handle():
                self.move_element(self.alist,self.atree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                for src in foo.get_source_references():
                    base_handle = src.get_base_handle()
                    newbase = self.db.get_source_from_handle(base_handle)
                    src.set_base_handle(newbase)
                self.alist.append(foo)
            self.lists_changed = True
            self.redraw_attr_list()

    def at_drag_begin(self, context, a):
        return

    def at_drag_data_get(self,widget, context, sel_data, info, time):
        ev = self.atree.get_selected_objects()

        if len(ev):
            bits_per = 8; # we're going to pass a string
            pickled = pickle.dumps(ev[0]);
            data = str(('pattr',self.person.get_handle(),pickled));
            sel_data.set(sel_data.target, bits_per, data)
            
    def ad_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.ptree.get_row_at(x,y)

        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if mytype != 'paddr':
                return
            elif person == self.person.get_handle():
                self.move_element(self.plist,self.ptree.get_selected_row(),row)
            else:
                foo = pickle.loads(data[2]);
                for src in foo.get_source_references():
                    base_handle = src.get_base_handle()
                    newbase = self.db.get_source_from_handle(base_handle)
                    src.set_base_handle(newbase)
                self.plist.insert(row,foo)
                
            self.lists_changed = True
            self.redraw_addr_list()

    def ad_drag_data_get(self,widget, context, sel_data, info, time):
        ev = self.ptree.get_selected_objects()
        
        if len(ev):
            bits_per = 8; # we're going to pass a string
            pickled = pickle.dumps(ev[0]);
            data = str(('paddr',self.person.get_handle(),pickled));
            sel_data.set(sel_data.target, bits_per, data)

    def ad_drag_begin(self, context, a):
        return

    def menu_changed(self,obj):
        self.ldsfam = self.lds_fam_list[obj.get_active()]
        
    def get_widget(self,str):
        """returns the widget related to the passed string"""
        return self.top.get_widget(str)

    def redraw_name_list(self):
        """redraws the name list"""
        self.ntree.clear()
        self.nmap = {}
        for name in self.nlist:
            node = self.ntree.add([name.get_name(),_(name.get_type())],name)
            self.nmap[str(name)] = node
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
            node = self.wtree.add([url.get_path(),url.get_description()],url)
            self.wmap[str(url)] = node
            
        if len(self.ulist) > 0:
            self.web_go.set_sensitive(False)
            self.wtree.select_row(0)
            Utils.bold_label(self.inet_label)
        else:
            self.web_go.set_sensitive(False)
            self.web_url.set_text("")
            self.web_description.set_text("")
            Utils.unbold_label(self.inet_label)

    def redraw_addr_list(self):
        """Redraws the address list"""
        self.ptree.clear()
        self.pmap = {}
        for addr in self.plist:
            location = "%s %s %s %s" % (addr.get_street(),addr.get_city(),
                                        addr.get_state(),addr.get_country())
            node = self.ptree.add([addr.get_date(),location],addr)
            self.pmap[str(addr)] = node
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
            node = self.atree.add([const.display_pattr(attr.get_type()),attr.get_value()],attr)
            self.amap[str(attr)] = node
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
        for event_handle in self.elist:
            event = self.db.get_event_from_handle(event_handle)
            pname = place_title(self.db,event)
            node = self.etree.add([const.display_pevent(event.get_name()),
                                   event.get_description(),
                                   event.get_date(),pname],event)
            self.emap[str(event)] = node
        if self.elist:
            self.etree.select_row(0)
            Utils.bold_label(self.events_label)
        else:
            Utils.unbold_label(self.events_label)

        # Remember old combo list input

        bplace_text = unicode(self.bplace.get_text())
        dplace_text = unicode(self.dplace.get_text())
            
        prev_btext = self.strip_id(bplace_text)
        prev_dtext = self.strip_id(dplace_text)

        # Update birth with new values, make sure death values don't change
        if self.update_birth:
            self.update_birth = False
            self.update_birth_info()
            self.dplace.set_text(prev_dtext)

        # Update death with new values, make sure birth values don't change
        if self.update_death:
            self.update_death = False
            self.update_death_info()
            self.bplace.set_text(prev_btext)

    def strip_id(self,text):
        index = text.rfind('[')
        if (index > 0):
            text = text[:index]
            text = text.rstrip()
        return text

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
        pname = self.name_display.display(self.person)
        UrlEdit.UrlEditor(self,pname,None,self.url_edit_callback,self.window)

    def on_add_attr_clicked(self,obj):
        """Brings up the AttributeEditor for a new attribute"""
        import AttrEdit
        pname = self.name_display.display(self.person)
        AttrEdit.AttributeEditor(self,None,pname,const.personalAttributes,
                                 self.attr_edit_callback,self.window)

    def on_up_clicked(self,obj):
        sel = obj.get_selection()
        store,node = sel.get_selected()
        if node:
            row = store.get_path(node)
            sel.select_path((row[0]-1))

    def on_down_clicked(self,obj):
        sel = obj.get_selection()
        store,node = sel.get_selected()
        if node:
            row = store.get_path(node)
            sel.select_path((row[0]+1))

    def on_event_add_clicked(self,obj):
        """Brings up the EventEditor for a new event"""
        import EventEdit
        pname = self.name_display.display(self.person)
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.personal_events,None,None,0,
                              self.event_edit_callback,
                              noedit=self.db.readonly)

    def on_edit_birth_clicked(self,obj):
        """Brings up the EventEditor for the birth record, event
        name cannot be changed"""
        
        import EventEdit
        self.update_birth = True
        pname = self.name_display.display(self.person)
        event = self.birth
        event.set_date_object(Date.Date(self.birth_date_object))
        def_placename = unicode(self.bplace.get_text())

        p = self.get_place(self.bplace)
        if p:
            event.set_place_handle(p)
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.personal_events,event,def_placename,1,
                              self.event_edit_callback,
                              noedit=self.db.readonly)
                              

    def on_edit_death_clicked(self,obj):
        """Brings up the EventEditor for the death record, event
        name cannot be changed"""
        
        import EventEdit
        self.update_death = True
        pname = self.name_display.display(self.person)
        event = self.death
        event.set_date_object(Date.Date(self.death_date_object))
        def_placename = unicode(self.dplace.get_text())

        p = self.get_place(self.dplace)
        if p:
            event.set_place_handle(p)
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.personal_events,event,def_placename,1,
                              self.event_edit_callback,
                              noedit=self.db.readonly)

    def on_aka_delete_clicked(self,obj):
        """Deletes the selected name from the name list"""
        store,node = self.ntree.get_selected()
        if node:
            self.nlist.remove(self.ntree.get_object(node))
            self.lists_changed = True
            self.redraw_name_list()

    def on_delete_url_clicked(self,obj):
        """Deletes the selected URL from the URL list"""
        store,node = self.wtree.get_selected()
        if node:
            self.ulist.remove(self.wtree.get_object(node))
            self.lists_changed = True
            self.redraw_url_list()

    def on_delete_attr_clicked(self,obj):
        """Deletes the selected attribute from the attribute list"""
        store,node = self.atree.get_selected()
        if node:
            self.alist.remove(self.atree.get_object(node))
            self.lists_changed = True
            self.redraw_attr_list()

    def on_delete_addr_clicked(self,obj):
        """Deletes the selected address from the address list"""
        store,node = self.ptree.get_selected()
        if node:
            self.plist.remove(self.ptree.get_object(node))
            self.lists_changed = True
            self.redraw_addr_list()

    def on_web_go_clicked(self,obj):
        """Attempts to display the selected URL in a web browser"""
        text = obj.get()
        if text:
            gnome.url_show(text)
        
    def on_cancel_edit(self,obj):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        
        if self.did_data_change() and not GrampsKeys.get_dont_ask():
            n = "<i>%s</i>" % self.person.get_primary_name().get_regular_name()
            SaveDialog(_('Save changes to %s?') % n,
                       _('If you close without saving, the changes you '
                         'have made will be lost'),
                       self.cancel_callback,
                       self.save)
        else:
            self.close()

    def save(self):
        self.on_apply_person_clicked(None)

    def on_delete_event(self,obj,b):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        if self.did_data_change() and not GrampsKeys.get_dont_ask():
            n = "<i>%s</i>" % self.person.get_primary_name().get_regular_name()
            SaveDialog(_('Save Changes to %s?') % n,
                       _('If you close without saving, the changes you '
                         'have made will be lost'),
                       self.cancel_callback,
                       self.save)
            return True
        else:
            self.close()
            return False

    def cancel_callback(self):
        """If the user answered yes to abandoning changes, close the window"""
        self.close()

    def did_data_change(self):
        """Check to see if any of the data has changed from the
        orig record"""

        surname = unicode(self.surname.get_text())
        self.birth.set_date_object(self.birth_date_object)
        self.death.set_date_object(self.death_date_object)

        ntype = unicode(self.ntype_field.child.get_text())
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
        if idval == "":
            idval = None

        changed = False
        name = self.person.get_primary_name()

        if self.complete.get_active() != self.person.get_complete_flag():
            changed = True

        if self.person.get_gramps_id() != idval:
            changed = True
        if suffix != name.get_suffix():
            changed = True
        if self.use_patronymic:
            if prefix != name.get_patronymic():
                changed = True
            elif prefix != name.get_surname_prefix():
                changed = True
        if surname.upper() != name.get_surname().upper():
            changed = True
        if ntype != const.NameTypesMap.find_value(name.get_type()):
            changed = True
        if given != name.get_first_name():
            changed = True
        if nick != self.person.get_nick_name():
            changed = True
        if title != name.get_title():
            changed = True
        if self.pname.get_note() != name.get_note():
            changed = True
        if not self.lds_not_loaded and self.check_lds():
            changed = True

        bplace = unicode(self.bplace.get_text().strip())
        dplace = unicode(self.dplace.get_text().strip())

        if self.pdmap.has_key(bplace):
            self.birth.set_place_handle(self.pdmap[bplace])
        else:
            if bplace != "":
                changed = True
            self.birth.set_place_handle('')

        if self.pdmap.has_key(dplace):
            self.death.set_place_handle(self.pdmap[dplace])
        else:
            if dplace != "":
                changed = True
            self.death.set_place_handle('')

        if not self.birth.are_equal(self.orig_birth):
            changed = True
        if not self.death.are_equal(self.orig_death):
            changed = True
        if male and self.person.get_gender() != RelLib.Person.MALE:
            changed = True
        elif female and self.person.get_gender() != RelLib.Person.FEMALE:
            changed = True
        elif unknown and self.person.get_gender() != RelLib.Person.UNKNOWN:
            changed = True
        if text != self.person.get_note():
            changed = True
        if format != self.person.get_note_format():
            changed = True

        if not self.lds_not_loaded:
            if not self.lds_baptism.are_equal(self.person.get_lds_baptism()):
                changed= True

            if not self.lds_endowment.are_equal(self.person.get_lds_endowment()):
                changed = True

            if not self.lds_sealing.are_equal(self.person.get_lds_sealing()):
                changed = True
                
        return changed

    def check_lds(self):
        self.lds_baptism.set_date(unicode(self.ldsbap_date.get_text()))
        temple = _temple_names[self.ldsbap_temple.get_active()]
        if const.lds_temple_codes.has_key(temple):
            self.lds_baptism.set_temple(const.lds_temple_codes[temple])
        else:
            self.lds_baptism.set_temple("")
        self.lds_baptism.set_place_handle(self.get_place(self.ldsbapplace,1))

        self.lds_endowment.set_date(unicode(self.ldsend_date.get_text()))
        temple = _temple_names[self.ldsend_temple.get_active()]
        if const.lds_temple_codes.has_key(temple):
            self.lds_endowment.set_temple(const.lds_temple_codes[temple])
        else:
            self.lds_endowment.set_temple("")
        self.lds_endowment.set_place_handle(self.get_place(self.ldsendowplace,1))

        self.lds_sealing.set_date(unicode(self.ldsseal_date.get_text()))
        temple = _temple_names[self.ldsseal_temple.get_active()]
        if const.lds_temple_codes.has_key(temple):
            self.lds_sealing.set_temple(const.lds_temple_codes[temple])
        else:
            self.lds_sealing.set_temple("")
        self.lds_sealing.set_family_handle(self.ldsfam)
        self.lds_sealing.set_place_handle(self.get_place(self.ldssealplace,1))

    def on_event_delete_clicked(self,obj):
        """Delete the selected event"""
        if Utils.delete_selected(obj,self.elist):
            self.lists_changed = True
            self.redraw_event_list()

    def update_birth_death(self):
        self.bplace.set_text(place_title(self.db,self.birth))
        self.dplace.set_text(place_title(self.db,self.death))

        self.bdate.set_text(self.dd.display(self.birth_date_object))
        self.ddate.set_text(self.dd.display(self.death_date_object))

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        store,node = self.atree.get_selected()
        if node:
            attr = self.atree.get_object(node)
            pname = self.name_display.display(self.person)
            AttrEdit.AttributeEditor(self,attr,pname,const.personalAttributes,
                                     self.attr_edit_callback,self.window)

    def on_update_addr_clicked(self,obj):
        import AddrEdit
        store,node = self.ptree.get_selected()
        if node:
            AddrEdit.AddressEditor(self,self.ptree.get_object(node),
                            self.addr_edit_callback,self.window)

    def on_update_url_clicked(self,obj):
        import UrlEdit
        store,node = self.wtree.get_selected()
        if node:
            pname = self.name_display.display(self.person)
            url = self.wtree.get_object(node)
            UrlEdit.UrlEditor(self,pname,url,self.url_edit_callback,self.window)

    def on_event_update_clicked(self,obj):
        import EventEdit

        store,node = self.etree.get_selected()
        if not node:
            return
        pname = self.name_display.display(self.person)
        event = self.etree.get_object(node)
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.personal_events,event,None,0,
                              self.event_edit_callback,
                              noedit=self.db.readonly)

    def on_aka_delete_clicked(self,obj):
        """Deletes the selected name from the name list"""
        store,node = self.ntree.get_selected()
        if node:
            self.nlist.remove(self.ntree.get_object(node))
            self.lists_changed = True
            self.redraw_name_list()

    def on_delete_url_clicked(self,obj):
        """Deletes the selected URL from the URL list"""
        store,node = self.wtree.get_selected()
        if node:
            self.ulist.remove(self.wtree.get_object(node))
            self.lists_changed = True
            self.redraw_url_list()

    def on_delete_attr_clicked(self,obj):
        """Deletes the selected attribute from the attribute list"""
        store,node = self.atree.get_selected()
        if node:
            self.alist.remove(self.atree.get_object(node))
            self.lists_changed = True
            self.redraw_attr_list()

    def on_delete_addr_clicked(self,obj):
        """Deletes the selected address from the address list"""
        store,node = self.ptree.get_selected()
        if node:
            self.plist.remove(self.ptree.get_object(node))
            self.lists_changed = True
            self.redraw_addr_list()

    def on_web_go_clicked(self,obj):
        """Attempts to display the selected URL in a web browser"""
        text = obj.get()
        if text:
            gnome.url_show(text)
        
    def on_cancel_edit(self,obj):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        
        if self.did_data_change() and not GrampsKeys.get_dont_ask():
            n = "<i>%s</i>" % self.person.get_primary_name().get_regular_name()
            SaveDialog(_('Save changes to %s?') % n,
                       _('If you close without saving, the changes you '
                         'have made will be lost'),
                       self.cancel_callback,
                       self.save)
        else:
            self.close()

    def save(self):
        self.on_apply_person_clicked(None)

    def on_delete_event(self,obj,b):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        if self.did_data_change() and not GrampsKeys.get_dont_ask():
            n = "<i>%s</i>" % self.person.get_primary_name().get_regular_name()
            SaveDialog(_('Save Changes to %s?') % n,
                       _('If you close without saving, the changes you '
                         'have made will be lost'),
                       self.cancel_callback,
                       self.save)
            return True
        else:
            self.close()
            return False

    def cancel_callback(self):
        """If the user answered yes to abandoning changes, close the window"""
        self.close()

    def did_data_change(self):
        """Check to see if any of the data has changed from the
        orig record"""

        surname = unicode(self.surname.get_text())
        self.birth.set_date_object(self.birth_date_object)
        self.death.set_date_object(self.death_date_object)

        ntype = unicode(self.ntype_field.child.get_text())
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
        if idval == "":
            idval = None

        changed = False
        name = self.person.get_primary_name()

        if self.complete.get_active() != self.person.get_complete_flag():
            changed = True
        if self.private.get_active() != self.person.get_privacy():
            changed = True

        if self.person.get_gramps_id() != idval:
            changed = True
        if suffix != name.get_suffix():
            changed = True
        if self.use_patronymic:
            if prefix != name.get_patronymic():
                changed = True
            elif prefix != name.get_surname_prefix():
                changed = True
        if surname.upper() != name.get_surname().upper():
            changed = True
        if ntype != const.NameTypesMap.find_value(name.get_type()):
            changed = True
        if given != name.get_first_name():
            changed = True
        if nick != self.person.get_nick_name():
            changed = True
        if title != name.get_title():
            changed = True
        if self.pname.get_note() != name.get_note():
            changed = True
        if not self.lds_not_loaded and self.check_lds():
            changed = True

        bplace = unicode(self.bplace.get_text().strip())
        dplace = unicode(self.dplace.get_text().strip())

        if self.pdmap.has_key(bplace):
            self.birth.set_place_handle(self.pdmap[bplace])
        else:
            if bplace != "":
                changed = True
            self.birth.set_place_handle('')

        if self.pdmap.has_key(dplace):
            self.death.set_place_handle(self.pdmap[dplace])
        else:
            if dplace != "":
                changed = True
            self.death.set_place_handle('')

        if not self.birth.are_equal(self.orig_birth):
            changed = True
        if not self.death.are_equal(self.orig_death):
            changed = True
        if male and self.person.get_gender() != RelLib.Person.MALE:
            changed = True
        elif female and self.person.get_gender() != RelLib.Person.FEMALE:
            changed = True
        elif unknown and self.person.get_gender() != RelLib.Person.UNKNOWN:
            changed = True
        if text != self.person.get_note():
            changed = True
        if format != self.person.get_note_format():
            changed = True

        if not self.lds_not_loaded:
            if not self.lds_baptism.are_equal(self.person.get_lds_baptism()):
                changed= True

            if not self.lds_endowment.are_equal(self.person.get_lds_endowment()):
                changed = True

            if not self.lds_sealing.are_equal(self.person.get_lds_sealing()):
                changed = True
                
        return changed

    def check_lds(self):
        self.lds_baptism.set_date(unicode(self.ldsbap_date.get_text()))
        temple = _temple_names[self.ldsbap_temple.get_active()]
        if const.lds_temple_codes.has_key(temple):
            self.lds_baptism.set_temple(const.lds_temple_codes[temple])
        else:
            self.lds_baptism.set_temple("")
        self.lds_baptism.set_place_handle(self.get_place(self.ldsbapplace,1))

        self.lds_endowment.set_date(unicode(self.ldsend_date.get_text()))
        temple = _temple_names[self.ldsend_temple.get_active()]
        if const.lds_temple_codes.has_key(temple):
            self.lds_endowment.set_temple(const.lds_temple_codes[temple])
        else:
            self.lds_endowment.set_temple("")
        self.lds_endowment.set_place_handle(self.get_place(self.ldsendowplace,1))

        self.lds_sealing.set_date(unicode(self.ldsseal_date.get_text()))
        temple = _temple_names[self.ldsseal_temple.get_active()]
        if const.lds_temple_codes.has_key(temple):
            self.lds_sealing.set_temple(const.lds_temple_codes[temple])
        else:
            self.lds_sealing.set_temple("")
        self.lds_sealing.set_family_handle(self.ldsfam)
        self.lds_sealing.set_place_handle(self.get_place(self.ldssealplace,1))

    def on_event_delete_clicked(self,obj):
        """Delete the selected event"""
        if Utils.delete_selected(obj,self.elist):
            self.lists_changed = True
            self.redraw_event_list()

    def update_birth_death(self):
        self.bplace.set_text(place_title(self.db,self.birth))
        self.dplace.set_text(place_title(self.db,self.death))

        self.bdate.set_text(self.dd.display(self.birth_date_object))
        self.ddate.set_text(self.dd.display(self.death_date_object))

    def on_update_attr_clicked(self,obj):
        import AttrEdit
        store,node = self.atree.get_selected()
        if node:
            attr = self.atree.get_object(node)
            pname = self.name_display.display(self.person)
            AttrEdit.AttributeEditor(self,attr,pname,const.personalAttributes,
                                     self.attr_edit_callback,self.window)

    def on_update_addr_clicked(self,obj):
        import AddrEdit
        store,node = self.ptree.get_selected()
        if node:
            AddrEdit.AddressEditor(self,self.ptree.get_object(node),
                            self.addr_edit_callback,self.window)

    def on_update_url_clicked(self,obj):
        import UrlEdit
        store,node = self.wtree.get_selected()
        if node:
            pname = self.name_display.display(self.person)
            url = self.wtree.get_object(node)
            UrlEdit.UrlEditor(self,pname,url,self.url_edit_callback,self.window)

    def on_event_update_clicked(self,obj):
        import EventEdit

        store,node = self.etree.get_selected()
        if not node:
            return
        pname = self.name_display.display(self.person)
        event = self.etree.get_object(node)
        EventEdit.EventEditor(self,pname,const.personalEvents,
                              const.personal_events,event,None,0,
                              noedit=self.db.readonly)
        
    def on_event_select_row(self,obj):
        store,node = obj.get_selected()
        if node:
            row = store.get_path(node)
            event = self.db.get_event_from_handle(self.elist[row[0]])
            self.event_date_field.set_text(event.get_date())
            self.event_place_field.set_text(place_title(self.db,event))
            self.event_name_field.set_text(const.display_pevent(event.get_name()))
            self.event_cause_field.set_text(event.get_cause())
            self.event_descr_field.set_text(short(event.get_description()))
            if len(event.get_source_references()) > 0:
                psrc_ref = event.get_source_references()[0]
                psrc_id = psrc_ref.get_base_handle()
                psrc = self.db.get_source_from_handle(psrc_id)
                self.event_src_field.set_text(short(psrc.get_title()))
                self.event_conf_field.set_text(const.confidence[psrc_ref.get_confidence_level()])
            else:
                self.event_src_field.set_text('')
                self.event_conf_field.set_text('')
            if not self.db.readonly:
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
        store,node = self.ptree.get_selected()
        if node:
            addr = self.ptree.get_object(node)
            self.addr_start.set_text(addr.get_date())
            self.addr_street.set_text(addr.get_street())
            self.addr_city.set_text(addr.get_city())
            self.addr_state.set_text(addr.get_state())
            self.addr_country.set_text(addr.get_country())
            self.addr_postal.set_text(addr.get_postal_code())
            self.addr_phone.set_text(addr.get_phone())
            if len(addr.get_source_references()) > 0:
                psrc_ref = addr.get_source_references()[0]
                psrc_id = psrc_ref.get_base_handle()
                psrc = self.db.get_source_from_handle(psrc_id)
                self.addr_conf_field.set_text(const.confidence[psrc_ref.get_confidence_level()])
                self.addr_src_field.set_text(short(psrc.get_title()))
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
        store,node = self.ntree.get_selected()
        if node:
            name = self.ntree.get_object(node)
            self.alt_given_field.set_text(name.get_first_name())
            self.alt_title_field.set_text(name.get_title())
            self.alt_last_field.set_text(name.get_surname())
            self.alt_suffix_field.set_text(name.get_suffix())
            self.alt_prefix_field.set_text(name.get_surname_prefix())
            self.name_type_field.set_text(const.NameTypesMap.find_value(name.get_type()))
            if len(name.get_source_references()) > 0:
                psrc_ref = name.get_source_references()[0]
                psrc_id = psrc_ref.get_base_handle()
                psrc = self.db.get_source_from_handle(psrc_id)
                self.name_src_field.set_text(short(psrc.get_title()))
                self.name_conf_field.set_text(const.confidence[psrc_ref.get_confidence_level()])
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
        store,node = self.wtree.get_selected()
        if node:
            url = self.wtree.get_object(node)
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
        store,node = self.atree.get_selected()
        if node:
            attr = self.atree.get_object(node)
            self.attr_type.set_text(const.display_pattr(attr.get_type()))
            self.attr_value.set_text(short(attr.get_value()))
            if len(attr.get_source_references()) > 0:
                psrc_ref = attr.get_source_references()[0]
                psrc_id = psrc_ref.get_base_handle()
                psrc = self.db.get_source_from_handle(psrc_id)
                self.attr_src_field.set_text(short(psrc.get_title()))
                self.attr_conf_field.set_text(const.confidence[psrc_ref.get_confidence_level()])
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
            if not self.db.readonly:
                msg = _("Make the selected name the preferred name")
                Utils.add_menuitem(menu,msg,None,self.change_name)
            menu.popup(None,None,None,event.button,event.time)

    def on_aka_update_clicked(self,obj):
        import NameEdit
        store,node = self.ntree.get_selected()
        if node:
            NameEdit.NameEditor(self,self.ntree.get_object(node),
                                self.name_edit_callback,self.window)

    def load_photo(self,photo):
        """loads, scales, and displays the person's main photo"""
        self.load_obj = photo
        if photo == None:
            self.person_photo.hide()
        else:
            try:
                i = pixbuf_new_from_file(photo)
                ratio = float(max(i.get_height(),i.get_width()))
                scale = float(_PICTURE_WIDTH)/ratio
                x = int(scale*(i.get_width()))
                y = int(scale*(i.get_height()))
                i = i.scale_simple(x,y,INTERP_BILINEAR)
                self.person_photo.set_from_pixbuf(i)
                self.person_photo.show()
            except:
                self.person_photo.hide()

    def update_lists(self):
        """Updates the person's lists if anything has changed"""
        if self.lists_changed:
            self.person.set_event_list(self.elist)
            self.person.set_alternate_names(self.nlist)
            self.person.set_url_list(self.ulist)
            self.person.set_attribute_list(self.alist)
            self.person.set_address_list(self.plist)
            self.person.set_birth_handle(self.birth.get_handle())
            self.person.set_death_handle(self.death.get_handle())

    def on_apply_person_clicked(self,obj):

        self.window.hide()
        trans = self.db.transaction_begin()

        surname = unicode(self.surname.get_text())
        suffix = unicode(self.suffix.get_text())
        prefix = unicode(self.prefix.get_text())
        ntype = unicode(self.ntype_field.child.get_text())
        given = unicode(self.given.get_text())
        nick = unicode(self.nick.get_text())
        title = unicode(self.title.get_text())
        idval = unicode(self.gid.get_text())

        name = self.pname

        self.birth.set_date_object(self.birth_date_object)
        self.birth.set_place_handle(self.get_place(self.bplace,1))

        if idval != self.person.get_gramps_id():
            person = self.db.get_person_from_gramps_id(idval)
            if not person:
                self.person.set_gramps_id(idval)
            else:
                n = self.name_display.display(person)
                msg1 = _("GRAMPS ID value was not changed.")
                msg2 = _("You have attempted to change the GRAMPS ID to a value "
                         "of %(grampsid)s. This value is already used by %(person)s.") % {
                    'grampsid' : idval,
                    'person' : n }
                WarningDialog(msg1,msg2)

        if suffix != name.get_suffix():
            name.set_suffix(suffix)

        if self.use_patronymic:
            if prefix != name.get_patronymic():
                name.set_patronymic(prefix)
        else:
            if prefix != name.get_surname_prefix():
                name.set_surname_prefix(prefix)

        if const.NameTypesMap.has_value(ntype):
            ntype = const.NameTypesMap.find_key(ntype)
        else:
            ntype = "Birth Name"

        if ntype != name.get_type():
            name.set_type(ntype)
            
        if surname != name.get_surname():
            name.set_surname(surname)

        if given != name.get_first_name():
            name.set_first_name(given)

        if title != name.get_title():
            name.set_title(title)

        name.set_source_reference_list(self.pname.get_source_references())

        if name != self.person.get_primary_name():
            self.person.set_primary_name(name)

        if nick != self.person.get_nick_name():
            self.person.set_nick_name(nick)

        self.pdmap.clear()
        for key in self.db.get_place_handles():
            p = self.db.get_place_from_handle(key).get_display_info()
            self.pdmap[p[0]] = key

        if self.orig_birth == None:
            self.db.add_event(self.birth,trans)
            self.person.set_birth_handle(self.birth.get_handle())
        elif not self.orig_birth.are_equal(self.birth):
            self.db.commit_event(self.birth,trans)

        # Update each of the families child lists to reflect any
        # change in ordering due to the new birth date
        family = self.person.get_main_parents_family_handle()
        if (family):
            f = self.db.find_family_from_handle(family,trans)
            new_order = self.reorder_child_list(self.person,f.get_child_handle_list())
            f.set_child_handle_list(new_order)
        for (family, rel1, rel2) in self.person.get_parent_family_handle_list():
            f = self.db.find_family_from_handle(family,trans)
            new_order = self.reorder_child_list(self.person,f.get_child_handle_list())
            f.set_child_handle_list(new_order)
    
        self.death.set_date_object(self.death_date_object)
        self.death.set_place_handle(self.get_place(self.dplace,1))

        if self.orig_death == None:
            self.db.add_event(self.death,trans)
            self.person.set_death_handle(self.death.get_handle())
        elif not self.orig_death.are_equal(self.death):
            self.db.commit_event(self.death,trans)

        male = self.is_male.get_active()
        female = self.is_female.get_active()
        unknown = self.is_unknown.get_active()
        error = False
        if male and self.person.get_gender() != RelLib.Person.MALE:
            self.person.set_gender(RelLib.Person.MALE)
            for temp_family in self.person.get_family_handle_list():
                if self.person == temp_family.get_mother_handle():
                    if temp_family.get_father_handle() != None:
                        error = True
                    else:
                        temp_family.set_mother_handle(None)
                        temp_family.set_father_handle(self.person)
        elif female and self.person.get_gender() != RelLib.Person.FEMALE:
            self.person.set_gender(RelLib.Person.FEMALE)
            for temp_family in self.person.get_family_handle_list():
                if self.person == temp_family.get_father_handle():
                    if temp_family.get_mother_handle() != None:
                        error = True
                    else:
                        temp_family.set_father_handle(None)
                        temp_family.set_mother_handle(self.person)
        elif unknown and self.person.get_gender() != RelLib.Person.UNKNOWN:
            self.person.set_gender(RelLib.Person.UNKNOWN)
            for temp_family in self.person.get_family_handle_list():
                if self.person == temp_family.get_father_handle():
                    if temp_family.get_mother_handle() != None:
                        error = True
                    else:
                        temp_family.set_father_handle(None)
                        temp_family.set_mother_handle(self.person)
                if self.person == temp_family.get_mother_handle():
                    if temp_family.get_father_handle() != None:
                        error = True
                    else:
                        temp_family.set_mother_handle(None)
                        temp_family.set_father_handle(self.person)

        if error:
            msg2 = _("Problem changing the gender")
            msg = _("Changing the gender caused problems "
                    "with marriage information.\nPlease check "
                    "the person's marriages.")
            ErrorDialog(msg)

        text = unicode(self.notes_buffer.get_text(self.notes_buffer.get_start_iter(),
                                          self.notes_buffer.get_end_iter(),gtk.FALSE))

        if text != self.person.get_note():
            self.person.set_note(text)

        format = self.preform.get_active()
        if format != self.person.get_note_format():
            self.person.set_note_format(format)

        self.person.set_complete_flag(self.complete.get_active())
        self.person.set_privacy(self.private.get_active())

        if not self.lds_not_loaded:
            self.check_lds()
            lds_ord = RelLib.LdsOrd(self.person.get_lds_baptism())
            if not self.lds_baptism.are_equal(lds_ord):
                self.person.set_lds_baptism(self.lds_baptism)

            lds_ord = RelLib.LdsOrd(self.person.get_lds_endowment())
            if not self.lds_endowment.are_equal(lds_ord):
                self.person.set_lds_endowment(self.lds_endowment)

            lds_ord = RelLib.LdsOrd(self.person.get_lds_sealing())
            if not self.lds_sealing.are_equal(lds_ord):
                self.person.set_lds_sealing(self.lds_sealing)

        if self.lists_changed:
            self.person.set_source_reference_list(self.srcreflist)
            self.update_lists()

        if not self.person.get_handle():
            self.db.add_person(self.person, trans)
            call_value = 0
        else:
            if not self.person.get_gramps_id():
                self.person.set_gramps_id(self.db.find_next_person_gramps_id())
            call_value = 1
            self.db.commit_person(self.person, trans)
        n = self.person.get_primary_name().get_regular_name()
        self.db.transaction_commit(trans,_("Edit Person (%s)") % n)
        if self.callback:
            self.callback(self,call_value)
        self.close()

    def get_place(self,field,makenew=0):
        text = unicode(field.get_text().strip())
        if text:
            if self.pdmap.has_key(text):
                return self.pdmap[text]
            elif makenew:
                place = RelLib.Place()
                place.set_title(text)
                trans = self.db.transaction_begin()
                self.db.add_place(place,trans)
                self.db.transaction_commit(trans,_('Add Place (%s)' % text))
                self.pdmap[text] = place.get_handle()
                self.add_places.append(place)
                return place.get_handle()
            else:
                return u""
        else:
            return u""

    def on_edit_name_clicked(self,obj):
        import NameEdit

        ntype = unicode(self.ntype_field.child.get_text())
        self.pname.set_type(const.NameTypesMap.find_value(ntype))
        self.pname.set_suffix(unicode(self.suffix.get_text()))
        self.pname.set_surname(unicode(self.surname.get_text()))
        if self.use_patronymic:
            self.pname.set_patronymic(unicode(self.prefix.get_text()))
        else:
            self.pname.set_surname_prefix(unicode(self.prefix.get_text()))
        self.pname.set_first_name(unicode(self.given.get_text()))
        self.pname.set_title(unicode(self.title.get_text()))

        NameEdit.NameEditor(self,self.pname,self.update_name,self.window)

    def update_name(self,name):
        self.write_primary_name()
        
    def on_ldsbap_source_clicked(self,obj):
        Sources.SourceSelector(self.lds_baptism.get_source_references(),
                               self,self.update_ldsbap_list)

    def update_ldsbap_list(self,list):
        self.lds_baptism.set_source_reference_list(list)
        self.lists_changed = True
        
    def on_ldsbap_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.lds_baptism,self,self.window,
                            readonly=self.db.readonly)

    def on_ldsendow_source_clicked(self,obj):
        Sources.SourceSelector(self.lds_endowment.get_source_references(),
                               self,self.set_ldsendow_list)

    def set_ldsendow_list(self,list):
        self.lds_endowment.set_source_reference_list(list)
        self.lists_changed = True

    def on_ldsendow_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.lds_endowment,self,self.window,
                            readonly=self.db.readonly)

    def on_ldsseal_source_clicked(self,obj):
        Sources.SourceSelector(self.lds_sealing.get_source_references(),
                               self,self.lds_seal_list)

    def lds_seal_list(self,list):
        self.lds_sealing.set_source_reference_list(list)
        self.lists_changed = True

    def on_ldsseal_note_clicked(self,obj):
        import NoteEdit
        NoteEdit.NoteEditor(self.lds_sealing,self,self.window,
                            readonly=self.db.readonly)

    def load_person_image(self):
        media_list = self.person.get_media_list()
        if media_list:
            ph = media_list[0]
            object_handle = ph.get_reference_handle()
            obj = self.db.get_object_from_handle(object_handle)
            if self.load_obj != obj.get_path():
                if obj.get_mime_type()[0:5] == "image":
                    self.load_photo(obj.get_path())
                else:
                    self.load_photo(None)
        else:
            self.load_photo(None)

    def update_birth_info(self):
        self.birth_date_object.copy(self.birth.get_date_object())
        self.bdate.set_text(self.birth.get_date())
        self.bplace.set_text(place_title(self.db,self.birth))

    def update_death_info(self):
        self.death_date_object.copy(self.death.get_date_object())
        self.ddate.set_text(self.death.get_date())
        self.dplace.set_text(place_title(self.db,self.death))
        
    def on_switch_page(self,obj,a,page):
        if page == 0:
            self.load_person_image()
        elif page == 2:
            self.redraw_event_list()
        elif page == 7 and self.not_loaded:
            self.not_loaded = False
        elif page == 9 and self.lds_not_loaded:
            self.lds_not_loaded = False
            self.draw_lds()
        note_buf = self.notes_buffer
        text = unicode(note_buf.get_text(note_buf.get_start_iter(),
                                       note_buf.get_end_iter(),gtk.FALSE))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)

        if not self.lds_not_loaded:
            self.check_lds()
        if self.lds_baptism.is_empty() \
                        and self.lds_endowment.is_empty() \
                        and self.lds_sealing.is_empty():
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
            self.lists_changed = True
            self.write_primary_name()

    def write_primary_name(self):
        # initial values
        name = '<span size="larger" weight="bold">%s</span>' % self.name_display.display(self.person)
        self.get_widget("activepersonTitle").set_text(name)
        self.get_widget("activepersonTitle").set_use_markup(gtk.TRUE)
        self.suffix.set_text(self.pname.get_suffix())
        if self.use_patronymic:
            self.prefix.set_text(self.pname.get_patronymic())
        else:
            self.prefix.set_text(self.pname.get_surname_prefix())

        self.surname.set_text(self.pname.get_surname())
        self.given.set_text(self.pname.get_first_name())

        self.ntype_field.child.set_text(_(self.pname.get_type()))
        self.title.set_text(self.pname.get_title())

    def birth_dates_in_order(self,list):
        """Check any *valid* birthdates in the list to insure that they are in
        numerically increasing order."""
        inorder = True
        prev_date = 0
        for i in range(len(list)):
            child_handle = list[i]
            child = self.db.get_person_from_handle(child_handle)
            if child.get_birth_handle():
                event = self.db.get_event_from_handle(child.get_birth_handle())
                child_date = event.get_date_object().get_sort_value()
            else:
                continue
            if (prev_date <= child_date):   # <= allows for twins
                prev_date = child_date
            else:
                inorder = False
        return inorder

    def reorder_child_list(self, person, list):
        """Reorder the child list to put the specified person in his/her
        correct birth order.  Only check *valid* birthdates.  Move the person
        as short a distance as possible."""

        if (self.birth_dates_in_order(list)):
            return(list)

        # Build the person's date string once
        event_handle = person.get_birth_handle()
        if event_handle:
            event = self.db.get_event_from_handle(event_handle)
            person_bday = event.get_date_object().get_sort_value()
        else:
            person_bday = 0

        # First, see if the person needs to be moved forward in the list

        index = list.index(person.get_handle())
        target = index
        for i in range(index-1, -1, -1):
            other = self.db.get_person_from_handle(list[i])
            event_handle = other.get_birth_handle()
            if event_handle:
                event = self.db.get_event_from_handle(event_handle)
                other_bday = event.get_date_object().get_sort_value()
                if other_bday == 0:
                    continue;
                if person_bday < other_bday:
                    target = i
            else:
                continue

        # Now try moving to a later position in the list
        if (target == index):
            for i in range(index, len(list)):
                other = self.db.get_person_from_handle(list[i])
                event_handle = other.get_birth_handle()
                if event_handle:
                    event = self.db.get_event_from_handle(event_handle)
                    other_bday = event.get_date_object().get_sort_value()
                    if other_bday == "99999999":
                        continue;
                    if person_bday > other_bday:
                        target = i
                else:
                    continue

        # Actually need to move?  Do it now.
        if (target != index):
            list.remove(person.get_handle())
            list.insert(target,person.get_handle())
        return list


def short(val,size=60):
    if len(val) > size:
        return "%s..." % val[0:size]
    else:
        return val

def place_title(db,event):
    pid = event.get_place_handle()
    if pid:
        return db.get_place_from_handle(pid).get_title()
    else:
        return u''

def build_dropdown(entry,strings):
    store = gtk.ListStore(str)
    for value in strings:
        node = store.append()
        store.set(node,0,unicode(value))
    completion = gtk.EntryCompletion()
    completion.set_text_column(0)
    completion.set_model(store)
    entry.set_completion(completion)

def build_combo(entry,strings):
    cell = gtk.CellRendererText()
    entry.pack_start(cell,True)
    entry.add_attribute(cell,'text',0)
    store = gtk.ListStore(str)
    for value in strings:
        node = store.append()
        store.set(node,0,unicode(value))
    entry.set_model(store)
