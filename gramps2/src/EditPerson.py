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
import os
import locale
import ListBox
import sets
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
import RelLib
import Sources
import DateEdit
import Date
import DateHandler
import NameDisplay
import NameEdit
import NoteEdit
import Spell
import DisplayState

from QuestionDialog import WarningDialog, ErrorDialog, SaveDialog, QuestionDialog2

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
class EditPerson(DisplayState.ManagedWindow):

    use_patronymic = locale.getlocale(locale.LC_TIME)[0] in _use_patronymic
    
    def __init__(self,state,uistate,person,callback=None):
        """Creates an edit window.  Associates a person with the window."""

        self.dp = DateHandler.parser
        self.dd = DateHandler.displayer
        self.nd = NameDisplay.displayer

        win_menu_label = self.nd.display(person)
        if not win_menu_label.strip():
            win_menu_label = _("New Person")

        DisplayState.ManagedWindow.__init__(
            self, uistate, [], self, win_menu_label, _('Edit Person'))

        if self.already_exist:
            return

        self.state = state
        self.uistate = uistate
        self.retval = const.UPDATE_PERSON
        
        if person:
            self.orig_handle = person.get_handle()
        else:
            self.orig_handle = ""
            
        # UGLY HACK to refresh person object from handle if that exists
        # done to ensure that the person object is not stale, as it could
        # have been changed by something external (merge, tool, etc).
        if self.orig_handle:
            person = self.state.db.get_person_from_handle(self.orig_handle)
        self.person = person
        self.orig_surname = self.person.get_primary_name().get_group_name()
        #if self.parent_window.child_windows.has_key(self.orig_handle):
        #    self.parent_window.child_windows[self.orig_handle].present(None)
        #    return
        self.db = self.state.db
        self.callback = callback
        self.child_windows = {}
        self.path = self.db.get_save_path()
        self.not_loaded = True
        self.lds_not_loaded = True
        self.lists_changed = False
        self.pdmap = {}
        self.add_places = []
        self.should_guess_gender = (not person.get_gramps_id() and
                                    person.get_gender () ==
                                    RelLib.Person.UNKNOWN)

        for key in self.db.get_place_handles():
            p = self.db.get_place_from_handle(key).get_display_info()
            self.pdmap[p[0]] = key

        mod = not self.db.readonly
            
        self.load_obj = None
        self.top = gtk.glade.XML(const.editPersonFile, "edit_person","gramps")
        self.window = self.get_widget("edit_person")
        self.window.set_title("%s - GRAMPS" % _('Edit Person'))
        
        #self.icon_list = self.top.get_widget("iconlist")
        #self.gallery = ImageSelect.Gallery(person, self.db.commit_person,
        #                                   self.path, self.icon_list,
        #                                   self.db, self, self.window)

        self.build_gallery(self.get_widget('iconbox'))

        self.marker = self.get_widget('marker')
        self.marker.set_sensitive(mod)
        if person:
            try:
                defval = person.get_marker()[0]
            except:
                defval = (RelLib.PrimaryObject.MARKER_NONE,"")
        else:
            defval = None
        self.marker_type_selector = AutoComp.StandardCustomSelector(
            Utils.marker_types, self.marker,
            RelLib.PrimaryObject.MARKER_CUSTOM, defval)
        
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
        event_sel_btn = self.top.get_widget('event_sel')
        event_edit_btn = self.top.get_widget('event_edit')
        attr_add_btn = self.top.get_widget('attr_add')
        attr_delete_btn = self.top.get_widget('attr_del')
        attr_edit_btn = self.top.get_widget('attr_edit')
        addr_add_btn = self.top.get_widget('addr_add')
        addr_delete_btn = self.top.get_widget('addr_del')
        addr_edit_btn = self.top.get_widget('addr_edit')

        self.notes_field = self.get_widget("personNotes")
        self.notes_field.set_editable(mod)
        self.spell_notes = Spell.Spell(self.notes_field)
        self.flowed = self.get_widget("flowed")
        self.flowed.set_sensitive(mod)
        self.preform = self.get_widget("preform")
        self.preform.set_sensitive(mod)
        self.attr_list = self.get_widget("attr_list")
        self.web_list = self.get_widget("web_list")
        self.web_go = self.get_widget("web_go")
        self.addr_list = self.get_widget("address_list")
        self.event_ref_list = self.get_widget("eventList")
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

        self.birth_ref = person.get_birth_ref()
        self.death_ref = person.get_death_ref()

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
        self.event_box = ListBox.EventListBox(
            self, self.person, self.event_ref_list, events_label,
            [event_add_btn,event_edit_btn,event_delete_btn,event_sel_btn])

        self.attr_box = ListBox.AttrListBox(
            self, self.person, self.attr_list, attr_label,
            [attr_add_btn, attr_edit_btn, attr_delete_btn])

        self.addr_box = ListBox.AddressListBox(
            self, self.person, self.addr_list, addr_label,
            [addr_add_btn, addr_edit_btn, addr_delete_btn])

        self.name_box = ListBox.NameListBox(
            self, self.person, self.name_list, names_label,
            [name_add_btn, name_edit_btn, name_delete_btn])

        self.url_box = ListBox.UrlListBox(
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

        self.ntype_selector = \
                           AutoComp.StandardCustomSelector(Utils.name_types,
                                                           self.ntype_field,
                                                           RelLib.Name.CUSTOM,
                                                           RelLib.Name.BIRTH)
        self.write_primary_name()
        
        self.load_person_image()
        
        # set notes data
        self.notes_buffer = self.notes_field.get_buffer()
        if person.get_note():
            self.notes_buffer.set_text(person.get_note())
            if person.get_note_object().get_format() == 1:
                self.preform.set_active(True)
            else:
                self.flowed.set_active(True)
            Utils.bold_label(self.notes_label)

        self.top.signal_autoconnect({
            "destroy_passed_object"     : self.on_cancel_edit,
            "on_up_clicked"             : self.on_up_clicked,
            "on_down_clicked"           : self.on_down_clicked,
            "on_apply_person_clicked"   : self.on_apply_person_clicked,
            "on_delete_event"           : self.on_delete_event,
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

        self.private.set_active(self.person.get_privacy())

        self.eventbox.connect('button-press-event',self.image_button_press)

        self.event_box.redraw()
        self.attr_box.redraw()
        self.addr_box.redraw() 
        self.name_box.redraw()
        self.url_box.redraw()
        self.get_widget("notebook").set_current_page(0)
        self.surname.grab_focus()

        if self.db.readonly:
            for i in ["ok", "aka_add", "aka_del", "event_add", "event_del",
                      "attr_add", "attr_del", "addr_add",
                      "addr_del", "media_add", "media_sel", "media_del",
                      "url_add", "url_del", "add_src", "del_src" ]:
                self.get_widget(i).set_sensitive(False)

        self.window.show()

    def build_pdmap(self):
        self.pdmap.clear()
        cursor = self.db.get_place_cursor()
        data = cursor.next()
        while data:
            if data[1][2]:
                self.pdmap[data[1][2]] = data[0]
            data = cursor.next()
        cursor.close()

    def build_gallery(self,container):
        self.iconmodel = gtk.ListStore(gtk.gdk.Pixbuf,str)
        self.iconlist = gtk.IconView(self.iconmodel)
        self.iconlist.set_pixbuf_column(0)
        self.iconlist.set_text_column(1)
        self.iconlist.show()
        container.add(self.iconlist)

        for ref in self.person.get_media_list():
            obj = self.db.get_object_from_handle(ref.get_reference_handle())
            pixbuf = self.get_image(obj)
            self.iconmodel.append(row=[pixbuf,obj.get_description()])

    def get_image(self,obj):
        import ImgManip
        
        mtype = obj.get_mime_type()
        if mtype[0:5] == "image":
            image = ImgManip.get_thumbnail_image(obj.get_path())
        else:
            image = Utils.find_mime_type_pixbuf(mtype)
        if not image:
            image = gtk.gdk.pixbuf_new_from_file(const.icon)
        return image
        
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
        if mtype and mtype.startswith("image"):
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

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')

    def lds_field(self,lds_ord,combo,date,place):
        build_combo(combo,_temple_names)
        temple_code = const.lds_temple_to_abrev.get(lds_ord.get_temple(),"")
        index = _temple_names.index(temple_code)
        combo.set_active(index)
        if not lds_ord.is_empty():
            stat = lds_ord.get_status()
        else:
            stat = 0
        date.set_text(DateHandler.get_date(lds_ord))

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

        gender = self.db.genderStats.guess_gender(unicode(entry.get_text ()))
        self.gender.set_active( gender)

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
            n = "<i>%s</i>" % self.nd.display(self.person)
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
            n = "<i>%s</i>" % self.nd.display(self.person)
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

        ntype = self.ntype_selector.get_values()
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

        
        #TODO#if self.complete.get_active() != self.person.get_complete_flag():
        #    changed = True
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
        if ntype != name.get_type():
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
        date_str = unicode(self.ldsbap_date.get_text())
        DateHandler.set_date(self.lds_baptism,date_str)
        temple = _temple_names[self.ldsbap_temple.get_active()]
        if const.lds_temple_codes.has_key(temple):
            self.lds_baptism.set_temple(const.lds_temple_codes[temple])
        else:
            self.lds_baptism.set_temple("")
        self.lds_baptism.set_place_handle(self.get_place(self.ldsbapplace,1))

        date_str = unicode(self.ldsend_date.get_text())
        DateHandler.set_date(self.lds_endowment,date_str)
        temple = _temple_names[self.ldsend_temple.get_active()]
        if const.lds_temple_codes.has_key(temple):
            self.lds_endowment.set_temple(const.lds_temple_codes[temple])
        else:
            self.lds_endowment.set_temple("")
        self.lds_endowment.set_place_handle(self.get_place(self.ldsendowplace,1))

        date_str = unicode(self.ldsseal_date.get_text())
        DateHandler.set_date(self.lds_sealing,date_str)
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
        self.person.set_alternate_names(self.name_box.data)
        self.person.set_url_list(self.url_box.data)
        self.person.set_attribute_list(self.attr_box.data)
        self.person.set_address_list(self.addr_box.data)

        self.person.set_birth_ref(None)
        self.person.set_death_ref(None)
        eref_list = self.event_box.data[:]
        for (event_ref,event) in eref_list:
            if event.get_type()[0] == RelLib.Event.BIRTH:
                self.person.set_birth_ref(event_ref)
                self.event_box.data.remove((event_ref,event))
            if event.get_type()[0] == RelLib.Event.DEATH:
                self.person.set_death_ref(event_ref)
                self.event_box.data.remove((event_ref,event))
        eref_list = [event_ref for (event_ref,event) in self.event_box.data]
        self.person.set_event_ref_list(eref_list)

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
        ntype = self.ntype_selector.get_values()
        given = unicode(self.given.get_text())
        title = unicode(self.title.get_text())
        idval = unicode(self.gid.get_text())

        name = self.pname
        if idval != self.person.get_gramps_id():
            person = self.db.get_person_from_gramps_id(idval)
            if not person:
                self.person.set_gramps_id(idval)
            else:
                n = self.nd.display(person)
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

        self.build_pdmap()


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

        self.person.set_marker(self.marker_type_selector.get_values())
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

        self.person.set_source_reference_list(self.srcreflist)
        self.update_lists()

        if not self.person.get_handle():
            self.db.add_person(self.person, trans)
        else:
            if not self.person.get_gramps_id():
                self.person.set_gramps_id(self.db.find_next_person_gramps_id())
            self.db.commit_person(self.person, trans)

        n = self.nd.display(self.person)

        for (event_ref,event) in self.event_box.get_changed_objects():
            self.db.commit_event(event,trans)
        
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
        ntype = self.ntype_selector.get_values()
        self.pname.set_type(ntype)
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
                mime_type = obj.get_mime_type()
                if mime_type and mime_type.startswith("image"):
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

        self.ntype_selector.set_values(self.pname.get_type())
        self.title.set_text(self.pname.get_title())

    def birth_dates_in_order(self,list):
        """Check any *valid* birthdates in the list to insure that they are in
        numerically increasing order."""
        inorder = True
        prev_date = 0
        for i in range(len(list)):
            child_handle = list[i]
            child = self.db.get_person_from_handle(child_handle)
            if child.get_birth_ref():
                event = self.db.get_event_from_handle(child.get_birth_ref().ref)
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
        event_ref = person.get_birth_ref()
        if event_ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            person_bday = event.get_date_object().get_sort_value()
        else:
            person_bday = 0

        # First, see if the person needs to be moved forward in the list

        index = list.index(person.get_handle())
        target = index
        for i in range(index-1, -1, -1):
            other = self.db.get_person_from_handle(list[i])
            event_ref = other.get_birth_ref()
            if event_ref:
                event = self.db.get_event_from_handle(event_ref.ref)
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
                event_ref = other.get_birth_ref()
                if event_ref:
                    event = self.db.get_event_from_handle(event_ref.ref)
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
