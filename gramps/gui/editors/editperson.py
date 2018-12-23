#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009-2011  Gary Burton
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
EditPerson Dialog. Provide the interface to allow the Gramps program
to edit information about a particular Person.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from copy import copy
import pickle

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.thumbnails import get_thumbnail_image
from ..utils import is_right_click, open_file_with_default_application
from gramps.gen.utils.db import get_birth_or_fallback
from gramps.gen.lib import NoteType, Person, Surname
from gramps.gen.db import DbTxn
from .. import widgets
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from ..glade import Glade
from ..ddtargets import DdTargets
from ..widgets.menuitem import add_menuitem

from .editprimary import EditPrimary
from .editmediaref import EditMediaRef
from .editname import EditName
from gramps.gen.config import config
from ..dialog import ErrorDialog, ICON
from gramps.gen.errors import ValidationError

from .displaytabs import (PersonEventEmbedList, NameEmbedList, CitationEmbedList,
                         AttrEmbedList, AddrEmbedList, NoteTab, GalleryTab,
                         WebEmbedList, PersonRefEmbedList, LdsEmbedList,
                         PersonBackRefList, SurnameTab)
from gramps.gen.plug import CATEGORY_QR_PERSON
from gramps.gen.const import URL_MANUAL_SECT1
from gramps.gen.utils.id import create_id

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT1

_select_gender = ((True, False, False),
                  (False, True, False),
                  (False, False, True))

