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
import cPickle as pickle
import os
import locale
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gobject
import gnome
import gtk.gdk

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
import UrlEdit
import NameEdit
import NoteEdit
import AttrEdit
import EventEdit
import AddrEdit

from QuestionDialog import WarningDialog, ErrorDialog, SaveDialog, QuestionDialog2

from DdTargets import DdTargets


#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

_PICTURE_WIDTH = 200.0

_temple_names = const.lds_temple_codes.keys()
_temple_names.sort()
_temple_names = [""] + _temple_names
_select_gender = ((True,False,False),(False,True,False),(False,False,True))
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

        self.retval = const.UPDATE_PERSON
        
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
        self.top = gtk.glade.XML(const.editPersonFile, "edit_person","gramps")
        self.window = self.get_widget("edit_person")
        self.window.set_title("%s - GRAMPS" % _('Edit Person'))
        
        self.icon_list = self.top.get_widget("iconlist")
        #self.gallery = ImageSelect.Gallery(person, self.db.commit_person,
        #                                   self.path, self.icon_list,
        #                                   self.db, self, self.window)

        self.complete = self.get_widget('complete')
        self.complete.set_sensitive(mod)
        self.gender = self.get_widget('gender')
        self.gender.set_sensitive(mod)
        self.private = self.get_widget('private')
        self.private.set_sensitive(mod)
        name_delete_btn = self.top.get_widget('aka_del')
        name_add_btn = self.top.get_widget('aka_add')
        name_edit_btn = self.top.get_widget('aka_edit')
        web_delete_btn = self.top.get_widget('url_del')
        web_edit_btn = self.top.get_widget('url_edit')
        web_add_btn = self.top.get_widget('url_add')
        event_delete_btn = self.top.get_widget('event_del')
        event_add_btn = self.top.get_widget('event_add')
        event_edit_btn = self.top.get_widget('event_edit')
        attr_add_btn = self.top.get_widget('attr_add')
        attr_delete_btn = self.top.get_widget('attr_del')
        attr_edit_btn = self.top.get_widget('attr_edit')
        addr_add_btn = self.top.get_widget('addr_add')
        addr_delete_btn = self.top.get_widget('addr_del')
        addr_edit_btn = self.top.get_widget('addr_edit')

        self.notes_field = self.get_widget("personNotes")
        self.notes_field.set_editable(mod)
        self.flowed = self.get_widget("flowed")
        self.flowed.set_sensitive(mod)
        self.preform = self.get_widget("preform")
        self.preform.set_sensitive(mod)
        self.attr_list = self.get_widget("attr_list")
        self.web_list = self.get_widget("web_list")
        self.web_go = self.get_widget("web_go")
        self.addr_list = self.get_widget("address_list")
        self.event_list = self.get_widget("eventList")
        self.edit_person = self.get_widget("editPerson")
        self.name_list = self.get_widget("nameList")
        self.name_type_field = self.get_widget("name_type")
        self.ntype_field = self.get_widget("ntype")
        self.suffix = self.get_widget("suffix")
        self.suffix.set_editable(mod)
        self.prefix = self.get_widget("prefix")
        self.prefix.set_editable(mod)
        self.given = self.get_widget("givenName")
        self.given.set_editable(mod)
        self.title = self.get_widget("title")
        self.title.set_editable(mod)
        self.surname = self.get_widget("surname")
        self.surname.set_editable(mod)
        self.gid = self.get_widget("gid")
        self.gid.set_editable(mod)
        self.slist = self.get_widget("slist")
        names_label = self.get_widget("names_label")
        events_label = self.get_widget("events_label")
        attr_label = self.get_widget("attr_label")
        addr_label = self.get_widget("addr_label")
        web_label = self.get_widget("inet_label")
        self.notes_label = self.get_widget("notes_label")
        self.sources_label = self.get_widget("sources_label")
        self.gallery_label = self.get_widget("gallery_label")
        self.lds_tab = self.get_widget("lds_tab")
        self.person_photo = self.get_widget("personPix")
        self.eventbox = self.get_widget("eventbox1")
        self.prefix_label = self.get_widget('prefix_label')

        if self.use_patronymic:
            self.prefix_label.set_text(_('Patronymic:'))
            self.prefix_label.set_use_underline(True)

        self.birth_handle = person.get_birth_handle()
        self.death_handle = person.get_death_handle()

        self.pname = RelLib.Name(person.get_primary_name())

        self.gender.set_active(person.get_gender())
        
        self.nlist = person.get_alternate_names()[:]
        self.alist = person.get_attribute_list()[:]
        self.ulist = person.get_url_list()[:]
        self.plist = person.get_address_list()[:]

        if person:
            self.srcreflist = person.get_source_references()
        else:
            self.srcreflist = []

        if self.srcreflist:
            Utils.bold_label(self.sources_label)
        if self.person.get_media_list():
            Utils.bold_label(self.gallery_label)

        # event display

        self.event_box = EventListBox(
            self, self.person, self.event_list, events_label,
            [event_add_btn,event_edit_btn,event_delete_btn])

        self.attr_box = AttrListBox(
            self, self.person, self.attr_list, attr_label,
            [attr_add_btn, attr_edit_btn, attr_delete_btn])

        self.addr_box = AddressListBox(
            self, self.person, self.addr_list, addr_label,
            [addr_add_btn, addr_edit_btn, addr_delete_btn])

        self.name_box = NameListBox(
            self, self.person, self.name_list, names_label,
            [name_add_btn, name_edit_btn, name_delete_btn])

        self.url_box = UrlListBox(
            self, self.person, self.web_list, web_label,
            [web_add_btn, web_edit_btn, web_delete_btn])

        self.place_list = self.pdmap.keys()
        self.place_list.sort()

        build_dropdown(self.surname,self.db.get_surname_list())

        gid = person.get_gramps_id()
        if gid:
            self.gid.set_text(gid)
        self.gid.set_editable(True)

        self.lds_baptism = RelLib.LdsOrd(self.person.get_lds_baptism())
        self.lds_endowment = RelLib.LdsOrd(self.person.get_lds_endowment())
        self.lds_sealing = RelLib.LdsOrd(self.person.get_lds_sealing())

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

        self.top.signal_autoconnect({
            "destroy_passed_object"     : self.on_cancel_edit,
            "on_up_clicked"             : self.on_up_clicked,
            "on_down_clicked"           : self.on_down_clicked,
#            "on_addphoto_clicked"       : self.gallery.on_add_media_clicked,
#            "on_selectphoto_clicked"    : self.gallery.on_select_media_clicked,
            "on_apply_person_clicked"   : self.on_apply_person_clicked,
            "on_delete_event"           : self.on_delete_event,
#            "on_deletephoto_clicked"    : self.gallery.on_delete_media_clicked,
#            "on_edit_properties_clicked": self.gallery.popup_change_description,
#            "on_editphoto_clicked"      : self.gallery.on_edit_media_clicked,
            "on_editperson_switch_page" : self.on_switch_page,
            "on_edit_name_clicked"      : self.on_edit_name_clicked,
            "on_ldsbap_note_clicked"    : self.on_ldsbap_note_clicked,
            "on_ldsendow_note_clicked"  : self.on_ldsendow_note_clicked,
            "on_ldsseal_note_clicked"   : self.on_ldsseal_note_clicked,
            "on_ldsbap_src_clicked"     : self.on_ldsbap_source_clicked,
            "on_ldsendow_src_clicked"   : self.on_ldsendow_source_clicked,
            "on_ldsseal_src_clicked"    : self.on_ldsseal_source_clicked,
            "on_web_go_clicked"         : self.on_web_go_clicked,
            "on_gender_activate"        : self.on_gender_activate,
            "on_given_focus_out"        : self.on_given_focus_out_event,
            "on_help_person_clicked"    : self.on_help_clicked,
            })

        self.sourcetab = Sources.SourceTab(
            self.srcreflist, self, self.top, self.window, self.slist,
            self.top.get_widget('add_src'), self.top.get_widget('edit_src'),
            self.top.get_widget('del_src'), self.db.readonly)

        self.complete.set_active(self.person.get_complete_flag())
        self.private.set_active(self.person.get_privacy())

        self.eventbox.connect('button-press-event',self.image_button_press)

        self.event_box.redraw()
        self.attr_box.redraw()
        self.addr_box.redraw() 
        self.name_box.redraw()
        self.url_box.redraw()
        self.get_widget("notebook").set_current_page(0)
        self.surname.grab_focus()
        self.add_itself_to_winsmenu()

        if self.db.readonly:
            for i in ["ok", "aka_add", "aka_del", "event_add", "event_del",
                      "attr_add", "attr_del", "addr_add",
                      "addr_del", "media_add", "media_sel", "media_del",
                      "url_add", "url_del", "add_src", "del_src" ]:
                self.get_widget(i).set_sensitive(False)

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
            ImageSelect.LocalMediaProperties(ph,obj.get_path(),self,
                                             self.window)

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def close(self):
        event_list = []
        #for col in self.event_list.get_columns():
        #    event_list.append(self.event_trans.find_key(col.get_title()))
        #if not self.db.readonly:
        #    self.db.metadata['event_order'] = event_list
        
        #self.gallery.close()
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
            if cnum == 0:
                renderer = gtk.CellRendererCombo()
            else:
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
        else:
            stat = 0
        date.set_text(lds_ord.get_date())

        build_dropdown(place,self.place_list)
        if lds_ord and lds_ord.get_place_handle():
            handle = lds_ord.get_place_handle()
            lds_ord_place = self.db.get_place_from_handle(handle)
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
        self.ldsbap_date_led = self.get_widget("ldsbap_stat")
        self.ldsbap_date_led.set_sensitive(not self.db.readonly)
        self.ldsbap_date_check = DateEdit.DateEdit(
            self.lds_baptism.get_date_object(), self.ldsbap_date,
            self.ldsbap_date_led, self.window)

        self.ldsend_date = self.get_widget("endowdate")
        self.ldsend_date.set_editable(not self.db.readonly)
        self.ldsend_temple = self.get_widget("endowtemple")
        self.ldsend_temple.set_sensitive(not self.db.readonly)
        self.ldsendowplace = self.get_widget("lds_end_place")
        self.ldsendowplace.set_editable(not self.db.readonly)
        self.ldsendowstat = self.get_widget("endowstat")
        self.ldsendowstat.set_sensitive(not self.db.readonly)
        self.ldsend_date_led = self.get_widget("endow_stat")
        self.ldsend_date_led.set_sensitive(not self.db.readonly)
        self.ldsend_date_check = DateEdit.DateEdit(
            self.lds_endowment.get_date_object(), self.ldsend_date,
            self.ldsend_date_led, self.window)

        self.ldsseal_date = self.get_widget("sealdate")
        self.ldsseal_temple = self.get_widget("sealtemple")
        self.ldssealplace = self.get_widget("lds_seal_place")
        self.ldsseal_date.set_editable(not self.db.readonly)
        self.ldsseal_temple.set_sensitive(not self.db.readonly)
        self.ldssealplace.set_editable(not self.db.readonly)
        self.ldsseal_date_led = self.get_widget("seal_stat")
        self.ldsseal_date_led.set_sensitive(not self.db.readonly)
        self.ldsseal_date_check = DateEdit.DateEdit(
            self.lds_sealing.get_date_object(), self.ldsseal_date,
            self.ldsseal_date_led, self.window)
        
        self.ldsseal_fam = self.get_widget("sealparents")
        self.ldsseal_fam.set_sensitive(not self.db.readonly)
        
        self.ldsbapstat = self.get_widget("ldsbapstat")
        self.ldsbapstat.set_sensitive(not self.db.readonly)

        self.ldssealstat = self.get_widget("sealstat")
        self.ldssealstat.set_sensitive(not self.db.readonly)

        self.bstat = self.lds_field(
            self.lds_baptism, self.ldsbap_temple,
            self.ldsbap_date, self.ldsbapplace)
        
        self.estat = self.lds_field(
            self.lds_endowment, self.ldsend_temple,
            self.ldsend_date, self.ldsendowplace)

        self.seal_stat = self.lds_field(
            self.lds_sealing, self.ldsseal_temple,
            self.ldsseal_date, self.ldssealplace)
        
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
            family = self.db.get_family_from_handle(fam_id)
            if family == None:
                continue
            name = Utils.family_name(family,self.db)
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

    def set_lds_bap(self,obj):
        self.lds_baptism.set_status(obj.get_active())

    def set_lds_endow(self,obj):
        self.lds_endowment.set_status(obj.get_active())

    def set_lds_seal(self,obj):
        self.lds_sealing.set_status(obj.get_active())

    def move_element(self,list,src,dest):
        if src == -1:
            return
        obj = list[src]
        list.remove(obj)
        list.insert(dest,obj)

    def menu_changed(self,obj):
        self.ldsfam = self.lds_fam_list[obj.get_active()]
        
    def get_widget(self,str):
        """returns the widget related to the passed string"""
        return self.top.get_widget(str)

    def strip_id(self,text):
        index = text.rfind('[')
        if (index > 0):
            text = text[:index]
            text = text.rstrip()
        return text

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

        ntype = unicode(self.ntype_field.child.get_text())
        suffix = unicode(self.suffix.get_text())
        prefix = unicode(self.prefix.get_text())
        given = unicode(self.given.get_text())
        title = unicode(self.title.get_text())

        start = self.notes_buffer.get_start_iter()
        end = self.notes_buffer.get_end_iter()
        text = unicode(self.notes_buffer.get_text(start, end, False))
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
        if title != name.get_title():
            changed = True
        if self.pname.get_note() != name.get_note():
            changed = True
        if not self.lds_not_loaded and self.check_lds():
            changed = True

        (female,male,unknown) = _select_gender[self.gender.get_active()]
        
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

    def load_photo(self,photo):
        """loads, scales, and displays the person's main photo"""
        self.load_obj = photo
        if photo == None:
            self.person_photo.hide()
        else:
            try:
                i = gtk.gdk.pixbuf_new_from_file(photo)
                ratio = float(max(i.get_height(),i.get_width()))
                scale = float(100.0)/ratio
                x = int(scale*(i.get_width()))
                y = int(scale*(i.get_height()))
                i = i.scale_simple(x,y,gtk.gdk.INTERP_BILINEAR)
                self.person_photo.set_from_pixbuf(i)
                self.person_photo.show()
            except:
                self.person_photo.hide()

    def update_lists(self):
        """Updates the person's lists if anything has changed"""
        if self.lists_changed:
            self.person.set_alternate_names(self.nlist)
            self.person.set_url_list(self.ulist)
            self.person.set_attribute_list(self.alist)
            self.person.set_address_list(self.plist)
            #self.person.set_event_list(self.elist)
