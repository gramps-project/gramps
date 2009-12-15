#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       B. Malengier
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
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import gen.lib
import Errors
from DdTargets import DdTargets
from _GroupEmbeddedList import GroupEmbeddedList
from _EventRefModel import EventRefModel
from gui.dbguielement import DbGUIElement
from gui.selectors import SelectorFactory

#-------------------------------------------------------------------------
#
# EventEmbedList
#
#-------------------------------------------------------------------------
class EventEmbedList(DbGUIElement, GroupEmbeddedList):

    _HANDLE_COL = 7
    _DND_TYPE   = DdTargets.EVENTREF
    _DND_EXTRA  = DdTargets.EVENT
    _WORKGROUP = EventRefModel._ROOTINDEX
    
    _WORKNAME = _("Family Events")
    _FATHNAME = _("Events father")
    _MOTHNAME = _("Events mother")

    _MSG = {
        'add'   : _('Add a new family event'),
        'del'   : _('Remove the selected family event'),
        'edit'  : _('Edit the selected family event or edit person'),
        'share' : _('Share an existing event'),
        'up'    : _('Move the selected event upwards'),
        'down'  : _('Move the selected event downwards'),
        }

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Description'), -1, 195, 0, EventRefModel.COL_FONTWEIGHT[0]),
        (_('Type'), EventRefModel.COL_TYPE[0], 100, 0, 
                                            EventRefModel.COL_FONTWEIGHT[0]),
        (_('ID'), EventRefModel.COL_GID[0], 60, 0, 
                                            EventRefModel.COL_FONTWEIGHT[0]),
        (_('Date'), EventRefModel.COL_SORTDATE[0], 150, 1, -1),
        (_('Place'), EventRefModel.COL_PLACE[0], 140, 0, -1),
        (_('Role'), EventRefModel.COL_ROLE[0], 80, 0, -1),
        None,
        None,
        None
        ]

    def __init__(self, dbstate, uistate, track, obj, 
                 build_model=EventRefModel):
        self.obj = obj
        self._groups = []
        self._data = []
        DbGUIElement.__init__(self, dbstate.db)
        GroupEmbeddedList.__init__(self, dbstate, uistate, track, _('_Events'), 
                              build_model, share_button=True, 
                              move_buttons=True)
    
    def _connect_db_signals(self):
        """
        called on init of DbGUIElement, connect to db as required.
        """
        #note: event-rebuild closes the editors, so no need to connect to it
        self.callman.register_callbacks(
           {'event-update': self.event_change,  #change to an event we track
            'event-delete': self.event_delete,  #delete of event we track
           })
        self.callman.connect_all(keys=['event'])

    def event_change(self, *obj):
        """
        Callback method called when a tracked event changes (description
        changes, source added, ...)
        Note that adding an event 
        """
        self.rebuild_callback()
    
    def event_delete(self, obj):
        """
        Callback method called when a tracked event is deleted. 
        There are two possibilities: 
        * a tracked non-workgroup event is deleted, just rebuilding the view  
            will correct this.
        * a workgroup event is deleted. The event must be removed from the obj
            so that no inconsistent data is shown.
        """
        for handle in obj:
            refs = self.get_data()[self._WORKGROUP]
            ref_list = [eref.ref for eref in refs]
            indexlist = []
            last = 0
            while True:
                try:
                    last = ref_list.index(handle)
                    indexlist.append(last)
                except ValueError:
                    break
            #remove the deleted workgroup events from the object
            for index in indexlist.reverse():
                del refs[index]
        #now rebuild the display tab
        self.rebuild_callback()

    def get_ref_editor(self):
        from Editors import EditFamilyEventRef
        return EditFamilyEventRef

    def get_icon_name(self):
        return 'gramps-event'

    def get_data(self):
        #family events
        if not self._data or self.changed:
            self._data = [self.obj.get_event_ref_list()]
            self._groups = [(self.obj.get_handle(), self._WORKNAME)]
            #father events
            fhandle = self.obj.get_father_handle()
            if fhandle:
                fdata = self.dbstate.db.get_person_from_handle(fhandle).\
                                        get_event_ref_list()
                if fdata:
                    self._groups.append((fhandle, self._FATHNAME))
                    self._data.append(fdata)
            #mother events
            mhandle = self.obj.get_mother_handle()
            if mhandle:
                mdata = self.dbstate.db.get_person_from_handle(mhandle).\
                                        get_event_ref_list()
                if mdata:
                    self._groups.append((mhandle, self._MOTHNAME))
                    self._data.append(mdata)
            #we register all events that need to be tracked
            for group in self._data:
                self.callman.register_handles(
                                    {'event': [eref.ref for eref in group]})
            self.changed = False

        return self._data

    def groups(self):
        """
        Return the (group key, group name)s in the order as given by get_data()
        """
        return self._groups

    def column_order(self):
        """
        The columns to show as a tuple containing 
        tuples (show/noshow, model column)
        """
        return ((1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5))

    def default_type(self):
        return gen.lib.EventType(gen.lib.EventType.MARRIAGE)

    def default_role(self):
        return gen.lib.EventRoleType(gen.lib.EventRoleType.FAMILY)

    def add_button_clicked(self, obj):
        try:
            ref = gen.lib.EventRef()
            event = gen.lib.Event()
            ref.set_role(self.default_role())
            event.set_type(self.default_type())
            self.get_ref_editor()(
                self.dbstate, self.uistate, self.track,
                event, ref, self.object_added)
        except Errors.WindowActiveError:
            pass

    def __blocked_text(self):
        """
        Return the common text used when eventref cannot be edited
        """
        return _("This event reference cannot be edited at this time. "
                    "Either the associated event is already being edited "
                    "or another event reference that is associated with "
                    "the same event is being edited.\n\nTo edit this event "
                    "reference, you need to close the event.")
    
    def share_button_clicked(self, obj):
        SelectEvent = SelectorFactory('Event')

        sel = SelectEvent(self.dbstate, self.uistate, self.track)
        event = sel.run()
        if event:
            try:
                ref = gen.lib.EventRef()
                ref.set_role(self.default_role())
                self.get_ref_editor()(
                    self.dbstate, self.uistate, self.track,
                    event, ref, self.object_added)
            except Errors.WindowActiveError:
                from QuestionDialog import WarningDialog
                WarningDialog(_("Cannot share this reference"),
                              self.__blocked_text() )
                pass

    def edit_button_clicked(self, obj):
        ref = self.get_selected()
        if ref and ref[1] is not None and ref[0] == self._WORKGROUP:
            event = self.dbstate.db.get_event_from_handle(ref[1].ref)
            try:
                self.get_ref_editor()(
                    self.dbstate, self.uistate, self.track,
                    event, ref[1], self.object_edited)
            except Errors.WindowActiveError:
                from QuestionDialog import WarningDialog
                WarningDialog(_("Cannot edit this reference"),
                              self.__blocked_text() )
        elif ref and ref[0] != self._WORKGROUP:
            #bring up family editor
            key = self._groups[ref[0]][0]
            self.editnotworkgroup(key)

    def object_added(self, reference, primary):
        reference.ref = primary.handle
        self.get_data()[self._WORKGROUP].append(reference)
        self.callman.register_handles({'event': [primary.handle]}) 
        self.changed = True
        self.rebuild()

    def object_edited(self, ref, event):
        """
        Called as callback after eventref has been edited. 
        Note that if the event changes too (so not only the ref data), then 
        an event-update signal from the database will also be raised, and the
        rebuild done here will not be needed. There is no way to avoid this ...
        """
        self.changed = True
        self.rebuild()

    def get_popup_menu_items(self):
        if self._tmpgroup == self._WORKGROUP:
            return GroupEmbeddedList.get_popup_menu_items(self)
        else:
            return [
                (True, True, gtk.STOCK_ADD, self.add_button_clicked),
                (False,True, gtk.STOCK_EDIT, self.edit_button_clicked),
                ]

    def _non_native_change(self):
        """
        handle change request of non native data
        """
        from QuestionDialog import WarningDialog
        WarningDialog(
                    _("Cannot change Person"),
                    _("You cannot change Person events in the Family Editor")
                    )

    def _handle_drag(self, row, obj):
        """
        An event reference that is from a drag and drop has
        an unknown event reference role, so it cannot just be added,
        it needs to be edited and confirmed
        """
        if row[0] == self._WORKGROUP:
            from gen.lib import EventRoleType
            obj.set_role((EventRoleType.UNKNOWN,''))
            #add the event
            GroupEmbeddedList._handle_drag(self, row, obj)
            #call editor to set new eventref
            event = self.dbstate.db.get_event_from_handle(obj.ref)
            try:
                self.get_ref_editor()(self.dbstate, self.uistate, self.track,
                                      event, obj, self.object_edited)
            except Errors.WindowActiveError:
                from QuestionDialog import WarningDialog
                WarningDialog(
                    _("Cannot edit this reference"),
                    _("This event reference cannot be edited at this time. "
                      "Either the associated event is already being edited "
                      "or another event reference that is associated with "
                      "the same event is being edited.\n\nTo edit this event "
                      "reference, you need to close the event.")
                    )
        else:
            self.dropnotworkgroup(row, obj)

    def handle_extra_type(self, objtype, obj):
        try:
            ref = gen.lib.EventRef()
            event = self.dbstate.db.get_event_from_handle(obj)
            ref.set_role(self.default_role())
            self.get_ref_editor()(
                self.dbstate, self.uistate, self.track,
                event, ref, self.object_added)
        except Errors.WindowActiveError:
            pass

    def editnotworkgroup(self, key):
        """
        Edit non native event in own editor
        """
        from Editors import EditPerson
        person = self.dbstate.db.get_person_from_handle(key)
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except Errors.WindowActiveError:
            pass

    def dropnotworkgroup(self, row, obj):
        """
        Drop of obj on row that is not WORKGROUP
        """
        self._non_native_change()

    def move_away_work(self, row_from, row_to, obj):
        """
        move from the workgroup to a not workgroup
        we allow to change the default name like this
        """
        self.dropnotworkgroup(None, None)
    
    def move_to_work(self, row_from, row_to, obj):
        """
        move from a non workgroup to the workgroup
        handle this as a drop from clipboard
        """
        self._handle_drag(row_to, obj)

    def _move_up_notwork(self, row_from, obj, selmethod=None):
        """
        move up outside of workgroup
        """
        self._non_native_change()

    def _move_down_notwork(self, row_from, obj, selmethod=None):
        """
        move up outside of workgroup
        """
        self._non_native_change()

    def post_rebuild(self, prebuildpath):
        """
        Allow post rebuild specific handling. 
        @param prebuildpath: path selected before rebuild, None if none
        @type prebuildpath: tree path
        """
        self.tree.expand_all()
        if not prebuildpath is None:
            self.selection.select_path(prebuildpath)
