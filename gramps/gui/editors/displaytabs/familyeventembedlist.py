#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

from gramps.gen.db import DbTxn
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import EventRoleType, EventRef

from .eventembedlist import EventEmbedList
from .eventrefmodel import EventRefModel

from ...dialog import WarningDialog
from ...merge import MergeEvent

#-------------------------------------------------------------------------
#
# FamilyEventEmbedList
#
#-------------------------------------------------------------------------
class FamilyEventEmbedList(EventEmbedList):

    def __init__(self, dbstate, uistate, track, obj, **kwargs):
        """"""
        self.dbstate = dbstate
        EventEmbedList.__init__(self, dbstate, uistate, track, obj,
                                build_model=EventRefModel, **kwargs)

    def merge_button_clicked(self, obj):
        """
        Method called with the Merge button is clicked.
        """
        self.action = ''   # Reset event action
        # double check for properly work; see eventembedlist/_selection_changed
        if len(self.selected_list) != 2:
            return

        family = self.dbstate.db.get_family_from_gramps_id(self.obj.gramps_id)
        if family:
            self.reload = True
            self.action = 'Event-Merge'
            event_ref_list = [event_ref.ref for event_ref in family.event_ref_list]

            selected0_ref = self.selected_list[0][1].ref
            selected1_ref = self.selected_list[1][1].ref

            # Checks if event are not equal
            if selected0_ref == selected1_ref:
                WarningDialog(
                    _("Cannot merge this references"),
                    _("This event is one, but with different roles."),
                    parent=self.uistate.window)
                return

            # Checks if event 1 is stored in DB. Note: if not, will be!
            if selected0_ref not in event_ref_list:
                event_ref = EventRef()
                event_ref.ref = selected0_ref
                event_ref.role = EventRoleType.FAMILY
                family.add_event_ref(event_ref)
                with DbTxn(_("Edit Family (%s)") % family.gramps_id,
                           self.dbstate.db) as trans:
                    self.dbstate.db.commit_family(family, trans)

            # Checks if event 2 is stored in DB. Note: if not, will be!
            selected1_ref = self.selected_list[1][1].ref
            if selected1_ref not in event_ref_list:
                event_ref = EventRef()
                event_ref.ref = selected1_ref
                event_ref.role = EventRoleType.FAMILY
                family.add_event_ref(event_ref)
                with DbTxn(_("Edit Family (%s)") % family.gramps_id,
                           self.dbstate.db) as trans:
                    self.dbstate.db.commit_family(family, trans)

            MergeEvent(self.dbstate, self.uistate, self.track, \
                       selected0_ref, selected1_ref)
        else:
            WarningDialog(
                _("Cannot merge this references"),
                _("This events cannot be merged at this time. "
                  "The family is not saved in database.\n\nTo merge this event "
                  "references, you need to press the OK button first."),
                parent=self.uistate.window)