#             self.person.set_birth_handle(self.birth.get_handle())
#             self.person.set_death_handle(self.death.get_handle())

    def on_apply_person_clicked(self,obj):

        if self.gender.get_active() == RelLib.Person.UNKNOWN:
            dialog = QuestionDialog2(
                _("Unknown gender specified"),
                _("The gender of the person is currently unknown. "
                  "Usually, this is a mistake. You may choose to "
                  "either continue saving, or returning to the "
                  "Edit Person dialog to fix the problem."),
                _("Continue saving"), _("Return to window"),
                self.window)
            if not dialog.run():
                return

        self.window.hide()
        trans = self.db.transaction_begin()

        surname = unicode(self.surname.get_text())
        suffix = unicode(self.suffix.get_text())
        prefix = unicode(self.prefix.get_text())
        ntype = unicode(self.ntype_field.child.get_text())
        given = unicode(self.given.get_text())
        title = unicode(self.title.get_text())
        idval = unicode(self.gid.get_text())

        name = self.pname

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

        self.pdmap.clear()
        for key in self.db.get_place_handles():
            p = self.db.get_place_from_handle(key).get_display_info()
            self.pdmap[p[0]] = key

#         if not self.orig_birth.are_equal(self.birth):
#             if self.orig_birth.is_empty():
#                 self.db.add_event(self.birth,trans)
#                 self.person.set_birth_handle(self.birth.get_handle())
#             self.db.commit_event(self.birth,trans)

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

        error = False
        (female,male,unknown) = _select_gender[self.gender.get_active()]
        if male and self.person.get_gender() != RelLib.Person.MALE:
            self.person.set_gender(RelLib.Person.MALE)
            for temp_family_handle in self.person.get_family_handle_list():
                temp_family = self.db.get_family_from_handle(temp_family_handle)
                if self.person == temp_family.get_mother_handle():
                    if temp_family.get_father_handle() != None:
                        error = True
                    else:
                        temp_family.set_mother_handle(None)
                        temp_family.set_father_handle(self.person)
        elif female and self.person.get_gender() != RelLib.Person.FEMALE:
            self.person.set_gender(RelLib.Person.FEMALE)
            for temp_family_handle in self.person.get_family_handle_list():
                temp_family = self.db.get_family_from_handle(temp_family_handle)
                if self.person == temp_family.get_father_handle():
                    if temp_family.get_mother_handle() != None:
                        error = True
                    else:
                        temp_family.set_father_handle(None)
                        temp_family.set_mother_handle(self.person)
        elif unknown and self.person.get_gender() != RelLib.Person.UNKNOWN:
            self.person.set_gender(RelLib.Person.UNKNOWN)
            for temp_family_handle in self.person.get_family_handle_list():
                temp_family = self.db.get_family_from_handle(temp_family_handle)
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

        start = self.notes_buffer.get_start_iter()
        stop = self.notes_buffer.get_end_iter()
        text = unicode(self.notes_buffer.get_text(start,stop,False))

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
        else:
            if not self.person.get_gramps_id():
                self.person.set_gramps_id(self.db.find_next_person_gramps_id())
            self.db.commit_person(self.person, trans)
        n = self.person.get_primary_name().get_regular_name()
        self.db.transaction_commit(trans,_("Edit Person (%s)") % n)
        if self.callback:
            self.callback(self,self.retval)
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
                self.retval |= const.UPDATE_PLACE
                self.db.transaction_commit(trans,_('Add Place (%s)' % text))
                self.pdmap[text] = place.get_handle()
                self.add_places.append(place)
                return place.get_handle()
            else:
                return u""
        else:
            return u""

    def on_edit_name_clicked(self,obj):
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

        NameEdit.NameEditor(self, self.pname, self.update_name, self.window)

    def update_name(self,name):
        self.write_primary_name()
        
    def on_ldsbap_source_clicked(self,obj):
        Sources.SourceSelector(self.lds_baptism.get_source_references(),
                               self,self.update_ldsbap_list)

    def update_ldsbap_list(self,list):
        self.lds_baptism.set_source_reference_list(list)
        self.lists_changed = True
        
    def on_ldsbap_note_clicked(self,obj):
        NoteEdit.NoteEditor(self.lds_baptism,self,self.window,
                            readonly=self.db.readonly)

    def on_ldsendow_source_clicked(self,obj):
        Sources.SourceSelector(self.lds_endowment.get_source_references(),
                               self,self.set_ldsendow_list)

    def set_ldsendow_list(self,list):
        self.lds_endowment.set_source_reference_list(list)
        self.lists_changed = True

    def on_ldsendow_note_clicked(self,obj):
        NoteEdit.NoteEditor(self.lds_endowment,self,self.window,
                            readonly=self.db.readonly)

    def on_ldsseal_source_clicked(self,obj):
        Sources.SourceSelector(self.lds_sealing.get_source_references(),
                               self,self.lds_seal_list)

    def lds_seal_list(self,list):
        self.lds_sealing.set_source_reference_list(list)
        self.lists_changed = True

    def on_ldsseal_note_clicked(self,obj):
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

    def on_switch_page(self,obj,a,page):
        if page == 0:
            self.load_person_image()
            self.event_box.redraw()
        elif page == 6 and self.not_loaded:
            self.not_loaded = False
        elif page == 8 and self.lds_not_loaded:
            self.lds_not_loaded = False
            self.draw_lds()
        note_buf = self.notes_buffer
        text = unicode(note_buf.get_text(note_buf.get_start_iter(),
                                       note_buf.get_end_iter(),False))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)

        if not self.lds_not_loaded:
            self.check_lds()
        if (self.lds_baptism.is_empty() and self.lds_endowment.is_empty() 
            and self.lds_sealing.is_empty()):
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
            self.name_box.redraw()
            self.pname = RelLib.Name(new)
            self.lists_changed = True
            self.write_primary_name()

    def write_primary_name(self):
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

