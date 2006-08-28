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
Address class for GRAMPS
"""

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
class Address(SecondaryObject,PrivacyBase,SourceBase,NoteBase,DateBase,
              LocationBase):
    """Provides address information."""

    def __init__(self,source=None):
        """Creates a new Address instance, copying from the source
        if provided"""
        SecondaryObject.__init__(self)
        PrivacyBase.__init__(self,source)
        SourceBase.__init__(self,source)
        NoteBase.__init__(self,source)
        DateBase.__init__(self,source)
        LocationBase.__init__(self,source)

        if source:
            self.street = source.street
        else:
            self.street = ""

    def serialize(self):
        return (PrivacyBase.serialize(self),
                SourceBase.serialize(self),
                NoteBase.serialize(self),
                DateBase.serialize(self),
                self.city,self.state,
                self.country,self.postal,self.phone,self.street)

    def unserialize(self,data):
        (privacy,source_list,note,date,self.city,self.state,
         self.country,self.postal,self.phone,self.street) = data
        PrivacyBase.unserialize(self,privacy)
        SourceBase.unserialize(self,source_list)
        NoteBase.unserialize(self,note)
        DateBase.unserialize(self,date)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.street] + LocationBase.get_text_data_list(self)
        #return [self.street,self.city,self.state,self.country,
        #        self.postal,self.phone,self.get_date()]

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
        their children, reference primary objects.
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

    def set_street(self,val):
        """sets the street portion of the Address"""
        self.street = val

    def get_street(self):
        """returns the street portion of the Address"""
        return self.street
