#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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

"""
EditPerson Dialog. Provide the interface to allow the GRAMPS program
to edit information about a particular Person.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import locale
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
from gui.utils import add_menuitem, open_file_with_default_application
import Mime
import gen.lib
from gui import widgets
from BasicUtils import name_displayer
import Errors
from glade import Glade
from gen.utils import set_birth_death_index

from editprimary import EditPrimary
from editmediaref import EditMediaRef
from editname import EditName
import config
from QuestionDialog import ErrorDialog, ICON

from displaytabs import (PersonEventEmbedList, NameEmbedList, SourceEmbedList, 
                         AttrEmbedList, AddrEmbedList, NoteTab, GalleryTab, 
                         WebEmbedList, PersonRefEmbedList, LdsEmbedList, 
                         PersonBackRefList)
from gen.plug import CATEGORY_QR_PERSON
    
#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

_select_gender = ((True, False, False),
                  (False, True, False),
                  (False, False, True))

class EditPerson(EditPrimary):
    """
    The EditPerson dialog is derived from the EditPrimary class. 
    
    It allows for the editing of the primary object type of Person.
    
    """

    QR_CATEGORY = CATEGORY_QR_PERSON

    def __init__(self, dbstate, uistate, track, person, callback=None):
        """
        Create an EditPerson window.  
        
        Associate a person with the window.
        
        """
        EditPrimary.__init__(self, dbstate, uistate, track, person, 
                             dbstate.db.get_person_from_handle, 
                             dbstate.db.get_person_from_gramps_id, callback)

    def empty_object(self):
        """
        Return an empty Person object for comparison for changes. 
        
        This is used by the base class (EditPrimary).
        
        """
        return gen.lib.Person()

    def get_menu_title(self):
        if self.obj.get_handle():
            name = name_displayer.display(self.obj)
            title = _('Person: %(name)s') % {'name': name}
        else:
            name = name_displayer.display(self.obj)
            if name:
                title = _('New Person: %(name)s')  % {'name': name}
            else:
                title = _('New Person')
        return title

    def _local_init(self):
        """
        Performs basic initialization, including setting up widgets and the 
        glade interface. 
        
        Local initialization function. 
        This is called by the base class of EditPrimary, and overridden here.
        
        """
        self.width_key = 'interface.person-width'
        self.height_key = 'interface.person-height'
        self.pname = self.obj.get_primary_name()
        self.should_guess_gender = (not self.obj.get_gramps_id() and
                                    self.obj.get_gender () ==
                                    gen.lib.Person.UNKNOWN)

        self.load_obj = None
        self.load_rect = None
        self.top = Glade()

        self.set_window(self.top.toplevel, None, 
                        self.get_menu_title())
        
        self.obj_photo = self.top.get_object("personPix")
        self.eventbox = self.top.get_object("eventbox1")
        
        self.set_contexteventbox(self.top.get_object("eventboxtop"))
        

    def _post_init(self):
        """
        Handle any initialization that needs to be done after the interface is 
        brought up.
         
        Post initalization function. 
        This is called by _EditPrimary's init routine, and overridden in the 
        derived class (this class).
        
        """
        self.load_person_image()
        if self.pname.get_surname() and not self.pname.get_first_name():
            self.given.grab_focus()
        else:
            self.surname_field.grab_focus()

    def _connect_signals(self):
        """
        Connect any signals that need to be connected. 
        Called by the init routine of the base class (_EditPrimary).
        """
        self.define_cancel_button(self.top.get_object("button15"))
        self.define_ok_button(self.top.get_object("ok"), self.save)
        self.define_help_button(self.top.get_object("button134"))

        self.given.connect("focus_out_event", self._given_focus_out_event)
        self.top.get_object("button177").connect("clicked",
                                                 self._edit_name_clicked)

        self.eventbox.connect('button-press-event',
                                self._image_button_press)

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected. 
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('person-rebuild', self._do_close)
        self._add_db_signal('person-delete', self.check_for_close)
        self._add_db_signal('family-rebuild', self.family_change)
        self._add_db_signal('family-delete', self.family_change)
        self._add_db_signal('family-update', self.family_change)
        self._add_db_signal('family-add', self.family_change)
        self._add_db_signal('event-update', self.event_updated)
        self._add_db_signal('event-rebuild', self.event_updated)
        self._add_db_signal('event-delete', self.event_updated)

    def family_change(self, handle_list=[]):
        """
        Callback for family change signals. 
        
        This should rebuild the 
           backreferences to family in person when:
            1)a family the person is parent of changes. Person could have 
              been removed
            2)a family the person is child in changes. Child could have been 
              removed
            3)a family is changed. The person could be added as child or
              parent
            
        """
        #As this would be an extensive check, we choose the easy path and
        #   rebuild family backreferences on all family changes
        self._update_families()

    def _update_families(self):
        phandle = self.obj.get_handle()
        if phandle:
            #new person has no handle yet and cannot be in a family.
            person = self.dbstate.db.get_person_from_handle(phandle)
            self.obj.set_family_handle_list(person.get_family_handle_list())
            self.obj.set_parent_family_handle_list(
                                        person.get_parent_family_handle_list())
            #a family groupname in event_list might need to be changed
            # we just rebuild the view always
            self.event_list.rebuild_callback()

    def event_updated(self, obj):
        #place in event might have changed, or person event shown in the list
        # we just rebuild the view always
        self.event_list.rebuild_callback()

    def _setup_fields(self):
        """
        Connect the GrampsWidget objects to field in the interface. 
        
        This allows the widgets to keep the data in the attached Person object
        up to date at all times, eliminating a lot of need in 'save' routine.
        
        """

        self.private = widgets.PrivacyButton(
            self.top.get_object('private'), 
            self.obj, 
            self.db.readonly)

        self.gender = widgets.MonitoredMenu(
            self.top.get_object('gender'), 
            self.obj.set_gender, 
            self.obj.get_gender, 
            (
            (_('female'), gen.lib.Person.FEMALE), 
            (_('male'), gen.lib.Person.MALE), 
            (_('unknown'), gen.lib.Person.UNKNOWN)
            ), 
            self.db.readonly)

        self.marker = widgets.MonitoredDataType(
            self.top.get_object('marker'), 
            self.obj.set_marker, 
            self.obj.get_marker, 
            self.db.readonly,
            self.db.get_marker_types(),
            )
        
        self.ntype_field = widgets.MonitoredDataType(
            self.top.get_object("ntype"), 
            self.pname.set_type, 
            self.pname.get_type,
            self.db.readonly,
            self.db.get_name_types())

        self.prefix_suffix = widgets.MonitoredComboSelectedEntry(
                self.top.get_object("prefixcmb"), 
                self.top.get_object("prefixentry"),
                [_('Prefix'), _('Suffix')],
                [self.pname.set_surname_prefix, self.pname.set_suffix], 
                [self.pname.get_surname_prefix, self.pname.get_suffix],
                default = config.get('interface.prefix-suffix'),
                read_only = self.db.readonly)
        
        self.patro_title = widgets.MonitoredComboSelectedEntry(
                self.top.get_object("patrocmb"), 
                self.top.get_object("patroentry"),
                [_('Patronymic'), _('Person|Title')],
                [self.pname.set_patronymic, self.pname.set_title], 
                [self.pname.get_patronymic, self.pname.get_title],
                default = config.get('interface.patro-title'),
                read_only = self.db.readonly)

        self.call = widgets.MonitoredEntry(
            self.top.get_object("call"), 
            self.pname.set_call_name, 
            self.pname.get_call_name, 
            self.db.readonly)

        self.given = widgets.MonitoredEntry(
            self.top.get_object("given_name"), 
            self.pname.set_first_name, 
            self.pname.get_first_name, 
            self.db.readonly)

        self.surname_field = widgets.MonitoredEntry(
            self.top.get_object("surname"), 
            self.pname.set_surname, 
            self.pname.get_surname, 
            self.db.readonly, 
            autolist=self.db.get_surname_list())

        self.gid = widgets.MonitoredEntry(
            self.top.get_object("gid"), 
            self.obj.set_gramps_id, 
            self.obj.get_gramps_id, 
            self.db.readonly)

        #make sure title updates automatically
        for obj in [self.top.get_object("surname"),
                    self.top.get_object("given_name"),
                    self.top.get_object("patroentry"),
                    self.top.get_object("call"),
                    self.top.get_object("prefixentry"),
                    ]:
            obj.connect('changed', self._changed_name)

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and insert them into the main window.
        """
        notebook = gtk.Notebook()
        notebook.set_scrollable(True)

        self.event_list = PersonEventEmbedList(self.dbstate,
                                               self.uistate, 
                                               self.track,
                                               self.obj)
        self._add_tab(notebook, self.event_list) 
        self.track_ref_for_deletion("event_list")
        
        self.name_list = NameEmbedList(self.dbstate,
                                       self.uistate,
                                       self.track, 
                                       self.obj.get_alternate_names(),
                                       self.obj,
                                       self.name_callback)
        self._add_tab(notebook, self.name_list)
        self.track_ref_for_deletion("name_list")
        
        self.srcref_list = SourceEmbedList(self.dbstate,
                                           self.uistate,
                                           self.track,
                                           self.obj)
        self._add_tab(notebook, self.srcref_list) 
        self.track_ref_for_deletion("srcref_list")
        
        self.attr_list = AttrEmbedList(self.dbstate,
                                       self.uistate,
                                       self.track, 
                                       self.obj.get_attribute_list())
        self._add_tab(notebook, self.attr_list) 
        self.track_ref_for_deletion("attr_list")
        
        self.addr_list = AddrEmbedList(self.dbstate,
                                       self.uistate,
                                       self.track, 
                                       self.obj.get_address_list())
        self._add_tab(notebook, self.addr_list) 
        self.track_ref_for_deletion("addr_list")
        
        self.note_tab = NoteTab(self.dbstate,
                                self.uistate,
                                self.track, 
                                self.obj.get_note_list(),
                                self.get_menu_title(),
                                notetype=gen.lib.NoteType.PERSON)
        self._add_tab(notebook, self.note_tab) 
        self.track_ref_for_deletion("note_tab")
        
        self.gallery_tab = GalleryTab(self.dbstate,
                                      self.uistate,
                                      self.track, 
                                      self.obj.get_media_list(),
                                      self.load_person_image)
        self._add_tab(notebook, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")
        
        self.web_list = WebEmbedList(self.dbstate,
                                     self.uistate,
                                     self.track, 
                                     self.obj.get_url_list())
        self._add_tab(notebook, self.web_list)
        self.track_ref_for_deletion("web_list")

        self.person_ref_list = PersonRefEmbedList(self.dbstate, self.uistate, 
                                                  self.track, 
                                                  self.obj.get_person_ref_list())
        self._add_tab(notebook, self.person_ref_list)
        self.track_ref_for_deletion("person_ref_list")

        self.lds_list = LdsEmbedList(self.dbstate,
                                     self.uistate,
                                     self.track, 
                                     self.obj.get_lds_ord_list())
        self._add_tab(notebook, self.lds_list)
        self.track_ref_for_deletion("lds_list")

        self.backref_tab = PersonBackRefList(self.dbstate,
                                             self.uistate,
                                             self.track,
                              self.db.find_backlink_handles(self.obj.handle))
        self._add_tab(notebook, self.backref_tab)
        self.track_ref_for_deletion("backref_tab")

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.top.get_object('vbox').pack_start(notebook, True)

    def _changed_name(self, obj):
        """
        callback to changes typed by user to the person name.
        Update the window title, and default name in name tab
        """
        self.update_title(self.get_menu_title())
        self.name_list.update_defname()

    def name_callback(self):
        """
        Callback if changes happen in the name tab that impact the preferred
        name.
        """
        self.pname = self.obj.get_primary_name()

        self.ntype_field.reinit(self.pname.set_type, self.pname.get_type)

        self.prefix_suffix.reinit(
            [self.pname.set_surname_prefix, self.pname.set_suffix],
            [self.pname.get_surname_prefix, self.pname.get_suffix])

        self.call.reinit(
            self.pname.set_call_name, 
            self.pname.get_call_name)

        self.given.reinit(
            self.pname.set_first_name, 
            self.pname.get_first_name)

        self.patro_title.reinit(
            [self.pname.set_patronymic, self.pname.set_title], 
            [self.pname.get_patronymic, self.pname.get_title])
        
        self.surname_field.reinit(
            self.pname.set_surname, 
            self.pname.get_surname)

    def build_menu_names(self, person):
        """
        Provide the information needed by the base class to define the
        window management menu entries.
        """
        return (_('Edit Person'), self.get_menu_title())

    def _image_callback(self, ref, obj):
        """
        Called when a media reference had been edited. 
        
        This allows for the updating image on the main form which has just 
        been modified.
         
        """
        self.load_photo(Utils.media_path_full(self.dbstate.db, obj.get_path()),
                        ref.get_rectangle())

    def _image_button_press(self, obj, event):
        """
        Button press event that is caught when a button has been pressed while 
        on the image on the main form. 
        
        This does not apply to the images in galleries, just the image on the 
        main form.
        
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:

            media_list = self.obj.get_media_list()
            if media_list:                
                media_ref = media_list[0]
                object_handle = media_ref.get_reference_handle()
                media_obj = self.db.get_object_from_handle(object_handle)

                try:
                    EditMediaRef(self.dbstate, self.uistate, self.track, 
                                 media_obj, media_ref, self._image_callback)
                except Errors.WindowActiveError:
                    pass

        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            media_list = self.obj.get_media_list()
            if media_list:
                photo = media_list[0]
                self._show_popup(photo, event)
        #do not propagate further:
        return True

    def _show_popup(self, photo, event):
        """
        Look for right-clicks on a picture and create a popup menu of the 
        available actions.
        """
        
        menu = gtk.Menu()
        menu.set_title(_("Media Object"))
        obj = self.db.get_object_from_handle(photo.get_reference_handle())
        if obj:
            add_menuitem(menu, _("View"), photo, self._popup_view_photo)
        add_menuitem(menu, _("Edit Object Properties"), photo, 
                           self._popup_change_description)
        menu.popup(None, None, None, event.button, event.time)

    def _popup_view_photo(self, obj):
        """
        Open this picture in the default picture viewer.
        """
        media_list = self.obj.get_media_list()
        if media_list:
            photo = media_list[0]
            object_handle = photo.get_reference_handle()
            ref_obj = self.db.get_object_from_handle(object_handle)
            photo_path = Utils.media_path_full(self.db, ref_obj.get_path())
            open_file_with_default_application(photo_path)

    def _popup_change_description(self, obj):
        """
        Bring up the EditMediaRef dialog for the image on the main form.
        """
        media_list = self.obj.get_media_list()
        if media_list:
            media_ref = media_list[0]
            object_handle = media_ref.get_reference_handle()
            media_obj = self.db.get_object_from_handle(object_handle)
            EditMediaRef(self.dbstate, self.uistate, self.track, 
                         media_obj, media_ref, self._image_callback)
                        
    def _top_contextmenu(self):
        """
        Override from base class, the menuitems and actiongroups for the top 
        of context menu.
        """
        self.all_action    = gtk.ActionGroup("/PersonAll")
        self.home_action   = gtk.ActionGroup("/PersonHome")
        self.track_ref_for_deletion("all_action")
        self.track_ref_for_deletion("home_action")
        
        self.all_action.add_actions([
                ('ActivePerson', gtk.STOCK_APPLY, _("Make Active Person"), 
                    None, None, self._make_active),
                ])
        self.home_action.add_actions([
                ('HomePerson', gtk.STOCK_HOME, _("Make Home Person"), 
                    None, None, self._make_home_person),
                ])
                
        self.all_action.set_visible(True)
        self.home_action.set_visible(True)
        
        ui_top_cm = '''
            <menuitem action="ActivePerson"/>
            <menuitem action="HomePerson"/>'''
            
        return ui_top_cm, [self.all_action, self.home_action]
    
    def _post_build_popup_ui(self):
        """
        Override base class, make inactive home action if not needed.
        """
        if self.dbstate.db.get_default_person() and \
                self.obj.get_handle() == \
                            self.dbstate.db.get_default_person().get_handle():
            self.home_action.set_sensitive(False)
        else :
            self.home_action.set_sensitive(True)
            
    def _make_active(self, obj):
        self.dbstate.change_active_person(self.obj)
        
    def _make_home_person(self, obj):
        handle = self.obj.get_handle()
        if handle:
            self.dbstate.db.set_default_person_handle(handle)

    def _given_focus_out_event (self, entry, event):
        """
        Callback that occurs when the user leaves the given name field,
        allowing us to attempt to guess the gender of the person if
        so requested.
        """
        if not self.should_guess_gender:
            return False
        try:
            gender_type = self.db.genderStats.guess_gender(
                unicode(entry.get_text()))
            self.gender.force(gender_type)
        except:
            return False
        return False

    def load_photo(self, path, rectangle=None):
        """
        Load, scale and display the person's main photo from the path.
        """
        self.load_obj = path
        self.load_rect = rectangle
        if path is None:
            self.obj_photo.hide()
        else:
            try:
                i = gtk.gdk.pixbuf_new_from_file(path)
                width = i.get_width()
                height = i.get_height()

                if rectangle is not None:
                    upper_x = min(rectangle[0], rectangle[2])/100.
                    lower_x = max(rectangle[0], rectangle[2])/100.
                    upper_y = min(rectangle[1], rectangle[3])/100.
                    lower_y = max(rectangle[1], rectangle[3])/100.
                    sub_x = int(upper_x * width)
                    sub_y = int(upper_y * height)
                    sub_width = int((lower_x - upper_x) * width)
                    sub_height = int((lower_y - upper_y) * height)
                    if sub_width > 0 and sub_height > 0:
                        i = i.subpixbuf(sub_x, sub_y, sub_width, sub_height)

                ratio = float(max(i.get_height(), i.get_width()))
                scale = float(100.0)/ratio
                x = int(scale*(i.get_width()))
                y = int(scale*(i.get_height()))
                i = i.scale_simple(x, y, gtk.gdk.INTERP_BILINEAR)
                self.obj_photo.set_from_pixbuf(i)
                self.obj_photo.show()
            except:
                self.obj_photo.hide()

    def _check_for_unknown_gender(self):
        if self.obj.get_gender() == gen.lib.Person.UNKNOWN:
            d = GenderDialog(self.window)
            gender = d.run()
            d.destroy()
            if gender >= 0:
                self.obj.set_gender(gender)

    def _update_family_ids(self):
        # Update each of the families child lists to reflect any
        # change in ordering due to the new birth date
        family = self.obj.get_main_parents_family_handle()
        if (family):
            f = self.db.get_family_from_handle(family)
            new_order = self.reorder_child_ref_list(self.obj,
                                                f.get_child_ref_list())
            f.set_child_ref_list(new_order)
        for family in self.obj.get_parent_family_handle_list():
            f = self.db.get_family_from_handle(family)
            new_order = self.reorder_child_ref_list(self.obj,
                                                f.get_child_ref_list())
            f.set_child_ref_list(new_order)

        error = False
        original = self.db.get_person_from_handle(self.obj.handle)

        if original:
            (female, male, unknown) = _select_gender[self.obj.get_gender()]
            if male and original.get_gender() != gen.lib.Person.MALE:
                for tmp_handle in self.obj.get_family_handle_list():
                    temp_family = self.db.get_family_from_handle(tmp_handle)
                    if self.obj == temp_family.get_mother_handle():
                        if temp_family.get_father_handle() is not None:
                            error = True
                        else:
                            temp_family.set_mother_handle(None)
                            temp_family.set_father_handle(self.obj)
            elif female and original != gen.lib.Person.FEMALE:
                for tmp_handle in self.obj.get_family_handle_list():
                    temp_family = self.db.get_family_from_handle(tmp_handle)
                    if self.obj == temp_family.get_father_handle():
                        if temp_family.get_mother_handle() is not None:
                            error = True
                        else:
                            temp_family.set_father_handle(None)
                            temp_family.set_mother_handle(self.obj)
            elif unknown and original.get_gender() != gen.lib.Person.UNKNOWN:
                for tmp_handle in self.obj.get_family_handle_list():
                    temp_family = self.db.get_family_from_handle(tmp_handle)
                    if self.obj == temp_family.get_father_handle():
                        if temp_family.get_mother_handle() is not None:
                            error = True
                        else:
                            temp_family.set_father_handle(None)
                            temp_family.set_mother_handle(self.obj)
                    if self.obj == temp_family.get_mother_handle():
                        if temp_family.get_father_handle() is not None:
                            error = True
                        else:
                            temp_family.set_mother_handle(None)
                            temp_family.set_father_handle(self.obj)

            if error:
                msg2 = _("Problem changing the gender")
                msg = _("Changing the gender caused problems "
                        "with marriage information.\nPlease check "
                        "the person's marriages.")
                ErrorDialog(msg2, msg)

    def save(self, *obj):
        """
        Save the data.
        """
        self.ok_button.set_sensitive(False)
        if self.object_is_empty():
            ErrorDialog(_("Cannot save person"), 
                        _("No data exists for this person. Please "
                          "enter data or cancel the edit."))
            self.ok_button.set_sensitive(True)
            return
        
        (uses_dupe_id, id) = self._uses_duplicate_id()
        if uses_dupe_id:
            prim_object = self.get_from_gramps_id(id)
            name = self.name_displayer.display(prim_object)
            msg1 = _("Cannot save person. ID already exists.")
            msg2 = _("You have attempted to use the existing Gramps ID with "
                         "value %(id)s. This value is already used by '" 
                         "%(prim_object)s'. Please enter a different ID or leave "
                         "blank to get the next available ID value.") % {
                         'id' : id, 'prim_object' : name }
            ErrorDialog(msg1, msg2)
            self.ok_button.set_sensitive(True)
            return
        
        self._check_for_unknown_gender()

        set_birth_death_index(self.db, self.obj)

        trans = self.db.transaction_begin()

            
        self._update_family_ids()

        if not self.obj.get_handle():
            self.db.add_person(self.obj, trans)
            msg = _("Add Person (%s)") % self.name_displayer.display(self.obj)
        else:
            if not self.obj.get_gramps_id():
                self.obj.set_gramps_id(self.db.find_next_person_gramps_id())
            self.db.commit_person(self.obj, trans)
            msg = _("Edit Person (%s)") % self.name_displayer.display(self.obj)

        self.db.transaction_commit(trans, msg)
        self.close()
        if self.callback:
            self.callback(self.obj)

    def _edit_name_clicked(self, obj):
        """
        Bring up the EditName dialog for this name.
        
        Called when the edit name button is clicked for the primary name
        on the main form (not in the names tab).
         
        """
        EditName(self.dbstate, self.uistate, self.track, 
                 self.pname, self._update_name)

    def _update_name(self, name):
        """
        Called when the primary name has been changed by the EditName
        dialog. 
        
        This allows us to update the main form in response to any changes.
        
        """
        for obj in (self.prefix_suffix, self.patro_title, self.given,  
                    self.ntype_field, self.surname_field, self.call):
            obj.update()

    def load_person_image(self):
        """
        Load the primary image into the main form if it exists.
        
        Used as callback on Gallery Tab too.
        
        """
        media_list = self.obj.get_media_list()
        if media_list:
            photo = media_list[0]
            object_handle = photo.get_reference_handle()
            obj = self.db.get_object_from_handle(object_handle)
            full_path = Utils.media_path_full(self.dbstate.db, obj.get_path())
            #reload if different media, or different rectangle
            if self.load_obj != full_path or \
                    self.load_rect != photo.get_rectangle():
                mime_type = obj.get_mime_type()
                if mime_type and mime_type.startswith("image"):
                    self.load_photo(full_path, photo.get_rectangle())
                else:
                    self.load_photo(None)
        else:
            self.load_photo(None)

    def birth_dates_in_order(self, child_ref_list):
        """
        Check any *valid* birthdates in the list to insure that they are in
        numerically increasing order.
        """
        inorder = True
        prev_date = 0
        handle_list = [ref.ref for ref in child_ref_list]
        for i in range(len(handle_list)):
            child_handle = handle_list[i]
            child = self.db.get_person_from_handle(child_handle)
            if child.get_birth_ref():
                event_handle = child.get_birth_ref().ref
                event = self.db.get_event_from_handle(event_handle)
                child_date = event.get_date_object().get_sort_value()
            else:
                continue
            if (prev_date <= child_date):   # <= allows for twins
                prev_date = child_date
            else:
                inorder = False
        return inorder

    def reorder_child_ref_list(self, person, child_ref_list):
        """
        Reorder the child list to put the specified person in his/her
        correct birth order.  
        
        Only check *valid* birthdates.  Move the person as short a distance as 
        possible.
        
        """

        if self.birth_dates_in_order(child_ref_list):
            return(child_ref_list)

        # Build the person's date string once
        event_ref = person.get_birth_ref()
        if event_ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            person_bday = event.get_date_object().get_sort_value()
        else:
            person_bday = 0

        # First, see if the person needs to be moved forward in the list
        handle_list = [ref.ref for ref in child_ref_list]

        index = handle_list.index(person.get_handle())
        target = index
        for i in range(index-1, -1, -1):
            other = self.db.get_person_from_handle(handle_list[i])
            event_ref = other.get_birth_ref()
            if event_ref:
                event = self.db.get_event_from_handle(event_ref.ref)
                other_bday = event.get_date_object().get_sort_value()
                if other_bday == 0:
                    continue
                if person_bday < other_bday:
                    target = i
            else:
                continue

        # Now try moving to a later position in the list
        if (target == index):
            for i in range(index, len(handle_list)):
                other = self.db.get_person_from_handle(handle_list[i])
                event_ref = other.get_birth_ref()
                if event_ref:
                    event = self.db.get_event_from_handle(event_ref.ref)
                    other_bday = event.get_date_object().get_sort_value()
                    if other_bday == "99999999":
                        continue
                    if person_bday > other_bday:
                        target = i
                else:
                    continue

        # Actually need to move?  Do it now.
        if (target != index):
            ref = child_ref_list.pop(index)
            child_ref_list.insert(target, ref)
        return child_ref_list

    def _cleanup_on_exit(self):
        config.set('interface.prefix-suffix', self.prefix_suffix.active_key)
        config.set('interface.patro-title', self.patro_title.active_key)
        config.save()


class GenderDialog(gtk.MessageDialog):
    def __init__(self, parent=None):
        gtk.MessageDialog.__init__(self,
                                parent, 
                                flags=gtk.DIALOG_MODAL,
                                type=gtk.MESSAGE_QUESTION,
                                   )
        self.set_icon(ICON)
        self.set_title('')

        self.set_markup('<span size="larger" weight="bold">%s</span>' % 
                        _('Unknown gender specified'))
        self.format_secondary_text(
            _("The gender of the person is currently unknown. "
              "Usually, this is a mistake. Please specify the gender."))

        self.add_button(_('_Male'), gen.lib.Person.MALE)
        self.add_button(_('_Female'), gen.lib.Person.FEMALE)
        self.add_button(_('_Unknown'), gen.lib.Person.UNKNOWN)