class ListBox:
    def __init__(self, parent, person, obj, label, button_list, titles):
        self.person = person
        self.label = label
        self.name = NameDisplay.displayer.display(self.person)
        self.db = parent.db
        self.parent = parent
        self.list_model = ListModel.ListModel(
            obj, titles, self.select_row, self.update)
        self.blist = button_list
        self.node_map = {}
        self.tree = obj
        self.changed = False
        self.blist[0].connect('clicked',self.add)
        self.blist[1].connect('clicked',self.update)
        self.blist[2].connect('clicked',self.delete)

    def add_object(self,item):
        self.data.append(item)
        
    def select_row(self,obj):
        store, node = obj.get_selected()
        enable = node != None
        for button in self.blist[1:]:
            button.set_sensitive(enable)

    def delete(self,obj):
        """Delete the selected event"""
        if Utils.delete_selected(obj,self.data):
            self.changed = True
            self.redraw()

    def update(self,obj):
        raise NotImplementedError

    def redraw(self):
        self.list_model.clear()
        self.node_map = {}
        for item in self.data:
            node = self.list_model.add(self.display_data(item),item)
            self.node_map[str(item)] = node
        if self.data:
            self.list_model.select_row(0)
        self.set_label()

    def display_data(self,item):
        raise NotImplementedError

    def delete(self,obj):
        """Deletes the selected name from the name list"""
        store,node = self.list_model.get_selected()
        if node:
            self.list_model.remove(self.list_model.get_object(node))
            self.changed = True
            self.redraw()

    def edit_callback(self,data):
        self.data.append(data)
        self.redraw()
        try:
            self.list_model.select_iter(self.node_map[str(data)])
        except:
            print self.node_map, data
            print "Edit callback failed"

    def set_label(self):
        if self.data:
            self.list_model.select_row(0)
            Utils.bold_label(self.label)
            self.blist[1].set_sensitive(True)
            self.blist[2].set_sensitive(True)
        else:
            Utils.unbold_label(self.label)
            self.blist[1].set_sensitive(False)
            self.blist[2].set_sensitive(False)

