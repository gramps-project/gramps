#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import pickle

#-------------------------------------------------------------------------
#
# enable logging for error handling
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from ..ddtargets import DdTargets
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import GLib

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.config import config
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.lib import ChildRef, Family, Name, NoteType, Person, Surname
from gramps.gen.db import DbTxn
from gramps.gen.errors import WindowActiveError
from gramps.gen.datehandler import displayer
from ..glade import Glade

from .editprimary import EditPrimary
from .editchildref import EditChildRef
from .editperson import EditPerson
from .displaytabs import (EmbeddedList, EventEmbedList, CitationEmbedList,
                         FamilyAttrEmbedList, NoteTab, GalleryTab,
                         FamilyLdsEmbedList, ChildModel,
                         TEXT_COL, MARKUP_COL, ICON_COL)
from ..widgets import (PrivacyButton, MonitoredEntry, MonitoredDataType,
                         MonitoredTagList)
from gramps.gen.plug import CATEGORY_QR_FAMILY
from ..dialog import (ErrorDialog, RunDatabaseRepair, WarningDialog,
                            MessageHideDialog)
from gramps.gen.utils.db import (get_birth_or_fallback, get_death_or_fallback,
                          get_marriage_or_fallback, preset_name, family_name)
from ..selectors import SelectorFactory
from gramps.gen.utils.id import create_id
from gramps.gen.const import URL_MANUAL_SECT1

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT1
WIKI_HELP_SEC = _('manual|Family_Editor_dialog')

SelectPerson = SelectorFactory('Person')

_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3

class ChildEmbedList(EmbeddedList):
    """
    The child embed list is specific to the Edit Family dialog, so it
    is contained here instead of in displaytabs.
    """

    _HANDLE_COL = 14
    _DND_TYPE = DdTargets.CHILDREF
    _DND_EXTRA = DdTargets.PERSON_LINK

    _MSG = {
        'add'   : _('Create a new person and add the child to the family'),
        'del'   : _('Remove the child from the family'),
        'edit'  : _('Edit the child reference'),
        'share' : _('Add an existing person as a child of the family'),
        'up'    : _('Move the child up in the children list'),
        'down'  : _('Move the child down in the children list'),
        }

    # (name, column in model, width, markup/text, font weight)
    _column_names = [
        (_('#'), 0, 25, TEXT_COL, -1, None),
        (_('ID'), 1, 60, TEXT_COL, -1, None),
        (_('Name'), 10, 250, TEXT_COL, -1, None),
        (_('Gender'), 3, 75, TEXT_COL, -1, None),
        (_('Paternal'), 4, 100, TEXT_COL, -1, None),
        (_('Maternal'), 5, 100, TEXT_COL, -1, None),
        (_('Birth Date'), 11, 150, MARKUP_COL, -1, None),
        (_('Death Date'), 12, 150, MARKUP_COL, -1, None),
        (_('Birth Place'), 8, 150, TEXT_COL, -1, None),
        (_('Death Place'), 9, 150, TEXT_COL, -1, None),
        None,
        None,
        None,
        (_('Private'), 13,  30, ICON_COL, -1, 'gramps-lock')
        ]

    def __init__(self, dbstate, uistate, track, family):
        """
        Create the object, storing the passed family value
        """
        self.family = family
        EmbeddedList.__init__(self, dbstate, uistate, track, _('Chil_dren'),
                              ChildModel, share_button=True, move_buttons=True)

    def get_popup_menu_items(self):
        return [
            (False, _('Edit child'), self.edit_child_button_clicked),
            (True, _('_Add'), self.add_button_clicked),
            (True, _('Add an existing child'), self.share_button_clicked),
            (False, _('Edit relationship'), self.edit_button_clicked),
            (True, _('_Remove'), self.del_button_clicked),
            ]

    def get_middle_click(self):
        return self.edit_child_button_clicked


    def get_icon_name(self):
        return 'gramps-family'

    def get_data(self):
        """
        Normally, get_data returns a list. However, we return family
        object here instead.
        """
        return self.family.get_child_ref_list()

    def column_order(self):
        return [(1, 13), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
                (0, 8), (0, 9)]

    def add_button_clicked(self, obj=None):
        person = Person()
        autoname = config.get('behavior.surname-guessing')
        #_("Father's surname"),
        #_("None"),
        #_("Combination of mother's and father's surname"),
        #_("Icelandic style"),
        if autoname == 0:
            name = self.north_american()
        elif autoname == 2:
            name = self.latin_american()
        else:
            name = self.no_name()
        person.set_primary_name(name)

        EditPerson(self.dbstate, self.uistate, self.track, person,
                   self.new_child_added)

    def handle_extra_type(self, objtype, obj):
        """
        Called when a person is dropped onto the list.  objtype will be
        'person-link' and obj will contain a person handle.
        """
        person = self.dbstate.db.get_person_from_handle(obj)
        self.new_child_added(person)

    def new_child_added(self, person):
        ref = ChildRef()
        ref.ref = person.get_handle()
        self.family.add_child_ref(ref)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell,
                         len(self.family.get_child_ref_list()) - 1)
        self.call_edit_childref(ref)

    def child_ref_edited(self, person):
        self.rebuild()

    def share_button_clicked(self, obj=None):
        # it only makes sense to skip those who are already in the family
        skip_list = [self.family.get_father_handle(),
                     self.family.get_mother_handle()]
        skip_list.extend(x.ref for x in self.family.get_child_ref_list())

        sel = SelectPerson(self.dbstate, self.uistate, self.track,
                           _("Select Child"), skip=skip_list)
        person = sel.run()

        if person:
            ref = ChildRef()
            ref.ref = person.get_handle()
            self.family.add_child_ref(ref)
            self.rebuild()
            GLib.idle_add(self.tree.scroll_to_cell,
                             len(self.family.get_child_ref_list()) - 1)
            self.call_edit_childref(ref)

    def run(self, skip):
        skip_list = [_f for _f in skip if _f]
        SelectPerson(self.dbstate, self.uistate, self.track,
                     _("Select Child"), skip=skip_list)

    def del_button_clicked(self, obj=None):
        ref = self.get_selected()
        if ref:
            self.family.remove_child_ref(ref)
            self.rebuild()

    def edit_button_clicked(self, obj=None):
        ref = self.get_selected()
        if ref:
            self.call_edit_childref(ref)

    def call_edit_childref(self, ref):
        p = self.dbstate.db.get_person_from_handle(ref.ref)
        n = name_displayer.display(p)
        try:
            EditChildRef(n, self.dbstate, self.uistate, self.track,
                         ref, self.child_ref_edited)
        except WindowActiveError:
            pass

    def edit_child_button_clicked(self, obj=None):
        ref = self.get_selected()
        if ref:
            p = self.dbstate.db.get_person_from_handle(ref.ref)
            try:
                EditPerson(self.dbstate, self.uistate, self.track,
                       p, self.child_ref_edited)
            except WindowActiveError:
                pass

    def north_american(self):
        """
        Child inherits name from father
        """
        name = Name()
        #the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        father_handle = self.family.get_father_handle()
        if father_handle:
            father = self.dbstate.db.get_person_from_handle(father_handle)
            preset_name(father, name)
        return name

    def no_name(self):
        name = Name()
        #the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        return name

    def latin_american(self):
        """
        Child inherits name from father and mother
        """
        name = Name()
        #the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        if self.family:
            father_handle = self.family.get_father_handle()
            mother_handle = self.family.get_mother_handle()
            father = self.dbstate.db.get_person_from_handle(father_handle)
            mother = self.dbstate.db.get_person_from_handle(mother_handle)
            if not father and not mother:
                return name
            if not father:
                preset_name(mother, name)
                return name
            if not mother:
                preset_name(father, name)
                return name
            #we take first surname, and keep that
            mothername = Name()
            preset_name(mother, mothername)
            preset_name(father, name)
            mothersurname = mothername.get_surname_list()[0]
            mothersurname.set_primary(False)
            name.set_surname_list([name.get_surname_list()[0], mothersurname])
            return name
        else:
            return name

