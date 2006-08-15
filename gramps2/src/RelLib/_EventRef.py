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

"""
Event Reference class for GRAMPS
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _SecondaryObject import SecondaryObject
from _PrivacyBase import PrivacyBase
from _NoteBase import NoteBase
from _AttributeBase import AttributeBase
from _RefBase import RefBase
from _EventRoleType import EventRoleType

#-------------------------------------------------------------------------
#
# Event References for Person/Family
#
#-------------------------------------------------------------------------
class EventRef(SecondaryObject,PrivacyBase,NoteBase,AttributeBase,RefBase):
    """
    Event reference class.

    This class is for keeping information about how the person relates
    to the refereneced event.
    """

    def __init__(self,source=None):
        """
        Creates a new EventRef instance, copying from the source if present.
        """
        SecondaryObject.__init__(self)
        PrivacyBase.__init__(self)
        NoteBase.__init__(self)
        AttributeBase.__init__(self)
        RefBase.__init__(self)
        if source:
            self.role = source.role
        else:
            self.role = EventRoleType()

    def serialize(self):
        return (
            PrivacyBase.serialize(self),
            NoteBase.serialize(self),
            AttributeBase.serialize(self),
            RefBase.serialize(self),
            self.role.serialize()
            )

    def unserialize(self,data):
        (privacy,note,attribute_list,ref,role) = data
        PrivacyBase.unserialize(self,privacy)
        NoteBase.unserialize(self,note)
        AttributeBase.unserialize(self,attribute_list)
        RefBase.unserialize(self,ref)
        self.role.unserialize(role)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [str(self.role)]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.attribute_list[:]
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_sourcref_child_list(self):
        """
        Returns the list of child secondary objects that may refer sources.

        @return: Returns the list of child secondary child objects that may refer sources.
        @rtype: list
        """
        return self.attribute_list[:]

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: Returns the list of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        if self.ref:
            return [('Event',self.ref)]
        else:
            return []

    def get_role(self):
        """
        Returns the tuple corresponding to the preset role.
        """
        return self.role

    def set_role(self,role):
        """
        Sets the role according to the given argument.
        """
        self.role.set(role)