class ReorderListBox(ListBox):

    def __init__(self,parent,person,obj,label,button_list,evalues, dnd_type):

        ListBox.__init__(self,parent,person,obj,label,button_list,evalues)

        self.dnd_type = dnd_type

        obj.drag_dest_set(gtk.DEST_DEFAULT_ALL, [dnd_type.target()],
                          gtk.gdk.ACTION_COPY)
        obj.drag_source_set(gtk.gdk.BUTTON1_MASK, [dnd_type.target()],
                            gtk.gdk.ACTION_COPY)
        obj.connect('drag_data_get', self.drag_data_get)
        obj.connect('drag_data_received',self.drag_data_received)

    def drag_data_get(self,widget, context, sel_data, info, time):
        node = self.list_model.get_selected_objects()

        bits_per = 8; # we're going to pass a string
        pickled = pickle.dumps(node[0]);
        data = str((self.dnd_type.drag_type, self.person.get_handle(),
                    pickled));
        sel_data.set(sel_data.target, bits_per, data)

    def unpickle(self, data):
        self.data.insert(pickle.loads(data))
    
    def drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.list_model.get_row_at(x,y)
        
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]
            if mytype != self.dnd_type.drag_type:
                return
            elif person == self.person.get_handle():
                self.move_element(self.list_model.get_selected_row(),row)
            else:
                self.unpickle(data[2])
            self.changed = True
            self.redraw()

    def move_element(self,src,dest):
        if src != -1:
            obj = self.data[src]
            self.data.remove(obj)
            self.data.insert(dest,obj)