class FastMaleFilter:

    def __init__(self, db):
        self.db = db

    def match(self, handle, db):
        value = self.db.get_raw_person_data(handle)
        return value[2] == Person.MALE

class FastFemaleFilter:

    def __init__(self, db):
        self.db = db

    def match(self, handle, db):
        value = self.db.get_raw_person_data(handle)
        return value[2] == Person.FEMALE

#-------------------------------------------------------------------------
#
# EditFamily
#
#-------------------------------------------------------------------------
class EditFamily(EditPrimary):

    QR_CATEGORY = CATEGORY_QR_FAMILY

    def __init__(self, dbstate, uistate, track, family, callback=None):

        EditPrimary.__init__(self, dbstate, uistate, track,
                             family, dbstate.db.get_family_from_handle,
                             dbstate.db.get_family_from_gramps_id,
                             callback)

        # look for the scenerio of a child and no parents on a new
        # family

        if (self.added and
          not self.obj.get_father_handle() and
          not self.obj.get_mother_handle() and
          len(self.obj.get_child_ref_list()) == 1):

            self.add_parent = True
            if not config.get('preferences.family-warn'):
                for i in self.hidden:
                    i.set_sensitive(False)

                MessageHideDialog(
                    _("Adding parents to a person"),
                    _("It is possible to accidentally create multiple "
                      "families with the same parents. To help avoid "
                      "this problem, only the buttons to select parents "
                      "are available when you create a new family. The "
                      "remaining fields will become available after you "
                      "attempt to select a parent."),
                    'preferences.family-warn',
                    parent=self.window)
        else:
            self.add_parent = False

    def _cleanup_on_exit(self):
        """Unset all things that can block garbage collection.
        Finalize rest
        """
        #FIXME, we rebind show_all below, this prevents garbage collection of
        #  the dialog, fix the rebind
        self.window.show_all = None
        EditPrimary._cleanup_on_exit(self)

    def empty_object(self):
        return Family()

    def _local_init(self):
        self.added = self.obj.handle is None
        if self.added:
            self.obj.handle = create_id()

        self.build_interface()
        self.load_data()

    def _connect_db_signals(self):
        """
        implement from base class DbGUIElement
        Register the callbacks we need.
        Note:
            * we do not connect to person-delete, as a delete of a person in
                the family outside of this editor will cause a family-update
                signal of this family
        """
        self.callman.register_handles({'family': [self.obj.get_handle()]})
        self.callman.register_callbacks(
           {'family-update': self.check_for_family_change,
            'family-delete': self.check_for_close,
            'family-rebuild': self._do_close,
            'event-update': self.topdata_updated,  # change eg birth event fath
            'event-rebuild': self.topdata_updated,
            'event-delete': self.topdata_updated,  # delete eg birth event fath
            'person-update': self.topdata_updated, # change eg name of father
            'person-rebuild': self._do_close,
           })
        self.callman.connect_all(keys=['family', 'event', 'person'])

    def check_for_family_change(self, handles):
        """
        Callback for family-update signal
        1. This method checks to see if the family shown has been changed. This
            is possible eg in the relationship view. If the family was changed,
            the view is refreshed and a warning dialog shown to indicate all
            changes have been lost.
            If a source/note/event is deleted, this method is called too. This
            is unfortunate as the displaytabs can track themself a delete and
            correct the view for this. Therefore, these tabs are not rebuild.
            Conclusion: this method updates so that remove/change of parent or
            remove/change of children in relationship view reloads the family
            from db.
        2. Changes in other families are of no consequence to the family shown
        """
        if self.obj.get_handle() in handles:
            #rebuild data
            ## Todo: Gallery and note tab are not rebuild ??
            objreal = self.dbstate.db.get_family_from_handle(
                                                        self.obj.get_handle())
            #update selection of data that we obtain from database change:
            maindatachanged = (self.obj.gramps_id != objreal.gramps_id or
                self.obj.father_handle != objreal.father_handle or
                self.obj.mother_handle != objreal.mother_handle or
                self.obj.private != objreal.private or
                self.obj.type != objreal.type or
                self.obj.get_tag_list() != objreal.get_tag_list() or
                self.obj.child_ref_list != objreal.child_ref_list)
            if maindatachanged:
                self.obj.gramps_id = objreal.gramps_id
                self.obj.father_handle = objreal.father_handle
                self.obj.mother_handle = objreal.mother_handle
                self.obj.private = objreal.private
                self.obj.type = objreal.type
                self.obj.set_tag_list(objreal.get_tag_list())
                self.obj.child_ref_list = objreal.child_ref_list
                self.reload_people()

            # No matter why the family changed (eg delete of a source), we notify
            # the user
            WarningDialog(
            _("Family has changed"),
            _("The %(object)s you are editing has changed outside this editor."
              " This can be due to a change in one of the main views, for "
              "example a source used here is deleted in the source view.\n"
              "To make sure the information shown is still correct, the "
              "data shown has been updated. Some edits you have made may have"
              " been lost.") % {'object': _('family')},
            parent=self.window)

    def topdata_updated(self, *obj):
        """
        Callback method called if data shown in top part of family editor
        (a parent, birth/death event of parent) changes
        Note: person events shown in the event list are not tracked, the
              tabpage itself tracks it
        """
        self.load_data()

    def show_buttons(self):
        """
        Used to reshow hidden/showing buttons.
        """
        fhandle = self.obj.get_father_handle()
        self.update_father(fhandle)
        mhandle = self.obj.get_mother_handle()
        self.update_mother(mhandle)

    def reload_people(self):
        fhandle = self.obj.get_father_handle()
        self.update_father(fhandle)

        mhandle = self.obj.get_mother_handle()
        self.update_mother(mhandle)
        self.child_tab.rebuild()

    def get_menu_title(self):
        if self.obj and self.obj.get_handle():
            dialog_title = family_name(self.obj, self.db, _("New Family"))
            dialog_title = _("Family") + ': ' + dialog_title
        else:
            dialog_title = _("New Family")
        return dialog_title

    def build_menu_names(self, family):
        return (_('Edit Family'), self.get_menu_title())

    def build_interface(self):
        self.top = Glade()
        self.set_window(self.top.toplevel, None, self.get_menu_title())
        self.setup_configs('interface.family', 700, 500)

        # HACK: how to prevent hidden items from showing
        #       when you use show_all?
        # Consider using show() rather than show_all()?
        # FIXME: remove if we can use show()
        self.window.show_all = self.window.show

        self.fbirth  = self.top.get_object('fbirth')
        self.fdeath  = self.top.get_object('fdeath')
        self.fbirth_label = self.top.get_object('label578')
        self.fdeath_label = self.top.get_object('label579')

        self.mbirth  = self.top.get_object('mbirth')
        self.mdeath  = self.top.get_object('mdeath')
        self.mbirth_label = self.top.get_object('label567')
        self.mdeath_label = self.top.get_object('label568')

        self.mname    = self.top.get_object('mname')
        self.fname    = self.top.get_object('fname')

        self.mbutton_index = self.top.get_object('mbutton_index')
        self.mbutton_add = self.top.get_object('mbutton_add')
        self.mbutton_del = self.top.get_object('mbutton_del')
        self.mbutton_edit = self.top.get_object('mbutton_edit')

        self.mbutton_index.set_tooltip_text(_("Select a person as the mother"))
        self.mbutton_add.set_tooltip_text(_("Add a new person as the mother"))
        self.mbutton_del.set_tooltip_text(_("Remove the person as the mother"))

        self.mbutton_edit.connect('button-press-event', self.edit_mother)
        self.mbutton_edit.connect('key-press-event', self.edit_mother)
        self.mbutton_index.connect('clicked', self.sel_mother_clicked)
        self.mbutton_del.connect('clicked', self.del_mother_clicked)
        self.mbutton_add.connect('clicked', self.add_mother_clicked)

        self.fbutton_index = self.top.get_object('fbutton_index')
        self.fbutton_add = self.top.get_object('fbutton_add')
        self.fbutton_del = self.top.get_object('fbutton_del')
        self.fbutton_edit = self.top.get_object('fbutton_edit')

        self.fbutton_index.set_tooltip_text(_("Select a person as the father"))
        self.fbutton_add.set_tooltip_text(_("Add a new person as the father"))
        self.fbutton_del.set_tooltip_text(_("Remove the person as the father"))

        self.fbutton_edit.connect('button-press-event', self.edit_father)
        self.fbutton_edit.connect('key-press-event', self.edit_father)
        self.fbutton_index.connect('clicked', self.sel_father_clicked)
        self.fbutton_del.connect('clicked', self.del_father_clicked)
        self.fbutton_add.connect('clicked', self.add_father_clicked)

        if self.added:
            return      # avoids crash on drag because not in db yet
        #allow for a context menu
        self.set_contexteventbox(self.top.get_object("eventboxtop"))
        #allow for drag of the family object from eventboxtop
        self.contexteventbox.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                   [], Gdk.DragAction.COPY)
        tglist = Gtk.TargetList.new([])
        tglist.add(DdTargets.FAMILY_LINK.atom_drag_type,
                   DdTargets.FAMILY_LINK.target_flags,
                   DdTargets.FAMILY_LINK.app_id)
        self.contexteventbox.drag_source_set_target_list(tglist)
        self.contexteventbox.drag_source_set_icon_name('gramps-family')
        self.contexteventbox.connect('drag_data_get', self.on_drag_data_get_family)

    def on_drag_data_get_family(self,widget, context, sel_data, info, time):
        if info == DdTargets.FAMILY_LINK.app_id:
            data = (DdTargets.FAMILY_LINK.drag_type, id(self), self.obj.get_handle(), 0)
            sel_data.set(DdTargets.FAMILY_LINK.atom_drag_type, 8, pickle.dumps(data))

    def _update_parent_dnd_handler(self, event_box, parent_handle, on_drag_data_get, on_drag_data_received):
        """
        Set the drag action from the label of father when he exists
        """
        if parent_handle:
            # Allow drag
            if not event_box.drag_source_get_target_list():
                event_box.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                           [],
                                           Gdk.DragAction.COPY)
                tglist = Gtk.TargetList.new([])
                tglist.add(DdTargets.PERSON_LINK.atom_drag_type,
                           DdTargets.PERSON_LINK.target_flags,
                           DdTargets.PERSON_LINK.app_id)
                event_box.drag_source_set_target_list(tglist)
                event_box.drag_source_set_icon_name('gramps-person')
                event_box.connect('drag_data_get', on_drag_data_get)
            #Disallow drop:
            if event_box.drag_dest_get_target_list():
                event_box.drag_dest_unset()
        else:
            # Disallow drag
            if event_box.drag_source_get_target_list():
                event_box.drag_source_unset()
            #allow for drop:
            if not event_box.drag_dest_get_target_list():
                event_box.drag_dest_set(Gtk.DestDefaults.MOTION |
                                    Gtk.DestDefaults.DROP,
                                    [],
                                    Gdk.DragAction.COPY)
                tglist = Gtk.TargetList.new([])
                tglist.add(DdTargets.PERSON_LINK.atom_drag_type,
                           DdTargets.PERSON_LINK.target_flags,
                           DdTargets.PERSON_LINK.app_id)
                event_box.drag_dest_set_target_list(tglist)
                event_box.connect('drag_data_received', on_drag_data_received)

    def on_drag_fatherdata_get(self, widget, context, sel_data, info, time):
        if info == DdTargets.PERSON_LINK.app_id:
            data = (DdTargets.PERSON_LINK.drag_type, id(self), self.obj.get_father_handle(), 0)
            sel_data.set(DdTargets.PERSON_LINK.atom_drag_type, 8, pickle.dumps(data))

    def on_drag_motherdata_get(self, widget, context, sel_data, info, time):
        if info == DdTargets.PERSON_LINK.app_id:
            data = (DdTargets.PERSON_LINK.drag_type, id(self), self.obj.get_mother_handle(), 0)
            sel_data.set(DdTargets.PERSON_LINK.atom_drag_type, 8, pickle.dumps(data))

    def _connect_signals(self):
        self.define_ok_button(self.top.get_object('ok'), self.save)
        self.define_cancel_button(self.top.get_object('cancel'))
        # TODO help button (rename glade button name)
        self.define_help_button(self.top.get_object('button119'),
                WIKI_HELP_PAGE, WIKI_HELP_SEC)

    def _can_be_replaced(self):
        pass

    def _setup_fields(self):

        self.private = PrivacyButton(
            self.top.get_object('private'),
            self.obj,
            self.db.readonly)

        self.gid = MonitoredEntry(
            self.top.get_object('gid'),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

        self.tags = MonitoredTagList(
            self.top.get_object("tag_label"),
            self.top.get_object("tag_button"),
            self.obj.set_tag_list,
            self.obj.get_tag_list,
            self.db,
            self.uistate, self.track,
            self.db.readonly)

        self.data_type = MonitoredDataType(
            self.top.get_object('marriage_type'),
            self.obj.set_relationship,
            self.obj.get_relationship,
            self.db.readonly,
            self.db.get_family_relation_types(),
            )

    def load_data(self):
        """
        Show top data of family editor: father and mother info
        and set self.phandles with all person handles in the family
        """
        fhandle = self.obj.get_father_handle()
        self.update_father(fhandle)

        mhandle = self.obj.get_mother_handle()
        self.update_mother(mhandle)

        self.phandles = [mhandle, fhandle]
        self.phandles.extend(x.ref for x in self.obj.get_child_ref_list())

        self.phandles = [_f for _f in self.phandles if _f]

    def get_start_date(self):
        """
        Get the start date for a family, usually a marriage date, or
        something close to marriage.
        """
        event = get_marriage_or_fallback(self.dbstate.db, self.obj)
        return event.get_date_object() if event else None

    def _create_tabbed_pages(self):

        notebook = Gtk.Notebook()

        self.child_list = ChildEmbedList(self.dbstate,
                                         self.uistate,
                                         self.track,
                                         self.obj)
        self.child_tab = self._add_tab(notebook, self.child_list)
        self.track_ref_for_deletion("child_list")
        self.track_ref_for_deletion("child_tab")

        self.event_list = EventEmbedList(self.dbstate,
                                         self.uistate,
                                         self.track,
                                         self.obj,
                                         start_date=self.get_start_date())

        self._add_tab(notebook, self.event_list)
        self.track_ref_for_deletion("event_list")

        self.citation_list = CitationEmbedList(self.dbstate,
                                           self.uistate,
                                           self.track,
                                           self.obj.get_citation_list(),
                                           self.get_menu_title())
        self._add_tab(notebook, self.citation_list)
        self.track_ref_for_deletion("citation_list")

        self.attr_list = FamilyAttrEmbedList(self.dbstate,
                                              self.uistate,
                                              self.track,
                                              self.obj.get_attribute_list())
        self._add_tab(notebook, self.attr_list)
        self.track_ref_for_deletion("attr_list")

        self.note_tab = NoteTab(self.dbstate,
                                self.uistate,
                                self.track,
                                self.obj.get_note_list(),
                                self.get_menu_title(),
                                notetype=NoteType.FAMILY)
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self.gallery_tab = GalleryTab(self.dbstate,
                                      self.uistate,
                                      self.track,
                                      self.obj.get_media_list())
        self._add_tab(notebook, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")

        self.lds_embed = FamilyLdsEmbedList(self.dbstate,
                                            self.uistate,
                                            self.track,
                                            self.obj.get_lds_ord_list())
        self._add_tab(notebook, self.lds_embed)
        self.track_ref_for_deletion("lds_embed")

        self._setup_notebook_tabs( notebook)
        notebook.show_all()

        self.hidden = (notebook, self.top.get_object('info'))
        self.top.get_object('vbox').pack_start(notebook, True, True, 0)

    def update_father(self, handle):
        self.load_parent(handle, self.fname, self.fbirth, self.fbirth_label,
                         self.fdeath, self.fdeath_label,
                         self.fbutton_index, self.fbutton_add,
                         self.fbutton_del, self.fbutton_edit)
        self._update_parent_dnd_handler(self.top.get_object('ftable_event_box'),
                                        self.obj.get_father_handle(),
                                        self.on_drag_fatherdata_get,
                                        self.on_drag_fatherdata_received)

    def update_mother(self, handle):
        self.load_parent(handle, self.mname, self.mbirth, self.mbirth_label,
                         self.mdeath, self.mdeath_label,
                         self.mbutton_index, self.mbutton_add,
                         self.mbutton_del, self.mbutton_edit)
        self._update_parent_dnd_handler(self.top.get_object('mtable_event_box'),
                                        self.obj.get_mother_handle(),
                                        self.on_drag_motherdata_get,
                                        self.on_drag_motherdata_received)

    def add_mother_clicked(self, obj):
        person = Person()
        person.set_gender(Person.FEMALE)
        autoname = config.get('behavior.surname-guessing')
        #_("Father's surname"),
        #_("None"),
        #_("Combination of mother's and father's surname"),
        #_("Icelandic style"),
        if autoname == 2:
            name = self.latin_american_child("mother")
        else:
            name = self.no_name()
        person.set_primary_name(name)
        EditPerson(self.dbstate, self.uistate, self.track, person,
                   self.new_mother_added)

    def add_father_clicked(self, obj):
        person = Person()
        person.set_gender(Person.MALE)
        autoname = config.get('behavior.surname-guessing')
        #_("Father's surname"),
        #_("None"),
        #_("Combination of mother's and father's surname"),
        #_("Icelandic style"),
        if autoname == 0:
            name = self.north_american_child()
        elif autoname == 2:
            name = self.latin_american_child("father")
        else:
            name = self.no_name()
        person.set_primary_name(name)
        EditPerson(self.dbstate, self.uistate, self.track,
                   person, self.new_father_added)

    def new_mother_added(self, person):
        for i in self.hidden:
            i.set_sensitive(True)
        self.obj.set_mother_handle(person.handle)
        self.update_mother(person.handle)

    def new_father_added(self, person):
        for i in self.hidden:
            i.set_sensitive(True)
        self.obj.set_father_handle(person.handle)
        self.update_father(person.handle)

    def del_mother_clicked(self, obj):
        for i in self.hidden:
            i.set_sensitive(True)

        self.obj.set_mother_handle(None)
        self.update_mother(None)

    def sel_mother_clicked(self, obj):
        for i in self.hidden:
            i.set_sensitive(True)

        data_filter = FastFemaleFilter(self.dbstate.db)
        sel = SelectPerson(self.dbstate, self.uistate, self.track,
                           _("Select Mother"),
                           filter=data_filter,
                           skip=[x.ref for x in self.obj.get_child_ref_list()])
        person = sel.run()

        if person:
            self.check_for_existing_family(self.obj.get_father_handle(),
                                           person.handle,
                                           self.obj.handle)
            self.obj.set_mother_handle(person.handle)
            self.update_mother(person.handle)

    def on_change_father(self, selector_window, obj):
        if  obj.__class__ == Person:
            try:
                person = obj
                self.obj.set_father_handle(person.get_handle())
                self.update_father(person.get_handle())
            except:
                log.warning("Failed to update father: \n"
                            "obj returned from selector was: %s\n"
                            % (repr(obj),))
                raise

        else:
            log.warning(
                "Object selector returned obj.__class__ = %s, it should "
                "have been of type %s." % (obj.__class__.__name__,
                                           Person.__name__))

        selector_window.close()

    def del_father_clicked(self, obj):
        for i in self.hidden:
            i.set_sensitive(True)

        self.obj.set_father_handle(None)
        self.update_father(None)

    def sel_father_clicked(self, obj):
        for i in self.hidden:
            i.set_sensitive(True)

        data_filter = FastMaleFilter(self.dbstate.db)
        sel = SelectPerson(self.dbstate, self.uistate, self.track,
                           _("Select Father"),
                           filter=data_filter,
                           skip=[x.ref for x in self.obj.get_child_ref_list()])
        person = sel.run()
        if person:
            self.check_for_existing_family(person.handle,
                                           self.obj.get_mother_handle(),
                                           self.obj.handle)
            self.obj.set_father_handle(person.handle)
            self.update_father(person.handle)

    def check_for_existing_family(self, father_handle, mother_handle,
                                  family_handle):

        if father_handle:
            father = self.dbstate.db.get_person_from_handle(father_handle)
            ffam = set(father.get_family_handle_list())
            if mother_handle:
                mother = self.dbstate.db.get_person_from_handle(mother_handle)
                mfam = set(mother.get_family_handle_list())
                common = list(mfam.intersection(ffam))
                if len(common) > 0:
                    if self.add_parent or self.obj.handle not in common:
                        WarningDialog(
                            _('Duplicate Family'),
                            _('A family with these parents already exists '
                              'in the database. If you save, you will create '
                              'a duplicate family. It is recommended that '
                              'you cancel the editing of this window, and '
                              'select the existing family'),
                            parent=self.window)

    def edit_father(self, obj, event):
        handle = self.obj.get_father_handle()
        return self.edit_person(obj, event, handle)

    def edit_mother(self, obj, event):
        handle = self.obj.get_mother_handle()
        return self.edit_person(obj, event, handle)

    def edit_person(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            try:
                person = self.db.get_person_from_handle(handle)
                EditPerson(self.dbstate, self.uistate,
                           self.track, person)
            except WindowActiveError:
                pass

    def load_parent(self, handle, name_obj, birth_obj, birth_label, death_obj,
                    death_label, btn_index, btn_add, btn_del, btn_edit):
        # is a parent used here:
        is_used = handle is not None

        # now we display the area:
        if is_used:
            db = self.db
            person = db.get_person_from_handle(handle)
            name = "%s [%s]" % (name_displayer.display(person),
                                person.gramps_id)
            birth = get_birth_or_fallback(db, person)
            self.callman.register_handles({'person': [handle]})
            if birth:
                #if event changes it view needs to update
                self.callman.register_handles({'event': [birth.get_handle()]})
                # translators: needed for French, ignore otherwise
                birth_label.set_label(_("%s:") % birth.get_type())

            death = get_death_or_fallback(db, person)
            if death:
                #if event changes it view needs to update
                self.callman.register_handles({'event': [death.get_handle()]})
                # translators: needed for French, ignore otherwise
                death_label.set_label(_("%s:") % death.get_type())

            btn_edit.set_tooltip_text(_('Edit %s') % name)
            btn_index.hide()
            btn_add.hide()
            btn_del.show()
            btn_edit.show()
        else:
            name = ""
            birth = None
            death = None

            btn_index.show()
            btn_add.show()
            btn_del.hide()
            btn_edit.hide()

        if name_obj:
            name_obj.set_text(name)
        if birth:
            birth_str = displayer.display(birth.get_date_object())
        else:
            birth_str = ""
        birth_obj.set_text(birth_str)
        if death:
            death_str = displayer.display(death.get_date_object())
        else:
            death_str = ""
        death_obj.set_text(death_str)

    def fix_parent_handles(self, orig_handle, new_handle, trans):
        if orig_handle != new_handle:
            if orig_handle:
                person = self.db.get_person_from_handle(orig_handle)
                person.family_list.remove(self.obj.handle)
                self.db.commit_person(person, trans)
            if new_handle:
                person = self.db.get_person_from_handle(new_handle)
                person.family_list.append(self.obj.handle)
                self.db.commit_person(person, trans)

    def on_drag_fatherdata_received(self, widget, context, x, y, sel_data,
                                    info, time):
        """
        Handle the standard gtk interface for drag_data_received.
        """
        if self.obj.get_father_handle():
            return
        for i in self.hidden:
            i.set_sensitive(True)
        if sel_data and sel_data.get_data():
            (drag_type, idval, handle, val) = pickle.loads(sel_data.get_data())
            person = self.db.get_person_from_handle(handle)

            if person:
                self.check_for_existing_family(person.handle,
                                               self.obj.get_mother_handle(),
                                               self.obj.handle)
                self.obj.set_father_handle(person.handle)
                self.update_father(person.handle)

    def on_drag_motherdata_received(self, widget, context, x, y, sel_data,
                                    info, time):
        """
        Handle the standard gtk interface for drag_data_received.
        """
        if self.obj.get_mother_handle():
            return
        for i in self.hidden:
            i.set_sensitive(True)
        if sel_data and sel_data.get_data():
            (drag_type, idval, handle, val) = pickle.loads(sel_data.get_data())
            person = self.db.get_person_from_handle(handle)

            if person:
                self.check_for_existing_family(self.obj.get_father_handle(),
                                               person.handle,
                                               self.obj.handle)
                self.obj.set_mother_handle(person.handle)
                self.update_mother(person.handle)

    def object_is_empty(self):
        return (not self.obj.get_father_handle() and
                not self.obj.get_mother_handle() and
                len(self.obj.get_child_ref_list()) == 0
               )

    def save(self, *obj):
        ## FIXME: how to catch a specific error?
        #try:
        self.__do_save()
        #except bsddb_db.DBRunRecoveryError as msg:
        #    RunDatabaseRepair(msg[1], parent=self.window)

    def __do_save(self):
        self.ok_button.set_sensitive(False)

        if not self.added:
            original = self.db.get_family_from_handle(self.obj.handle)
        else:
            original = None

        # do some basic checks

        child_list = [ ref.ref for ref in self.obj.get_child_ref_list() ]

        if self.obj.get_father_handle() in child_list:

            father = self.db.get_person_from_handle(self.obj.get_father_handle())
            name = "%s [%s]" % (name_displayer.display(father),
                                father.gramps_id)
            ErrorDialog(_("A father cannot be his own child"),
                        _("%s is listed as both the father and child "
                          "of the family.") % name,
                        parent=self.window)
            self.ok_button.set_sensitive(True)
            return
        elif self.obj.get_mother_handle() in child_list:

            mother = self.db.get_person_from_handle(self.obj.get_mother_handle())
            name = "%s [%s]" % (name_displayer.display(mother),
                                mother.gramps_id)
            ErrorDialog(_("A mother cannot be her own child"),
                        _("%s is listed as both the mother and child "
                          "of the family.") % name,
                        parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        if not original and self.object_is_empty():
            ErrorDialog(
                _("Cannot save family"),
                _("No data exists for this family. "
                  "Please enter data or cancel the edit."),
                parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        (uses_dupe_id, id) = self._uses_duplicate_id()
        if uses_dupe_id:
            msg1 = _("Cannot save family. ID already exists.")
            msg2 = _("You have attempted to use the existing Gramps ID with "
                         "value %(id)s. This value is already used. Please "
                         "enter a different ID or leave "
                         "blank to get the next available ID value.") % {
                         'id' : id}
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        # We disconnect the callbacks to all signals we connected earlier.
        # This prevents the signals originating in any of the following
        # commits from being caught by us again.
        self._cleanup_callbacks()

        if not original and not self.object_is_empty():
            with DbTxn(_("Add Family"), self.db) as trans:

                # find the father, add the family handle to the father
                handle = self.obj.get_father_handle()
                if handle:
                    parent = self.db.get_person_from_handle(handle)
                    parent.add_family_handle(self.obj.handle)
                    self.db.commit_person(parent, trans)

                # find the mother, add the family handle to the mother
                handle = self.obj.get_mother_handle()
                if handle:
                    parent = self.db.get_person_from_handle(handle)
                    parent.add_family_handle(self.obj.handle)
                    self.db.commit_person(parent, trans)

                # for each child, add the family handle to the child
                for ref in self.obj.get_child_ref_list():
                    child = self.db.get_person_from_handle(ref.ref)
                    # fix - relationships need to be extracted from the list
                    child.add_parent_family_handle(self.obj.handle)
                    self.db.commit_person(child, trans)

                self.db.add_family(self.obj, trans)
        elif self.data_has_changed():

            with DbTxn(_("Edit Family"), self.db) as trans:

                self.fix_parent_handles(original.get_father_handle(),
                                        self.obj.get_father_handle(), trans)
                self.fix_parent_handles(original.get_mother_handle(),
                                        self.obj.get_mother_handle(), trans)

                orig_set = set(original.get_child_ref_list())
                new_set = set(self.obj.get_child_ref_list())

                # remove the family from children which have been removed
                for ref in orig_set.difference(new_set):
                    person = self.db.get_person_from_handle(ref.ref)
                    person.remove_parent_family_handle(self.obj.handle)
                    self.db.commit_person(person, trans)

                # add the family to children which have been added
                for ref in new_set.difference(orig_set):
                    person = self.db.get_person_from_handle(ref.ref)
                    person.add_parent_family_handle(self.obj.handle)
                    self.db.commit_person(person, trans)

                if self.object_is_empty():
                    self.db.remove_family_relationships(self.obj.handle, trans)
                else:
                    if not self.obj.get_gramps_id():
                        self.obj.set_gramps_id(
                                         self.db.find_next_family_gramps_id())
                    self.db.commit_family(self.obj, trans)

        self._do_close()
        if self.callback:
            self.callback(self.obj)
        self.callback = None

    def no_name(self):
        """
        Default surname guess.
        """
        name = Name()
        #the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        return name

    def north_american_child(self):
        """
        If SURNAME_GUESSING is north american, then find a child
        and return their name for the father.
        """
        # for each child, find one with a last name
        name = Name()
        #the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        for ref in self.obj.get_child_ref_list():
            child = self.db.get_person_from_handle(ref.ref)
            if child:
                preset_name(child, name)
                return name
        return name

    def latin_american_child(self, parent):
        """
        If SURNAME_GUESSING is latin american, then find a child
        and return their name for the father or mother.

        parent = "mother" | "father"
        """
        name = Name()
        #the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        # for each child, find one with a last name
        for ref in self.obj.get_child_ref_list():
            child = self.db.get_person_from_handle(ref.ref)
            if child:
                pname = child.get_primary_name()
                preset_name(child, name) # add the known family surnames, etc.
                surnames = name.get_surname_list()
                if len(surnames) < 2:
                    return name
                else:
                    #return first for the father, and last for the mother
                    if parent == 'father':
                        name.set_surname_list([surnames[0]])
                        return name
                    else:
                        name.set_surname_list([surnames[-1]])
                        return name
        return name

def button_activated(event, mouse_button):
    if (event.type == Gdk.EventType.BUTTON_PRESS and
        event.button == mouse_button) or \
       (event.type == Gdk.EventType.KEY_PRESS and
        event.keyval in (_RETURN, _KP_ENTER)):
        return True
    else:
        return False
