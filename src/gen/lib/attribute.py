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
Attribute class for GRAMPS.
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
from gen.lib.attrtype import AttributeType

#-------------------------------------------------------------------------
#
# Attribute for Person/Family/MediaObject/MediaRef
#
#-------------------------------------------------------------------------
class Attribute(SecondaryObject, PrivacyBase, SourceBase, NoteBase):
    """
    Provide a simple key/value pair for describing properties. 
    
    Used by the Person and Family objects to store descriptive information.
    """
    
    def __init__(self, source=None):
        """
        Create a new Attribute object, copying from the source if provided.
        """
        PrivacyBase.__init__(self, source)
        SourceBase.__init__(self, source)
        NoteBase.__init__(self, source)
        
        if source:
            self.type = source.type
            self.value = source.value
        else:
            self.type = AttributeType()
            self.value = ""

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (PrivacyBase.serialize(self),
                SourceBase.serialize(self),
                NoteBase.serialize(self),
                self.type.serialize(), self.value)

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (privacy, source_list, note_list, the_type, self.value) = data
        PrivacyBase.unserialize(self, privacy)
        SourceBase.unserialize(self, source_list)
        NoteBase.unserialize(self, note_list)
        self.type.unserialize(the_type)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.value]

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

        :returns: Returns the list of child secondary child objects that may 
                refer notes.
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

    def set_type(self, val):
        """Set the type (or key) of the Attribute instance."""
        self.type.set(val)

    def get_type(self):
        """Return the type (or key) or the Attribute instance."""
        return self.type

    def set_value(self, val):
        """Set the value of the Attribute instance."""
        self.value = val

    def get_value(self):
        """Return the value of the Attribute instance."""
        return self.value