class AttrListBox(ListBox):

    titles = [
        # Title          Sort Column       Min Width, Type
        (_('Attribute'), ListModel.NOSORT, 200,       ListModel.TEXT),
        (_('Value'),     ListModel.NOSORT, 350,       ListModel.TEXT),
        (_('Source'),    ListModel.NOSORT, 50,        ListModel.TOGGLE),
        (_('Note'),      ListModel.NOSORT, 50,        ListModel.TOGGLE),
        ]

    def __init__(self, parent, person, obj, label, button_list):
        self.data = person.get_attribute_list()[:]
        ListBox.__init__(self, parent, person, obj, label,
                         button_list, self.titles)

    def add(self,obj):
        """Brings up the AttributeEditor for a new attribute"""
        AttrEdit.AttributeEditor(self.parent, None, self.name,
                                 const.personalAttributes,
                                 self.edit_callback,self.parent.window)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            attr = self.list_model.get_object(node)
            AttrEdit.AttributeEditor(self.parent, attr, self.name,
                                     const.personalAttributes,
                                     self.edit_callback,self.parent.window)

    def display_data(self,attr):
        has_note = attr.get_note()
        has_source = len(attr.get_source_references())> 0
        return [const.display_pattr(attr.get_type()), attr.get_value(),
                has_source, has_note]


