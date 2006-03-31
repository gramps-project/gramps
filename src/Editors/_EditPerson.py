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
from TransUtils import sgettext as _
from cgi import escape

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import Config
import Mime
import RelLib
import DateHandler
import NameDisplay
import DisplayState
import GrampsDisplay
import GrampsWidgets
import AutoComp
from _EditPrimary import EditPrimary
from DisplayTabs import *

from QuestionDialog import WarningDialog, ErrorDialog, QuestionDialog2
from DdTargets import DdTargets

try:
    set()
except:
    from sets import Set as set
    
#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

_select_gender = ((True,False,False),(False,True,False),(False,False,True))
_use_patronymic = set(["ru","RU","ru_RU","koi8r","ru_koi8r","russian","Russian"])

#-------------------------------------------------------------------------
#
# EditPerson class
#
#-------------------------------------------------------------------------
class EditPerson(EditPrimary):

    use_patronymic = locale.getlocale(locale.LC_TIME)[0] in _use_patronymic

    def __init__(self,state,uistate,track,person,callback=None):
        """Creates an edit window.  Associates a person with the window."""

        EditPrimary.__init__(self, state, uistate, track, person,
                             state.db.get_person_from_handle, callback)

    def empty_object(self):
        return RelLib.Person()

    def _local_init(self):
        self.pname = self.obj.get_primary_name()
        self.should_guess_gender = (not self.obj.get_gramps_id() and
                                    self.obj.get_gender () ==
                                    RelLib.Person.UNKNOWN)

        self.load_obj = None
        self.top = gtk.glade.XML(const.person_glade, "edit_person","gramps")
        self.define_top_level(self.top.get_widget("edit_person"), None,
                              _('Edit Person'))
        
        self.obj_photo = self.top.get_widget("personPix")
        self.eventbox = self.top.get_widget("eventbox1")

    def _post_init(self):
        self.load_person_image()
        self.surname_field.grab_focus()

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_widget("button15"))
        self.define_ok_button(self.top.get_widget("ok"), self.save)
        self.define_help_button(self.top.get_widget("button134"),'adv-pers')

        self.given.connect("focus_out_event",self.given_focus_out_event)
        self.top.get_widget("button177").connect("clicked", self.edit_name_clicked)

        self.eventbox.connect('button-press-event',self.image_button_press)

    def _setup_fields(self):

        self.private = GrampsWidgets.PrivacyButton(
            self.top.get_widget('private'),
            self.obj)

        self.gender = GrampsWidgets.MonitoredMenu(
            self.top.get_widget('gender'),
            self.obj.set_gender,
            self.obj.get_gender,
            (
            (_('female'),RelLib.Person.FEMALE),
            (_('male'),RelLib.Person.MALE),
            (_('unknown'),RelLib.Person.UNKNOWN)
            ),
            self.db.readonly)

        self.ntype_field = GrampsWidgets.MonitoredType(
            self.top.get_widget("ntype"),
            self.pname.set_type,
            self.pname.get_type,
            dict(Utils.name_types),
            RelLib.Name.CUSTOM,
            self.db.readonly)

        self.marker = GrampsWidgets.MonitoredType(
            self.top.get_widget('marker'),
            self.obj.set_marker,
            self.obj.get_marker,
            dict(Utils.marker_types),
            RelLib.PrimaryObject.MARKER_CUSTOM,
            self.db.readonly)
        
        if self.use_patronymic:
            self.prefix = GrampsWidgets.MonitoredEntry(
                self.top.get_widget("prefix"),
                self.pname.set_patronymic,
                self.pname.get_patronymic,
                self.db.readonly)
            
            prefix_label = self.top.get_widget('prefix_label')
            prefix_label.set_text(_('Patronymic:'))
            prefix_label.set_use_underline(True)
        else:
            self.prefix = GrampsWidgets.MonitoredEntry(
                self.top.get_widget("prefix"),
                self.pname.set_surname_prefix,
                self.pname.get_surname_prefix,
                self.db.readonly)

        self.suffix = GrampsWidgets.MonitoredEntry(
            self.top.get_widget("suffix"),
            self.pname.set_suffix,
            self.pname.get_suffix,
            self.db.readonly)

        self.given = GrampsWidgets.MonitoredEntry(
            self.top.get_widget("given_name"),
            self.pname.set_first_name,
            self.pname.get_first_name,
            self.db.readonly)

        self.title = GrampsWidgets.MonitoredEntry(
            self.top.get_widget("title"),
            self.pname.set_title,
            self.pname.get_title,
            self.db.readonly)
        
        self.surname_field = GrampsWidgets.MonitoredEntry(
            self.top.get_widget("surname"),
            self.pname.set_surname,
            self.pname.get_surname,
            self.db.readonly,
            autolist=self.db.get_surname_list())

        self.gid = GrampsWidgets.MonitoredEntry(
            self.top.get_widget("gid"),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        
        """
        notebook = gtk.Notebook()

        self.event_list = self._add_tab(
            notebook,
            PersonEventEmbedList(self.dbstate,self.uistate,
                                 self.track,self.obj))
        
        self.name_list = self._add_tab(
            notebook,
            NameEmbedList(self.dbstate, self.uistate, self.track,
                          self.obj.get_alternate_names()))
        
        self.srcref_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate,
                            self.track, self.obj.source_list))
        
        self.attr_list = self._add_tab(
            notebook,
            AttrEmbedList(self.dbstate,self.uistate, self.track,
                          self.obj.get_attribute_list()))
        
        self.addr_list = self._add_tab(
            notebook,
            AddrEmbedList(self.dbstate,self.uistate,self.track,
                          self.obj.get_address_list()))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_object()))
        
        self.gallery_tab = self._add_tab(
            notebook,
            GalleryTab(self.dbstate, self.uistate, self.track,
                       self.obj.get_media_list()))
        
        self.web_list = self._add_tab(
            notebook,
            WebEmbedList(self.dbstate,self.uistate,self.track,
                         self.obj.get_url_list()))

        notebook.show_all()
        self.top.get_widget('vbox').pack_start(notebook,True)

    def build_menu_names(self,person):
        win_menu_label = self.nd.display(person)
        if not win_menu_label.strip():
            win_menu_label = _("New Person")
        return (_('Edit Person'),win_menu_label)

#     def set_list_dnd(self,obj, get, begin, receive):
#         obj.drag_dest_set(gtk.DEST_DEFAULT_ALL, [DdTargets.NAME.target()],
#                           gtk.gdk.ACTION_COPY)
#         obj.drag_source_set(gtk.gdk.BUTTON1_MASK,[DdTargets.NAME.target()],
#                             gtk.gdk.ACTION_COPY)
#         obj.connect('drag_data_get', get)
#         obj.connect('drag_begin', begin)
#         if not self.db.readonly:
#             obj.connect('drag_data_received', receive)

    def image_callback(self,ref):
        obj = self.db.get_object_from_handle(ref.get_reference_handle())
        self.load_photo(obj)

    def image_button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:

            media_list = self.obj.get_media_list()
            if media_list:
                from Editors import EditMediaRef
                
                media_ref = media_list[0]
                object_handle = media_ref.get_reference_handle()
                media_obj = self.db.get_object_from_handle(object_handle)

                EditMediaRef(self.dbstate, self.uistate, self.track,
                             media_obj, media_ref, self.image_callback)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            media_list = self.obj.get_media_list()
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
        progname = Mime.get_application(mtype)
        
        if progname and len(progname) > 1:
            Utils.add_menuitem(menu,_("Open in %s") % progname[1],
                               photo,self.popup_view_photo)
        Utils.add_menuitem(menu,_("Edit Object Properties"),photo,
                           self.popup_change_description)
        menu.popup(None,None,None,event.button,event.time)

    def popup_view_photo(self, obj):
        """Open this picture in a picture viewer"""
        media_list = self.obj.get_media_list()
        if media_list:
            ph = media_list[0]
            object_handle = ph.get_reference_handle()
            Utils.view_photo(self.db.get_object_from_handle(object_handle))

    def popup_change_description(self,obj):
        media_list = self.obj.get_media_list()
        if media_list:
            from Editors import EditMediaRef
            
            media_ref = media_list[0]
            object_handle = media_ref.get_reference_handle()
            media_obj = self.db.get_object_from_handle(object_handle)
            EditMediaRef(self.dbstate, self.uistate, self.track,
                         media_obj, media_ref, self.image_callback)

    def given_focus_out_event (self, entry, event):
        if not self.should_guess_gender:
            return False
        try:
            self.gender.force(self.db.genderStats.guess_gender(entry.get_text()))
        except:
            return False
        return False

    def load_photo(self,photo):
        """loads, scales, and displays the person's main photo"""
        self.load_obj = photo
        if photo == None:
            self.obj_photo.hide()
        else:
            try:
                i = gtk.gdk.pixbuf_new_from_file(photo)
                ratio = float(max(i.get_height(),i.get_width()))
                scale = float(100.0)/ratio
                x = int(scale*(i.get_width()))
                y = int(scale*(i.get_height()))
                i = i.scale_simple(x,y,gtk.gdk.INTERP_BILINEAR)
                self.obj_photo.set_from_pixbuf(i)
                self.obj_photo.show()
            except:
                self.obj_photo.hide()

    def _check_for_unknown_gender(self):
        if self.obj.get_gender() == RelLib.Person.UNKNOWN:
            dialog = QuestionDialog2(
                _("Unknown gender specified"),
                _("The gender of the person is currently unknown. "
                  "Usually, this is a mistake. You may choose to "
                  "either continue saving, or returning to the "
                  "Edit Person dialog to fix the problem."),
                _("Continue saving"), _("Return to window"),
                self.window)
            if not dialog.run():
                return True
        return False
        
    def _check_and_update_id(self):
        original = self.db.get_person_from_handle(self.obj.get_handle())
        
        if original and original.get_gramps_id() != self.obj.get_gramps_id():
            idval = self.obj.get_gramps_id()
            person = self.db.get_person_from_gramps_id(idval)
            if person:
                n = self.nd.display(person)
                msg1 = _("GRAMPS ID value was not changed.")
                msg2 = _("You have attempted to change the GRAMPS ID to a value "
                         "of %(grampsid)s. This value is already used by %(person)s.") % {
                    'grampsid' : idval,
                    'person' : n }
                WarningDialog(msg1,msg2)

    def _update_family_ids(self, trans):
        # Update each of the families child lists to reflect any
        # change in ordering due to the new birth date
        family = self.obj.get_main_parents_family_handle()
        if (family):
            f = self.db.find_family_from_handle(family,trans)
            new_order = self.reorder_child_list(self.obj,f.get_child_handle_list())
            f.set_child_handle_list(new_order)
        for (family, rel1, rel2) in self.obj.get_parent_family_handle_list():
            f = self.db.find_family_from_handle(family,trans)
            new_order = self.reorder_child_list(self.obj,f.get_child_handle_list())
            f.set_child_handle_list(new_order)

        error = False
        original = self.db.get_person_from_handle(self.obj.handle)

        if original:
            (female,male,unknown) = _select_gender[self.obj.get_gender()]
            if male and original.get_gender() != RelLib.Person.MALE:
                for temp_family_handle in self.obj.get_family_handle_list():
                    temp_family = self.db.get_family_from_handle(temp_family_handle)
                    if self.obj == temp_family.get_mother_handle():
                        if temp_family.get_father_handle() != None:
                            error = True
                        else:
                            temp_family.set_mother_handle(None)
                            temp_family.set_father_handle(self.obj)
            elif female and original != RelLib.Person.FEMALE:
                for temp_family_handle in self.obj.get_family_handle_list():
                    temp_family = self.db.get_family_from_handle(temp_family_handle)
                    if self.obj == temp_family.get_father_handle():
                        if temp_family.get_mother_handle() != None:
                            error = True
                        else:
                            temp_family.set_father_handle(None)
                            temp_family.set_mother_handle(self.obj)
            elif unknown and original.get_gender() != RelLib.Person.UNKNOWN:
                for temp_family_handle in self.obj.get_family_handle_list():
                    temp_family = self.db.get_family_from_handle(temp_family_handle)
                    if self.obj == temp_family.get_father_handle():
                        if temp_family.get_mother_handle() != None:
                            error = True
                        else:
                            temp_family.set_father_handle(None)
                            temp_family.set_mother_handle(self.obj)
                    if self.obj == temp_family.get_mother_handle():
                        if temp_family.get_father_handle() != None:
                            error = True
                        else:
                            temp_family.set_mother_handle(None)
                            temp_family.set_father_handle(self.obj)

            if error:
                msg2 = _("Problem changing the gender")
                msg = _("Changing the gender caused problems "
                        "with marriage information.\nPlease check "
                        "the person's marriages.")
                ErrorDialog(msg)

    def save(self,*obj):
        """
        Save the data.
        """

        if self.object_is_empty():
            ErrorDialog(_("Cannot save person"),
                        _("No data exists for this person. Please "
                          "enter data or cancel the edit."))
            return
        
        if self._check_for_unknown_gender():
            return

        (br, dr, el) = self.event_list.return_info()
        self.obj.set_birth_ref(br)
        self.obj.set_death_ref(dr)
        self.obj.set_event_ref_list(el)
        
        self.window.hide()

        trans = self.db.transaction_begin()

        self._check_and_update_id()
        self._update_family_ids(trans)

        if not self.obj.get_handle():
            self.db.add_person(self.obj, trans)
        else:
            if not self.obj.get_gramps_id():
                self.obj.set_gramps_id(self.db.find_next_person_gramps_id())
            self.db.commit_person(self.obj, trans)

        self.db.transaction_commit(trans,_("Edit Person (%s)") % self.nd.display(self.obj))
        self.close()
        if self.callback:
            self.callback(self.obj)

    def edit_name_clicked(self,obj):
        NameEdit.NameEditor(self.dbstate, self.uistate, self.track,
                            self.pname, self.update_name)

    def update_name(self,name):
        for obj in (self.suffix, self.prefix, self.given, self.title,
                    self.ntype_field, self.surname_field):
            obj.update()

    def load_person_image(self):
        media_list = self.obj.get_media_list()
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

