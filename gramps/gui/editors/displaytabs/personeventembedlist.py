#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       B. Malengier
# Copyright (C) 2018       Alois Poettker
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
# python
#
#-------------------------------------------------------------------------
import copy

from gi.repository import GObject
from gi.repository import GLib

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.db import DbTxn
from gramps.gen.lib import EventRoleType, EventType, EventRef
from gramps.gen.display.name import displayer as name_displayer
from .eventembedlist import EventEmbedList
from .eventrefmodel import EventRefModel
from gramps.gen.errors import WindowActiveError

#-------------------------------------------------------------------------
#
# PersonEventEmbedList
#
#-------------------------------------------------------------------------
class PersonEventEmbedList(EventEmbedList):

    _WORKNAME = _("Personal")
    #_FAMNAME = _("With %(namepartner)s (%(famid)s)")
    _FAMNAME = _("Family")
    _UNKNOWNNAME = _("<Unknown>")

    _MSG = {
        'add'   : _('Add a new personal event'),
        'del'   : _('Remove the selected personal event'),
        'edit'  : _('Edit the selected personal event or edit family'),
        'share' : _('Share an existing event'),
        'clone' : _('Clone an existing event'),
        'merge' : _('Merge two existing events'),
        'up'    : _('Move the selected event upwards or change family order'),
        'down'  : _('Move the selected event downwards or change family order'),
        }

    def __init__(self, dbstate, uistate, track, obj, **kwargs):
        """"""
        self.dbstate = dbstate
        EventEmbedList.__init__(self, dbstate, uistate, track, obj,
                                build_model=EventRefModel, **kwargs)

    def get_data(self):
        if self.reload:
            # Reload obj/person from DBase (may changed, eg. EventMerge)
            person = self.dbstate.db.get_person_from_gramps_id(self.obj.gramps_id)
            eventref_list = person.get_event_ref_list()
            self.obj.event_ref_list = copy.deepcopy(eventref_list)

        if not self._data or self.changed:
            self._data = [self.obj.get_event_ref_list()]
            self._groups = [(self.obj.get_handle(), self._WORKNAME, '')]
            # own Family events
            family_handle_list = self.obj.get_family_handle_list()
            if family_handle_list:
                for family_handle in family_handle_list:
                    family = self.dbstate.db.get_family_from_handle(family_handle)
                    if family is None:
                        continue
                    father_handle = family.get_father_handle()
                    mother_handle = family.get_mother_handle()
                    if self.obj.get_handle() == father_handle:
                        handlepartner = mother_handle
                    else:
                        handlepartner = father_handle
                    if handlepartner:
                        partner = self.dbstate.db.get_person_from_handle(
                                                    handlepartner)
                        groupname = name_displayer.display(partner)
                    else:
                        groupname = self._UNKNOWNNAME
                    self._data.append(family.get_event_ref_list())
                    self._groups.append((family_handle, self._FAMNAME,
                                         groupname))
            self.changed = False

        return self._data

    def default_role(self):
        return EventRoleType(EventRoleType.PRIMARY)

    def default_types(self):
        return [
            EventType(EventType.BIRTH),
            EventType(EventType.DEATH),
            EventType(EventType.BURIAL),
            ]

    def get_ref_editor(self):
        from .. import EditEventRef
        return EditEventRef

    def editnotworkgroup(self, key):
        """
        Edit non native event in own editor
        """
        family = self.dbstate.db.get_family_from_handle(key)
        try:
            from .. import EditFamily
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass

    def _non_native_change(self):
        """
        handle change request of non native data
        """
        from ...dialog import WarningDialog
        WarningDialog(
            _("Cannot change Family"),
            _("You cannot change Family events in the Person Editor"),
            parent=self.uistate.window)

    def _move_up_group(self, groupindex):
        """
        move up pressed on the group
        If on a family group, allow to reorder the order of families
        as connected to this person.
        """
        ref = self.get_selected()
        if not ref or ref[1]:
            return
        if ref[0] == 0:
            #the workgroup: person events, cannot move up
            return
        if ref[0] == 1:
            #cannot move up, already first family
            return
        #change family list and rebuild the tabpage
        index = ref[0] - 1
        flist = self.obj.get_family_handle_list()
        handle = flist.pop(index)
        flist.insert(index-1, handle)
        self.changed = True
        self.rebuild()
        # select the row
        # New index is index-1 but for path, add another 1 for person events.
        path = (index,)
        self.tree.get_selection().select_path(path)
        GLib.idle_add(self.tree.scroll_to_cell, path)

    def _move_down_group(self, groupindex):
        """
        move down pressed on the group
        If on a family group, allow to reorder the order of families
        as connected to this person.
        """
        ref = self.get_selected()
        if not ref or ref[1]:
            return
        if ref[0] == 0:
            #person events, cannot move down
            return
        if ref[0] == len(self._groups)-1:
            #cannot move down, already last family
            return
        #change family list and rebuild the tabpage
        index = ref[0] -1
        flist = self.obj.get_family_handle_list()
        handle = flist.pop(index)
        flist.insert(index+1, handle)
        self.changed = True
        self.rebuild()
        # select the row
        # New index is index+1 but for path, add another 1 for person events.
        path = (index + 2,)
        self.tree.get_selection().select_path(path)
        GLib.idle_add(self.tree.scroll_to_cell, path)

    def merge_button_clicked(self, obj):
        """
        Method called with the Merge button is clicked.
        """
        self.action = ''   # Reset event action
        # double check for properly work; see eventembedlist/_selection_changed
        if len(self.selected_list) != 2:
            return

        person = self.dbstate.db.get_person_from_gramps_id(self.obj.gramps_id)
        if person:
            self.reload = True
            self.action = 'Event-Merge'
            event_ref_list = [event_ref.ref for event_ref in person.event_ref_list]

            selected0_ref = self.selected_list[0][1].ref
            selected1_ref = self.selected_list[1][1].ref

            # Checks if event are not equal
            if selected0_ref == selected1_ref:
                WarningDialog(
                    _("Cannot merge this references"),
                    _("This is one event, but with different roles."),
                    parent=self.uistate.window)
                return

            # Checks if event 1 is stored in DB. Note: if not, will be!
            if selected0_ref not in event_ref_list:
                event_ref = EventRef()
                event_ref.ref = selected0_ref
                event_ref.role = EventRoleType.PRIMARY
                person.add_event_ref(event_ref)
                with DbTxn(_("Edit Person (%s)") % person.gramps_id,
                           self.dbstate.db) as trans:
                    self.dbstate.db.commit_person(person, trans)

            # Checks if event 2 is stored in DB. Note: if not, will be!
            if selected1_ref not in event_ref_list:
                event_ref = EventRef()
                event_ref.ref = selected1_ref
                event_ref.role = EventRoleType.PRIMARY
                person.add_event_ref(event_ref)
                with DbTxn(_("Edit Person (%s)") % person.gramps_id,
                           self.dbstate.db) as trans:
                    self.dbstate.db.commit_person(person, trans)

            from ...merge import MergeEvent
            MergeEvent(self.dbstate, self.uistate, self.track, \
                       selected0_ref, selected1_ref)

        else:
            from ...dialog import WarningDialog
            WarningDialog(
                _("Cannot merge this references"),
                _("This events cannot be merged at this time. "
                  "The person is not saved in database.\n\nTo merge this event "
                  "references, you need to press the OK button first."),
                parent=self.uistate.window)