class EventListBox(ReorderListBox):
    
    evalues = [
        # Title            Sort Column       Min Width,  Type
        (_('Event'),       ListModel.NOSORT, 125,        ListModel.COMBO),
        (_('Description'), ListModel.NOSORT, 150,        ListModel.TEXT),
        (_('Date'),        ListModel.NOSORT, 100,        ListModel.TEXT),
        (_('Place'),       ListModel.NOSORT, 100,        ListModel.TEXT),
        (_('Source'),      ListModel.NOSORT, 50,         ListModel.TOGGLE),
        (_('Note'),        ListModel.NOSORT, 50,         ListModel.TOGGLE)
        ]

    titles = ['Event', 'Description','Date','Place','Source','Note']

    def __init__(self,parent,person,obj,label,button_list):

        self.trans = TransTable.TransTable(self.titles)

        self.data = []
        if person.get_birth_handle():
            self.data.append(person.get_birth_handle())
        if person.get_death_handle():
            self.data.append(person.get_death_handle())
        for val in person.get_event_list():
            self.data.append(val)

        ReorderListBox.__init__(self, parent, person, obj, label,
                                button_list, self.evalues, DdTargets.EVENT)

    def add(self,obj):
        """Brings up the EventEditor for a new event"""
        EventEdit.EventEditor(
            self.parent, self.name, const.personalEvents,
            const.personal_events, None, None, 0,
            self.edit_callback, noedit=self.db.readonly)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if not node:
            return
        event = self.list_model.get_object(node)
        EventEdit.EventEditor(
            self.parent, self.name, const.personalEvents,
            const.personal_events,event, None, 0,
            self.edit_callback, noedit=self.db.readonly)

    def redraw(self):
        """redraw_event_list - Update both the birth and death place combo
        boxes for any changes that occurred in the 'Event Edit' window.
        Make sure not to allow the editing of a birth event to change
        any values in the death event, and vice versa.  Since updating a
        combo list resets its present value, this code will have to save
        and restore the value for the event *not* being edited."""

        self.list_model.clear()
        self.node_map = {}
        for handle in self.data:
            event = self.db.get_event_from_handle(handle)
            if not event:
                print "couldn't find",handle
            pname = place_title(self.db,event)
            has_note = event.get_note()
            has_source = len(event.get_source_references())> 0
            data = [const.display_pevent(event.get_name()),
                    event.get_description(), event.get_date(),
                    pname, has_source, has_note]
            node = self.list_model.add(data, event)
            self.node_map[handle] = node
        if self.data:
            self.list_model.select_row(0)
        self.set_label()

    def unpickle(self, data):
        foo = pickle.loads(data);
        for src in foo.get_source_references():
            base_handle = src.get_base_handle()
            newbase = self.db.get_source_from_handle(base_handle)
            src.set_base_handle(newbase.get_handle())
        place = foo.get_place_handle()
        if place:
            foo.set_place_handle(place.get_handle())
        self.data.insert(row,foo.get_handle())

