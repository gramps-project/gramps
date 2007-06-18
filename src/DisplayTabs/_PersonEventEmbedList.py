#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# GRAMPS classes
#
#-------------------------------------------------------------------------
import RelLib
from _EventEmbedList import EventEmbedList

_std_types = [
    RelLib.EventType(RelLib.EventType.BIRTH),
    RelLib.EventType(RelLib.EventType.DEATH),
    ]
               

#-------------------------------------------------------------------------
#
# PersonEventEmbedList
#
#-------------------------------------------------------------------------
class PersonEventEmbedList(EventEmbedList):

    def __init__(self, dbstate, uistate, track, obj):        
        EventEmbedList.__init__(self, dbstate, uistate, track, obj)

    def get_data(self):
        return self.obj.get_event_ref_list()

    def default_role(self):
        return RelLib.EventRoleType(RelLib.EventRoleType.PRIMARY)

    def default_type(self):
        type_list = []

        # combine return info into a single flat sequence

        event = None
        for event_ref in self.get_data():
            event = self.dbstate.db.get_event_from_handle(event_ref.ref)
            type_list.append(event.get_type())

        for etype in _std_types:
            if etype not in type_list:
                return RelLib.EventType(etype)
        return RelLib.EventType(RelLib.EventType.BIRTH)

    def get_ref_editor(self):
        from Editors import EditEventRef
        return EditEventRef

