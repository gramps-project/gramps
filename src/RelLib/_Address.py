#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Address class for GRAMPS
"""

__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _SecondaryObject import SecondaryObject
from _PrivacyBase import PrivacyBase
from _SourceBase import SourceBase
from _NoteBase import NoteBase
from _DateBase import DateBase
from _LocationBase import LocationBase

#-------------------------------------------------------------------------
#
# Address for Person/Repository
#
#-------------------------------------------------------------------------
class Address(SecondaryObject, PrivacyBase, SourceBase, NoteBase, DateBase,
              LocationBase):
    """Provides address information."""

    def __init__(self, source=None):
        """Creates a new Address instance, copying from the source
        if provided"""
        PrivacyBase.__init__(self, source)
        SourceBase.__init__(self, source)
        NoteBase.__init__(self, source)
        DateBase.__init__(self, source)
        LocationBase.__init__(self, source)

    def serialize(self):
        """
        Converts the object to a serialized tuple of data
        """
        return (PrivacyBase.serialize(self),
                SourceBase.serialize(self),
                NoteBase.serialize(self),
                DateBase.serialize(self),
                LocationBase.serialize(self))

    def unserialize(self, data):
        """
        Converts a serialized tuple of data to an object
        """
        (privacy, source_list, note_list, date, location) = data
        
        PrivacyBase.unserialize(self, privacy)
        SourceBase.unserialize(self, source_list)
        NoteBase.unserialize(self, note_list)
        DateBase.unserialize(self, date)
        LocationBase.unserialize(self, location)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return LocationBase.get_text_data_list(self)

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        return self.source_list

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects.
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

    def get_referenced_handles(self):
        """
        Returns the list of (classname,handle) tuples for all directly
        referenced primary objects.
        
        @return: List of (classname,handle) tuples for referenced objects.
        @rtype: list
        """
        return self.get_referenced_note_handles()