class NameListBox(ReorderListBox):
    
    titles = [
        # Title              Sort Column       Min Width, Type
        (_('Family Name'),   ListModel.NOSORT, 225,       ListModel.TEXT),
        (_('Prefix'),        ListModel.NOSORT, 50,        ListModel.TEXT),
        (_('Given Name'),    ListModel.NOSORT, 200,       ListModel.TEXT),
        (_('Suffix'),        ListModel.NOSORT, 50,        ListModel.TEXT),
        (_('Type'),          ListModel.NOSORT, 100,       ListModel.TEXT),
        (_('Source'),        ListModel.NOSORT, 50,        ListModel.TOGGLE),
        (_('Note'),          ListModel.NOSORT, 50,        ListModel.TOGGLE),
        ]

    def __init__(self,parent,person,obj,label,button_list):
        self.data = person.get_alternate_names()[:]
        ReorderListBox.__init__(self, parent, person, obj, label,
                                button_list, self.titles, DdTargets.NAME)

    def add(self,obj):
        NameEdit.NameEditor(self.parent, None, self.edit_callback,
                            self.parent.window)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            NameEdit.NameEditor(self.parent, self.list_model.get_object(node),
                                self.edit_callback, self.window)

    def display_data(self,name):
        has_note = name.get_note()
        has_source = len(name.get_source_references())> 0
        return [name.get_surname(),name.get_surname_prefix(),
                name.get_first_name(), name.get_suffix(),
                _(name.get_type()),has_source,has_note]

    def unpickle(self, data):
        foo = pickle.loads(data);
        for src in foo.get_source_references():
            base_handle = src.get_base_handle()
            newbase = self.db.get_source_from_handle(base_handle)
            src.set_base_handle(newbase.get_handle())
        self.data.insert(row,foo)

