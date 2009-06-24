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
Address class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.secondaryobj import SecondaryObject
from gen.lib.privacybase import PrivacyBase
from gen.lib.srcbase import SourceBase
from gen.lib.notebase import NoteBase
from gen.lib.datebase import DateBase
from gen.lib.locationbase import LocationBase

#-------------------------------------------------------------------------
#
# Address for Person/Repository
#
#-------------------------------------------------------------------------
class Address(SecondaryObject, PrivacyBase, SourceBase, NoteBase, DateBase,
              LocationBase):
    """Provide address information."""

    def __init__(self, source=None):
        """
        Create a new Address instance, copying from the source if provided.
        """
        PrivacyBase.__init__(self, source)
        SourceBase.__init__(self, source)
        NoteBase.__init__(self, source)
        DateBase.__init__(self, source)
        LocationBase.__init__(self, source)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (PrivacyBase.serialize(self),
                SourceBase.serialize(self),
                NoteBase.serialize(self),
                DateBase.serialize(self),
                LocationBase.serialize(self))

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
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
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return LocationBase.get_text_data_list(self)

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.source_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may refer notes.
        :rtype: list
        """
        return self.source_list

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.
        
        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.source_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        
        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return self.get_referenced_note_handles()
