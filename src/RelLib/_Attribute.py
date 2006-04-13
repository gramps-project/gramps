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
Attribute class for GRAMPS
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from warnings import warn

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _BaseObject import BaseObject
from _PrivacyBase import PrivacyBase
from _SourceBase import SourceBase
from _NoteBase import NoteBase

#-------------------------------------------------------------------------
#
# Attribute for Person/Family/MediaObject/MediaRef
#
#-------------------------------------------------------------------------
class Attribute(BaseObject,PrivacyBase,SourceBase,NoteBase):
    """Provides a simple key/value pair for describing properties. Used
    by the Person and Family objects to store descriptive information."""
    
    UNKNOWN     = -1
    CUSTOM      = 0
    CASTE       = 1
    DESCRIPTION = 2
    ID          = 3
    NATIONAL    = 4
    NUM_CHILD   = 5
    SSN         = 6

    def __init__(self,source=None):
        """
        Creates a new Attribute object, copying from the source if provided.
        """
        BaseObject.__init__(self)
        PrivacyBase.__init__(self,source)
        SourceBase.__init__(self,source)
        NoteBase.__init__(self,source)
        
        if source:
            self.type = source.type
            self.value = source.value
        else:
            self.type = (Attribute.CUSTOM,"")
            self.value = ""

    def serialize(self):
        return (PrivacyBase.serialize(self),
                SourceBase.serialize(self),
                NoteBase.serialize(self),
                self.type,self.value)

    def unserialize(self,data):
        (privacy,source_list,note,self.type,self.value) = data
        PrivateBase.unserialize(self,privacy)
        SourceBase.unserialize(self,source_list)
        NoteBase.unserialize(self,note)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.value]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.source_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

    def set_type(self,val):
        """sets the type (or key) of the Attribute instance"""
        if not type(val) == tuple:
            warn( "set_type now takes a tuple", DeprecationWarning, 2)
            # Wrapper for old API
            # remove when transitition done.
            if val in range(-1,7):
                val = (val,'')
            else:
                val = (Attribute.CUSTOM,val)
        self.type = val

    def get_type(self):
        """returns the type (or key) or the Attribute instance"""
        return self.type

    def set_value(self,val):
        """sets the value of the Attribute instance"""
        self.value = val

    def get_value(self):
        """returns the value of the Attribute instance"""
        return self.value