class AddressListBox(ReorderListBox):
    
    titles = [
        # Title              Sort Column       Min Width, Type
        (_('Date'),          ListModel.NOSORT, 175,       ListModel.TEXT),
        (_('Address'),       ListModel.NOSORT, 150,       ListModel.TEXT),
        (_('City'),          ListModel.NOSORT, 100,       ListModel.TEXT),
        (_('State/Province'),ListModel.NOSORT, 75,        ListModel.TEXT),
        (_('Country'),       ListModel.NOSORT, 100,       ListModel.TEXT),
        (_('Source'),        ListModel.NOSORT, 50,        ListModel.TOGGLE),
        (_('Note'),          ListModel.NOSORT, 50,        ListModel.TOGGLE),
        ]

    def __init__(self,parent,person,obj,label,button_list):
        self.data = person.get_address_list()[:]
        ReorderListBox.__init__(self, parent, person, obj, label,
                                button_list, self.titles, DdTargets.ADDRESS)

    def add(self,obj):
        AddrEdit.AddressEditor(self.parent, None, self.edit_callback,
                               self.parent.window)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            item = self.list_model.get_object(node)
            AddrEdit.AddressEditor(self.parent, item,
                                   self.edit_callback, self.parent.window)

    def display_data(self,item):
        has_note = item.get_note()
        has_source = len(item.get_source_references())> 0
        return [item.get_date(),item.get_street(),
                item.get_city(), item.get_state(),
                item.get_country(), has_source,has_note]

    def unpickle(self,data):
        foo = pickle.loads(data);
        for src in foo.get_source_references():
            base_handle = src.get_base_handle()
            newbase = self.db.get_source_from_handle(base_handle)
            src.set_base_handle(newbase.get_handle())
        self.data.insert(row,foo)

class UrlListBox(ReorderListBox):
    
    titles = [
        # Title              Sort Column       Min Width, Type
        (_('Path'),          ListModel.NOSORT, 250,       ListModel.TEXT),
        (_('Description'),   ListModel.NOSORT, 100,       ListModel.TEXT),
        ]

    def __init__(self,parent,person,obj,label,button_list):
        self.data = person.get_url_list()[:]
        ReorderListBox.__init__(self, parent, person, obj, label,
                                button_list, self.titles, DdTargets.URL)

    def add(self,obj):
        UrlEdit.UrlEditor(self.parent, self.name, None,
                          self.edit_callback, self.parent.window)

    def update(self,obj):
        store,node = self.list_model.get_selected()
        if node:
            UrlEdit.UrlEditor(self.parent, self.name,
                              self.list_model.get_object(node),
                              self.edit_callback, self.window)

    def display_data(self,url):
        return [url.get_path(), url.get_description()]


