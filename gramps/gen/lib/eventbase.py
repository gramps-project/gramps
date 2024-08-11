#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2022       Christopher Horn
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
EventBase class for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .eventref import EventRef
from .eventroletype import EventRoleType
from .const import EQUAL, DIFFERENT


# -------------------------------------------------------------------------
#
# EventBase
#
# -------------------------------------------------------------------------
class EventBase:
    """
    Base class for storing event references.
    """

    def __init__(self, source=None):
        """
        Create a new EventBase, copying from source if not None.

        :param source: Object used to initialize the new object
        :type source: EventBase
        """
        self.event_ref_list = (
            list(map(EventRef, source.event_ref_list)) if source else []
        )

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return [event_ref.serialize() for event_ref in self.event_ref_list]

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.event_ref_list = [EventRef().unserialize(item) for item in data]
        return self

    def add_event_ref(self, event_ref):
        """
        Add the :class:`~.eventref.EventRef` to the instance's
        :class:`~.eventref.EventRef` list.

        This is accomplished by assigning the :class:`~.eventref.EventRef` for
        the valid :class:`~.event.Event` in the current database.

        :param event_ref: the :class:`~.eventref.EventRef` to be added to the
                          instance's :class:`~.eventref.EventRef` list.
        :type event_ref: EventRef
        """
        if not isinstance(event_ref, EventRef):
            raise ValueError("Expecting EventRef instance")

        if not any(event_ref.is_equal(ref) for ref in self.event_ref_list):
            self.event_ref_list.append(event_ref)

    def get_event_ref_list(self):
        """
        Return the list of :class:`~.eventref.EventRef` objects associated with
        :class:`~.event.Event` instances.

        :returns: Returns the list of :class:`~.eventref.EventRef` objects
                  associated with the instance.
        :rtype: list
        """
        return self.event_ref_list

    def get_primary_event_ref_list(self, role=EventRoleType.PRIMARY):
        """
        Return the list of :class:`~.eventref.EventRef` objects associated with
        :class:`~.event.Event` instances that have been marked as primary
        events or some other role if specified.

        :returns: Returns generator of :class:`~.eventref.EventRef` objects
                  associated with the instance.
        :rtype: generator
        """
        return (
            event_ref
            for event_ref in self.event_ref_list
            if event_ref.get_role() == role
        )

    def set_event_ref_list(self, event_ref_list):
        """
        Set the instance's :class:`~.eventref.EventRef` list to the
        passed list.

        :param event_ref_list: List of valid :class:`~.eventref.EventRef`
                               objects
        :type event_ref_list: list
        """
        self.event_ref_list = event_ref_list

    def _has_event_reference(self, event_handle):
        """
        Return True if the object has reference to a given event handle

        :param handle: The event handle to be checked.
        :type handle: str
        :returns: Returns True if the object has a reference to the handle
        :rtype: bool
        """
        return event_handle in [event_ref.ref for event_ref in self.event_ref_list]

    def _remove_event_references(self, handle_list):
        """
        Remove any references to the given event handles from the instance's
        :class:`~.eventref.EventRef` list.

        :param handle_list: List of valid event handles to remove
        :type handle_list: list
        """
        new_list = [
            event_ref
            for event_ref in self.event_ref_list
            if event_ref.ref not in handle_list
        ]
        self.event_ref_list = new_list

    def _replace_event_references(self, old_handle, new_handle):
        """
        Replace all references to old handle with those to the new handle.

        :param old_handle: The handle to be replaced.
        :type old_handle: str
        :param new_handle: The handle to replace the old one with.
        :type new_handle: str
        """
        refs_list = [ref.ref for ref in self.event_ref_list]
        new_ref = None
        if new_handle in refs_list:
            new_ref = self.event_ref_list[refs_list.index(new_handle)]
        n_replace = refs_list.count(old_handle)
        for dummy_ix_replace in range(n_replace):
            idx = refs_list.index(old_handle)
            self.event_ref_list[idx].ref = new_handle
            refs_list[idx] = new_handle
            if new_ref:
                evt_ref = self.event_ref_list[idx]
                equi = new_ref.is_equivalent(evt_ref)
                if equi != DIFFERENT:
                    if equi == EQUAL:
                        new_ref.merge(evt_ref)
                    self.event_ref_list.pop(idx)
                    refs_list.pop(idx)


#    def _merge_event_ref_list(self, acquisition):
#        """
#        Merge the list of event references from acquisition with our own.

#        :param acquisition: the event references list of this object will be
#                            merged with the current event references list.
#        :type acquisition: Subject
#        """
#        eventref_list = self.event_ref_list[:]
#        for addendum in acquisition.get_event_ref_list():
#            for eventref in eventref_list:
#                equi = eventref.is_equivalent(addendum)
#                if equi == IDENTICAL:
#                    break
#                elif equi == EQUAL:
#                    eventref.merge(addendum)
#                    break
#            else:
#                self.event_ref_list.append(addendum)
