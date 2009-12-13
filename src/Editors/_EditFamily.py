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

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from bsddb import db as bsddb_db
from gettext import gettext as _
from DdTargets import DdTargets
import cPickle as pickle

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
import gtk
from gtk import gdk
import pango

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
import const
import config
from BasicUtils import name_displayer
import gen.lib
import Errors
import DateHandler
from glade import Glade

from Editors import EditPrimary
from ReportBase import ReportUtils
from DisplayTabs import (EmbeddedList, EventEmbedList, SourceEmbedList, 
                         FamilyAttrEmbedList, NoteTab, GalleryTab, 
                         FamilyLdsEmbedList, ChildModel)
from widgets import (PrivacyButton, MonitoredEntry, MonitoredDataType, 
                     IconButton, LinkBox, BasicLabel)
from gen.plug import CATEGORY_QR_FAMILY
from QuestionDialog import (ErrorDialog, RunDatabaseRepair, WarningDialog,
                            MessageHideDialog)

from Selectors import selector_factory
SelectPerson = selector_factory('Person')

_RETURN = gdk.keyval_from_name("Return")
_KP_ENTER = gdk.keyval_from_name("KP_Enter")
_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3

class ChildEmbedList(EmbeddedList):
    """
    The child embed list is specific to the Edit Family dialog, so it
    is contained here instead of in DisplayTabs.
    """

    _HANDLE_COL = 10
    _DND_TYPE = DdTargets.PERSON_LINK

    _MSG = {
        'add'   : _('Create a new person and add the child to the family'),
        'del'   : _('Remove the child from the family'),
        'edit'  : _('Edit the child reference'),
        'share' : _('Add an existing person as a child of the family'),
        'up'	: _('Move the child up in the childrens list'),
        'down'	: _('Move the child down in the childrens list'),
        }

    _column_names = [
        (_('#'),0) ,
        (_('ID'),1) ,
        (_('Name'),11),
        (_('Gender'),3),
        (_('Paternal'),4),
        (_('Maternal'),5),
        (_('Birth Date'),12),
        (_('Death Date'),13),
        (_('Birth Place'),8),
        (_('Death Place'),9),
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
            (False, True,  (gtk.STOCK_EDIT, _('Edit child')), 
                                            self.edit_child_button_clicked),
            (True, True, gtk.STOCK_ADD, self.add_button_clicked),
            (True, False, _('Add an existing child'), 
                                            self.share_button_clicked),
            (False, True,  (gtk.STOCK_EDIT, _('Edit relationship')), 
                                            self.edit_button_clicked),
            (True, True, gtk.STOCK_REMOVE, self.del_button_clicked),
            ]

    def get_middle_click(self):
        return self.edit_child_button_clicked

    def find_index(self, obj):
        """
        returns the index of the object within the associated data
        """
        reflist = [ref.ref for ref in self.family.get_child_ref_list()]
        return reflist.index(obj)

    def _find_row(self, x, y):
        row = self.tree.get_path_at_pos(x, y)
        if row is None:
            return len(self.family.get_child_ref_list())
        else:
            return row[0][0]

    def _handle_drag(self, row, obj):
        self.family.get_child_ref_list().insert(row, obj)
        self.changed = True
        self.rebuild()

    def _move(self, row_from, row_to, obj):
        dlist = self.family.get_child_ref_list()
        if row_from < row_to:
            dlist.insert(row_to, obj)
            del dlist[row_from]
        else:
            del dlist[row_from]
            dlist.insert(row_to-1, obj)
        self.changed = True
        self.rebuild()

    def build_columns(self):
        for column in self.columns:
            self.tree.remove_column(column)
        self.columns = []

        for pair in self.column_order():
            if not pair[0]:
                continue
            name = self._column_names[pair[1]][0]
            render = gtk.CellRendererText()
            column = gtk.TreeViewColumn(name, render, markup=pair[1])
            column.set_min_width(50)

            column.set_resizable(True)
            column.set_sort_column_id(self._column_names[pair[1]][1])
            self.columns.append(column)
            self.tree.append_column(column)

    def get_icon_name(self):
        return 'gramps-family'

    def is_empty(self):
        """
        The list is considered empty if the child list is empty.
        """
        return len(self.family.get_child_ref_list()) == 0

    def get_data(self):
        """
        Normally, get_data returns a list. However, we return family
        object here instead.
        """
        return self.family

    def column_order(self):
        return [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), 
                (0, 8), (0, 9)]

    def add_button_clicked(self, obj):
        from Editors import EditPerson
        person = gen.lib.Person()
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
        person.get_primary_name().set_surname(name[1])
        person.get_primary_name().set_surname_prefix(name[0])

        EditPerson(self.dbstate, self.uistate, self.track, person,
                   self.new_child_added)

    def new_child_added(self, person):
        ref = gen.lib.ChildRef()
        ref.ref = person.get_handle()
        self.family.add_child_ref(ref)
        self.rebuild()
        self.call_edit_childref(ref.ref)

    def child_ref_edited(self, person):
        self.rebuild()

    def share_button_clicked(self, obj):
        # it only makes sense to skip those who are already in the family
        skip_list = [self.family.get_father_handle(), \
                     self.family.get_mother_handle()] + \
                    [x.ref for x in self.family.get_child_ref_list() ]

        sel = SelectPerson(self.dbstate, self.uistate, self.track,
                           _("Select Child"), skip=skip_list)
        person = sel.run()
        
        if person:
            ref = gen.lib.ChildRef()
            ref.ref = person.get_handle()
            self.family.add_child_ref(ref)
            self.rebuild()
            self.call_edit_childref(ref.ref)

    def run(self, skip):
        skip_list = [ x for x in skip if x]
        SelectPerson(self.dbstate, self.uistate, self.track,
                     _("Select Child"), skip=skip_list)

    def del_button_clicked(self, obj):
        handle = self.get_selected()
        if handle:
            for ref in self.family.get_child_ref_list():
                if ref.ref == handle:
                    self.family.remove_child_ref(ref)
            self.rebuild()

    def edit_button_clicked(self, obj):
        handle = self.get_selected()
        if handle:
            self.call_edit_childref(handle)

    def call_edit_childref(self, handle):
        from Editors import EditChildRef

        for ref in self.family.get_child_ref_list():
            if ref.ref == handle:
                p = self.dbstate.db.get_person_from_handle(handle)
                n = name_displayer.display(p)
                try:
                    EditChildRef(n, self.dbstate, self.uistate, self.track,
                                 ref, self.child_ref_edited)
                except Errors.WindowActiveError:
                    pass
                break

    def edit_child_button_clicked(self, obj):
        handle = self.get_selected()
        if handle:
            from Editors import EditPerson

            for ref in self.family.get_child_ref_list():
                if ref.ref == handle:
                    p = self.dbstate.db.get_person_from_handle(handle)
                    try:
                        EditPerson(self.dbstate, self.uistate, self.track,
                               p, self.child_ref_edited)
                    except Errors.WindowActiveError:
                        pass
                    break
    
    def up_button_clicked(self, obj):
        handle = self.get_selected()
        if handle:
            pos = self.find_index(handle)
            if pos > 0 :
                self._move_up(pos,self.family.get_child_ref_list()[pos], 
                              selmethod=self.family.get_child_ref_list)
                
    def down_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            pos = self.find_index(ref)
            if pos >=0 and pos < len(self.family.get_child_ref_list())-1:
                self._move_down(pos,self.family.get_child_ref_list()[pos], 
                                selmethod=self.family.get_child_ref_list)
    

    def drag_data_received(self, widget, context, x, y, sel_data, info, time):
        """
        Handle the standard gtk interface for drag_data_received.

        If the selection data is define, extract the value from sel_data.data,
        and decide if this is a move or a reorder.
        """
        if sel_data and sel_data.data:
            (mytype, selfid, obj, row_from) = pickle.loads(sel_data.data)

            # make sure this is the correct DND type for this object
            if mytype == self._DND_TYPE.drag_type:
                
                # determine the destination row
                row = self._find_row(x, y)

                # if the is same object, we have a move, otherwise,
                # it is a standard drag-n-drop
                
                if id(self) == selfid:
                    obj = self.get_data().get_child_ref_list()[row_from]
                    self._move(row_from, row, obj)
                else:
                    handle = obj
                    obj = gen.lib.ChildRef()
                    obj.ref = handle
                    self._handle_drag(row, obj)
                self.rebuild()
            elif self._DND_EXTRA and mytype == self._DND_EXTRA.drag_type:
                self.handle_extra_type(mytype, obj)

    def north_american(self):
        father_handle = self.family.get_father_handle()
        if father_handle:
            father = self.dbstate.db.get_person_from_handle(father_handle)
            pname = father.get_primary_name()
            return (pname.get_surname_prefix(), pname.get_surname())
        return ("","")

    def no_name(self):
        return ("","")

    def latin_american(self):
        if self.family:
            father_handle = self.family.get_father_handle()
            mother_handle = self.family.get_mother_handle()
            if not father_handle or not mother_handle:
                return ("","")
            father = self.dbstate.db.get_person_from_handle(father_handle)
            mother = self.dbstate.db.get_person_from_handle(mother_handle)
            if not father or not mother:
                return ("","")
            fsn = father.get_primary_name().get_surname()
            msn = mother.get_primary_name().get_surname()
            try:
                return ("", "%s %s" % (fsn.split()[0], msn.split()[0]))
            except:
                return ("", "")
        else:
            return ("", "")