class SingSurn:
    """
    Managing the single surname components
    """
    def __init__(self, gladeobj):
        self.top = gladeobj

    def hide_all(self):
        #self.top.get_object('prefixlabel').hide()
        self.top.get_object('prefix').hide()
        self.top.get_object('surnamelabel').hide()
        self.top.get_object('surname').hide()
        self.top.get_object('originlabel').hide()
        self.top.get_object('originlabel').hide()
        self.top.get_object('cmborigin').hide()
        self.top.get_object('multsurnamebtn').hide()

    def show_all(self):
        #self.top.get_object('prefixlabel').show()
        self.top.get_object('prefix').show()
        self.top.get_object('surnamelabel').show()
        self.top.get_object('surname').show()
        self.top.get_object('originlabel').show()
        self.top.get_object('originlabel').show()
        self.top.get_object('cmborigin').show()
        self.top.get_object('multsurnamebtn').show()

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
        person = Person()
        #the editor requires a surname
        person.primary_name.add_surname(Surname())
        person.primary_name.set_primary_surname(0)
        return person

    def get_menu_title(self):
        if self.obj and self.obj.get_handle():
            name = name_displayer.display(self.obj)
            title = _('Person: %(name)s') % {'name': name}
        else:
            name = name_displayer.display(self.obj)
            if name:
                title = _('New Person: %(name)s')  % {'name': name}
            else:
                title = _('New Person')
        return title

    def get_preview_name(self):
        prevname = name_displayer.display(self.obj)
        return prevname

    def _local_init(self):
        """
        Performs basic initialization, including setting up widgets and the
        glade interface.

        Local initialization function.
        This is called by the base class of EditPrimary, and overridden here.

        """
        self.pname = self.obj.get_primary_name()
        self.should_guess_gender = (not self.obj.get_gramps_id() and
                                    self.obj.get_gender () ==
                                    Person.UNKNOWN)

        self.added = self.obj.handle is None
        if self.added:
            self.obj.handle = create_id()

        self.top = Glade()

        self.set_window(self.top.toplevel, None,
                        self.get_menu_title())
        self.setup_configs('interface.person', 750, 550)

        self.obj_photo = self.top.get_object("personPix")
        self.frame_photo = self.top.get_object("frame5")
        self.eventbox = self.top.get_object("eventbox1")
        self.singsurnfr = SingSurn(self.top)
        self.multsurnfr = self.top.get_object("hboxmultsurnames")
        self.singlesurn_active = True

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
        self.given.grab_focus()
        self._changed_name(None)
        self.top.get_object("hboxmultsurnames").pack_start(self.surntab, True, True, 0)

        if len(self.obj.get_primary_name().get_surname_list()) > 1:
            self.multsurnfr.set_size_request(-1,
                                int(config.get('interface.surname-box-height')))
            self.singsurnfr.hide_all()
            self.multsurnfr.show_all()
            self.singlesurn_active = False
        else:
            self.multsurnfr.hide()
            self.singsurnfr.show_all()
            self.singlesurn_active = True
        #if self.pname.get_surname() and not self.pname.get_first_name():
        #    self.given.grab_focus()
        #else:
        #    self.surname_field.grab_focus()

    def _connect_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditPrimary).
        """
        self.define_cancel_button(self.top.get_object("button15"))
        self.define_ok_button(self.top.get_object("ok"), self.save)
        self.define_help_button(self.top.get_object("button134"),
                WIKI_HELP_PAGE,
                _('manual|Editing_information_about_people'))

        self.given.connect("focus-out-event", self._given_focus_out_event)
        self.top.get_object("editnamebtn").connect("clicked",
                                                 self._edit_name_clicked)
        self.top.get_object("multsurnamebtn").connect("clicked",
                                                 self._mult_surn_clicked)

        self.eventbox.connect('button-press-event',
                                self._image_button_press)
        # allow to initiate a drag-and-drop with this person if it has a handle
        if self.added:
            return  # Avoid HandleError if dragging an objet not in db yet
        tglist = Gtk.TargetList.new([])
        tglist.add(DdTargets.PERSON_LINK.atom_drag_type,
                   DdTargets.PERSON_LINK.target_flags,
                   DdTargets.PERSON_LINK.app_id)
        self.contexteventbox.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                   [],
                                   Gdk.DragAction.COPY)
        self.contexteventbox.drag_source_set_target_list(tglist)
        self.contexteventbox.drag_source_set_icon_name('gramps-person')
        self.contexteventbox.connect('drag_data_get', self._top_drag_data_get)

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
        if self.dbstate.db.has_person_handle(phandle):
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

    def _validate_call(self, widget, text):
        """ a callname must be a part of the given name, see if this is the
            case """
        validcall = self.given.obj.get_text().split()
        dummy = copy(validcall)
        for item in dummy:
            validcall += item.split('-')
        if text in validcall:
            return
        return ValidationError(_("Call name must be the given name that "
                                     "is normally used."))

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
            (_('female'), Person.FEMALE),
            (_('male'), Person.MALE),
            (_('unknown'), Person.UNKNOWN)
            ),
            self.db.readonly)

        self.ntype_field = widgets.MonitoredDataType(
            self.top.get_object("ntype"),
            self.pname.set_type,
            self.pname.get_type,
            self.db.readonly,
            self.db.get_name_types())

        #part of Given Name section
        self.given = widgets.MonitoredEntry(
            self.top.get_object("given_name"),
            self.pname.set_first_name,
            self.pname.get_first_name,
            self.db.readonly)

        self.call = widgets.MonitoredEntry(
            self.top.get_object("call"),
            self.pname.set_call_name,
            self.pname.get_call_name,
            self.db.readonly)
        self.call.connect("validate", self._validate_call)
        #force validation now with initial entry
        self.call.obj.validate(force=True)

        self.title = widgets.MonitoredEntry(
            self.top.get_object("title"),
            self.pname.set_title,
            self.pname.get_title,
            self.db.readonly)

        self.suffix = widgets.MonitoredEntryIndicator(
            self.top.get_object("suffix"),
            self.pname.set_suffix,
            self.pname.get_suffix,
            _('suffix'),
            self.db.readonly)

        self.nick = widgets.MonitoredEntry(
            self.top.get_object("nickname"),
            self.pname.set_nick_name,
            self.pname.get_nick_name,
            self.db.readonly)

        #part of Single Surname section
        self.surname_field = widgets.MonitoredEntry(
            self.top.get_object("surname"),
            self.pname.get_primary_surname().set_surname,
            self.pname.get_primary_surname().get_surname,
            self.db.readonly,
            autolist=self.db.get_surname_list() if not self.db.readonly else [])

        self.prefix = widgets.MonitoredEntryIndicator(
            self.top.get_object("prefix"),
            self.pname.get_primary_surname().set_prefix,
            self.pname.get_primary_surname().get_prefix,
            _('prefix'),
            self.db.readonly)

        self.ortype_field = widgets.MonitoredDataType(
            self.top.get_object("cmborigin"),
            self.pname.get_primary_surname().set_origintype,
            self.pname.get_primary_surname().get_origintype,
            self.db.readonly,
            self.db.get_origin_types())

        #other fields

        self.tags = widgets.MonitoredTagList(
            self.top.get_object("tag_label"),
            self.top.get_object("tag_button"),
            self.obj.set_tag_list,
            self.obj.get_tag_list,
            self.db,
            self.uistate, self.track,
            self.db.readonly)

        self.gid = widgets.MonitoredEntry(
            self.top.get_object("gid"),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

        #make sure title updates automatically
        for obj in [self.top.get_object("given_name"),
                    self.top.get_object("nickname"),
                    self.top.get_object("call"),
                    self.top.get_object("suffix"),
                    self.top.get_object("prefix"),
                    self.top.get_object("surname"),
                    ]:
            obj.connect('changed', self._changed_name)

        self.preview_name = self.top.get_object("full_name")
        self.preview_name.override_font(Pango.FontDescription('sans bold 12'))
        self.surntab = SurnameTab(self.dbstate, self.uistate, self.track,
                                  self.obj.get_primary_name(),
                                  on_change=self._changed_name)

    def get_start_date(self):
        """
        Get the start date for a person, usually a birth date, or
        something close to birth.
        """
        event = get_birth_or_fallback(self.dbstate.db, self.obj)
        return event.get_date_object() if event else None

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and insert them into the main window.
        """
        notebook = Gtk.Notebook()
        notebook.set_scrollable(True)

        self.event_list = PersonEventEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj,
            start_date=self.get_start_date())

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

        self.srcref_list = CitationEmbedList(self.dbstate,
                                           self.uistate,
                                           self.track,
                                           self.obj.get_citation_list(),
                                           self.get_menu_title())
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
                                notetype=NoteType.PERSON)
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
        self.top.get_object('vbox').pack_start(notebook, True, True, 0)

    def _changed_name(self, *obj):
        """
        callback to changes typed by user to the person name.
        Update the window title, and default name in name tab
        """
        self.update_title(self.get_menu_title())
        self.preview_name.set_text(self.get_preview_name())
        self.name_list.update_defname()

    def name_callback(self):
        """
        Callback if changes happen in the name tab that impact the preferred
        name.
        """
        self.pname = self.obj.get_primary_name()

        self.ntype_field.reinit(self.pname.set_type, self.pname.get_type)
        self.given.reinit(self.pname.set_first_name, self.pname.get_first_name)
        self.call.reinit(self.pname.set_call_name, self.pname.get_call_name)
        self.title.reinit(self.pname.set_title, self.pname.get_title)
        self.suffix.reinit(self.pname.set_suffix, self.pname.get_suffix)
        self.nick.reinit(self.pname.set_nick_name, self.pname.get_nick_name)
        #part of Single Surname section
        self.surname_field.reinit(
            self.pname.get_primary_surname().set_surname,
            self.pname.get_primary_surname().get_surname)

        self.prefix.reinit(
            self.pname.get_primary_surname().set_prefix,
            self.pname.get_primary_surname().get_prefix)

        self.ortype_field.reinit(
            self.pname.get_primary_surname().set_origintype,
            self.pname.get_primary_surname().get_origintype)

        self.__renewmultsurnames()

        if len(self.pname.get_surname_list()) == 1:
            self.singlesurn_active = True
        else:
            self.singlesurn_active = False
        if self.singlesurn_active:
            self.multsurnfr.hide()
            self.singsurnfr.show_all()
        else:
            self.singsurnfr.hide_all()
            self.multsurnfr.show_all()

    def build_menu_names(self, person):
        """
        Provide the information needed by the base class to define the
        window management menu entries.
        """
        return (_('Edit Person'), self.get_menu_title())

    def _image_button_press(self, obj, event):
        """
        Button press event that is caught when a button has been pressed while
        on the image on the main form.

        This does not apply to the images in galleries, just the image on the
        main form.

        """
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:

            media_list = self.obj.get_media_list()
            if media_list:
                media_ref = media_list[0]
                object_handle = media_ref.get_reference_handle()
                media_obj = self.db.get_media_from_handle(object_handle)

                try:
                    EditMediaRef(self.dbstate, self.uistate, self.track,
                                 media_obj, media_ref, self.load_photo)
                except WindowActiveError:
                    pass

        elif is_right_click(event):
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
        self.imgmenu = Gtk.Menu()
        menu = self.imgmenu
        menu.set_title(_("Media Object"))
        obj = self.db.get_media_from_handle(photo.get_reference_handle())
        if obj:
            add_menuitem(menu, _("View"), photo,
                                   self._popup_view_photo)
        add_menuitem(menu, _("Edit Object Properties"), photo,
                               self._popup_change_description)
        menu.popup(None, None, None, None, event.button, event.time)

    def _popup_view_photo(self, obj):
        """
        Open this picture in the default picture viewer.
        """
        media_list = self.obj.get_media_list()
        if media_list:
            photo = media_list[0]
            object_handle = photo.get_reference_handle()
            ref_obj = self.db.get_media_from_handle(object_handle)
            photo_path = media_path_full(self.db, ref_obj.get_path())
            open_file_with_default_application(photo_path, self.uistate)

    def _popup_change_description(self, obj):
        """
        Bring up the EditMediaRef dialog for the image on the main form.
        """
        media_list = self.obj.get_media_list()
        if media_list:
            media_ref = media_list[0]
            object_handle = media_ref.get_reference_handle()
            media_obj = self.db.get_media_from_handle(object_handle)
            EditMediaRef(self.dbstate, self.uistate, self.track,
                         media_obj, media_ref, self.load_photo)

    def _top_contextmenu(self, prefix):
        """
        Override from base class, the menuitems and actiongroups for the top
        of context menu.
        """
        if self.added:
            # Don't add items if not a real person yet
            return '', []

        _actions = [('ActivePerson', self._make_active),
                    ('HomePerson', self._make_home_person)]

        ui_top_cm = (
            '''
        <item>
          <attribute name="action">{prefix}.ActivePerson</attribute>
          <attribute name="label" translatable="yes">Make Active Person'''
            '''</attribute>
        </item>
        <item>
          <attribute name="action">{prefix}.HomePerson</attribute>
          <attribute name="label" translatable="yes">Make Home Person'''
            '''</attribute>
        </item>
        '''.format(prefix=prefix))

        return ui_top_cm, _actions

    def _top_drag_data_get(self, widget, context, sel_data, info, time):
        if info == DdTargets.PERSON_LINK.app_id:
            data = (DdTargets.PERSON_LINK.drag_type, id(self), self.obj.get_handle(), 0)
            sel_data.set(DdTargets.PERSON_LINK.atom_drag_type, 8, pickle.dumps(data))

    def _post_build_popup_ui(self):
        """
        Override base class, make inactive home action if not needed.
        """
        if self.added:
            return
        home_action = self.uistate.uimanager.get_action(self.action_group,
                                                        'HomePerson')
        if (self.dbstate.db.get_default_person() and
                self.obj.get_handle() ==
                    self.dbstate.db.get_default_person().get_handle()):
            home_action.set_enabled(False)
        else:
            home_action.set_enabled(True)

    def _make_active(self, obj, value):
        self.uistate.set_active(self.obj.get_handle(), 'Person')

    def _make_home_person(self, obj, value):
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
                                                    str(entry.get_text()))
            self.gender.force(gender_type)
        except:
            return False
        return False

    def _check_for_unknown_gender(self):
        if self.obj.get_gender() == Person.UNKNOWN:
            d = GenderDialog(parent=self.window)
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
        if self.original:
            (female, male, unknown) = _select_gender[self.obj.get_gender()]
            if male and self.original.get_gender() != Person.MALE:
                for tmp_handle in self.obj.get_family_handle_list():
                    temp_family = self.db.get_family_from_handle(tmp_handle)
                    if self.obj == temp_family.get_mother_handle():
                        if temp_family.get_father_handle() is not None:
                            error = True
                        else:
                            temp_family.set_mother_handle(None)
                            temp_family.set_father_handle(self.obj)
            elif female and self.original != Person.FEMALE:
                for tmp_handle in self.obj.get_family_handle_list():
                    temp_family = self.db.get_family_from_handle(tmp_handle)
                    if self.obj == temp_family.get_father_handle():
                        if temp_family.get_mother_handle() is not None:
                            error = True
                        else:
                            temp_family.set_father_handle(None)
                            temp_family.set_mother_handle(self.obj)
            elif unknown and self.original.get_gender() != Person.UNKNOWN:
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
                ErrorDialog(msg2, msg, parent=self.window)

    def save(self, *obj):
        """
        Save the data.
        """
        self.ok_button.set_sensitive(False)
        if self.object_is_empty():
            ErrorDialog(_("Cannot save person"),
                        _("No data exists for this person. Please "
                          "enter data or cancel the edit."),
                        parent=self.window)
            self.ok_button.set_sensitive(True)
            return
        # fix surname problems
        for name in [self.obj.get_primary_name()] + self.obj.get_alternate_names():
            if len(name.get_surname_list()) > 1:
                newlist = [surn for surn in name.get_surname_list() if not surn.is_empty()]
                if len(newlist) != len(name.get_surname_list()):
                    name.set_surname_list(newlist)
            if len(name.get_surname_list()) == 0:
                name.set_surname_list([Surname()])
            try:
                primind = [surn.get_primary() for surn in name.get_surname_list()].index(True)
            except ValueError:
                primind = 0 # no match
            name.set_primary_surname(primind)

        # fix ide problems
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
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        self._check_for_unknown_gender()

        self.db.set_birth_death_index(self.obj)

        if not self.obj.handle:
            with DbTxn(_("Add Person (%s)") % \
                        self.name_displayer.display(self.obj),
                       self.db) as trans:
                self.db.add_person(self.obj, trans)
        else:
            if self.data_has_changed():
                with DbTxn(_("Edit Person (%s)") % \
                            self.name_displayer.display(self.obj),
                           self.db) as trans:
                    if not self.obj.get_gramps_id():
                        self.obj.set_gramps_id(self.db.find_next_person_gramps_id())
                    self.db.commit_person(self.obj, trans)

        self._do_close()
        if self.callback:
            self.callback(self.obj)
        self.callback = None

    def _edit_name_clicked(self, obj):
        """
        Bring up the EditName dialog for this name.

        Called when the edit name button is clicked for the primary name
        on the main form (not in the names tab).

        """
        try:
            EditName(self.dbstate, self.uistate, self.track,
                 self.pname, self._update_name)
        except WindowActiveError:
            pass

    def _mult_surn_clicked(self, obj):
        """
        Show the list entry of multiple surnames
        """
        self.singsurnfr.hide_all()
        self.singlesurn_active = False
        #update multsurnfr for possible changes
        self.__renewmultsurnames()
        self.multsurnfr.show_all()

    def _update_name(self, name):
        """
        Called when the primary name has been changed by the EditName
        dialog.

        This allows us to update the main form in response to any changes.

        """
        for obj in (self.ntype_field, self.given, self.call, self.title,
                    self.suffix, self.nick, self.surname_field, self.prefix,
                    self.ortype_field):
            obj.update()

        self.__renewmultsurnames()

        if len(self.obj.get_primary_name().get_surname_list()) == 1:
            self.singlesurn_active = True
        else:
            self.singlesurn_active = False
        if self.singlesurn_active:
            self.multsurnfr.hide()
            self.singsurnfr.show_all()

        else:
            self.singsurnfr.hide_all()
            self.multsurnfr.show_all()

    def __renewmultsurnames(self):
        """Update mult surnames section with what is presently the
           correct surname.
           It is easier to recreate the entire mult surnames GUI than
           changing what has changed visually.
        """
        #remove present surname tab, and put new one
        msurhbox = self.top.get_object("hboxmultsurnames")
        msurhbox.remove(self.surntab)
        self.surntab = SurnameTab(self.dbstate, self.uistate, self.track,
                                  self.obj.get_primary_name(),
                                  on_change=self._changed_name)
        self.multsurnfr.set_size_request(-1,
                                int(config.get('interface.surname-box-height')))
        msurhbox.pack_start(self.surntab, True, True, 0)

    def load_person_image(self):
        """
        Load the primary image into the main form if it exists.

        Used as callback on Gallery Tab too.

        """
        media_list = self.obj.get_media_list()
        if media_list:
            ref = media_list[0]
            handle = ref.get_reference_handle()
            obj = self.dbstate.db.get_media_from_handle(handle)
            if obj is None :
                #notify user of error
                from ..dialog import RunDatabaseRepair
                RunDatabaseRepair(
                    _('Non existing media found in the Gallery'),
                    parent=self.window)
            else :
                self.load_photo(ref, obj)
        else:
            self.obj_photo.hide()
            self.frame_photo.hide()

    def load_photo(self, ref, obj):
        """
        Load the person's main photo using the Thumbnailer.
        """
        pixbuf = get_thumbnail_image(
                        media_path_full(self.dbstate.db,
                                              obj.get_path()),
                        obj.get_mime_type(),
                        ref.get_rectangle())

        self.obj_photo.set_from_pixbuf(pixbuf)
        self.obj_photo.show()
        self.frame_photo.show_all()

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
        """Unset all things that can block garbage collection.
        Finalize rest
        """
##        self.private.destroy()
##        self.gender.destroy()
##        self.ntype_field.destroy()
##        self.given.destroy()
##        self.call.destroy()
##        self.title.destroy()
##        self.suffix.destroy()
##        self.nick.destroy()
##        self.surname_field.destroy()
##        self.prefix.destroy()
##        self.ortype_field.destroy()
##        self.tags.destroy()
##        self.gid.destroy()
        EditPrimary._cleanup_on_exit(self)
        #config.save()


class GenderDialog(Gtk.MessageDialog):
    def __init__(self, parent=None):
        Gtk.MessageDialog.__init__(self,
                                parent,
                                flags=Gtk.DialogFlags.MODAL,
                                type=Gtk.MessageType.QUESTION,
                                   )
        self.set_icon(ICON)
        self.set_title('')

        self.set_markup('<span size="larger" weight="bold">%s</span>' %
                        _('Unknown gender specified'))
        self.format_secondary_text(
            _("The gender of the person is currently unknown. "
              "Usually, this is a mistake. Please specify the gender."))

        self.add_button(_('_Male'), Person.MALE)
        self.add_button(_('_Female'), Person.FEMALE)
        self.add_button(_('_Unknown'), Person.UNKNOWN)