class FastMaleFilter(object):

    def __init__(self, db):
        self.db = db

    def match(self, handle, db):
        value = self.db.get_raw_person_data(handle)
        return value[2] == gen.lib.Person.MALE

class FastFemaleFilter(object):

    def __init__(self, db):
        self.db = db

    def match(self, handle, db):
        value = self.db.get_raw_person_data(handle)
        return value[2] == gen.lib.Person.FEMALE

#-------------------------------------------------------------------------
#
# EditFamily
#
#-------------------------------------------------------------------------
class EditFamily(EditPrimary):

    QR_CATEGORY = CATEGORY_QR_FAMILY
    
    def __init__(self, dbstate, uistate, track, family):
        
        EditPrimary.__init__(self, dbstate, uistate, track,
                             family, dbstate.db.get_family_from_handle,
                             dbstate.db.get_family_from_gramps_id)

        # look for the scenerio of a child and no parents on a new
        # family
        
        if self.added and self.obj.get_father_handle() is None and \
               self.obj.get_mother_handle() is None and \
               len(self.obj.get_child_ref_list()) == 1:
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
                    'preferences.family-warn')
        else:
            self.add_parent = False

    def empty_object(self):
        return gen.lib.Family()

    def _local_init(self):
        self.build_interface()
        
        self.added = self.obj.handle is None
        if self.added:
            self.obj.handle = Utils.create_id()
            
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
                self.obj.marker != objreal.marker or
                self.obj.child_ref_list != objreal.child_ref_list)
            if maindatachanged:
                self.obj.gramps_id = objreal.gramps_id
                self.obj.father_handle = objreal.father_handle
                self.obj.mother_handle = objreal.mother_handle
                self.obj.private = objreal.private
                self.obj.type = objreal.type
                self.obj.marker = objreal.marker
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
              " been lost.") % {'object': _('family')}, parent=self.window)

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
        if self.obj.get_handle():
            dialog_title = Utils.family_name(self.obj, self.db, _("New Family"))
            dialog_title = _("Family") + ': ' + dialog_title
        else:
            dialog_title = _("New Family")
        return dialog_title

    def build_menu_names(self, family):
        return (_('Edit Family'), self.get_menu_title())

    def build_interface(self):
        self.width_key = 'interface.family-width'
        self.height_key = 'interface.family-height'
        
        self.top = Glade()
        self.set_window(self.top.toplevel, None, self.get_menu_title())

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

        #allow for a context menu
        self.set_contexteventbox(self.top.get_object("eventboxtop"))

    def _connect_signals(self):
        self.define_ok_button(self.top.get_object('ok'), self.save)
        self.define_cancel_button(self.top.get_object('cancel'))

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
        
        self.marker = MonitoredDataType(
            self.top.get_object('marker'), 
            self.obj.set_marker, 
            self.obj.get_marker, 
            self.db.readonly,
            self.db.get_marker_types(),
            )

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

        self.phandles = [mhandle, fhandle] + \
                        [ x.ref for x in self.obj.get_child_ref_list()]
        
        self.phandles = [handle for handle in self.phandles if handle]

    def _create_tabbed_pages(self):

        notebook = gtk.Notebook()

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
                                         self.obj)
        self._add_tab(notebook, self.event_list)
        self.track_ref_for_deletion("event_list")
            
        self.source_list = SourceEmbedList(self.dbstate,
                                           self.uistate, 
                                           self.track,
                                           self.obj)
        self._add_tab(notebook, self.source_list)
        self.track_ref_for_deletion("source_list")

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
                                notetype=gen.lib.NoteType.FAMILY)
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
        self.top.get_object('vbox').pack_start(notebook, True)

    def update_father(self, handle):
        self.load_parent(handle, self.fname, self.fbirth, self.fbirth_label,
                         self.fdeath, self.fdeath_label, 
                         self.fbutton_index, self.fbutton_add,
                         self.fbutton_del, self.fbutton_edit)

    def update_mother(self, handle):
        self.load_parent(handle, self.mname, self.mbirth, self.mbirth_label,
                         self.mdeath, self.mdeath_label, 
                         self.mbutton_index, self.mbutton_add,
                         self.mbutton_del, self.mbutton_edit)

    def add_mother_clicked(self, obj):
        from Editors import EditPerson
        person = gen.lib.Person()
        person.set_gender(gen.lib.Person.FEMALE)
        autoname = config.get('behavior.surname-guessing')
        #_("Father's surname"), 
        #_("None"), 
        #_("Combination of mother's and father's surname"), 
        #_("Icelandic style"), 
        if autoname == 2:
            name = self.latin_american_child("mother")
        else:
            name = self.no_name()
        person.get_primary_name().set_surname(name[1])
        person.get_primary_name().set_surname_prefix(name[0])
        EditPerson(self.dbstate, self.uistate, self.track, person,
                   self.new_mother_added)

    def add_father_clicked(self, obj):
        from Editors import EditPerson
        person = gen.lib.Person()
        person.set_gender(gen.lib.Person.MALE)
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
        person.get_primary_name().set_surname(name[1])
        person.get_primary_name().set_surname_prefix(name[0])
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
        if  obj.__class__ == gen.lib.Person:
            try:
                person = obj
                self.obj.set_father_handle(person.get_handle()) 
                self.update_father(person.get_handle())                    
            except:
                log.warn("Failed to update father: \n"
                         "obj returned from selector was: %s\n"
                         % (repr(obj),))                
                raise
            
        else:
            log.warn(
                "Object selector returned obj.__class__ = %s, it should "
                "have been of type %s." % (obj.__class__.__name__,
                                           gen.lib.Person.__name__))
            
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
            from _EditPerson import EditPerson
            try:
                person = self.db.get_person_from_handle(handle)
                EditPerson(self.dbstate, self.uistate,
                           self.track, person)
            except Errors.WindowActiveError:
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
            birth = ReportUtils.get_birth_or_fallback(db, person)
            self.callman.register_handles({'person': [handle]})
            if birth:
                #if event changes it view needs to update
                self.callman.register_handles({'event': [birth.get_handle()]})
            if birth and birth.get_type() == gen.lib.EventType.BAPTISM:
                birth_label.set_label(_("Baptism:"))

            death = ReportUtils.get_death_or_fallback(db, person)
            if death:
                #if event changes it view needs to update
                self.callman.register_handles({'event': [death.get_handle()]})
            if death and death.get_type() == gen.lib.EventType.BURIAL:
                death_label.set_label(_("Burial:"))

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
            birth_str = DateHandler.displayer.display(birth.get_date_object())
        else:
            birth_str = ""
        birth_obj.set_text(birth_str)
        if death:
            death_str = DateHandler.displayer.display(death.get_date_object())
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
                if self.obj.handle not in person.family_list:
                    person.family_list.append(self.obj.handle)
                self.db.commit_person(person, trans)

    def object_is_empty(self):
        return self.obj.get_father_handle() is None and \
               self.obj.get_mother_handle() is None and \
               len(self.obj.get_child_ref_list()) == 0
            
    def save(self, *obj):
        try:
            self.__do_save()
        except bsddb_db.DBRunRecoveryError, msg:
            RunDatabaseRepair(msg[1])

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
                                         "of the family.") % name)
            self.ok_button.set_sensitive(True)
            return
        elif self.obj.get_mother_handle() in child_list:

            mother = self.db.get_person_from_handle(self.obj.get_mother_handle())
            name = "%s [%s]" % (name_displayer.display(mother),
                                mother.gramps_id)
            ErrorDialog(_("A mother cannot be her own child"),
                                       _("%s is listed as both the mother and child "
                                         "of the family.") % name)
            self.ok_button.set_sensitive(True)
            return

        if not original and self.object_is_empty():
            ErrorDialog(
                _("Cannot save family"),
                _("No data exists for this family. "
                  "Please enter data or cancel the edit."))
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
            ErrorDialog(msg1, msg2)
            self.ok_button.set_sensitive(True)
            return

        # We disconnect the callbacks to all signals we connected earlier.
        # This prevents the signals originating in any of the following
        # commits from being caught by us again.
        self._cleanup_callbacks()
            
        if not original and not self.object_is_empty():
            trans = self.db.transaction_begin()

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
            self.db.transaction_commit(trans, _("Add Family"))
        elif cmp(original.serialize(),self.obj.serialize()):

            trans = self.db.transaction_begin()

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
                self.db.remove_family(self.obj.handle, trans)
            else:
                if not self.obj.get_gramps_id():
                    self.obj.set_gramps_id(self.db.find_next_family_gramps_id())
                self.db.commit_family(self.obj, trans)
            self.db.transaction_commit(trans, _("Edit Family"))

        self._do_close()

    def no_name(self):
        """
        Default surname guess.
        """
        return ("","")

    def north_american_child(self):
        """
        If SURNAME_GUESSING is north american, then find a child
        and return their name for the father.
        """
        # for each child, find one with a last name
        for ref in self.obj.get_child_ref_list():
            child = self.db.get_person_from_handle(ref.ref)
            if child:
                pname = child.get_primary_name()
                return (pname.get_surname_prefix(), pname.get_surname())
        return ("", "")

    def latin_american_child(self, parent):
        """
        If SURNAME_GUESSING is latin american, then find a child
        and return their name for the father or mother.

        parent = "mother" | "father"
        """
        # for each child, find one with a last name
        for ref in self.obj.get_child_ref_list():
            child = self.db.get_person_from_handle(ref.ref)
            if child:
                pname = child.get_primary_name()
                prefix, surname = (pname.get_surname_prefix(),
                                   pname.get_surname())
                if " " in surname:
                    fsn, msn = surname.split(" ", 1)
                else:
                    fsn, msn = surname, surname
                if parent == "father":
                    return prefix, fsn
                elif parent == "mother":    
                    return prefix, msn
                else:    
                    return ("", "")
        return ("", "")

def button_activated(event, mouse_button):
    if (event.type == gtk.gdk.BUTTON_PRESS and \
        event.button == mouse_button) or \
       (event.type == gtk.gdk.KEY_PRESS and \
        event.keyval in (_RETURN, _KP_ENTER)):
        return True
    else:
        return False

